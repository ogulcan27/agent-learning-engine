# Experience Note — <short title>

> Template: `.claude/skills/stay-in-the-loop/templates/EXPERIENCE_NOTE_TEMPLATE.md`
> Target: `docs/learning/experiences/<experience-id>.md`
> Rules: `references/06_KNOWLEDGE_PERSISTENCE.md` §15
> Role: Concept'in bu projede nasıl ve neden kullanıldığı. General theory tekrar edilmez.
> Evidence bir alanı desteklemiyorsa alan `UNRESOLVED` yazılır.

## Identity

```text
Experience ID:     EX-xxxxxxxx
Event ID:          LE-<learning-pass-id>-NN
Concept ID:        CH-xxxxxxxx
Project ID:        PRJ-xxxxxxxx
Project Name:      <name>
Work Unit IDs:     <id>; <id>
Category:          <SYSTEM_DESIGN | DSA | ...>
Decision Record:   -
Experience Map:    NONE
Map Status:        NOT_APPLICABLE
Concept Home Ref:  -
Created At:        YYYY-MM-DD
```

- `Concept ID`: `CH-...` veya `UNASSIGNED`
- `Concept Home Ref`: `personal:CH-...`, `local-temporary:CH-...` veya `-`
- `Experience Map`: `SYSTEM_DESIGN` · `DSA` · `NONE`
- `Map Status`: `WRITTEN` · `DEFERRED` · `NOT_APPLICABLE`

## Experience

```text
Problem:
Constraint:
Why It Appeared:
Alternatives:
Selected:
Why Selected:
Trade-off:
Failure Mode:
Observed Result:
Reusable Signal:
```

## DSA Detail

<!-- Yalnız Category: DSA. Diğerlerinde bu bölüm yoktur. -->

```text
Pattern:
Naive Solution:
Bottleneck:
Time Complexity:
Space Complexity:
Real System Use:
```

## Evidence

`03` §7 modeli. `VERIFIED` ref zorunlu. Claim status kaynak event'ten güçlü olamaz.

| Claim | Evidence Status | Evidence Ref |
|---|---|---|
