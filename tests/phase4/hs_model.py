"""Reference model of 03_HUMAN_SYNC_PROTOCOL used for synthetic Phase 4 tests.

Vocabularies, the disposition rule table, the filter list, the event field
labels and the debt columns are parsed from the skill files, so the tests also
validate the written protocol and templates. Judgment inputs (signals, user
knowledge) come from fixtures.
"""
import re
from pathlib import Path

TICK = re.compile(r"`([A-Z_]+)`")


def section(text: str, heading: str) -> str:
    """Return the body under `heading` up to the next heading of the same or higher level."""
    level = len(heading) - len(heading.lstrip("#"))
    body = text.split(heading, 1)[1]
    stop = re.search(r"\n#{1,%d} " % level, body)
    return body[: stop.start()] if stop else body


def first_col_ticks(block: str) -> list:
    out = []
    for line in block.splitlines():
        m = re.match(r"^\| `([A-Z_]+)` \|", line)
        if m:
            out.append(m.group(1))
    return out


def table_rows(block: str) -> list:
    rows = [l for l in block.splitlines() if l.startswith("|")]
    return [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]


class Protocol:
    def __init__(self, skill: Path):
        p = (skill / "references" / "03_HUMAN_SYNC_PROTOCOL.md").read_text(encoding="utf-8")
        self.evidence = first_col_ticks(section(p, "### 7.1 Evidence status"))
        self.categories = first_col_ticks(section(p, "### 10.1 Canonical category set"))
        self.priorities = first_col_ticks(section(p, "## 11. Knowledge Priority"))
        self.gaps = first_col_ticks(section(p, "## 12. Knowledge Gap"))
        self.dispositions = first_col_ticks(section(p, "## 13. Event disposition").split("### 13.1")[0])
        self.rules = table_rows(section(p, "### 13.1 Disposition rule"))
        self.routine = [r[0] for r in table_rows(section(p, "### 8.2 Filter"))]
        sd = section(p, "### 10.1 Canonical category set")
        self.sd_signals = [s.strip() for s in
                           re.search(r"constraint, .*?\n.*?behaviour", sd, re.S).group(0).replace("\n", " ").split(",")]
        debt = section(p, "### 14.1 Debt record")
        self.debt_priority = TICK.findall(next(l for l in debt.splitlines() if l.startswith("| `priority`")))
        self.debt_status = TICK.findall(next(l for l in debt.splitlines() if l.startswith("| `debt_status`")))
        t = (skill / "templates" / "LEARNING_PASS_TEMPLATE.md").read_text(encoding="utf-8")
        block = section(t, "## Learning Events").split("```text", 1)[1].split("```", 1)[0]
        self.event_labels = [l.split(":", 1)[0] for l in block.strip().splitlines()]
        q = (skill / "templates" / "LEARNING_QUEUE_TEMPLATE.md").read_text(encoding="utf-8")
        header = next(l for l in section(q, "## B. Knowledge Debt").splitlines() if l.startswith("| debt_id"))
        self.debt_columns = [c.strip() for c in header.strip("|").split("|")]


def is_event(proto: Protocol, change: dict) -> bool:
    """§8.2: routine kinds are never events; others need a yes on q1 or q2."""
    return change["kind"] not in proto.routine and (change.get("q1") or change.get("q2"))


def category(proto: Protocol, change: dict) -> str:
    """§10.1 order: System Design first, DSA only on real computational need."""
    if set(change.get("sd_signals", [])) & set(proto.sd_signals):
        return "SYSTEM_DESIGN"
    if change.get("computational_need"):
        return "DSA"
    return change.get("category", "OTHER")


def priority(change: dict) -> str:
    if change.get("priority"):
        return change["priority"]
    return "MUST_UNDERSTAND" if change.get("must_signals") else "USEFUL_TO_KNOW"


def gap(change: dict, prio: str) -> str:
    """§12: never guess user knowledge."""
    if prio == "IMPLEMENTATION_DETAIL":
        return "-"
    if change.get("user_knowledge") in ("stated_known", "prior_artifact"):
        return "KNOWN"
    if change.get("user_knowledge") == "stated_unknown" or change.get("gap_signals"):
        return "GAP"
    return "UNKNOWN"


def disposition(proto: Protocol, prio: str, gp: str, evidence: str) -> str:
    """§13.1: first matching row wins."""
    core_unresolved = evidence.startswith("UNRESOLVED")
    for p, g, ev, disp in proto.rules:
        if ev.startswith("event"):
            if core_unresolved:
                return disp
            continue
        if p in (prio, "any") and g in (gp, "any"):
            return disp
    raise ValueError(f"no disposition rule for {prio}/{gp}")


def build_pass(proto: Protocol, pass_id: str, scope: list, changes: list, today="2026-10-27",
               overrides=None) -> dict:
    """Human Sync (one per scope) + extraction + priority + disposition + debt + proposal."""
    overrides = overrides or {}
    topics, suppressed = {}, []
    for ch in changes:
        if is_event(proto, ch):
            topics.setdefault(ch["topic"], []).append(ch)
        else:
            suppressed.append(ch)
    events, debts = [], []
    for n, (topic, group) in enumerate(topics.items(), 1):
        ch = group[0]
        prio = priority(ch)
        gp = gap(ch, prio)
        ev = {"Event ID": f"LE-{pass_id}-{n:02d}", "Category": category(proto, ch),
              "Work Units": "; ".join(dict.fromkeys(c["wu"] for c in group)), "Problem": topic,
              "Why It Matters": "-", "Decision / Mechanism": ch.get("mechanism", "-"),
              "Reusable Signal": ch.get("signal", "-"), "Evidence Status": ch["evidence"],
              "Knowledge Priority": prio, "Knowledge Gap": gp,
              "Disposition": disposition(proto, prio, gp, ch["evidence"]), "Open Question": "-"}
        if overrides.get(topic) == "defer" and ev["Disposition"] == "ULA_CANDIDATE":
            ev["Disposition"] = "KNOWLEDGE_DEBT"
        events.append(ev)
        if ev["Disposition"] == "KNOWLEDGE_DEBT":
            debts.append({"debt_id": f"KD-{pass_id}-{len(debts) + 1:02d}", "concept": ch.get("concept", topic),
                          "originating_event_id": ev["Event ID"], "work_unit_ids": ev["Work Units"],
                          "one_sentence_explanation": "-", "why_it_matters": "-",
                          "priority": "NOW" if prio == "MUST_UNDERSTAND" else "LATER",
                          "debt_status": "OPEN", "created_at": today, "concept_home": "UNASSIGNED"})
    return {"id": pass_id, "scope": scope, "human_sync_count": 1, "events": events, "debts": debts,
            "suppressed": len(suppressed), "proposal": proposal(scope, events, changes)}


def proposal(scope: list, events: list, changes: list) -> dict:
    """§15: per-unit coverage outcome proposal."""
    out = {}
    for wu in scope:
        mine = [e for e in events if wu in e["Work Units"].split("; ")]
        readable = all(c["evidence"] != "UNREADABLE" for c in changes if c["wu"] == wu)
        open_ids = [e["Event ID"] for e in mine if e["Disposition"] in ("ULA_CANDIDATE", "UNRESOLVED")]
        learning = [e for e in mine if e["Disposition"] != "IMPLEMENTATION_DETAIL"]
        if not learning:
            out[wu] = ("NOT_LEARNING_RELEVANT", "-") if readable else (None, "-")
        elif open_ids:
            out[wu] = ("PARTIAL", "; ".join(open_ids))
        else:
            out[wu] = ("COVERED", "-")
    return out


def render_events(proto: Protocol, events: list) -> str:
    blocks = []
    for e in events:
        lines = [f"{label}: {e.get(label, '-')}" for label in proto.event_labels]
        blocks.append(f"### {e['Event ID']}\n\n```text\n" + "\n".join(lines) + "\n```")
    return "\n\n".join(blocks)


def parse_events(text: str) -> list:
    events = []
    for block in re.findall(r"```text\n(.*?)```", text, re.S):
        events.append(dict(l.split(": ", 1) for l in block.strip().splitlines()))
    return events


def render_debts(proto: Protocol, debts: list) -> str:
    out = ["| " + " | ".join(proto.debt_columns) + " |", "|" + "---|" * len(proto.debt_columns)]
    out += ["| " + " | ".join(d.get(c, "") for c in proto.debt_columns) + " |" for d in debts]
    return "\n".join(out)


def parse_debts(proto: Protocol, table: str) -> list:
    return [dict(zip(proto.debt_columns, r)) for r in table_rows(table)]


def integrity(proto: Protocol, events: list, debts: list, scope: list, ula_list=None,
              partial_open_items=None) -> list:
    """07 §E checks."""
    f = []
    ids = [e.get("Event ID", "") for e in events]
    known = set(ids)
    if len(ids) != len(known):
        f.append(("E-01", "FAIL"))
    for e in events:
        wus = [w for w in e.get("Work Units", "").split("; ") if w and w != "-"]
        if not wus or any(w not in scope for w in wus):
            f.append(("E-02", "FAIL"))
        if e.get("Category", "").split(" ")[0] not in proto.categories:
            f.append(("E-03", "FAIL"))
        if e.get("Knowledge Priority") not in proto.priorities:
            f.append(("E-04", "FAIL"))
        if e.get("Disposition") not in proto.dispositions:
            f.append(("E-05", "FAIL"))
        if e.get("Knowledge Priority") == "IMPLEMENTATION_DETAIL" and \
                e.get("Disposition") in ("ULA_CANDIDATE", "KNOWLEDGE_DEBT"):
            f.append(("E-09", "FAIL"))
        status = e.get("Evidence Status", "")
        if status.split(" ")[0] not in proto.evidence:
            f.append(("E-12", "FAIL"))
        if status.startswith("VERIFIED") and not re.search(r"\(\w[\w-]*:[^)]+\)", status):
            f.append(("E-11", "FAIL"))
        if e.get("Disposition") == "KNOWLEDGE_DEBT" and \
                e.get("Event ID") not in {d.get("originating_event_id") for d in debts}:
            f.append(("E-13", "FAIL"))
        if e.get("Disposition") == "ULA_CANDIDATE" and e.get("Knowledge Gap") != "GAP":
            f.append(("E-14", "WARNING"))
    ula = ula_list if ula_list is not None else [e["Event ID"] for e in events if e.get("Disposition") == "ULA_CANDIDATE"]
    if any(i not in known for i in ula):
        f.append(("E-06", "FAIL"))
    for d in debts:
        if d.get("originating_event_id", "") not in known:
            f.append(("E-07", "FAIL"))
        if d.get("priority") not in proto.debt_priority or d.get("debt_status") not in proto.debt_status:
            f.append(("E-12", "FAIL"))
    debt_ids = [d.get("debt_id") for d in debts]
    if len(debt_ids) != len(set(debt_ids)):
        f.append(("E-08", "FAIL"))
    open_concepts = [d.get("concept") for d in debts if d.get("debt_status") == "OPEN"]
    if len(open_concepts) != len(set(open_concepts)):
        f.append(("E-15", "WARNING"))
    for item in (partial_open_items or "").split("; "):
        if item and item != "-" and item not in known:
            f.append(("E-10", "FAIL"))
    return sorted(set(f))


def fails(findings: list) -> list:
    return [x for x in findings if x[1] == "FAIL"]
