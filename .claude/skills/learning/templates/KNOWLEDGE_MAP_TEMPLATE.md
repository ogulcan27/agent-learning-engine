# Horizontal Knowledge Map

> Template: `.claude/skills/learning/templates/KNOWLEDGE_MAP_TEMPLATE.md`
> Target: `docs/learning/maps/HORIZONTAL_MAP.md`
> Rules: `references/05_MINDMAP_PROTOCOL.md` §12
> Role: **GENERATED VIEW — elle düzenleme.** `SEMANTIC_GRAPH.md` her başarılı mutation'dan sonra bu dosyayı yeniden üretir.
> Node metadata buraya kopyalanmaz. Ayrıntı: `/learning map <node-id>`.

## Map Metadata

```yaml
generated_from_graph_version: 0
generated_at: YYYY-MM-DD
```

## Root Map

```text
<[Block] (+N) → [Block] (+N) → ...>
<zincir dışı block'lar>
<… +N block (map <root-id>)>
Unplaced: <parent_id - olan node'lar>
```

## Legend

| Sembol | Anlam |
|---|---|
| `→` | NEXT |
| `↳` | Primary child (`parent_id`) |
| `-RELATION→` | Diğer canonical relation |
| `(+N)` | Açılmamış child sayısı |
| `(DEBT)` | Knowledge Debt node |

## Navigation

```text
/learning map <node-id>        local zoom
/learning map <node-id> L2     depth view
/learning map debt             DEBT node'ları
```
