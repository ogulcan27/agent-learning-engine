"""Unified Knowledge View suite (09_KNOWLEDGE_VIEW, 07 §V).

Usage: run_tests.py [<skill_dir>]
Temporary git projects get real Human Sync state from the sync model (08); graph, ULA artifacts and queue §B are fixtures
written in their template formats. The view is built, patched, read and checked by the view model (09).
"""
import atexit
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import REPO as DEV_REPO, report, skill_dir, use  # noqa: E402

use("sync", "view")
import sync_model as sm  # noqa: E402
import view_model as vm  # noqa: E402
from sync_model import Repo, wu  # noqa: E402
from view_model import GRAPH_F, QUEUE_F, VIEW_F, Reader, View, ViewBlocked  # noqa: E402

SKILL = skill_dir()
SP = sm.Protocol(SKILL)
P = vm.Protocol(SKILL)
TMP = Path(tempfile.mkdtemp(prefix="view_"))
atexit.register(shutil.rmtree, TMP, True)
RESULTS = []
PRJ = "PRJ-7c1d2e3f"
INTERNAL = {"state", "sync", "passes", "maps", "concepts", "experiences", "audits"}


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def project(name, prj=PRJ, steps=3):
    repo = Repo(TMP / name)
    repo.write(sm.CONFIG_F, f"# Learning Config\n\n```text\nproject_id: {prj}\nproject_name: {name}\npersonal_library_path: UNCONFIGURED\n"
                            "work_unit_source: phase-doc\n```\n")
    for n in range(1, steps + 1):
        repo.step(n, [f"src/s{n}.py"])
    return repo


def state_rows(root):
    text = (root / sm.STATE_F).read_text(encoding="utf-8") if (root / sm.STATE_F).exists() else None
    return sm.parse_state(SP, text)[1] if text else []


def sync(repo, view, arg="", judge=None, sync_only=True):
    """08 §11 sync-only run, then the 09 §8 view trigger with the pre-run state rows."""
    pre = state_rows(repo.root)
    out = sm.Sync(SP, repo.root).run(arg, judge=judge)
    rd = Reader()
    out["view"] = view.on_sync(pre, rd, sync_only=sync_only)
    out["view_reads"] = rd.log
    return out


def blocks(text):
    """{key: block text} for every marker section."""
    return {k: View.lines_of(text, s) for k, s in View.spans(text).items()}


def vtext(repo):
    return (repo.root / VIEW_F).read_text(encoding="utf-8")


def hs(n):
    return f"HS:{sm.record_id(wu(n))}"


def node(nid, name, ntype="CONCEPT", parent="-", depth="-", status="ACTIVE", arts="-", events="-", meaning="Kısa anlam cümlesi burada."):
    d = {c: "-" for c in P.node_cols}
    d.update(node_id=nid, canonical_name=name, node_type=ntype, parent_id=parent, short_meaning=meaning, system_role="Rol.",
             home_ref="UNASSIGNED", available_depth=depth, source_event_ids=events, source_artifacts=arts, node_status=status)
    return d


def edge(eid, s, rel, t):
    d = {c: "-" for c in P.edge_cols}
    d.update(edge_id=eid, source_node_id=s, relation_type=rel, target_node_id=t, meaning="m", evidence_status="VERIFIED")
    return d


def write_graph(repo, version, nodes, edges):
    repo.write(GRAPH_F, vm.render_graph(P, version, nodes, edges))


TPL_LIGHT = (SKILL / "templates" / "LIGHT_ULA_TEMPLATE.md").read_text(encoding="utf-8")
TPL_FULL = (SKILL / "ula" / "templates" / "CONTENT_BUILD_TEMPLATE.md").read_text(encoding="utf-8")


def light(repo, rel, topic, filled, status="COMPLETE"):
    """LIGHT_ULA.md from the template: given sections filled, others keep the template body."""
    out, cur = [], None
    for line in TPL_LIGHT.splitlines():
        m = re.match(r"^## (.+)$", line)
        if m:
            cur = m.group(1)
            out += [line, "", filled[cur], ""] if cur in filled else [line]
            continue
        if cur in filled:
            continue
        out.append(line.replace("status: IN_PROGRESS", f"status: {status}").replace("<canonical technical term>", topic))
    repo.write(rel, "\n".join(out) + "\n")


def full(repo, rel, filled, status="COMPLETE"):
    """CONTENT.md from the template with a 04 §9 header: given level-1 sections filled, others 'internal …'."""
    out, cur = [f"```yaml\nevent_id: LE-x\nartifact: CONTENT\nartifact_status: {status}\nupdated_at: 2026-10-28\n```\n"], None
    for line in TPL_FULL.splitlines():
        m = re.match(r"^# (.+)$", line)
        if m:
            cur = m.group(1)
            out += [line, "", filled.get(cur, f"internal {cur} text"), ""]
            continue
        if cur is None:
            out.append(line)
    repo.write(rel, "\n".join(out) + "\n")


L_LIGHT = {"L0 — Local Map": "Data → Split → Model", "L1 — Simple Explanation": "Gelecek bilgisi geçmişe sızar. Skor yanlış iyi görünür.",
           "L2 — Mechanism": "1. Feature gelecek satırı kullanır.\n2. Model bunu ezberler.\n\n```text\nt+1 → feature(t)\n```",
           "Retrieval": "Hangi feature gelecek bilgisini taşır?"}
L_FULL = {"Local Map": "```text\nData → Split → Walk-Forward → Score\n```", "L1 — Simple Explanation": "Zaman sırasını koruyarak test et.",
          "L2 — Mechanism": "## Mechanism Map\n\nPencere ileri kayar. Her adımda yalnız geçmiş eğitilir.",
          "L3 — Theory": "## Core Idea\n\nStationarity varsayımı zayıftır.", "L4 — Math / Formalism": "## Formula / Formal Representation\n\n$$E = \\frac{1}{K}\\sum_k e_k$$",
          "Example": "Aylık veri, 12 pencere.", "Retrieval Check": "Pencere neden ileri kayar?", "R — Reference Links": "GENERAL THEORY: time-series CV."}


def learning_graph(repo, version=1, extra=()):
    """ROOT → Validation (DOMAIN) → Temporal Leakage (Light), Walk-Forward (Full or not yet)."""
    nodes = [node("KN-00000001", "Project Root", "ROOT"),
             node("KN-0000000a", "Validation", "DOMAIN", "KN-00000001"),
             node("KN-0000000b", "Temporal Leakage", "CONCEPT", "KN-0000000a", "L1; L2", events="LE-LP-20261028-01-01",
                  arts=LIGHT_A)]
    return nodes + list(extra)


LIGHT_A = "docs/learning/passes/LP-20261028-01/ula/LE-LP-20261028-01-01/LIGHT_ULA.md"
FULL_A = "docs/learning/passes/LP-20261028-02/ula/LE-LP-20261028-02-01/CONTENT.md"


def human_files(root):
    learn = root / "docs/learning"
    return sorted(f.relative_to(learn).as_posix() for f in learn.rglob("*") if f.is_file() and f.relative_to(learn).parts[0] not in INTERNAL)


# Test A - creation only when content exists (09 §2)
pa = project("pa")
va = View(P, pa.root)
check("A initialized project without content -> no view", (va.update(["INDEX"]), (pa.root / VIEW_F).exists()), ("NO_CONTENT", False))
check("A no content -> no V finding", va.integrity(None), [])
pu = project("pu", prj="UNCONFIGURED")
check("A project_id UNCONFIGURED -> no view", (View(P, pu.root).update(["INDEX"]), (pu.root / VIEW_F).exists()), ("NO_CONTENT", False))
check("A skill install / dev repository has no view", (DEV_REPO / VIEW_F).exists(), False)

# Test B - incremental Human Sync presentation: Stages 1-3, then 4-5 (spec 36)
pb = project("pb")
vb = View(P, pb.root)
r1 = sync(pb, vb)
t1 = vtext(pb)
b1 = blocks(t1)
check("B first sync creates the view", (r1["view"], sorted(k for k in b1 if k.startswith("HS:"))), ("CREATED", sorted(hs(n) for n in (1, 2, 3))))
check("B view == deterministic rebuild", t1, vb.rebuild())
check("B no V finding", vb.integrity(t1), [])
pb.step(4, ["src/s4.py"])
pb.step(5, ["src/s5.py"])
r2 = sync(pb, vb)
t2 = vtext(pb)
b2 = blocks(t2)
check("B Stages 1-3 sections byte-identical", [b2[hs(n)] == b1[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("B Stages 4-5 added", (r2["view"], hs(4) in b2, hs(5) in b2), ("UPDATED", True, True))
idx = re.findall(r"^- \[(Step \d)\]\(#(hs-[0-9a-f]{8})\)", b2["INDEX"], re.M)
check("B index lists 5 units in seq order with stable anchors", idx, [(f"Step {n}", sm.record_id(wu(n)).lower()) for n in range(1, 6)])
check("B HS order in file follows seq", [k for k in View.spans(t2) if k.startswith("HS:")], [hs(n) for n in range(1, 6)])
check("B second update reads only new records, no whole view", (sorted(k for k, _, _ in r2["view_reads"] if k == "RECORD"),
      sorted(u for k, u, _ in r2["view_reads"] if k == "RECORD"), "WHOLE_REBUILD" in [k for k, _, _ in r2["view_reads"]]),
      (["RECORD", "RECORD"], sorted([sm.record_id(wu(4)), sm.record_id(wu(5))]), False))
check("B unrelated sections only touched by index", [k for k in b2 if k in b1 and b1[k] != b2[k]], ["INDEX", "MODEL"])
check("B incremental == rebuild after Stage 5", t2, vb.rebuild())
check("B HS section hides machine metadata", [x for x in ("checkpoint", "record_version", "git:", "Evidence / Provenance") if x in b2[hs(4)]], [])
check("B empty record parts omitted, Purpose kept", re.findall(r"^#### (.+)$", b2[hs(1)], re.M), ["Purpose"])
check("B status line Current", "**Status:** Current ·" in b2[hs(1)], True)
again = sync(pb, vb)
check("B up-to-date sync -> view unchanged", (again["result"], vtext(pb) == t2), ("UP_TO_DATE", True))

# Test C - stale presentation and refresh (spec 37)
pc = project("pc", steps=4)
pc.step(5, ["src/s5.py"], depends=2)
pc.step(6, ["src/s6.py"])
vc = View(P, pc.root)
sync(pc, vc)
c0 = vtext(pc)
pc.write("src/s2.py", "# step 2 changed\nv2 behaviour\n")
pc.commit("change step 2")
judge = {("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(5)): "CONTRACT"}
rc = sync(pc, vc, "latest", judge)
c1 = vtext(pc)
k0, k1 = blocks(c0), blocks(c1)
st = {r["work_unit_id"]: r["sync_status"] for r in state_rows(pc.root)}
check("C material change -> Step 2 + dependent Step 5 STALE (state)", (st[wu(2)], st[wu(5)], st[wu(1)]), ("STALE", "STALE", "SYNCED"))
check("C stale shown as Needs refresh", ["**Status:** Needs refresh ·" in k1[hs(n)] for n in (2, 5)], [True, True])
check("C only status line changed in stale sections", [[a for a, b in zip(k0[hs(n)].splitlines(), k1[hs(n)].splitlines()) if a != b] for n in (2, 5)],
      [[k0[hs(2)].splitlines()[4]], [k0[hs(5)].splitlines()[4]]])
check("C unrelated HS sections byte-identical", [k0[hs(n)] == k1[hs(n)] for n in (1, 3, 4, 6)], [True] * 4)
check("C index marks needs refresh", re.findall(r"\(#(hs-[0-9a-f]{8})\) · needs refresh", k1["INDEX"]),
      [sm.record_id(wu(2)).lower(), sm.record_id(wu(5)).lower()])
check("C no duplicate stale + current versions", (c1.count(f"SITL:{hs(2)}:START"), c1.count("#### Purpose")), (1, 6))
check("C stale view passes V checks", vc.integrity(c1), [])
check("C sync latest: target empty, staleness persisted only", (rc["synced"], rc["refreshed"]), ([], []))
rc2 = sync(pc, vc, "", judge)
c2 = vtext(pc)
k2 = blocks(c2)
check("C refresh -> v2, Current again", [(View.spans(c2)[hs(n)][2]["v"], "**Status:** Current ·" in k2[hs(n)]) for n in (2, 5)], [("2", True), ("2", True)])
check("C refresh leaves unrelated HS byte-identical", [k1[hs(n)] == k2[hs(n)] for n in (1, 3, 4, 6)], [True] * 4)
check("C refresh content from new record version", "(v2)" in k2[hs(2)], True)
check("C incremental == rebuild", c2, vc.rebuild())

# Test D - Light then Full ULA persist into one concept section (spec 38)
pd = project("pd")
vd = View(P, pd.root)
sync(pd, vd)
d0 = blocks(vtext(pd))
light(pd, LIGHT_A, "Temporal Leakage", L_LIGHT)
before_files = sorted(f.relative_to(pd.root).as_posix() for f in pd.root.rglob("*") if f.is_file() and ".git" not in f.parts)
pre_graph = None
write_graph(pd, 1, learning_graph(pd), [])
rd = Reader()
check("D map sync -> view updated", vd.on_map_sync(pre_graph, rd), "UPDATED")
d1 = vtext(pd)
kb = blocks(d1)["KN:KN-0000000b"]
check("D Light concept in STAY_IN_THE_LOOP.md", ("### KN-0000000b — Temporal Leakage" in kb, "Skor yanlış iyi görünür." in kb), (True, True))
check("D Light levels only L0-L2 (+Retrieval)", re.findall(r"^#### (.+)$", kb, re.M),
      ["Where am I?", "L0 — Map", "L1 — Simple Mental Model", "L2 — Mechanism", "Retrieval"])
check("D Light: no L3 / L4 fabricated", ("L3 —" in kb, "L4 —" in kb, "<details>" in kb), (False, False, False))
check("D Light: Self-Check / Metadata not shown", ("Self-Check" in kb, "mode: LIGHT" in kb), (False, False))
check("D marker depth = available_depth", View.spans(d1)["KN:KN-0000000b"][2]["depth"], "L1;L2")
after_files = sorted(f.relative_to(pd.root).as_posix() for f in pd.root.rglob("*") if f.is_file() and ".git" not in f.parts)
check("D no new user-facing file (only graph fixture added)", sorted(set(after_files) - set(before_files)), [GRAPH_F])
check("D HS sections untouched by learning", [blocks(d1)[hs(n)] == d0[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("D artifact reads limited to the concept's artifact", sorted({u for k, u, _ in rd.log if k == "ARTIFACT"}), [LIGHT_A])
check("D no record read for a learning update", [u for k, u, _ in rd.log if k == "RECORD"], [])
g1 = (pd.root / GRAPH_F).read_text(encoding="utf-8")
full(pd, FULL_A, L_FULL)
nodes = learning_graph(pd)
nodes[2] = dict(nodes[2], available_depth="L1; L2; L3; L4", source_artifacts=f"{LIGHT_A}; {FULL_A}",
                source_event_ids="LE-LP-20261028-01-01; LE-LP-20261028-02-01")
write_graph(pd, 2, nodes, [])
vd.on_map_sync(g1)
d2 = vtext(pd)
kf = blocks(d2)["KN:KN-0000000b"]
check("D Full: deeper levels in the same section", (d2.count("SITL:KN:KN-0000000b:START"), "<summary><strong>L3 — Theory</strong></summary>" in kf,
      "<summary><strong>L4 — Formalism</strong></summary>" in kf), (1, True, True))
check("D Full: L1 from latest artifact, L0 kept", ("Zaman sırasını koruyarak test et." in kf, "#### L0 — Map" in kf), (True, True))
check("D Full: L0-L2 open, L3 / L4 / Reference collapsed", (kf.count("<details>"), "#### L2 — Mechanism" in kf), (3, True))
check("D Full: internal artifact parts not shown", [x for x in ("internal Oral Version", "internal Content Integrity Check", "internal Transition")
                                                  if x in kf], [])
check("D Full: inner artifact headings demoted", (re.findall(r"^#{1,3} ", kf, re.M), "###### Core Idea" in kf), (["### "], True))
check("D Full: only the concept + index changed", [k for k in blocks(d2) if blocks(d1).get(k) != blocks(d2)[k]], ["INDEX", "KN:KN-0000000b"])
check("D no per-level user-facing file", human_files(pd.root), ["STAY_IN_THE_LOOP.md"])
check("D view == rebuild", d2, vd.rebuild())
check("D view passes V checks", vd.integrity(d2), [])

# Test E - normal workflow reuses Human Sync; learning not duplicated (spec 39)
pe = project("pe")
ve = View(P, pe.root)
hsj = {("hs", wu(2)): {"Purpose": "Validation katmanı eklendi → sızıntı kontrolü → güvenilir skor",
                       "Why It Changed": "Skorlar fazla iyiydi. Kontrol gerekliydi.", "Dependencies": "Yok."}}
sync(pe, ve, judge=hsj)
e0 = vtext(pe)
rd = Reader()
src = sm.Sync(SP, pe.root).full_sources([wu(1), wu(2), wu(3)], reader=rd)
check("E full mode reuses SYNCED records", set(map(tuple, src.values())), {("OWN_RECORD",)})
check("E view HS unchanged by full-mode Human Sync reuse", ve.on_sync(state_rows(pe.root)), "UNCHANGED")
light(pe, LIGHT_A, "Temporal Leakage", L_LIGHT)
write_graph(pe, 1, learning_graph(pe), [])
ve.on_map_sync(None)
e1 = vtext(pe)
eb = blocks(e1)
check("E HS sections byte-identical after learning", [blocks(e0)[hs(n)] == eb[hs(n)] for n in (1, 2, 3)], [True, True, True])
check("E HS parts follow 09 §5 order, empty ones omitted", re.findall(r"^#### (.+)$", eb[hs(2)], re.M), ["Purpose", "Why"])
check("E learning added to Learning section", e1.index("## Learning") < e1.index("SITL:KN:KN-0000000b:START") < e1.index("SITL:MAP:START"), True)
hs_lines = {l for k, b in eb.items() if k.startswith("HS:") for l in b.splitlines() if len(l) > 25}
kn_lines = {l for k, b in eb.items() if k.startswith("KN:") for l in b.splitlines() if len(l) > 25}
check("E no prose shared between Human Sync and Learning", sorted(hs_lines & kn_lines), [])
check("E Learning index states Human Sync ≠ learned", "Human Sync ≠ learned" in eb["INDEX"], True)

# Test F - sync-only never writes KN / MAP / DEBT (08 §11, 09 §8, V-13)
check("F 08 §11 sync-only view scope", P.sync_only_kinds, ["HS", "MODEL", "INDEX"])
pe.write(QUEUE_F, vm.render_queue(P, [dict(zip(P.debt_cols, ["KD-LP-20261028-01-01", "Regime Persistence", "LE-LP-20261028-01-02",
                                                           wu(3), "Rejim kalıcılığı.", "Model seçimi.", "LATER", "OPEN", "2026-10-28", "UNASSIGNED", "-"]))]))
ve.on_debt()
f0 = blocks(vtext(pe))
check("F debt listed in Open Learning Debt", "`KD-LP-20261028-01-01` — Regime Persistence · LATER" in f0["DEBT"], True)
pe.step(4, ["src/s4.py"])
sync(pe, ve)
f1 = blocks(vtext(pe))
check("F sync-only: KN / MAP / DEBT byte-identical", [f0[k] == f1[k] for k in ("KN:KN-0000000b", "MAP", "DEBT")], [True, True, True])
check("F sync-only: new HS added", hs(4) in f1, True)
rd = Reader()
ve.update(["KN:KN-0000000b", "MAP", "DEBT"], rd, sync_only=True)
check("F sync-only filters KN / MAP / DEBT keys", [u for k, u, _ in rd.log if k == "SECTION"], [])

# Test G - section-level retrieval on a large view (spec 40)
pg = project("pg", steps=40)
vg = View(P, pg.root)
sm.Sync(SP, pg.root).run("")
big = [node("KN-00000001", "Project Root", "ROOT")] + [node(f"KN-a{d:07x}", f"Domain {d}", "DOMAIN", "KN-00000001", "L1", arts=LIGHT_A)
                                                         for d in range(6)]
for i in range(150):
    big.append(node(f"KN-{i + 0x100:08x}", f"Concept {i}", "CONCEPT", f"KN-a{i % 6:07x}", "L1; L2", arts=LIGHT_A, events=f"LE-{i}"))
bedges = [edge(f"KE-{i:04d}", f"KN-{i + 0x100:08x}", "REQUIRES", f"KN-{i + 0x101:08x}") for i in range(0, 149, 7)]
light(pg, LIGHT_A, "Concept", L_LIGHT)
write_graph(pg, 1, big, bedges)
vg.update([])
gt = vtext(pg)
total = len(gt.splitlines())
rd = Reader()
got = vg.retrieve("KN", "KN:KN-00000107", rd=rd)
read_lines = sum(n for k, _, n in rd.log if k in ("SECTION", "WHOLE_VIEW"))
check("G KN plan = markers + index + target", [(k, u) for k, u, _ in rd.log], [("MARKERS", "-"), ("SECTION", "INDEX"), ("SECTION", "KN:KN-00000107")])
check("G whole document not read by default", "WHOLE_VIEW" in rd.kinds(), False)
check("G lines read << document", (read_lines < total / 4, total > 2000), (True, True))
check("G target section returned intact", (got["KN:KN-00000107"].startswith("<!-- SITL:KN:KN-00000107:START"),
                                           got["KN:KN-00000107"].endswith("<!-- SITL:KN:KN-00000107:END -->")), (True, True))
rd = Reader()
vg.retrieve("KN", "KN:KN-00000107", deps=True, rd=rd)
check("G dependencies only on request: REQUIRES target", [u for k, u, _ in rd.log if k == "SECTION"], ["INDEX", "KN:KN-00000107", "KN:KN-00000108"])
rd = Reader()
vg.retrieve("HS", hs(7), rd=rd)
check("G HS plan = markers + index + target", [u for k, u, _ in rd.log if k == "SECTION"], ["INDEX", hs(7)])
check("G 09 §9 never-list keeps WHOLE_VIEW out of HS / KN", all("WHOLE_VIEW" in P.plan[r][1] and "WHOLE_VIEW" not in P.plan[r][0] for r in ("HS", "KN")), True)

# Test H - section write stability (spec 41)
g_pre = (pg.root / GRAPH_F).read_text(encoding="utf-8")
big2 = [dict(n) for n in big]
target = next(n for n in big2 if n["node_id"] == "KN-00000120")
target["available_depth"] = "L1; L2; L3"
light(pg, "docs/learning/passes/LP-x/ula/LE-x/LIGHT_ULA.md", "Concept", dict(L_LIGHT, **{"L3 — Theory": "Neden: varsayım bozulur."}))
target["source_artifacts"] = f"{LIGHT_A}; docs/learning/passes/LP-x/ula/LE-x/LIGHT_ULA.md"
write_graph(pg, 2, big2, bedges)
rd = Reader()
vg.on_map_sync(g_pre, rd)
ht = vtext(pg)
hb0, hb1 = blocks(gt), blocks(ht)
check("H only the modified concept + index changed", sorted(k for k in hb1 if hb0.get(k) != hb1[k]), ["INDEX", "KN:KN-00000120"])
check("H every other section byte-identical", sum(hb0[k] == hb1[k] for k in hb0), len(hb0) - 2)
check("H unchanged prefix / suffix bytes", (ht.split("<!-- SITL:KN:KN-00000120:START")[0].split("<!-- SITL:INDEX:END -->")[1]
                                            == gt.split("<!-- SITL:KN:KN-00000120:START")[0].split("<!-- SITL:INDEX:END -->")[1],
                                            ht.split("<!-- SITL:KN:KN-00000120:END -->")[1] == gt.split("<!-- SITL:KN:KN-00000120:END -->")[1]), (True, True))
check("H write read only the changed concept", (sorted({u for k, u, _ in rd.log if k == "SECTION"}), "WHOLE_REBUILD" in rd.kinds()),
      (["INDEX", "KN:KN-00000120", "MAP"], False))
check("H incremental == rebuild", ht, vg.rebuild())

# Test I - global map derived from the Semantic Graph (spec 42)
gmap = blocks(ht)["MAP"]
mer = vm.mermaid_blocks(gmap + "\n")
check("I one Mermaid flowchart LR", (len(mer), mer[0].splitlines()[0]), (1, "flowchart LR"))
check("I Mermaid static check", vm.mermaid_errors(mer[0]), [])
ids = set(re.findall(r"KN_([0-9a-f]{8})\[", mer[0]))
gnodes = {n["node_id"]: n for n in big2}
check("I map nodes are graph nodes", all(f"KN-{i}" in gnodes for i in ids), True)
pedges = re.findall(r"KN_([0-9a-f]{8}) --> KN_([0-9a-f]{8})$", mer[0], re.M)
check("I map edges = graph parent_id", all(gnodes[f"KN-{c}"]["parent_id"] == f"KN-{p}" for p, c in pedges) and len(pedges) == len(ids) - 1, True)
check("I map has no lesson / meaning text", ("Kısa anlam" in gmap, "Skor yanlış" in gmap, "Rol." in gmap), (False, False, False))
labels = re.findall(r'\["([^"]*)"\]', mer[0])
check("I short labels: name + ID only", all(len(l.split(" (KN-")[0]) <= P.int_rule("map_label_max_chars") and re.search(r"\(KN-[0-9a-f]{8}\)$", l)
                                            for l in labels), True)
pi = project("pi", steps=1)
long_name = "A Very Long Canonical Concept Name That Goes Beyond The Map Limit Easily"
write_graph(pi, 1, [node("KN-00000001", "Root", "ROOT"), node("KN-00000002", long_name, parent="KN-00000001", depth="L1", arts=LIGHT_A),
                    node("KN-00000003", "Next Step", parent="KN-00000001", status="DEBT")],
            [edge("KE-0001", "KN-00000002", "NEXT", "KN-00000003"), edge("KE-0002", "KN-00000002", "USES", "KN-00000003")])
light(pi, LIGHT_A, "x", L_LIGHT)
vi = View(P, pi.root)
vi.update([])
imap = blocks(vtext(pi))["MAP"]
check("I long label shortened, DEBT tagged, NEXT edge drawn", ("…" in imap, long_name not in imap, "Next Step (DEBT) (KN-00000003)" in imap,
                                                            "KN_00000002 -. NEXT .-> KN_00000003" in imap), (True, True, True, True))
check("I global map shows only hierarchy + NEXT (no USES)", "USES" in imap, False)
check("I DEBT node: no Learning section, appears in map", ("SITL:KN:KN-00000003" in vtext(pi), "KN_00000003" in imap), (False, True))

# Test J - recursive zoom: global map + local maps (spec 43)
pj = project("pj", steps=1)
zn = [node("KN-00000001", "Machine Learning", "ROOT"),
      node("KN-00000010", "Sequence Models", "DOMAIN", "KN-00000001", "L1", arts=LIGHT_A),
      node("KN-00000020", "Hidden-State Models", "CONCEPT", "KN-00000010", "L1; L2", arts=LIGHT_A),
      node("KN-00000021", "Attention", "CONCEPT", "KN-00000010", "L1", arts=LIGHT_A),
      node("KN-00000022", "Recurrent Nets", "CONCEPT", "KN-00000010", "L1", arts=LIGHT_A),
      node("KN-00000030", "State Process", "CONCEPT", "KN-00000020", "L1", arts=LIGHT_A),
      node("KN-00000031", "Observation Process", "CONCEPT", "KN-00000020", "L1", arts=LIGHT_A),
      node("KN-00000032", "Duration", "CONCEPT", "KN-00000020", "L1; L2", arts=LIGHT_A),
      node("KN-00000040", "Duration Model", "CONCEPT", "KN-00000032", "L1", arts=LIGHT_A),
      node("KN-00000050", "Probabilistic Models", "DOMAIN", "KN-00000001")]
ze = [edge("KE-0001", "KN-00000020", "PART_OF", "KN-00000050"), edge("KE-0002", "KN-00000020", "USES", "KN-00000040")]
light(pj, LIGHT_A, "x", L_LIGHT)
write_graph(pj, 1, zn, ze)
vj = View(P, pj.root)
vj.update([])
jt = vtext(pj)
jb = blocks(jt)
jmap = vm.mermaid_blocks(jb["MAP"] + "\n")[0]
check("J global map: depth <= 2 only", (("KN_00000020" in jmap), ("KN_00000030" in jmap), ("KN_00000040" in jmap)), (True, False, False))
lm = {k: vm.mermaid_blocks(b + "\n") for k, b in jb.items() if k.startswith("KN:")}
check("J local maps only for 3+ children", sorted(k for k, v in lm.items() if v), ["KN:KN-00000010", "KN:KN-00000020"])
hsm = lm["KN:KN-00000020"][0]
check("J local map: State / Observation / Duration branches", [c in hsm for c in ("KN_00000030", "KN_00000031", "KN_00000032")], [True, True, True])
check("J local map shows node relations", "KN_00000020 -- USES --> KN_00000040" in hsm, True)
check("J local maps valid Mermaid", [vm.mermaid_errors(v[0]) for v in lm.values() if v], [[], []])
check("J breadcrumb from parent_id chain", re.search(r"^.* → \*\*Duration Model\*\*$", jb["KN:KN-00000040"], re.M).group(0),
      "Machine Learning → [Sequence Models](#kn-00000010) → [Hidden-State Models](#kn-00000020) → [Duration](#kn-00000032) → **Duration Model**")
check("J secondary membership shown separately", "Also part of: Probabilistic Models" in jb["KN:KN-00000020"], True)
check("J maps carry no lesson text", any("Skor yanlış" in b for k, b in jb.items() if k == "MAP") or any("Skor yanlış" in m[0] for m in lm.values() if m), False)
check("J lesson text once per concept section", all(b.count("Skor yanlış iyi görünür.") == 1 for k, b in jb.items() if k.startswith("KN:")), True)
check("J related concepts link to sections", "- USES → [Duration Model](#kn-00000040)" in jb["KN:KN-00000020"], True)

# Test K - 07 §V integrity, candidate safety, write failure (spec 33, 34)
check("K 14 V checks", sorted(P.checks), [f"V-{i:02d}" for i in range(1, 15)])
check("K structural / misleading checks FAIL", sorted(c for c, s in P.checks.items() if s == "FAIL"),
      ["V-02", "V-03", "V-04", "V-05", "V-09", "V-10", "V-12", "V-13"])
base = vtext(pd)
vf = (pd.root / VIEW_F)


def crafted(fn):
    vf.write_text(fn(base), encoding="utf-8")
    try:
        return [c for c, _ in vd.integrity(vtext(pd))]
    finally:
        vf.write_text(base, encoding="utf-8")


kn_block = blocks(base)["KN:KN-0000000b"]
check("K V-01 index -> missing section", "V-01" in crafted(lambda t: t.replace(kn_block + "\n\n", "")), True)
check("K V-02 duplicate concept section", "V-02" in crafted(lambda t: t.replace(kn_block, kn_block + "\n\n" + kn_block)), True)
check("K V-03 broken marker pairing", "V-03" in crafted(lambda t: t.replace("<!-- SITL:KN:KN-0000000b:END -->\n", "")), True)
check("K V-03 unknown SITL marker", "V-03" in crafted(lambda t: t.replace("## Learning\n", "## Learning\n<!-- SITL:XX:START -->\n")), True)
check("K V-04 concept ID mismatch", "V-04" in crafted(lambda t: t.replace("### KN-0000000b — ", "### KN-0000000c — ")), True)
check("K V-05 header project mismatch", "V-05" in crafted(lambda t: t.replace(f"project_id={PRJ}", "project_id=PRJ-00000000")), True)
other = "HS-deadbeef"
check("K V-05 HS section from another project", "V-05" in crafted(lambda t: t.replace(hs(1)[3:], other)), True)
check("K V-07 stale record version", "V-07" in crafted(lambda t: t.replace(f"SITL:{hs(1)}:START v=1", f"SITL:{hs(1)}:START v=7")), True)
check("K V-06 STALE shown as Current", "V-06" in crafted(lambda t: t.replace(f"{blocks(t)[hs(1)].splitlines()[4]}",
                                                                              blocks(t)[hs(1)].splitlines()[4].replace("Current", "Needs refresh"))), True)
check("K V-09 unclosed fence", "V-09" in crafted(lambda t: t.replace("#### L1 — Simple Mental Model\n", "#### L1 — Simple Mental Model\n```text\n")), True)
check("K V-10 level-2 heading inside a section", "V-10" in crafted(lambda t: t.replace("#### L1 — Simple Mental Model", "## L1 — Simple Mental Model")), True)
check("K V-11 L4 heading on a Light (L1;L2) concept", [c for c, _ in ve.integrity(vtext(pe).replace("#### L2 — Mechanism", "#### L4 — Formalism"))],
      ["V-11"])
check("K V-14 map node not in graph", "V-14" in crafted(lambda t: t.replace("KN_0000000b[", "KN_0000beef[")), True)
check("K clean view -> no finding", vd.integrity(base), [])
# misleading presentation is repaired section by section
st_text = (pd.root / sm.STATE_F).read_text(encoding="utf-8")
(pd.root / sm.STATE_F).write_text(st_text.replace("| SYNCED |", "| STALE |", 1), encoding="utf-8")
found = vd.integrity(vtext(pd))
check("K state STALE, view Current -> V-06 WARNING", found, [("V-06", "WARNING")])
pre = blocks(vtext(pd))
res = vd.repair()
post = blocks(vtext(pd))
check("K repair rewrites only that HS section (+ index)", (res[1], sorted(k for k in post if pre[k] != post[k])), ("REPAIRED", [hs(1), "INDEX"]))
check("K after repair: clean", vd.integrity(vtext(pd)), [])
(pd.root / sm.STATE_F).write_text(st_text, encoding="utf-8")
vd.repair()
# structural FAIL blocks writes; file unchanged
good = vtext(pd)
vf.write_text(good.replace("<!-- SITL:MAP:END -->\n", ""), encoding="utf-8")
bad = vtext(pd)
try:
    vd.update(["INDEX", "MAP"])
    blocked = None
except ViewBlocked as e:
    blocked = str(e)
check("K corrupt view -> update BLOCKED, no write", (blocked, vtext(pd) == bad), ("V-03", True))
check("K corrupt view -> repair refuses (FAIL)", vd.repair()[1], "FAIL")
vf.write_text(good, encoding="utf-8")
# candidate FAIL: a record with an unclosed fence never reaches the view; authoritative sync stays
pk = project("pk", steps=2)
vk = View(P, pk.root)
sync(pk, vk)
k_before = vtext(pk)
pk.step(3, ["src/s3.py"])
try:
    sync(pk, vk, judge={("hs", wu(3)): {"How It Works": "```text\nA → B"}})
    cand = None
except ViewBlocked as e:
    cand = str(e)
check("K candidate V-09 -> view write refused", (cand, vtext(pk) == k_before), ("V-09", True))
check("K authoritative sync not undone by view failure", {r["work_unit_id"]: r["sync_status"] for r in state_rows(pk.root)}[wu(3)], "SYNCED")
# write failure mid-way restores the pre-image (no half section, no lone marker)
pk.write(f"{sm.SYNC}/records/{sm.record_id(wu(3))}.md", (pk.root / f"{sm.SYNC}/records/{sm.record_id(wu(3))}.md").read_text(encoding="utf-8").replace("```text\nA → B", "A → B"))
try:
    vk.update([hs(3), "MODEL", "INDEX"], fail_on="INDEX")
    wf = None
except ViewBlocked as e:
    wf = str(e)
check("K injected write error -> pre-image restored", (wf, vtext(pk) == k_before, vk.integrity(vtext(pk), structural_only=True)), ("write error", True, []))
vk.update([hs(3), "MODEL", "INDEX"])
check("K retry after failure -> consistent", (vk.integrity(vtext(pk)), vtext(pk) == vk.rebuild()), ([], True))
# foreign file is never overwritten
pf = project("pf")
(pf.root / VIEW_F).parent.mkdir(parents=True, exist_ok=True)
(pf.root / VIEW_F).write_text("# My own notes\n", encoding="utf-8")
vfo = View(P, pf.root)
try:
    sync(pf, vfo)
    fo = None
except ViewBlocked as e:
    fo = str(e)
check("K foreign STAY_IN_THE_LOOP.md -> V-12, not overwritten", (fo, (pf.root / VIEW_F).read_text(encoding="utf-8")), ("V-12", "# My own notes\n"))

# Test L - migration of an existing project (spec 31)
pl = project("pl")
sm.Sync(SP, pl.root).run("")
light(pl, LIGHT_A, "Temporal Leakage", L_LIGHT)
full(pl, FULL_A, L_FULL)
mig_nodes = learning_graph(pl, extra=[node("KN-0000000c", "Walk-Forward Validation", "CONCEPT", "KN-0000000a", "L1; L2; L3; L4", arts=FULL_A)])
write_graph(pl, 3, mig_nodes, [edge("KE-0001", "KN-0000000b", "NEXT", "KN-0000000c")])
learn = pl.root / "docs/learning"
snap = {f.relative_to(learn).as_posix(): sha(f.read_bytes()) for f in learn.rglob("*") if f.is_file()}
check("L existing content, no view -> V-08 WARNING", vl_f := View(P, pl.root).integrity(None), [("V-08", "WARNING")])
vl = View(P, pl.root)
check("L derived repair builds the view", vl.repair()[1], "REBUILT")
after = {f.relative_to(learn).as_posix(): sha(f.read_bytes()) for f in learn.rglob("*") if f.is_file()}
check("L authoritative files untouched (no move / delete)", {k: v for k, v in after.items() if k != "STAY_IN_THE_LOOP.md"}, snap)
check("L migrated view: HS + both concepts + provenance path", (len([k for k in blocks(vtext(pl)) if k.startswith("HS:")]),
                                                                  sorted(k for k in blocks(vtext(pl)) if k.startswith("KN:")),
                                                                  f"(`{FULL_A}`)" in blocks(vtext(pl))["KN:KN-0000000c"]),
      (3, ["KN:KN-0000000b", "KN:KN-0000000c"], True))
check("L migrated view clean", vl.integrity(vtext(pl)), [])

# Test M - one human-facing file for a multi-unit, multi-concept, multi-map project (spec 35)
check("M pilot-like projects: only STAY_IN_THE_LOOP.md is human-facing", [human_files(p.root) for p in (pb, pc, pd, pe, pg, pj, pl)],
      [["STAY_IN_THE_LOOP.md"]] * 7)
check("M no HTML anywhere under docs/learning", [f.name for p in (pb, pd, pg, pj, pl) for f in (p.root / "docs/learning").rglob("*.htm*")], [])
check("M no per-level files", [f.name for p in (pd, pg, pj, pl) for f in (p.root / "docs/learning").rglob("*") if re.search(r"L[0-4]\.md$", f.name)], [])

# Test N - README architecture visualization (spec 44)
readme = (DEV_REPO / "README.md").read_text(encoding="utf-8")
check("N README: How Stay in the Loop Works near the top", 0 < readme.find("## How Stay in the Loop Works") < readme.find("## Install") if "## Install" in readme
      else "## How Stay in the Loop Works" in readme, True)
rm = vm.mermaid_blocks(readme)
check("N README: >= 2 Mermaid diagrams, all closed", (len(rm) >= 2, readme.count("```mermaid") == len(rm)), (True, True))
check("N README: Mermaid static check", [vm.mermaid_errors(b) for b in rm], [[] for _ in rm])
arch = next((b for b in rm if "/stay-in-the-loop sync" in b), "")
check("N README: Human Sync vs Learning branches", [x in arch for x in ("Human Sync", "/stay-in-the-loop sync", "STOP", "Light / Full ULA",
                                                                     "Semantic Graph")], [True] * 5)
inc = next((b for b in rm if "Minimum Required Context" in b), "")
check("N README: incremental Human Sync diagram", [x in inc for x in ("Human Sync State", "Rolling Project Context", "Relevant Previous Sync",
                                                                    "Updated Sync State")], [True] * 4)
check("N README: incremental reuse explained", ("Previously synchronized work is reused." in readme,
                                               "Only new, stale, or dependency-affected work is processed by default." in readme), (True, True))
check("N README: mode table", [bool(re.search(p, readme, re.M)) for p in (r"^\| Mode \| Purpose \| Human Sync \| ULA \| Learning Coverage \|$",
                                                                       r"^\| `/stay-in-the-loop sync` \| .* \| Unchanged \|$",
                                                                       r"^\| `/stay-in-the-loop` \| .* \| Normal workflow \|$")], [True] * 3)
check("N README: single knowledge file + internal state explained", ("docs/learning/STAY_IN_THE_LOOP.md" in readme,
      all(w in readme for w in ("incremental sync", "checkpoints", "integrity", "coverage", "resume"))), (True, True))

# Test O - protocol vocabulary
check("O authority rules", {k: P.rules[k] for k in ("authority", "read_mode", "write_mode", "on_write_error", "failure_effect")},
      {"authority": "DERIVED", "read_mode": "MARKERS_THEN_SECTION", "write_mode": "SECTION_PATCH", "on_write_error": "RESTORE_PRE_IMAGE",
       "failure_effect": "WARNING"})
check("O structure order", P.order, ["VIEW", "INDEX", "MODEL", "HS", "KN", "MAP", "DEBT"])
check("O status lines", P.status_line, {"SYNCED": "Current", "STALE": "Needs refresh"})
check("O HS template parts = 09 §5 mapping", P.hs_sections, [v for v, _ in P.hs_map])
check("O Light has no L4 source", P.artifact_map["L4 — Formalism"]["LIGHT"], None)
check("O collapsed parts", P.collapsed, ["L3", "L4", "Reference"])
s07 = (SKILL / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8")
check("O 07 §L.1 KNOWLEDGE_VIEW is DERIVED", bool(re.search(r"^\| `KNOWLEDGE_VIEW` \| DERIVED \|", s07, re.M)), True)
check("O 07 §L.3 runs §V", "+ §V + §L checks" in s07, True)
check("O view template has no per-level or HTML file target", re.findall(r"(?:L[0-4]\.md|\.html\b)", (SKILL / "templates" / "KNOWLEDGE_VIEW_TEMPLATE.md").read_text(encoding="utf-8")), [])

report(RESULTS)
