"""Phase 8 end-to-end integration tests A-N, identity chain, lock and final integrity checks.

Usage: run_tests.py [<skill_dir>]
Every scenario uses a new temporary target project and a temporary personal library.
"""
import atexit
import copy
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402

use("phase3", "phase4", "phase5", "phase6", "phase7", "integration")
import coverage_model as cm  # noqa: E402
import final_integrity as fi  # noqa: E402
import graph_model as gm  # noqa: E402
import lock  # noqa: E402
import persist_model as pm  # noqa: E402
import ula_model as um  # noqa: E402
from files import CONFIG, GRAPH, HMAP, LEDGER, QUEUE, STATE, parse_ledger  # noqa: E402
from lifecycle import Env, Project  # noqa: E402

ENV = Env(skill_dir())
TMP = Path(tempfile.mkdtemp(prefix="p8_e2e_"))
atexit.register(shutil.rmtree, TMP, True)
RESULTS = []
V = "VERIFIED (commit:9f3a1c2b7d4e; test:tests/test_worker.py)"
Q_MEAN = "işleri sıraya koyar"
LIGHT = {"L0 — Local Map": "Request → Queue → Worker",
         "L1 — Simple Explanation": "Queue işleri sıraya koyar. Worker işi sonra alır.",
         "L2 — Mechanism": "Producer mesajı yazar. Broker mesajı saklar. Consumer mesajı alır ve ack gönderir.",
         "Retrieval": "Queue neden request süresini kısaltır?"}
FULL = {"Local Map": "Client → Rate Limiter → API",
        "L1 — Simple Explanation": "Rate limiter istek sayısını sınırlar.",
        "L2 — Mechanism": "Token bucket her istekte bir token harcar. Token bitince istek reddedilir.",
        "L3 — Theory": "Token bucket ortalama hızı ve burst boyutunu ayrı kontrol eder.",
        "L4 — Math / Formalism": "tokens(t) = min(b, tokens(t0) + r (t - t0))",
        "Retrieval Check": "Burst neden kabul edilir?", "R — Reference Links": "RFC 6585"}
SD_EXP = {"Problem": "Rapor isteği 40 saniye sürüyordu", "Constraint": "HTTP timeout 30 saniye",
          "Why It Appeared": "Uzun işi request dışına taşımak gerekti", "Alternatives": "sync call; background queue",
          "Selected": "background queue", "Why Selected": "request hemen döner", "Trade-off": "eventual result",
          "Failure Mode": "consumer lag", "Observed Result": "p95 300 ms", "Reusable Signal": "Uzun iş + timeout → queue düşün"}


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def codes(findings, sev=None):
    return {c for c, s in findings if sev in (None, s)}


def wu(n):
    return f"phase-doc:PLAN.md#step-{n}"


def change(n, topic, **kw):
    """A Human Sync change on work unit n (03 §8-§13 inputs)."""
    c = {"wu": wu(n), "kind": "design change", "topic": topic, "q1": True, "q2": True, "evidence": V,
         "sd_signals": ["flow", "performance"], "mechanism": topic, "signal": f"{topic} reusable signal"}
    c.update(kw)
    return c


def must_gap(n, topic, **kw):
    return change(n, topic, must_signals=["system behaviour"], gap_signals=["concept first appearance"], **kw)


def project(name, prj, lib=True, seed=1):
    root = TMP / name
    return Project(ENV, root, prj, name.title(), library=(root / "library") if lib else None, seed=seed)


def prepare(p, pid, n, topic, meaning=Q_MEAN):
    """One unit, one LIGHT ULA event, completion and map sync. Returns event id."""
    p.discover([n])
    p.scope([wu(n)])
    p.human_sync(pid, [wu(n)], [must_gap(n, topic)])
    eid = p.event_id(pid, topic)
    art = p.light(pid, eid, LIGHT)
    p.complete(pid)
    p.map_sync(pid, {topic: [{"name": topic, "type": "CONCEPT", "meaning": meaning, "depth": ["L1", "L2"],
                              "artifacts": [art]}]})
    return eid


def golden(p, pid, n, topic="Queue", meaning=Q_MEAN):
    """prepare + persistence with a project experience."""
    eid = prepare(p, pid, n, topic, meaning)
    p.persist(pid, topic, {"name": topic, "meaning": meaning}, extra={"project_experience": True, "experience": SD_EXP})
    return eid


def chain(p, pid, eid, unit):
    """Walk WORK UNIT -> ... -> EXPERIENCE MAP from disk. Returns the broken link names."""
    broken, st = [], p.store
    s = pm.State.load(ENV.P7, st, p.ctx)
    pf = p.pass_file(pid)
    led = parse_ledger(ENV.P3_cols, st.read(LEDGER))
    row = next((r for r in led.rows if r["work_unit_id"] == unit), None)
    if not (row and row["status"] == "COVERED" and row["learning_pass_id"] == pid):
        broken.append("WORK UNIT")
    ev = next((e for e in pf["events"] if e["Event ID"] == eid), None)
    if not (ev and unit in pm.split(ev["Work Units"])):
        broken.append("LEARNING EVENT")
    rt = next((r for r in pf["routing"] if r["Event ID"] == eid), {})
    art = rt.get("Artifact", "-")
    if not (rt.get("ULA Status") == "COMPLETE" and st.read(f"P:{art}")):
        broken.append("ULA ARTIFACT")
    ms = next(r for r in pf["ms"] if r["Event ID"] == eid)
    nodes = [s.graph.node(n) for n in pm.split(ms["Node IDs"])]
    if not nodes or any(n is None or eid not in pm.split(n["source_event_ids"]) or art not in pm.split(n["source_artifacts"])
                        for n in nodes):
        broken.append("GRAPH NODE")
    cid = nodes[0]["home_ref"] if nodes and nodes[0] else "UNASSIGNED"
    ptr = s.pointers.get(cid, ({}, ""))[0]
    reg = next((r for r in s.registry if r["Concept ID"] == cid), None)
    if not (ptr.get("Home Ref") == f"personal:{cid}" and reg and st.read(f"L:{reg['Home']}")):
        broken.append("CONCEPT HOME")
    kp = next((k for k in pf["kp"] if k["Event ID"] == eid), {})
    xid = kp.get("Experience ID", "-")
    note = s.notes.get(xid)
    if not (note and note["id"]["Event ID"] == eid and note["id"]["Concept ID"] == cid):
        broken.append("EXPERIENCE NOTE")
    if not any(r["Experience Note"] == f"{p.ctx['config']['project_id']}/{xid}" and r["Concept Home"] == cid for r in s.sd):
        broken.append("EXPERIENCE MAP")
    return broken


def theory_count(p, text, *others):
    """Persisted files (pass artifacts excluded) that contain the theory text."""
    roots = {r for q in (p, *others) for r in q.store.roots.values() if r.exists()}
    files = {f for r in roots for f in r.rglob("*.md") if "passes" not in f.parts}
    return sum(text in f.read_text(encoding="utf-8") for f in files)


def authoritative(p):
    """Bytes of every AUTHORITATIVE file; queue only §B."""
    derived = {STATE, HMAP, pm.IDX, QUEUE}
    snap = {k: v for k, v in p.store.snapshot().items() if k not in derived}
    snap[QUEUE + "#B"] = gm.section(p.store.read(QUEUE), "## B. Knowledge Debt")
    return snap


def lib_snapshot(path):
    return {f.relative_to(path).as_posix(): f.read_bytes() for f in Path(path).rglob("*") if f.is_file()}


# Test A - routine work -> NOT_LEARNING_RELEVANT -> DONE
pa = project("e2e_a", "PRJ-a0000001")
pa.discover([1])
pa.scope([wu(1)])
ev_a = pa.human_sync("LP-20261027-01", [wu(1)], [change(1, "rename file", kind="file rename")])
check("A no learning event", ev_a, [])
check("A pass COMPLETE", pa.complete("LP-20261027-01"), "COMPLETE")
check("A ledger NOT_LEARNING_RELEVANT", pa.ledger.by_id(wu(1))["status"], "NOT_LEARNING_RELEVANT")
check("A map sync nothing", pa.map_sync("LP-20261027-01"), {})
fa = pa.final()
check("A final integrity PASS", (fa["result"], fa["check1"]), ("PASS", []))
check("A no library write", (TMP / "e2e_a" / "library").exists(), False)

# Test B - Light ULA golden path
pb = project("e2e_b", "PRJ-b0000001")
eb = golden(pb, "LP-20261027-01", 1)
pf = pb.pass_file("LP-20261027-01")
ms_b = pf["ms"][0]
check("B pass COMPLETE", pf["meta"]["pass_status"], "COMPLETE")
check("B ledger COVERED", pb.ledger.by_id(wu(1))["status"], "COVERED")
check("B map sync COMPLETE", ms_b["Map Sync"], "COMPLETE")
check("B persistence COMPLETE", ms_b["Experience Persistence"], "COMPLETE")
fb = pb.final()
check("B final integrity PASS", (fb["result"], fb["check1"]), ("PASS", []))
check("B identity chain resolves", chain(pb, "LP-20261027-01", eb, wu(1)), [])

# Test C - Full ULA + resume
pc = project("e2e_c", "PRJ-c0000001")
pc.discover([1])
pc.scope([wu(1)])
pc.human_sync("LP-20261027-01", [wu(1)], [must_gap(1, "Rate Limiter")],
              triggers={"Rate Limiter": ["IMPORTANT_ARCHITECTURE_DECISION", "RECURSIVE_TOPIC_STRUCTURE"]})
ec = pc.event_id("LP-20261027-01", "Rate Limiter")
pc.full_until_review("LP-20261027-01", ec)
meta_c = pc.pass_file("LP-20261027-01")["meta"]
check("C WAITING_USER at review", (meta_c["pass_status"], meta_c["current_stage"]), ("WAITING_USER", "FULL_ULA_REVIEW"))
lp_c = pc.passes["LP-20261027-01"]
check("C new /stay-in-the-loop asks resume/new/abandon", um.startup([lp_c])[0], "ASK")
check("C resume keeps pass id and stage", um.resume(lp_c), ("LP-20261027-01", "FULL_ULA_REVIEW"))
brief_before = pc.store.read(f"P:passes/LP-20261027-01/ula/{ec}/PROJECT_BRIEF.md")
art_c = pc.full_after_review("LP-20261027-01", ec, FULL)
check("C completed brief not regenerated", (pc.writes[f"P:passes/LP-20261027-01/ula/{ec}/PROJECT_BRIEF.md"],
                                             pc.store.read(f"P:passes/LP-20261027-01/ula/{ec}/PROJECT_BRIEF.md") == brief_before), (1, True))
check("C ULA COMPLETE", lp_c.routing[ec]["ULA Status"], "COMPLETE")
check("C pass COMPLETE same id", (pc.complete("LP-20261027-01"), lp_c.id), ("COMPLETE", "LP-20261027-01"))
pc.map_sync("LP-20261027-01", {"Rate Limiter": [{"name": "Rate Limiter", "type": "CONCEPT", "meaning": "istek hızını sınırlar",
                                                  "depth": ["L1", "L2", "L3", "L4"], "artifacts": [art_c]}]})
check("C persistence COMPLETE", pc.persist("LP-20261027-01", "Rate Limiter", {"name": "Rate Limiter", "meaning": "istek hızını sınırlar"}),
      "COMPLETE")
home_c = pm.State.load(ENV.P7, pc.store, pc.ctx).homes
check("C Home has L3 and L4", sorted(k.split(" ")[0] for k, v in next(iter(home_c.values()))["sections"].items()
                                     if k.startswith("L") and v != "N/A"), ["L0", "L1", "L2", "L3", "L4"])
fc = pc.final()
check("C final DONE (PASS)", fc["result"], "PASS")

# Test D - coverage gap: 1-3 COVERED, 4-10 UNCOVERED, /latest
pd = project("e2e_d", "PRJ-d0000001")
pd.discover([1, 2, 3])
pd.scope("catch-up")
pd.human_sync("LP-20261027-01", [wu(1), wu(2), wu(3)], [must_gap(n, "Queue") for n in (1, 2, 3)])
pd.light("LP-20261027-01", pd.event_id("LP-20261027-01", "Queue"), LIGHT)
pd.complete("LP-20261027-01")
check("D 1-3 COVERED", [pd.ledger.by_id(wu(n))["status"] for n in (1, 2, 3)], ["COVERED"] * 3)
pd.discover(range(1, 11))
check("D 4-10 open", pd.open_coverage(), [wu(n) for n in range(4, 11)])
check("D /latest selects 10", pd.scope("latest"), [wu(10)])
check("D 4-9 DEFERRED", [pd.ledger.by_id(wu(n))["status"] for n in range(4, 10)], ["DEFERRED"] * 6)
pd.human_sync("LP-20261027-02", [wu(10)], [must_gap(10, "Cache")])
pd.light("LP-20261027-02", pd.event_id("LP-20261027-02", "Cache"), LIGHT)
check("D unit 10 pipeline COMPLETE", pd.complete("LP-20261027-02"), "COMPLETE")
pd.map_sync("LP-20261027-01")
pd.map_sync("LP-20261027-02")
check("D persistence COMPLETE for both passes", (pd.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN}),
                                                pd.persist("LP-20261027-02", "Cache", {"name": "Cache", "meaning": "veriyi yakında tutar"})),
      ("COMPLETE", "COMPLETE"))
check("D next call: 4-9 still visible", pd.open_coverage(), [wu(n) for n in range(4, 10)])
check("D pending scope = 4-9", [r["work_unit_id"] for r in cm.resolve_scope(pd.ledger, "pending")], [wu(n) for n in range(4, 10)])
fd = pd.final()
check("D final PASS with open DEFERRED units", fd["result"], "PASS")

# Test E - Knowledge Debt lifecycle
pe = project("e2e_e", "PRJ-e0000001")
pe.discover([1, 2])
pe.scope([wu(1)])
pe.human_sync("LP-20261027-01", [wu(1)], [change(1, "Backpressure", gap_signals=["concept first appearance"])])
debt = pe.all_debts()
check("E debt OPEN", [(d["debt_status"], d["concept_home"]) for d in debt], [("OPEN", "UNASSIGNED")])
check("E unit COVERED with OPEN debt", (pe.complete("LP-20261027-01"), pe.ledger.by_id(wu(1))["status"]), ("COMPLETE", "COVERED"))
pe.map_sync("LP-20261027-01", {"Backpressure": [{"name": "Backpressure", "type": "CONCEPT", "meaning": "üreticiyi yavaşlatır"}]})
g = gm.Graph.parse(ENV.P6, pe.store.read(GRAPH))
debt_node = next(n for n in g.nodes if n["canonical_name"] == "Backpressure")
check("E DEBT node", (debt_node["node_status"], debt_node["debt_id"]), ("DEBT", debt[0]["debt_id"]))
check("E debt event persistence NOT_APPLICABLE", pe.persist("LP-20261027-01", "Backpressure"), "NOT_APPLICABLE")
check("E final with OPEN debt PASS", pe.final()["result"], "PASS")
pe.scope([wu(2)])
pe.human_sync("LP-20261027-02", [wu(2)], [must_gap(2, "Backpressure")])
art_e = pe.light("LP-20261027-02", pe.event_id("LP-20261027-02", "Backpressure"), LIGHT)
pe.complete("LP-20261027-02")
pe.map_sync("LP-20261027-02", {"Backpressure": [{"name": "Backpressure", "type": "CONCEPT", "meaning": "üreticiyi yavaşlatır",
                                                  "depth": ["L1", "L2"], "artifacts": [art_e]}]})
g = gm.Graph.parse(ENV.P6, pe.store.read(GRAPH))
node_e = g.node(debt_node["node_id"])
check("E DEBT -> ACTIVE same node", (node_e["node_status"], node_e["debt_id"]), ("ACTIVE", debt[0]["debt_id"]))
check("E persistence COMPLETE", pe.persist("LP-20261027-02", "Backpressure", {"name": "Backpressure", "meaning": "üreticiyi yavaşlatır"}),
      "COMPLETE")
d2 = pe.all_debts()[0]
cid_e = gm.Graph.parse(ENV.P6, pe.store.read(GRAPH)).node(debt_node["node_id"])["home_ref"]
check("E debt RESOLVED -> CH", (d2["debt_status"], d2["concept_home"], d2["resolution_ref"]),
      ("RESOLVED", cid_e, pe.event_id("LP-20261027-02", "Backpressure")))
check("E final PASS", pe.final()["result"], "PASS")

# Test F - LOCAL_TEMPORARY -> personal promotion
pf_ = project("e2e_f", "PRJ-f0000001", lib=False)
pf_.discover([1])
pf_.scope([wu(1)])
pf_.human_sync("LP-20261027-01", [wu(1)], [must_gap(1, "Queue")])
art_f = pf_.light("LP-20261027-01", pf_.event_id("LP-20261027-01", "Queue"), LIGHT)
pf_.complete("LP-20261027-01")
pf_.map_sync("LP-20261027-01", {"Queue": [{"name": "Queue", "type": "CONCEPT", "meaning": Q_MEAN, "depth": ["L1", "L2"],
                                           "artifacts": [art_f]}]})
check("F unconfigured, no choice -> PENDING", pf_.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN}), "PENDING")
check("F local temporary -> COMPLETE", pf_.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN},
                                                   user={"library": "local"}, extra={"project_experience": True, "experience": SD_EXP}),
      "COMPLETE")
s_f = pm.State.load(ENV.P7, pf_.store, pf_.ctx)
cid_f = next(iter(s_f.local))
check("F Home Mode LOCAL_TEMPORARY", s_f.local[cid_f]["id"]["Home Mode"], "LOCAL_TEMPORARY")
check("F final before promotion PASS", pf_.final()["result"], "PASS")
pf_.configure_library(TMP / "e2e_f" / "library")
check("F promotion COMPLETE same id", pf_.promote(), {cid_f: "COMPLETE"})
s_f2 = pm.State.load(ENV.P7, pf_.store, pf_.ctx)
check("F CH unchanged; Home personal; project pointer", (list(s_f2.homes), list(s_f2.local), list(s_f2.pointers)),
      ([cid_f], [], [cid_f]))
check("F graph home_ref same CH", [n["home_ref"] for n in s_f2.graph.nodes if n["canonical_name"] == "Queue"], [cid_f])
check("F theory in one place", theory_count(pf_, LIGHT["L2 — Mechanism"]), 1)
ff = pf_.final()
check("F final PASS after promotion", ff["result"], "PASS")

# Test G - map ambiguity (same name, different meaning)
pg = project("e2e_g", "PRJ-a7000001")
golden(pg, "LP-20261027-01", 1)
pg.discover([2])
pg.scope([wu(2)])
pg.human_sync("LP-20261027-02", [wu(2)], [must_gap(2, "Queue")])
art_g = pg.light("LP-20261027-02", pg.event_id("LP-20261027-02", "Queue"), LIGHT)
pg.complete("LP-20261027-02")
st_g = pg.map_sync("LP-20261027-02", {"Queue": [{"name": "Queue", "type": "CONCEPT", "meaning": "veri yapısı: FIFO liste",
                                                 "depth": ["L1", "L2"], "artifacts": [art_g]}]})
check("G map sync BLOCKED", list(st_g.values()), ["BLOCKED"])
check("G persistence waits (PENDING)", pg.persist("LP-20261027-02", "Queue", {"name": "Queue", "meaning": "veri yapısı: FIFO liste"}),
      "PENDING")
check("G pass COMPLETE, ledger COVERED", (pg.pass_file("LP-20261027-02")["meta"]["pass_status"], pg.ledger.by_id(wu(2))["status"]),
      ("COMPLETE", "COVERED"))
fg = pg.final()
check("G final PASS_WITH_WARNINGS (L-08 only)", (fg["result"], fg["check2"]), ("PASS_WITH_WARNINGS", [("L-08", "WARNING")]))

# Test H - persistence conflict
ph = project("e2e_h", "PRJ-a8000001")
golden(ph, "LP-20261027-01", 1)
cid_h = next(iter(pm.State.load(ENV.P7, ph.store, ph.ctx).homes))
home_before = ph.store.read(f"L:concepts/{cid_h}.md")
ph.discover([2])
ph.scope([wu(2)])
ph.human_sync("LP-20261027-02", [wu(2)], [must_gap(2, "Queue")])
art_h = ph.light("LP-20261027-02", ph.event_id("LP-20261027-02", "Queue"),
                 dict(LIGHT, **{"L2 — Mechanism": "Queue mesajı hemen siler. Ack yoktur."}))
ph.complete("LP-20261027-02")
ph.map_sync("LP-20261027-02", {"Queue": [{"name": "Queue", "type": "CONCEPT", "meaning": Q_MEAN, "depth": ["L1", "L2"],
                                          "artifacts": [art_h]}]})
check("H conflict -> BLOCKED", ph.persist("LP-20261027-02", "Queue", {"name": "Queue", "meaning": Q_MEAN},
                                          extra={"compare": {"L2 — Mechanism": "CONFLICT"}}), "BLOCKED")
check("H Home unchanged (no silent overwrite)", ph.store.read(f"L:concepts/{cid_h}.md") == home_before, True)
check("H pass COMPLETE, ledger COVERED", (ph.pass_file("LP-20261027-02")["meta"]["pass_status"], ph.ledger.by_id(wu(2))["status"]),
      ("COMPLETE", "COVERED"))
fh = ph.final()
check("H final PASS_WITH_WARNINGS, no FAIL", (fh["result"], codes(fh["check1"], "FAIL")), ("PASS_WITH_WARNINGS", set()))

# Test I - abandon an incomplete Full ULA pass
pi = project("e2e_i", "PRJ-a9000001")
pi.discover([1])
pi.scope([wu(1)])
pi.human_sync("LP-20261027-01", [wu(1)], [must_gap(1, "Queue"), must_gap(1, "Rate Limiter")],
              triggers={"Rate Limiter": ["IMPORTANT_ARCHITECTURE_DECISION"]})
e_q, e_r = pi.event_id("LP-20261027-01", "Queue"), pi.event_id("LP-20261027-01", "Rate Limiter")
pi.light("LP-20261027-01", e_q, LIGHT)
pi.full_until_review("LP-20261027-01", e_r)
pi.complete("LP-20261027-01")
check("I unit PARTIAL with open Full event", (pi.ledger.by_id(wu(1))["status"], pi.ledger.by_id(wu(1))["open_items"]), ("PARTIAL", e_r))
pi.abandon("LP-20261027-01")
check("I pass ABANDONED", pi.pass_file("LP-20261027-01")["meta"]["pass_status"], "ABANDONED")
check("I ledger open, open_items kept", (pi.ledger.by_id(wu(1))["status"], pi.ledger.by_id(wu(1))["open_items"]), ("PARTIAL", e_r))
check("I final after abandon PASS", pi.final()["result"], "PASS")
check("I new pass may select same unit", (um.new_pass_conflict(list(pi.passes.values()), [wu(1)])[0], wu(1) in pi.open_coverage()),
      ("OK", True))
pi.human_sync("LP-20261027-02", [wu(1)], [must_gap(1, "Rate Limiter")])
pi.light("LP-20261027-02", pi.event_id("LP-20261027-02", "Rate Limiter"), LIGHT)
check("I new pass covers unit", (pi.complete("LP-20261027-02"), pi.ledger.by_id(wu(1))["status"]), ("COMPLETE", "COVERED"))

# Test J - derived state corruption -> rebuild -> PASS
pj = project("e2e_j", "PRJ-aa000001")
golden(pj, "LP-20261027-01", 1)
auth_j = authoritative(pj)
pj.store.write(STATE, pj.store.read(STATE).replace("uncovered_count: 0", "uncovered_count: 7"))
pj.store.write(HMAP, re.sub(r"generated_from_graph_version: \d+", "generated_from_graph_version: 0", pj.store.read(HMAP)))
pj.store.write(pm.IDX, pm.doc("Personal Technical Library Index", "Concepts", ENV.P7.idx_cols, []))
fj = pj.final()
check("J check1 = derived WARNINGs only", sorted(codes(fj["check1"])), ["L-01", "L-18", "L-19"])
check("J repaired derived set", sorted(fj["repaired"]), ["HORIZONTAL_MAP", "LEARNING_STATE", "LIBRARY_INDEX"])
check("J check2 empty -> PASS", (fj["check2"], fj["result"]), ([], "PASS"))
check("J authoritative unchanged", authoritative(pj) == auth_j, True)

# Test K - authoritative corruption -> FAIL, no repair
pk = project("e2e_k", "PRJ-ab000001")
golden(pk, "LP-20261027-01", 1)
xk = next(iter(pm.State.load(ENV.P7, pk.store, pk.ctx).notes))
note_key = f"P:experiences/{xk}.md"
pk.store.write(note_key, re.sub(r"(Concept ID:\s+)CH-\w+", r"\1CH-deadbeef", pk.store.read(note_key)))
pk.store.write(STATE, pk.store.read(STATE).replace("uncovered_count: 0", "uncovered_count: 7"))
before_k = pk.store.snapshot()
fk = pk.final()
check("K unknown concept in note -> L-22 FAIL", ("L-22", "FAIL") in fk["check1"], True)
check("K result FAIL, no repair", (fk["result"], fk["repaired"]), ("FAIL", []))
check("K no file changed (derived also untouched)", pk.store.snapshot() == before_k, True)
pk2 = project("e2e_k2", "PRJ-ab000002")
golden(pk2, "LP-20261027-01", 1)
led = pk2.store.read(LEDGER)
row = next(l for l in led.splitlines() if l.startswith(f"| {wu(1)} "))
pk2.store.write(LEDGER, led.rstrip("\n") + "\n" + row + "\n")
fk2 = pk2.final()
check("K duplicate work_unit_id -> C-01 FAIL", (("C-01", "FAIL") in fk2["check1"], fk2["result"], fk2["repaired"]), (True, "FAIL", []))

# Test L - concurrent personal write
SHARED = TMP / "shared_lib"
pl_a = Project(ENV, TMP / "e2e_l_a", "PRJ-ac000001", "Alpha", library=SHARED, seed=11)
pl_b = Project(ENV, TMP / "e2e_l_b", "PRJ-ac000002", "Beta", library=SHARED, seed=12)
prepare(pl_a, "LP-20261027-01", 1, "Queue")
prepare(pl_b, "LP-20261027-01", 1, "Cache", "veriyi yakında tutar")
got, _ = lock.acquire(ENV.lock, SHARED, {"lock_id": "LK-a0a0a0a0", "project_id": "PRJ-ac000001",
                                          "learning_pass_id": "LP-20261027-01", "created_at": "2026-10-27T10:00",
                                          "operation": "PERSIST LE-LP-20261027-01-01"})
lib_before = lib_snapshot(SHARED)
check("L A holds lock", got, "ACQUIRED")
check("L B persistence BLOCKED", pl_b.persist("LP-20261027-01", "Cache", {"name": "Cache", "meaning": "veriyi yakında tutar"},
                                              extra={"project_experience": True, "experience": SD_EXP}), "BLOCKED")
check("L B sees lock owner", pl_b.last_lock["project_id"], "PRJ-ac000001")
check("L library unchanged by B", lib_snapshot(SHARED) == lib_before, True)
check("L B pass COMPLETE, ledger COVERED", (pl_b.pass_file("LP-20261027-01")["meta"]["pass_status"],
                                            pl_b.ledger.by_id(wu(1))["status"]), ("COMPLETE", "COVERED"))
check("L A releases", lock.release(ENV.lock, SHARED, "LK-a0a0a0a0"), "RELEASED")
check("L A persists", pl_a.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN},
                                   extra={"project_experience": True, "experience": SD_EXP}), "COMPLETE")
check("L B retry COMPLETE", pl_b.persist("LP-20261027-01", "Cache", {"name": "Cache", "meaning": "veriyi yakında tutar"},
                                         extra={"project_experience": True, "experience": SD_EXP}), "COMPLETE")
check("L no lock left", lock.read(SHARED), None)
check("L registry has both concepts", len(pm.State.load(ENV.P7, pl_b.store, pl_b.ctx).registry), 2)
check("L final A and B PASS", (pl_a.final()["result"], pl_b.final()["result"]), ("PASS", "PASS"))

# Test M - stale lock needs user decision
pm_ = project("e2e_m", "PRJ-ad000001")
prepare(pm_, "LP-20261027-01", 1, "Queue")
lib_m = TMP / "e2e_m" / "library"
lock.acquire(ENV.lock, lib_m, {"lock_id": "LK-dead0001", "project_id": "PRJ-ffffffff", "learning_pass_id": "LP-20261001-01",
                               "created_at": "2026-10-01T09:00", "operation": "PERSIST LE-LP-20261001-01-01"})
check("M persistence BLOCKED by existing lock", pm_.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN}), "BLOCKED")
check("M lock info shown", (pm_.last_lock["project_id"], pm_.last_lock["created_at"], pm_.last_lock["operation"]),
      ("PRJ-ffffffff", "2026-10-01T09:00", "PERSIST LE-LP-20261001-01-01"))
check("M no auto removal -> WAITING_USER", (lock.stale(ENV.lock, lib_m), lock.read(lib_m) is not None), ("WAITING_USER", True))
check("M user keeps lock", (lock.stale(ENV.lock, lib_m, 1), lock.read(lib_m) is not None), ("KEPT", True))
check("M user confirms stale -> removed", (lock.stale(ENV.lock, lib_m, 2), lock.read(lib_m)), ("REMOVED", None))
check("M retry COMPLETE", pm_.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN}), "COMPLETE")
check("M final PASS", pm_.final()["result"], "PASS")

# Test N - cross-project concept reuse
NLIB = TMP / "n_lib"
pn_a = Project(ENV, TMP / "e2e_n_a", "PRJ-ae000001", "Alpha", library=NLIB, seed=21)
pn_b = Project(ENV, TMP / "e2e_n_b", "PRJ-ae000002", "Beta", library=NLIB, seed=22)
en_a = golden(pn_a, "LP-20261027-01", 1)
en_b = golden(pn_b, "LP-20261027-01", 1)
s_na, s_nb = pm.State.load(ENV.P7, pn_a.store, pn_a.ctx), pm.State.load(ENV.P7, pn_b.store, pn_b.ctx)
check("N same CH in both projects", (list(s_na.pointers), len(s_nb.registry)), (list(s_nb.pointers), 1))
cid_n = next(iter(s_nb.homes))
check("N no duplicate theory", theory_count(pn_a, LIGHT["L2 — Mechanism"], pn_b), 1)
check("N two appearances", sorted(a["project_id"] for a in s_nb.homes[cid_n]["appearances"]), ["PRJ-ae000001", "PRJ-ae000002"])
check("N one Experience Note per project", (len(s_na.notes), len(s_nb.notes)), (1, 1))
check("N SD map cross-project rows", sorted(r["Experience Note"].split("/")[0] for r in s_nb.sd), ["PRJ-ae000001", "PRJ-ae000002"])
check("N final A and B PASS", (pn_a.final()["result"], pn_b.final()["result"]), ("PASS", "PASS"))
check("N identity chain A", chain(pn_a, "LP-20261027-01", en_a, wu(1)), [])
check("N identity chain B", chain(pn_b, "LP-20261027-01", en_b, wu(1)), [])

# Extra - identity chain detects a broken link
px = project("e2e_x", "PRJ-af000001")
ex = golden(px, "LP-20261027-01", 1)
xid_x = next(iter(pm.State.load(ENV.P7, px.store, px.ctx).notes))
(px.store.roots["P"] / "experiences" / f"{xid_x}.md").unlink()
check("X chain broken at EXPERIENCE NOTE", chain(px, "LP-20261027-01", ex, wu(1))[:1], ["EXPERIENCE NOTE"])
check("X broken note pointer -> FAIL", px.final()["result"], "FAIL")

# Extra - final integrity checks on crafted state
base = project("e2e_base", "PRJ-b1000001")
eb0 = golden(base, "LP-20261027-01", 1)
SNAP = base.store.snapshot()


def crafted(edit):
    """Restore the golden project, apply one edit, return CHECK 1 findings."""
    for k in list(base.store.snapshot()):
        if k not in SNAP:
            base.store.path(k).unlink()
    for k, v in SNAP.items():
        base.store.path(k).parent.mkdir(parents=True, exist_ok=True)
        base.store.path(k).write_bytes(v)
    edit(base.store)
    return fi.check(ENV, base.store, base.ctx)


def sub(key, pattern, repl, count=0):
    return lambda st: st.write(key, re.sub(pattern, repl, st.read(key), count=count, flags=re.M))


PK = pm.pass_key("LP-20261027-01")
check("X golden base clean", crafted(lambda st: None), [])
check("X L-03 debt with unknown origin", "L-03" in codes(crafted(lambda st: st.write(QUEUE, st.read(QUEUE).rstrip("\n") +
      "\n| KD-x-01 | Lag | LE-LP-x-01 | - | - | - | LATER | OPEN | 2026-10-27 | UNASSIGNED | - |\n"))), True)
check("X L-04 fake RESOLVED debt", "L-04" in codes(crafted(lambda st: st.write(QUEUE, st.read(QUEUE).rstrip("\n") +
      f"\n| KD-x-01 | Lag | {eb0} | - | - | - | LATER | RESOLVED | 2026-10-27 | CH-00000000 | {eb0} |\n"))), True)
check("X L-05 pass scope unit missing in ledger", "L-05" in codes(crafted(sub(PK, r"^selected_scope: \[.*\]$", "selected_scope: [jira:NOPE-1]"))), True)
check("X L-06 event outside pass scope", "L-06" in codes(crafted(sub(PK, r"^Work Units: .*$", "Work Units: jira:OTHER-9"))), True)
check("X L-07 COMPLETE pass with PARTIAL unit", "L-07" in codes(crafted(sub(LEDGER, r"\| COVERED \|", "| PARTIAL |"))), True)
check("X L-08 BLOCKED persistence -> WARNING", ("L-08", "WARNING") in crafted(sub(PK, r"\| COMPLETE \|$", "| BLOCKED |")), True)
check("X L-09 Map Sync COMPLETE, node missing", "L-09" in codes(crafted(sub(PK, r"KN-[0-9a-f]{8}", "KN-00000bad", 1))), True)
check("X L-10 persistence COMPLETE, note missing", "L-10" in codes(crafted(lambda st: st.path(f"P:experiences/{next(iter(pm.State.load(ENV.P7, st, base.ctx).notes))}.md").unlink())), True)
check("X L-11 graph home_ref unknown", "L-11" in codes(crafted(sub(GRAPH, r"\| CH-[0-9a-f]{8} \|", "| CH-0000beef |"))), True)
check("X L-12 pointer to unknown personal CH", "L-12" in codes(crafted(sub(pm.REG, r"^\| CH-.*\n", ""))), True)
check("X L-12 library unreachable -> WARNING", ("L-12", "WARNING") in crafted(sub(CONFIG, r"^personal_library_path: .*$",
                                                                                   "personal_library_path: Z:/missing-lib")), True)
check("X L-13 map row to missing note", "L-13" in codes(crafted(lambda st: st.write(pm.SDMAP, st.read(pm.SDMAP).rstrip("\n") +
      "\n| Queue | PRJ-b1000001 (Base) | p | c | w | a | s | y | t | f | o | r | L1 | - | PRJ-b1000001/EX-00000000 |\n"))), True)
check("X L-15 two active passes same unit", "L-15" in codes(crafted(lambda st: [st.write(f"P:passes/{p}/LEARNING_PASS.md",
      re.sub(r"^pass_status: \w+", "pass_status: IN_PROGRESS", re.sub(r"LP-20261027-01", p, st.read(PK)), flags=re.M))
      for p in ("LP-20261027-08", "LP-20261027-09")])), True)
check("X L-16 ABANDONED pass closed ledger", "L-16" in codes(crafted(sub(PK, r"^pass_status: COMPLETE$", "pass_status: ABANDONED"))), True)
check("X L-17 project_id changed in config", "L-17" in codes(crafted(sub(CONFIG, r"^project_id: .*$", "project_id: PRJ-99999999"))), True)
check("X L-17 rename keeps id -> no L-17", "L-17" in codes(crafted(sub(CONFIG, r"^project_name: .*$", "project_name: Renamed"))), False)
check("X L-18 stale view -> WARNING", ("L-18", "WARNING") in crafted(sub(HMAP, r"generated_from_graph_version: \d+", "generated_from_graph_version: 0")), True)
check("X L-19 stale index -> WARNING", ("L-19", "WARNING") in crafted(sub(pm.IDX, r"\| ACTIVE \|", "| MERGED |")), True)
check("X L-23 note event unknown", "L-23" in codes(crafted(lambda st: [st.write(k, re.sub(r"(Event ID:\s+)\S+", r"\1LE-LP-x-09", st.read(k)))
                                                          for k in st.keys("P:experiences/")])), True)

# Extra - DSA note with Decision Record (L-14)
pz = project("e2e_z", "PRJ-b2000001")
pz.discover([1])
pz.scope([wu(1)])
pz.human_sync("LP-20261027-01", [wu(1)], [must_gap(1, "Top-K", sd_signals=[], computational_need=True)])
art_z = pz.light("LP-20261027-01", pz.event_id("LP-20261027-01", "Top-K"), LIGHT)
pz.complete("LP-20261027-01")
pz.map_sync("LP-20261027-01", {"Top-K": [{"name": "Top-K", "type": "CONCEPT", "meaning": "en büyük k elemanı bulur",
                                          "depth": ["L1", "L2"], "artifacts": [art_z]}]})
check("X DSA event persisted with DSA_DR", pz.persist("LP-20261027-01", "Top-K", {"name": "Top-K", "meaning": "en büyük k elemanı bulur"},
      extra={"project_experience": True, "experience": SD_EXP, "alternatives_in_project": 2, "selected_evidence": "VERIFIED",
             "dsa": {"Pattern": "Top-K", "Time": "O(n log k)", "Space": "O(k)"}}), "COMPLETE")
s_z = pm.State.load(ENV.P7, pz.store, pz.ctx)
check("X DR exists and note points to it", [n["id"]["Decision Record"] in s_z.drs for n in s_z.notes.values()], [True])
check("X final with DR PASS", pz.final()["result"], "PASS")
dr_key = f"P:experiences/{next(iter(s_z.drs))}.md"
pz.store.write(dr_key, re.sub(r"(Experience ID:\s+)\S+", r"\1EX-00000000", pz.store.read(dr_key)))
check("X L-14 DR not pointing back -> FAIL", ("L-14", "FAIL") in pz.final()["check1"], True)

# Extra - L-20: repair is never trusted without CHECK 2
pq = project("e2e_q", "PRJ-b4000001")
golden(pq, "LP-20261027-01", 1)
pq.store.write(STATE, pq.store.read(STATE).replace("uncovered_count: 0", "uncovered_count: 7"))
real_rebuild = fi.rebuild
fi.rebuild = lambda env, store, ctx, artifact: env.L.derived(artifact)  # reports success, writes nothing
fq = pq.final()
fi.rebuild = real_rebuild
check("X ineffective repair -> CHECK 2 still WARNING, no PASS", (fq["repaired"], fq["check2"], fq["result"]),
      (["LEARNING_STATE"], [("L-01", "WARNING")], "PASS_WITH_WARNINGS"))

# Extra - lock protocol
check("X lock rules parsed", (ENV.lock["acquire"], ENV.lock["on_existing"], ENV.lock["stale_lock"], ENV.lock["on_release_error"]),
      ("EXCLUSIVE_CREATE", "BLOCKED", "USER_DECISION", "WARNING"))
check("X lock path", ENV.lock["lock_path"], "<personal_library_path>/.learning-write-lock/")
check("X LOCK.md fields", ENV.lock_fields, ["lock_id", "project_id", "learning_pass_id", "created_at", "operation"])
LT = TMP / "lock_unit"
meta1 = {"lock_id": "LK-00000001", "project_id": "PRJ-1", "learning_pass_id": "LP-1", "created_at": "t", "operation": "PERSIST x"}
check("X first acquire", lock.acquire(ENV.lock, LT, meta1)[0], "ACQUIRED")
check("X second acquire blocked, lock not overwritten", (lock.acquire(ENV.lock, LT, dict(meta1, lock_id="LK-2"))[0],
                                                          lock.read(LT)["lock_id"]), ("BLOCKED", "LK-00000001"))
check("X non-owner cannot release", (lock.release(ENV.lock, LT, "LK-2"), lock.read(LT)["lock_id"]), ("NOT_OWNER", "LK-00000001"))
check("X release failure -> WARNING", lock.release(ENV.lock, LT, "LK-00000001", fail=True), "WARNING")
check("X owner release", lock.release(ENV.lock, LT, "LK-00000001"), "RELEASED")
pr = project("e2e_r", "PRJ-b3000001")
prepare(pr, "LP-20261027-01", 1, "Queue")
pr.fail_release = True
check("X persist COMPLETE though release failed", pr.persist("LP-20261027-01", "Queue", {"name": "Queue", "meaning": Q_MEAN}), "COMPLETE")
fr = pr.final()
check("X leftover own lock -> L-21 WARNING, DONE allowed", (("L-21", "WARNING") in fr["check1"], fr["result"]), (True, "PASS_WITH_WARNINGS"))

# Extra - protocol vocabulary
check("X authority DERIVED set", sorted(a for a, c in ENV.L.authority.items() if c == "DERIVED"),
      ["HORIZONTAL_MAP", "KNOWLEDGE_VIEW", "LEARNING_QUEUE §A", "LEARNING_STATE", "LIBRARY_INDEX"])
check("X required AUTHORITATIVE present", {"LEARNING_CONFIG", "COVERAGE_LEDGER", "LEARNING_QUEUE §B", "LEARNING_PASS", "SEMANTIC_GRAPH",
                                           "CONCEPT_REGISTRY", "CONCEPT_HOME", "EXPERIENCE_NOTE", "DECISION_RECORD"}
      <= {a for a, c in ENV.L.authority.items() if c == "AUTHORITATIVE"}, True)
check("X result vocabulary", ENV.L.results, ["PASS", "PASS_WITH_WARNINGS", "FAIL"])
check("X 23 L checks", sorted(ENV.L.checks), [f"L-{i:02d}" for i in range(1, 24)])
check("X rebuild targets are DERIVED only", all(ENV.L.derived(c["rebuild"]) for c in ENV.L.checks.values() if c["rebuild"]), True)
check("X authoritative rebuild refused", fi.rebuild(ENV, base.store, base.ctx, "COVERAGE_LEDGER"), False)
skill_text = "\n".join(p.read_text(encoding="utf-8") for p in skill_dir().rglob("*.md") if "00_MASTER" not in p.name and "ula" not in p.parts)
check("X no runtime NOT IMPLEMENTED YET", "NOT IMPLEMENTED YET" in skill_text, False)
check("X SKILL routes integrity", "`integrity`" in (skill_dir() / "SKILL.md").read_text(encoding="utf-8"), True)

report(RESULTS)
