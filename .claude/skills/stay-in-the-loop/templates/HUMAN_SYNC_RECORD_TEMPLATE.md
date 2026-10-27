# Human Sync Record

> Template: `.claude/skills/stay-in-the-loop/templates/HUMAN_SYNC_RECORD_TEMPLATE.md`
> Target: `docs/learning/sync/records/<record-id>.md`
> Role: AUTHORITATIVE. Work unit başına sıkıştırılmış mental model.
> Rules: `references/08_HUMAN_SYNC_STATE.md` §4, §9. İçerik kuralları: `references/03_HUMAN_SYNC_PROTOCOL.md` §5–§7.
> Kod, uzun kaynak metin veya teori dersi yazılmaz.

## Header

```text
record_id: <HS-xxxxxxxx>
project_id: <LEARNING_CONFIG.project_id>
work_unit_id: <work_unit_id>
record_version: <n>
checkpoint: <git:xxxxxxxxxxxx | fp:xxxxxxxxxxxxxxxx>
updated_at: <YYYY-MM-DD>
```

## Purpose

<Problem> → <Action> → <Result>

## Why It Changed

<3–6 kısa cümle: Problem neydi? Neden önemliydi? Ne yaptık? Neden?>

## How It Works

```text
<INPUT → PROCESS → DECISION → OUTPUT veya doğal system / causal / data flow>
```

## Technical Translation

```text
"<basit anlam>" ↔ <Canonical Technical Term>
```

## Key Decisions

```text
Decision:
Alternatives:   <VERIFIED (ref) veya GENERAL THEORY>
Selected:
Why:
Trade-off:
```

## What Changed

```text
ÖNCE  → <system behaviour>
SONRA → <system behaviour>
```

## Dependencies

<önceki unit'ler ve neden; yoksa `Yok.`>

## Downstream Impact

<sonraki işin bu unit'ten neye bağlı olduğu>

## Open / Uncertain Points

<soru listesi veya `Yok.`>

## Evidence / Provenance

| Claim | Evidence Status |
|---|---|
| <iddia> | <VERIFIED (kind:pointer) · INFERRED · ASSUMED · UNRESOLVED> |
