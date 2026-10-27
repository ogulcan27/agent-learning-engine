"""Mutation checks: break one protocol rule in a temporary skill copy; the suite must catch it.

A mutation is caught when every expected suite reports at least one failing test.
The skill under test is never modified.
"""
import re
import shutil
import tempfile
from pathlib import Path

import run_all

R03, R04, R05 = "references/03_HUMAN_SYNC_PROTOCOL.md", "references/04_ULA_PROTOCOL.md", "references/05_MINDMAP_PROTOCOL.md"
R06, R07 = "references/06_KNOWLEDGE_PERSISTENCE.md", "references/07_INTEGRITY_CHECKS.md"

# (id, description, [(file, regex, replacement)], expected failing suites)
MUTATIONS = [
    ("P4-M1", "03 ULA_CANDIDATE disposition row removed",
     [(R03, r"^\| MUST_UNDERSTAND \| GAP \| yeterli \| ULA_CANDIDATE \|\n", "")], ["phase4", "integration"]),
    ("P5-M1", "04 review gate removed (architecture proposed -> FULL_ULA_BUILD)",
     [(R04, r"^(\| FULL_ULA_ARCHITECT \| architecture proposed \|) FULL_ULA_REVIEW ", r"\1 FULL_ULA_BUILD ")], ["phase5"]),
    ("P5-M2", "04 open ULA event no longer blocks the unit",
     [(R04, r"^(\| ULA_CANDIDATE \| ula_status not COMPLETE \|) yes \|$", r"\1 no |")], ["phase5"]),
    ("P5-M3", "04 Builder without frozen architecture",
     [(R04, r"^(\| FULL_ULA_REVIEW \| user approve \| FULL_ULA_BUILD \|) user_approval ", r"\1 - "),
      (R04, r"^(\| FULL_ULA_BUILD \| content generated \| FULL_ULA_AUDIT \|) frozen_architecture ", r"\1 - ")], ["phase5"]),
    ("P6-M1", "07 M-04 orphan edge check removed", [(R07, r"^\| M-04 \|.*\n", "")], ["phase6"]),
    ("P6-M2", "07 M-08 hierarchy cycle check removed", [(R07, r"^\| M-08 \|.*\n", "")], ["phase6"]),
    ("P6-M3", "05 §7.1 idempotent merge broken (UNION -> APPEND)",
     [(R05, r"^\| source_event_ids \| UNION \|$", "| source_event_ids | APPEND |"),
      (R05, r"^\| project_appearances \| UNION \|$", "| project_appearances | APPEND |")], ["phase6"]),
    ("P7-M1", "06 §7 NAME resolution row removed (duplicate Concept Home prevention)",
     [(R06, r"^\| NAME \|.*\n", "")], ["phase7", "integration"]),
    ("P7-M2", "06 §20 RESOLVED guard removed + 07 P-12 removed",
     [(R06, r"^(\| OPEN \| RESOLVED \|) .+ \|$", r"\1 - |"), (R07, r"^\| P-12 \|.*\n", "")], ["phase7"]),
    ("P7-M3", "06 §22 atomic write removed (SEQUENTIAL, no rollback)",
     [(R06, r"^\| write_mode \| ALL_OR_NOTHING \|$", "| write_mode | SEQUENTIAL |"),
      (R06, r"^\| on_write_error \| RESTORE_PRE_IMAGES \|$", "| on_write_error | NONE |")], ["phase7"]),
    ("P8-M1", "07 L-04 removed (fake RESOLVED debt accepted)", [(R07, r"^\| L-04 \|.*\n", "")], ["integration"]),
    ("P8-M2", "06 §22.1 on_existing BLOCKED -> OVERWRITE (concurrent write)",
     [(R06, r"^\| on_existing \| BLOCKED \|$", "| on_existing | OVERWRITE |")], ["integration"]),
    ("P8-M3", "06 §22.1 stale_lock USER_DECISION -> AUTO_REMOVE",
     [(R06, r"^\| stale_lock \| USER_DECISION \|$", "| stale_lock | AUTO_REMOVE |")], ["integration"]),
    ("P8-M4", "07 L-08 WARNING -> FAIL (coverage independence broken)",
     [(R07, r"^(\| L-08 \|.*\|) WARNING (\|.*\|)$", r"\1 FAIL \2")], ["integration"]),
    ("P8-M5", "07 §L.1 COVERAGE_LEDGER marked DERIVED",
     [(R07, r"^(\| `COVERAGE_LEDGER` \|) AUTHORITATIVE (\|.*\|) NO \|$", r"\1 DERIVED \2 YES |")], ["integration"]),
    ("P8-M8", "07 L-20 removed (repair trusted without CHECK 2)", [(R07, r"^\| L-20 \|.*\n", "")], ["integration"]),
    ("P8-M6", "config template hard-codes a personal library path",
     [("templates/LEARNING_CONFIG_TEMPLATE.md", r"^personal_library_path: UNCONFIGURED$", "personal_library_path: D:/Users/me/library")],
     ["static"]),
    ("P8-M7", "07 §L.6 renumbered; SKILL.md pointer becomes stale",
     [(R07, r"^### L\.6 Command$", "### L.9 Command")], ["static"]),
]


def mutate(skill, rel, pattern, repl):
    f = skill / rel
    text, n = re.subn(pattern, repl, f.read_text(encoding="utf-8"), flags=re.M)
    assert n == 1, f"mutation target not unique in {rel}: {pattern} ({n})"
    f.write_text(text, encoding="utf-8")


def main(skill):
    ok = True
    for mid, desc, edits, expected in MUTATIONS:
        tmp = Path(tempfile.mkdtemp(prefix=f"mut_{mid}_"))
        copy = tmp / "stay-in-the-loop"
        shutil.copytree(skill, copy)
        for edit in edits:
            mutate(copy, *edit)
        results = {name: run_all.run_suite(name, copy) for name in run_all.SUITES}
        shutil.rmtree(tmp, ignore_errors=True)
        hit = {n: r for n, r in results.items() if r[2]}
        caught = all(n in hit for n in expected)
        ok &= caught
        print(f"{mid:<6} {'CAUGHT' if caught else 'MISSED'}  {desc}")
        print(f"       " + ", ".join(f"{n} {p}/{t}" for n, (p, t, _) in hit.items()) + f"; e.g. {next(iter(hit.values()))[2][:2] if hit else []}")
    return ok
