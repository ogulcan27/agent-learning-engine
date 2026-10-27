"""Static audit of the runtime skill: router, cross references, portability, encoding, scope boundary.

Usage: run_tests.py [<skill_dir>]
Canonical ULA source copies (ula/) and the Master spec are excluded from language and marker checks.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "common"))
from harness import report, skill_dir  # noqa: E402

SKILL = skill_dir()
RESULTS = []
FILES = sorted(SKILL.rglob("*.md"))
OPERATIONAL = [f for f in FILES if "ula" not in f.relative_to(SKILL).parts and f.name != "00_MASTER_SYSTEM_SPEC.md"]
HEAD = re.compile(r"^#{1,4} ([0-9]+[A-Z]?(?:\.[0-9]+)*|[A-Z](?:\.[0-9]+)?)[.\s]", re.M)
PREFIX = r"`?((?:references/)?0[0-7](?:_[A-Z_]+\.md)?|ula/[A-Z_]+\.md)`?"
REF = re.compile(PREFIX + r" (§[0-9A-Z][0-9A-Z.]*(?:(?:–| / |, )§[0-9A-Z][0-9A-Z.]*)*)")


def check(name, actual, expected):
    RESULTS.append((name, actual == expected, actual, expected))


def text(f):
    return f.read_text(encoding="utf-8")


def headings(f):
    return {h.rstrip(".") for h in HEAD.findall(text(f))}


HEADS = {f.name[:2]: headings(f) for f in (SKILL / "references").glob("0*.md")}
HEADS |= {f"ula/{f.name}": headings(f) for f in (SKILL / "ula").glob("*.md")}


def target(token):
    return token if token.startswith("ula/") else token.replace("references/", "")[:2]


# Extra - cross references
def broken_refs():
    out = []
    for f in OPERATIONAL:
        body = text(f)
        for token, chain_ in REF.findall(body):
            for sec in re.findall(r"§([0-9A-Z][0-9A-Z.]*[0-9A-Z])|§([0-9A-Z])", chain_):
                sec = (sec[0] or sec[1]).rstrip(".")
                if sec not in HEADS[target(token)]:
                    out.append(f"{f.relative_to(SKILL).as_posix()}: {token} §{sec}")
        if f.parent.name == "references" and f.name[:2] in HEADS:
            own = f.name[:2]
            for line in body.splitlines():
                stripped = re.sub(REF.pattern, "", line)
                for sec in re.findall(r"(?<![\w`])§([0-9]+(?:\.[0-9]+)*)", stripped):
                    if sec not in HEADS[own]:
                        out.append(f"{f.relative_to(SKILL).as_posix()}: §{sec} (same file)")
    return sorted(set(out))


def missing_paths():
    out = []
    for f in FILES:
        for p in re.findall(r"(?<![\w/])((?:references|templates|ula)/[A-Za-z0-9_/]+\.md)", text(f)):
            if not (SKILL / p).exists():
                out.append(f"{f.relative_to(SKILL).as_posix()}: {p}")
    return sorted(set(out))


check("X section references resolve", broken_refs(), [])
check("X file references exist", missing_paths(), [])

# Extra - router
skill_md = text(SKILL / "SKILL.md")
router = re.findall(r"^\| (\d+) \| (.+?) \| (.+?) \| (.+?) \|$", skill_md.split("## 7. Run router", 1)[1].split("\n## ", 1)[0], re.M)
check("X router has 13 steps", [r[0] for r in router], [str(i) for i in range(1, 14)])
check("X every router step IMPLEMENTED", [r[0] for r in router if not r[3].startswith("IMPLEMENTED")], [])
check("X router step 13 -> 07 §L", "07_INTEGRITY_CHECKS.md` §L" in router[-1][2], True)
check("X manual only", ("disable-model-invocation: true" in skill_md, "user-invocable: true" in skill_md), (True, True))
hint = re.search(r'^argument-hint: "(.+)"$', skill_md, re.M).group(1)
check("X argument hint covers commands", [c for c in ("map", "concept", "library", "experiences", "debt", "integrity", "resume",
                                                      "abandon") if c not in hint], [])
check("X arguments routed", [c for c in ("map", "concept", "library", "experiences", "debt", "integrity")
                             if not re.search(rf"^\| `{c}( |`)", skill_md, re.M)], [])
check("X SKILL.md short (<= 220 lines)", len(skill_md.splitlines()) <= 220, True)
check("X final flow line", "START → COVERAGE → HUMAN SYNC → ULA → COMPLETION → MAP SYNC → KNOWLEDGE PERSISTENCE → FINAL INTEGRITY → DONE"
      in skill_md, True)
check("X DONE defined in 01", "`DONE` anlamı: Bu Learning Pass için required pipeline ve blocking integrity checks tamamlandı."
      in text(SKILL / "references" / "01_OPERATIONAL_CORE.md"), True)

# Extra - markers and stale phase numbers
check("X no NOT IMPLEMENTED YET", [f.name for f in OPERATIONAL if "NOT IMPLEMENTED YET" in text(f)], [])
stale = [f"{f.name}: {l.strip()[:60]}" for f in OPERATIONAL for l in text(f).splitlines()
         if re.search(r"Phase [2-8]", l) and not re.search(r"\*\*Status:\*\*|Phase 1 audit|Phase 8 audit|§22.1 write lock: Phase 8", l)]
check("X no stale phase numbers in behaviour text", stale, [])
check("X 07 status lists §L implemented", "§L IMPLEMENTED" in text(SKILL / "references" / "07_INTEGRITY_CHECKS.md"), True)

# Extra - portability and scope boundary
PORT = re.compile(r"[A-Za-z]:[\\/]|/Users/|/home/|scratchpad|AppData|Incubator|Claude Learning Skill|INC-\d", re.I)
check("X no absolute path / user / project value", [f"{f.relative_to(SKILL).as_posix()}: {m}" for f in FILES
                                                    for m in PORT.findall(text(f))], [])
check("X no project state in skill", sorted(p.name for p in SKILL.rglob("*") if p.name in (
    "LEARNING_STATE.md", "COVERAGE_LEDGER.md", "LEARNING_QUEUE.md", "LEARNING_CONFIG.md", "SEMANTIC_GRAPH.md", "LIBRARY_INDEX.md",
    "CONCEPT_REGISTRY.md", "docs", "passes", ".learning-write-lock")), [])
check("X only Markdown in skill", sorted({p.suffix for p in SKILL.rglob("*") if p.is_file()}), [".md"])
check("X Graphify not required", [f.name for f in OPERATIONAL if re.search(r"graphify", text(f), re.I)], [])
check("X no HTML output required", [f.name for f in OPERATIONAL if re.search(r"\.html\b", text(f), re.I)], [])
check("X personal_library_path never hard-coded", [l for f in OPERATIONAL for l in text(f).splitlines()
                                                   if re.match(r"\s*personal_library_path\s*[:=][ \t]*(?!UNCONFIGURED|<)\S", l)], [])

# Extra - encoding and language
check("X UTF-8 without BOM", [f.name for f in FILES if f.read_bytes().startswith(b"\xef\xbb\xbf")], [])
check("X decodes as UTF-8", all(isinstance(text(f), str) for f in FILES), True)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿]")
check("X no emoji", [f.name for f in OPERATIONAL if EMOJI.search(text(f))], [])
check("X operational files are Turkish", [f.name for f in OPERATIONAL if not re.search(r"[çğışöüÇĞİŞÖÜ]", text(f))], [])
long_ = [f"{f.name}: {s[:50]}" for f in (SKILL / "references" / "07_INTEGRITY_CHECKS.md", SKILL / "references" / "01_OPERATIONAL_CORE.md")
         for s in re.split(r"(?<=[.!?])\s", re.sub(r"\|.*\||```.*?```", "", text(f), flags=re.S)) if len(s.split()) > 30]
check("X ASD-STE100 sentence length <= 30 words (01, 07)", long_, [])
check("X canonical ULA copies untranslated (English)", all(re.search(r"\b(the|and)\b", text(f)) for f in (SKILL / "ula").glob("*.md")), True)

report(RESULTS)
