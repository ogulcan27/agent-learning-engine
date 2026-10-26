# 02 — Coverage Protocol

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 3 (tentative)

## Purpose

Work unit'lerin learning coverage durumunu kalıcı ve set-based biçimde yönetir.

## Responsibility

- Work unit discovery (universal priority, `work_unit_source`).
- Gap detection.
- Scope resolution menüsü.
- Coverage durumları: UNCOVERED, COVERED, PARTIAL, DEFERRED, SKIPPED_BY_USER, NOT_LEARNING_RELEVANT.
- Coverage update.

## Inputs

- `docs/learning/state/LEARNING_CONFIG.md`
- `docs/learning/state/COVERAGE_LEDGER.md`
- Project evidence: user scope, issue tracker, task / phase document, git history, other stable identifier.

## Outputs

- Gap listesi.
- Kullanıcının seçtiği scope.
- Güncellenmiş `COVERAGE_LEDGER.md` ve `LEARNING_QUEUE.md`.

## Must Not

- File modification time ile coverage kararı vermez.
- Chat context'i tek başına persistent source kabul etmez.
- Tek bir `last covered boundary` değerini coverage gerçeği kabul etmez.
- Seçilmeyen work unit'i kaybetmez. Seçilmeyen birim DEFERRED olur.

## Authoritative Source

- Phase 1 audit: Bölüm 7, 8, 8.1A, Bölüm 21 (Q4, Q5, Q11, Coverage model).
- Master kaynakta coverage kavramı yoktur (ABSENT). Bu protocol yeni bileşendir.
