"""Phase 9 distribution suite: manifest, release ZIP, installer, update, rollback, uninstall, remote bootstrap.

Usage: run_tests.py [<skill_dir>]
Needs Windows PowerShell 5.1+ (powershell.exe). Standard library only.
Every scenario works in a temporary copy of the package source. The real repository,
the real user home and the real ~/.claude are never written. HOME is a temporary fixture.
"""
import atexit
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import zipfile
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import DEFAULT_SKILL, REPO, report, skill_dir  # noqa: E402

SKILL = skill_dir()
RESULTS = []
TMP = Path(tempfile.mkdtemp(prefix="p9_dist_"))
atexit.register(shutil.rmtree, TMP, True)
REL = Path(".claude/skills/learning")
REAL_PERSONAL = Path(os.environ.get("USERPROFILE") or os.environ["HOME"]) / REL
REAL_PERSONAL_BEFORE = REAL_PERSONAL.exists()
FAKE_HOME = TMP / "home"
FAKE_HOME.mkdir()


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree(d):
    """Map relative path -> sha256 for every file under d (empty dict if missing)."""
    d = Path(d)
    return {p.relative_to(d).as_posix(): sha(p) for p in sorted(d.rglob("*")) if p.is_file()} if d.exists() else {}


def ps(src, script, *args, home=FAKE_HOME, fault=None, cwd=None):
    """Run <src>/scripts/<script> with Windows PowerShell. Return (exit code, output)."""
    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home))
    env.pop("LEARNING_SKILL_TEST_FAULT", None)
    if fault:
        env["LEARNING_SKILL_TEST_FAULT"] = fault
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(Path(src) / "scripts" / script), *map(str, args)]
    out = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd)
    return out.returncode, out.stdout + out.stderr


def make_source(name, skill=SKILL, version=None):
    """Copy VERSION, scripts/ and a skill into TMP/<name>; build manifest + release ZIP there."""
    src = TMP / name
    shutil.copytree(skill, src / REL)
    shutil.copytree(REPO / "scripts", src / "scripts")
    (src / "VERSION").write_text(version or (REPO / "VERSION").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    build(src)
    return src


def build(src, out=None):
    rc, log = ps(src, "build-release.ps1", "-RepoRoot", src, *(["-OutDir", out] if out else []))
    assert rc == 0, log
    return log


def zip_of(src):
    v = (src / "VERSION").read_text(encoding="utf-8").strip()
    return src / "dist" / f"claude-learning-skill-v{v}.zip"


def project(name, state=True):
    """Temporary git project. With state=True it holds docs/learning, CLAUDE.md, another skill and settings."""
    p = TMP / name
    (p / "src").mkdir(parents=True)
    (p / "PLAN.md").write_text("# Plan\n\n- Step 1: build parser\n", encoding="utf-8")
    if state:
        (p / "docs/learning/state").mkdir(parents=True)
        (p / "docs/learning/state/LEARNING_CONFIG.md").write_text("project_id: PRJ-0000test\n", encoding="utf-8")
        (p / "docs/learning/passes/LP-20261027-01").mkdir(parents=True)
        (p / "docs/learning/passes/LP-20261027-01/LEARNING_PASS.md").write_text("pass\n", encoding="utf-8")
        (p / "CLAUDE.md").write_text("project rules\n", encoding="utf-8")
        (p / ".claude/skills/other").mkdir(parents=True)
        (p / ".claude/skills/other/SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")
        (p / ".claude/settings.json").write_text("{}\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(p)], check=True)
    return p


def outside_skill(p):
    """Every file of a project except the learning skill target."""
    return {k: v for k, v in tree(p).items() if not k.startswith(REL.as_posix() + "/")}


def library(name):
    lib = TMP / name
    (lib / "registry").mkdir(parents=True)
    (lib / "registry/CONCEPT_REGISTRY.md").write_text("| CH-00000001 | Cache |\n", encoding="utf-8")
    (lib / "concepts").mkdir()
    (lib / "concepts/CH-00000001.md").write_text("home\n", encoding="utf-8")
    return lib


def leftovers(p):
    return sorted(x.name for x in (Path(p) / ".claude").glob(".learning-*"))


SRC = make_source("src")
MANIFEST = json.loads((SRC / "distribution/manifest.json").read_text(encoding="utf-8"))
V1 = tree(SRC / REL)
V1_ZIP = zip_of(SRC)

# Test A - package manifest
check("A manifest version = VERSION", MANIFEST["version"], (REPO / "VERSION").read_text(encoding="utf-8").strip())
check("A manifest skill_name / entry_point", (MANIFEST["skill_name"], MANIFEST["entry_point"]), ("learning", "SKILL.md"))
check("A manifest file set = runtime skill", sorted(f["path"] for f in MANIFEST["files"]), sorted(V1))
check("A manifest sha256 = runtime skill", {f["path"]: f["sha256"] for f in MANIFEST["files"]}, V1)
check("A entry point listed", "SKILL.md" in V1, True)
check("A no non-markdown runtime file", [k for k in V1 if not k.endswith(".md")], [])
if SKILL.resolve() == DEFAULT_SKILL.resolve():
    committed = json.loads((REPO / "distribution/manifest.json").read_text(encoding="utf-8"))
    check("A repository manifest is current", committed, MANIFEST)

# Test B - release ZIP contents
names = zipfile.ZipFile(V1_ZIP).namelist()
check("B zip entries = skill + manifest",
      sorted(names), sorted([f"{REL.as_posix()}/{k}" for k in V1] + ["distribution/manifest.json"]))
banned = ("tests/", "docs/", ".git", "Universal_Learning_Architecture", "StudySystem", "scripts/", "__pycache__")
check("B no tests / docs / sources / git / scripts in zip", [n for n in names if any(b in n for b in banned)], [])
check("B no backslash entry names", [n for n in names if "\\" in n], [])
sums = (SRC / "dist/SHA256SUMS.txt").read_text(encoding="utf-8").split()
check("B SHA256SUMS matches zip", sums, [sha(V1_ZIP), V1_ZIP.name])
build(SRC, TMP / "rebuild")
check("B deterministic rebuild", sha(TMP / "rebuild" / V1_ZIP.name), sha(V1_ZIP))

# Test C - clean package (extracted release ZIP verifies)
clean = TMP / "clean"
zipfile.ZipFile(V1_ZIP).extractall(clean)
check("C extracted skill = manifest", tree(clean / REL), V1)
rc, log = ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", clean, "-Archive", V1_ZIP)
check("C verify-install PASS on extracted package", (rc, "PASS:" in log), (0, True))

# Test D - project install (LOCAL source)
bare = project("proj_bare", state=False)
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", bare)
check("D project install exit 0", rc, 0)
check("D target = manifest", tree(bare / REL), V1)
check("D docs/learning not created", (bare / "docs/learning").exists(), False)
check("D no staging leftovers", leftovers(bare), [])
rc, log = ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", bare)
check("D verify-install PASS", (rc, "PASS:" in log), (0, True))
cwdp = project("proj_cwd", state=False)
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", cwd=cwdp)
check("D no -ProjectPath -> current directory", (rc, tree(cwdp / REL) == V1), (0, True))

# Test E - existing install
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", bare)
check("E same package -> ALREADY INSTALLED", (rc, "ALREADY INSTALLED" in log), (0, True))
(bare / REL / "SKILL.md").write_text("locally edited\n", encoding="utf-8")
edited = tree(bare / REL)
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", bare)
check("E different package -> refused, no silent overwrite", (rc != 0, "different learning skill" in log), (True, True))
check("E refused install left target unchanged", tree(bare / REL), edited)
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", bare, "-Force")
check("E -Force replaces", (rc, tree(bare / REL)), (0, V1))

# Test F - personal install (temporary HOME)
rc, log = ps(SRC, "install.ps1", "-Scope", "Personal")
check("F personal install exit 0", rc, 0)
check("F target = <temp-home>/.claude/skills/learning", tree(FAKE_HOME / REL), V1)
p1, p2 = project("proj_p1", state=False), project("proj_p2", state=False)
rc1, log1 = ps(SRC, "install.ps1", "-Scope", "Personal", cwd=p1)
rc2, log2 = ps(SRC, "verify-install.ps1", "-Scope", "Personal", cwd=p2)
check("F two projects resolve the same personal target", (rc1, "ALREADY INSTALLED" in log1, rc2, "PASS:" in log2), (0, True, 0, True))
check("F personal install writes nothing into projects", (p1 / ".claude").exists() or (p2 / ".claude").exists(), False)
check("F real personal skill untouched", REAL_PERSONAL.exists(), REAL_PERSONAL_BEFORE)

# Test G - update preserves state
skill2 = TMP / "skill_v2"
shutil.copytree(SKILL, skill2)
with open(skill2 / "SKILL.md", "a", encoding="utf-8", newline="\n") as f:
    f.write("\n<!-- controlled 1.0.1 change -->\n")
(skill2 / "templates/NEW_TEMPLATE.md").write_text("# New\n", encoding="utf-8", newline="\n")
SRC2 = make_source("src2", skill=skill2, version="1.0.1\n")
V2, V2_ZIP = tree(SRC2 / REL), zip_of(SRC2)
lib = library("library")
up = project("proj_update")
ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", up)
state_before, lib_before = outside_skill(up), tree(lib)
head_before = tree(up / ".git")
rc, log = ps(SRC, "update.ps1", "-Scope", "Project", "-ProjectPath", up, "-Archive", V2_ZIP)
check("G update exit 0", (rc, "UPDATED" in log), (0, True))
check("G runtime skill = v2", tree(up / REL), V2)
check("G docs/learning, CLAUDE.md, other skill, settings unchanged", outside_skill(up), state_before)
check("G .git unchanged", tree(up / ".git"), head_before)
check("G personal library unchanged", tree(lib), lib_before)
check("G no staging leftovers", leftovers(up), [])
rc, log = ps(SRC, "update.ps1", "-Scope", "Project", "-ProjectPath", project("proj_noinst", state=False), "-Archive", V2_ZIP)
check("G update without install refused", (rc != 0, "existing install" in log), (True, True))
rc, log = ps(SRC, "update.ps1", "-Scope", "Project", "-ProjectPath", up, "-Archive", V2_ZIP)
check("G update to same package -> ALREADY INSTALLED", (rc, "ALREADY INSTALLED" in log), (0, True))
ps(SRC, "install.ps1", "-Scope", "Personal")
rc, log = ps(SRC, "update.ps1", "-Scope", "Personal", "-Archive", V2_ZIP)
check("G personal update", (rc, tree(FAKE_HOME / REL)), (0, V2))
check("G personal update leaves library unchanged", tree(lib), lib_before)

# Test H - rollback (old working install kept)
for fault in ("stage", "replace", "verify"):
    rb = project(f"proj_rb_{fault}")
    ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", rb)
    before = outside_skill(rb)
    rc, log = ps(SRC, "update.ps1", "-Scope", "Project", "-ProjectPath", rb, "-Archive", V2_ZIP, fault=fault)
    check(f"H {fault} fault -> update fails", rc != 0, True)
    check(f"H {fault} fault -> old install intact", tree(rb / REL), V1)
    check(f"H {fault} fault -> state unchanged", outside_skill(rb), before)
    check(f"H {fault} fault -> no staging leftovers", leftovers(rb), [])
fresh = project("proj_rb_fresh", state=False)
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", fresh, fault="verify")
check("H fresh install verify fault -> no partial skill", (rc != 0, (fresh / REL).exists()), (True, False))
locked = project("proj_rb_locked")
ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", locked)
with open(locked / REL / "references/01_OPERATIONAL_CORE.md", "rb"):
    rc, log = ps(SRC, "update.ps1", "-Scope", "Project", "-ProjectPath", locked, "-Archive", V2_ZIP)
check("H real replacement failure (open file) -> update fails", rc != 0, True)
check("H real replacement failure -> old install intact", tree(locked / REL), V1)
check("H real replacement failure -> no staging leftovers", leftovers(locked), [])

# Test I - failure injection on the source package
bad = make_source("src_badhash")
(bad / REL / "references/02_COVERAGE_PROTOCOL.md").write_text("tampered\n", encoding="utf-8")
tgt = project("proj_bad", state=False)
rc, log = ps(bad, "install.ps1", "-Scope", "Project", "-ProjectPath", tgt)
check("I bad hash -> refused", (rc != 0, "hash mismatch" in log), (True, True))
check("I bad hash -> nothing written", (tgt / ".claude").exists(), False)
nosk = make_source("src_noskill")
(nosk / REL / "SKILL.md").unlink()
rc, log = ps(nosk, "install.ps1", "-Scope", "Project", "-ProjectPath", tgt)
check("I missing SKILL.md -> refused", (rc != 0, "missing file: SKILL.md" in log), (True, True))
check("I missing SKILL.md -> nothing written", (tgt / ".claude").exists(), False)
inst = project("proj_bad_existing")
ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", inst)
rc, log = ps(bad, "update.ps1", "-Scope", "Project", "-ProjectPath", inst)
check("I bad hash update -> old install intact", (rc != 0, tree(inst / REL)), (True, V1))
crash = project("proj_crash", state=False)
(crash / ".claude/.learning-install-deadbeef/stage").mkdir(parents=True)
(crash / ".claude/.learning-install-deadbeef/stage/SKILL.md").write_text("half\n", encoding="utf-8")
rc, log = ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", crash)
check("I leftover from interrupted run does not block install", (rc, tree(crash / REL)), (0, V1))
check("I leftover lives outside .claude/skills (not a skill)", (crash / ".claude/skills/.learning-install-deadbeef").exists(), False)
check("I missing project path -> refused", ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", TMP / "nope")[0] != 0, True)

# Test J - verify FAIL cases
vf = project("proj_verify", state=False)
check("J verify not installed -> FAIL", ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", vf)[0] != 0, True)
ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", vf)
(vf / REL / "state").mkdir()
(vf / REL / "state/LEARNING_CONFIG.md").write_text("project state\n", encoding="utf-8")
rc, log = ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", vf)
check("J project state inside skill -> FAIL", (rc != 0, "possible project state" in log), (True, True))
shutil.rmtree(vf / REL / "state")
(vf / REL / "SKILL.md").unlink()
rc, log = ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", vf)
check("J missing SKILL.md -> FAIL", (rc != 0, "missing file: SKILL.md" in log), (True, True))

# Test K - uninstall keeps state
un = project("proj_uninstall")
ps(SRC, "install.ps1", "-Scope", "Project", "-ProjectPath", un)
before = outside_skill(un)
rc, log = ps(SRC, "uninstall.ps1", "-Scope", "Project", "-ProjectPath", un)
check("K project uninstall exit 0", rc, 0)
check("K project skill removed", (un / REL).exists(), False)
check("K docs/learning, CLAUDE.md, other skill retained", outside_skill(un), before)
check("K retained messages", ("Learning state retained." in log, "Personal Technical Library retained." in log), (True, True))
rc, log = ps(SRC, "uninstall.ps1", "-Scope", "Project", "-ProjectPath", un)
check("K uninstall when absent -> NOT INSTALLED", (rc, "NOT INSTALLED" in log), (0, True))
lib_before = tree(lib)
rc, log = ps(SRC, "uninstall.ps1", "-Scope", "Personal")
check("K personal skill removed", (rc, (FAKE_HOME / REL).exists()), (0, False))
check("K personal library retained", tree(lib), lib_before)
check("K real personal skill untouched", REAL_PERSONAL.exists(), REAL_PERSONAL_BEFORE)

# Test L - remote bootstrap (GitHub-style source archive over HTTP)
srv = TMP / "srv"
(srv / "owner/repo/archive").mkdir(parents=True)
(srv / "raw").mkdir()
shutil.copy(SRC / "scripts/install.ps1", srv / "raw/install.ps1")


def github_archive(src, dest):
    """Zip src the way GitHub source archives look: one top folder <repo>-<ref>/."""
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file() and "dist" not in f.relative_to(src).parts:
                z.write(f, "repo-1.0.0/" + f.relative_to(src).as_posix())


github_archive(SRC, srv / "owner/repo/archive/v1.0.0.zip")
github_archive(bad, srv / "owner/repo/archive/tampered.zip")
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


handler = partial(QuietHandler, directory=str(srv))
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{httpd.server_port}"


def one_liner(target, ref):
    """README quick-install syntax, with the test server in place of GitHub."""
    cmd = (f"& ([scriptblock]::Create((Invoke-RestMethod '{base}/raw/install.ps1'))) "
           f"-Scope Project -ProjectPath '{target}' -Repository owner/repo -Ref {ref} -BaseUrl '{base}'")
    env = dict(os.environ, USERPROFILE=str(FAKE_HOME), HOME=str(FAKE_HOME))
    out = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd], capture_output=True, text=True, env=env)
    return out.returncode, out.stdout + out.stderr


rp = project("proj_remote")
before = outside_skill(rp)
rc, log = one_liner(rp, "v1.0.0")
check("L one-liner remote install exit 0", (rc, "INSTALLED" in log), (0, True))
check("L remote target = manifest", tree(rp / REL), V1)
check("L remote install keeps state", outside_skill(rp), before)
rc, log = ps(SRC, "verify-install.ps1", "-Scope", "Project", "-ProjectPath", rp, "-Repository", "owner/repo", "-Ref", "v1.0.0", "-BaseUrl", base)
check("L remote verify PASS", (rc, "PASS:" in log), (0, True))
rt = project("proj_remote_bad", state=False)
rc, log = one_liner(rt, "tampered")
check("L tampered remote archive -> refused, nothing written", (rc != 0, "hash mismatch" in log, (rt / ".claude").exists()), (True, True, False))
rc, log = one_liner(rt, "missing-ref")
check("L download failure -> nothing written", (rc != 0, (rt / ".claude").exists()), (True, False))
httpd.shutdown()

report(RESULTS)
