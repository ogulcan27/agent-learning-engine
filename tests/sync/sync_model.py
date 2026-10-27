"""Reference model of 08_HUMAN_SYNC_STATE: standalone, incremental Human Sync over a real temporary git project.

Rules (statuses, authority, scope sets, retrieval plan, materiality, sync-only writes, full-mode reuse,
07 §S checks, template columns and sections) are parsed from the skill files.
Judgment inputs (materiality of a delta, record text) come from fixtures.
Every evidence read goes through Reader.log so tests can assert what was (not) read.
"""
import hashlib
import re
import subprocess
from pathlib import Path

TICK = re.compile(r"`([A-Z_]+)`")
KV = re.compile(r"^(\w+):[ \t]*(.*?)[ \t]*$", re.M)
SYNC = "docs/learning/sync"
STATE_F, CONTEXT_F = f"{SYNC}/HUMAN_SYNC_STATE.md", f"{SYNC}/PROJECT_SYNC_CONTEXT.md"
CONFIG_F = "docs/learning/state/LEARNING_CONFIG.md"
CHECKPOINT = re.compile(r"^(git:[0-9a-f]{12}|fp:[0-9a-f]{16})$")


def section(text, heading):
    level = len(heading) - len(heading.lstrip("#"))
    body = text.split(heading, 1)[1]
    stop = re.search(r"\n#{1,%d} " % level, body)
    return body[: stop.start()] if stop else body


def tables(block):
    out, cur = [], []
    for line in block.splitlines() + [""]:
        if line.startswith("|"):
            cur.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif cur:
            out.append(cur[2:])
            cur = []
    return out


def header(block):
    return [c.strip() for c in next(l for l in block.splitlines() if l.startswith("|")).strip("|").split("|")]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")


class Protocol:
    def __init__(self, skill: Path):
        p = (skill / "references" / "08_HUMAN_SYNC_STATE.md").read_text(encoding="utf-8")
        self.statuses = [TICK.findall(r[0])[0] for r in tables(section(p, "### 3.1 Sync status"))[0]]
        self.authority = {r[0].strip("`"): (r[1], r[2]) for r in tables(section(p, "## 3. Storage"))[0]}
        self.material = {TICK.findall(r[0])[0]: TICK.findall(r[1])[0] for r in tables(section(p, "## 6. Staleness"))[0]}
        dep = tables(section(p, "### 6.1 Dependency freshness"))
        self.dep_rules = {r[0]: r[1] for r in dep[0]}
        self.impact = {TICK.findall(r[0])[0]: TICK.findall(r[1])[0] for r in dep[1]}
        scope = tables(section(p, "## 7. Sync scope"))[0]
        self.scope = {re.match(r"`sync ?([^`]*)`", r[0]).group(1): [x.strip() for x in re.search(r"`([^`]+)`", r[1]).group(1).split("∪")]
                      for r in scope}
        self.plan = {TICK.findall(r[0])[0]: (TICK.findall(r[1]), TICK.findall(r[2]))
                     for r in tables(section(p, "## 8. Retrieval plan"))[0]}
        self.sync_only = {r[0].strip("`"): r[1] for r in tables(section(p, "## 11. Sync-only run loop"))[0]}
        self.write_rules = {r[0]: r[1] for r in tables(section(p, "### 11.1 Write"))[0]}
        self.reuse = [(r[0], TICK.findall(r[1])) for r in tables(section(p, "## 12. Full mode reuse"))[0]]
        ctx = section(p, "## 10. Rolling context")
        self.ctx_items = int(re.search(r"en fazla (\d+) madde", ctx).group(1))
        self.ctx_lines = int(re.search(r"en fazla (\d+) satır", ctx).group(1))
        t = skill / "templates"
        self.state_cols = header(section((t / "HUMAN_SYNC_STATE_TEMPLATE.md").read_text(encoding="utf-8"), "## Work Units"))
        self.record_sections = [h for h in re.findall(r"^## (.+)$", (t / "HUMAN_SYNC_RECORD_TEMPLATE.md").read_text(encoding="utf-8"), re.M)
                                if h != "Header"]
        self.ctx_sections = [h for h in re.findall(r"^## (.+)$", (t / "PROJECT_SYNC_CONTEXT_TEMPLATE.md").read_text(encoding="utf-8"), re.M)
                             if h != "Header"]
        s07 = section((skill / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8"), "## S. Human Sync State Integrity")
        self.checks = {r[0]: r[2] for r in tables(s07)[0]}


# --- project fixture -------------------------------------------------------------

class Repo:
    """Temporary git project. PLAN.md lists steps: '## Step N — label', 'Paths: a; b', optional 'Depends: Step k'."""

    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)
        git(root, "init", "-q")
        self.steps = {}

    def write(self, rel, text):
        f = self.root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(text.encode("utf-8"))

    def commit(self, msg):
        git(self.root, "add", "-A")
        git(self.root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", msg)

    def step(self, n, paths, depends=None, body="v1"):
        self.steps[n] = (paths, depends)
        for p in paths:
            if not (self.root / p).exists():
                self.write(p, f"# step {n} {p}\n{body}\n")
        plan = "# Plan\n\n" + "\n".join(
            f"## Step {k} — Step {k}\n\nPaths: {'; '.join(ps)}\n" + (f"Depends: Step {d}\n" if d else "") + "\n"
            for k, (ps, d) in sorted(self.steps.items()))
        self.write("PLAN.md", plan)
        self.commit(f"step {n}")


def wu(n):
    return f"phase-doc:PLAN.md#step-{n}"


def discover(root):
    """02 §3-§4 read-only discovery from PLAN.md: work unit id, seq, label, paths, explicit refs."""
    plan = (root / "PLAN.md").read_text(encoding="utf-8")
    out = []
    for n, body in re.findall(r"^## Step (\d+) — .*?\n(.*?)(?=^## |\Z)", plan, re.M | re.S):
        paths = re.search(r"^Paths: (.+)$", body, re.M).group(1).split("; ")
        dep = re.search(r"^Depends: Step (\d+)$", body, re.M)
        out.append({"work_unit_id": wu(n), "seq": int(n), "label": f"Step {n}", "paths": paths,
                    "refs": [wu(dep.group(1))] if dep else []})
    return out


# --- checkpoint (08 §5) -------------------------------------------------------------

def files_under(root, paths):
    for p in paths:
        f = root / p
        yield from ([f] if f.is_file() else sorted(x for x in f.rglob("*") if x.is_file()) if f.exists() else [])


def fingerprint(root, paths):
    lines = sorted(f"{f.relative_to(root).as_posix()}\t{sha(f.read_bytes())}" for f in files_under(root, paths))
    return sha("\n".join(lines).encode())[:16]


def checkpoint(root, paths):
    head = git(root, "rev-parse", "HEAD").stdout.strip()
    dirty = git(root, "status", "--porcelain", "--", *paths).stdout.strip() if head else "x"
    return f"git:{head[:12]}" if head and not dirty else f"fp:{fingerprint(root, paths)}"


def changed(root, cp, paths):
    if cp.startswith("git:"):
        return git(root, "diff", "--quiet", cp[4:], "--", *paths).returncode != 0
    return fingerprint(root, paths) != cp[3:]


# --- render / parse -------------------------------------------------------------------

def kv(text):
    return dict(KV.findall(text.split("```text", 1)[1].split("```", 1)[0])) if text and "```text" in text else {}


def kv_block(title, d):
    return f"# {title}\n\n## Header\n\n```text\n" + "\n".join(f"{k}: {v}" for k, v in d.items()) + "\n```\n"


def render_state(P, prj, rows):
    lines = ["| " + " | ".join(P.state_cols) + " |", "|" + "---|" * len(P.state_cols)]
    lines += ["| " + " | ".join(str(r[c]) for c in P.state_cols) + " |" for r in sorted(rows, key=lambda r: r["seq"])]
    return kv_block("Human Sync State", {"human_sync_state_version": 1, "project_id": prj}) + "\n## Work Units\n\n" + "\n".join(lines) + "\n"


def parse_state(P, text):
    rows = [dict(zip(P.state_cols, r)) for r in tables(section(text, "## Work Units"))[0]]
    for r in rows:
        r["seq"] = int(r["seq"])
    return kv(text), rows


def record_id(work_unit_id):
    return "HS-" + sha(work_unit_id.encode())[:8]


def render_record(P, head, content):
    body = "\n\n".join(f"## {s}\n\n{content.get(s, 'Yok.')}" for s in P.record_sections)
    return kv_block("Human Sync Record", head) + "\n" + body + "\n"


def split(v):
    return [] if v in ("-", "") else v.split(";")


# --- engine -------------------------------------------------------------------------------

class Reader:
    def __init__(self):
        self.log = []

    def read(self, kind, unit="-"):
        self.log.append((kind, unit))


class Blocked(Exception):
    pass


class Sync:
    """One active project root. run() = 08 §11 sync-only loop. full_sources() = 08 §12."""

    def __init__(self, P, root: Path):
        self.P, self.root = P, root

    def path(self, rel):
        return self.root / rel

    def read(self, rel):
        f = self.path(rel)
        return f.read_text(encoding="utf-8") if f.exists() else None

    def config(self):
        return dict(KV.findall(self.read(CONFIG_F) or ""))

    def load(self):
        text = self.read(STATE_F)
        head, rows = parse_state(self.P, text) if text else ({}, [])
        recs = {f.stem: f.read_text(encoding="utf-8") for f in self.path(f"{SYNC}/records").glob("HS-*.md")}
        return head, rows, recs, self.read(CONTEXT_F)

    # 07 §S
    def integrity(self, head, rows, recs, ctx, prj):
        out, ids = [], [r["work_unit_id"] for r in rows]
        if head and head.get("project_id") != prj:
            out.append("S-05")
        for r in rows:
            if r["sync_status"] not in self.P.statuses:
                out.append("S-07")
            if r["sync_status"] in ("SYNCED", "STALE") and r["record_id"] not in recs:
                out.append("S-01")
                continue
            if r["sync_status"] == "UNSYNCED":
                continue
            rh = kv(recs[r["record_id"]])
            if r["sync_status"] == "SYNCED" and not (CHECKPOINT.match(r["checkpoint"]) and CHECKPOINT.match(rh.get("checkpoint", ""))):
                out.append("S-02")
            if rh.get("work_unit_id") != r["work_unit_id"]:
                out.append("S-03")
            if rh.get("project_id") != prj:
                out.append("S-04")
            if rh.get("record_version") != r["record_version"]:
                out.append("S-06")
            if any(p in ("", "-") or p.startswith("/") or ":" in p or ".." in p for p in split(r["evidence_paths"]) or [""]):
                out.append("S-09")
            if any(d not in ids for d in split(r["depends_on"])):
                out.append("S-10")
        if len(ids) != len(set(ids)) or len([r["record_id"] for r in rows if r["record_id"] != "-"]) != \
                len({r["record_id"] for r in rows if r["record_id"] != "-"}):
            out.append("S-08")
        if set(recs) - {r["record_id"] for r in rows}:
            out.append("S-12")
        if ctx:
            ch = kv(ctx)
            if ch.get("project_id") != prj:
                out.append("S-11")
            want = sorted(f"{r['record_id']}@{r['record_version']}" for r in rows if r["sync_status"] == "SYNCED")
            if sorted(split(ch.get("source_records", "-").replace(" ", ""))) != want:
                out.append("S-13")
            if len(ctx.splitlines()) > self.P.ctx_lines:
                out.append("S-14")
        return sorted(set(out))

    @staticmethod
    def overwrites(writes, pre_recs):
        """07 S-16: an existing record may only be replaced by pre-image record_version + 1."""
        return [k for k, v in writes.items() if "/records/" in k and Path(k).stem in pre_recs
                and int(kv(v)["record_version"]) != int(kv(pre_recs[Path(k).stem]).get("record_version", "0")) + 1]

    def fails(self, findings):
        return [c for c in findings if self.P.checks.get(c) == "FAIL"]

    def protected(self):
        """Files sync-only must not change (08 §11 table rows marked NO)."""
        names = {"COVERAGE_LEDGER.md": "docs/learning/state/COVERAGE_LEDGER.md", "LEARNING_STATE.md": "docs/learning/state/LEARNING_STATE.md",
                 "LEARNING_QUEUE.md": "docs/learning/state/LEARNING_QUEUE.md", "passes/": "docs/learning/passes",
                 "maps/": "docs/learning/maps", "concepts/": "docs/learning/concepts", "experiences/": "docs/learning/experiences"}
        rels = [v for k, v in names.items() if self.P.sync_only.get(k) == "NO"]
        return {f.relative_to(self.root).as_posix(): sha(f.read_bytes()) for f in files_under(self.root, rels)}

    def propagate(self, up, rows, judge, rd):
        """08 §6.1: bounded dependency freshness from one materially changed unit."""
        rules, seen, queue = self.P.dep_rules, set(), [up]
        while queue:
            x = queue.pop(0)
            for d in sorted(rows, key=lambda r: r["seq"]):
                edge = x["work_unit_id"] in split(d["depends_on"]) if rules["edges"] == "EXPLICIT_DEPENDS_ON" else d["seq"] > x["seq"]
                if d["sync_status"] != "SYNCED" or d["work_unit_id"] in seen or not edge:
                    continue
                seen.add(d["work_unit_id"])
                if rules["evidence"] == "RECORDS_FIRST":
                    rd.read("RECORD", d["work_unit_id"])
                else:
                    rd.read("RAW", f"{d['work_unit_id']}|*")
                if self.P.impact[judge.get(("impact", x["work_unit_id"], d["work_unit_id"]), "UNKNOWN")] == "STALE":
                    d["sync_status"] = "STALE"
                    queue.append(d)
                elif rules["transitive"] != "ON_MATERIAL_IMPACT":
                    queue.append(d)

    def deps(self, unit, rows):
        """08 §8: explicit refs + path overlap with earlier units (state only)."""
        earlier = [r for r in rows if r["seq"] < unit["seq"]]
        overlap = [r["work_unit_id"] for r in earlier if set(unit["paths"]) & set(split(r["evidence_paths"]))]
        return sorted(set(unit["refs"]) | set(overlap), key=lambda w: int(w.rsplit("-", 1)[1]))

    def targets(self, arg, rows):
        pos = max([r["seq"] for r in rows if r["sync_status"] in ("SYNCED", "STALE")], default=0)
        sets = self.P.scope[arg] if arg in self.P.scope else self.P.scope["<work-unit-id>"]
        cur = max(rows, key=lambda r: r["seq"]) if rows else None
        pick = {
            "UNSYNCED_AFTER": lambda r: r["sync_status"] == "UNSYNCED" and r["seq"] > pos,
            "UNSYNCED_BEFORE": lambda r: r["sync_status"] == "UNSYNCED" and r["seq"] <= pos,
            "STALE": lambda r: r["sync_status"] == "STALE",
            "CURRENT": lambda r: r is cur and r["sync_status"] != "SYNCED",
            "MATCH": lambda r: r["work_unit_id"] == arg,
        }
        return sorted((r for r in rows if any(pick[s](r) for s in sets)), key=lambda r: r["seq"])

    def run(self, arg="", judge=None, reader=None, approve_id=False, fail_on=None, today="2026-10-27", skip_state=False):
        """08 §11. Returns footer dict. Raises Blocked on 07 §S FAIL or missing approval.
        skip_state=True reproduces a run that never read HUMAN_SYNC_STATE (smoke-test incident)."""
        judge, rd = judge or {}, reader or Reader()
        cfg = self.config()
        if not cfg:
            raise Blocked("INIT_REQUIRED")
        prj = cfg.get("project_id", "UNCONFIGURED")
        if prj == "UNCONFIGURED":
            if not approve_id:
                raise Blocked("PROJECT_ID")
            prj = "PRJ-" + sha(str(self.root).encode())[:8]
            self.path(CONFIG_F).write_bytes((self.read(CONFIG_F).replace("project_id: UNCONFIGURED", f"project_id: {prj}")).encode())
        head, rows, recs, ctx = self.load()
        pre_recs = dict(recs)
        if skip_state:
            head, rows, recs, ctx = {}, [], {}, None
        if ctx:
            rd.read("CONTEXT")
        found = self.integrity(head, rows, recs, ctx, prj)
        if self.fails(found):
            raise Blocked(",".join(self.fails(found)))
        before = self.protected()
        rd.read("DISCOVERY", "PLAN.md")
        units = {u["work_unit_id"]: u for u in discover(self.root)}
        known = {r["work_unit_id"] for r in rows}
        for u in units.values():
            if u["work_unit_id"] not in known:
                rows.append({"work_unit_id": u["work_unit_id"], "seq": u["seq"], "label": u["label"], "sync_status": "UNSYNCED",
                             "record_id": "-", "record_version": "-", "checkpoint": "-", "evidence_paths": ";".join(u["paths"]),
                             "depends_on": "-", "synced_at": "-"})
        state_changed = len(rows) != len(known)
        for r in rows:  # 08 §6
            if r["sync_status"] == "SYNCED" and changed(self.root, r["checkpoint"], split(r["evidence_paths"])):
                rd.read("DELTA", r["work_unit_id"])
                if self.P.material[judge.get(("material", r["work_unit_id"]), "UNKNOWN")] == "STALE":
                    r["sync_status"] = "STALE"
                    self.propagate(r, rows, judge, rd)
                else:
                    r["checkpoint"] = checkpoint(self.root, split(r["evidence_paths"]))
                state_changed = True
        by_id = {r["work_unit_id"]: r for r in rows}
        unit = lambda r: dict(units.get(r["work_unit_id"], {"seq": r["seq"], "paths": split(r["evidence_paths"]), "refs": []}),
                              work_unit_id=r["work_unit_id"])
        todo = self.targets(arg, rows)
        todo += [by_id[d] for r in list(todo) for d in self.deps(unit(r), rows)  # 08 §8 step 4: STALE dependency first
                 if by_id[d]["sync_status"] == "STALE" and by_id[d] not in todo]
        todo = sorted({id(r): r for r in todo}.values(), key=lambda r: r["seq"])
        synced, refreshed, writes = [], [], {}
        for r in todo:
            u = unit(r)
            deps = self.deps(u, rows)
            reads, never = self.P.plan[r["sync_status"]]
            if "DEP_RECORDS" in reads:
                for d in deps:
                    rd.read("RECORD", d)
            if "OWN_RECORD" in reads:
                rd.read("RECORD", r["work_unit_id"])
            if "DELTA" in reads and ("DELTA", r["work_unit_id"]) not in rd.log:
                rd.read("DELTA", r["work_unit_id"])
            if "RAW_EVIDENCE" in reads:
                for p in u["paths"]:
                    rd.read("RAW", f"{r['work_unit_id']}|{p}")
            (refreshed if r["sync_status"] == "STALE" else synced).append(r["work_unit_id"])
            rid = record_id(r["work_unit_id"])
            ver = 1 if r["record_version"] == "-" else int(r["record_version"]) + 1
            cp = checkpoint(self.root, u["paths"])
            content = judge.get(("hs", r["work_unit_id"]), {"Purpose": f"{r['label']} problem → action → result (v{ver})",
                                                               "Dependencies": ", ".join(deps) or "Yok."})
            writes[f"{SYNC}/records/{rid}.md"] = render_record(self.P, {
                "record_id": rid, "project_id": prj, "work_unit_id": r["work_unit_id"], "record_version": ver,
                "checkpoint": cp, "updated_at": today}, content)
            r.update(sync_status="SYNCED", record_id=rid, record_version=str(ver), checkpoint=cp,
                     evidence_paths=";".join(u["paths"]), depends_on=";".join(deps) or "-", synced_at=today)
        if not todo and not state_changed and ctx and "S-13" not in found:
            return {"result": "UP_TO_DATE", "synced": [], "refreshed": [], "reused": len(rows), "reads": rd.log,
                    "stale": [r["work_unit_id"] for r in rows if r["sync_status"] == "STALE"], "ula": "NOT RUN", "coverage": "UNCHANGED"}
        all_recs = dict(recs, **{Path(k).stem: v for k, v in writes.items()})
        writes[CONTEXT_F] = self.context(prj, rows, all_recs, today)
        writes[STATE_F] = render_state(self.P, prj, rows)
        cand_head, cand_rows = parse_state(self.P, writes[STATE_F])
        if self.overwrites(writes, pre_recs) and self.P.checks.get("S-16") == "FAIL":
            raise Blocked("S-16")
        if self.fails(self.integrity(cand_head, cand_rows, all_recs, writes[CONTEXT_F], prj)):
            raise Blocked("candidate integrity")
        self.write_all(writes, fail_on)
        if self.protected() != before:
            raise Blocked("S-15")
        return {"result": "COMPLETE", "synced": synced, "refreshed": refreshed, "ula": "NOT RUN", "coverage": "UNCHANGED",
                "reused": len([r for r in rows if r["sync_status"] == "SYNCED"]) - len(synced) - len(refreshed),
                "stale": [r["work_unit_id"] for r in rows if r["sync_status"] == "STALE"], "reads": rd.log}

    def context(self, prj, rows, recs, today):
        """08 §10: derived from SYNCED records only; bounded; rewritten, never appended."""
        ok = [r for r in sorted(rows, key=lambda r: r["seq"]) if r["sync_status"] == "SYNCED"]
        n = self.P.ctx_items
        body = {s: [] for s in self.P.ctx_sections}
        body["Components"] = [f"- {r['label']}" for r in ok][-n:]
        body["Current Position"] = [f"- {ok[-1]['label']}"] if ok else []
        body["Open Points"] = [f"- STALE: {r['label']}" for r in rows if r["sync_status"] == "STALE"][:n]
        src = "; ".join(f"{r['record_id']}@{r['record_version']}" for r in ok) or "-"
        text = kv_block("Project Sync Context", {"project_id": prj, "source_records": src, "updated_at": today})
        return text + "".join(f"\n## {s}\n\n" + ("\n".join(v) + "\n" if v else "") for s, v in body.items())

    def write_all(self, writes, fail_on):
        """08 §11.1: pre-images; records → context → state (commit point); restore on error."""
        order = sorted(k for k in writes if "/records/" in k) + [CONTEXT_F, STATE_F]
        pre = {k: (self.path(k).read_bytes() if self.path(k).exists() else None) for k in order}
        try:
            for k in order:
                if k == fail_on:
                    raise OSError(f"injected write failure: {k}")
                self.path(k).parent.mkdir(parents=True, exist_ok=True)
                self.path(k).write_bytes(writes[k].encode("utf-8"))
        except OSError:
            for k, b in pre.items():
                if b is None:
                    self.path(k).unlink(missing_ok=True)
                else:
                    self.path(k).write_bytes(b)
            raise Blocked("write error")

    def full_sources(self, unit_ids, judge=None, reader=None):
        """08 §12: Human Sync source per selected unit in full mode."""
        judge, rd = judge or {}, reader or Reader()
        _, rows, _, _ = self.load()
        by_id, out = {r["work_unit_id"]: r for r in rows}, {}
        for w in unit_ids:
            r = by_id.get(w)
            st = r["sync_status"] if r else "UNSYNCED"
            if st == "SYNCED" and changed(self.root, r["checkpoint"], split(r["evidence_paths"])) and                     self.P.material[judge.get(("material", w), "UNKNOWN")] == "STALE":
                st = "STALE"
            src = self.P.reuse[0][1] if st == "SYNCED" else next(s for c, s in self.P.reuse if c.startswith(f"`{st}`"))
            for s in src:
                if s == "RAW_EVIDENCE":
                    for p in (r and split(r["evidence_paths"])) or [w]:
                        rd.read("RAW", f"{w}|{p}")
                else:
                    rd.read(s.replace("OWN_RECORD", "RECORD"), w)
            out[w] = src
        return out
