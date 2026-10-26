# Learning Queue

> Template: `.claude/skills/learning/templates/LEARNING_QUEUE_TEMPLATE.md`
> Target: `docs/learning/state/LEARNING_QUEUE.md`
> Role: Open-item convenience view.

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

**RESERVED — implemented in later phase.**

Knowledge Debt ertelenmiş **kavramdır**. Deferred Work Unit ertelenmiş **proje işidir**. İki kayıt ayrıdır.
