# Semantic Graph

> Template: `.claude/skills/learning/templates/SEMANTIC_GRAPH_TEMPLATE.md`
> Target: `docs/learning/maps/SEMANTIC_GRAPH.md`
> Rules: `references/05_MINDMAP_PROTOCOL.md`
> Role: **AUTHORITATIVE** project-local knowledge graph. `HORIZONTAL_MAP.md` bu dosyadan üretilir.
> Satır silinmez. Primary navigation parent `parent_id` içindedir. Secondary membership `PART_OF` edge olarak tutulur. Aynı membership iki yerde tutulmaz.

## Metadata

```yaml
schema_version: 1
graph_version: 0
last_updated: YYYY-MM-DD
```

## Nodes

| node_id | canonical_name | node_type | parent_id | short_meaning | system_role | home_ref | available_depth | source_event_ids | source_artifacts | project_appearances | aliases | node_status | debt_id | superseded_by |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Edges

| edge_id | source_node_id | relation_type | target_node_id | meaning | source_event_ids | evidence_status |
|---|---|---|---|---|---|---|

## Field Reference

| Alan | Değerler |
|---|---|
| `node_id` | `KN-` + 8 lowercase hex, opaque |
| `node_type` | `ROOT` · `DOMAIN` · `CONCEPT` · `SYSTEM_COMPONENT` · `DECISION` · `PATTERN` · `FAILURE_MODE` · `OTHER` |
| `node_status` | `ACTIVE` · `DEBT` · `SUPERSEDED` |
| `available_depth` | `L1`…`L4` alt kümesi veya `-` |
| `home_ref` | Concept Home pointer veya `UNASSIGNED` |
| `edge_id` | `KE-NNNN` |
| `relation_type` | `NEXT` · `REQUIRES` · `PRODUCES` · `CAUSES` · `USES` · `DEPENDS_ON` · `ALTERNATIVE_TO` · `COMPARED_WITH` · `PART_OF` · `EVIDENCE_FOR` · `FAILS_WHEN` · `IMPLEMENTED_BY` |
| Liste ayırıcı | `; ` |
