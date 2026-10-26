# 03 — Human Synchronization Protocol

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 4 (tentative)

## Purpose

Seçilen scope içindeki AI çalışmasını insanın yönetebileceği minimum yeterli mental modele sıkıştırır.

## Responsibility

- Human Synchronization çıktısı.
- Knowledge Priority: MUST UNDERSTAND / USEFUL TO KNOW / IMPLEMENTATION DETAIL.
- Learning Event extraction: EXPERIENCE ONLY veya KNOWLEDGE GAP.
- Knowledge Debt kaydı.

## Inputs

- Seçilen scope (work unit listesi).
- Project evidence (kod, doküman, commit, issue).

## Outputs

- `templates/HUMAN_SYNC_TEMPLATE.md` formatında çıktı.
- Learning event listesi.
- Knowledge Debt kayıtları (`LEARNING_QUEUE.md`).

## Must Not

- Bütün işi öğretmez. Yalnız minimum yeterli mental model üretir.
- Dosya listesi yerine sistem davranışını anlatır.
- IMPLEMENTATION DETAIL için ULA başlatmaz.
- Knowledge Debt ile Deferred Work Unit'i karıştırmaz.

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §14, §15, §16, §17, §18, §19, §36.
- Phase 1 audit: Bölüm 9, 10, Q12.
