# Decision Record — <short title>

> Template: `.claude/skills/learning/templates/DECISION_RECORD_TEMPLATE.md`
> Target: `docs/learning/experiences/<decision-id>.md`
> Rules: `references/06_KNOWLEDGE_PERSISTENCE.md` §16
> Role: Significant decision'ın reasoning'ini saklar. Her event için üretilmez.
> Type'a göre yalnız ilgili bölüm doldurulur. Diğer bölüm silinir.

## Identity

```text
Decision ID:    DR-xxxxxxxx
Type:           ADR
Event ID:       LE-<learning-pass-id>-NN
Experience ID:  EX-xxxxxxxx
Concept ID:     CH-xxxxxxxx
Project ID:     PRJ-xxxxxxxx
Date:           YYYY-MM-DD
```

- `Type`: `ADR` (SYSTEM_DESIGN) · `DSA_DR` (DSA)
- `Concept ID`: `CH-...` veya `UNASSIGNED`

## ADR

```text
Problem:
Constraints:
Alternatives:
Selected Solution:
Why:
Trade-offs:
Failure Modes:
Future Trigger:
```

## DSA_DR

```text
Problem Pattern:      <06 §17.3 vocabulary>
Naive Solution:
Bottleneck:
Candidates:
Chosen:
Complexity:
Trade-off:
Where Appeared:
Reusable Signal:
Concept Home:         personal:CH-... | local-temporary:CH-... | -
```

## Evidence

| Claim | Evidence Status | Evidence Ref |
|---|---|---|
