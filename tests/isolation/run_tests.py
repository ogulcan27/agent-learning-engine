"""Cross-project isolation suite: a /stay-in-the-loop startup in Project B never selects Project A.

Usage: run_tests.py [<skill_dir>]
Root resolution is driven by the 01 §0 signal table. State files come from SKILL.md §9.
The library rule comes from 06 §2.3. Project A carries the sentinel V8_Clean_Validation (test data only).
"""
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir  # noqa: E402

SKILL = skill_dir()
RESULTS = []
SENTINEL = "V8_Clean_Validation"
PRIMARY = "Primary working directory (çağrı başı)"
ADDITIONAL = "Additional working directories"
SHELL_CWD = "Çağrı sırasında değişen shell cwd"
SKILL_BASE = "Skill base directory"
LIBRARY = "`personal_library_path`"


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def text(rel):
    return (SKILL / rel).read_text(encoding="utf-8")


def section(body, head):
    return body.split(head, 1)[1].split("\n## ", 1)[0] if head in body else ""


def root_sources():
    """01 §0 table: signal -> YES/NO."""
    body = section(text("references/01_OPERATIONAL_CORE.md"), "## 0. Active project root")
    return dict(re.findall(r"^\| (.+?) \| (YES|NO) \|$", body, re.M))


def state_files():
    """SKILL.md §9 tree: state file -> template."""
    return dict(re.findall(r"│   [├└]── (\w+\.md)\s+← (templates/\w+\.md)", section(text("SKILL.md"), "## 9.")))


def library_rule():
    """06 §2.3: result for a library path inside a docs/learning/ tree."""
    body = text("references/06_KNOWLEDGE_PERSISTENCE.md").split("### 2.3", 1)
    rows = re.findall(r"^\| .*`docs/learning/`.* \| (.+?) \|$", body[1].split("\n## ", 1)[0], re.M) if len(body) > 1 else []
    return rows[0] if rows else None


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def resolve_root(session):
    """Startup root resolution. session: signal -> path. Returns Path or 'BLOCKED'."""
    picks = {Path(session[s]).resolve() for s, v in root_sources().items() if v == "YES" and session.get(s)}
    picks = {p for p in picks if p.is_dir()}
    if len(picks) != 1:
        return "BLOCKED"
    start = picks.pop()
    top = git(start, "rev-parse", "--show-toplevel")
    return Path(top).resolve() if top else start


def startup(session):
    """Returns (root, status, missing state files)."""
    root = resolve_root(session)
    if root == "BLOCKED":
        return root, "BLOCKED", []
    lib = session.get(LIBRARY)
    if lib and "docs/learning" in Path(lib).as_posix() and library_rule() == "CONFIG ERROR":
        return root, "CONFIG ERROR", []
    missing = sorted(f for f in state_files() if not (root / "docs/learning/state" / f).exists())
    return root, ("FIRST_RUN" if missing else "LOAD"), missing


def initialize(root):
    """First run (user approved): create missing state files from templates; project_name = root folder name."""
    state = root / "docs/learning/state"
    state.mkdir(parents=True, exist_ok=True)
    for name, tpl in state_files().items():
        if not (state / name).exists():
            body = text(tpl).replace("project_name: UNCONFIGURED", f"project_name: {root.name}")
            (state / name).write_text(body, encoding="utf-8")
    for d in ("passes", "experiences", "concepts", "maps", "audits"):
        (root / "docs/learning" / d).mkdir(exist_ok=True)


def tree_hash(p):
    h = hashlib.sha256()
    for f in sorted(x for x in p.rglob("*") if x.is_file() and ".git" not in x.parts):
        h.update(f.relative_to(p).as_posix().encode() + f.read_bytes())
    return h.hexdigest()


def leaks(root):
    return [f.relative_to(root).as_posix() for f in (root / "docs/learning").rglob("*")
            if f.is_file() and SENTINEL in f.read_text(encoding="utf-8")] if (root / "docs/learning").exists() else []


def project_a(base):
    """Initialized project with recognizable identifiers, phase doc and a commit."""
    a = base / SENTINEL
    (a / "docs/learning/state").mkdir(parents=True)
    (a / "docs/learning/passes/LP-20261027-01").mkdir(parents=True)
    for name, tpl in state_files().items():
        (a / "docs/learning/state" / name).write_text(text(tpl).replace("UNCONFIGURED", SENTINEL), encoding="utf-8")
    (a / "docs/learning/passes/LP-20261027-01/LEARNING_PASS.md").write_text(f"pass_status: ACTIVE\nproject: {SENTINEL}\n", encoding="utf-8")
    (a / "V8_STAGE_GATES.md").write_text("# Stage gates\n1. Stage 01\n2. Stage 02\n", encoding="utf-8")
    (a / "outputs/stage_09_paper").mkdir(parents=True)
    git(a, "init", "-q")
    git(a, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    git(a, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", f"{SENTINEL} stage 18")
    return a


def project_b(base):
    """Fresh git repository: no commits, no docs/learning/."""
    b = base / "fresh-project"
    b.mkdir()
    git(b, "init", "-q")
    return b


BASE = Path(tempfile.mkdtemp(prefix="isolation_"))
A, B = project_a(BASE), project_b(BASE)
HOME_SKILL = BASE / "home/.claude/skills/stay-in-the-loop"
HOME_SKILL.mkdir(parents=True)
a_before = tree_hash(A)

# Extra - rule presence
src = root_sources()
check("R 01 §0 primary working directory is the only root source", [s for s, v in src.items() if v == "YES"], [PRIMARY])
check("R 01 §0 additional dirs / shell cwd / skill base / library are not root sources",
      [src.get(s) for s in (ADDITIONAL, SHELL_CWD, SKILL_BASE, LIBRARY)], ["NO"] * 4)
check("R SKILL.md §9 lists four state files", len(state_files()), 4)
check("R 06 §2.3 library inside docs/learning/ -> CONFIG ERROR", library_rule(), "CONFIG ERROR")

# Test A - incident: fresh B with A as additional working directory, personal-scope skill
incident = {PRIMARY: B, ADDITIONAL: A, SHELL_CWD: A, SKILL_BASE: HOME_SKILL}
root, status, missing = startup(incident)
check("A root is Project B", root, B.resolve())
check("A status FIRST_RUN", status, "FIRST_RUN")
check("A all four state files missing", len(missing), 4)
check("A Project A not selected", SENTINEL in str(root), False)
initialize(root)
check("A B state created under B/docs/learning", sorted(p.name for p in (B / "docs/learning/state").iterdir()), sorted(state_files()))
check("A B project_name = fresh-project", "project_name: fresh-project" in (B / "docs/learning/state/LEARNING_CONFIG.md").read_text(encoding="utf-8"), True)
check("A no V8_Clean_Validation in B state", leaks(B), [])
check("A no pass imported from A", list((B / "docs/learning/passes").iterdir()), [])
check("A Project A unchanged", tree_hash(A), a_before)

# Test B - second startup in B loads B state, never A
root, status, _ = startup(incident)
check("B second startup LOAD from B", (root, status), (B.resolve(), "LOAD"))
check("B loaded config is B", SENTINEL in (root / "docs/learning/state/LEARNING_CONFIG.md").read_text(encoding="utf-8"), False)

# Test C - launched from a subdirectory of B -> git top level of B
(B / "src/pkg").mkdir(parents=True)
check("C subdirectory resolves to B top level", startup({PRIMARY: B / "src/pkg", ADDITIONAL: A})[0], B.resolve())

# Test D - non-git fresh directory: root is the directory itself
plain = BASE / "plain-dir"
plain.mkdir()
check("D non-git directory -> itself, FIRST_RUN", startup({PRIMARY: plain, ADDITIONAL: A})[:2], (plain.resolve(), "FIRST_RUN"))

# Test E - primary working directory unknown -> BLOCKED, never another project
check("E no primary working directory -> BLOCKED", startup({ADDITIONAL: A, SKILL_BASE: HOME_SKILL})[1], "BLOCKED")
check("E missing primary working directory -> BLOCKED", startup({PRIMARY: BASE / "gone", ADDITIONAL: A})[1], "BLOCKED")

# Test F - personal library pointing into another project's docs/learning
check("F library = A/docs/learning -> CONFIG ERROR", startup({PRIMARY: B, LIBRARY: A / "docs/learning"})[1], "CONFIG ERROR")
lib = BASE / "library"
lib.mkdir()
(lib / "LIBRARY_INDEX.md").write_text(f"projects: {SENTINEL}\n", encoding="utf-8")
check("F library outside project does not change root", startup({PRIMARY: B, LIBRARY: lib})[:2], (B.resolve(), "LOAD"))

# Test G - discovery is bounded to the active project root
core = text("references/01_OPERATIONAL_CORE.md")
check("G 02 §3.4 discovery bounded to ACTIVE_PROJECT_ROOT", "<ACTIVE_PROJECT_ROOT>" in section(text("references/02_COVERAGE_PROTOCOL.md"), "### 3.4"), True)
check("G 02 §11 first run names the active root", "<ACTIVE_PROJECT_ROOT>" in section(text("references/02_COVERAGE_PROTOCOL.md"), "## 11."), True)
check("G 01 run loop step 1 resolves root first", bool(re.search(r"1\. STARTUP .*01 §0", core)), True)
check("G 01 stop rule: root unknown -> BLOCKED", bool(re.search(r"^\| Active project root belirlenemedi \| .*BLOCKED", core, re.M)), True)
check("G SKILL.md state layer uses <ACTIVE_PROJECT_ROOT>/docs/learning/", "`<ACTIVE_PROJECT_ROOT>/docs/learning/`" in text("SKILL.md"), True)

# Test H - standalone sync in B never uses A's Human Sync state (08 §3, 07 §S)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sync"))
import sync_model as sm  # noqa: E402

SP = sm.Protocol(SKILL)
(A / sm.SYNC / "records").mkdir(parents=True)
a_rec = sm.render_record(SP, {"record_id": sm.record_id(sm.wu(1)), "project_id": SENTINEL, "work_unit_id": sm.wu(1),
                              "record_version": 1, "checkpoint": "fp:0123456789abcdef", "updated_at": "2026-10-27"},
                         {"Purpose": f"{SENTINEL} regime model stage 18"})
(A / sm.SYNC / "records" / f"{sm.record_id(sm.wu(1))}.md").write_text(a_rec, encoding="utf-8")
(A / sm.STATE_F).write_text(sm.render_state(SP, SENTINEL, [{"work_unit_id": sm.wu(1), "seq": 1, "label": "Step 1", "sync_status": "SYNCED",
                                                           "record_id": sm.record_id(sm.wu(1)), "record_version": "1",
                                                           "checkpoint": "fp:0123456789abcdef", "evidence_paths": "src/a.py",
                                                           "depends_on": "-", "synced_at": "2026-10-27"}]), encoding="utf-8")
a_before = tree_hash(A)
(B / "PLAN.md").write_text("# Plan\n\n## Step 1 — Step 1\n\nPaths: src/b.py\n", encoding="utf-8")
(B / "src/b.py").write_text("print('b')\n", encoding="utf-8")
root = resolve_root(incident)
res = sm.Sync(SP, root).run("", approve_id=True)
b_sync = B / sm.SYNC
check("H sync runs in Project B", (root, res["synced"]), (B.resolve(), [sm.wu(1)]))
check("H B receives its own docs/learning/sync", (b_sync / "HUMAN_SYNC_STATE.md").exists(), True)
check("H no A identifier in B sync state", [f.name for f in b_sync.rglob("*.md") if SENTINEL in f.read_text(encoding="utf-8")], [])
check("H B record belongs to B project_id", sm.kv((b_sync / "records" / f"{sm.record_id(sm.wu(1))}.md").read_text(encoding="utf-8"))["project_id"]
      == dict(sm.KV.findall((B / sm.CONFIG_F).read_text(encoding="utf-8")))["project_id"], True)
check("H Project A (state + Human Sync) unchanged", tree_hash(A), a_before)
(b_sync / "records" / f"{sm.record_id(sm.wu(1))}.md").write_text(a_rec, encoding="utf-8")
try:
    sm.Sync(SP, root).run("")
    code = "NOT BLOCKED"
except sm.Blocked as e:
    code = str(e)
check("H A record copied into B -> S-04 BLOCKED, never used as B state", code, "S-04")

# Extra - cleanup
shutil.rmtree(BASE, ignore_errors=True)

report(RESULTS)
