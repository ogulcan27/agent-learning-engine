# 04 — ULA Protocol

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 5 (tentative)

## Purpose

KNOWLEDGE GAP olan learning event için Light ULA veya Full ULA seçer ve çalıştırır.

## Responsibility

- Light / Full ULA seçim kuralı.
- Light ULA tek geçiş akışı.
- Full ULA rol sırası: Architect → user review → Builder → Auditor.
- Retrieval.
- Canonical vocabulary ve alias eşleme.

## Inputs

- KNOWLEDGE GAP learning event'leri.
- Concept Home pointer'ları (varsa).

## Outputs

- Learning pass içeriği (`templates/LEARNING_PASS_TEMPLATE.md`).
- Retrieval soruları.

## Must Not

- ULA kurallarını değiştirmez veya tekrar yazmaz. `ula/` dosyalarına pointer verir.
- Full ULA rol dosyalarını aynı anda yüklemez.
- Mechanism'den önce theory, theory'den önce formalism vermez.
- Concept Home'da öğretilmiş teoriyi yeniden öğretmez.

## Authoritative Source

- ULA domain: `ula/ULA_SPECIFICATION.md`, `ula/LEARNING_ARCHITECT.md`, `ula/CONTENT_BUILDER.md`, `ula/LEARNING_AUDITOR.md`.
- Depth seçimi: `00_MASTER_SYSTEM_SPEC.md` §20, §35, §40, §50.
- Phase 1 audit: Bölüm 13, Q1.
