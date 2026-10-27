"""Reference model of 05_MINDMAP_PROTOCOL used for synthetic Phase 6 tests.

Parsed from skill files: node types, node statuses, relation vocabulary,
eligibility table, identity steps and merge rules (05); enabled checks (07 §M);
node and edge columns (SEMANTIC_GRAPH_TEMPLATE). Judgment inputs (candidate
nodes and edges, meaning equivalence) come from fixtures.
"""
import copy
import random
import re
from pathlib import Path


def section(text, heading):
    level = len(heading) - len(heading.lstrip("#"))
    body = text.split(heading, 1)[1]
    stop = re.search(r"\n#{1,%d} " % level, body)
    return body[: stop.start()] if stop else body


def first_table(block):
    lines = block.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("|"))
    out = []
    for l in lines[start:]:
        if not l.startswith("|"):
            break
        out.append([c.strip() for c in l.strip("|").split("|")])
    return out


def ticks(block):
    return [m.group(1) for m in (re.match(r"^\| `([A-Z_]+)` \|", l) for l in block.splitlines()) if m]


class Protocol:
    def __init__(self, skill: Path):
        t = (skill / "references" / "05_MINDMAP_PROTOCOL.md").read_text(encoding="utf-8")
        self.node_types = ticks(section(t, "### 3.2 Node type"))
        self.node_status = ticks(section(t, "### 3.3 Node status"))
        self.relations = ticks(section(t, "### 4.1 Canonical relation vocabulary"))
        self.eligibility = first_table(section(t, "## 6. Map eligibility"))[2:]
        self.identity = [r[0] for r in first_table(section(t, "## 7. Identity resolution"))[2:]]
        self.merge = {r[0]: r[1].split(" ")[0] for r in first_table(section(t, "### 7.1 Merge rules"))[2:]}
        i = (skill / "references" / "07_INTEGRITY_CHECKS.md").read_text(encoding="utf-8")
        self.checks = set(re.findall(r"^\| (M-\d\d) \|", section(i, "## M. MindMap"), re.M))
        g = (skill / "templates" / "SEMANTIC_GRAPH_TEMPLATE.md").read_text(encoding="utf-8")
        self.node_cols = first_table(section(g, "## Nodes"))[0]
        self.edge_cols = first_table(section(g, "## Edges"))[0]


LIST = ("source_event_ids", "source_artifacts", "project_appearances", "aliases", "available_depth")


def split(v):
    return [] if v in ("", "-") else v.split("; ")


def join(xs):
    return "; ".join(xs) if xs else "-"


class Graph:
    def __init__(self, version=0, nodes=None, edges=None):
        self.version, self.nodes, self.edges = version, nodes or [], edges or []

    def node(self, nid):
        return next((n for n in self.nodes if n["node_id"] == nid), None)

    def by_name(self, name):
        return [n for n in self.nodes if n["canonical_name"] == name or name in split(n["aliases"])]

    def render(self, P):
        rows = ["## Nodes", "| " + " | ".join(P.node_cols) + " |", "|" + "---|" * len(P.node_cols)]
        rows += ["| " + " | ".join(n.get(c, "-") for c in P.node_cols) + " |" for n in self.nodes]
        rows += ["", "## Edges", "| " + " | ".join(P.edge_cols) + " |", "|" + "---|" * len(P.edge_cols)]
        rows += ["| " + " | ".join(e.get(c, "-") for c in P.edge_cols) + " |" for e in self.edges]
        return f"graph_version: {self.version}\n\n" + "\n".join(rows) + "\n"

    @classmethod
    def parse(cls, P, text):
        version = int(re.search(r"graph_version: (\d+)", text).group(1))
        nodes = [dict(zip(P.node_cols, r)) for r in first_table(section(text, "## Nodes"))[2:]]
        edges = [dict(zip(P.edge_cols, r)) for r in first_table(section(text, "## Edges"))[2:]] \
            if "|" in section(text, "## Edges") else []
        return cls(version, nodes, edges)

    def signature(self):
        return (sorted(tuple(sorted(n.items())) for n in self.nodes), sorted(tuple(sorted(e.items())) for e in self.edges))


def new_id(graph, rng):
    """Opaque, collision-checked node id; never derived from the name."""
    taken = {n["node_id"] for n in graph.nodes}
    while True:
        nid = f"KN-{rng.getrandbits(32):08x}"
        if nid not in taken:
            return nid


def eligibility(P, ev):
    for disp, cond, result in P.eligibility:
        if disp != ev["disposition"]:
            continue
        ok = (cond == "-"
              or (cond == "ula_status COMPLETE" and ev.get("ula_status") == "COMPLETE")
              or (cond == "ula_status not COMPLETE" and ev.get("ula_status") != "COMPLETE")
              or (cond == "reusable signal var" and ev.get("reusable"))
              or (cond == "reusable signal yok" and not ev.get("reusable"))
              or (cond.startswith("§B") and ev.get("debt_id")))
        if ok:
            return result
    return "EXCLUDE"


def resolve(P, graph, cand, event_id):
    """05 §7 steps in protocol order. Returns (step, node_id or None)."""
    for step in P.identity:
        if step == "EVENT":
            hit = [n for n in graph.by_name(cand["name"]) if event_id in split(n["source_event_ids"])]
            if hit:
                return step, hit[0]["node_id"]
        elif step == "HOME" and cand.get("home_ref", "UNASSIGNED") != "UNASSIGNED":
            hit = [n for n in graph.nodes if n["home_ref"] == cand["home_ref"]]
            if hit:
                return step, hit[0]["node_id"]
        elif step == "NODE_ID" and cand.get("node_ref") and graph.node(cand["node_ref"]):
            return step, cand["node_ref"]
        elif step == "NAME":
            hit = [n for n in graph.nodes if n["canonical_name"] == cand["name"] and n["short_meaning"] == cand["meaning"]]
            if hit:
                return step, canonical(graph, hit[0])
        elif step == "ALIAS":
            hit = [n for n in graph.nodes if cand["name"] in split(n["aliases"]) and n["short_meaning"] == cand["meaning"]]
            if hit:
                return step, canonical(graph, hit[0])
        elif step == "AMBIGUOUS" and graph.by_name(cand["name"]):
            return step, None
        elif step == "NEW":
            return step, None
    return "NEW", None


def canonical(graph, node):
    return node["superseded_by"] if node["node_status"] == "SUPERSEDED" else node["node_id"]


def merge_list(P, field, old, new):
    xs = split(old)
    for x in new:
        if P.merge.get(field) == "APPEND" or x not in xs:
            xs.append(x)
    return join(xs)


def ensure_root(graph, rng, project="Project"):
    root = next((n for n in graph.nodes if n["node_type"] == "ROOT"), None)
    if root:
        return root["node_id"]
    nid = new_id(graph, rng)
    graph.nodes.append({"node_id": nid, "canonical_name": project, "node_type": "ROOT", "parent_id": "-",
                        "short_meaning": "project root", "system_role": "-", "home_ref": "UNASSIGNED",
                        "available_depth": "-", "source_event_ids": "-", "source_artifacts": "-",
                        "project_appearances": "-", "aliases": "-", "node_status": "ACTIVE", "debt_id": "-",
                        "superseded_by": "-"})
    return nid


def apply_event(P, graph, lp_id, ev, rng):
    """Apply one event delta in place. Returns 'AMBIGUOUS' or None."""
    names = {}
    for c in ev.get("nodes", []):
        step, nid = resolve(P, graph, c, ev["id"])
        if step == "AMBIGUOUS":
            return "AMBIGUOUS"
        if step == "EVENT":
            names[c["name"]] = nid
            continue
        status = "DEBT" if ev["disposition"] == "KNOWLEDGE_DEBT" else "ACTIVE"
        if nid is None:
            nid = new_id(graph, rng)
            graph.nodes.append({"node_id": nid, "canonical_name": c["name"], "node_type": c["type"],
                                "parent_id": "-", "short_meaning": c["meaning"], "system_role": c.get("role", "-"),
                                "home_ref": "UNASSIGNED", "available_depth": "-", "source_event_ids": "-",
                                "source_artifacts": "-", "project_appearances": "-", "aliases": "-",
                                "node_status": status, "debt_id": ev.get("debt_id", "-") if status == "DEBT" else "-",
                                "superseded_by": "-"})
        n = graph.node(nid)
        if n["node_status"] == "DEBT" and status == "ACTIVE":
            n["node_status"] = "ACTIVE"
        for field, values in (("source_event_ids", [ev["id"]]), ("project_appearances", [lp_id]),
                              ("source_artifacts", c.get("artifacts", [])), ("available_depth", c.get("depth", []))):
            n[field] = merge_list(P, field, n[field], values)
        names[c["name"]] = nid
    for c in ev.get("nodes", []):
        n = graph.node(names[c["name"]])
        parent = c.get("parent")
        if parent and n["parent_id"] == "-":
            n["parent_id"] = names.get(parent) or next((x["node_id"] for x in graph.by_name(parent)), parent)
        elif not parent and n["parent_id"] == "-" and n["node_type"] != "ROOT":
            n["parent_id"] = ensure_root(graph, rng)
    edges = list(ev.get("edges", []))
    for c in ev.get("nodes", []):
        edges += [{"source": c["name"], "relation": "PART_OF", "target": d,
                   "meaning": f"{c['name']} PART_OF {d}", "evidence": "INFERRED"} for d in c.get("also_part_of", [])]
    for e in edges:
        src = names.get(e["source"]) or next((x["node_id"] for x in graph.by_name(e["source"])), e["source"])
        tgt = names.get(e["target"]) or next((x["node_id"] for x in graph.by_name(e["target"])), e["target"])
        same = [x for x in graph.edges if (x["source_node_id"], x["relation_type"], x["target_node_id"]) ==
                (src, e["relation"], tgt)]
        if same and P.merge.get("edges") == "DEDUPE":
            same[0]["source_event_ids"] = merge_list(P, "source_event_ids", same[0]["source_event_ids"], [ev["id"]])
            continue
        num = max([int(x["edge_id"][3:]) for x in graph.edges] + [0]) + 1
        graph.edges.append({"edge_id": f"KE-{num:04d}", "source_node_id": src, "relation_type": e["relation"],
                            "target_node_id": tgt, "meaning": e.get("meaning", "-"), "source_event_ids": ev["id"],
                            "evidence_status": e.get("evidence", "INFERRED")})
    return None


def sync(P, graph, lp, ctx, rng):
    """05 §8-§9: atomic per pass. Returns (graph, statuses). Original graph is never mutated."""
    statuses = {}
    if lp["status"] != "COMPLETE":
        return graph, statuses
    work = copy.deepcopy(graph)
    ensure_root(work, rng, lp.get("project", "Project"))
    included = []
    for ev in lp["events"]:
        result = eligibility(P, ev)
        if result == "EXCLUDE" or (result == "INCLUDE" and not ev.get("nodes")):
            statuses[ev["id"]] = "NOT_APPLICABLE"
        elif result == "INCLUDE":
            included.append(ev)
    for i, ev in enumerate(included):
        if apply_event(P, work, lp["id"], ev, rng) == "AMBIGUOUS" or fails(integrity(P, work, ctx)):
            statuses[ev["id"]] = "BLOCKED"
            for rest in included[i + 1:] + included[:i]:
                statuses[rest["id"]] = "PENDING"
            return graph, statuses
    for ev in included:
        statuses[ev["id"]] = "COMPLETE"
    if not included or work.signature() == graph.signature():
        return graph, statuses
    work.version = graph.version + 1
    return work, statuses


def rename(graph, nid, new_name):
    n = graph.node(nid)
    n["aliases"] = join(split(n["aliases"]) + [n["canonical_name"]])
    n["canonical_name"] = new_name
    graph.version += 1


# --- integrity §M -------------------------------------------------------------

def integrity(P, g, ctx, view=None):
    """ctx: {'events': {id: event}, 'artifacts': {path: levels}, 'debts': set, 'sync': {id: status}}."""
    f, on = [], P.checks
    ids = [n["node_id"] for n in g.nodes]
    known = set(ids)

    def add(code, sev="FAIL"):
        if code in on:
            f.append((code, sev))
    if len(ids) != len(known):
        add("M-01")
    eids = [e["edge_id"] for e in g.edges]
    if len(eids) != len(set(eids)):
        add("M-02")
    triples = []
    for e in g.edges:
        if e["source_node_id"] not in known:
            add("M-03")
        if e["target_node_id"] not in known:
            add("M-04")
        if e["relation_type"] not in P.relations:
            add("M-05")
        if e["relation_type"] == "PART_OF":
            src = g.node(e["source_node_id"])
            if src and src["parent_id"] == e["target_node_id"]:
                add("M-21")
            if e["source_node_id"] == e["target_node_id"]:
                add("M-09")
        triples.append((e["source_node_id"], e["relation_type"], e["target_node_id"]))
        if len(split(e["source_event_ids"])) != len(set(split(e["source_event_ids"]))):
            add("M-17")
        if any(unsettled(ctx, x) for x in split(e["source_event_ids"])):
            add("M-19")
    if len(triples) != len(set(triples)):
        add("M-11")
    for n in g.nodes:
        if n["node_type"] not in P.node_types:
            add("M-06")
        if n["node_status"] not in P.node_status:
            add("M-07")
        if n["parent_id"] == n["node_id"]:
            add("M-09")
        if n["node_status"] == "SUPERSEDED" and g.node(n["superseded_by"]) is None:
            add("M-10")
        for field in ("source_event_ids", "project_appearances"):
            if len(split(n[field])) != len(set(split(n[field]))):
                add("M-17")
        arts = split(n["source_artifacts"])
        if any(a not in ctx.get("artifacts", {}) for a in arts):
            add("M-13")
        have = set().union(*[ctx.get("artifacts", {}).get(a, set()) for a in arts]) if arts else set()
        if not set(split(n["available_depth"])) <= have:
            add("M-14")
        if n["node_status"] == "ACTIVE" and any(unsettled(ctx, x) for x in split(n["source_event_ids"])):
            add("M-19")
        if n["node_status"] == "DEBT" and n["debt_id"] not in ctx.get("debts", set()):
            add("M-20")
    if sum(n["node_type"] == "ROOT" for n in g.nodes) > 1:
        add("M-22")
    if hierarchy_cycle(g):
        add("M-08")
    in_graph = {x for n in g.nodes for x in split(n["source_event_ids"])} | \
               {x for e in g.edges for x in split(e["source_event_ids"])}
    if any(s == "COMPLETE" and eid not in in_graph for eid, s in ctx.get("sync", {}).items()):
        add("M-18")
    if view is not None:
        if view["version"] > g.version:
            add("M-15")
        elif view["version"] < g.version:
            add("M-16", "WARNING")
        if set(view["node_ids"]) - known:
            add("M-12", "WARNING")
    return sorted(set(f))


def unsettled(ctx, eid):
    ev = ctx.get("events", {}).get(eid)
    return bool(ev) and (ev["disposition"] == "UNRESOLVED" or
                         (ev["disposition"] == "ULA_CANDIDATE" and ev.get("ula_status") != "COMPLETE"))


def hierarchy_cycle(g):
    """Combined hierarchy: primary parent_id links plus secondary PART_OF edges (05 §5.2)."""
    up = {n["node_id"]: {n["parent_id"]} - {"-"} for n in g.nodes}
    for e in g.edges:
        if e["relation_type"] == "PART_OF":
            up.setdefault(e["source_node_id"], set()).add(e["target_node_id"])
    state = {}

    def visit(nid):
        if state.get(nid) == 1:
            return True
        if state.get(nid) == 2:
            return False
        state[nid] = 1
        if any(visit(p) for p in up.get(nid, ())):
            return True
        state[nid] = 2
        return False
    return any(visit(n) for n in list(up))


def fails(f):
    return [x for x in f if x[1] == "FAIL"]


# --- views --------------------------------------------------------------------

def children(g, nid):
    return [n for n in g.nodes if n["parent_id"] == nid and n["node_status"] != "SUPERSEDED"]


def descendants(g, nid):
    return sum(1 + descendants(g, c["node_id"]) for c in children(g, nid))


def label(n, g):
    k = len(children(g, n["node_id"]))
    return f"[{n['canonical_name']}]" + (" (DEBT)" if n["node_status"] == "DEBT" else "") + (f" (+{k})" if k else "")


def root_map(g, limit=10):
    """05 §12.2: root children only, NEXT order, at most 10 blocks."""
    root = next(n for n in g.nodes if n["node_type"] == "ROOT")
    blocks = children(g, root["node_id"])
    extra = 0
    if len(blocks) > limit:
        blocks = sorted(blocks, key=lambda n: -descendants(g, n["node_id"]))
        extra, blocks = len(blocks) - (limit - 1), blocks[: limit - 1]
    ids = {b["node_id"] for b in blocks}
    nxt = {e["source_node_id"]: e["target_node_id"] for e in g.edges
           if e["relation_type"] == "NEXT" and e["source_node_id"] in ids and e["target_node_id"] in ids}
    heads = [b for b in blocks if b["node_id"] not in nxt.values()]
    lines, shown = [], []
    for h in heads:
        chain, cur = [], h["node_id"]
        while cur and cur not in shown:
            shown.append(cur)
            chain.append(label(g.node(cur), g))
            cur = nxt.get(cur)
        lines.append(" → ".join(chain))
    if extra:
        lines.append(f"… +{extra} block (map {root['node_id']})")
    unplaced = [n for n in g.nodes if n["parent_id"] == "-" and n["node_type"] != "ROOT"]
    if unplaced:
        lines.append("Unplaced: " + ", ".join(label(n, g) for n in unplaced))
    return {"version": g.version, "node_ids": shown, "text": "\n".join(lines)}


def breadcrumb(g, nid):
    path, cur = [], g.node(nid)
    while cur:
        path.append(cur["canonical_name"])
        cur = g.node(cur["parent_id"]) if cur["parent_id"] != "-" else None
    return " → ".join(reversed(path))


def local_map(g, nid):
    n = g.node(nid)
    name = lambda x: g.node(x)["canonical_name"]
    rel = [f"-{e['relation_type']}→ [{name(e['target_node_id'])}]"
           for e in g.edges if e["source_node_id"] == nid and e["relation_type"] != "PART_OF"]
    also = [name(e["target_node_id"]) for e in g.edges if e["source_node_id"] == nid and e["relation_type"] == "PART_OF"]
    members = [name(e["source_node_id"]) for e in g.edges if e["target_node_id"] == nid and e["relation_type"] == "PART_OF"]
    return {"breadcrumb": breadcrumb(g, nid), "node": n["canonical_name"],
            "children": [c["canonical_name"] for c in children(g, nid)], "also_part_of": also,
            "secondary_members": members, "relations": rel}


def depth_view(g, nid, level):
    n = g.node(nid)
    have = split(n["available_depth"])
    if level not in have:
        return f"{level} unavailable. Mevcut: {', '.join(have) if have else '-'}."
    return {"breadcrumb": breadcrumb(g, nid), "level": level, "artifact": split(n["source_artifacts"])[0]}
