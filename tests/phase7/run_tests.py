"""Synthetic Phase 7 tests A-T plus extra integrity / consistency checks.

Usage: run_tests.py <skill_dir>
Fixtures live in a new temporary directory per run. No real project or personal library is touched.
"""
import atexit
import copy
import random
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402

use("phase6")
import graph_model as gm
from persist_model import (DSAMAP, GRAPH, IDX, QUEUE, REG, SDMAP, Protocol, State, Store, build_index, integrity,
                           md_table, doc, pass_key, persist_event, promote, rename, render_note, render_pointer,
                           resolve, resolve_debt, split)

P = Protocol(skill_dir())
RESULTS = []
RNG = random.Random(7)
FIX = Path(tempfile.mkdtemp(prefix="p7_")) / "fixtures"
atexit.register(shutil.rmtree, FIX.parent, True)
LEDGER = "P:state/COVERAGE_LEDGER.md"


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def codes(f, sev="FAIL"):
    return {c for c, s in f if s == sev}


def setup(name, prj, pname, lib=None, configured=True):
    store = Store(FIX / name / "project", lib or FIX / name / "library")
    ctx = {"config": {"project_id": prj, "project_name": pname,
                      "personal_library_path": str(store.roots["L"]) if configured else "UNCONFIGURED",
                      "work_unit_source": "auto"},
           "passes": {}, "events": {}, "artifacts": {}}
    store.write(LEDGER, "| work_unit_id | status | learning_pass_id |\n|---|---|---|\n| WU-1 | COVERED | LP-1 |\n")
    store.write(GRAPH, gm.Graph(1, [node("KN-00000000", "Project", typ="ROOT")]).render(P.gp))
    store.write(QUEUE, doc("Learning Queue", "B. Knowledge Debt", P.debt_cols, []))
    return store, ctx


def node(nid, name, meaning="-", status="ACTIVE", debt="-", typ="CONCEPT", events="-"):
    return {"node_id": nid, "canonical_name": name, "node_type": typ, "parent_id": "-" if typ == "ROOT" else "KN-00000000",
            "short_meaning": meaning, "system_role": "-", "home_ref": "UNASSIGNED", "available_depth": "-",
            "source_event_ids": events, "source_artifacts": "-", "project_appearances": "-", "aliases": "-",
            "node_status": status, "debt_id": debt, "superseded_by": "-"}


def add_nodes(store, *nodes):
    g = gm.Graph.parse(P.gp, store.read(GRAPH))
    g.nodes += list(nodes)
    g.version += 1
    store.write(GRAPH, g.render(P.gp))


def open_pass(store, ctx, lp, events, map_sync=None):
    """Pass after Phase 6: COMPLETE, Map Sync table filled with the 05 §10.1 initial marker."""
    ctx["passes"][lp] = "COMPLETE"
    ms = []
    for e in events:
        ctx["events"][e["id"]] = e
        initial = "PENDING" if e["disposition"] == "EXPERIENCE_ONLY" or (
            e["disposition"] == "ULA_CANDIDATE" and e.get("ula_status") == "COMPLETE") else "NOT_APPLICABLE"
        ms.append({"Event ID": e["id"], "Map Sync": (map_sync or {}).get(e["id"], "COMPLETE" if e.get("concept_nodes") else "NOT_APPLICABLE"),
                   "Node IDs": "; ".join(e.get("concept_nodes", [])) or "-", "Experience Persistence": initial})
    store.write(pass_key(lp), f"# Learning Pass {lp}\n\n## Map Sync\n\n{md_table(P.ms_cols, ms)}\n\n"
                              f"## Knowledge Persistence\n\n{md_table(P.kp_cols, [])}\n")


def ev(eid, lp, disp, name, meaning, **kw):
    e = {"id": eid, "pass": lp, "disposition": disp, "title": name, "concept": {"name": name, "meaning": meaning},
         "category": "SYSTEM_DESIGN", "work_units": ["WU-1"], "evidence_status": "VERIFIED", "experience": {},
         "dsa": {}, "evidence": []}
    e.update(kw)
    return e


def light(path, **secs):
    base = {"L0 — Local Map": "Request → Queue → Worker",
            "L1 — Simple Explanation": "Queue işleri sıraya koyar. Worker işi sonra alır ve çalıştırır.",
            "L2 — Mechanism": "Producer mesajı yazar. Broker mesajı saklar. Consumer mesajı alır ve ack gönderir.",
            "Retrieval": "Queue neden request süresini kısaltır?"}
    base.update(secs)
    return {"mode": "LIGHT", "path": path, "sections": base}


Q_MEAN = "işleri sıraya koyar"
SD_EXP = {"Problem": "Rapor isteği 40 saniye sürüyordu", "Constraint": "HTTP timeout 30 saniye",
          "Why It Appeared": "Uzun işi request dışına taşımak gerekti", "Alternatives": "sync call; background queue",
          "Selected": "background queue", "Why Selected": "request hemen döner", "Trade-off": "eventual result",
          "Failure Mode": "consumer lag", "Observed Result": "p95 300 ms", "Reusable Signal": "Uzun iş + timeout → queue düşün"}


def theory_count(store, text):
    """How many persisted Home / pointer / note files contain the text (pass artifacts excluded)."""
    files = [p for root in store.roots.values() if root.exists() for p in root.rglob("*.md")
             if "passes" not in p.parts]
    return sum(text in p.read_text(encoding="utf-8") for p in files)


def lib_files(store):
    root = store.roots["L"]
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()) if root.exists() else []


# Test A - new Concept Home
SA, CA = setup("alpha", "PRJ-a1a1a1a1", "Alpha")
LIB = SA.roots["L"]
add_nodes(SA, node("KN-11111111", "Queue", Q_MEAN, events="LE-LP-1-01"))
EA = ev("LE-LP-1-01", "LP-1", "ULA_CANDIDATE", "Queue", Q_MEAN, ula_status="COMPLETE", reusable=True,
        concept_nodes=["KN-11111111"], project_experience=True, experience=SD_EXP,
        artifact=light("passes/LP-1/ula/LE-LP-1-01/LIGHT_ULA.md"),
        evidence=[("Problem", "VERIFIED", "issue:INC-44"), ("Observed Result", "VERIFIED", "diagnostic:logs/p95.md")])
open_pass(SA, CA, "LP-1", [EA])
g_before = State.load(P, SA, CA).graph
check("A status COMPLETE", persist_event(P, SA, CA, EA["id"], RNG), "COMPLETE")
sa = State.load(P, SA, CA)
CH = sa.registry[0]["Concept ID"] if sa.registry else None
check("A CH id format", bool(CH and re.fullmatch(r"CH-[0-9a-f]{8}", CH)), True)
check("A registry entry", [(r["Concept ID"], r["Canonical Name"], r["Status"]) for r in sa.registry], [(CH, "Queue", "ACTIVE")])
check("A home file in personal library", (LIB / "concepts" / f"{CH}.md").exists(), True)
h = sa.homes.get(CH)
check("A home version 1, mode PERSONAL", (h["id"]["Version"], h["id"]["Home Mode"]), ("1", "PERSONAL"))
check("A L1 ULA-DERIVED provenance", h["sections"]["L1 — Simple Explanation"].startswith("Provenance: ULA-DERIVED"), True)
check("A no invented depth (L3, L4 N/A)", (h["sections"]["L3 — Theory"], h["sections"]["L4 — Math / Formalism"]), ("N/A", "N/A"))
ptr = sa.pointers.get(CH, ({}, ""))[0]
check("A project pointer", (ptr.get("Home Mode"), ptr.get("Home Ref"), ptr.get("Project Node IDs")),
      ("PERSONAL", f"personal:{CH}", "KN-11111111"))
check("A pointer has no theory", "Queue işleri sıraya koyar" in SA.read(f"P:concepts/{CH}.md"), False)
check("A pointer has no absolute path", str(LIB) in SA.read(f"P:concepts/{CH}.md"), False)
qn = sa.graph.node("KN-11111111")
check("A graph home_ref = CH, same node id", (qn["home_ref"], qn["node_id"]), (CH, "KN-11111111"))
check("A graph version +1", sa.graph.version, g_before.version + 1)
check("A one appearance", len(h["appearances"]), 1)
check("A experience note", [n["id"]["Concept ID"] for n in sa.notes.values()], [CH])
check("A integrity clean", codes(integrity(P, sa, CA)), set())
check("A index row", [(r["Concept ID"], r["Depth"], r["Project Count"]) for r in sa.index], [(CH, "L1; L2", "1")])
check("A ledger untouched", SA.read(LEDGER).count("COVERED"), 1)

# Test B - existing concept reuse from project B
SB, CB = setup("beta", "PRJ-b2b2b2b2", "Beta", lib=LIB)
add_nodes(SB, node("KN-22222222", "Queue", Q_MEAN, events="LE-LP-1-01"))
EB = ev("LE-LP-1-01", "LP-1", "ULA_CANDIDATE", "Queue", Q_MEAN, ula_status="COMPLETE", reusable=True,
        concept_nodes=["KN-22222222"], project_experience=True,
        experience=dict(SD_EXP, Problem="E-posta gönderimi request'i yavaşlatıyordu"),
        artifact=light("passes/LP-1/ula/LE-LP-1-01/LIGHT_ULA.md"))
open_pass(SB, CB, "LP-1", [EB])
home_before = State.load(P, SA, CA).homes[CH]
check("B status COMPLETE", persist_event(P, SB, CB, EB["id"], RNG), "COMPLETE")
sb = State.load(P, SB, CB)
hb = sb.homes[CH]
check("B same CH id", sb.pointers.get(CH, ({},))[0].get("Concept ID"), CH)
check("B one registry row", len(sb.registry), 1)
check("B theory duplicated = NO (sections unchanged)", hb["sections"], home_before["sections"])
check("B theory text in exactly one persisted file", theory_count(SB, "Broker mesajı saklar") + theory_count(SA, "Broker mesajı saklar") - 1, 1)
check("B version unchanged", hb["id"]["Version"], "1")
check("B new Project Appearance", [a["project_id"] for a in hb["appearances"]], ["PRJ-a1a1a1a1", "PRJ-b2b2b2b2"])
check("B new Experience Note in project B", [n["id"]["Project ID"] for n in sb.notes.values()], ["PRJ-b2b2b2b2"])
check("B graph home_ref in project B", sb.graph.node("KN-22222222")["home_ref"], CH)
check("B index project count 2", sb.index[0]["Project Count"], "2")
check("B integrity clean", codes(integrity(P, sb, CB)), set())

# Test C - appearance idempotence
snap = (SA.snapshot(), SB.snapshot())
check("C re-run COMPLETE is no-op", (persist_event(P, SA, CA, EA["id"], RNG), SA.snapshot()), ("COMPLETE", snap[0]))
txt = SA.read(pass_key("LP-1")).replace("| COMPLETE |\n\n## Knowledge", "| PENDING |\n\n## Knowledge")
SA.write(pass_key("LP-1"), txt)
check("C forced retry COMPLETE", persist_event(P, SA, CA, EA["id"], RNG), "COMPLETE")
sc = State.load(P, SA, CA)
check("C no duplicate appearance", len(sc.homes[CH]["appearances"]), 2)
check("C no duplicate note", len(sc.notes), 1)
check("C version unchanged", sc.homes[CH]["id"]["Version"], "1")
check("C library bytes unchanged", {k: v for k, v in SA.snapshot().items() if "concepts" in k or "registry" in k},
      {k: v for k, v in snap[0].items() if "concepts" in k or "registry" in k})

# Test D - project delta only
ED = ev("LE-LP-2-01", "LP-2", "EXPERIENCE_ONLY", "Queue", Q_MEAN, reusable=True, concept_nodes=["KN-22222222"],
        local_delta="Beta'da priority queue kullanıldı",
        experience=dict(SD_EXP, Problem="Toplu e-posta kuyrukta önceliklendirilmedi", Selected="priority queue"))
open_pass(SB, CB, "LP-2", [ED])
before = State.load(P, SB, CB).homes[CH]
check("D status COMPLETE", persist_event(P, SB, CB, ED["id"], RNG), "COMPLETE")
sd = State.load(P, SB, CB)
check("D general theory unchanged", (sd.homes[CH]["sections"], sd.homes[CH]["id"]["Version"]), (before["sections"], "1"))
check("D experience note created with CH", sorted(n["id"]["Concept ID"] for n in sd.notes.values()), [CH, CH])
check("D pointer local delta", sd.pointers[CH][0]["Local Delta"], "Beta'da priority queue kullanıldı")
check("D appearance added", len(sd.homes[CH]["appearances"]), 3)

# Test E - general knowledge enrichment
EE = ev("LE-LP-2-01", "LP-2", "ULA_CANDIDATE", "Queue", Q_MEAN, ula_status="COMPLETE", concept_nodes=["KN-11111111"],
        artifact={"mode": "FULL", "path": "passes/LP-2/ula/LE-LP-2-01/CONTENT.md", "sections": {
            "L1 — Simple Explanation": "Queue işleri sıraya koyar.", "L2 — Mechanism": "Producer yazar, consumer okur.",
            "L3 — Theory": "Queue producer ve consumer hızını ayırır. Bu decoupling backpressure sağlar."}})
open_pass(SA, CA, "LP-2", [EE])
check("E status COMPLETE", persist_event(P, SA, CA, EE["id"], RNG), "COMPLETE")
se = State.load(P, SA, CA)
he = se.homes[CH]
check("E same CH id", list(se.homes), [CH])
check("E L3 added", he["sections"]["L3 — Theory"].split("\n\n", 1)[-1],
      "Queue producer ve consumer hızını ayırır. Bu decoupling backpressure sağlar.")
check("E version +1", he["id"]["Version"], "2")
check("E L1 unchanged", he["sections"]["L1 — Simple Explanation"], before["sections"]["L1 — Simple Explanation"])
check("E change history ENRICH", he["history"][-1]["change"], "ENRICH L3 — Theory")
check("E index depth", se.index[0]["Depth"], "L1; L2; L3")
check("E integrity clean", codes(integrity(P, se, CA)), set())

# Test F - conflicting theory
EF = ev("LE-LP-3-01", "LP-3", "ULA_CANDIDATE", "Queue", Q_MEAN, ula_status="COMPLETE", concept_nodes=["KN-11111111"],
        compare={"L2 — Mechanism": "CONFLICT"},
        artifact=light("passes/LP-3/ula/LE-LP-3-01/LIGHT_ULA.md", **{"L2 — Mechanism": "Consumer mesajı ack olmadan siler."}))
open_pass(SA, CA, "LP-3", [EF])
lib_snap = {k: v for k, v in SA.snapshot().items()}
check("F status BLOCKED", persist_event(P, SA, CA, EF["id"], RNG), "BLOCKED")
after = SA.snapshot()
guarded = [k for k in lib_snap if "concepts" in k or "registry" in k or k == "P:" + GRAPH[2:]]
check("F no silent overwrite (homes, registry, pointer, graph unchanged)",
      (len(guarded), all(after[k] == lib_snap[k] for k in guarded)), (4, True))
check("F persistence BLOCKED recorded", State.load(P, SA, CA).ms("LP-3", EF["id"])["Experience Persistence"], "BLOCKED")
check("F user option 3 -> boundary", persist_event(P, SA, CA, EF["id"], RNG, {"conflict": 3}), "COMPLETE")
hf = State.load(P, SA, CA).homes[CH]
check("F boundary USER-CONFIRMED, version +1",
      (hf["sections"]["Confusion Boundaries"].startswith("Provenance: USER-CONFIRMED"), hf["id"]["Version"]), (True, "3"))
check("F L2 not overwritten", hf["sections"]["L2 — Mechanism"], he["sections"]["L2 — Mechanism"])

# Test G - local temporary
SG, CG = setup("gamma", "PRJ-c3c3c3c3", "Gamma", configured=False)
add_nodes(SG, node("KN-33333333", "Kalman Filter", "gürültülü ölçümden state tahmin eder", events="LE-LP-1-01"))
EG = ev("LE-LP-1-01", "LP-1", "ULA_CANDIDATE", "Kalman Filter", "gürültülü ölçümden state tahmin eder",
        ula_status="COMPLETE", reusable=True, concept_nodes=["KN-33333333"], project_experience=True, experience=SD_EXP,
        artifact=light("passes/LP-1/ula/LE-LP-1-01/LIGHT_ULA.md", **{
            "L1 — Simple Explanation": "Kalman Filter tahmini ve ölçümü ağırlıklı birleştirir."}))
open_pass(SG, CG, "LP-1", [EG])
check("G no choice -> PENDING", persist_event(P, SG, CG, EG["id"], RNG), "PENDING")
check("G defer -> PENDING", persist_event(P, SG, CG, EG["id"], RNG, {"library": "defer"}), "PENDING")
check("G local -> COMPLETE", persist_event(P, SG, CG, EG["id"], RNG, {"library": "local"}), "COMPLETE")
sg = State.load(P, SG, CG)
GCH = next(iter(sg.local), None)
check("G CH id format", bool(GCH and re.fullmatch(r"CH-[0-9a-f]{8}", GCH)), True)
check("G Home Mode LOCAL_TEMPORARY", sg.local[GCH]["id"]["Home Mode"], "LOCAL_TEMPORARY")
check("G full home in project", sg.local[GCH]["sections"]["L1 — Simple Explanation"].endswith("ağırlıklı birleştirir."), True)
check("G no personal write", lib_files(SG), [])
check("G graph home_ref", sg.graph.node("KN-33333333")["home_ref"], GCH)
check("G note local-temporary ref, map DEFERRED",
      [(n["id"]["Concept Home Ref"], n["id"]["Map Status"]) for n in sg.notes.values()], [(f"local-temporary:{GCH}", "DEFERRED")])
check("G integrity clean", codes(integrity(P, sg, CG)), set())

# Test H - promotion
CG["config"]["personal_library_path"] = str(SG.roots["L"])
check("H promotion COMPLETE", promote(P, SG, CG, RNG), {GCH: "COMPLETE"})
sh = State.load(P, SG, CG)
check("H same CH id in registry", [r["Concept ID"] for r in sh.registry], [GCH])
check("H global home created", (sh.homes[GCH]["id"]["Home Mode"], (SG.roots["L"] / "concepts" / f"{GCH}.md").exists()),
      ("PERSONAL", True))
check("H project file is pointer", SG.read(f"P:concepts/{GCH}.md").startswith("# Concept Pointer"), True)
check("H pointer keeps node ids", sh.pointers[GCH][0]["Project Node IDs"], "KN-33333333")
check("H theory not duplicated", theory_count(SG, "ağırlıklı birleştirir."), 1)
check("H version unchanged, PROMOTED history", (sh.homes[GCH]["id"]["Version"], sh.homes[GCH]["history"][-1]["change"]),
      ("1", "PROMOTED"))
check("H deferred SD row written", ([r["Concept Home"] for r in sh.sd], [n["id"]["Map Status"] for n in sh.notes.values()]),
      ([GCH], ["WRITTEN"]))
check("H graph home_ref still resolves", sh.graph.node("KN-33333333")["home_ref"] in sh.known_ids(), True)
check("H integrity clean", codes(integrity(P, sh, CG)), set())

# Test I - experience only
SI, CI = setup("delta", "PRJ-d4d4d4d4", "Delta")
EI = ev("LE-LP-1-01", "LP-1", "EXPERIENCE_ONLY", "Retry Budget", "retry sayısını sınırlar", reusable=True,
        experience=dict(SD_EXP, Selected="retry budget 3", **{"Failure Mode": "retry storm"}))
open_pass(SI, CI, "LP-1", [EI])
check("I status COMPLETE", persist_event(P, SI, CI, EI["id"], RNG), "COMPLETE")
si = State.load(P, SI, CI)
check("I experience note, concept UNASSIGNED", [(n["id"]["Concept ID"], n["id"]["Concept Home Ref"]) for n in si.notes.values()],
      [("UNASSIGNED", "-")])
check("I no Concept Home", (si.registry, si.homes, si.pointers), ([], {}, {}))
check("I SD row without home", [r["Concept Home"] for r in si.sd], ["-"])

# Test J - implementation detail
EJ = ev("LE-LP-2-01", "LP-2", "IMPLEMENTATION_DETAIL", "rename var", "-")
open_pass(SI, CI, "LP-2", [EJ])
snap = SI.snapshot()
check("J NOT_APPLICABLE", persist_event(P, SI, CI, EJ["id"], RNG), "NOT_APPLICABLE")
changed = sorted(k for k, v in SI.snapshot().items() if snap.get(k) != v)
check("J no file changed (marker already NOT_APPLICABLE)", changed, [])

# Test K - knowledge debt
SK, CK = setup("kappa", "PRJ-e5e5e5e5", "Kappa")
VI_MEAN = "benzer vektörleri hızlı bulur"
add_nodes(SK, node("KN-55555555", "Vector Index", VI_MEAN, status="DEBT", debt="KD-LP-1-01", events="LE-LP-1-01"))
SK.write(QUEUE, doc("Learning Queue", "B. Knowledge Debt", P.debt_cols, [{
    "debt_id": "KD-LP-1-01", "concept": "Vector Index", "originating_event_id": "LE-LP-1-01", "work_unit_ids": "WU-1",
    "one_sentence_explanation": "ANN index", "why_it_matters": "retrieval latency", "priority": "LATER",
    "debt_status": "OPEN", "created_at": "2026-10-27", "concept_home": "UNASSIGNED", "resolution_ref": "-"}]))
EK = ev("LE-LP-1-01", "LP-1", "KNOWLEDGE_DEBT", "Vector Index", VI_MEAN, concept_nodes=["KN-55555555"], debt_id="KD-LP-1-01")
open_pass(SK, CK, "LP-1", [EK])
check("K NOT_APPLICABLE", persist_event(P, SK, CK, EK["id"], RNG), "NOT_APPLICABLE")
sk = State.load(P, SK, CK)
check("K no learned Concept Home", (sk.registry, sk.homes, lib_files(SK)), ([], {}, []))
check("K debt reference kept OPEN", (sk.debts[0]["debt_status"], sk.debts[0]["concept_home"]), ("OPEN", "UNASSIGNED"))
check("K DEBT node unchanged", (sk.graph.node("KN-55555555")["node_status"], sk.graph.node("KN-55555555")["home_ref"]),
      ("DEBT", "UNASSIGNED"))
check("K integrity clean", codes(integrity(P, sk, CK)), set())

# Test L - debt resolved
VI_ART = "passes/LP-2/ula/LE-LP-2-01/LIGHT_ULA.md"
CK["artifacts"] = {VI_ART: {"L1", "L2"}}
gpass = {"id": "LP-2", "status": "COMPLETE", "events": [{"id": "LE-LP-2-01", "disposition": "ULA_CANDIDATE",
         "ula_status": "COMPLETE", "edges": [], "nodes": [{"name": "Vector Index", "type": "CONCEPT", "meaning": VI_MEAN,
                                                            "parent": None, "depth": ["L1", "L2"], "artifacts": [VI_ART]}]}]}
g2, st = gm.sync(P.gp, State.load(P, SK, CK).graph, gpass, {"artifacts": CK["artifacts"], "debts": {"KD-LP-1-01"}, "events": {}},
                 random.Random(1))
SK.write(GRAPH, g2.render(P.gp))
check("L map sync promoted DEBT -> ACTIVE (same node)", (st, g2.node("KN-55555555")["node_status"]),
      ({"LE-LP-2-01": "COMPLETE"}, "ACTIVE"))
EL = ev("LE-LP-2-01", "LP-2", "ULA_CANDIDATE", "Vector Index", VI_MEAN, ula_status="COMPLETE", concept_nodes=["KN-55555555"],
        artifact=light(VI_ART, **{"L1 — Simple Explanation": "Vector Index yakın vektörleri tüm veriyi taramadan bulur."}))
open_pass(SK, CK, "LP-2", [EL])
check("L status COMPLETE", persist_event(P, SK, CK, EL["id"], RNG), "COMPLETE")
sl = State.load(P, SK, CK)
LCH = sl.registry[0]["Concept ID"]
d = sl.debts[0]
check("L OPEN -> RESOLVED", (d["debt_status"], d["resolution_ref"], d["concept_home"]), ("RESOLVED", "LE-LP-2-01", LCH))
vn = sl.graph.node("KN-55555555")
check("L node ACTIVE, same id, home_ref", (vn["node_status"], vn["node_id"], vn["home_ref"]), ("ACTIVE", "KN-55555555", LCH))
check("L debt_id kept as history", vn["debt_id"], "KD-LP-1-01")
check("L integrity clean", codes(integrity(P, sl, CK)), set())

# Test M - false debt resolution
SM, CM = setup("mu", "PRJ-f6f6f6f6", "Mu", lib=LIB)
SM.write(QUEUE, doc("Learning Queue", "B. Knowledge Debt", P.debt_cols, [{
    "debt_id": "KD-LP-1-01", "concept": "Queue", "originating_event_id": "LE-LP-1-01", "work_unit_ids": "WU-1",
    "one_sentence_explanation": "-", "why_it_matters": "-", "priority": "LATER", "debt_status": "OPEN",
    "created_at": "2026-10-27", "concept_home": "UNASSIGNED", "resolution_ref": "-"}]))
EM = ev("LE-LP-2-01", "LP-2", "EXPERIENCE_ONLY", "Queue", Q_MEAN, reusable=False)
open_pass(SM, CM, "LP-2", [EM])
persist_event(P, SM, CM, EM["id"], RNG)
check("M home file exists (other project)", (LIB / "concepts" / f"{CH}.md").exists(), True)
ok, f = resolve_debt(P, SM, CM, "KD-LP-1-01", EM["id"])
check("M resolve without completed learning refused", ok, False)
check("M debt stays OPEN", State.load(P, SM, CM).debts[0]["debt_status"], "OPEN")
sm = State.load(P, SM, CM)
sm.debts[0].update({"debt_status": "RESOLVED", "concept_home": CH, "resolution_ref": EM["id"]})
check("M crafted RESOLVED -> P-12 FAIL", "P-12" in codes(integrity(P, sm, CM)), True)

# Test N - System Design Experience Map
sn = State.load(P, SA, CA)
row = next(r for r in sn.sd if r["Experience Note"].startswith("PRJ-a1a1a1a1/"))
check("N SD columns from template", list(row), P.sd_cols)
check("N SD row values", (row["Concept"], row["Project"], row["Problem"], row["Selected"], row["Reusable Signal"],
                          row["Concept Home"], row["Depth Reached"]),
      ("Queue", "PRJ-a1a1a1a1 (Alpha)", SD_EXP["Problem"], "background queue", SD_EXP["Reusable Signal"], CH, "L1; L2"))
check("N SD row note resolves", row["Experience Note"].split("/")[1] in sn.notes, True)
check("N one SD row per note (A + B projects)", sorted(r["Project"].split(" ")[0] for r in sn.sd),
      ["PRJ-a1a1a1a1", "PRJ-b2b2b2b2", "PRJ-b2b2b2b2"])
check("N SD row has no theory", any("Broker mesajı saklar" in v for v in row.values()), False)

# Test O - DSA Experience Map
EO = ev("LE-LP-4-01", "LP-4", "EXPERIENCE_ONLY", "Heap", "en büyük K öğeyi tutar", category="DSA", reusable=True,
        alternatives_in_project=2, selected_evidence="VERIFIED", priority="MUST_UNDERSTAND",
        experience=dict(SD_EXP, Problem="Günlük en hızlı yükselen 100 artist", Selected="min-heap size K",
                        **{"Reusable Signal": "Bütün veriyi sıralamak istemiyorum, yalnız top-K"}),
        dsa={"Pattern": "Top-K", "Naive Solution": "full sort", "Bottleneck": "O(n log n) gereksiz",
             "Time Complexity": "O(n log k)", "Space Complexity": "O(k)", "Real System Use": "ranking job"},
        decision={"Problem Pattern": "Top-K", "Chosen": "Heap"})
open_pass(SA, CA, "LP-4", [EO])
check("O status COMPLETE", persist_event(P, SA, CA, EO["id"], RNG), "COMPLETE")
so = State.load(P, SA, CA)
check("O DSA columns from template", list(so.dsa[0]) if so.dsa else None, P.dsa_cols)
check("O DSA row", [(r["Pattern"], r["Time Complexity"], r["Space Complexity"], r["Chosen Structure / Algorithm"]) for r in so.dsa],
      [("Top-K", "O(n log k)", "O(k)", "min-heap size K")])
check("O pattern in universal vocabulary", so.dsa[0]["Pattern"] in P.patterns, True)
check("O DSA_DR created", [t.split("Type:", 1)[1].split("\n")[0].strip() for t in so.drs.values()], ["DSA_DR"])
check("O DSA event not in SD map", any(r["Experience Note"] == so.dsa[0]["Experience Note"] for r in so.sd), False)

# Test P - non-DSA row in DSA map
sp = State.load(P, SA, CA)
sd_note = next(x for x, n in sp.notes.items() if n["id"]["Category"] == "SYSTEM_DESIGN")
sp.dsa.append(dict(sp.dsa[0], **{"Experience Note": f"PRJ-a1a1a1a1/{sd_note}"}))
check("P non-DSA in DSA map -> P-22 FAIL", "P-22" in codes(integrity(P, sp, CA)), True)

# Test Q - duplicate experience
txt = SA.read(pass_key("LP-1"))
kp_line = next(l for l in txt.splitlines() if l.startswith(f"| {EA['id']} |") and "EX-" in l)
SA.write(pass_key("LP-1"), txt.replace(kp_line + "\n", "").replace("| COMPLETE |\n", "| PENDING |\n"))
xid_before = sorted(State.load(P, SA, CA).notes)
check("Q second sync COMPLETE", persist_event(P, SA, CA, EA["id"], RNG), "COMPLETE")
sq = State.load(P, SA, CA)
check("Q no duplicate note (event lookup)", sorted(sq.notes), xid_before)
check("Q mapping restored", sq.kp("LP-1", EA["id"])["Experience ID"] in xid_before, True)
dup = copy.deepcopy(sq)
x0 = next(x for x, n in dup.notes.items() if n["id"]["Event ID"] == EA["id"])
dup.notes["EX-ffffffff"] = dict(copy.deepcopy(dup.notes[x0]), id=dict(dup.notes[x0]["id"], **{"Experience ID": "EX-ffffffff"}))
check("Q duplicate note same event -> P-09 FAIL", "P-09" in codes(integrity(P, dup, CA)), True)

# Test R - graph home_ref orphan
sr = State.load(P, SA, CA)
sr.graph.node("KN-11111111")["home_ref"] = "CH-deadbeef"
check("R orphan home_ref -> P-08 FAIL", "P-08" in codes(integrity(P, sr, CA)), True)

# Test S - personal library write failure
ES = ev("LE-LP-5-01", "LP-5", "ULA_CANDIDATE", "Cache", "pahalı sonucu saklar", ula_status="COMPLETE",
        artifact=light("passes/LP-5/ula/LE-LP-5-01/LIGHT_ULA.md"))
ES["concept"]["aliases"] = ["Queue"]
open_pass(SA, CA, "LP-5", [ES])
snap = SA.snapshot()
check("S invalid registry candidate -> BLOCKED", persist_event(P, SA, CA, ES["id"], RNG), "BLOCKED")
check("S reason P-06", "P-06" in codes(CA["last_fails"][ES["id"]]), True)
changed = sorted(k for k, v in SA.snapshot().items() if snap.get(k) != v)
check("S no partial write", changed, ["P:passes/LP-5/LEARNING_PASS.md"])
check("S coverage unchanged, pass COMPLETE", (SA.read(LEDGER).count("COVERED"), CA["passes"]["LP-5"]), (1, "COMPLETE"))
ES2 = ev("LE-LP-6-01", "LP-6", "ULA_CANDIDATE", "Cache", "pahalı sonucu saklar", ula_status="COMPLETE",
         artifact=light("passes/LP-6/ula/LE-LP-6-01/LIGHT_ULA.md"))
open_pass(SA, CA, "LP-6", [ES2])
snap = SA.snapshot()
SA.fail_on = {REG}
check("S registry write error -> BLOCKED", persist_event(P, SA, CA, ES2["id"], RNG), "BLOCKED")
SA.fail_on = set()
changed = sorted(k for k, v in SA.snapshot().items() if snap.get(k) != v)
check("S write error rolled back (no Home without registry)", changed, ["P:passes/LP-6/LEARNING_PASS.md"])
check("S library integrity clean after rollback", codes(integrity(P, State.load(P, SA, CA), CA)), set())

# Test T - rename
ok, f = rename(P, SA, CA, CH, "Message Queue")
st_ = State.load(P, SA, CA)
check("T rename committed", ok, True)
check("T same concept_id, old name alias", (st_.registry[0]["Concept ID"], st_.registry[0]["Aliases"],
                                             st_.homes[CH]["id"]["Canonical Name"]), (CH, "Queue", "Message Queue"))
check("T version +1", st_.homes[CH]["id"]["Version"], str(int(hf["id"]["Version"]) + 1))
check("T project pointers still resolve (A, B)", [p[0]["Concept ID"] in st_.known_ids() for p in st_.pointers.values()] +
      [State.load(P, SB, CB).pointers[CH][0]["Concept ID"] in State.load(P, SB, CB).known_ids()], [True, True])
check("T old name resolves via ALIAS", resolve(P, st_, {"concept": {"name": "Queue", "meaning": Q_MEAN}}, "PERSONAL"),
      ("ALIAS", CH))
fT = integrity(P, st_, CA)
check("T no FAIL; stale pointer label WARNING", (codes(fT), "P-24" in codes(fT, "WARNING")), (set(), True))

# Extra
check("X 4 ID kinds", P.ids, {"project_id": "PRJ-", "concept_id": "CH-", "experience_id": "EX-", "decision_id": "DR-"})
check("X persistence statuses", P.status, ["PENDING", "COMPLETE", "NOT_APPLICABLE", "BLOCKED"])
check("X home modes", P.modes, ["PERSONAL", "LOCAL_TEMPORARY"])
check("X provenance labels", P.provenance, ["ULA-DERIVED", "PROJECT-DERIVED", "GENERAL THEORY", "USER-CONFIRMED"])
check("X resolution order", P.resolution, ["GRAPH_HOME_REF", "CONCEPT_ID", "NAME", "ALIAS", "AMBIGUOUS", "NEW"])
check("X 28 P checks active", len(P.checks), 28)
check("X 16 DSA patterns", len(P.patterns), 16)
check("X config keys", [k for k in P.config_keys if k != "learning_config_version"],
      ["project_id", "project_name", "work_unit_source", "personal_library_path"])
check("X debt transitions", sorted(P.debt_tx), [("DISMISSED", "OPEN"), ("OPEN", "DISMISSED"), ("OPEN", "RESOLVED")])
check("X pointer template has no theory section", any(re.match(r"L[0-4]", k) for k in P.pointer_keys), False)
check("X experience note fields", P.note_exp_keys, ["Problem", "Constraint", "Why It Appeared", "Alternatives", "Selected",
                                                    "Why Selected", "Trade-off", "Failure Mode", "Observed Result", "Reusable Signal"])
check("X ADR / DSA_DR fields", (len(P.adr_keys), len(P.dsadr_keys)), (8, 10))
check("X no absolute library path in skill", str(LIB).split("fixtures")[0] in (skill_dir() / "references" / "06_KNOWLEDGE_PERSISTENCE.md").read_text(encoding="utf-8"), False)
# Extra - project rename keeps project_id
CB["config"]["project_name"] = "Beta Renamed"
EB2 = ev("LE-LP-3-01", "LP-3", "EXPERIENCE_ONLY", "Message Queue", Q_MEAN, reusable=True, concept_nodes=["KN-22222222"],
         experience=SD_EXP)
open_pass(SB, CB, "LP-3", [EB2])
persist_event(P, SB, CB, EB2["id"], RNG)
apps = State.load(P, SB, CB).homes[CH]["appearances"]
check("X project rename keeps project_id", sorted({a["project_id"] for a in apps}), ["PRJ-a1a1a1a1", "PRJ-b2b2b2b2"])
check("X new appearance uses new project_name", apps[-1]["project_name"], "Beta Renamed")
# Extra - index rebuildable
idx = SA.read(IDX)
SA.write(IDX, None)
check("X index rebuilt equals", doc("Personal Technical Library Index", "Concepts", P.idx_cols,
                                    build_index(P, State.load(P, SA, CA))) == idx, True)
SA.write(IDX, idx)
# Extra - unconfigured personal write attempt
SU, CU = setup("upsilon", "PRJ-0a0a0a0a", "Upsilon", configured=False)
EU = ev("LE-LP-1-01", "LP-1", "ULA_CANDIDATE", "Bloom Filter", "üyeliği yaklaşık test eder", ula_status="COMPLETE",
        artifact=light("passes/LP-1/ula/LE-LP-1-01/LIGHT_ULA.md"))
open_pass(SU, CU, "LP-1", [EU])
check("X unconfigured personal write -> BLOCKED", persist_event(P, SU, CU, EU["id"], RNG, {"library": "configure"}), "BLOCKED")
check("X ... reason P-17, no library files", ("P-17" in codes(CU["last_fails"][EU["id"]]), lib_files(SU)), (True, []))
# Extra - promotion changing concept_id
SV, CV = setup("phi", "PRJ-0b0b0b0b", "Phi", configured=False)
EV = ev("LE-LP-1-01", "LP-1", "ULA_CANDIDATE", "Bloom Filter", "üyeliği yaklaşık test eder", ula_status="COMPLETE",
        artifact=light("passes/LP-1/ula/LE-LP-1-01/LIGHT_ULA.md"))
open_pass(SV, CV, "LP-1", [EV])
persist_event(P, SV, CV, EV["id"], RNG, {"library": "local"})
vcid = next(iter(State.load(P, SV, CV).local))
CV["config"]["personal_library_path"] = str(SV.roots["L"])
CV["promotion_id_override"] = {vcid: "CH-00000bad"}
check("X promotion changed id -> BLOCKED", promote(P, SV, CV, RNG), {vcid: "BLOCKED"})
check("X ... reason P-19, nothing written", ("P-19" in codes(CV["last_fails"]["promotion"]), lib_files(SV)), (True, []))
# Extra - crafted integrity cases
base = State.load(P, SA, CA)


def crafted(mut):
    s = copy.deepcopy(base)
    mut(s)
    return codes(integrity(P, s, CA))


check("X duplicate concept_id -> P-01", "P-01" in crafted(lambda s: s.registry.append(dict(s.registry[0], **{"Canonical Name": "Other"}))), True)
check("X registry without home -> P-03", "P-03" in crafted(lambda s: s.homes.pop(CH)), True)
check("X home without registry -> P-04", "P-04" in crafted(lambda s: s.registry.pop(0)), True)
check("X canonical name conflict -> P-05", "P-05" in crafted(lambda s: s.registry.append(dict(s.registry[0], **{"Concept ID": "CH-12345678", "Aliases": "-"}))), True)
check("X pointer unknown concept -> P-07", "P-07" in crafted(lambda s: s.pointers.update({"CH-87654321": (dict(s.pointers[CH][0], **{"Concept ID": "CH-87654321"}), "")})), True)
check("X duplicate appearance -> P-10", "P-10" in crafted(lambda s: s.homes[CH]["appearances"].append(s.homes[CH]["appearances"][0])), True)
x_sd = next(x for x, n in base.notes.items() if n["id"]["Concept ID"] == CH)
check("X note with theory -> P-11", "P-11" in crafted(lambda s: s.notes[x_sd].update(raw=s.notes[x_sd]["raw"] + "\n## L1 — Simple Explanation\n")), True)
check("X DISMISSED without user -> P-15", "P-15" in crafted(lambda s: s.debts.append({"debt_id": "KD-X-01", "concept": "X", "debt_status": "DISMISSED", "resolution_ref": "-", "concept_home": "UNASSIGNED"})), True)
check("X COMPLETE but note missing -> P-16", "P-16" in crafted(lambda s: s.notes.pop(x_sd)), True)
check("X LOCAL_TEMPORARY marked personal -> P-18", "P-18" in crafted(lambda s: s.pointers[CH][0].update({"Home Mode": "LOCAL_TEMPORARY"})), True)
check("X SD row missing note -> P-20", "P-20" in crafted(lambda s: s.sd.append(dict(s.sd[0], **{"Experience Note": "PRJ-a1a1a1a1/EX-00000000"}))), True)
check("X registry/home mismatch -> P-23", "P-23" in crafted(lambda s: s.registry[0].update({"Canonical Name": "Kuyruk"})), True)
check("X provenance missing -> P-26", "P-26" in crafted(lambda s: s.homes[CH]["sections"].update({"L1 — Simple Explanation": "metin"})), True)
check("X VERIFIED without ref -> P-27", "P-27" in crafted(lambda s: s.notes[x_sd]["evidence"].append({"Claim": "Selected", "Evidence Status": "VERIFIED", "Evidence Ref": "-"})), True)
CA["events"][EA["id"]]["claim_sources"] = {"Constraint": "UNRESOLVED"}
check("X UNRESOLVED fact as VERIFIED -> P-27", "P-27" in crafted(lambda s: s.notes[x_sd]["evidence"].append({"Claim": "Constraint", "Evidence Status": "VERIFIED", "Evidence Ref": "issue:INC-1"})), True)
CA["events"][EA["id"]].pop("claim_sources")
check("X pointer with theory -> P-28", "P-28" in crafted(lambda s: s.pointers.update({CH: (s.pointers[CH][0], render_pointer(s.pointers[CH][0]) + "\n## L1 — Simple Explanation\n")})), True)
prev = copy.deepcopy(base)
cur_ = copy.deepcopy(base)
cur_.homes[CH]["id"]["Version"] = str(int(cur_.homes[CH]["id"]["Version"]) + 1)
check("X version bump without change -> P-25", "P-25" in codes(integrity(P, cur_, CA, prev=prev)), True)
cur_ = copy.deepcopy(base)
cur_.homes[CH]["sections"]["Reference"] = "Provenance: ULA-DERIVED (x)\n\nyeni"
check("X content change without bump -> P-25", "P-25" in codes(integrity(P, cur_, CA, prev=prev)), True)
cur_ = copy.deepcopy(base)
cur_.homes[CH]["appearances"].append(dict(cur_.homes[CH]["appearances"][0], event_id="LE-NEW"))
check("X appearance only, same version -> no P-25", "P-25" in codes(integrity(P, cur_, CA, prev=prev)), False)

report(RESULTS)
