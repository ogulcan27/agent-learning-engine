# PHASE 5 — ULA Routing + Light/Full ULA + Pass Resume + Early Completion Report

## 1. Status

**PHASE 5 STATUS: PASS**
**PHASE 6 STATUS: READY**

Implemented boundary:

```text
START → COVERAGE → HUMAN SYNC → EVENTS → ULA ROUTING → LIGHT / FULL → COMPLETION
→ [MINDMAP / KNOWLEDGE PERSISTENCE: NOT IMPLEMENTED YET → STOP]
```

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `.claude/skills/learning/references/04_ULA_PROTOCOL.md` | Skeleton → IMPLEMENTED (12 bölüm) |
| `.claude/skills/learning/templates/LIGHT_ULA_TEMPLATE.md` | Yeni |
| `.claude/skills/learning/templates/LEARNING_PASS_TEMPLATE.md` | Metadata genişletildi; ULA Routing tablosu; yeni target path |
| `.claude/skills/learning/references/03_HUMAN_SYNC_PROTOCOL.md` | Yalnız pointer: pass klasör yolu, resume ve completion `04`'e taşındı |
| `.claude/skills/learning/references/07_INTEGRITY_CHECKS.md` | §U eklendi (U-01…U-18); E-10 path |
| `.claude/skills/learning/references/01_OPERATIONAL_CORE.md` | Flow Completion'a kadar; stop ve write rules |
| `.claude/skills/learning/SKILL.md` | Router 8–10 IMPLEMENTED; guard MindMap'te; `resume` / `new` / `abandon` argümanları; load map |
| `docs/audit/PHASE_5_ULA_ROUTING_TESTS.md` | Yeni |
| `docs/audit/PHASE_5_ULA_ROUTING_REPORT.md` | Yeni |

Değişmeyen: `02_COVERAGE_PROTOCOL.md`, `05`, `06`, `ula/` dosyaları, original sources.

## 3. ULA Role

- ULA bir Learning Content Protocol'dür. Öğrenilmesine karar verilmiş bilgiyi doğru zihinsel sırayla öğretir.
- Discovery, event extraction, priority ve persistence yapmaz.
- Canonical order L0 → L1 → L2 → L3 → L4 → Boundary → Retrieval → R. Mechanism before Theory before Formalism.
- DEPTH ≠ PROCESS: katman seçimi ile üretim süreci ayrı kavramlardır.

## 4. Light ULA

- Tek geçiş: L0 Local Map → L1 → L2 → (L3) → (Boundary) → Retrieval → (R) → Self-Check.
- L4 default açılmaz. Formalism gerekirse Full önerilir.
- Rol dosyası yüklenmez. Architect / Builder / Auditor stage'i yok.
- 8 maddelik self-check. FAIL → bir kez düzelt. Aynı FAIL → `BLOCKED`.
- Artifact: `templates/LIGHT_ULA_TEMPLATE.md` → `ula/<event-id>/LIGHT_ULA.md`.
- L0 Local Map yalnız orientation içindir. Persistent MindMap değildir.

## 5. Full ULA

- Project Brief → Architect → Human Review → Builder → Auditor → freeze / revision routing.
- Rol sınırları `ula/` dosyalarında kaldı. Bu phase onları değiştirmedi.
- Review gate: architecture otomatik freeze edilmez. approve / revise / reject. Approve `approved_by: user` + `approved_at` yazar.
- Audit routing Auditor'ın Freeze Recommendation değerlerini kullanır:
  - READY TO FREEZE → `COMPLETE`
  - FREEZE AFTER MINOR FIXES → Builder minor fix → `COMPLETE`
  - REVISION REQUIRED → Builder revision → Audit
  - ARCHITECTURE REVISIT REQUIRED → Architect → Review → Builder → Audit
- Revision limit: her route türü event başına bir kez. Tekrar → `BLOCKED`.

## 6. Routing Rules

- Sıra: explicit user override → Full trigger check → Light default.
- 12 canonical Full trigger. Trigger evidence ile desteklenmezse sayılmaz.
- Bilgi yetersizse `ROUTING UNCERTAIN` → `WAITING_USER`.
- User override en yüksek authority. Light override + Full trigger → sınır bir kez açıklanır (U-17 WARNING). Seçim değiştirilmez.
- Routing kaydı pass içinde tek tablo: Event ID, Mode, Reason, User Override, ULA Status, Artifact (pointer).

## 7. Pass Lifecycle

- Pass status: `IN_PROGRESS` · `WAITING_USER` · `BLOCKED` · `COMPLETE` · `ABANDONED`.
- ULA status: `PENDING` · `WAITING_USER` · `IN_PROGRESS` · `NEEDS_REVISION` · `COMPLETE` · `BLOCKED`.
- `current_stage`: 10 canonical değer.
- Stage geçişleri tek tabloda (`04` §5). Tabloda olmayan geçiş yapılmaz. Her geçişin bir `requires` koşulu var.
- Metadata: ID, status, stage, created_at, updated_at, scope, coverage source.

## 8. Resume / New / Abandon

- Startup'ta active pass taraması. Sessiz yeni pass yok.
- Explicit argüman (`resume`, `new`, `abandon <pass-id>`) varsa soru sorulmaz.
- Resume = continue, not regenerate. Aynı pass ID. `COMPLETE` / `FROZEN` artifact yeniden yazılmaz (U-14).
- New: active pass ile scope kesişimi → `CONFLICT`. İki active pass aynı unit'i içeremez (U-15).
- Abandon: ledger, `open_items`, Knowledge Debt, event ve artifact değişmez. Abandon sonrası ledger değişikliği → U-13 FAIL.

## 9. Early Completion

Phase 4 OI-03 çözüldü.

- `ULA_CANDIDATE = 0` ve `UNRESOLVED = 0` → doğrudan `COMPLETION`. ULA dosyası yüklenmez.
- Bütün unit'ler `NOT_LEARNING_RELEVANT` ise de geçerli.
- `UNRESOLVED > 0`, `ULA_CANDIDATE = 0` → önce kullanıcı kararı (resolve / defer / dismiss / reclassify). Karar yoksa Completion; ilgili unit `PARTIAL` kalır.

## 10. Coverage Completion

- Unit bazında. Scope-level tek status yok.
- Blocking tablosu: `EXPERIENCE_ONLY`, `KNOWLEDGE_DEBT` (§B `OPEN`), `IMPLEMENTATION_DETAIL`, `COMPLETE` ULA → bloklamaz. Açık ULA ve `UNRESOLVED` → bloklar.
- Sonuç: event yok → `NOT_LEARNING_RELEVANT`; bloklayan yok → `COVERED`; bloklayan var → `PARTIAL` + event ID'ler.
- Commit yalnız integrity PASS (§C, §E, §U) ise. Transition Phase 3 matrix'ine uyar (trigger `C`).
- ULA `COMPLETE` → event ID `open_items`'tan çıkar. Liste boşsa `PARTIAL → COVERED`.
- Pass `COMPLETE` yalnız açık item yoksa. Aksi halde `WAITING_USER` veya `BLOCKED`.

## 11. Artifact Structure

```text
docs/learning/passes/<learning-pass-id>/
├── LEARNING_PASS.md
└── ula/<event-id>/
    ├── LIGHT_ULA.md                                         (LIGHT)
    └── PROJECT_BRIEF.md, ARCHITECTURE.md, CONTENT.md, AUDIT.md   (FULL)
```

- Event başına tek mode klasörü. Mode değişirse eski artifact `superseded/` altına taşınır.
- Full artifact başında kısa header: event_id, artifact, artifact_status, approval, updated_at.
- Pass içine artifact içeriği kopyalanmaz.
- Dev repo içinde runtime pass oluşturulmadı.

## 12. Token Load Policy

- Light: `04` + Light template + gerekli evidence. `ula/` yüklenmez.
- Full: stage başına tek rol dosyası. Architect → (review: yalnız `ARCHITECTURE.md`) → Builder → Auditor.
- `ULA_SPECIFICATION.md` yalnız rol dosyası belirsiz kalırsa.
- Master ve `ula/examples/` default load dışında.
- Test: hiçbir stage iki rol dosyası yüklemiyor; master load tablosunda yok.

## 13. Integrity Rules

07 §U: 16 FAIL + 2 WARNING.

| FAIL | WARNING |
|---|---|
| U-01 mode · U-02 status/stage · U-03 duplicate routing/artifact · U-04 unknown event · U-05 Builder without Frozen Architecture · U-06 Auditor without Content · U-07 frozen without approval · U-08 Light core eksik · U-09 Light COMPLETE + failed self-check · U-10 Full COMPLETE without freeze-ready · U-11 COMPLETE + open_items · U-12 COMPLETE + pending ULA · U-13 abandon ledger değişikliği · U-14 resume regeneration · U-15 overlapping active passes · U-16 artifact path eksik | U-17 Light override + Full trigger · U-18 event BLOCKED |

## 14. Test Results

- 74/74 PASS (A–P: 53; ek: 21).
- İlk çalıştırma 69/71. İki FAIL test modelindeydi (tablo parser, load sırası). Root cause bulundu ve düzeltildi.
- Mutation: M1 review gate kaldır (61/66), M2 COMPLETE + open_items (69/73), M3 Builder frozen architecture olmadan (67/70). Üçü de yakalandı.
- M3 ilk çalıştırmada frozen-architecture gereksinimini tek başına test etmiyordu. Doğrudan test eklendi.
- Regression: Phase 3 24/24, Phase 4 46/46.
- Validation: source sha256 15/15 aynı; 53 `.md` UTF-8, BOM yok; `docs/learning/` yok; HTML yok; Graphify yok; personal path yok.

## 15. Deviations

| ID | Sapma | Gerekçe |
|---|---|---|
| D-01 | Pass yolu `passes/<id>.md` → `passes/<id>/LEARNING_PASS.md`; `03` ve `07` E-10'da path güncellendi | User'ın Phase 5 artifact yapısı. Yalnız pointer değişti; Phase 4 kuralları aynı. |
| D-02 | Completion, MindMap / Persistence'tan önce çalışır; router sırası değişti | User'ın akışı. `EXPERIENCE_ONLY` completion'ı bloklamaz; persistence coverage'a bağlı değil. |
| D-03 | Phase 4 OI-04 kapandı: `03` §3'teki basit "devam mı yeni mi" sorusu `04` §10 ile değiştirildi | Resume protokolü tek yerde. |
| D-04 | FREEZE AFTER MINOR FIXES → yeniden audit olmadan `COMPLETE` | Auditor'ın kendi tanımı. Sonsuz döngü riskini azaltır. |
| D-05 | Revision limit route türü başına bir | "Aynı sorun ikinci kez" kuralının deterministic hali. |
| D-06 | Full trigger kodları `SNAKE_CASE` | Parse edilebilir ve `routing_reason` içinde stabil. |
| D-07 | `superseded/` klasörü (mode değişimi) | Artifact silinmez; U-03 çakışması önlenir. |
| D-08 | `resume` / `new` / `abandon <pass-id>` argümanları | §15 "explicit komut varsa soru sorma" kuralı için. |
| D-09 | Full artifact header (metadata) ULA template'lerine eklenmedi; protokolde tanımlandı | `ula/` dosyaları ULA domain'ine ait; değiştirilmedi. |
| D-10 | UNRESOLVED "dismiss" → priority ve disposition `IMPLEMENTATION_DETAIL` + not | Mevcut vocabulary ile ifade edilir; yeni değer eklenmedi. |

## 16. Open Issues

| ID | Konu |
|---|---|
| OI-01 | Gerçek target project ile end-to-end çalışma yapılmadı. |
| OI-02 | Full trigger tanıma Claude judgment'ına dayanır. Kontrol: routing checkpoint. |
| OI-03 | `COMPLETE` pass'teki `EXPERIENCE_ONLY` event'lerin persistence durumu için marker yok. Phase 6/7 bunu tanımlamalı. |
| OI-04 | Revision limit sayacı `AUDIT.md` round geçmişinden okunur. Ayrı alan yok. |
| OI-05 | Concept Home okuma (kısa hatırlatma) Persistence phase'ine kadar yok. |
| OI-06 | Test script'leri session scratchpad içinde. Spec kalıcı dokümanda. |

## 17. Phase 6 Readiness

**READY.**

Phase 6 girdileri:

- `COMPLETE` pass ve event kayıtları (`LEARNING_PASS.md`).
- Light / Full artifact path'leri (MindMap linking için).
- Event ID ve debt ID formatları.
- Router guard MindMap adımında duruyor.

Phase 6 açık işleri: OI-03.
