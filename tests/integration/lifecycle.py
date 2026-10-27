"""End-to-end driver: one temporary target project through the full /learning pipeline.

Each stage calls the phase model that already encodes that protocol:
coverage (phase3) -> human sync (phase4) -> ULA + completion (phase5) -> map sync (phase6)
-> persistence (phase7) + write lock (06 §22.1) -> final integrity (07 §L).
State lives only in Markdown files under a temporary directory.
"""
import random
from pathlib import Path

import coverage_model as cm
import final_integrity as fi
import graph_model as gm
import hs_model as hs
import lock
import persist_model as pm
import ula_model as um
from files import (CONFIG, GRAPH, HMAP, LEDGER, QUEUE, STATE, kv, kv_doc, parse_ledger, parse_pass, queue_a_rows,
                   render_hmap, render_ledger, render_pass, render_queue)

QA_COLS = ["work_unit_id", "label", "status", "reason", "deferred_at", "source"]
TODAY = "2026-10-27"


class Env:
    """All protocols, parsed once from one skill directory."""

    def __init__(self, skill: Path):
        self.skill = skill
        self.P3 = cm.load_transitions(skill / "references" / "02_COVERAGE_PROTOCOL.md")
        self.P3_cols = cm.load_ledger_header(skill / "templates" / "COVERAGE_LEDGER_TEMPLATE.md")
        self.P4 = hs.Protocol(skill)
        self.P5 = um.Protocol(skill)
        self.P6 = gm.Protocol(skill)
        self.P7 = pm.Protocol(skill)
        self.L = fi.Protocol(skill)
        self.lock = lock.load_rules(skill)
        self.lock_fields = lock.lock_fields(skill)


class Project:
    def __init__(self, env, root: Path, prj, name, library=None, seed=1):
        self.env, self.rng = env, random.Random(seed)
        self.store = pm.Store(Path(root) / "project", Path(library) if library else Path(root) / "no-library")
        self.ctx = {"config": {"project_id": prj, "project_name": name,
                               "personal_library_path": str(library) if library else "UNCONFIGURED",
                               "work_unit_source": "phase-doc"}, "passes": {}, "events": {}, "artifacts": {}}
        self.ledger = cm.Ledger(env.P3_cols)
        self.passes, self.hs, self.debts, self.locks, self.writes = {}, {}, [], [], {}
        self.last_lock, self.release_result, self.fail_release = None, None, False
        self.store.write(CONFIG, kv_doc("Learning Config", "Config", dict(learning_config_version=1, **self.ctx["config"])))
        if not self.store.read(GRAPH):
            self.store.write(GRAPH, gm.Graph(0).render(env.P6))
            self.store.write(HMAP, render_hmap(gm.Graph(0)))
        self.commit_ledger()

    # --- config ------------------------------------------------------------------
    def set_config(self, **kw):
        self.ctx["config"].update(kw)
        self.store.write(CONFIG, kv_doc("Learning Config", "Config", dict(learning_config_version=1, **self.ctx["config"])))

    def configure_library(self, library: Path):
        self.store.roots["L"] = Path(library)
        self.set_config(personal_library_path=str(library))

    # --- coverage ----------------------------------------------------------------
    def commit_ledger(self):
        """Ledger commit; state and queue §A are regenerated after every commit (01 §3)."""
        self.store.write(LEDGER, render_ledger(self.ledger))
        st = dict(schema_version=1, status="OK", last_run=TODAY, **cm.rebuild_state(self.ledger))
        self.store.write(STATE, "# Learning State\n\n## State\n\n```text\n" + "\n".join(f"{k}: {v}" for k, v in st.items()) + "\n```\n")
        debts = pm.parse_table(pm.gm.section(self.store.read(QUEUE), "## B. Knowledge Debt"), self.env.P7.debt_cols) \
            if self.store.read(QUEUE) else []
        self.store.write(QUEUE, render_queue(QA_COLS, queue_a_rows(self.ledger), self.env.P7.debt_cols, debts))
        self.ledger = parse_ledger(self.env.P3_cols, self.store.read(LEDGER))

    def discover(self, seqs):
        added = cm.discover(self.ledger, [cm.unit(n) for n in seqs])
        self.commit_ledger()
        return [r["work_unit_id"] for r in added]

    def scope(self, arg):
        selected = cm.resolve_scope(self.ledger, arg) if not isinstance(arg, list) else \
            [self.ledger.by_id(w) for w in arg]
        cm.scope_commit(self.ledger, self.env.P3, selected, f"scope {arg}")
        self.commit_ledger()
        return [r["work_unit_id"] for r in selected]

    def open_coverage(self):
        return [r["work_unit_id"] for r in cm.open_coverage(parse_ledger(self.env.P3_cols, self.store.read(LEDGER)))]

    # --- human sync + ULA ----------------------------------------------------------
    def human_sync(self, pid, scope, changes, triggers=None):
        """03: events + debts; queue §B gets OPEN debts; pass file written."""
        out = hs.build_pass(self.env.P4, pid, scope, changes)
        triggers = triggers or {}
        evs = [um.event(e["Event ID"], e["Disposition"], pm.split(e["Work Units"]), triggers.get(e["Problem"], ()))
               for e in out["events"]]
        lp = um.Pass(pid, scope, evs, [{"origin": d["originating_event_id"], "status": "OPEN"} for d in out["debts"]])
        self.passes[pid], self.hs[pid] = lp, out
        cur = pm.parse_table(pm.gm.section(self.store.read(QUEUE), "## B. Knowledge Debt"), self.env.P7.debt_cols)
        new = [dict(d, resolution_ref="-") for d in out["debts"]]
        self.store.write(QUEUE, render_queue(QA_COLS, queue_a_rows(self.ledger), self.env.P7.debt_cols, cur + new))
        um.early_check(self.env.P5, lp)
        um.route_all(self.env.P5, lp)
        self.save_pass(pid)
        return out["events"]

    def event_id(self, pid, topic):
        return next(e["Event ID"] for e in self.hs[pid]["events"] if e["Problem"] == topic)

    def write_artifact(self, pid, eid, name, sections):
        rel = f"passes/{pid}/ula/{eid}/{name}.md"
        body = "\n\n".join(f"## {k}\n\n{v}" for k, v in sections.items())
        key = f"P:{rel}"
        self.writes[key] = self.writes.get(key, 0) + 1
        self.store.write(key, f"# {name}\n\n{body}\n")
        return rel

    def light(self, pid, eid, sections):
        lp = self.passes[pid]
        um.run_light(self.env.P5, lp, eid, [[]])
        rel = self.write_artifact(pid, eid, "LIGHT_ULA", sections)
        lp.routing[eid]["Artifact"] = rel
        self.ctx["artifacts"][rel] = {k.split(" ")[0] for k in sections if k.startswith("L")}
        self.save_pass(pid)
        return rel

    def full_until_review(self, pid, eid):
        lp = self.passes[pid]
        um.start_full(self.env.P5, lp, eid)
        self.write_artifact(pid, eid, "PROJECT_BRIEF", {"Brief": "project problem"})
        self.write_artifact(pid, eid, "ARCHITECTURE", {"Architecture": "status: PROPOSED"})
        lp.routing[eid]["Artifact"] = f"passes/{pid}/ula/{eid}/ARCHITECTURE.md"
        self.save_pass(pid)

    def full_after_review(self, pid, eid, sections):
        lp = self.passes[pid]
        um.review(self.env.P5, lp, eid, "approve")
        self.write_artifact(pid, eid, "ARCHITECTURE", {"Architecture": "status: FROZEN\napproved_by: user"})
        um.build(self.env.P5, lp, eid)
        rel = self.write_artifact(pid, eid, "CONTENT", sections)
        um.audit(self.env.P5, lp, eid, "READY TO FREEZE")
        self.write_artifact(pid, eid, "AUDIT", {"Recommendation": "READY TO FREEZE"})
        lp.routing[eid]["Artifact"] = rel
        self.ctx["artifacts"][rel] = {k.split(" ")[0] for k in sections if k.startswith("L")}
        self.save_pass(pid)
        return rel

    def complete(self, pid):
        lp = self.passes[pid]
        um.completion(self.env.P5, lp, self.ledger)
        self.commit_ledger()
        self.save_pass(pid)
        return lp.status

    def abandon(self, pid):
        um.abandon(self.passes[pid], self.ledger)
        self.save_pass(pid)

    # --- pass file -----------------------------------------------------------------
    def pass_file(self, pid):
        text = self.store.read(pm.pass_key(pid))
        return parse_pass(self.env.P5, self.env.P7.ms_cols, self.env.P7.kp_cols, text) if text else None

    def save_pass(self, pid, ms=None):
        lp, old = self.passes[pid], self.pass_file(pid)
        meta = {"learning_pass_id": pid, "pass_status": lp.status, "current_stage": lp.stage,
                "created_at": TODAY, "updated_at": TODAY, "selected_scope": "[" + ", ".join(lp.scope) + "]",
                "coverage_source": "phase-doc"}
        routing = [{k: (eid if k == "Event ID" else r[k]) for k in self.env.P5.routing_header} for eid, r in lp.routing.items()]
        self.store.write(pm.pass_key(pid), render_pass(self.env.P4, self.env.P5, self.env.P7.ms_cols, self.env.P7.kp_cols,
                                                         meta, self.hs[pid]["events"], routing,
                                                         ms if ms is not None else (old["ms"] if old else []),
                                                         old["kp"] if old else []))
        self.ctx["passes"][pid] = lp.status

    # --- map sync --------------------------------------------------------------------
    def map_sync(self, pid, nodes=None):
        """05 §8-§9. nodes: {topic: [node spec]} for each event that adds graph nodes."""
        lp, nodes = self.passes[pid], nodes or {}
        debt_of = {d["originating_event_id"]: d["debt_id"] for d in self.hs[pid]["debts"]}
        evs = []
        for e in self.hs[pid]["events"]:
            eid = e["Event ID"]
            evs.append({"id": eid, "disposition": e["Disposition"], "reusable": e["Reusable Signal"] != "-",
                        "ula_status": lp.routing.get(eid, {}).get("ULA Status"), "debt_id": debt_of.get(eid),
                        "nodes": nodes.get(e["Problem"], [])})
        graph = gm.Graph.parse(self.env.P6, self.store.read(GRAPH))
        mctx = {"artifacts": self.ctx["artifacts"], "debts": {d["debt_id"] for d in self.all_debts()}, "events": {}}
        new, statuses = gm.sync(self.env.P6, graph, {"id": pid, "status": lp.status, "events": evs}, mctx, self.rng)
        if new is not graph:
            self.store.write(GRAPH, new.render(self.env.P6))
            self.store.write(HMAP, render_hmap(new))
        ms = []
        for ev in evs:
            st = statuses.get(ev["id"], "NOT_APPLICABLE")
            ids = [next(n["node_id"] for n in new.nodes if n["canonical_name"] == c["name"] and ev["id"] in pm.split(n["source_event_ids"]))
                   for c in ev["nodes"]] if st == "COMPLETE" else []
            initial = "PENDING" if ev["disposition"] == "EXPERIENCE_ONLY" or (
                ev["disposition"] == "ULA_CANDIDATE" and ev["ula_status"] == "COMPLETE") else "NOT_APPLICABLE"
            ms.append({"Event ID": ev["id"], "Map Sync": st, "Node IDs": pm.join(ids), "Experience Persistence": initial})
        self.save_pass(pid, ms)
        return statuses

    def all_debts(self):
        return pm.parse_table(pm.gm.section(self.store.read(QUEUE), "## B. Knowledge Debt"), self.env.P7.debt_cols)

    # --- persistence -------------------------------------------------------------------
    def persist(self, pid, topic, concept=None, user=None, extra=None):
        """06: lock (if personal write possible) + atomic transaction. Returns persistence status."""
        e = next(x for x in self.hs[pid]["events"] if x["Problem"] == topic)
        eid, lp = e["Event ID"], self.passes[pid]
        ms = next(r for r in self.pass_file(pid)["ms"] if r["Event ID"] == eid)
        art = lp.routing.get(eid, {}).get("Artifact", "-")
        sections = self.artifact_sections(art)
        ev = {"id": eid, "pass": pid, "disposition": e["Disposition"], "title": topic,
              "concept": concept or {"name": topic, "meaning": "-"}, "category": e["Category"],
              "work_units": pm.split(e["Work Units"]), "evidence_status": e["Evidence Status"].split(" ")[0],
              "ula_status": lp.routing.get(eid, {}).get("ULA Status"), "reusable": e["Reusable Signal"] != "-",
              "concept_nodes": pm.split(ms["Node IDs"]), "priority": e["Knowledge Priority"],
              "experience": {}, "dsa": {}, "evidence": [],
              "artifact": {"mode": "LIGHT" if art.endswith("LIGHT_ULA.md") else "FULL", "path": art, "sections": sections}
              if sections else None}
        ev.update(extra or {})
        self.ctx["events"][eid] = ev
        lib = self.ctx["config"]["personal_library_path"]
        held = None
        if lib != "UNCONFIGURED":
            meta = {"lock_id": f"LK-{self.rng.getrandbits(32):08x}", "project_id": self.ctx["config"]["project_id"],
                    "learning_pass_id": pid, "created_at": f"{TODAY}T10:00", "operation": f"PERSIST {eid}"}
            got, info = lock.acquire(self.env.lock, Path(lib), meta)
            if got == "BLOCKED":
                self.last_lock = info
                return pm.write_status_only(self.env.P7, self.store, self.ctx, pm.State.load(self.env.P7, self.store, self.ctx),
                                            ev, "BLOCKED")
            held = meta["lock_id"]
            self.locks.append(held)
        try:
            status = pm.persist_event(self.env.P7, self.store, self.ctx, eid, self.rng, user)
            graph = gm.Graph.parse(self.env.P6, self.store.read(GRAPH))
            if kv(self.store.read(HMAP)).get("generated_from_graph_version") != str(graph.version):
                self.store.write(HMAP, render_hmap(graph))
            return status
        finally:
            if held:
                self.release_result = lock.release(self.env.lock, Path(lib), held, fail=self.fail_release)

    def artifact_sections(self, rel):
        if rel in ("-", "") or not rel.endswith((".md",)):
            return None
        text = self.store.read(f"P:{rel}")
        if not text:
            return None
        parts = text.split("\n## ")[1:]
        return {p.split("\n", 1)[0]: p.split("\n", 1)[1].strip() for p in parts}

    def promote(self):
        lib = Path(self.ctx["config"]["personal_library_path"])
        meta = {"lock_id": f"LK-{self.rng.getrandbits(32):08x}", "project_id": self.ctx["config"]["project_id"],
                "learning_pass_id": "-", "created_at": f"{TODAY}T10:00", "operation": "PROMOTE"}
        got, _ = lock.acquire(self.env.lock, lib, meta)
        if got == "BLOCKED":
            return "BLOCKED"
        try:
            return pm.promote(self.env.P7, self.store, self.ctx, self.rng)
        finally:
            lock.release(self.env.lock, lib, meta["lock_id"])

    # --- final integrity ---------------------------------------------------------------
    def final(self, repair=True):
        return fi.run(self.env, self.store, self.ctx, self.locks, repair)
