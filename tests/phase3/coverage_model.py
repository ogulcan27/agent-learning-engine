"""Reference model of 02_COVERAGE_PROTOCOL used for synthetic Phase 3 tests.

The transition matrix and the ledger table header are parsed from the skill
files, so the tests also validate the written protocol and template.
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

STATUSES = ["UNCOVERED", "COVERED", "PARTIAL", "DEFERRED", "SKIPPED_BY_USER", "NOT_LEARNING_RELEVANT"]
SOURCE_TYPES = {"user", "jira", "phase-doc", "git", "other"}
OPEN = {"UNCOVERED", "PARTIAL", "DEFERRED"}
PASS_REQUIRED = {"COVERED", "PARTIAL", "NOT_LEARNING_RELEVANT"}


def load_transitions(protocol: Path) -> dict:
    """Parse the §9 matrix into {(from, to): trigger_code}."""
    text = protocol.read_text(encoding="utf-8")
    section = text.split("## 9. Status transitions", 1)[1].split("\n## ", 1)[0]
    rows = [l for l in section.splitlines() if l.startswith("|")]
    header = [c.strip() for c in rows[0].strip("|").split("|")][1:]
    matrix = {}
    for row in rows[2:]:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells[0] not in STATUSES and cells[0] != "(yeni satır)":
            break
        for to, code in zip(header, cells[1:]):
            code = re.sub(r"[¹²³⁴]", "", code)
            if code != "—":
                matrix[(cells[0], to)] = code
    return matrix


def load_ledger_header(template: Path) -> list:
    """Return column names of the Work Units table in the ledger template."""
    lines = template.read_text(encoding="utf-8").splitlines()
    i = lines.index("## Work Units")
    header = next(l for l in lines[i:] if l.startswith("| work_unit_id"))
    return [c.strip() for c in header.strip("|").split("|")]


@dataclass
class Ledger:
    columns: list
    rows: list = field(default_factory=list)

    def render(self) -> str:
        out = ["| " + " | ".join(self.columns) + " |", "|" + "---|" * len(self.columns)]
        for r in self.rows:
            out.append("| " + " | ".join(str(r.get(c, "-")) for c in self.columns) + " |")
        return "\n".join(out)

    @classmethod
    def parse(cls, columns: list, table: str) -> "Ledger":
        rows = []
        for line in table.splitlines()[2:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            rows.append(dict(zip(columns, cells)))
        return cls(columns, rows)

    def by_id(self, wid):
        return next(r for r in self.rows if r["work_unit_id"] == wid)


def unit(n, status="UNCOVERED", pass_id="-", source="phase-doc"):
    return {"work_unit_id": f"{source}:PLAN.md#step-{n}", "seq": str(n), "label": f"Step {n}",
            "source_type": source, "source_ref": f"PLAN.md Step {n}", "status": status,
            "discovered_at": "2026-10-27", "last_evaluated_at": "-", "learning_pass_id": pass_id,
            "open_items": "-", "notes": "-"}


def discover(ledger: Ledger, current: list) -> list:
    """Discovery Commit: add unknown units as UNCOVERED."""
    known = {r["work_unit_id"] for r in ledger.rows}
    added = [u for u in current if u["work_unit_id"] not in known]
    ledger.rows.extend(added)
    return added


def open_coverage(ledger: Ledger) -> list:
    return [r for r in ledger.rows if r["status"] in OPEN]


def skipped(ledger: Ledger) -> list:
    return [r for r in ledger.rows if r["status"] == "SKIPPED_BY_USER"]


def resolve_scope(ledger: Ledger, arg: str) -> list:
    rows = sorted(ledger.rows, key=lambda r: int(r["seq"]))
    if arg == "latest":
        return [rows[-1]]
    if arg == "catch-up":
        return [r for r in rows if r["status"] in OPEN]
    if arg == "pending":
        return [r for r in rows if r["status"] in {"DEFERRED", "PARTIAL"}]
    raise ValueError(f"ambiguous scope argument: {arg}")


def transition(ledger: Ledger, matrix: dict, wid: str, to: str, trigger: str, **fields):
    row = ledger.by_id(wid)
    code = matrix.get((row["status"], to))
    if code != trigger:
        raise ValueError(f"C-10 invalid transition {row['status']} -> {to} via {trigger}")
    row.update(status=to, last_evaluated_at="2026-10-27", **fields)


def scope_commit(ledger: Ledger, matrix: dict, selected: list, reason: str):
    """Unselected UNCOVERED -> DEFERRED. PARTIAL and DEFERRED stay."""
    chosen = {r["work_unit_id"] for r in selected}
    for r in ledger.rows:
        if r["status"] == "UNCOVERED" and r["work_unit_id"] not in chosen:
            transition(ledger, matrix, r["work_unit_id"], "DEFERRED", "S", notes=f"not selected: {reason}")


def integrity(ledger: Ledger, state=None, queue_ids=None) -> list:
    findings = []
    ids = [r["work_unit_id"] for r in ledger.rows]
    if len(ids) != len(set(ids)):
        findings.append(("C-01", "FAIL"))
    if any(r["status"] not in STATUSES for r in ledger.rows):
        findings.append(("C-02", "FAIL"))
    if any(r["source_type"] not in SOURCE_TYPES for r in ledger.rows):
        findings.append(("C-03", "FAIL"))
    seqs = [(r["source_type"], r["seq"]) for r in ledger.rows]
    if len(seqs) != len(set(seqs)):
        findings.append(("C-04", "FAIL"))
    if any(r["status"] in PASS_REQUIRED and r["learning_pass_id"] == "-" for r in ledger.rows):
        findings.append(("C-05", "FAIL"))
    if state is not None and state != rebuild_state(ledger):
        findings.append(("C-08", "WARNING"))
    if queue_ids is not None and set(queue_ids) != {r["work_unit_id"] for r in rebuild_queue(ledger)}:
        findings.append(("C-09", "WARNING"))
    open_ids = {r["work_unit_id"] for r in open_coverage(ledger)}
    if any(r["status"] in OPEN and r["work_unit_id"] not in open_ids for r in ledger.rows):
        findings.append(("C-11", "FAIL"))
    return findings


def rebuild_state(ledger: Ledger) -> dict:
    count = lambda s: sum(r["status"] == s for r in ledger.rows)
    return {"open_coverage_count": len(open_coverage(ledger)), "uncovered_count": count("UNCOVERED"),
            "deferred_count": count("DEFERRED"), "partial_count": count("PARTIAL"),
            "skipped_count": count("SKIPPED_BY_USER")}


def rebuild_queue(ledger: Ledger) -> list:
    return [r for r in ledger.rows if r["status"] in {"DEFERRED", "PARTIAL"}]
