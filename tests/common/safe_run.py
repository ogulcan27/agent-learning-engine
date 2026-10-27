"""Run a suite's run_tests.py scenario by scenario; a crashing scenario is recorded as FAIL.

Usage: safe_run.py <run_tests.py> [<skill_dir>]
Scenario blocks start with '# Test ' or '# Extra ' comment lines.
"""
import re
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
sys.argv = [str(target)] + sys.argv[2:]
sys.path.insert(0, str(target.parent))
src = target.read_text(encoding="utf-8")
body, _ = src.rsplit("report(RESULTS)", 1)
head, *blocks = re.split(r"\n(?=# (?:Test|Extra) )", body)
g = {"__name__": "scenario", "__file__": str(target)}
exec(compile(head, str(target), "exec"), g)
for block in blocks:
    title = block.splitlines()[0].lstrip("# ")
    try:
        exec(compile(block, str(target), "exec"), g)
    except Exception as e:
        g["RESULTS"].append((f"{title} CRASHED: {type(e).__name__}: {e}", False, None, None))
g["report"](g["RESULTS"])
