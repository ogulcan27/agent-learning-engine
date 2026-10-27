# Learning Pass

> Template: `.claude/skills/stay-in-the-loop/templates/LEARNING_PASS_TEMPLATE.md`
> Target: `docs/learning/passes/<learning-pass-id>/LEARNING_PASS.md`
> Rules: `references/03_HUMAN_SYNC_PROTOCOL.md`, `references/04_ULA_PROTOCOL.md`
> Role: Pipeline handoff ve resume artifact. Event kaydı burada tutulur. Disposition listeleri ve routing tablosu yalnız ID ve pointer verir.

## Metadata

```yaml
learning_pass_id: LP-YYYYMMDD-NN
pass_status: IN_PROGRESS        # IN_PROGRESS | WAITING_USER | BLOCKED | COMPLETE | ABANDONED
current_stage: HUMAN_SYNC       # 04 §2.4
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
selected_scope: [<work_unit_id>, ...]
coverage_source: <resolved work_unit_source>
```

## Human Synchronization

<Format ve kurallar: templates/HUMAN_SYNC_TEMPLATE.md. Scope başlığı Metadata'da olduğu için tekrar yazılmaz.>

### One-Sentence Summary

### Simple Causal Explanation

### Mental Model

### Technical Translation

### Important Decisions

### What Changed?

### Evidence

### Unresolved Questions

## Learning Events

### LE-<learning-pass-id>-NN — <title>

```text
Event ID:
Category:               <primary> [secondary_tags: ...]
Work Units:
Problem:
Why It Matters:
Decision / Mechanism:   <SYSTEM_DESIGN veya DSA için 03 §10.2 / §10.3 zinciri>
Reusable Signal:
Evidence Status:        <VERIFIED (kind:pointer) · INFERRED · ASSUMED · UNRESOLVED>
Knowledge Priority:     <MUST_UNDERSTAND · USEFUL_TO_KNOW · IMPLEMENTATION_DETAIL>
Knowledge Gap:          <GAP · KNOWN · UNKNOWN · ->
Disposition:            <EXPERIENCE_ONLY · ULA_CANDIDATE · KNOWLEDGE_DEBT · IMPLEMENTATION_DETAIL · UNRESOLVED>
Open Question:          <opsiyonel>
```

## Disposition Summary

| Disposition | Event IDs |
|---|---|
| ULA_CANDIDATE | |
| EXPERIENCE_ONLY | |
| KNOWLEDGE_DEBT | <event_id → debt_id> |
| IMPLEMENTATION_DETAIL | |
| UNRESOLVED | |

## Implementation Details Suppressed

<Event olmayan değişikliklerin sayısı ve tek satır özeti.>

## Coverage Outcome Proposal

Handoff'ta yazılır. Ledger'a yazılmaz. Completion Commit güncel ULA status ile yeniden hesaplar (04 §11.4).

| work_unit_id | proposed_status | open_items |
|---|---|---|

## ULA Routing

Kurallar: 04 §4. Artifact içeriği buraya kopyalanmaz. `Artifact` = `ula/<event-id>/` altındaki dosya yolu.

| Event ID | Mode | Reason | User Override | ULA Status | Artifact |
|---|---|---|---|---|---|

## Map Sync

Pass `COMPLETE` olduktan sonra doldurulur. Post-completion enrichment. Coverage'ı ve pass status'u değiştirmez (05 §10).

| Event ID | Map Sync | Node IDs | Experience Persistence |
|---|---|---|---|

- `Map Sync`: `PENDING` · `COMPLETE` · `NOT_APPLICABLE` · `BLOCKED`
- `Experience Persistence`: `PENDING` · `COMPLETE` · `NOT_APPLICABLE` · `BLOCKED` (lifecycle: 06 §19)

## Knowledge Persistence

Persistence sonrası doldurulur. ID ve pointer tutar. İçerik kopyalanmaz. `event_id → experience_id` eşlemesinin deterministic kaydıdır (06 §15.1).

| Event ID | Concept ID | Experience ID | Decision Record | Note |
|---|---|---|---|---|

- `Concept ID`: `CH-...` · `UNASSIGNED` · `-`
- `Experience ID`: `EX-...` · `-`
- `Decision Record`: `DR-...` · `-`

## Pipeline Handoff

```text
Next Stage: <ULA ROUTING | COMPLETION | MAP SYNC | KNOWLEDGE PERSISTENCE | FINAL INTEGRITY | DONE>
```
