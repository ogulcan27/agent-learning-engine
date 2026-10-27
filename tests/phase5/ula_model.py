"""Reference model of 04_ULA_PROTOCOL used for synthetic Phase 5 tests.

Vocabularies, the stage transition table, the unit blocking table and the
token load table are parsed from 04; the routing header from the pass
template; Light core sections from the Light template. Ledger commits are
validated against the Phase 3 transition matrix parsed from 02.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase3"))
from coverage_model import Ledger, load_ledger_header, load_transitions, transition  # noqa: E402
from coverage_model import unit as cov_unit  # noqa: E402


def section(text, heading):
    level = len(heading) - len(heading.lstrip("#"))
    body = text.split(heading, 1)[1]
    stop = re.search(r"\n#{1,%d} " % level, body)
    return body[: stop.start()] if stop else body


def ticks(block):
    return [m.group(1) for m in (re.match(r"^\| `([A-Z_]+)` \|", l) for l in block.splitlines()) if m]


def rows(block):
    """Rows of the first Markdown table in block."""
    lines = block.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("|"))
    table = []
    for l in lines[start:]:
        if not l.startswith("|"):
            break
        table.append(l)
    return [[c.strip() for c in l.strip("|").split("|")] for l in table[2:]]


class Protocol:
    def __init__(self, skill: Path):
        t = (skill / "references" / "04_ULA_PROTOCOL.md").read_text(encoding="utf-8")
        self.modes = ticks(section(t, "### 2.1 ULA mode"))
        self.ula_status = ticks(section(t, "### 2.2 ULA status"))
        self.pass_status = ticks(section(t, "### 2.3 Pass status"))
        self.stages = ticks(section(t, "### 2.4 Current stage"))
        self.triggers = ticks(section(t, "### 4.1 Full triggers"))
        self.transitions = rows(section(t, "## 5. Stage transitions"))
        self.blocking = rows(section(t, "### 11.2 Unit blocking rule"))
        self.loads = {r[0]: r[1] for r in rows(section(t, "## 12. Token load rules"))}
        lt = (skill / "templates" / "LIGHT_ULA_TEMPLATE.md").read_text(encoding="utf-8")
        self.light_core = [h for h in re.findall(r"^## (L[0-2] — .+)$", lt, re.M)]
        pt = (skill / "templates" / "LEARNING_PASS_TEMPLATE.md").read_text(encoding="utf-8")
        self.routing_header = [c.strip() for c in
                               next(l for l in section(pt, "## ULA Routing").splitlines()
                                    if l.startswith("| Event ID")).strip("|").split("|")]
        self.matrix = load_transitions(skill / "references" / "02_COVERAGE_PROTOCOL.md")
        self.ledger_cols = load_ledger_header(skill / "templates" / "COVERAGE_LEDGER_TEMPLATE.md")


class Pass:
    def __init__(self, pid, scope, events, debts=(), readable=None):
        self.id, self.scope, self.events = pid, scope, {e["id"]: e for e in events}
        self.debts = list(debts)
        self.readable = readable or {w: True for w in scope}
        self.status, self.stage = "IN_PROGRESS", "HUMAN_SYNC"
        self.routing, self.art, self.revisions, self.loaded = {}, {}, {}, []
        self.selfcheck_fail = {}
        self.ledger_snapshot = None


def event(eid, disp, wus, triggers=(), override=None, uncertain=False):
    return {"id": eid, "disposition": disp, "wus": list(wus), "triggers": list(triggers),
            "override": override, "uncertain": uncertain}


# --- routing ----------------------------------------------------------------

def early_check(P, lp):
    """04 §3: no ULA candidate and no UNRESOLVED -> COMPLETION."""
    disp = [e["disposition"] for e in lp.events.values()]
    if "ULA_CANDIDATE" not in disp and "UNRESOLVED" not in disp:
        lp.stage = "COMPLETION"
    elif "ULA_CANDIDATE" in disp:
        lp.stage = "ULA_ROUTING"
    else:
        lp.stage, lp.status = "HUMAN_SYNC", "WAITING_USER"
    return lp.stage


def route(P, ev):
    """04 §4: override > Full trigger > Light default. Unknown triggers do not count."""
    real = [t for t in ev["triggers"] if t in P.triggers]
    if ev["override"]:
        return ev["override"], ("override; triggers: " + ", ".join(real)) if real else "override"
    if real:
        return "FULL", "FULL: " + ", ".join(real)
    if ev["uncertain"]:
        return None, "ROUTING UNCERTAIN"
    return "LIGHT", "no Full trigger"


def route_all(P, lp):
    for ev in lp.events.values():
        if ev["disposition"] != "ULA_CANDIDATE":
            continue
        mode, reason = route(P, ev)
        lp.routing[ev["id"]] = {"Mode": mode or "-", "Reason": reason, "User Override": ev["override"] or "-",
                                "ULA Status": "WAITING_USER" if mode is None else "PENDING", "Artifact": "-",
                                "triggers": [t for t in ev["triggers"] if t in P.triggers]}
    if any(r["ULA Status"] == "WAITING_USER" for r in lp.routing.values()):
        lp.status = "WAITING_USER"


# --- stage machine ------------------------------------------------------------

def facts(lp, eid):
    a = lp.art.get(eid, {})
    f = {"-"}
    if "PROJECT_BRIEF" in a:
        f.add("project_brief")
    arch = a.get("ARCHITECTURE")
    if arch and arch["status"] == "PROPOSED":
        f.add("proposed_architecture")
    if arch and arch["status"] == "FROZEN" and arch.get("approved_by") == "user":
        f.add("frozen_architecture")
    if "AUDIT" in a:
        f.add("audit_report")
    light = a.get("LIGHT_ULA")
    if light and all(light["sections"].get(s) for s in ("L0", "L1", "L2")):
        f.add("light_core")
    return f


def advance(P, lp, eid, trigger, extra=()):
    """Apply one row of the 04 §5 table. Missing row or requirement -> refused."""
    row = next((r for r in P.transitions if r[0] == lp.stage and r[1] == trigger), None)
    if row is None:
        raise ValueError(f"no transition {lp.stage} --{trigger}-->")
    if row[3] not in facts(lp, eid) | set(extra):
        raise ValueError(f"requirement {row[3]} missing for {lp.stage} --{trigger}-->")
    lp.stage = row[2]
    if row[4] != "-":
        lp.routing[eid]["ULA Status"] = row[4]
    lp.status = pass_status(lp)
    return lp.stage


def pass_status(lp):
    if lp.stage == "COMPLETE":
        return "COMPLETE"
    if lp.stage == "FULL_ULA_REVIEW" or any(r["ULA Status"] == "WAITING_USER" for r in lp.routing.values()):
        return "WAITING_USER"
    return "IN_PROGRESS"


def write(lp, eid, name, legit=True, **fields):
    a = lp.art.setdefault(eid, {}).setdefault(name, {"writes": 0, "allowed": 0, "status": "DRAFT"})
    a["writes"] += 1
    a["allowed"] += 1 if legit else 0
    a.update(fields)
    lp.routing[eid]["Artifact"] = f"passes/{lp.id}/ula/{eid}/"


def load(P, lp, stage):
    lp.loaded.append((stage, P.loads[stage]))


# --- Light --------------------------------------------------------------------

def run_light(P, lp, eid, selfchecks):
    """selfchecks: list of failing item numbers per attempt ([] = PASS)."""
    lp.stage = "ULA_ROUTING"
    advance(P, lp, eid, "mode LIGHT")
    load(P, lp, "LIGHT_ULA")
    write(lp, eid, "LIGHT_ULA", sections={"L0": "map", "L1": "simple", "L2": "mechanism"}, status="IN_PROGRESS")
    seen = set()
    for failing in selfchecks:
        if not failing:
            lp.art[eid]["LIGHT_ULA"]["selfcheck"] = "PASS"
            return advance(P, lp, eid, "self-check PASS")
        if seen & set(failing):
            lp.routing[eid]["ULA Status"] = "BLOCKED"
            lp.art[eid]["LIGHT_ULA"]["selfcheck"] = "FAIL"
            lp.stage = "ULA_ROUTING"
            return "BLOCKED"
        seen |= set(failing)
        advance(P, lp, eid, "self-check FAIL")
        write(lp, eid, "LIGHT_ULA")
    return lp.stage


# --- Full ---------------------------------------------------------------------

def start_full(P, lp, eid):
    lp.stage = "ULA_ROUTING"
    write(lp, eid, "PROJECT_BRIEF", status="COMPLETE")
    advance(P, lp, eid, "mode FULL")
    architect(P, lp, eid)


def architect(P, lp, eid):
    load(P, lp, "FULL_ULA_ARCHITECT")
    write(lp, eid, "ARCHITECTURE", status="PROPOSED", approved_by=None)
    advance(P, lp, eid, "architecture proposed")


def review(P, lp, eid, decision):
    if decision == "approve":
        arch = lp.art[eid]["ARCHITECTURE"]
        advance(P, lp, eid, "user approve", extra={"user_approval"})
        arch.update(status="FROZEN", approved_by="user")
    elif decision == "revise":
        advance(P, lp, eid, "user revise", extra={"user_feedback"})
        architect(P, lp, eid)
    else:
        advance(P, lp, eid, "user reject", extra={"user_decision"})


def build(P, lp, eid):
    advance(P, lp, eid, "content generated")
    load(P, lp, "FULL_ULA_BUILD")
    write(lp, eid, "CONTENT", status="COMPLETE")


def audit(P, lp, eid, recommendation):
    """04 §7.8 routing with one revision per route type."""
    load(P, lp, "FULL_ULA_AUDIT")
    write(lp, eid, "AUDIT", status="COMPLETE", last=recommendation)
    route_kind = {"DO NOT FREEZE — REVISION REQUIRED": "builder",
                  "DO NOT FREEZE — ARCHITECTURE REVISIT REQUIRED": "architecture"}.get(recommendation)
    if route_kind:
        count = lp.revisions.setdefault(eid, {}).get(route_kind, 0)
        if count >= 1:
            lp.routing[eid]["ULA Status"] = "BLOCKED"
            lp.stage = "ULA_ROUTING"
            return "BLOCKED"
        lp.revisions[eid][route_kind] = count + 1
    advance(P, lp, eid, recommendation)
    if recommendation == "DO NOT FREEZE — ARCHITECTURE REVISIT REQUIRED":
        lp.art[eid]["ARCHITECTURE"].update(status="PROPOSED", approved_by=None)
        architect(P, lp, eid)
    elif recommendation == "FREEZE AFTER MINOR FIXES":
        write(lp, eid, "CONTENT")
        advance(P, lp, eid, "minor fixes applied", extra={"minor_fix_list"})
    return lp.stage


# --- completion ----------------------------------------------------------------

def blocks(P, ev, lp):
    status = lp.routing.get(ev["id"], {}).get("ULA Status")
    for disp, cond, blocked in P.blocking:
        if disp != ev["disposition"]:
            continue
        if cond == "-" or (cond.startswith("§B") and any(d["origin"] == ev["id"] and d["status"] == "OPEN"
                                                           for d in lp.debts)) \
                or (cond == "ula_status COMPLETE" and status == "COMPLETE") \
                or (cond == "ula_status not COMPLETE" and status != "COMPLETE"):
            return blocked == "yes"
    raise ValueError(f"no blocking rule for {ev['disposition']}")


def completion(P, lp, ledger):
    """04 §11.4 unit-based commit + §11.5 pass result."""
    lp.stage = "COMPLETION"
    load(P, lp, "COMPLETION")
    for wu in lp.scope:
        mine = [e for e in lp.events.values() if wu in e["wus"]]
        learning = [e for e in mine if e["disposition"] != "IMPLEMENTATION_DETAIL"]
        open_ids = [e["id"] for e in mine if blocks(P, e, lp)]
        if not learning:
            if not lp.readable[wu]:
                continue
            new, items = "NOT_LEARNING_RELEVANT", "-"
        elif open_ids:
            new, items = "PARTIAL", "; ".join(open_ids)
        else:
            new, items = "COVERED", "-"
        transition(ledger, P.matrix, wu, new, "C", learning_pass_id=lp.id, open_items=items)
    open_events = [e for e in lp.events.values() if blocks(P, e, lp)]
    if not open_events:
        lp.stage, lp.status = "COMPLETE", "COMPLETE"
    elif any(e["disposition"] == "UNRESOLVED" for e in open_events):
        lp.stage, lp.status = "HUMAN_SYNC", "WAITING_USER"
    elif any(lp.routing[e["id"]]["ULA Status"] == "BLOCKED" for e in open_events):
        lp.stage, lp.status = "ULA_ROUTING", "BLOCKED"
    else:
        lp.stage, lp.status = "ULA_ROUTING", "WAITING_USER"


def new_ledger(P, scope, status="UNCOVERED", open_items="-", pass_id="-"):
    rows = []
    for i, wu in enumerate(scope, 1):
        r = cov_unit(i, status, pass_id)
        r.update(work_unit_id=wu, source_type="jira", open_items=open_items)
        rows.append(r)
    return Ledger(P.ledger_cols, rows)


# --- lifecycle ----------------------------------------------------------------

ACTIVE = {"IN_PROGRESS", "WAITING_USER", "BLOCKED"}


def startup(passes, arg=None):
    """04 §10.1: never start silently when an active pass exists."""
    active = [p for p in passes if p.status in ACTIVE]
    if not active:
        return "NEW"
    if arg in ("resume", "new", "abandon"):
        return arg.upper()
    return ("ASK", ["resume", "new", "abandon"], active[0].id, active[0].stage)


def resume(lp):
    """Continue from current_stage; nothing is regenerated."""
    return lp.id, lp.stage


def new_pass_conflict(passes, scope):
    overlap = {w for p in passes if p.status in ACTIVE for w in p.scope} & set(scope)
    return ("CONFLICT", sorted(overlap)) if overlap else ("OK", [])


def abandon(lp, ledger):
    lp.status = "ABANDONED"
    lp.ledger_snapshot = [dict(r) for r in ledger.rows]


# --- integrity §U -------------------------------------------------------------

def integrity_u(P, lp, ledger=None, passes=()):
    f = []
    ids = list(lp.routing)
    for eid, r in lp.routing.items():
        if r["Mode"] not in P.modes and r["ULA Status"] != "WAITING_USER":
            f.append(("U-01", "FAIL"))
        if r["ULA Status"] not in P.ula_status:
            f.append(("U-02", "FAIL"))
        if eid not in lp.events or lp.events[eid]["disposition"] != "ULA_CANDIDATE":
            f.append(("U-04", "FAIL"))
        a = lp.art.get(eid, {})
        if "LIGHT_ULA" in a and {"ARCHITECTURE", "CONTENT"} & set(a):
            f.append(("U-03", "FAIL"))
        arch = a.get("ARCHITECTURE")
        if "CONTENT" in a and not (arch and arch["status"] == "FROZEN"):
            f.append(("U-05", "FAIL"))
        if "AUDIT" in a and "CONTENT" not in a:
            f.append(("U-06", "FAIL"))
        if arch and arch["status"] == "FROZEN" and arch.get("approved_by") != "user":
            f.append(("U-07", "FAIL"))
        light = a.get("LIGHT_ULA")
        if light and not all(light["sections"].get(s) for s in ("L0", "L1", "L2")):
            f.append(("U-08", "FAIL"))
        if r["ULA Status"] == "COMPLETE" and light and light.get("selfcheck") != "PASS":
            f.append(("U-09", "FAIL"))
        if r["ULA Status"] == "COMPLETE" and r["Mode"] == "FULL" and \
                a.get("AUDIT", {}).get("last") not in ("READY TO FREEZE", "FREEZE AFTER MINOR FIXES"):
            f.append(("U-10", "FAIL"))
        if any(x["writes"] > x["allowed"] for x in a.values()):
            f.append(("U-14", "FAIL"))
        if r["ULA Status"] != "PENDING" and r["Mode"] != "-" and r["Artifact"] == "-":
            f.append(("U-16", "FAIL"))
        if r["Mode"] == "LIGHT" and r["triggers"]:
            f.append(("U-17", "WARNING"))
        if r["ULA Status"] == "BLOCKED":
            f.append(("U-18", "WARNING"))
    if len(ids) != len(set(ids)):
        f.append(("U-03", "FAIL"))
    if lp.status not in P.pass_status or lp.stage not in P.stages:
        f.append(("U-02", "FAIL"))
    if lp.status == "COMPLETE":
        if ledger and any(r["work_unit_id"] in lp.scope and r["open_items"] != "-" for r in ledger.rows):
            f.append(("U-11", "FAIL"))
        if any(r["ULA Status"] != "COMPLETE" for r in lp.routing.values()):
            f.append(("U-12", "FAIL"))
    if lp.status == "ABANDONED" and ledger and lp.ledger_snapshot is not None and \
            [dict(r) for r in ledger.rows] != lp.ledger_snapshot:
        f.append(("U-13", "FAIL"))
    for other in passes:
        if other is not lp and other.status in ACTIVE and lp.status in ACTIVE and set(other.scope) & set(lp.scope):
            f.append(("U-15", "FAIL"))
    return sorted(set(f))


def fails(f):
    return [x for x in f if x[1] == "FAIL"]
