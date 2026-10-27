"""Markdown render / parse for the temporary target project used by the E2E suite.

Section names and table headers come from the skill templates (via the phase models).
"""
import re

import graph_model as gm
import persist_model as pm
from coverage_model import Ledger

CONFIG, STATE, LEDGER = "P:state/LEARNING_CONFIG.md", "P:state/LEARNING_STATE.md", "P:state/COVERAGE_LEDGER.md"
QUEUE, GRAPH, HMAP = pm.QUEUE, pm.GRAPH, "P:maps/HORIZONTAL_MAP.md"
KV = re.compile(r"^(\w+):[ \t]*(.*?)[ \t]*$", re.M)


def kv(text):
    return dict(KV.findall(text or ""))


def kv_doc(title, sec, d):
    body = "\n".join(f"{k}: {v}" for k, v in d.items())
    return f"# {title}\n\n## {sec}\n\n```text\n{body}\n```\n"


def table(text, heading, cols):
    return pm.parse_table(gm.section(text, f"## {heading}"), cols) if text and f"## {heading}\n" in text else []


# --- state ---------------------------------------------------------------------

def render_ledger(ledger):
    return f"# Coverage Ledger\n\n## Work Units\n\n{ledger.render()}\n"


def parse_ledger(cols, text):
    return Ledger.parse(cols, "\n".join(l for l in gm.section(text, "## Work Units").splitlines() if l.startswith("|")))


def render_queue(cols_a, rows_a, cols_b, debts):
    return (f"# Learning Queue\n\n## A. Deferred Work Units\n\n{pm.md_table(cols_a, rows_a)}\n\n"
            f"## B. Knowledge Debt\n\n{pm.md_table(cols_b, debts)}\n")


def queue_a_rows(ledger):
    return [{"work_unit_id": r["work_unit_id"], "label": r["label"], "status": r["status"], "reason": r["notes"],
             "deferred_at": r["last_evaluated_at"], "source": r["source_type"]}
            for r in ledger.rows if r["status"] in ("DEFERRED", "PARTIAL")]


# --- pass ----------------------------------------------------------------------

def render_pass(hs_proto, ula_proto, ms_cols, kp_cols, meta, events, routing, ms, kp):
    import hs_model
    lines = "\n".join(f"{k}: {v}" for k, v in meta.items())
    return (f"# Learning Pass\n\n## Metadata\n\n```text\n{lines}\n```\n\n"
            f"## Learning Events\n\n{hs_model.render_events(hs_proto, events)}\n\n"
            f"## ULA Routing\n\n{pm.md_table(ula_proto.routing_header, routing)}\n\n"
            f"## Map Sync\n\n{pm.md_table(ms_cols, ms)}\n\n"
            f"## Knowledge Persistence\n\n{pm.md_table(kp_cols, kp)}\n")


def parse_pass(ula_proto, ms_cols, kp_cols, text):
    import hs_model
    meta = kv(gm.section(text, "## Metadata"))
    meta["selected_scope"] = [x.strip() for x in meta.get("selected_scope", "[]").strip("[]").split(",") if x.strip()]
    return {"meta": meta, "events": hs_model.parse_events(gm.section(text, "## Learning Events")),
            "routing": table(text, "ULA Routing", ula_proto.routing_header),
            "ms": table(text, "Map Sync", ms_cols), "kp": table(text, "Knowledge Persistence", kp_cols)}


# --- views ---------------------------------------------------------------------

def render_hmap(graph):
    view = gm.root_map(graph) if any(n["node_type"] == "ROOT" for n in graph.nodes) else {"node_ids": [], "text": "-"}
    return (f"# Horizontal Knowledge Map\n\n## Map Metadata\n\n```text\ngenerated_from_graph_version: {graph.version}\n```\n\n"
            f"## Root Map\n\n{view['text']}\n\nnode_ids: {'; '.join(view['node_ids']) or '-'}\n")


def render_index(P7, state):
    return pm.doc("Personal Technical Library Index", "Concepts", P7.idx_cols, pm.build_index(P7, state))
