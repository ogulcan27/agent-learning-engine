"""Synthetic Phase 6 tests A-S plus consistency checks.

Usage: run_tests.py <skill_dir>
"""
import copy
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402
from graph_model import (Graph, Protocol, depth_view, fails, integrity, local_map, new_id, rename, root_map, split,
                         sync)

P = Protocol(skill_dir())
RESULTS = []
RNG = random.Random(6)
LIGHT = "passes/LP-1/ula/LE-1/LIGHT_ULA.md"
FULL = "passes/LP-2/ula/LE-3/CONTENT.md"
CTX = {"artifacts": {LIGHT: {"L1", "L2"}, FULL: {"L1", "L2", "L3", "L4"}}, "debts": {"KD-LP-4-01"}, "events": {}}
Q_MEANING = "işleri sıraya koyar"


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def roundtrip(g):
    return Graph.parse(P, g.render(P))


def ev(eid, disp, nodes=(), edges=(), **kw):
    e = {"id": eid, "disposition": disp, "nodes": list(nodes), "edges": list(edges)}
    e.update(kw)
    return e


def node(name, typ, meaning, parent=None, depth=(), artifacts=()):
    return {"name": name, "type": typ, "meaning": meaning, "parent": parent, "depth": list(depth),
            "artifacts": list(artifacts)}


def by(g, name):
    return next(n for n in g.nodes if n["canonical_name"] == name)


# Test A - first graph build
pass1 = {"id": "LP-1", "status": "COMPLETE", "events": [
    ev("LE-1", "ULA_CANDIDATE", ula_status="COMPLETE",
       nodes=[node("Async Processing", "DOMAIN", "uzun işi request dışına taşır"),
              node("Queue", "CONCEPT", Q_MEANING, "Async Processing", ["L1", "L2"], [LIGHT])]),
    ev("LE-2", "EXPERIENCE_ONLY", reusable=True,
       nodes=[node("Queue", "CONCEPT", Q_MEANING),
              node("Background Worker", "SYSTEM_COMPONENT", "kuyruktaki işi çalıştırır", "Async Processing")],
       edges=[{"source": "Background Worker", "relation": "USES", "target": "Queue",
               "meaning": "Background Worker USES Queue", "evidence": "VERIFIED (commit:9f3a1c2b7d4e)"},
              {"source": "Queue", "relation": "NEXT", "target": "Background Worker",
               "meaning": "İş kuyruktan worker'a geçer", "evidence": "VERIFIED (commit:9f3a1c2b7d4e)"}])]}
g0 = Graph()
g1, st = sync(P, g0, pass1, CTX, RNG)
g1 = roundtrip(g1)
check("A nodes created (root + 3)", len(g1.nodes), 4)
check("A semantic edges", sorted(e["relation_type"] for e in g1.edges), ["NEXT", "USES"])
check("A graph version 1", g1.version, 1)
check("A sync COMPLETE", st, {"LE-1": "COMPLETE", "LE-2": "COMPLETE"})
check("A Queue appearance once", by(g1, "Queue")["project_appearances"], "LP-1")
check("A integrity clean", fails(integrity(P, g1, CTX)), [])
view = root_map(g1)
check("A root map shows major block", view["text"], "[Async Processing] (+2)")
check("A original graph untouched", (g0.version, len(g0.nodes)), (0, 0))

# Test B - incremental update
pass2 = {"id": "LP-2", "status": "COMPLETE", "events": [
    ev("LE-3", "ULA_CANDIDATE", ula_status="COMPLETE",
       nodes=[node("Queue", "CONCEPT", Q_MEANING),
              node("Consumer Lag", "FAILURE_MODE", "worker kuyruğa yetişemez", "Queue", ["L1", "L2", "L3"], [FULL])],
       edges=[{"source": "Queue", "relation": "FAILS_WHEN", "target": "Consumer Lag",
               "meaning": "Queue FAILS_WHEN Consumer Lag", "evidence": "INFERRED"}])]}
queue_id = by(g1, "Queue")["node_id"]
g2, st = sync(P, g1, pass2, CTX, RNG)
g2 = roundtrip(g2)
check("B Queue node reused", by(g2, "Queue")["node_id"], queue_id)
check("B only delta added (+1 node, +1 edge)", (len(g2.nodes) - len(g1.nodes), len(g2.edges) - len(g1.edges)), (1, 1))
check("B graph version +1", g2.version, 2)
check("B Queue appearances", by(g2, "Queue")["project_appearances"], "LP-1; LP-2")

# Test C - idempotence
g3, st = sync(P, g2, pass2, CTX, RNG)
check("C node count unchanged", len(g3.nodes), len(g2.nodes))
check("C edge count unchanged", len(g3.edges), len(g2.edges))
check("C no appearance duplication", by(g3, "Queue")["project_appearances"], "LP-1; LP-2")
check("C version unchanged", g3.version, 2)
g3b, _ = sync(P, g1, pass1, CTX, RNG)
check("C first pass re-sync is a no-op", g3b.signature(), g1.signature())

# Test D - exact concept reuse
pass_d = {"id": "LP-5", "status": "COMPLETE", "events": [
    ev("LE-9", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Queue", "CONCEPT", Q_MEANING)])]}
gd, _ = sync(P, g2, pass_d, CTX, RNG)
check("D same meaning -> same node_id", by(gd, "Queue")["node_id"], queue_id)
check("D no new node", len(gd.nodes), len(g2.nodes))

# Test E - ambiguous same name
pass_e0 = {"id": "LP-6", "status": "COMPLETE", "events": [
    ev("LE-10", "EXPERIENCE_ONLY", reusable=True, nodes=[node("State", "CONCEPT", "uygulama durumu")])]}
ge, _ = sync(P, g2, pass_e0, CTX, RNG)
pass_e = {"id": "LP-7", "status": "COMPLETE", "events": [
    ev("LE-11", "ULA_CANDIDATE", ula_status="COMPLETE",
       nodes=[node("State", "CONCEPT", "gizli rejim durumu", depth=["L1", "L2"], artifacts=[LIGHT])])]}
ge2, st = sync(P, ge, pass_e, CTX, RNG)
check("E no silent merge -> BLOCKED", st, {"LE-11": "BLOCKED"})
check("E graph unchanged", (ge2.version, ge2.signature()), (ge.version, ge.signature()))

# Test F - rename
pass_f = {"id": "LP-8", "status": "COMPLETE", "events": [
    ev("LE-12", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Async Queue", "CONCEPT", "iş kuyruğu")])]}
gf, _ = sync(P, Graph(), pass_f, CTX, RNG)
fid = by(gf, "Async Queue")["node_id"]
rename(gf, fid, "Job Queue")
check("F same node_id after rename", by(gf, "Job Queue")["node_id"], fid)
check("F old name -> alias", by(gf, "Job Queue")["aliases"], "Async Queue")
pass_f2 = {"id": "LP-9", "status": "COMPLETE", "events": [
    ev("LE-13", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Async Queue", "CONCEPT", "iş kuyruğu")])]}
gf2, _ = sync(P, gf, pass_f2, CTX, RNG)
check("F old name resolves via alias", (len(gf2.nodes), by(gf2, "Job Queue")["node_id"]), (len(gf.nodes), fid))

# Test G - debt node
pass_g = {"id": "LP-4", "status": "COMPLETE", "events": [
    ev("LE-14", "KNOWLEDGE_DEBT", debt_id="KD-LP-4-01", nodes=[node("Vector Index", "CONCEPT", "benzer vektörü hızlı bulur")])]}
gg, st = sync(P, g2, pass_g, CTX, RNG)
vi = by(gg, "Vector Index")
check("G node_status DEBT", vi["node_status"], "DEBT")
check("G no invented depth", vi["available_depth"], "-")
check("G debt reference", vi["debt_id"], "KD-LP-4-01")
check("G DEBT label in root map", "[Vector Index] (DEBT)" in root_map(gg)["text"], True)
check("G DEBT without debt_id -> M-20 FAIL",
      ("M-20", "FAIL") in integrity(P, Graph(gg.version, [dict(n, debt_id="-") if n is vi else n for n in gg.nodes],
                                         gg.edges), CTX), True)
pass_g2 = {"id": "LP-10", "status": "COMPLETE", "events": [
    ev("LE-15", "ULA_CANDIDATE", ula_status="COMPLETE",
       nodes=[node("Vector Index", "CONCEPT", "benzer vektörü hızlı bulur", depth=["L1", "L2"], artifacts=[LIGHT])])]}
gg2, _ = sync(P, gg, pass_g2, CTX, RNG)
check("G DEBT -> ACTIVE keeps node_id", (by(gg2, "Vector Index")["node_status"], by(gg2, "Vector Index")["node_id"]),
      ("ACTIVE", vi["node_id"]))

# Test H - implementation detail
pass_h = {"id": "LP-11", "status": "COMPLETE", "events": [
    ev("LE-16", "IMPLEMENTATION_DETAIL", nodes=[node("Import Fix", "OTHER", "import düzeltmesi")])]}
gh, st = sync(P, g2, pass_h, CTX, RNG)
check("H not added", (st, gh.signature() == g2.signature()), ({"LE-16": "NOT_APPLICABLE"}, True))

# Test I - unresolved
pass_i = {"id": "LP-12", "status": "WAITING_USER", "events": [
    ev("LE-17", "UNRESOLVED", nodes=[node("Leakage", "CONCEPT", "geleceği kullanma")])]}
gi, st = sync(P, g2, pass_i, CTX, RNG)
check("I pass not COMPLETE -> no sync", (st, gi.version), ({}, g2.version))
pass_i2 = dict(pass_i, status="COMPLETE")
gi2, st = sync(P, g2, pass_i2, CTX, RNG)
check("I UNRESOLVED waits, not persisted", (st, len(gi2.nodes)), ({}, len(g2.nodes)))
forged = copy.deepcopy(g2)
forged.nodes[1]["source_event_ids"] += "; LE-17"
check("I ACTIVE node from UNRESOLVED -> M-19 FAIL",
      ("M-19", "FAIL") in integrity(P, forged, dict(CTX, events={"LE-17": pass_i["events"][0]})), True)

# Test J - edge vocabulary
pass_j = {"id": "LP-13", "status": "COMPLETE", "events": [
    ev("LE-18", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Queue", "CONCEPT", Q_MEANING)],
       edges=[{"source": "Queue", "relation": "MAGICALLY_CONNECTS", "target": "Background Worker"}])]}
gj, st = sync(P, g2, pass_j, CTX, RNG)
check("J unknown relation -> BLOCKED, graph unchanged", (st, gj.version), ({"LE-18": "BLOCKED"}, g2.version))
bad = copy.deepcopy(g2)
bad.edges[0]["relation_type"] = "MAGICALLY_CONNECTS"
check("J unknown relation -> M-05 FAIL", ("M-05", "FAIL") in integrity(P, bad, CTX), True)

# Test K - orphan edge
orphan = copy.deepcopy(g2)
orphan.edges[0]["target_node_id"] = "KN-deadbeef"
check("K orphan target -> M-04 FAIL", ("M-04", "FAIL") in integrity(P, orphan, CTX), True)
pass_k = {"id": "LP-14", "status": "COMPLETE", "events": [
    ev("LE-19", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Queue", "CONCEPT", Q_MEANING)],
       edges=[{"source": "Queue", "relation": "USES", "target": "Nonexistent Store"}])]}
gk, st = sync(P, g2, pass_k, CTX, RNG)
check("K orphan in delta -> BLOCKED", (st, gk.version), ({"LE-19": "BLOCKED"}, g2.version))


def mini(*pairs, edges=()):
    nodes = []
    for nid, parent in pairs:
        nodes.append({"node_id": nid, "canonical_name": nid, "node_type": "CONCEPT", "parent_id": parent,
                      "short_meaning": "-", "system_role": "-", "home_ref": "UNASSIGNED", "available_depth": "-",
                      "source_event_ids": "-", "source_artifacts": "-", "project_appearances": "-", "aliases": "-",
                      "node_status": "ACTIVE", "debt_id": "-", "superseded_by": "-"})
    es = [{"edge_id": f"KE-{i:04d}", "source_node_id": s, "relation_type": r, "target_node_id": t, "meaning": "-",
           "source_event_ids": "-", "evidence_status": "INFERRED"} for i, (s, r, t) in enumerate(edges, 1)]
    return Graph(1, nodes, es)


# Test L - hierarchy cycle
check("L A PART_OF B, B PART_OF A -> M-08 FAIL", ("M-08", "FAIL") in integrity(P, mini(("A", "B"), ("B", "A")), CTX), True)
check("L self parent -> M-09 FAIL", ("M-09", "FAIL") in integrity(P, mini(("A", "A")), CTX), True)

# Test M - non-hierarchy cycle
check("M DEPENDS_ON cycle allowed",
      fails(integrity(P, mini(("A", "-"), ("B", "-"), edges=[("A", "DEPENDS_ON", "B"), ("B", "DEPENDS_ON", "A")]), CTX)), [])

# Test N - root map clutter
big = Graph()
rng = random.Random(1)
nodes = [node(f"Domain {i}", "DOMAIN", f"alan {i}") for i in range(12)]
nodes += [node(f"Concept {i}", "CONCEPT", f"kavram {i}", f"Domain {i % 12}") for i in range(18)]
gn, _ = sync(P, big, {"id": "LP-15", "status": "COMPLETE",
                      "events": [ev("LE-20", "EXPERIENCE_ONLY", reusable=True, nodes=nodes)]}, CTX, rng)
view = root_map(gn)
check("N 30-node graph", len(gn.nodes) - 1, 30)
check("N root map shows <= 10 lines of blocks", len(view["node_ids"]) <= 10 and len(view["node_ids"]) >= 4, True)
check("N remainder summarized", bool(re.search(r"… \+\d+ block", view["text"])), True)

# Test O - recursive zoom
lag = by(g2, "Consumer Lag")["node_id"]
check("O breadcrumb WORLD → REGION → NODE", local_map(g2, lag)["breadcrumb"],
      "Project → Async Processing → Queue → Consumer Lag")
lm = local_map(g2, queue_id)
check("O local children", lm["children"], ["Consumer Lag"])
check("O relations shown with token", lm["relations"], ["-NEXT→ [Background Worker]", "-FAILS_WHEN→ [Consumer Lag]"])

# Test P - depth view
check("P L3 unavailable, no fabrication", depth_view(g2, queue_id, "L3"), "L3 unavailable. Mevcut: L1, L2.")
check("P L2 routes to artifact", depth_view(g2, queue_id, "L2")["artifact"], LIGHT)
claim = copy.deepcopy(g2)
by(claim, "Queue")["available_depth"] = "L1; L2; L4"
check("P depth without content -> M-14 FAIL", ("M-14", "FAIL") in integrity(P, claim, CTX), True)

# Test Q - atomic failure
pass_q = {"id": "LP-16", "status": "COMPLETE", "events": [
    ev("LE-21", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Retry Policy", "PATTERN", "hata sonrası tekrar dener", "Queue")]),
    ev("LE-22", "EXPERIENCE_ONLY", reusable=True, nodes=[node("Queue", "CONCEPT", Q_MEANING)],
       edges=[{"source": "Queue", "relation": "USES", "target": "Missing Node"}])]}
before = g2.signature()
gq, st = sync(P, g2, pass_q, CTX, RNG)
check("Q graph version unchanged", gq.version, g2.version)
check("Q existing graph unchanged (no partial write)", (gq.signature() == before, g2.signature() == before), (True, True))
check("Q map_sync BLOCKED / PENDING", st, {"LE-22": "BLOCKED", "LE-21": "PENDING"})

# Test R - coverage independence
lp_r = {"id": "LP-17", "status": "COMPLETE", "events": pass_k["events"]}
ledger_r = {"jira:INC-44": ("COVERED", "-")}
snap = (lp_r["status"], dict(ledger_r))
gr, st = sync(P, g2, lp_r, CTX, RNG)
check("R map sync BLOCKED", st, {"LE-19": "BLOCKED"})
check("R pass stays COMPLETE, ledger stays COVERED", (lp_r["status"], ledger_r), snap)

# Test S - stale map
gs = copy.deepcopy(g2)
gs.version = 4
check("S view v3 < graph v4 -> M-16 WARNING", ("M-16", "WARNING") in integrity(P, gs, CTX, view={"version": 3, "node_ids": []}), True)
regen = root_map(gs)
check("S regenerated view clean", [x for x in integrity(P, gs, CTX, view=regen) if x[0] == "M-16"], [])
check("S view newer than graph -> M-15 FAIL", ("M-15", "FAIL") in integrity(P, gs, CTX, view={"version": 5, "node_ids": []}), True)

# Test HA - hierarchy amendment (primary parent_id + secondary PART_OF)
check("HA-A parent DA + PART_OF DB -> PASS",
      fails(integrity(P, mini(("DA", "-"), ("DB", "-"), ("K", "DA"), edges=[("K", "PART_OF", "DB")]), CTX)), [])
check("HA-B parent DA + PART_OF DA -> M-21 FAIL (duplicate membership)",
      ("M-21", "FAIL") in integrity(P, mini(("DA", "-"), ("K", "DA"), edges=[("K", "PART_OF", "DA")]), CTX), True)
check("HA-C A parent B + B PART_OF A -> M-08 FAIL (combined cycle)",
      ("M-08", "FAIL") in integrity(P, mini(("A", "B"), ("B", "-"), edges=[("B", "PART_OF", "A")]), CTX), True)
check("HA-C2 A PART_OF B + B PART_OF A -> M-08 FAIL",
      ("M-08", "FAIL") in integrity(P, mini(("A", "-"), ("B", "-"), edges=[("A", "PART_OF", "B"), ("B", "PART_OF", "A")]), CTX), True)
check("HA-D A PART_OF B + A PART_OF C -> PASS",
      fails(integrity(P, mini(("A", "-"), ("B", "-"), ("C", "-"), edges=[("A", "PART_OF", "B"), ("A", "PART_OF", "C")]), CTX)), [])
pass_ha = {"id": "LP-18", "status": "COMPLETE", "events": [
    ev("LE-30", "ULA_CANDIDATE", ula_status="COMPLETE",
       nodes=[node("State Estimation", "DOMAIN", "gizli durumu tahmin eder"),
              node("Bayesian Filtering", "DOMAIN", "inancı gözlemle günceller"),
              dict(node("Kalman Filter", "CONCEPT", "lineer Gauss filtre", "State Estimation", ["L1", "L2"], [LIGHT]),
                   also_part_of=["Bayesian Filtering"])])]}
gha, st = sync(P, Graph(), pass_ha, CTX, random.Random(7))
kf = by(gha, "Kalman Filter")["node_id"]
lm = local_map(gha, kf)
check("HA-E sync PASS", (st, fails(integrity(P, gha, CTX))), ({"LE-30": "COMPLETE"}, []))
check("HA-E primary breadcrumb unchanged", lm["breadcrumb"], "Project → State Estimation → Kalman Filter")
check("HA-E secondary shown as Also Part Of", lm["also_part_of"], ["Bayesian Filtering"])
check("HA-E PART_OF not listed as plain relation", lm["relations"], [])
check("HA-E domain view lists secondary member",
      local_map(gha, by(gha, "Bayesian Filtering")["node_id"])["secondary_members"], ["Kalman Filter"])
check("HA-E primary children unaffected", local_map(gha, by(gha, "Bayesian Filtering")["node_id"])["children"], [])
check("HA-F membership not emitted as DEPENDS_ON / USES",
      sorted(e["relation_type"] for e in gha.edges), ["PART_OF"])

# Extra
check("X roundtrip preserves graph", roundtrip(g2).signature(), g2.signature())
check("X node id format KN-8hex", all(re.fullmatch(r"KN-[0-9a-f]{8}", n["node_id"]) for n in g2.nodes), True)
other, _ = sync(P, Graph(), pass1, CTX, random.Random(99))
check("X id not derived from name", by(other, "Queue")["node_id"] != queue_id, True)


class Fixed:
    def __init__(self, values):
        self.values = list(values)

    def getrandbits(self, _):
        return self.values.pop(0)


taken = Graph(1, [dict(g2.nodes[0], node_id="KN-00000001")])
check("X id collision skipped", new_id(taken, Fixed([1, 2])), "KN-00000002")
check("X 8 node types", len(P.node_types), 8)
check("X 3 node statuses", P.node_status, ["ACTIVE", "DEBT", "SUPERSEDED"])
check("X 12 relations", len(P.relations), 12)
check("X PART_OF self target -> M-09 FAIL",
      ("M-09", "FAIL") in integrity(P, mini(("A", "-"), edges=[("A", "PART_OF", "A")]), CTX), True)
check("X duplicate semantic edge -> M-11 FAIL",
      ("M-11", "FAIL") in integrity(P, mini(("A", "-"), ("B", "-"), edges=[("A", "USES", "B"), ("A", "USES", "B")]), CTX), True)
sup = mini(("A", "-"))
sup.nodes[0]["node_status"] = "SUPERSEDED"
check("X SUPERSEDED without pointer -> M-10 FAIL", ("M-10", "FAIL") in integrity(P, sup, CTX), True)
check("X sync COMPLETE but event absent -> M-18 FAIL",
      ("M-18", "FAIL") in integrity(P, g2, dict(CTX, sync={"LE-99": "COMPLETE"})), True)
dup = copy.deepcopy(g2)
by(dup, "Queue")["project_appearances"] = "LP-1; LP-1"
check("X duplicate appearance -> M-17 FAIL", ("M-17", "FAIL") in integrity(P, dup, CTX), True)
check("X view with unknown node -> M-12 WARNING",
      ("M-12", "WARNING") in integrity(P, g2, CTX, view={"version": 2, "node_ids": ["KN-ffffffff"]}), True)

report(RESULTS)
