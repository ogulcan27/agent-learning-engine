"""Shared helpers for the permanent regression suite (standard library only)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
DEFAULT_SKILL = REPO / ".claude" / "skills" / "learning"


def use(*dirs):
    """Put sibling test packages (e.g. 'phase3') on sys.path."""
    for d in dirs:
        p = str(ROOT / d)
        if p not in sys.path:
            sys.path.insert(0, p)


def skill_dir():
    """Skill directory under test: first CLI argument or the repo skill."""
    return Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else DEFAULT_SKILL


def report(results):
    """Print PASS/FAIL lines and the 'n/m passed' summary; exit 1 on any failure."""
    failed = [r for r in results if not r[1]]
    for name, ok, actual, expected in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"  actual={actual} expected={expected}"))
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    sys.exit(1 if failed else 0)
