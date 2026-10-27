"""Synthetic Phase 5 tests A-P plus protocol consistency checks.

Usage: run_tests.py <skill_dir>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir, use  # noqa: E402
from ula_model import (Pass, Protocol, abandon, audit, build, completion, early_check, event, fails, integrity_u,
                       new_ledger, new_pass_conflict, resume, review, route, route_all, run_light, start_full,
                       startup, write)

P = Protocol(skill_dir())
RESULTS = []


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def refused(fn, *a, **kw):
    try:
        fn(*a, **kw)
        return False
    except ValueError:
        return True


def status(ledger, wu):
    r = ledger.by_id(wu)
    return r["status"], r["open_items"]


def full_pass(pid="LP-20261027-01", wu="jira:INC-44"):
    eid = f"LE-{pid}-01"
    lp = Pass(pid, [wu], [event(eid, "ULA_CANDIDATE", [wu], triggers=["IMPORTANT_ARCHITECTURE_DECISION",
                                                                       "RECURSIVE_TOPIC_STRUCTURE"])])
    early_check(P, lp)
    route_all(P, lp)
    start_full(P, lp, eid)
    return lp, eid


# Test A - no ULA candidate
wu = "jira:INC-10"
lp = Pass("LP-20261027-01", [wu], [event("LE-1", "EXPERIENCE_ONLY", [wu]), event("LE-2", "KNOWLEDGE_DEBT", [wu])],
          debts=[{"origin": "LE-2", "status": "OPEN"}])
check("A early completion", early_check(P, lp), "COMPLETION")
led = new_ledger(P, [wu])
completion(P, lp, led)
check("A only COMPLETION stage loaded (no ULA)", [s for s, _ in lp.loaded], ["COMPLETION"])
check("A unit COVERED, pass COMPLETE", (status(led, wu)[0], lp.status), ("COVERED", "COMPLETE"))

# Test B - all routine
scope = ["git:aaaaaaaaaaaa", "git:bbbbbbbbbbbb"]
lp = Pass("LP-20261027-02", scope, [])
check("B ULA not entered", early_check(P, lp), "COMPLETION")
led = new_ledger(P, scope)
completion(P, lp, led)
check("B all NOT_LEARNING_RELEVANT", [status(led, w)[0] for w in scope], ["NOT_LEARNING_RELEVANT"] * 2)
check("B pass COMPLETE", lp.status, "COMPLETE")

# Test C - Light route
ev = event("LE-3", "ULA_CANDIDATE", [wu])
check("C cache invalidation basic -> LIGHT", route(P, ev)[0], "LIGHT")
lp = Pass("LP-20261027-03", [wu], [ev])
early_check(P, lp)
route_all(P, lp)
run_light(P, lp, "LE-3", [[]])
check("C Light COMPLETE", lp.routing["LE-3"]["ULA Status"], "COMPLETE")
check("C Light loads no role file", any("ula/LEARNING" in f or "ula/CONTENT" in f for s, f in lp.loaded), False)
check("C integrity clean", fails(integrity_u(P, lp)), [])
check("C unknown trigger not counted", route(P, event("x", "ULA_CANDIDATE", [wu], triggers=["COOL_TOPIC"]))[0],
      "LIGHT")

# Test D - Full route
check("D critical recursive architecture -> FULL",
      route(P, event("x", "ULA_CANDIDATE", [wu], triggers=["IMPORTANT_ARCHITECTURE_DECISION",
                                                            "RECURSIVE_TOPIC_STRUCTURE", "CRITICAL_THEORY"]))[0],
      "FULL")
check("D uncertain -> ROUTING UNCERTAIN", route(P, event("x", "ULA_CANDIDATE", [wu], uncertain=True)),
      (None, "ROUTING UNCERTAIN"))

# Test E - explicit override
check("E LIGHT auto + user FULL -> FULL", route(P, event("x", "ULA_CANDIDATE", [wu], override="FULL"))[0], "FULL")
ev = event("LE-4", "ULA_CANDIDATE", [wu], triggers=["CRITICAL_THEORY"], override="LIGHT")
check("E FULL auto + user LIGHT -> LIGHT", route(P, ev)[0], "LIGHT")
lp = Pass("LP-20261027-04", [wu], [ev])
early_check(P, lp)
route_all(P, lp)
check("E LIGHT override with trigger -> U-17 WARNING", ("U-17", "WARNING") in integrity_u(P, lp), True)

# Test F - Full review gate
lp, eid = full_pass("LP-20261027-05")
check("F after Architect -> FULL_ULA_REVIEW", lp.stage, "FULL_ULA_REVIEW")
check("F pass WAITING_USER", lp.status, "WAITING_USER")
check("F Builder refused at review", refused(build, P, lp, eid), True)
check("F approve without user approval refused", refused(lambda: __import__("ula_model").advance(
    P, lp, eid, "user approve")), True)
check("F no CONTENT written", "CONTENT" in lp.art[eid], False)

# Test G - Full successful flow
review(P, lp, eid, "approve")
check("G architecture FROZEN by user", (lp.art[eid]["ARCHITECTURE"]["status"],
                                        lp.art[eid]["ARCHITECTURE"]["approved_by"]), ("FROZEN", "user"))
build(P, lp, eid)
audit(P, lp, eid, "READY TO FREEZE")
check("G ULA COMPLETE", lp.routing[eid]["ULA Status"], "COMPLETE")
check("G integrity clean", fails(integrity_u(P, lp)), [])
check("G roles loaded one stage at a time", [s for s, _ in lp.loaded],
      ["FULL_ULA_ARCHITECT", "FULL_ULA_BUILD", "FULL_ULA_AUDIT"])
lp2, e2 = full_pass("LP-20261027-06")
review(P, lp2, e2, "approve")
build(P, lp2, e2)
audit(P, lp2, e2, "FREEZE AFTER MINOR FIXES")
check("G minor fixes -> COMPLETE, no re-audit", (lp2.routing[e2]["ULA Status"], lp2.art[e2]["AUDIT"]["writes"]),
      ("COMPLETE", 1))

# Test H - auditor -> Builder revision
lp, eid = full_pass("LP-20261027-07")
review(P, lp, eid, "approve")
build(P, lp, eid)
audit(P, lp, eid, "DO NOT FREEZE — REVISION REQUIRED")
check("H content problem -> FULL_ULA_BUILD", lp.stage, "FULL_ULA_BUILD")
check("H architecture not reopened", (lp.art[eid]["ARCHITECTURE"]["status"], lp.art[eid]["ARCHITECTURE"]["writes"]),
      ("FROZEN", 1))
build(P, lp, eid)
check("H second same route -> BLOCKED", audit(P, lp, eid, "DO NOT FREEZE — REVISION REQUIRED"), "BLOCKED")

# Test I - architecture revision
lp, eid = full_pass("LP-20261027-08")
review(P, lp, eid, "approve")
build(P, lp, eid)
audit(P, lp, eid, "DO NOT FREEZE — ARCHITECTURE REVISIT REQUIRED")
check("I architect reopen -> human review", (lp.stage, lp.status), ("FULL_ULA_REVIEW", "WAITING_USER"))
check("I architecture back to PROPOSED", lp.art[eid]["ARCHITECTURE"]["status"], "PROPOSED")
check("I Builder blocked until approval", refused(build, P, lp, eid), True)

# Test J - resume
lp, eid = full_pass("LP-20261027-09")
check("J new /learning asks resume/new/abandon", startup([lp])[:2], ("ASK", ["resume", "new", "abandon"]))
check("J explicit arg -> no question", startup([lp], "resume"), "RESUME")
arch_writes = lp.art[eid]["ARCHITECTURE"]["writes"]
check("J resume keeps pass id and stage", resume(lp), ("LP-20261027-09", "FULL_ULA_REVIEW"))
check("J same architecture, no regeneration", lp.art[eid]["ARCHITECTURE"]["writes"], arch_writes)
check("J integrity clean after resume", fails(integrity_u(P, lp)), [])
write(lp, eid, "PROJECT_BRIEF", legit=False)
check("J regenerated completed stage -> U-14 FAIL", ("U-14", "FAIL") in integrity_u(P, lp), True)

# Test K - abandon
lp, eid = full_pass("LP-20261027-10")
led = new_ledger(P, ["jira:INC-44"], status="PARTIAL", open_items=eid, pass_id="LP-20261027-00")
before = [dict(r) for r in led.rows]
abandon(lp, led)
check("K pass ABANDONED", lp.status, "ABANDONED")
check("K ledger unchanged, open_items kept", [dict(r) for r in led.rows], before)
check("K events kept", list(lp.events), [eid])
led.rows[0]["status"] = "COVERED"
check("K ledger change after abandon -> U-13 FAIL", ("U-13", "FAIL") in integrity_u(P, lp, led), True)

# Test L - ULA closes open item
wu = "jira:INC-90"
lp = Pass("LP-20261027-11", [wu], [event("LE-01", "EXPERIENCE_ONLY", [wu]), event("LE-02", "ULA_CANDIDATE", [wu])])
early_check(P, lp)
route_all(P, lp)
led = new_ledger(P, [wu])
completion(P, lp, led)
check("L first commit PARTIAL, open_items LE-02", status(led, wu), ("PARTIAL", "LE-02"))
check("L pass not COMPLETE", lp.status, "WAITING_USER")
run_light(P, lp, "LE-02", [[]])
completion(P, lp, led)
check("L LE-02 COMPLETE -> open_items empty, COVERED", status(led, wu), ("COVERED", "-"))
check("L pass COMPLETE + integrity clean", (lp.status, fails(integrity_u(P, lp, led))), ("COMPLETE", []))

# Test M - unresolved event
lp = Pass("LP-20261027-12", [wu], [event("LE-05", "UNRESOLVED", [wu])])
check("M ULA not entered, waits user", (early_check(P, lp), lp.status), ("HUMAN_SYNC", "WAITING_USER"))
led = new_ledger(P, [wu])
completion(P, lp, led)
check("M PARTIAL, open_items remains", status(led, wu), ("PARTIAL", "LE-05"))
check("M pass not COMPLETE", (lp.status, lp.stage), ("WAITING_USER", "HUMAN_SYNC"))

# Test N - debt does not block
lp = Pass("LP-20261027-13", [wu], [event("LE-06", "KNOWLEDGE_DEBT", [wu])], debts=[{"origin": "LE-06", "status": "OPEN"}])
early_check(P, lp)
led = new_ledger(P, [wu])
completion(P, lp, led)
check("N unit COVERED, debt OPEN", (status(led, wu)[0], lp.debts[0]["status"]), ("COVERED", "OPEN"))

# Test O - experience does not block
lp = Pass("LP-20261027-14", [wu], [event("LE-07", "EXPERIENCE_ONLY", [wu])])
early_check(P, lp)
led = new_ledger(P, [wu])
completion(P, lp, led)
check("O unit COVERED", status(led, wu)[0], "COVERED")

# Test P - overlapping active passes
a, _ = full_pass("LP-20261027-15", "jira:INC-44")
b, _ = full_pass("LP-20261027-16", "jira:INC-44")
check("P overlap -> U-15 FAIL", ("U-15", "FAIL") in integrity_u(P, b, passes=[a, b]), True)
check("P new pass overlap -> CONFLICT", new_pass_conflict([a], ["jira:INC-44", "jira:INC-45"]),
      ("CONFLICT", ["jira:INC-44"]))

# Extra - unit-based commit example (04 §11.4)
units = ["u:A", "u:B", "u:C", "u:D", "u:E"]
lp = Pass("LP-20261027-17", units, [event("B1", "EXPERIENCE_ONLY", ["u:B"]), event("C1", "ULA_CANDIDATE", ["u:C"]),
                                    event("D1", "ULA_CANDIDATE", ["u:D"]), event("E1", "UNRESOLVED", ["u:E"])])
early_check(P, lp)
route_all(P, lp)
run_light(P, lp, "C1", [[]])
led = new_ledger(P, units)
completion(P, lp, led)
check("X unit-based statuses", [status(led, w)[0] for w in units],
      ["NOT_LEARNING_RELEVANT", "COVERED", "COVERED", "PARTIAL", "PARTIAL"])
check("X pass not COMPLETE (UNRESOLVED open)", lp.status, "WAITING_USER")
lp.status = "COMPLETE"
check("X forced COMPLETE with open items -> U-11 + U-12 FAIL",
      {"U-11", "U-12"} <= {x[0] for x in fails(integrity_u(P, lp, led))}, True)

# Extra - Light self-check
lp = Pass("LP-20261027-18", [wu], [event("LE-08", "ULA_CANDIDATE", [wu])])
early_check(P, lp)
route_all(P, lp)
check("X Light self-check FAIL once -> fixed -> COMPLETE", run_light(P, lp, "LE-08", [[5], []]), "ULA_ROUTING")
check("X Light status COMPLETE", lp.routing["LE-08"]["ULA Status"], "COMPLETE")
lp = Pass("LP-20261027-19", [wu], [event("LE-09", "ULA_CANDIDATE", [wu])])
early_check(P, lp)
route_all(P, lp)
check("X Light same self-check FAIL twice -> BLOCKED", run_light(P, lp, "LE-09", [[5], [5]]), "BLOCKED")
lp.routing["LE-09"]["ULA Status"] = "COMPLETE"
check("X Light COMPLETE with failed self-check -> U-09 FAIL", ("U-09", "FAIL") in integrity_u(P, lp), True)
lp.art["LE-09"]["LIGHT_ULA"]["sections"]["L2"] = ""
check("X Light missing L2 -> U-08 FAIL", ("U-08", "FAIL") in integrity_u(P, lp), True)

# Extra - Builder needs frozen architecture even at build stage
lp, eid = full_pass("LP-20261027-20")
lp.stage = "FULL_ULA_BUILD"
check("X Builder without Frozen Architecture refused", refused(build, P, lp, eid), True)
lp.art[eid]["CONTENT"] = {"writes": 1, "allowed": 1, "status": "COMPLETE"}
check("X CONTENT without FROZEN architecture -> U-05 FAIL", ("U-05", "FAIL") in integrity_u(P, lp), True)
lp.art[eid]["ARCHITECTURE"].update(status="FROZEN", approved_by=None)
check("X FROZEN without user approval -> U-07 FAIL", ("U-07", "FAIL") in integrity_u(P, lp), True)

# Extra - static protocol consistency
check("X modes", P.modes, ["LIGHT", "FULL"])
check("X ula statuses", P.ula_status, ["PENDING", "WAITING_USER", "IN_PROGRESS", "NEEDS_REVISION", "COMPLETE", "BLOCKED"])
check("X pass statuses", P.pass_status, ["IN_PROGRESS", "WAITING_USER", "BLOCKED", "COMPLETE", "ABANDONED"])
check("X 10 stages", len(P.stages), 10)
check("X 12 Full triggers", len(P.triggers), 12)
check("X transition table uses only known stages",
      all(r[0] in P.stages and r[2] in P.stages for r in P.transitions), True)
roles = ["LEARNING_ARCHITECT", "CONTENT_BUILDER", "LEARNING_AUDITOR"]
check("X no stage loads two role files", all(sum(r in f.split("|")[0] for r in roles) <= 1
                                              for f in P.loads.values()), True)
check("X master never in load table", any("00_MASTER" in f.split("|")[0] for f in P.loads.values()), False)
check("X Light template core = L0, L1, L2", [h.split(" ")[0] for h in P.light_core], ["L0", "L1", "L2"])
check("X routing header", P.routing_header, ["Event ID", "Mode", "Reason", "User Override", "ULA Status", "Artifact"])

report(RESULTS)
