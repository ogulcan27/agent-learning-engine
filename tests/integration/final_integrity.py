"""Reference model of 07 §L Final Integrity.

Parsed from 07: authority table (§L.1), result vocabulary (§L.2), check table (§L.5) and the
§U check IDs. A check runs only if its row exists. Severity and repair target come from the row.
"""
import re
from pathlib import Path

import coverage_model as cm
import graph_model as gm
import persist_model as pm
from files import (CONFIG, GRAPH, HMAP, LEDGER, QUEUE, STATE, kv, parse_ledger, parse_pass, render_hmap,
                   render_index, render_queue, queue_a_rows)

ACTIVE_PASS = {"IN_PROGRESS", "WAITING_USER", "BLOCKED"}
OPEN_ENRICH = {"BLOCKED", "PENDING"}


class Protocol:
    def __init__(self, skill: Path):
        t = (skill / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8")
        sec = t.split("## L. Learning State / Cross-Layer Integrity", 1)[1].split("\n## ", 1)[0]
        auth = pm.rows(gm.section("\n" + sec, "### L.1 Authority model"))
        self.authority = {r[0].strip("`"): r[1] for r in auth}
        self.results = [r[0].strip("`") for r in pm.rows(gm.section("\n" + sec, "### L.2 Final integrity result"))]
        self.checks = {}
        for r in pm.rows(gm.section("\n" + sec, "### L.5 Checks")):
            target = re.match(r"rebuild `(.+?)`", r[3])
            self.checks[r[0]] = {"severity": r[2].split()[0], "rebuild": target.group(1) if target else None,
                                 "unreachable_warning": "erişilemiyorsa sonuç WARNING" in r[1]}
        self.u_checks = set(re.findall(r"^\| (U-\d\d) \|", t, re.M))

    def derived(self, artifact):
        return self.authority.get(artifact) == "DERIVED"


def result(proto, findings):
    """§L.2: FAIL > PASS_WITH_WARNINGS > PASS."""
    sev = {s for _, s in findings}
    name = "FAIL" if "FAIL" in sev else "PASS_WITH_WARNINGS" if "WARNING" in sev else "PASS"
    assert name in proto.results, name
    return name


# --- load --------------------------------------------------------------------------

def load(env, store, ctx):
    """Read the project (and library if configured) from disk."""
    cfg = kv(store.read(CONFIG))
    passes = {}
    base = store.roots["P"] / "passes"
    for f in sorted(base.glob("*/LEARNING_PASS.md")) if base.exists() else []:
        p = parse_pass(env.P5, env.P7.ms_cols, env.P7.kp_cols, f.read_text(encoding="utf-8"))
        passes[p["meta"]["learning_pass_id"]] = p
    pctx = dict(ctx, config=dict(ctx["config"], **{k: cfg[k] for k in ("project_id", "project_name") if k in cfg}),
                passes={k: p["meta"]["pass_status"] for k, p in passes.items()})
    lib_path = cfg.get("personal_library_path", "UNCONFIGURED")
    return {"cfg": cfg, "ledger": parse_ledger(env.P3_cols, store.read(LEDGER)), "state": kv(store.read(STATE)),
            "queue_a": [r["work_unit_id"] for r in pm.parse_table(gm.section(store.read(QUEUE), "## A. Deferred Work Units"),
                                                                    ["work_unit_id", "label", "status", "reason", "deferred_at", "source"])],
            "passes": passes, "s": pm.State.load(env.P7, store, pctx), "ctx": pctx,
            "hmap": kv(store.read(HMAP)), "lib": lib_path != "UNCONFIGURED",
            "lib_reachable": lib_path != "UNCONFIGURED" and Path(lib_path).exists()}


# --- checks --------------------------------------------------------------------------

def check(env, store, ctx, session_locks=()):
    """CHECK 1 / CHECK 2 of §L.3. Returns sorted [(id, severity)]."""
    L, d = env.L, load(env, store, ctx)
    f = []

    def add(cid, sev=None):
        if cid in L.checks:
            f.append((cid, sev or L.checks[cid]["severity"]))

    ledger, s, passes = d["ledger"], d["s"], d["passes"]
    lrows = {r["work_unit_id"]: r for r in ledger.rows}
    f += cm.integrity(ledger)
    f += pm.integrity(env.P7, s, d["ctx"])
    events = {e["Event ID"]: (pid, e) for pid, p in passes.items() for e in p["events"]}
    known = s.known_ids()
    pid_cfg = d["cfg"].get("project_id")

    state = {k: str(v) for k, v in cm.rebuild_state(ledger).items()}
    if any(d["state"].get(k) != v for k, v in state.items()):
        add("L-01")
    if set(d["queue_a"]) != {r["work_unit_id"] for r in cm.rebuild_queue(ledger)}:
        add("L-02")
    for debt in s.debts:
        if debt["originating_event_id"] not in events:
            add("L-03")
        if debt["debt_status"] == "RESOLVED":
            ref = events.get(debt.get("resolution_ref"))
            ms = next((r for r in passes[ref[0]]["ms"] if r["Event ID"] == ref[1]["Event ID"]), None) if ref else None
            nodes = [n for n in s.graph.nodes if n["debt_id"] == debt["debt_id"]]
            if not (ms and ms["Experience Persistence"] == "COMPLETE" and debt["concept_home"] in known
                    and all(n["node_status"] == "ACTIVE" and n["home_ref"] == debt["concept_home"] for n in nodes)):
                add("L-04")
    active = {}
    for pid, p in passes.items():
        meta, scope = p["meta"], p["meta"]["selected_scope"]
        if any(w not in lrows for w in scope):
            add("L-05")
        for e in p["events"]:
            if not set(pm.split(e["Work Units"])) <= set(scope):
                add("L-06")
        routing = {r["Event ID"]: r for r in p["routing"]}
        if meta["pass_status"] == "COMPLETE":
            if any(w in lrows and (lrows[w]["status"] == "PARTIAL" or lrows[w]["open_items"] != "-") for w in scope) \
                    or any(r["ULA Status"] != "COMPLETE" for r in routing.values()) \
                    or any(e["Disposition"] == "UNRESOLVED" for e in p["events"]):
                add("L-07")
            if any(r["Map Sync"] in OPEN_ENRICH or r["Experience Persistence"] in OPEN_ENRICH for r in p["ms"]):
                add("L-08")
        for r in p["ms"]:
            if r["Map Sync"] == "COMPLETE":
                in_graph = any(r["Event ID"] in pm.split(x["source_event_ids"]) for x in s.graph.nodes + s.graph.edges)
                if not in_graph or any(s.graph.node(n) is None for n in pm.split(r["Node IDs"])):
                    add("L-09")
            ev = next((e for e in p["events"] if e["Event ID"] == r["Event ID"]), None)
            route = pm.route(env.P7, {"disposition": ev["Disposition"] if ev else "-",
                                      "reusable": ev and ev.get("Reusable Signal", "-") != "-",
                                      "ula_status": routing.get(r["Event ID"], {}).get("ULA Status")})
            kp = next((k for k in p["kp"] if k["Event ID"] == r["Event ID"]), None)
            if r["Experience Persistence"] == "COMPLETE":
                cid, xid = (kp or {}).get("Concept ID", "-"), (kp or {}).get("Experience ID", "-")
                if kp is None or (route["concept_home"] == "YES" and cid not in s.pointers and cid not in s.local) \
                        or (route["experience_note"] == "YES" and xid not in s.notes) \
                        or (xid != "-" and xid not in s.notes):
                    add("L-10")
            if r["Experience Persistence"] == "NOT_APPLICABLE" and route["status"] != "NOT_APPLICABLE":
                add("L-10")
        for r in p["routing"]:
            art = r["Artifact"]
            if "U-16" in L.u_checks and r["ULA Status"] != "PENDING" and (art in ("", "-") or not (store.roots["P"] / art).exists()):
                f.append(("U-16", "FAIL"))
        if meta["pass_status"] in ACTIVE_PASS:
            for w in scope:
                if w in active:
                    add("L-15")
                active[w] = pid
        if meta["pass_status"] == "ABANDONED":
            own = {e["Event ID"] for e in p["events"]}
            for r in ledger.rows:
                if r["learning_pass_id"] == pid and r["status"] in ("COVERED", "NOT_LEARNING_RELEVANT"):
                    add("L-16")
                if any(x.startswith(f"LE-{pid}-") and x not in own for x in pm.split(r["open_items"])):
                    add("L-16")
    for n in s.graph.nodes:
        if n["home_ref"] != "UNASSIGNED" and n["home_ref"] not in known:
            add("L-11")
    reg = {r["Concept ID"]: r for r in s.registry}
    for cid, (ptr, _) in s.pointers.items():
        ref = ptr["Home Ref"]
        if ref.startswith("personal:"):
            target = ref.split(":", 1)[1]
            if not d["lib_reachable"]:
                add("L-12", "WARNING" if L.checks.get("L-12", {}).get("unreachable_warning") else None)
            elif target not in reg or target not in s.homes:
                add("L-12")
    for rows_ in (s.sd, s.dsa):
        for r in rows_:
            prj, xid = r["Experience Note"].split("/")
            if prj == pid_cfg and xid not in s.notes:
                add("L-13")
            if xid in s.notes and prj != pid_cfg:
                add("L-17")
    for xid, n in s.notes.items():
        dr = n["id"]["Decision Record"]
        if dr != "-" and (dr not in s.drs or re.search(rf"^Experience ID:\s+{xid}$", s.drs[dr], re.M) is None):
            add("L-14")
        if n["id"]["Project ID"] != pid_cfg:
            add("L-17")
        cid = n["id"]["Concept ID"]
        if cid != "UNASSIGNED" and cid not in known:
            add("L-22")
        ev = events.get(n["id"]["Event ID"])
        kp = next((k for k in passes[ev[0]]["kp"] if k["Event ID"] == ev[1]["Event ID"]), None) if ev else None
        if ev is None or (kp and kp["Experience ID"] not in ("-", xid)):
            add("L-23")
    for did, text in s.drs.items():
        x = re.search(r"^Experience ID:\s+(\S+)$", text, re.M)
        prj = re.search(r"^Project ID:\s+(\S+)$", text, re.M)
        if not x or x.group(1) not in s.notes or s.notes[x.group(1)]["id"]["Decision Record"] != did:
            add("L-14")
        if prj and prj.group(1) != pid_cfg:
            add("L-17")
    for h in list(s.homes.values()) + list(s.local.values()):
        if any(a["experience_id"] in s.notes and a["project_id"] != pid_cfg for a in h["appearances"]):
            add("L-17")
    if int(d["hmap"].get("generated_from_graph_version", -1)) < s.graph.version:
        add("L-18")
    if d["lib"] and s.index != pm.build_index(env.P7, s):
        add("L-19")
    lib = store.roots["L"]
    lock = kv((lib / ".learning-write-lock" / "LOCK.md").read_text(encoding="utf-8")) \
        if (lib / ".learning-write-lock" / "LOCK.md").exists() else None
    if lock and lock.get("lock_id") in session_locks:
        add("L-21")
    return sorted(set(f))


# --- repair + procedure ------------------------------------------------------------

def rebuild(env, store, ctx, artifact):
    """Regenerate one DERIVED artifact from its authoritative source. Refuses anything else."""
    if not env.L.derived(artifact):
        return False
    d = load(env, store, ctx)
    if artifact == "LEARNING_STATE":
        st = dict(d["state"], **{k: str(v) for k, v in cm.rebuild_state(d["ledger"]).items()}, status="REBUILT")
        store.write(STATE, "# Learning State\n\n## State\n\n```text\n" + "\n".join(f"{k}: {v}" for k, v in st.items()) + "\n```\n")
    elif artifact == "LEARNING_QUEUE §A":
        store.write(QUEUE, render_queue(["work_unit_id", "label", "status", "reason", "deferred_at", "source"],
                                        queue_a_rows(d["ledger"]), env.P7.debt_cols, d["s"].debts))
    elif artifact == "HORIZONTAL_MAP":
        store.write(HMAP, render_hmap(d["s"].graph))
    elif artifact == "LIBRARY_INDEX":
        store.write(pm.IDX, render_index(env.P7, d["s"]))
    else:
        return False
    return True


def run(env, store, ctx, session_locks=(), repair=True):
    """§L.3. Returns {'result', 'check1', 'check2', 'repaired'}."""
    f1 = check(env, store, ctx, session_locks)
    out = {"check1": f1, "check2": None, "repaired": []}
    if result(env.L, f1) == "FAIL" or not repair:
        out["result"] = result(env.L, f1)
        return out
    for cid, sev in f1:
        target = env.L.checks.get(cid, {}).get("rebuild")
        if sev == "WARNING" and target and target not in out["repaired"] and rebuild(env, store, ctx, target):
            out["repaired"].append(target)
    if out["repaired"] and "L-20" in env.L.checks:
        out["check2"] = check(env, store, ctx, session_locks)
    else:
        repaired_ids = {c for c, _ in f1 if env.L.checks.get(c, {}).get("rebuild") in out["repaired"]}
        out["check2"] = [x for x in f1 if x[0] not in repaired_ids]
    out["result"] = result(env.L, out["check2"])
    return out
