"""Reference model of 06 §22.1 personal library write lock.

Rules (acquire, on_existing, stale_lock, release, on_release_error) are parsed from 06.
"""
import os
import re
import shutil
from pathlib import Path

LOCK_DIR = ".learning-write-lock"


def load_rules(skill: Path) -> dict:
    """Parse the §22.1 rule table into {rule: value}."""
    t = (skill / "references" / "06_KNOWLEDGE_PERSISTENCE.md").read_text(encoding="utf-8")
    sec = t.split("### 22.1 Personal library write lock", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\| (\w+) \| (.+?) \|$", sec, re.M)
    return {k: v.strip("`") for k, v in rows if k not in ("rule",)}


def lock_fields(skill: Path) -> list:
    t = (skill / "references" / "06_KNOWLEDGE_PERSISTENCE.md").read_text(encoding="utf-8")
    sec = t.split("`LOCK.md` alanları:", 1)[1].split("```", 2)[1]
    return re.findall(r"^(\w+):", sec, re.M)


def path(library: Path) -> Path:
    return Path(library) / LOCK_DIR


def read(library: Path):
    f = path(library) / "LOCK.md"
    if not f.exists():
        return None
    return dict(re.findall(r"^(\w+):\s+(.+)$", f.read_text(encoding="utf-8"), re.M))


def acquire(rules: dict, library: Path, meta: dict):
    """Returns ('ACQUIRED', meta) or ('BLOCKED', existing_meta)."""
    d = path(library)
    Path(library).mkdir(parents=True, exist_ok=True)
    if rules["acquire"] == "EXCLUSIVE_CREATE":
        try:
            os.mkdir(d)
        except FileExistsError:
            if rules["on_existing"] == "BLOCKED":
                return "BLOCKED", read(library)
            shutil.rmtree(d)
            os.mkdir(d)
    else:
        d.mkdir(exist_ok=True)
    body = "\n".join(f"{k}: {v}" for k, v in meta.items())
    (d / "LOCK.md").write_text(f"# Learning Write Lock\n\n{body}\n", encoding="utf-8")
    return "ACQUIRED", meta


def release(rules: dict, library: Path, lock_id: str, fail=False) -> str:
    """Remove only our own lock. A failing release yields the protocol's on_release_error value."""
    cur = read(library)
    if cur is None or cur.get("lock_id") != lock_id:
        return "NOT_OWNER"
    if fail:
        return rules["on_release_error"]
    shutil.rmtree(path(library))
    return "RELEASED"


def stale(rules: dict, library: Path, decision=None) -> str:
    """Existing lock found at startup. decision: None / 1 = keep, 2 = user confirms stale."""
    if read(library) is None:
        return "NO_LOCK"
    if rules["stale_lock"] == "USER_DECISION" and decision != 2:
        return "WAITING_USER" if decision is None else "KEPT"
    shutil.rmtree(path(library))
    return "REMOVED"
