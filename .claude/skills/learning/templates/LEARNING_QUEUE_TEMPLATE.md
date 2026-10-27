# Learning Queue

> Template: `.claude/skills/learning/templates/LEARNING_QUEUE_TEMPLATE.md`
> Target: `docs/learning/state/LEARNING_QUEUE.md`
> Role: §A open work unit view (derived). §B Knowledge Debt record (authoritative).

## A. Deferred Work Units

**GENERATED VIEW — elle düzenleme.** Bu bölüm her ledger commit'inden sonra `COVERAGE_LEDGER.md` içindeki `DEFERRED` ve `PARTIAL` satırlarından yeniden üretilir. Authoritative status ledger'dadır.

| work_unit_id | label | status | reason | deferred_at | source |
|---|---|---|---|---|---|

Alan eşlemesi (ledger → queue):

| Queue alanı | Ledger alanı |
|---|---|
| `reason` | `notes` (`PARTIAL` için: `open_items`) |
| `deferred_at` | `last_evaluated_at` |
| `source` | `source_type` + `source_ref` |

## B. Knowledge Debt

**AUTHORITATIVE RECORD — generated view değildir.** Kayıtlar `references/03_HUMAN_SYNC_PROTOCOL.md` §14 ile eklenir. Satır silinmez. Status değişir.

Knowledge Debt ertelenmiş **kavramdır**. Deferred Work Unit ertelenmiş **proje işidir**. İki kayıt ayrıdır.

| debt_id | concept | originating_event_id | work_unit_ids | one_sentence_explanation | why_it_matters | priority | debt_status | created_at | concept_home | resolution_ref |
|---|---|---|---|---|---|---|---|---|---|---|

| Alan | Değerler |
|---|---|
| `debt_id` | `KD-<learning-pass-id>-NN` |
| `originating_event_id` | `LE-<learning-pass-id>-NN`. Zorunlu. |
| `priority` | `NOW` · `LATER` · `OPTIONAL` |
| `debt_status` | `OPEN` · `RESOLVED` · `DISMISSED` |
| `concept_home` | `CH-xxxxxxxx` veya `UNASSIGNED` |
| `resolution_ref` | `OPEN`: `-` · `RESOLVED`: resolution `event_id` · `DISMISSED`: `user:YYYY-MM-DD` |

Lifecycle ve `RESOLVED` guard: `references/06_KNOWLEDGE_PERSISTENCE.md` §20.
