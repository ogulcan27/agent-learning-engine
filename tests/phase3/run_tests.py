"""Synthetic Phase 3 coverage tests A-I plus protocol consistency checks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402
from coverage_model import (Ledger, discover, integrity, load_ledger_header, load_transitions,
                            open_coverage, rebuild_queue, rebuild_state, resolve_scope, scope_commit,
                            skipped, transition, unit)

SKILL = skill_dir()
MATRIX = load_transitions(SKILL / "references" / "02_COVERAGE_PROTOCOL.md")
COLUMNS = load_ledger_header(SKILL / "templates" / "COVERAGE_LEDGER_TEMPLATE.md")
RESULTS = []


def seqs(rows):
    return sorted(int(r["seq"]) for r in rows)


def check(name, actual, expected):
    ok = actual == expected
    RESULTS.append((name, ok, actual, expected))


def roundtrip(ledger):
    """Write the ledger to Markdown and read it back, as /stay-in-the-loop would."""
    return Ledger.parse(COLUMNS, ledger.render())


# Test A — first discovery
led = Ledger(COLUMNS)
discover(led, [unit(n) for n in (1, 2, 3)])
led = roundtrip(led)
check("A first discovery -> 1-3 UNCOVERED", [(int(r["seq"]), r["status"]) for r in led.rows],
      [(1, "UNCOVERED"), (2, "UNCOVERED"), (3, "UNCOVERED")])

# Test B — covered history 1-3, current project 1-10
led = Ledger(COLUMNS, [unit(n, "COVERED", "EXTERNAL") for n in (1, 2, 3)])
discover(led, [unit(n) for n in range(1, 11)])
led = roundtrip(led)
check("B open gap -> 4-10", seqs(open_coverage(led)), list(range(4, 11)))
check("B integrity clean", [f for f in integrity(led) if f[1] == "FAIL"], [])

# Test C — latest only
selected = resolve_scope(led, "latest")
check("C latest selects 10", seqs(selected), [10])
scope_commit(led, MATRIX, selected, "latest")
led = roundtrip(led)
check("C 4-9 DEFERRED", seqs([r for r in led.rows if r["status"] == "DEFERRED"]), list(range(4, 10)))
check("C 10 still UNCOVERED before completion", led.by_id(selected[0]["work_unit_id"])["status"], "UNCOVERED")
# simulated Completion Commit for 10 (test only)
transition(led, MATRIX, selected[0]["work_unit_id"], "COVERED", "C", learning_pass_id="LP-20261027-01")
led = roundtrip(led)

# Test D — next invocation, same project
discover(led, [unit(n) for n in range(1, 11)])
check("D 4-9 still open", seqs(open_coverage(led)), list(range(4, 10)))

# Test E — catch-up
check("E catch-up selects 4-9", seqs(resolve_scope(led, "catch-up")), list(range(4, 10)))

# Test F — skip 5
transition(led, MATRIX, unit(5)["work_unit_id"], "SKIPPED_BY_USER", "U", notes="user: not needed")
led = roundtrip(led)
check("F 5 not in default gap", 5 in seqs(open_coverage(led)), False)
check("F 5 in show skipped", seqs(skipped(led)), [5])
check("F catch-up excludes 5", 5 in seqs(resolve_scope(led, "catch-up")), False)

# Test G — partial 6 (simulated completion)
transition(led, MATRIX, unit(6)["work_unit_id"], "PARTIAL", "C",
           learning_pass_id="LP-20261027-02", open_items="replication lag")
led = roundtrip(led)
check("G 6 in open coverage", 6 in seqs(open_coverage(led)), True)
check("G pending = DEFERRED+PARTIAL", seqs(resolve_scope(led, "pending")), [4, 6, 7, 8, 9])

# Test H — duplicate ID
dup = Ledger(COLUMNS, led.rows + [dict(led.rows[0])])
check("H duplicate id -> C-01 FAIL", ("C-01", "FAIL") in integrity(dup), True)

# Test I — state mismatch
stale_state = dict(rebuild_state(led), deferred_count=2)
check("I ledger deferred = 4", rebuild_state(led)["deferred_count"], 4)
check("I mismatch -> C-08 WARNING", ("C-08", "WARNING") in integrity(led, state=stale_state), True)
check("I rebuilt state clean", ("C-08", "WARNING") in integrity(led, state=rebuild_state(led)), False)

# Extra — protocol consistency
try:
    transition(led, MATRIX, unit(10)["work_unit_id"], "DEFERRED", "S")
    check("X COVERED -> DEFERRED rejected", "accepted", "C-10")
except ValueError as e:
    check("X COVERED -> DEFERRED rejected", str(e)[:4], "C-10")
try:
    transition(led, MATRIX, unit(4)["work_unit_id"], "COVERED", "S")
    check("X COVERED only via Completion Commit", "accepted", "C-10")
except ValueError as e:
    check("X COVERED only via Completion Commit", str(e)[:4], "C-10")
transition(led, MATRIX, unit(5)["work_unit_id"], "UNCOVERED", "U", notes="user reopened")
check("X SKIPPED -> UNCOVERED on explicit reopen", 5 in seqs(open_coverage(led)), True)
check("X queue mismatch -> C-09 WARNING", ("C-09", "WARNING") in integrity(led, queue_ids=["x"]), True)
check("X queue rebuild = DEFERRED+PARTIAL", seqs(rebuild_queue(led)), [4, 6, 7, 8, 9])
missing_pass = Ledger(COLUMNS, [unit(1, "COVERED", "-")])
check("X COVERED without pass -> C-05 FAIL", ("C-05", "FAIL") in integrity(missing_pass), True)
required = {("UNCOVERED", t) for t in ("COVERED", "PARTIAL", "DEFERRED", "SKIPPED_BY_USER", "NOT_LEARNING_RELEVANT")}
required |= {("DEFERRED", t) for t in ("COVERED", "PARTIAL", "SKIPPED_BY_USER")}
required |= {("PARTIAL", "COVERED"), ("PARTIAL", "DEFERRED"), ("SKIPPED_BY_USER", "UNCOVERED")}
check("X required transitions present", sorted(required - set(MATRIX)), [])

report(RESULTS)
