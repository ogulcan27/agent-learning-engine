# 06 — Knowledge Persistence

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 7 (tentative)

## Purpose

General knowledge ile project experience'ı ayrı ve tekrarsız saklar.

## Responsibility

- One Concept — One Home.
- Hybrid model: Concept Home personal library'de, projede pointer.
- Library yoksa temporary local concept ve sonra promote.
- Experience Note, Decision Record (ADR, DSA Decision Record).
- Project Appearance ve project-specific delta.

## Inputs

- Learning pass çıktısı.
- `LEARNING_CONFIG.md → personal_library_path`.

## Outputs

- Concept Home veya pointer.
- Experience Note.
- Decision Record.

## Must Not

- Aynı teoriyi ikinci kez yazmaz. Delta ekler.
- Library yolunu hard-code etmez.
- Library yoksa hata vermez.

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §5, §8, §9, §32, §33, §38, §39, §45.
- `ula/ULA_SPECIFICATION.md` §17, §18.
- Phase 1 audit: Bölüm 11, Q2, Q12.
