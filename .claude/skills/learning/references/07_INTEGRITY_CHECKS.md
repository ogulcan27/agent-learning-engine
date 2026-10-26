# 07 — Integrity Checks

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 8 (tentative)

## Purpose

`/learning` çağrısı sonunda project state tutarlılığını kontrol eder.

## Responsibility

- Ledger, queue ve state arasında tutarlılık.
- Pointer'ların hedefi var mı kontrolü.
- Skill klasörüne state yazılmadı kontrolü.

## Inputs

- `docs/learning/state/` dosyaları.
- Bu çağrıda yazılan dosyalar.

## Outputs

- Kısa PASS / FAIL listesi.

## Must Not

- Öğretim içeriğinin learning quality audit'ini yapmaz. Bu iş `ula/LEARNING_AUDITOR.md` rolüne aittir.
- Hatalı state'i sessizce düzeltmez. Raporlar.

## Authoritative Source

- Phase 1 audit: Bölüm 15.1, 17 (M-16), 18.
- Content audit: `ula/LEARNING_AUDITOR.md`.
