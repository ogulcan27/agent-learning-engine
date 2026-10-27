"""Reference model of 06_KNOWLEDGE_PERSISTENCE used for synthetic Phase 7 tests.

Parsed from skill files: ID prefixes (06 §4), routing (§5), resolution steps (§7),
section mapping (§8.1), provenance labels (§8.2), update outcomes (§9), home modes (§13.1),
persistence statuses (§19), debt transitions (§20), atomic rules (§22), DSA patterns (§17.3);
enabled checks (07 §P); template headings and columns. Judgment inputs (meaning
equivalence, section comparison, project experience) come from fixtures.
State is written as Markdown files under temporary fixture directories and parsed back.
"""
import copy
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase6"))
import graph_model as gm  # noqa: E402

TODAY = "2026-10-27"
EVIDENCE_RANK = {"UNRESOLVED": 0, "ASSUMED": 1, "INFERRED": 2, "VERIFIED": 3}
VERSIONED_ID = ("Canonical Name", "Aliases", "Short Meaning", "Status")


def tables(block):
    out, cur = [], []
    for line in block.splitlines() + [""]:
        if line.startswith("|"):
            cur.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif cur:
            out.append(cur)
            cur = []
    return out


def rows(block, n=0):
    return tables(block)[n][2:]


def header(block, n=0):
    return tables(block)[n][0]


def ticks(block):
    return [m.group(1) for m in (re.match(r"^\| `([A-Za-z_\- ]+)` \|", l) for l in block.splitlines()) if m]


def kv_block(block):
    body = block.split("```text", 1)[1].split("```", 1)[0]
    return {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in body.strip().splitlines())}


class Protocol:
    def __init__(self, skill: Path):
        sec = gm.section
        t = (skill / "references" / "06_KNOWLEDGE_PERSISTENCE.md").read_text(encoding="utf-8")
        self.ids = {r[0].strip("`"): re.match(r"`([A-Z]+-)`", r[1]).group(1) for r in rows(sec(t, "## 4. Identity"))}
        self.routing = [dict(zip(header(sec(t, "## 5. Persistence routing")), r)) for r in rows(sec(t, "## 5. Persistence routing"))]
        self.resolution = [r[0] for r in rows(sec(t, "## 7. Concept resolution"))]
        self.mapping = rows(sec(t, "### 8.1 Source rule"), 1)
        self.provenance = ticks(sec(t, "### 8.2 Provenance"))
        self.outcomes = {r[0]: r[3] for r in rows(sec(t, "## 9. Update = delta"))}
        self.modes = ticks(sec(t, "### 13.1 Home mode"))
        self.status = ticks(sec(t, "## 19. Persistence status"))
        self.debt_tx = {(r[0], r[1]): r[2] for r in rows(sec(t, "## 20. Knowledge Debt lifecycle"))}
        self.atomic = {r[0]: r[1] for r in rows(sec(t, "## 22. Atomic write"))}
        self.patterns = ticks(sec(t, "### 17.3 Universal DSA pattern vocabulary"))
        i = (skill / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8")
        self.checks = set(re.findall(r"^\| (P-\d\d) \|", sec(i, "## P. Knowledge Persistence Integrity"), re.M))
        tp = skill / "templates"
        h = (tp / "CONCEPT_HOME_TEMPLATE.md").read_text(encoding="utf-8")
        heads = re.findall(r"^## (.+)$", h, re.M)
        self.content = heads[heads.index("L0 — Map / Context"): heads.index("Reference") + 1]
        self.identity_keys = list(kv_block(sec(h, "## Identity")))
        self.app_cols = header(sec(h, "## Project Appearances"))
        self.src_cols = header(sec(h, "## Source Artifacts"))
        self.hist_cols = header(sec(h, "## Change History"))
        self.local_keys = list(kv_block(sec(h, "## Local Pointer")))
        self.pointer_keys = list(kv_block((tp / "CONCEPT_POINTER_TEMPLATE.md").read_text(encoding="utf-8")))
        n = (tp / "EXPERIENCE_NOTE_TEMPLATE.md").read_text(encoding="utf-8")
        self.note_id_keys = list(kv_block(sec(n, "## Identity")))
        self.note_exp_keys = list(kv_block(sec(n, "## Experience")))
        self.note_dsa_keys = list(kv_block(sec(n, "## DSA Detail")))
        self.ev_cols = header(sec(n, "## Evidence"))
        d = (tp / "DECISION_RECORD_TEMPLATE.md").read_text(encoding="utf-8")
        self.dr_id_keys = list(kv_block(sec(d, "## Identity")))
        self.adr_keys = list(kv_block(sec(d, "## ADR")))
        self.dsadr_keys = list(kv_block(sec(d, "## DSA_DR")))
        self.reg_cols = header(sec((tp / "CONCEPT_REGISTRY_TEMPLATE.md").read_text(encoding="utf-8"), "## Concepts"))
        self.idx_cols = header(sec((tp / "PERSONAL_LIBRARY_INDEX_TEMPLATE.md").read_text(encoding="utf-8"), "## Concepts"))
        self.sd_cols = header(sec((tp / "SYSTEM_DESIGN_EXPERIENCE_MAP_TEMPLATE.md").read_text(encoding="utf-8"), "## Experiences"))
        self.dsa_cols = header(sec((tp / "DSA_EXPERIENCE_MAP_TEMPLATE.md").read_text(encoding="utf-8"), "## Experiences"))
        q = (tp / "LEARNING_QUEUE_TEMPLATE.md").read_text(encoding="utf-8")
        self.debt_cols = next(r for r in tables(sec(q, "## B. Knowledge Debt")) if r[0][0] == "debt_id")[0]
        p = (tp / "LEARNING_PASS_TEMPLATE.md").read_text(encoding="utf-8")
        self.ms_cols = header(sec(p, "## Map Sync"))
        self.kp_cols = header(sec(p, "## Knowledge Persistence"))
        c = (tp / "LEARNING_CONFIG_TEMPLATE.md").read_text(encoding="utf-8")
        self.config_keys = re.findall(r"^(\w+): ", c, re.M)
        self.gp = gm.Protocol(skill)


# --- markdown rendering --------------------------------------------------------

def md_table(cols, items):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    return "\n".join(out + ["| " + " | ".join(str(i.get(c, "-")) for c in cols) + " |" for i in items])


def parse_table(block, cols):
    t = tables(block)
    return [dict(zip(cols, r)) for r in t[0][2:]] if t else []


def kv_render(d):
    width = max(len(k) for k in d) + 2
    return "```text\n" + "\n".join(f"{k + ':':<{width}}{v}" for k, v in d.items()) + "\n```"


def split(v):
    return [] if v in ("", "-") else v.split("; ")


def join(xs):
    return "; ".join(xs) if xs else "-"


def render_home(P, h):
    out = [f"# Concept Home — {h['id']['Canonical Name']}", "", "## Identity", "", kv_render(h["id"]), "",
           "## System Position", "", h["position"], ""]
    for s in P.content:
        out += [f"## {s}", "", h["sections"][s], ""]
    out += ["## Project Appearances", "", md_table(P.app_cols, h["appearances"]), "",
            "## Source Artifacts", "", md_table(P.src_cols, h["sources"]), "",
            "## Change History", "", md_table(P.hist_cols, h["history"]), ""]
    if h.get("local"):
        out += ["## Local Pointer", "", kv_render(h["local"]), ""]
    return "\n".join(out)


def parse_home(P, text):
    parts = {p.split("\n", 1)[0]: (p.split("\n", 1) + [""])[1].strip() for p in text.split("\n## ")[1:]}
    return {"id": kv_block(parts["Identity"]), "position": parts["System Position"],
            "sections": {s: parts[s] for s in P.content},
            "appearances": parse_table(parts["Project Appearances"], P.app_cols),
            "sources": parse_table(parts["Source Artifacts"], P.src_cols),
            "history": parse_table(parts["Change History"], P.hist_cols),
            "local": kv_block(parts["Local Pointer"]) if "Local Pointer" in parts else None}


def render_pointer(ptr):
    return f"# Concept Pointer — {ptr['Canonical Name']}\n\n## Pointer\n\n{kv_render(ptr)}\n"


def render_note(P, n):
    out = [f"# Experience Note — {n['title']}", "", "## Identity", "", kv_render(n["id"]), "",
           "## Experience", "", kv_render(n["exp"]), ""]
    if n.get("dsa"):
        out += ["## DSA Detail", "", kv_render(n["dsa"]), ""]
    out += ["## Evidence", "", md_table(P.ev_cols, n["evidence"]), ""]
    return "\n".join(out)


def parse_note(P, text):
    parts = {p.split("\n", 1)[0]: p.split("\n", 1)[1] for p in text.split("\n## ")[1:]}
    return {"title": text.split("\n", 1)[0].split("— ", 1)[1], "id": kv_block(parts["Identity"]),
            "exp": kv_block(parts["Experience"]), "dsa": kv_block(parts["DSA Detail"]) if "DSA Detail" in parts else None,
            "evidence": parse_table(parts["Evidence"], P.ev_cols), "raw": text}


def render_dr(P, d):
    body = "ADR" if d["id"]["Type"] == "ADR" else "DSA_DR"
    return (f"# Decision Record — {d['title']}\n\n## Identity\n\n{kv_render(d['id'])}\n\n"
            f"## {body}\n\n{kv_render(d['body'])}\n")


def doc(title, sec, cols, items):
    return f"# {title}\n\n## {sec}\n\n{md_table(cols, items)}\n"


def replace_section(text, heading, body):
    """Replace the body of '## heading'; every other section stays byte-identical."""
    start = text.index(f"## {heading}\n")
    end = text.find("\n## ", start + 1)
    tail = "" if end < 0 else "\n" + text[end + 1:]
    return text[:start] + f"## {heading}\n\n{body}\n" + tail


# --- storage -------------------------------------------------------------------

class Store:
    """Project root (P:) and optional personal library root (L:). Writes can be made to fail."""

    def __init__(self, project: Path, library: Path):
        self.roots = {"P": project, "L": library}
        self.fail_on = set()

    def path(self, key):
        r, rel = key.split(":", 1)
        return self.roots[r] / rel

    def read(self, key, overlay=None):
        if overlay is not None and key in overlay:
            return overlay[key]
        p = self.path(key)
        return p.read_text(encoding="utf-8") if p.exists() else None

    def write(self, key, text):
        if key in self.fail_on:
            raise OSError(f"injected write failure: {key}")
        p = self.path(key)
        if text is None:
            p.unlink(missing_ok=True)
            return
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def keys(self, prefix, overlay=None):
        r, rel = prefix.split(":", 1)
        base = self.roots[r] / rel
        found = {f"{r}:{rel}{p.name}" for p in base.glob("*.md")} if base.exists() else set()
        for k, v in (overlay or {}).items():
            if k.startswith(prefix) and "/" not in k[len(prefix):]:
                (found.add if v is not None else found.discard)(k)
        return sorted(k for k in found if self.read(k, overlay) is not None)

    def snapshot(self):
        return {f"{r}:{p.relative_to(root).as_posix()}": p.read_bytes() for r, root in self.roots.items() if root.exists()
                for p in root.rglob("*") if p.is_file()}


REG, IDX = "L:registry/CONCEPT_REGISTRY.md", "L:LIBRARY_INDEX.md"
SDMAP, DSAMAP = "L:experience-maps/SYSTEM_DESIGN_EXPERIENCE_MAP.md", "L:experience-maps/DSA_EXPERIENCE_MAP.md"
GRAPH, QUEUE = "P:maps/SEMANTIC_GRAPH.md", "P:state/LEARNING_QUEUE.md"
ORDER = ("L:concepts/", REG, "L:experience-maps/", "P:concepts/", "P:experiences/EX-", "P:experiences/DR-",
         GRAPH, QUEUE, "P:passes/")


def pass_key(lp):
    return f"P:passes/{lp}/LEARNING_PASS.md"


class State:
    """Parsed project + personal state, optionally with a candidate overlay."""

    @classmethod
    def load(cls, P, store, ctx, overlay=None):
        s, rd = cls(), (lambda k: store.read(k, overlay))
        s.lib = ctx["config"]["personal_library_path"] != "UNCONFIGURED"
        s.registry = parse_table(gm.section(rd(REG), "## Concepts"), P.reg_cols) if rd(REG) else []
        s.homes = {k.split("/")[-1][:-3]: parse_home(P, rd(k)) for k in store.keys("L:concepts/", overlay)}
        s.homes_raw = {k.split("/")[-1][:-3]: rd(k) for k in store.keys("L:concepts/", overlay)}
        s.pointers, s.local = {}, {}
        for k in store.keys("P:concepts/", overlay):
            text, cid = rd(k), k.split("/")[-1][:-3]
            if text.startswith("# Concept Pointer"):
                s.pointers[cid] = (kv_block(text), text)
            else:
                s.local[cid] = parse_home(P, text)
        s.notes = {k.split("/")[-1][:-3]: parse_note(P, rd(k)) for k in store.keys("P:experiences/", overlay)
                   if k.split("/")[-1].startswith("EX-")}
        s.drs = {k.split("/")[-1][:-3]: rd(k) for k in store.keys("P:experiences/", overlay)
                 if k.split("/")[-1].startswith("DR-")}
        s.sd = parse_table(gm.section(rd(SDMAP), "## Experiences"), P.sd_cols) if rd(SDMAP) else []
        s.dsa = parse_table(gm.section(rd(DSAMAP), "## Experiences"), P.dsa_cols) if rd(DSAMAP) else []
        s.index = parse_table(gm.section(rd(IDX), "## Concepts"), P.idx_cols) if rd(IDX) else []
        s.graph = gm.Graph.parse(P.gp, rd(GRAPH)) if rd(GRAPH) else gm.Graph()
        s.debts = parse_table(gm.section(rd(QUEUE), "## B. Knowledge Debt"), P.debt_cols) if rd(QUEUE) else []
        s.raw = {QUEUE: rd(QUEUE)}
        s.passes = {}
        for lp in ctx["passes"]:
            text = rd(pass_key(lp))
            if text:
                s.raw[pass_key(lp)] = text
                s.passes[lp] = {"ms": parse_table(gm.section(text, "## Map Sync"), P.ms_cols),
                                "kp": parse_table(gm.section(text, "## Knowledge Persistence"), P.kp_cols)}
        return s

    def ms(self, lp, eid):
        return next((r for r in self.passes[lp]["ms"] if r["Event ID"] == eid), None)

    def kp(self, lp, eid):
        return next((r for r in self.passes[lp]["kp"] if r["Event ID"] == eid), None)

    def known_ids(self):
        return {r["Concept ID"] for r in self.registry} | set(self.local)


def render_state_files(P, s, ctx):
    """Every persisted file of the state, keyed by store key."""
    out = {}
    if s.lib:
        out[REG] = doc("Concept Registry", "Concepts", P.reg_cols, s.registry)
        for cid, h in s.homes.items():
            out[f"L:concepts/{cid}.md"] = render_home(P, h)
        out[SDMAP] = doc("System Design Experience Map", "Experiences", P.sd_cols, s.sd)
        out[DSAMAP] = doc("DSA Experience Map", "Experiences", P.dsa_cols, s.dsa)
    for cid, (ptr, _) in s.pointers.items():
        out[f"P:concepts/{cid}.md"] = render_pointer(ptr)
    for cid, h in s.local.items():
        out[f"P:concepts/{cid}.md"] = render_home(P, h)
    for xid, n in s.notes.items():
        out[f"P:experiences/{xid}.md"] = render_note(P, n)
    for did, text in s.drs.items():
        out[f"P:experiences/{did}.md"] = text
    out[GRAPH] = s.graph.render(P.gp)
    raw = getattr(s, "raw", {})
    out[QUEUE] = (replace_section(raw[QUEUE], "B. Knowledge Debt", md_table(P.debt_cols, s.debts)) if raw.get(QUEUE)
                  else doc("Learning Queue", "B. Knowledge Debt", P.debt_cols, s.debts))
    for lp, t in s.passes.items():
        text = raw.get(pass_key(lp)) or f"# Learning Pass {lp}\n\n## Map Sync\n\n\n## Knowledge Persistence\n\n"
        text = replace_section(text, "Map Sync", md_table(P.ms_cols, t["ms"]))
        out[pass_key(lp)] = replace_section(text, "Knowledge Persistence", md_table(P.kp_cols, t["kp"]))
    return out


def delta(store, files):
    return {k: v for k, v in files.items() if store.read(k) != v}


# --- protocol steps ------------------------------------------------------------

def new_id(P, kind, taken, rng):
    while True:
        x = f"{P.ids[kind]}{rng.getrandbits(32):08x}"
        if x not in taken:
            return x


def route(P, ev):
    for r in P.routing:
        if r["disposition"] != ev["disposition"]:
            continue
        c = r["condition"]
        if (c == "-" or (c == "reusable signal var" and ev.get("reusable"))
                or (c == "reusable signal yok" and not ev.get("reusable"))
                or (c == "ula_status COMPLETE" and ev.get("ula_status") == "COMPLETE")
                or (c == "ula_status not COMPLETE" and ev.get("ula_status") != "COMPLETE")):
            return r
    return {"concept_home": "NO", "experience_note": "NO", "status": "BLOCKED"}


def registry_view(s, mode):
    if mode == "LOCAL_TEMPORARY":
        return [{"Concept ID": cid, "Canonical Name": h["id"]["Canonical Name"], "Aliases": h["id"]["Aliases"],
                 "Short Meaning": h["id"]["Short Meaning"], "Home": f"concepts/{cid}.md", "Status": h["id"]["Status"]}
                for cid, h in s.local.items()]
    return s.registry


def follow(regs, cid):
    row = next((r for r in regs if r["Concept ID"] == cid), None)
    if row and row["Status"] == "MERGED":
        return row["Home"].split(":", 1)[1]
    return cid if row else None


def resolve(P, s, ev, mode):
    """06 §7 in protocol order. Returns (step, concept_id or None)."""
    regs, c = registry_view(s, mode), ev["concept"]
    active = [r for r in regs if r["Status"] == "ACTIVE"]
    for step in P.resolution:
        if step == "GRAPH_HOME_REF":
            refs = [s.graph.node(n)["home_ref"] for n in ev.get("concept_nodes", []) if s.graph.node(n)]
            refs = [r for r in refs if r != "UNASSIGNED" and follow(regs, r)]
            if refs:
                return step, follow(regs, refs[0])
        elif step == "CONCEPT_ID" and c.get("concept_id") and follow(regs, c["concept_id"]):
            return step, follow(regs, c["concept_id"])
        elif step == "NAME":
            hit = [r for r in active if r["Canonical Name"] == c["name"] and r["Short Meaning"] == c["meaning"]]
            if hit:
                return step, hit[0]["Concept ID"]
        elif step == "ALIAS":
            hit = [r for r in active if c["name"] in split(r["Aliases"]) and r["Short Meaning"] == c["meaning"]]
            if hit:
                return step, hit[0]["Concept ID"]
        elif step == "AMBIGUOUS":
            if any(c["name"] == r["Canonical Name"] or c["name"] in split(r["Aliases"]) for r in active):
                return step, None
        elif step == "NEW":
            return step, None
    return "NEW", None


def artifact_sections(P, art):
    col = 1 if art["mode"] == "LIGHT" else 2
    out = {}
    for row in P.mapping:
        src = [x.strip() for x in re.split(r" \+ | → ", row[col].replace(" (doluysa)", ""))]
        text = next((art["sections"][x] for x in src if x in art["sections"]), None)
        if text:
            out[row[0]] = text
    return out


def provenance(label, src):
    return f"Provenance: {label} ({src})"


def body_of(section_text):
    return section_text.split("\n\n", 1)[1] if section_text.startswith("Provenance:") else ""


def bump(P, h, outcome):
    if P.outcomes.get(outcome) == "+1":
        h["id"]["Version"] = str(int(h["id"]["Version"]) + 1)


def build_home(P, ctx, ev, cid, mode, existing, user):
    """Returns (home, outcome) or (None, 'CONFLICT')."""
    src = f"{ctx['config']['project_id']}:{ev['artifact']['path']}" if ev.get("artifact") else None
    new = artifact_sections(P, ev["artifact"]) if ev.get("artifact") else {}
    if existing is None:
        h = {"id": {"Concept ID": cid, "Canonical Name": ev["concept"]["name"], "Aliases": join(ev["concept"].get("aliases", [])),
                    "Short Meaning": ev["concept"]["meaning"], "Status": "ACTIVE", "Home Mode": mode,
                    "Version": "1", "Updated At": TODAY},
             "position": ev["concept"].get("position", "-"),
             "sections": {s: (provenance("ULA-DERIVED", src) + "\n\n" + new[s] if s in new else "N/A") for s in P.content},
             "appearances": [], "history": [{"version": "1", "date": TODAY, "change": "CREATED",
                                             "provenance": "ULA-DERIVED", "source": src}],
             "sources": [{"project_id": ctx["config"]["project_id"], "artifact": ev["artifact"]["path"],
                          "levels": join([s.split(" ")[0] for s in new if s.startswith("L")]), "version": "1"}],
             "local": None}
        return h, "NEW"
    h = copy.deepcopy(existing)
    judged = {s: ev.get("compare", {}).get(s, "ADD" if h["sections"][s] == "N/A" else "SAME") for s in new}
    conflicts = [s for s, j in judged.items() if j == "CONFLICT"]
    if conflicts:
        choice = user.get("conflict")
        if choice in (None, 4):
            return None, "CONFLICT"
        if choice == 1:
            judged = {}
        for s in conflicts:
            if choice == 2:
                h["history"].append({"version": str(int(h["id"]["Version"]) + 1), "date": TODAY,
                                     "change": f"REPLACED {s.split(' ')[0]}: {body_of(h['sections'][s])}",
                                     "provenance": "USER-CONFIRMED", "source": f"user:{TODAY}"})
                h["sections"][s] = provenance("USER-CONFIRMED", f"user:{TODAY}") + "\n\n" + new[s]
            elif choice == 3:
                cb = "Confusion Boundaries"
                old = body_of(h["sections"][cb]) if h["sections"][cb] != "N/A" else ""
                h["sections"][cb] = (provenance("USER-CONFIRMED", f"user:{TODAY}") + "\n\n" + (old + " " if old else "")
                                     + f"Koşul A: {body_of(h['sections'][s])} Koşul B: {new[s]}")
            judged.pop(s, None)
    changed = [s for s, j in judged.items() if j in ("ADD", "EXTEND")]
    for s in changed:
        h["sections"][s] = (provenance("ULA-DERIVED", src) + "\n\n" + new[s] if judged[s] == "ADD"
                            else h["sections"][s] + " " + new[s])
    if changed or (conflicts and user.get("conflict") in (2, 3)):
        outcome = "ENRICH"
        bump(P, h, outcome)
        h["sources"].append({"project_id": ctx["config"]["project_id"], "artifact": ev["artifact"]["path"],
                             "levels": join([s.split(" ")[0] for s in changed if s.startswith("L")]),
                             "version": h["id"]["Version"]})
        user_ok = conflicts and user.get("conflict") in (2, 3)
        h["history"].append({"version": h["id"]["Version"], "date": TODAY,
                             "change": f"CONFLICT OPTION {user['conflict']} " + join(conflicts) if user_ok else "ENRICH " + join(changed),
                             "provenance": "USER-CONFIRMED" if user_ok else "ULA-DERIVED", "source": src})
        h["id"]["Updated At"] = TODAY
        return h, outcome
    return h, "APPEARANCE_ONLY"


def add_appearance(h, ctx, ev, xid):
    key = (ctx["config"]["project_id"], ev["id"])
    if not any((a["project_id"], a["event_id"]) == key for a in h["appearances"]):
        h["appearances"].append({"project_id": key[0], "project_name": ctx["config"]["project_name"],
                                 "event_id": ev["id"], "learning_pass_id": ev["pass"], "experience_id": xid,
                                 "date": TODAY})


def significant(ev):
    return (ev["category"] in ("SYSTEM_DESIGN", "DSA") and ev.get("alternatives_in_project", 0) >= 2
            and ev.get("selected_evidence") in ("VERIFIED", "INFERRED")
            and (ev.get("priority") == "MUST_UNDERSTAND" or ev.get("want_dr")))


def map_kind(ev):
    return {"SYSTEM_DESIGN": "SYSTEM_DESIGN", "DSA": "DSA"}.get(ev["category"], "NONE")


def note_ref(ctx, xid):
    return f"{ctx['config']['project_id']}/{xid}"


def sd_row(ctx, n, depth):
    e = n["exp"]
    return {"Concept": n["concept_name"], "Project": f"{ctx['config']['project_id']} ({ctx['config']['project_name']})",
            "Problem": e["Problem"], "Constraint": e["Constraint"], "Why Needed": e["Why It Appeared"],
            "Alternatives": e["Alternatives"], "Selected": e["Selected"], "Why": e["Why Selected"],
            "Trade-off": e["Trade-off"], "Failure Mode": e["Failure Mode"], "Observed Behaviour": e["Observed Result"],
            "Reusable Signal": e["Reusable Signal"], "Depth Reached": depth,
            "Concept Home": n["id"]["Concept ID"] if n["id"]["Concept ID"] != "UNASSIGNED" else "-",
            "Experience Note": note_ref(ctx, n["id"]["Experience ID"])}


def dsa_row(ctx, n):
    e, d = n["exp"], n["dsa"]
    return {"Pattern": d["Pattern"], "Project": f"{ctx['config']['project_id']} ({ctx['config']['project_name']})",
            "Real Problem": e["Problem"], "Naive Solution": d["Naive Solution"], "Bottleneck": d["Bottleneck"],
            "Chosen Structure / Algorithm": e["Selected"], "Time Complexity": d["Time Complexity"],
            "Space Complexity": d["Space Complexity"], "Trade-off": e["Trade-off"],
            "Real System Use": d["Real System Use"], "Reusable Signal": e["Reusable Signal"],
            "Concept Home": n["id"]["Concept ID"] if n["id"]["Concept ID"] != "UNASSIGNED" else "-",
            "Experience Note": note_ref(ctx, n["id"]["Experience ID"])}


def depth_of(h):
    return join([s.split(" ")[0] for s, v in h["sections"].items() if s.startswith("L") and s[1] != "0" and v != "N/A"]) \
        if h else "-"


def add_map_row(ctx, s, n, home):
    rows_, row = (s.sd, sd_row(ctx, n, depth_of(home))) if n["id"]["Experience Map"] == "SYSTEM_DESIGN" \
        else (s.dsa, dsa_row(ctx, n))
    if not any(r["Experience Note"] == row["Experience Note"] for r in rows_):
        rows_.append(row)


def set_status(s, ev, status, kp=None):
    s.ms(ev["pass"], ev["id"])["Experience Persistence"] = status
    if kp:
        row = s.kp(ev["pass"], ev["id"])
        if row:
            row.update(kp)
        else:
            s.passes[ev["pass"]]["kp"].append(dict({"Event ID": ev["id"], "Note": "-"}, **kp))


def build_index(P, s):
    return [{"Concept ID": cid, "Canonical Name": h["id"]["Canonical Name"], "Status": h["id"]["Status"],
             "Depth": depth_of(h), "Project Count": str(len({a["project_id"] for a in h["appearances"]})),
             "Last Updated": h["id"]["Updated At"]} for cid, h in sorted(s.homes.items())]


def commit(P, store, ctx, files, cur):
    """06 §22. Returns (ok, fails)."""
    writes = delta(store, files)
    order = lambda k: next((i for i, p in enumerate(ORDER) if k.startswith(p)), len(ORDER))
    keys = sorted(writes, key=order)
    if P.atomic.get("integrity") == "BEFORE_ANY_WRITE" and P.atomic.get("write_mode") == "ALL_OR_NOTHING":
        f = integrity(P, State.load(P, store, ctx, writes), ctx, prev=cur, personal=any(k.startswith("L:") for k in keys))
        if fails(f):
            return False, f
    pre, done = {k: store.read(k) for k in keys}, []
    try:
        for k in keys:
            store.write(k, writes[k])
            done.append(k)
    except OSError:
        if P.atomic.get("on_write_error") == "RESTORE_PRE_IMAGES":
            for k in done:
                store.write(k, pre[k])
        return False, [("WRITE", "FAIL")]
    f = integrity(P, State.load(P, store, ctx), ctx, prev=cur, personal=any(k.startswith("L:") for k in keys))
    return not fails(f), f


def write_status_only(P, store, ctx, cur, ev, status):
    s = copy.deepcopy(cur)
    set_status(s, ev, status)
    store.write(pass_key(ev["pass"]), render_state_files(P, s, ctx)[pass_key(ev["pass"])])
    return status


def persist_event(P, store, ctx, eid, rng, user=None):
    """06 §5-§22 for one event. Returns persistence status."""
    user, ev = user or {}, ctx["events"][eid]
    cur = State.load(P, store, ctx)
    ms = cur.ms(ev["pass"], eid)
    if ms["Experience Persistence"] == "COMPLETE":
        return "COMPLETE"
    r = route(P, ev)
    if r["status"] in ("NOT_APPLICABLE", "BLOCKED"):
        return write_status_only(P, store, ctx, cur, ev, r["status"])
    if ms["Map Sync"] in ("PENDING", "BLOCKED") or (ev.get("concept_nodes") and ms["Map Sync"] != "COMPLETE"):
        return "PENDING"
    lib = ctx["config"]["personal_library_path"] != "UNCONFIGURED"
    mode = "PERSONAL" if lib else None
    if not lib and r["concept_home"] == "YES":
        choice = user.get("library")
        if choice in (None, "defer"):
            return "PENDING"
        mode = "LOCAL_TEMPORARY" if choice == "local" else "PERSONAL"
    mode = mode or "LOCAL_TEMPORARY"
    s = copy.deepcopy(cur)
    cid, home, outcome = "UNASSIGNED", None, None
    if r["concept_home"] in ("YES", "EXISTING_ONLY"):
        step, found = resolve(P, s, ev, mode)
        if step == "AMBIGUOUS":
            return write_status_only(P, store, ctx, cur, ev, "BLOCKED")
        homes = s.homes if mode == "PERSONAL" else s.local
        if found or r["concept_home"] == "YES":
            cid = found or new_id(P, "concept_id", s.known_ids() | set(s.homes), rng)
            home, outcome = build_home(P, ctx, ev, cid, mode, homes.get(cid), user)
            if outcome == "CONFLICT":
                return write_status_only(P, store, ctx, cur, ev, "BLOCKED")
    xid = "-"
    needs_note = r["experience_note"] == "YES" or (r["experience_note"] == "IF_PROJECT_EXPERIENCE"
                                                   and ev.get("project_experience"))
    if needs_note:
        kp = s.kp(ev["pass"], eid)
        xid = (kp["Experience ID"] if kp and kp["Experience ID"] != "-" else
               next((x for x, n in s.notes.items() if n["id"]["Event ID"] == eid), None)
               or new_id(P, "experience_id", set(s.notes), rng))
    if home is not None:
        add_appearance(home, ctx, ev, xid)
        homes[cid] = home
        if mode == "PERSONAL":
            row = {"Concept ID": cid, "Canonical Name": home["id"]["Canonical Name"], "Aliases": home["id"]["Aliases"],
                   "Short Meaning": home["id"]["Short Meaning"], "Home": f"concepts/{cid}.md", "Status": "ACTIVE"}
            s.registry = [x for x in s.registry if x["Concept ID"] != cid] + [row]
            old = s.pointers.get(cid, ({}, ""))[0]
            s.pointers[cid] = ({"Concept ID": cid, "Canonical Name": home["id"]["Canonical Name"],
                                "Home Mode": "PERSONAL", "Home Ref": f"personal:{cid}",
                                "Project Node IDs": join(sorted(set(split(old.get("Project Node IDs", "-"))) | set(ev.get("concept_nodes", [])))),
                                "Project Appearances": join(split(old.get("Project Appearances", "-")) +
                                                            ([eid] if eid not in split(old.get("Project Appearances", "-")) else [])),
                                "Local Delta": ev.get("local_delta", old.get("Local Delta", "-"))}, "")
        else:
            loc = home.get("local") or {"Project Node IDs": "-", "Local Delta": "-"}
            loc["Project Node IDs"] = join(sorted(set(split(loc["Project Node IDs"])) | set(ev.get("concept_nodes", []))))
            loc["Local Delta"] = ev.get("local_delta", loc["Local Delta"])
            home["local"] = loc
    dr = "-"
    if needs_note:
        kind = map_kind(ev)
        mstat = "NOT_APPLICABLE"
        if kind != "NONE" and ev.get("reusable"):
            mstat = "WRITTEN" if lib else "DEFERRED"
        if significant(ev):
            dr = next((d for d, t in s.drs.items() if f"Event ID:" in t and eid in t), None) or \
                new_id(P, "decision_id", set(s.drs) | set(s.notes), rng)
        ref = "-" if cid == "UNASSIGNED" else f"{'personal' if mode == 'PERSONAL' else 'local-temporary'}:{cid}"
        n = {"title": ev["title"], "concept_name": ev["concept"]["name"],
             "id": {"Experience ID": xid, "Event ID": eid, "Concept ID": cid, "Project ID": ctx["config"]["project_id"],
                    "Project Name": ctx["config"]["project_name"], "Work Unit IDs": join(ev["work_units"]),
                    "Category": ev["category"], "Decision Record": dr, "Experience Map": kind, "Map Status": mstat,
                    "Concept Home Ref": ref, "Created At": TODAY},
             "exp": {k: ev["experience"].get(k, "UNRESOLVED") for k in P.note_exp_keys},
             "dsa": {k: ev["dsa"].get(k, "UNRESOLVED") for k in P.note_dsa_keys} if ev["category"] == "DSA" else None,
             "evidence": [dict(zip(P.ev_cols, c)) for c in ev.get("evidence", [])]}
        s.notes[xid] = n
        if dr != "-":
            body_keys = P.adr_keys if ev["category"] == "SYSTEM_DESIGN" else P.dsadr_keys
            s.drs[dr] = render_dr(P, {"title": ev["title"], "id": {
                "Decision ID": dr, "Type": "ADR" if ev["category"] == "SYSTEM_DESIGN" else "DSA_DR", "Event ID": eid,
                "Experience ID": xid, "Concept ID": cid, "Project ID": ctx["config"]["project_id"], "Date": TODAY},
                "body": {k: ev.get("decision", {}).get(k, "-") for k in body_keys}})
        if mstat == "WRITTEN":
            n2 = copy.deepcopy(n)
            add_map_row(ctx, s, n2, home if mode == "PERSONAL" else None)
    if cid != "UNASSIGNED":
        g = s.graph
        for nid in ev.get("concept_nodes", []):
            node = g.node(nid)
            if node["node_status"] != "ACTIVE":
                continue
            if node["home_ref"] not in ("UNASSIGNED", cid):
                return write_status_only(P, store, ctx, cur, ev, "BLOCKED")
            node["home_ref"] = cid
        if g.signature() != cur.graph.signature():
            g.version = cur.graph.version + 1
        guard = P.debt_tx.get(("OPEN", "RESOLVED"), "-")
        for nid in ev.get("concept_nodes", []):
            node = g.node(nid)
            d = next((x for x in s.debts if x["debt_id"] == node["debt_id"] and x["debt_status"] == "OPEN"), None)
            if not d:
                continue
            ok = guard == "-" or (ev["disposition"] == "ULA_CANDIDATE" and ev.get("ula_status") == "COMPLETE"
                                  and ctx["passes"][ev["pass"]] == "COMPLETE" and node["node_status"] == "ACTIVE")
            if ok:
                d.update({"debt_status": "RESOLVED", "concept_home": cid, "resolution_ref": eid})
    set_status(s, ev, "COMPLETE", {"Concept ID": cid if r["concept_home"] != "NO" else "-", "Experience ID": xid,
                                   "Decision Record": dr})
    files = render_state_files(P, s, ctx)
    if not lib and mode == "PERSONAL":
        files.update({f"L:concepts/{cid}.md": render_home(P, home), REG: doc("Concept Registry", "Concepts", P.reg_cols, s.registry)})
    ok, f = commit(P, store, ctx, files, cur)
    ctx.setdefault("last_fails", {})[eid] = f
    if not ok:
        return write_status_only(P, store, ctx, cur, ev, "BLOCKED")
    if lib:
        s2 = State.load(P, store, ctx)
        store.write(IDX, doc("Personal Technical Library Index", "Concepts", P.idx_cols, build_index(P, s2)))
    return "COMPLETE"


def promote(P, store, ctx, rng):
    """06 §13.2: every LOCAL_TEMPORARY Home -> personal library, same concept_id."""
    cur = State.load(P, store, ctx)
    s = copy.deepcopy(cur)
    result = {}
    for cid, h in list(s.local.items()):
        fake = {"concept": {"name": h["id"]["Canonical Name"], "meaning": h["id"]["Short Meaning"]}}
        step, found = resolve(P, s, fake, "PERSONAL")
        if found and found != cid or step == "AMBIGUOUS":
            result[cid] = "BLOCKED"
            continue
        g = copy.deepcopy(h)
        g["id"]["Home Mode"], loc, g["local"] = "PERSONAL", g["local"] or {}, None
        g["history"].append({"version": g["id"]["Version"], "date": TODAY, "change": "PROMOTED",
                             "provenance": "-", "source": ctx["config"]["project_id"]})
        new_cid = ctx.get("promotion_id_override", {}).get(cid, cid)
        g["id"]["Concept ID"] = new_cid
        s.homes[new_cid] = g
        s.registry.append({"Concept ID": new_cid, "Canonical Name": g["id"]["Canonical Name"], "Aliases": g["id"]["Aliases"],
                           "Short Meaning": g["id"]["Short Meaning"], "Home": f"concepts/{new_cid}.md", "Status": "ACTIVE"})
        evs = [a["event_id"] for a in g["appearances"] if a["project_id"] == ctx["config"]["project_id"]]
        s.pointers[cid] = ({"Concept ID": new_cid, "Canonical Name": g["id"]["Canonical Name"], "Home Mode": "PERSONAL",
                            "Home Ref": f"personal:{new_cid}", "Project Node IDs": loc.get("Project Node IDs", "-"),
                            "Project Appearances": join(evs), "Local Delta": loc.get("Local Delta", "-")}, "")
        del s.local[cid]
        for n in s.notes.values():
            if n["id"]["Concept ID"] == cid:
                n["id"]["Concept Home Ref"] = f"personal:{new_cid}"
        result[cid] = "COMPLETE"
    for n in s.notes.values():
        if n["id"]["Map Status"] == "DEFERRED":
            n["id"]["Map Status"] = "WRITTEN"
            n["concept_name"] = s.homes.get(n["id"]["Concept ID"], {"id": {"Canonical Name": "-"}})["id"]["Canonical Name"]
            add_map_row(ctx, s, n, s.homes.get(n["id"]["Concept ID"]))
    ctx["promotion"] = [(cid, ctx.get("promotion_id_override", {}).get(cid, cid)) for cid, v in result.items() if v == "COMPLETE"]
    ok, f = commit(P, store, ctx, render_state_files(P, s, ctx), cur)
    ctx["last_fails"] = {"promotion": f}
    if ok:
        store.write(IDX, doc("Personal Technical Library Index", "Concepts", P.idx_cols, build_index(P, State.load(P, store, ctx))))
    return result if ok else {k: "BLOCKED" for k in result}


def rename(P, store, ctx, cid, new_name):
    """06 §14.1: registry + Home in one transaction; id unchanged; old name -> alias; version +1."""
    cur = State.load(P, store, ctx)
    s = copy.deepcopy(cur)
    h = s.homes[cid]
    h["id"]["Aliases"] = join(split(h["id"]["Aliases"]) + [h["id"]["Canonical Name"]])
    h["id"]["Canonical Name"] = new_name
    h["id"]["Version"] = str(int(h["id"]["Version"]) + 1)
    h["history"].append({"version": h["id"]["Version"], "date": TODAY, "change": "RENAME", "provenance": "USER-CONFIRMED",
                         "source": f"user:{TODAY}"})
    row = next(x for x in s.registry if x["Concept ID"] == cid)
    row.update({"Canonical Name": new_name, "Aliases": h["id"]["Aliases"]})
    return commit(P, store, ctx, render_state_files(P, s, ctx), cur)


def resolve_debt(P, store, ctx, debt_id, eid):
    """Explicit RESOLVED request (06 §20.1). Guard from protocol; P-12 verifies the candidate."""
    cur = State.load(P, store, ctx)
    s = copy.deepcopy(cur)
    d = next(x for x in s.debts if x["debt_id"] == debt_id)
    guard = P.debt_tx.get(("OPEN", "RESOLVED"))
    if guard is None:
        return False, [("TRANSITION", "FAIL")]
    ev = ctx["events"].get(eid, {})
    if guard != "-":
        ms = cur.ms(ev["pass"], eid) if ev else None
        if not (ev.get("disposition") == "ULA_CANDIDATE" and ev.get("ula_status") == "COMPLETE"
                and ms and ms["Experience Persistence"] == "COMPLETE"):
            return False, [("GUARD", "FAIL")]
    cid = next((x["Concept ID"] for x in cur.registry if x["Canonical Name"] == d["concept"]), "UNASSIGNED")
    d.update({"debt_status": "RESOLVED", "concept_home": cid, "resolution_ref": eid})
    return commit(P, store, ctx, render_state_files(P, s, ctx), cur)


# --- integrity §P --------------------------------------------------------------

def fails(f):
    return [x for x in f if x[1] == "FAIL"]


def versioned(h):
    return (h["position"], tuple(sorted(h["sections"].items())), tuple(h["id"][k] for k in VERSIONED_ID),
            tuple(tuple(sorted(x.items())) for x in h["sources"]))


def integrity(P, s, ctx, prev=None, personal=False):
    f, on = [], P.checks

    def add(code, sev="FAIL"):
        if code in on:
            f.append((code, sev))
    reg_ids = [r["Concept ID"] for r in s.registry]
    if len(reg_ids) != len(set(reg_ids)) or set(s.homes) & set(s.local):
        add("P-01")
    if any(h["id"]["Concept ID"] != cid for cid, h in list(s.homes.items()) + list(s.local.items())):
        add("P-01")
    xids = [n["id"]["Experience ID"] for n in s.notes.values()]
    if len(xids) != len(set(xids)) or any(n["id"]["Experience ID"] != x for x, n in s.notes.items()):
        add("P-02")
    reg = {r["Concept ID"]: r for r in s.registry}
    for cid, r in reg.items():
        if r["Status"] == "ACTIVE" and cid not in s.homes:
            add("P-03")
    for cid in s.homes:
        if cid not in reg:
            add("P-04")
    active = [r for r in s.registry if r["Status"] == "ACTIVE"]
    names = [r["Canonical Name"] for r in active]
    if len(names) != len(set(names)):
        add("P-05")
    for r in active:
        for o in active:
            if o is not r and set(split(r["Aliases"])) & ({o["Canonical Name"]} | set(split(o["Aliases"]))):
                add("P-06")
    known = s.known_ids()
    for cid, (ptr, text) in s.pointers.items():
        if ptr["Concept ID"] not in known:
            add("P-07")
        mode, ref = ptr["Home Mode"], ptr["Home Ref"]
        if (mode == "LOCAL_TEMPORARY" and ref.startswith("personal:")) or \
                (ref.startswith("personal:") and ref.split(":", 1)[1] not in s.homes and s.lib) or \
                (mode == "PERSONAL" and cid in s.local):
            add("P-18")
        if re.search(r"^## L[0-4]", text or render_pointer(ptr), re.M):
            add("P-28")
        if cid in reg and ptr["Canonical Name"] != reg[cid]["Canonical Name"]:
            add("P-24", "WARNING")
    for cid, h in s.local.items():
        if h["id"]["Home Mode"] != "LOCAL_TEMPORARY":
            add("P-18")
    for n in s.graph.nodes:
        if n["home_ref"] != "UNASSIGNED" and n["home_ref"] not in known:
            add("P-08")
    evs = [n["id"]["Event ID"] for n in s.notes.values()]
    if len(evs) != len(set(evs)):
        add("P-09")
    for h in list(s.homes.values()) + list(s.local.values()):
        keys = [(a["project_id"], a["event_id"]) for a in h["appearances"]]
        if len(keys) != len(set(keys)):
            add("P-10")
        for sec, v in h["sections"].items():
            if v != "N/A":
                m = re.match(r"Provenance: ([A-Z\- ]+?) \(", v)
                if not m or m.group(1) not in P.provenance:
                    add("P-26")
    for n in s.notes.values():
        home = s.homes.get(n["id"]["Concept ID"]) or s.local.get(n["id"]["Concept ID"])
        theory = [body_of(v) for k, v in home["sections"].items() if k.startswith("L")] if home else []
        if re.search(r"^## L[0-4]", n["raw"], re.M) or any(len(t) > 40 and t in n["raw"] for t in theory):
            add("P-11")
        ev = ctx["events"].get(n["id"]["Event ID"], {})
        for c in n["evidence"]:
            src = ev.get("claim_sources", {}).get(c["Claim"], ev.get("evidence_status", "UNRESOLVED"))
            if (c["Evidence Status"] == "VERIFIED" and c["Evidence Ref"] in ("", "-")) or \
                    EVIDENCE_RANK.get(c["Evidence Status"], 0) > EVIDENCE_RANK.get(src, 0):
                add("P-27")
    debts = {d["debt_id"]: d for d in s.debts}
    for d in s.debts:
        if d["debt_status"] == "RESOLVED":
            ev = ctx["events"].get(d.get("resolution_ref"), {})
            ms = s.ms(ev["pass"], ev["id"]) if ev and ev.get("pass") in s.passes else None
            if not (ev.get("disposition") == "ULA_CANDIDATE" and ev.get("ula_status") == "COMPLETE"
                    and ctx["passes"].get(ev.get("pass")) == "COMPLETE" and ms and ms["Experience Persistence"] == "COMPLETE"
                    and d["concept_home"] in known):
                add("P-12")
            if any(n["debt_id"] == d["debt_id"] and n["node_status"] == "DEBT" for n in s.graph.nodes):
                add("P-13")
        if d["debt_status"] == "DISMISSED" and not d.get("resolution_ref", "").startswith("user:"):
            add("P-15")
    for n in s.graph.nodes:
        d = debts.get(n["debt_id"])
        if n["node_status"] == "ACTIVE" and d and d["debt_status"] == "RESOLVED" and n["home_ref"] == "UNASSIGNED":
            add("P-14")
    for lp, t in s.passes.items():
        for row in t["ms"]:
            if row["Experience Persistence"] != "COMPLETE":
                continue
            kp = s.kp(lp, row["Event ID"]) or {}
            cid, xid, dr = kp.get("Concept ID", "-"), kp.get("Experience ID", "-"), kp.get("Decision Record", "-")
            if (cid not in ("-", "UNASSIGNED") and cid not in s.pointers and cid not in s.local) or \
                    (xid != "-" and xid not in s.notes) or (dr != "-" and dr not in s.drs):
                add("P-16")
    if personal and not s.lib:
        add("P-17")
    for old, new in ctx.get("promotion", []):
        if old != new:
            add("P-19")
    for rows_, code in ((s.sd, "P-20"), (s.dsa, "P-21")):
        for r in rows_:
            prj, xid = r["Experience Note"].split("/")
            if prj == ctx["config"]["project_id"] and xid not in s.notes:
                add(code)
    for r in s.dsa:
        prj, xid = r["Experience Note"].split("/")
        if prj == ctx["config"]["project_id"] and xid in s.notes and s.notes[xid]["id"]["Category"] != "DSA":
            add("P-22")
    for cid, h in s.homes.items():
        r = reg.get(cid)
        if r and (r["Canonical Name"], r["Aliases"], r["Status"], r["Home"]) != \
                (h["id"]["Canonical Name"], h["id"]["Aliases"], h["id"]["Status"], f"concepts/{cid}.md"):
            add("P-23")
    if s.index and s.index != build_index(P, s):
        add("P-24", "WARNING")
    if prev is not None:
        for cid, h in list(s.homes.items()) + list(s.local.items()):
            old = prev.homes.get(cid) or prev.local.get(cid)
            if old is None:
                if h["id"]["Version"] != "1":
                    add("P-25")
                continue
            ch = versioned(old) != versioned(h)
            dv = int(h["id"]["Version"]) - int(old["id"]["Version"])
            if (ch and dv != 1) or (not ch and dv != 0):
                add("P-25")
    mctx = {"artifacts": ctx.get("artifacts", {}), "debts": {d["debt_id"] for d in s.debts}, "events": {}}
    f += [x for x in gm.integrity(P.gp, s.graph, mctx)]
    return sorted(set(f))
