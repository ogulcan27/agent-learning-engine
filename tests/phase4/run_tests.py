"""Synthetic Phase 4 tests A-J plus protocol consistency checks.

Usage: run_tests.py <skill_dir> [--mutate dup-event]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402
from hs_model import (Protocol, build_pass, fails, integrity, parse_debts, parse_events, render_debts,
                      render_events)

SKILL = skill_dir()
MUTATE = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--mutate" else None
P = Protocol(SKILL)
RESULTS = []
V = "VERIFIED (commit:9f3a1c2b7d4e; test:tests/test_worker.py)"


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def roundtrip(lp):
    """Write events and debts as Markdown and read them back."""
    events = parse_events(render_events(P, lp["events"]))
    if MUTATE == "dup-event" and events:
        events.append(dict(events[0]))
    return events, parse_debts(P, render_debts(P, lp["debts"]))


def routine(wu, kind):
    return {"wu": wu, "kind": kind, "topic": kind, "evidence": V}


def queue_change(wu="jira:INC-44", **kw):
    ch = {"wu": wu, "kind": "async job design", "topic": "Long request blocks API", "q1": True, "q2": True,
          "sd_signals": ["flow", "performance"], "must_signals": ["system behaviour"],
          "gap_signals": ["concept first appearance"], "evidence": V,
          "mechanism": "background queue", "signal": "slow work on request path -> move off path"}
    ch.update(kw)
    return ch


# Test A - routine only
scope = ["git:aaaaaaaaaaaa"]
lp = build_pass(P, "LP-20261027-01", scope, [routine(scope[0], k) for k in
                                              ("file rename", "formatting", "import change")])
check("A meaningful events = 0", len(lp["events"]), 0)
check("A eligible outcome = NOT_LEARNING_RELEVANT", lp["proposal"][scope[0]][0], "NOT_LEARNING_RELEVANT")

# Test B - System Design decision
scope = ["jira:INC-44"]
lp = build_pass(P, "LP-20261027-02", scope, [queue_change()])
ev, debts = roundtrip(lp)
check("B category SYSTEM_DESIGN", ev[0]["Category"], "SYSTEM_DESIGN")
check("B priority MUST_UNDERSTAND", ev[0]["Knowledge Priority"], "MUST_UNDERSTAND")
check("B gap -> ULA_CANDIDATE", ev[0]["Disposition"], "ULA_CANDIDATE")
check("B integrity clean", fails(integrity(P, ev, debts, scope)), [])
lp_known = build_pass(P, "LP-20261027-03", scope, [queue_change(user_knowledge="prior_artifact")])
check("B known -> EXPERIENCE_ONLY", lp_known["events"][0]["Disposition"], "EXPERIENCE_ONLY")
lp_unknown = build_pass(P, "LP-20261027-04", scope, [queue_change(gap_signals=[])])
check("B MUST + UNKNOWN -> UNRESOLVED (no guess)", lp_unknown["events"][0]["Disposition"], "UNRESOLVED")

# Test C - DSA event
scope = ["jira:INC-50"]
topk = {"wu": scope[0], "kind": "ranking", "topic": "Need only Top-K", "q1": True, "q2": True,
        "computational_need": True, "must_signals": ["recurring pattern"], "gap_signals": ["reusable but new"],
        "evidence": V, "mechanism": "heap of size K, O(n log k)", "signal": "only top K needed -> heap, not full sort"}
lp = build_pass(P, "LP-20261027-05", scope, [topk])
check("C category DSA", lp["events"][0]["Category"], "DSA")
check("C reusable signal present", lp["events"][0]["Reusable Signal"] != "-", True)
no_need = dict(topk, computational_need=False, category="SOFTWARE_ENGINEERING")
check("C no computational need -> not DSA", build_pass(P, "LP-20261027-06", scope, [no_need])["events"][0]["Category"],
      "SOFTWARE_ENGINEERING")

# Test D - implementation detail suppression
scope = ["jira:INC-60"]
kinds = ["file rename", "formatting", "import change", "trivial syntax fix", "mechanical refactor",
         "routine CRUD", "file rename", "formatting", "import change", "routine CRUD"]
changes = [routine(scope[0], k) for k in kinds] + [queue_change(scope[0])]
lp = build_pass(P, "LP-20261027-07", scope, changes)
check("D 11 changes -> 1 meaningful event", len(lp["events"]), 1)
check("D 10 suppressed", lp["suppressed"], 10)

# Test E - Knowledge Debt
scope = ["jira:INC-70"]
idem = {"wu": scope[0], "kind": "api retry", "topic": "Idempotency key", "q1": True, "concept": "Idempotency",
        "gap_signals": ["reusable but new"], "evidence": V, "category": "RELIABILITY"}
lp = build_pass(P, "LP-20261027-08", scope, [idem])
ev, debts = roundtrip(lp)
check("E USEFUL_TO_KNOW + GAP -> KNOWLEDGE_DEBT", ev[0]["Disposition"], "KNOWLEDGE_DEBT")
check("E queue §B OPEN, LATER", (debts[0]["debt_status"], debts[0]["priority"]), ("OPEN", "LATER"))
check("E debt references event", debts[0].get("originating_event_id"), ev[0]["Event ID"])
check("E concept_home UNASSIGNED", debts[0]["concept_home"], "UNASSIGNED")
check("E integrity clean", fails(integrity(P, ev, debts, scope)), [])
lp = build_pass(P, "LP-20261027-09", ["jira:INC-44"], [queue_change()],
                overrides={"Long request blocks API": "defer"})
check("E user defers MUST event -> debt NOW", lp["debts"][0]["priority"], "NOW")

# Test F - multiple work units
scope = ["jira:INC-44", "jira:INC-45", "jira:INC-46", "jira:INC-47"]
changes = [queue_change("jira:INC-44"), queue_change("jira:INC-45", kind="worker retry"),
           routine("jira:INC-46", "formatting"), routine("jira:INC-47", "import change")]
lp = build_pass(P, "LP-20261027-10", scope, changes)
ev, debts = roundtrip(lp)
check("F one scope-level Human Sync", lp["human_sync_count"], 1)
check("F one high-signal event for 4 units", len(ev), 1)
check("F event links INC-44 and INC-45", ev[0]["Work Units"], "jira:INC-44; jira:INC-45")
check("F per-unit outcome", {k: v[0] for k, v in lp["proposal"].items()},
      {"jira:INC-44": "PARTIAL", "jira:INC-45": "PARTIAL",
       "jira:INC-46": "NOT_LEARNING_RELEVANT", "jira:INC-47": "NOT_LEARNING_RELEVANT"})
check("F integrity clean", fails(integrity(P, ev, debts, scope)), [])

# Test G - evidence status
scope = ["jira:INC-80"]
leak = queue_change(scope[0], topic="Feature uses future data?", sd_signals=[],
                    category="DATA_SCIENCE", evidence="UNRESOLVED")
lp = build_pass(P, "LP-20261027-11", scope, [leak])
check("G unclear evidence -> UNRESOLVED", lp["events"][0]["Disposition"], "UNRESOLVED")
check("G unit stays open (PARTIAL proposal)", lp["proposal"][scope[0]][0], "PARTIAL")
bare = [dict(lp["events"][0], **{"Evidence Status": "VERIFIED"})]
check("G VERIFIED without ref -> E-11 FAIL", ("E-11", "FAIL") in integrity(P, bare, [], scope), True)
unreadable = build_pass(P, "LP-20261027-12", scope, [routine(scope[0], "formatting") | {"evidence": "UNREADABLE"}])
check("G unreadable evidence -> no NLR proposal", unreadable["proposal"][scope[0]][0], None)

# Test H - partial handoff
scope = ["jira:INC-90"]
exp = queue_change(scope[0], topic="Cache TTL", kind="cache", user_knowledge="stated_known")
ula = queue_change(scope[0], topic="Replication lag", kind="db")
lp = build_pass(P, "LP-20261027-13", scope, [exp, ula])
ev, debts = roundtrip(lp)
check("H LE-01 EXPERIENCE_ONLY", ev[0]["Disposition"], "EXPERIENCE_ONLY")
check("H LE-02 ULA_CANDIDATE", ev[1]["Disposition"], "ULA_CANDIDATE")
check("H open_items -> LE-02 only", lp["proposal"][scope[0]], ("PARTIAL", "LE-LP-20261027-13-02"))
check("H open_items resolve to known events",
      fails(integrity(P, ev, debts, scope, partial_open_items=lp["proposal"][scope[0]][1])), [])
check("H unknown open_items -> E-10 FAIL",
      ("E-10", "FAIL") in integrity(P, ev, debts, scope, partial_open_items="LE-LP-20261027-13-07"), True)

# Test I - duplicate event id
check("I duplicate event_id -> E-01 FAIL", ("E-01", "FAIL") in integrity(P, ev + [dict(ev[0])], debts, scope), True)

# Test J - orphan debt
orphan = [{"debt_id": "KD-LP-20261027-13-01", "concept": "Idempotency", "originating_event_id": "LE-LP-20261027-13-09",
           "priority": "LATER", "debt_status": "OPEN"}]
check("J orphan debt -> E-07 FAIL", ("E-07", "FAIL") in integrity(P, ev, orphan, scope), True)

# Extra - consistency
check("X dispositions = 5 canonical", sorted(P.dispositions),
      sorted(["EXPERIENCE_ONLY", "ULA_CANDIDATE", "KNOWLEDGE_DEBT", "IMPLEMENTATION_DETAIL", "UNRESOLVED"]))
check("X priorities = 3", P.priorities, ["MUST_UNDERSTAND", "USEFUL_TO_KNOW", "IMPLEMENTATION_DETAIL"])
check("X evidence statuses = 4", P.evidence, ["VERIFIED", "INFERRED", "ASSUMED", "UNRESOLVED"])
check("X categories = 9", len(P.categories), 9)
check("X rule table outputs are known dispositions", all(r[3] in P.dispositions for r in P.rules), True)
impl = dict(lp["events"][0], **{"Knowledge Priority": "IMPLEMENTATION_DETAIL", "Disposition": "ULA_CANDIDATE"})
check("X IMPLEMENTATION_DETAIL as ULA_CANDIDATE -> E-09 FAIL", ("E-09", "FAIL") in integrity(P, [impl], [], scope), True)
check("X ULA list with unknown id -> E-06 FAIL", ("E-06", "FAIL") in integrity(P, ev, debts, scope, ula_list=["LE-x"]), True)
dup_debt = parse_debts(P, render_debts(P, build_pass(P, "LP-20261027-14", ["jira:INC-70"], [idem])["debts"] * 2))
e_ev = parse_events(render_events(P, build_pass(P, "LP-20261027-14", ["jira:INC-70"], [idem])["events"]))
check("X duplicate debt_id -> E-08 FAIL", ("E-08", "FAIL") in integrity(P, e_ev, dup_debt, ["jira:INC-70"]), True)
check("X debt event without §B -> E-13 FAIL", ("E-13", "FAIL") in integrity(P, e_ev, [], ["jira:INC-70"]), True)
check("X unknown category -> E-03 FAIL",
      ("E-03", "FAIL") in integrity(P, [dict(ev[0], Category="ML")], [], scope), True)
check("X event outside scope -> E-02 FAIL",
      ("E-02", "FAIL") in integrity(P, [dict(ev[0], **{"Work Units": "jira:INC-1"})], [], scope), True)

report(RESULTS)
