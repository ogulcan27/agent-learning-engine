"""Standalone incremental Human Sync suite (08_HUMAN_SYNC_STATE, 07 §S).

Usage: run_tests.py [<skill_dir>]
One temporary git project grows step by step. Its docs/learning/ is created by the full-pipeline
lifecycle model, so coverage, queue, graph and library are real and can be compared byte by byte.
"""
import atexit
import hashlib
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402

use("phase3", "phase4", "phase5", "phase6", "phase7", "integration", "sync")
import graph_model as gm  # noqa: E402
import sync_model as sm  # noqa: E402
from files import GRAPH, QUEUE, parse_ledger, queue_a_rows, render_queue  # noqa: E402
from lifecycle import QA_COLS, Env, Project  # noqa: E402
from sync_model import CONTEXT_F, STATE_F, Blocked, Reader, Repo, wu  # noqa: E402

SKILL = skill_dir()
ENV = Env(SKILL)
P = sm.Protocol(SKILL)
TMP = Path(tempfile.mkdtemp(prefix="sync_"))
atexit.register(shutil.rmtree, TMP, True)
RESULTS = []
V = "VERIFIED (commit:9f3a1c2b7d4e; test:tests/test_worker.py)"
LIGHT = {"L0 — Local Map": "Request → Queue → Worker", "L1 — Simple Explanation": "Queue işleri sıraya koyar.",
         "L2 — Mechanism": "Producer yazar. Consumer alır.", "Retrieval": "Queue neden request süresini kısaltır?"}


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def digest(root, skip=("sync",)):
    """Hashes of every file under root, except the sync layer."""
    return {f.relative_to(root).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(root.rglob("*"))
            if f.is_file() and not set(skip) & set(f.relative_to(root).parts)} if root.exists() else {}


def rows():
    return {r["work_unit_id"]: r for r in sm.parse_state(P, (REPO.root / STATE_F).read_text(encoding="utf-8"))[1]}


def record(n):
    return (REPO.root / f"{sm.SYNC}/records/{sm.record_id(wu(n))}.md").read_bytes()


def raw(log):
    return sorted({u.split("|")[0] for k, u in log if k == "RAW"})


def recs(log):
    return sorted(u for k, u in log if k == "RECORD")


def ledger():
    return {r["work_unit_id"]: r["status"] for r in parse_ledger(ENV.P3_cols, (LEARN / "state/COVERAGE_LEDGER.md").read_text(encoding="utf-8")).rows}


def change(n, topic):
    return {"wu": wu(n), "kind": "design change", "topic": topic, "q1": True, "q2": True, "evidence": V,
            "sd_signals": ["flow", "performance"], "mechanism": topic, "signal": f"{topic} reusable signal",
            "must_signals": ["system behaviour"], "gap_signals": ["concept first appearance"]}


# Project: git repo + full-pipeline docs/learning (ledger, queue with one OPEN debt, graph, library)
REPO = Repo(TMP / "proj")
for n in (1, 2, 3):
    REPO.step(n, [f"src/s{n}.py"])
LEARN = REPO.root / "docs/learning"
LIB = TMP / "library"
LP = Project(ENV, TMP / "lc", "PRJ-5e1f0a2b", "Proj", library=LIB)
LP.store.roots["P"] = LEARN
LP.set_config(work_unit_source="phase-doc")
LP.store.write(GRAPH, gm.Graph(0).render(ENV.P6))
LP.discover([1, 2, 3])
DEBT = {c: "-" for c in ENV.P7.debt_cols}
DEBT.update(debt_id="KD-LP-20261020-01-01", concept="Backpressure", debt_status="OPEN", priority="LATER")
LP.store.write(QUEUE, render_queue(QA_COLS, queue_a_rows(LP.ledger), ENV.P7.debt_cols, [DEBT]))
for d in ("concepts", "experiences"):
    (LEARN / d).mkdir(exist_ok=True)
    (LEARN / d / "keep.md").write_text(f"{d}\n", encoding="utf-8")
LIB.mkdir(exist_ok=True)
(LIB / "LIBRARY_INDEX.md").write_text("# Library\n", encoding="utf-8")
S = sm.Sync(P, REPO.root)
LOGS = {}

# Extra - rule presence
check("R statuses UNSYNCED / SYNCED / STALE only", P.statuses, ["UNSYNCED", "SYNCED", "STALE"])
check("R authority: state + records AUTHORITATIVE, context DERIVED rebuildable", P.authority,
      {"HUMAN_SYNC_STATE.md": ("AUTHORITATIVE", "NO"), "records/HS-*.md": ("AUTHORITATIVE", "NO"), "PROJECT_SYNC_CONTEXT.md": ("DERIVED", "YES")})
check("R sync-only never writes coverage / queue / pass / graph / concept / experience / library",
      [k for k in ("COVERAGE_LEDGER.md", "LEARNING_STATE.md", "LEARNING_QUEUE.md", "passes/", "maps/", "concepts/", "experiences/",
                   "Personal Technical Library") if P.sync_only.get(k) != "NO"], [])
check("R write ALL_OR_NOTHING, integrity first, restore, state is commit point", P.write_rules,
      {"write_mode": "ALL_OR_NOTHING", "integrity": "BEFORE_ANY_WRITE", "on_write_error": "RESTORE_PRE_IMAGES", "commit_point": "HUMAN_SYNC_STATE"})
check("R STALE refresh never reads full raw evidence", "RAW_EVIDENCE" in P.plan["STALE"][1] and "RAW_EVIDENCE" not in P.plan["STALE"][0], True)
check("R SYNCED unit: nothing read", P.plan["SYNCED"][0], [])
check("R record carries 03 §5 fields + sync fields",
      [s for s in ("Purpose", "Why It Changed", "How It Works", "Key Decisions", "What Changed", "Dependencies", "Downstream Impact",
                   "Open / Uncertain Points", "Evidence / Provenance") if s not in P.record_sections], [])
check("R 07 §S: 16 checks, S-12..S-14 WARNING", (len(P.checks), [c for c, s in P.checks.items() if s == "WARNING"]),
      (16, ["S-12", "S-13", "S-14"]))
check("R existing state is read by exact path; listings are no evidence of absence",
      "Directory listing, kısaltılmış (truncated) çıktı veya hafıza yokluk kanıtı değildir." in
      (SKILL / "references/08_HUMAN_SYNC_STATE.md").read_text(encoding="utf-8"), True)
s08 = (SKILL / "references/08_HUMAN_SYNC_STATE.md").read_text(encoding="utf-8")
check("R semantic boundary invariants", all(x in s08 for x in ("Human Sync complete ≠ concept learned", "Human Sync complete ≠ ULA complete",
                                                              "Human Sync complete ≠ learning coverage complete")), True)
check("R sync-only STOP before events / ULA / debt / completion / map / persistence",
      bool(re.search(r"STOP sonrası Learning Event, Knowledge Priority, Knowledge Debt, ULA, Completion, map sync ve persistence çalışmaz", s08)), True)
check("R full mode with UNCONFIGURED project_id writes no record and asks nothing",
      "`project_id: UNCONFIGURED` ise full mode record yazmaz ve soru sormaz." in s08, True)
check("R 03 remains the single Human Sync content source",
      "§4–§7 Human Synchronization içeriği için tek kaynaktır." in (SKILL / "references/03_HUMAN_SYNC_PROTOCOL.md").read_text(encoding="utf-8"), True)

# Test A - routing
skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
ARGS = [re.match(r"`([a-z-]+)", r[0]).group(1) for r in sm.tables(sm.section(skill_md, "## 6. Arguments"))[0] if re.match(r"`[a-z-]+", r[0])]
SYNC_ROUTE = "`sync ...` argümanları run loop'u çalıştırmaz. Doğrudan `references/08_HUMAN_SYNC_STATE.md` §11'e gider." in skill_md


def route(argstr):
    """SKILL.md §6/§7: the first token selects the mode; anything else is a full-mode scope."""
    tok, _, rest = argstr.strip().partition(" ")
    if tok == "sync" and "sync" in ARGS and SYNC_ROUTE:
        return ("SYNC", rest)
    if tok in ("map", "concept", "library", "experiences", "debt", "integrity") and tok in ARGS:
        return (tok.upper(), rest)
    return ("FULL", argstr.strip())


check("A /stay-in-the-loop -> FULL", route(""), ("FULL", ""))
check("A sync -> SYNC (incremental default)", route("sync"), ("SYNC", ""))
check("A sync latest / pending / catch-up -> SYNC", [route(f"sync {a}") for a in ("latest", "pending", "catch-up")],
      [("SYNC", "latest"), ("SYNC", "pending"), ("SYNC", "catch-up")])
check("A sync <work-unit-id> -> SYNC MATCH", route(f"sync {wu(2)}"), ("SYNC", wu(2)))
check("A latest / pending / catch-up stay FULL", [route(a)[0] for a in ("latest", "pending", "catch-up", wu(2))], ["FULL"] * 4)
check("A map sync stays MAP", route("map sync"), ("MAP", "sync"))
check("A every sync scope form is defined in 08 §7", sorted(P.scope), sorted(["", "latest", "pending", "catch-up", "<work-unit-id>"]))
check("A manual-only frontmatter unchanged", ("disable-model-invocation: true" in skill_md, "user-invocable: true" in skill_md), (True, True))

# Test B - first catch-up: Step 1-3, no Human Sync history
before = digest(LEARN), digest(LIB)
rd = Reader()
res = S.run("", reader=rd)
LOGS["B"] = rd.log
st = rows()
check("B Step 1-3 synced", res["synced"], [wu(1), wu(2), wu(3)])
check("B Step 1-3 SYNCED in state", [st[wu(n)]["sync_status"] for n in (1, 2, 3)], ["SYNCED"] * 3)
check("B three records + state + context exist", (len(list((REPO.root / sm.SYNC / "records").glob("HS-*.md"))),
                                                  (REPO.root / STATE_F).exists(), (REPO.root / CONTEXT_F).exists()), (3, True, True))
check("B context built from the three records", sm.kv((REPO.root / CONTEXT_F).read_text(encoding="utf-8"))["source_records"].count("@1"), 3)
check("B footer: ULA NOT RUN, coverage UNCHANGED", (res["ula"], res["coverage"]), ("NOT RUN", "UNCHANGED"))
check("B learning coverage still UNCOVERED", set(ledger().values()), {"UNCOVERED"})
check("B ledger / state / queue / graph / concepts / experiences byte-identical", digest(LEARN), before[0])
check("B Knowledge Debt unchanged (OPEN debt kept, none added)", (LEARN / "state/LEARNING_QUEUE.md").read_text(encoding="utf-8").count("KD-"), 1)
check("B personal library unchanged", digest(LIB), before[1])
check("B no Learning Pass opened", list((LEARN / "passes").glob("*")) if (LEARN / "passes").exists() else [], [])
check("B raw evidence read once per unit", raw(rd.log), [wu(1), wu(2), wu(3)])

# Test C - incremental second run: Step 4, Step 5 (depends on Step 2)
REPO.step(4, ["src/s4.py"])
REPO.step(5, ["src/s5.py"], depends=2)
old = {n: record(n) for n in (1, 2, 3)}
rd = Reader()
res = S.run("", reader=rd)
LOGS["C"] = rd.log
st = rows()
check("C Step 4-5 synced", res["synced"], [wu(4), wu(5)])
check("C Step 1-3 reused, not regenerated", ({n: record(n) for n in (1, 2, 3)} == old, res["reused"]), (True, 3))
check("C raw evidence read only for Step 4-5", raw(rd.log), [wu(4), wu(5)])
check("C rolling context read", ("CONTEXT", "-") in rd.log, True)

# Test D - dependency-based retrieval: Step 5 uses HS(Step 2), never Step 2 raw evidence
check("D Step 5 depends_on Step 2", st[wu(5)]["depends_on"], wu(2))
check("D only the Step 2 record is loaded", recs(rd.log), [wu(2)])
check("D Step 2 raw evidence not reread", wu(2) in raw(rd.log), False)

# Test E - up to date: nothing read
rd = Reader()
check("E no change -> UP_TO_DATE", S.run("", reader=rd)["result"], "UP_TO_DATE")
check("E nothing beyond discovery + context read", sorted({k for k, _ in rd.log}), ["CONTEXT", "DISCOVERY"])

# Test F - non-material changes
REPO.write("README.md", "# Proj\nTypo fixd\n")
REPO.commit("readme typo")
rd = Reader()
check("F unrelated README typo -> UP_TO_DATE, no delta read", (S.run("", reader=rd)["result"], [k for k, _ in rd.log if k == "DELTA"]),
      ("UP_TO_DATE", []))
old, cp3 = {n: record(n) for n in range(1, 6)}, rows()[wu(3)]["checkpoint"]
REPO.write("src/s3.py", (REPO.root / "src/s3.py").read_text(encoding="utf-8") + "# typo in comment\n")
REPO.commit("comment typo in step 3 file")
rd = Reader()
S.run("", judge={("material", wu(3)): "TYPO"}, reader=rd)
st = rows()
check("F in-path TYPO: Step 3 stays SYNCED, checkpoint advances", (st[wu(3)]["sync_status"], st[wu(3)]["checkpoint"] != cp3), ("SYNCED", True))
check("F in-path TYPO: no record rewritten", {n: record(n) for n in range(1, 6)} == old, True)
check("F delta read only for Step 3", [u for k, u in rd.log if k == "DELTA"], [wu(3)])

# Test G - stale detection: SYNCED -> STALE -> refreshed -> SYNCED; unrelated units untouched
REPO.write("src/s2.py", "# step 2\nbehaviour changed by hotfix\n")
REPO.commit("hotfix step 2 behaviour")
old = {n: record(n) for n in (1, 3, 4, 5)}
res = S.run("latest", judge={("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(5)): "NONE"})
st = rows()
check("G material change -> Step 2 STALE (persisted)", (st[wu(2)]["sync_status"], res["stale"]), ("STALE", [wu(2)]))
check("G other units stay SYNCED", [st[wu(n)]["sync_status"] for n in (1, 3, 4, 5)], ["SYNCED"] * 4)
check("G STALE excluded from rolling context", sm.record_id(wu(2)) in sm.kv((REPO.root / CONTEXT_F).read_text(encoding="utf-8"))["source_records"], False)
rd = Reader()
res = S.run("pending", reader=rd)
st = rows()
check("G pending refreshes Step 2 -> SYNCED v2", (res["refreshed"], st[wu(2)]["sync_status"], st[wu(2)]["record_version"]), ([wu(2)], "SYNCED", "2"))
check("G refresh = own record + delta, no raw evidence", (recs(rd.log), ("DELTA", wu(2)) in rd.log, raw(rd.log)), ([wu(2)], True, []))
check("G unrelated records byte-identical", {n: record(n) for n in (1, 3, 4, 5)} == old, True)

# Test G2 - default sync refreshes an independent STALE unit (no new work, no dependency pull)
REPO.write("src/s4.py", "# step 4\nflow changed\n")
REPO.commit("step 4 flow change")
old = {n: record(n) for n in (1, 2, 3, 5)}
rd = Reader()
res = S.run("", judge={("material", wu(4)): "FLOW"}, reader=rd)
check("G2 default sync refreshes STALE Step 4", (res["synced"], res["refreshed"], rows()[wu(4)]["sync_status"]), ([], [wu(4)], "SYNCED"))
check("G2 refresh without raw evidence, others untouched", (raw(rd.log), {n: record(n) for n in (1, 2, 3, 5)} == old), ([], True))

# Test H - later step changes an earlier step's architecture (path overlap)
REPO.write("src/s2.py", "# step 2\narchitecture replaced by step 6\n")
REPO.step(6, ["src/s2.py", "src/s6.py"])
old = {n: record(n) for n in (1, 3, 4, 5)}
rd = Reader()
res = S.run("", judge={("material", wu(2)): "INTERFACE", ("impact", wu(2), wu(5)): "NONE"}, reader=rd)
st = rows()
check("H Step 2 refreshed, Step 6 synced", (res["refreshed"], res["synced"]), ([wu(2)], [wu(6)]))
check("H Step 6 depends_on Step 2 (path overlap)", st[wu(6)]["depends_on"], wu(2))
check("H Step 2 v3 from record + delta, not raw", (st[wu(2)]["record_version"], wu(2) in raw(rd.log)), ("3", False))
check("H unrelated records byte-identical", {n: record(n) for n in (1, 3, 4, 5)} == old, True)

# Test I - full workflow reuses a valid record; learning pipeline unchanged
rec1 = record(1)
rd = Reader()
check("I full mode: SYNCED Step 1 -> OWN_RECORD", S.full_sources([wu(1)], reader=rd), {wu(1): ["OWN_RECORD"]})
check("I full mode: no raw evidence for Step 1", raw(rd.log), [])
LP.scope([wu(1)])
events = LP.human_sync("LP-20261027-01", [wu(1)], [change(1, "Queue")])
check("I Learning Event pipeline still runs", len(events) > 0, True)
LP.light("LP-20261027-01", LP.event_id("LP-20261027-01", "Queue"), LIGHT)
check("I ULA reachable, pass completes", LP.complete("LP-20261027-01"), "COMPLETE")
check("I normal coverage transition: Step 1 COVERED", ledger()[wu(1)], "COVERED")
check("I Human Sync record not regenerated, still SYNCED", (record(1) == rec1, rows()[wu(1)]["sync_status"]), (True, "SYNCED"))
REPO.step(7, ["src/s7.py"])
LP.discover([7])
rd = Reader()
check("I full mode: UNSYNCED Step 7 -> RAW_EVIDENCE", S.full_sources([wu(7)], reader=rd), {wu(7): ["RAW_EVIDENCE"]})
S.run(wu(7))
rec7 = record(7)
rd = Reader()
S.run("", reader=rd)
check("I record written by full mode is reused by sync", (record(7) == rec7, raw(rd.log)), (True, []))
check("I full mode STALE -> refresh first (record + delta)", P.reuse[2][1], ["OWN_RECORD", "DELTA"])
check("I sync after full mode leaves coverage as full mode set it", ledger()[wu(1)], "COVERED")

# Test J - corruption fails safely, nothing written, nothing borrowed
SYNC_DIR = REPO.root / sm.SYNC
SNAP = TMP / "snap"
shutil.copytree(SYNC_DIR, SNAP)


def corrupt(edit):
    """Apply edit to a fresh copy of the sync layer, run sync, return (blocked codes, files unchanged)."""
    shutil.rmtree(SYNC_DIR)
    shutil.copytree(SNAP, SYNC_DIR)
    edit()
    pre = digest(SYNC_DIR, ())
    try:
        S.run("")
        code = "NOT BLOCKED"
    except Blocked as e:
        code = str(e)
    return code, digest(SYNC_DIR, ()) == pre


def sub(rel, old, new):
    f = SYNC_DIR / rel
    t = f.read_text(encoding="utf-8")
    assert old in t, (rel, old)
    f.write_bytes(t.replace(old, new, 1).encode("utf-8"))


R1, STATE = f"records/{sm.record_id(wu(1))}.md", "HUMAN_SYNC_STATE.md"
row1 = next(l for l in (SYNC_DIR / STATE).read_text(encoding="utf-8").splitlines() if l.startswith(f"| {wu(1)} "))
check("J SYNCED unit with missing record -> S-01, no write", corrupt(lambda: (SYNC_DIR / R1).unlink()), ("S-01", True))
check("J state checkpoint missing -> S-02", corrupt(lambda: sub(STATE, row1, re.sub(r"\| (git|fp):\w+ \|", "| - |", row1))), ("S-02", True))
check("J record checkpoint missing -> S-02",
      corrupt(lambda: sub(R1, re.search(r"checkpoint: .*\n", (SYNC_DIR / R1).read_text(encoding="utf-8")).group(0), "")), ("S-02", True))
check("J state points to nonexistent record -> S-01", corrupt(lambda: sub(STATE, row1, row1.replace(sm.record_id(wu(1)), "HS-deadbeef"))),
      ("S-01", True))
check("J STALE unit pointing to missing record -> S-01",
      corrupt(lambda: (sub(STATE, row1, row1.replace("| SYNCED |", "| STALE |")), (SYNC_DIR / R1).unlink())), ("S-01", True))
check("J record of another project -> S-04", corrupt(lambda: sub(R1, "project_id: PRJ-5e1f0a2b", "project_id: PRJ-0ther000")), ("S-04", True))
check("J state of another project -> S-05", corrupt(lambda: sub(STATE, "project_id: PRJ-5e1f0a2b", "project_id: PRJ-0ther000")), ("S-05", True))
check("J rolling context of another project -> S-11", corrupt(lambda: sub("PROJECT_SYNC_CONTEXT.md", "project_id: PRJ-5e1f0a2b",
                                                                         "project_id: PRJ-0ther000")), ("S-11", True))
check("J record version mismatch -> S-06", corrupt(lambda: sub(R1, "record_version: 1", "record_version: 9")), ("S-06", True))
check("J evidence path outside project -> S-09", corrupt(lambda: sub(STATE, row1, row1.replace("| src/s1.py |", "| ../other/s1.py |"))),
      ("S-09", True))
code, _ = corrupt(lambda: sub("PROJECT_SYNC_CONTEXT.md", "source_records: ", "source_records: HS-00000000@1; "))
check("J stale context source list -> WARNING only, rebuilt from own records", (code, "HS-00000000" in (SYNC_DIR / "PROJECT_SYNC_CONTEXT.md").read_text(encoding="utf-8")),
      ("NOT BLOCKED", False))
shutil.rmtree(SYNC_DIR)
shutil.copytree(SNAP, SYNC_DIR)
REPO.step(8, ["src/s8.py"])
pre = digest(SYNC_DIR, ())
try:
    S.run("", fail_on=STATE_F)
    code = "NOT BLOCKED"
except Blocked as e:
    code = str(e)
check("J write error at state -> restored, Step 8 not SYNCED, no orphan record",
      (code, digest(SYNC_DIR, ()) == pre, wu(8) in rows()), ("write error", True, False))
S.run("")
check("J after recovery Step 8 SYNCED", rows()[wu(8)]["sync_status"], "SYNCED")
pre = digest(SYNC_DIR, ())
try:
    S.run("", skip_state=True)
    code = "NOT BLOCKED"
except Blocked as e:
    code = str(e)
check("J run that skipped the existing state cannot regenerate records as v1 -> S-16, no write",
      (code, digest(SYNC_DIR, ()) == pre), ("S-16", True))

# Test K - initialization and project identity reuse the existing rules
fresh = Repo(TMP / "fresh")
fresh.step(1, ["src/a.py"])
FS = sm.Sync(P, fresh.root)
try:
    FS.run("")
    code = "NOT BLOCKED"
except Blocked as e:
    code = str(e)
check("K no docs/learning -> first-run initialization required (02 §11), nothing written", (code, (fresh.root / "docs").exists()),
      ("INIT_REQUIRED", False))
(fresh.root / "docs/learning/state").mkdir(parents=True)
for name in ("LEARNING_CONFIG", "LEARNING_STATE", "COVERAGE_LEDGER", "LEARNING_QUEUE"):
    (fresh.root / f"docs/learning/state/{name}.md").write_bytes((SKILL / f"templates/{name}_TEMPLATE.md").read_bytes())
try:
    FS.run("")
    code = "NOT BLOCKED"
except Blocked as e:
    code = str(e)
check("K project_id UNCONFIGURED without approval -> BLOCKED, no sync dir", (code, (fresh.root / sm.SYNC).exists()), ("PROJECT_ID", False))
FS.run("", approve_id=True)
prj = sm.KV.findall((fresh.root / sm.CONFIG_F).read_text(encoding="utf-8"))
prj = dict(prj)["project_id"]
check("K approved project_id written, record belongs to it",
      (bool(re.match(r"PRJ-[0-9a-f]{8}$", prj)), sm.kv((fresh.root / f"{sm.SYNC}/records/{sm.record_id(wu(1))}.md").read_text(encoding="utf-8"))["project_id"] == prj),
      (True, True))

# Test M - dependency freshness (08 §6.1): direct edge Step 5 -> Step 2, Step 6 is an independent head
def dep_repo(name, edges):
    """Steps 1-6 with explicit depends_on edges; fully synced once."""
    r = Repo(TMP / name)
    for n in range(1, 7):
        r.step(n, [f"src/s{n}.py"], depends=edges.get(n))
    (r.root / sm.CONFIG_F).parent.mkdir(parents=True)
    (r.root / sm.CONFIG_F).write_text("project_id: PRJ-0dep0000\n", encoding="utf-8")
    s = sm.Sync(P, r.root)
    s.run("")
    return r, s


def touch(r, n, line):
    r.write(f"src/s{n}.py", (r.root / f"src/s{n}.py").read_text(encoding="utf-8") + line + "\n")
    r.commit(f"change step {n}")


def st_of(s):
    return {r["work_unit_id"]: r["sync_status"] for r in sm.parse_state(P, (s.root / STATE_F).read_text(encoding="utf-8"))[1]}


def recs_of(r):
    return {f.name: f.read_bytes() for f in (r.root / sm.SYNC / "records").glob("*.md")}


DR, DS = dep_repo("dep_direct", {5: 2})
touch(DR, 2, "# typo fix in comment")
rd = Reader()
before = recs_of(DR)
DS.run("latest", judge={("material", wu(2)): "TYPO"}, reader=rd)
check("M non-material upstream change: Step 2 and Step 5 stay SYNCED", (st_of(DS)[wu(2)], st_of(DS)[wu(5)]), ("SYNCED", "SYNCED"))
check("M non-material upstream change: dependent not even evaluated, records unchanged", (recs(rd.log), recs_of(DR) == before), ([], True))

touch(DR, 3, "behaviour = 'changed'")
rd = Reader()
DS.run("latest", judge={("material", wu(3)): "BEHAVIOUR"}, reader=rd)
check("M unrelated unit: Step 3 STALE, Step 5 (no edge to 3) stays SYNCED", (st_of(DS)[wu(3)], st_of(DS)[wu(5)]), ("STALE", "SYNCED"))
check("M unrelated unit: no later unit evaluated without an edge", recs(rd.log), [])
DS.run("pending")

touch(DR, 2, "behaviour = 'internal refactor'")
rd = Reader()
DS.run("latest", judge={("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(5)): "NONE"}, reader=rd)
check("M material upstream, dependent does not rely on it: Step 2 STALE, Step 5 SYNCED", (st_of(DS)[wu(2)], st_of(DS)[wu(5)]),
      ("STALE", "SYNCED"))
check("M dependent assessed from its record only", (recs(rd.log), raw(rd.log)), ([wu(5)], []))
DS.run("pending")

touch(DR, 2, "def build(path, strict): ...  # contract changed")
rd = Reader()
before = recs_of(DR)
DS.run("latest", judge={("material", wu(2)): "INTERFACE", ("impact", wu(2), wu(5)): "CONTRACT"}, reader=rd)
st = st_of(DS)
check("M direct material dependency: Step 2 and Step 5 STALE", (st[wu(2)], st[wu(5)]), ("STALE", "STALE"))
check("M only the dependent's record read, no raw evidence", (recs(rd.log), raw(rd.log)), ([wu(5)], []))
check("M other units stay SYNCED", [st[wu(n)] for n in (1, 3, 4, 6)], ["SYNCED"] * 4)
ctx = (DR.root / CONTEXT_F).read_text(encoding="utf-8")
check("M context: STALE dependent not current, listed as stale",
      (sm.record_id(wu(5)) in sm.kv(ctx)["source_records"], "STALE: Step 5" in ctx), (False, True))
rd = Reader()
res = DS.run("", reader=rd)
check("M refresh: Step 2 refreshed (v3, second refresh in this repo), Step 5 first refresh v2", (res["refreshed"], [r["record_version"] for r in sm.parse_state(P, (DR.root / STATE_F)
      .read_text(encoding="utf-8"))[1] if r["work_unit_id"] in (wu(2), wu(5))]), ([wu(2), wu(5)], ["3", "2"]))
check("M refresh of dependent: own record + upstream record + delta, no raw", (wu(5) in raw(rd.log), recs(rd.log).count(wu(2)) >= 1),
      (False, True))
check("M unrelated records byte-identical", {k: v for k, v in recs_of(DR).items() if k not in (f"{sm.record_id(wu(2))}.md", f"{sm.record_id(wu(5))}.md")}
      == {k: v for k, v in before.items() if k not in (f"{sm.record_id(wu(2))}.md", f"{sm.record_id(wu(5))}.md")}, True)

# Test N - transitive dependency: Step 5 -> Step 4 -> Step 2, evaluated one boundary at a time
TR, TS = dep_repo("dep_transitive", {4: 2, 5: 4})
touch(TR, 2, "behaviour = 'v2'")
rd = Reader()
TS.run("latest", judge={("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(4)): "NONE"}, reader=rd)
check("N 2->4 not affected: Step 4 and Step 5 SYNCED, Step 5 not evaluated",
      (st_of(TS)[wu(4)], st_of(TS)[wu(5)], recs(rd.log)), ("SYNCED", "SYNCED", [wu(4)]))
TS.run("pending")
touch(TR, 2, "behaviour = 'v3'")
rd = Reader()
TS.run("latest", judge={("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(4)): "CONTRACT", ("impact", wu(4), wu(5)): "NONE"}, reader=rd)
check("N 2->4 affected, 4->5 not: Step 4 STALE, Step 5 SYNCED", (st_of(TS)[wu(4)], st_of(TS)[wu(5)], recs(rd.log)),
      ("STALE", "SYNCED", [wu(4), wu(5)]))
TS.run("pending")
touch(TR, 2, "behaviour = 'v4'")
rd = Reader()
TS.run("latest", judge={("material", wu(2)): "BEHAVIOUR", ("impact", wu(2), wu(4)): "CONTRACT",
                        ("impact", wu(4), wu(5)): "DATA_SEMANTICS"}, reader=rd)
st = st_of(TS)
check("N both boundaries affected: Step 4 and Step 5 STALE", (st[wu(4)], st[wu(5)]), ("STALE", "STALE"))
check("N later Step 3 / Step 6 without edges never evaluated, stay SYNCED", (st[wu(3)], st[wu(6)], raw(rd.log)), ("SYNCED", "SYNCED", []))
check("N rule table: explicit edges, records first, transitive only on material impact", P.dep_rules,
      {"edges": "EXPLICIT_DEPENDS_ON", "evidence": "RECORDS_FIRST", "transitive": "ON_MATERIAL_IMPACT"})
check("N uncertain impact -> STALE (no raw read to decide)", P.impact["UNKNOWN"], "STALE")

# Test L - token-efficiency audit over every recorded run
allowed = {"DISCOVERY", "CONTEXT", "RECORD", "RAW", "DELTA"}
check("L only planned read kinds", sorted({k for log in LOGS.values() for k, _ in log} - allowed), [])
check("L second run: raw only for new units, records only for dependencies", (raw(LOGS["C"]), recs(LOGS["C"])), ([wu(4), wu(5)], [wu(2)]))
check("L discovery is the only broad read (source index, no content)", [u for k, u in LOGS["C"] if k == "DISCOVERY"], ["PLAN.md"])
check("L rolling context bounded", len((REPO.root / CONTEXT_F).read_text(encoding="utf-8").splitlines()) <= P.ctx_lines, True)

report(RESULTS)
