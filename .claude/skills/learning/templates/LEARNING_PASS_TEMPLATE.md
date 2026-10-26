# Learning Pass

> Template: `.claude/skills/learning/templates/LEARNING_PASS_TEMPLATE.md`
> Target: `docs/learning/passes/<learning-pass-id>.md`
> Rules: `references/03_HUMAN_SYNC_PROTOCOL.md`
> Role: Pipeline handoff artifact. Event kaydı burada tutulur. Disposition listeleri yalnız event ID verir.

## Metadata

```yaml
learning_pass_id: LP-YYYYMMDD-NN
date: YYYY-MM-DD
selected_scope: [<work_unit_id>, ...]
coverage_source: <resolved work_unit_source>
pass_status: IN_PROGRESS        # IN_PROGRESS | COMPLETE
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

Ledger'a yazılmaz. Completion Commit bu öneriyi kullanır (03 §15).

| work_unit_id | proposed_status | open_items |
|---|---|---|

## Pipeline Handoff

```text
Next Stage: ULA ROUTING
```
