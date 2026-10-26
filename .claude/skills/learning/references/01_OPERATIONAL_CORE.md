# 01 — Operational Core

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 3 (tentative)

## Purpose

`/learning` run loop'unun genel akış kurallarını tanımlar.

## Responsibility

- Adımların sırasını ve adımlar arası geçiş koşullarını tanımlar.
- Hangi adımın atlanabileceğini tanımlar.
- Hata ve dur kurallarını tanımlar.

## Inputs

- `$ARGUMENTS`
- `docs/learning/state/LEARNING_CONFIG.md`
- `docs/learning/state/LEARNING_STATE.md`

## Outputs

- Sıradaki adımın kararı.
- Kullanıcıya kısa durum özeti.

## Must Not

- Normal project work sırasında çalışmaz.
- Diğer protocol dosyalarının kurallarını tekrar etmez. Pointer verir.

## Authoritative Source

- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §3A, §37, §41, §42, §48 (project-learning domain).
- Manual timing: Phase 1 audit, Q4 ve Q10.
