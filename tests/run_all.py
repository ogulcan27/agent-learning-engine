"""Run the permanent regression suite: Phase 3-7 subsystem suites, Phase 8 E2E suite, static, cross-project isolation and Human Sync suites,
Phase 9 distribution suite, mutation checks.

Usage:
    uv run --no-project python tests/run_all.py [<skill_dir>] [--no-mutations]

Standard library only. Every suite reads its rules from the skill files under test.
The distribution suite needs Windows PowerShell 5.1+ and runs once (not inside mutation checks).
"""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SUITES = ["phase3", "phase4", "phase5", "phase6", "phase7", "integration", "static", "isolation", "sync"]
DISTRIBUTION = ["distribution"]


def run_suite(name, skill):
    """Run one suite in a subprocess. Returns (passed, total, failing test names)."""
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    cmd = [sys.executable, str(ROOT / "common" / "safe_run.py"), str(ROOT / name / "run_tests.py"), str(skill)]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    m = re.search(r"^(\d+)/(\d+) passed$", out.stdout, re.M)
    failing = [l[6:].split("  actual=")[0] for l in out.stdout.splitlines() if l.startswith("FAIL  ")]
    if not m:
        return 0, 0, failing + [f"CRASH: {(out.stderr.strip().splitlines() or ['?'])[-1]}"]
    return int(m.group(1)), int(m.group(2)), failing


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    skill = Path(args[0]) if args else ROOT.parent / ".claude" / "skills" / "stay-in-the-loop"
    ok = True
    print(f"Skill under test: {skill}\n")
    for name in SUITES + DISTRIBUTION:
        passed, total, failing = run_suite(name, skill)
        ok &= passed == total and total > 0
        print(f"{name:<12} {passed}/{total} {'PASS' if passed == total and total else 'FAIL'}")
        for f in failing:
            print(f"    FAIL {f}")
    if "--no-mutations" not in sys.argv:
        import mutation
        print("\nMutation checks (each mutation must be caught):")
        ok &= mutation.main(skill)
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
