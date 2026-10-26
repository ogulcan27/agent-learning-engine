# 05 — MindMap Protocol

**Status:** NOT IMPLEMENTED YET (skeleton)
**Planned Phase:** Phase 6 (tentative)

## Purpose

Learning bilgisini semantic graph olarak tutar ve terminal-friendly MindMap olarak gösterir.

## Responsibility

- Semantic graph: node ve edge.
- X axis = doğal system / causal / data / reasoning / dependency flow.
- Y axis = seçilmiş node'un öğrenme derinliği.
- Recursive zoom ve parent context (breadcrumb).
- Markdown / text view.

## Inputs

- Learning pass çıktısı.
- Mevcut project map (`docs/learning/maps/`).

## Outputs

- Güncellenmiş semantic graph.
- Text / ASCII MindMap view.

## Must Not

- HTML üretmez (Phase 1 Q8).
- Dekoratif edge çizmez. Her edge bir relation type taşır.
- Depth'i horizontal axis'e koymaz.
- Harici graph tool'una bağımlı olmaz. Semantic graph bu skill'in kendi sistemidir.

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §21–§26, §46, §47.
- `ula/ULA_SPECIFICATION.md` §5, §13, §14, §31.
- Phase 1 audit: Bölüm 5.
