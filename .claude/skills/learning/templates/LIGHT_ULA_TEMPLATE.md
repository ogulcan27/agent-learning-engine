# Light ULA

> Template: `.claude/skills/learning/templates/LIGHT_ULA_TEMPLATE.md`
> Target: `docs/learning/passes/<learning-pass-id>/ula/<event-id>/LIGHT_ULA.md`
> Rules: `references/04_ULA_PROTOCOL.md` §6
> Dil: Türkçe açıklama. Canonical technical term İngilizce kalabilir.

## Metadata

```yaml
event_id: LE-<learning-pass-id>-NN
topic: <canonical technical term>
mode: LIGHT
status: IN_PROGRESS        # IN_PROGRESS | NEEDS_REVISION | COMPLETE | BLOCKED
updated_at: YYYY-MM-DD
```

## L0 — Local Map

<Bu kavram büyük resimde nerede duruyor? Kısa yerel harita. Persistent MindMap değildir.>

## L1 — Simple Explanation

<Kısa cümleler. Jargonsuz ana fikir.>

## L2 — Mechanism

<Adım adım nasıl çalışıyor? Okların anlamı açık.>

## L3 — Theory

<!-- Yalnız gerekirse. Mekanizmayı tekrar etme. Nedenini açıkla. -->

## Boundary / Confusion Check

<!-- Yalnız gerekirse. A ≠ B ve "Ne değildir?" -->

## Retrieval

<2–4 soru. System Design veya DSA retrieval soruları: 04 §8.>

## Reference

<!-- Yalnız gerekirse. Sayı, kaynak, edge case. Outside knowledge: GENERAL THEORY etiketi. -->

## Self-Check

| # | Kontrol | Sonuç |
|---|---|---|
| 1 | Whole / local context (L0) var | PASS / FAIL |
| 2 | Simple explanation (L1) var | PASS / FAIL |
| 3 | Mechanism (L2) açık | PASS / FAIL |
| 4 | Theory nedeni açıklıyor, mekanizmayı tekrar etmiyor | PASS / FAIL / N/A |
| 5 | Gereksiz jargon yok | PASS / FAIL |
| 6 | Gerekli confusion boundary var | PASS / FAIL / N/A |
| 7 | Retrieval sorusu var | PASS / FAIL |
| 8 | Reference ana içeriğe sızmamış | PASS / FAIL |
