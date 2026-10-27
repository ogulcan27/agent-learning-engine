# PHASE 6 — Hierarchy Amendment

**Tarih:** 2026-10-27
**Tür:** Architecture amendment. Yeni phase değildir.
**Kapsam:** Phase 6 raporu D-02.

## 1. Problem

Phase 6 hierarchy'yi yalnız `parent_id` içinde tutuyordu. `PART_OF` edge yasaktı.

Bir concept birden fazla semantic domain'e aitse ikinci membership için `DEPENDS_ON` veya `USES` önerildi. Bu yanlış relation kullanımıdır. Taxonomic / compositional membership dependency veya kullanım ilişkisi değildir.

## 2. Decision

```text
parent_id     = PRIMARY NAVIGATION PARENT       (en fazla bir)
PART_OF edge  = SECONDARY SEMANTIC MEMBERSHIP   (sıfır veya daha fazla)
```

- Her membership tek yerde saklanır. Duplicate truth yoktur.
- `node.parent_id = X` + `node PART_OF X` → FAIL (aynı membership iki kez).
- `node.parent_id = X` + `node PART_OF Y` → geçerli.
- Primary ve secondary bağlar birlikte combined hierarchy oluşturur. Combined hierarchy acyclic olmalıdır.
- Diğer relation cycle'ları (ör. karşılıklı `DEPENDS_ON`) hierarchy FAIL değildir.
- Breadcrumb ve recursive zoom yalnız `parent_id` zincirini kullanır. Secondary membership local view'da `Also Part Of:` (üye tarafında) ve `Secondary Members:` (domain tarafında) olarak görünür.
- `DEPENDS_ON` / `USES` yalnız gerçek ilişki varsa eklenir. Membership yerine üretilmez.

## 3. Files Changed

| Dosya | Değişiklik |
|---|---|
| `.claude/skills/learning/references/05_MINDMAP_PROTOCOL.md` | §5 yeniden yazıldı (§5.1–§5.4); `parent_id` tanımı; `PART_OF` relation açıklaması; §12.3 legend; §13 local view (`Also Part Of`, `Secondary Members`, breadcrumb kuralı) |
| `.claude/skills/learning/templates/SEMANTIC_GRAPH_TEMPLATE.md` | Header notu; `PART_OF` relation vocabulary içinde yeniden geçerli. Diğer alanlar değişmedi. |
| `.claude/skills/learning/templates/KNOWLEDGE_MAP_TEMPLATE.md` | Legend: `↳` = primary child |
| `.claude/skills/learning/references/07_INTEGRITY_CHECKS.md` | M-08, M-09, M-21 yeniden tanımlandı |
| `docs/audit/PHASE_6_MINDMAP_REPORT.md` | Status, D-02 (AMENDED), OI-03 (KAPANDI), §5 ve §14 notları |
| `docs/audit/PHASE_6_MINDMAP_TESTS.md` | Güncel toplam notu |

## 4. Integrity Changes

| ID | Önce | Sonra | Sonuç |
|---|---|---|---|
| M-08 | `parent_id` hierarchy cycle | Combined hierarchy cycle (`parent_id` + `PART_OF` edge) | FAIL |
| M-09 | Node kendi parent'ı | Node kendi parent'ı veya kendi `PART_OF` hedefi | FAIL |
| M-21 | Edges tablosunda `PART_OF` satırı | Primary parent ayrıca `PART_OF` edge olarak yazılmış | FAIL |

Orphan (M-03, M-04), vocabulary (M-05, M-06, M-07) ve diğer kontroller değişmedi.

## 5. Tests

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | `parent_id = Domain-A` + `PART_OF Domain-B` | FAIL yok | PASS |
| B | `parent_id = Domain-A` + `PART_OF Domain-A` | M-21 FAIL | PASS |
| C | `A parent_id B` + `B PART_OF A` | M-08 FAIL | PASS |
| C2 | `A PART_OF B` + `B PART_OF A` | M-08 FAIL | PASS |
| D | `A PART_OF B` + `A PART_OF C` | FAIL yok | PASS |
| E | Kalman Filter: parent State Estimation, `PART_OF` Bayesian Filtering (sync ile) | Sync `COMPLETE`, temiz; breadcrumb `Project → State Estimation → Kalman Filter`; `Also Part Of: Bayesian Filtering`; `PART_OF` düz relation listesinde yok; domain view `Secondary Members: Kalman Filter`; primary children değişmez | PASS (6/6) |
| F | Secondary membership sync | Graph'ta yalnız `PART_OF` edge; `DEPENDS_ON` / `USES` üretilmedi | PASS |

Mevcut Phase 6 testi güncellendi: "Edges tablosunda `PART_OF` → M-21" artık geçersiz semantik. Yerine "self `PART_OF` → M-09" testi kondu.

Phase 6 toplam: **83/83 PASS** (71 önceki + 12 amendment).

Mutation check (geçici kopyalar):

| Mutation | Sonuç |
|---|---|
| `07` M-21 satırı silindi | 82/83. Test B FAIL. |
| `07` M-08 satırı silindi | 80/83. L, C, C2 FAIL. |

## 6. Regression

| Phase | Sonuç |
|---|---|
| Phase 3 coverage | 24/24 PASS |
| Phase 4 human sync | 46/46 PASS |
| Phase 5 ULA routing | 74/74 PASS |
| Phase 6 mindmap | 83/83 PASS |

Original source sha256: 15/15 aynı. Graphify yok. HTML yok. Commit yok.

## 7. Final Phase 6 Status

```text
PHASE 6 STATUS: FROZEN / PASS
PHASE 7 STATUS: READY
```
