# Learning Coverage Ledger

> Template: `.claude/skills/stay-in-the-loop/templates/COVERAGE_LEDGER_TEMPLATE.md`
> Target: `docs/learning/state/COVERAGE_LEDGER.md`
> Role: **Authoritative coverage truth.**
> Kurallar: `references/02_COVERAGE_PROTOCOL.md`

## Metadata

```yaml
schema_version: 1
project: <PROJECT_NAME>
last_updated: <YYYY-MM-DD>
```

## Work Units

Bu tablo tek canonical kayıttır. Open, Skipped ve Closed listeleri burada saklanmaz. Her `/stay-in-the-loop` çağrısında bu tablodan hesaplanır.

Satır silinmez. Yalnız status değişir.

| work_unit_id | seq | label | source_type | source_ref | status | discovered_at | last_evaluated_at | learning_pass_id | open_items | notes |
|---|---|---|---|---|---|---|---|---|---|---|

## Field Reference

| Alan | Değerler |
|---|---|
| `work_unit_id` | `<source_type>:<native-id>` — benzersiz |
| `seq` | Tam sayı — aynı `source_type` içinde benzersiz |
| `source_type` | `user` · `jira` · `phase-doc` · `git` · `other` |
| `status` | `UNCOVERED` · `COVERED` · `PARTIAL` · `DEFERRED` · `SKIPPED_BY_USER` · `NOT_LEARNING_RELEVANT` |
| `learning_pass_id` | `LP-YYYYMMDD-NN` · `EXTERNAL` · `-` |
| `open_items` | `PARTIAL` için `;` ile ayrılmış liste · diğer durumlarda `-` |
| Boş alan | `-` |

Tablo hücrelerinde `|` karakteri kullanılmaz.
