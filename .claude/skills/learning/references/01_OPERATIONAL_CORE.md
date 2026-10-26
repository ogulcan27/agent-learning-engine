# 01 — Operational Core

**Status:** Startup → Handoff IMPLEMENTED (Phase 3 + Phase 4). ULA Routing ve sonrası NOT IMPLEMENTED YET.

## Purpose

`/learning` run loop'unun genel akışını ve dur kurallarını tanımlar.

## Must Not

- Normal project work sırasında çalışmaz.
- Diğer protocol dosyalarının kurallarını tekrar etmez. Pointer verir.

---

## 1. Implemented boundary (Phase 4)

```text
/learning
↓
START
 1. STARTUP            config + state oku; yoksa initialization (02 §11)
 2. CONFIG CHECK       work_unit_source geçerli mi? (02 §3.3)
 3. INTEGRITY          ledger (07 §C) + queue §B (07 §E)
↓
COVERAGE
 4. DISCOVERY          current work units + Discovery Commit (02 §3–§6)
 5. COVERAGE CHECK     OPEN COVERAGE hesapla (02 §6)
↓
SCOPE
 6. SCOPE RESOLUTION   argüman veya menü + Scope Commit (02 §8)
↓
HUMAN SYNCHRONIZATION
 7. PASS OPEN + EVIDENCE READ + scope-level çıktı (03 §3–§7)
↓
LEARNING EVENT EXTRACTION
 8. filter + event model (03 §8–§10)
↓
KNOWLEDGE PRIORITY
 9. priority + knowledge gap (03 §11–§12)
↓
EVENT DISPOSITION
10. disposition + user checkpoint (03 §13, §16)
↓
HANDOFF
11. integrity (07 §E) + pass dosyası + queue §B (03 §14, §17)
↓
NEXT: ULA ROUTING      04_ULA_PROTOCOL.md — NOT IMPLEMENTED YET
```

## 2. Stop rules

| Durum | Davranış |
|---|---|
| State yok ve kullanıcı initialization'ı onaylamadı | Dur. Dosya oluşturma. |
| CONFIG ERROR | Dur. Hatayı göster. Fallback yapma. |
| Coverage integrity FAIL | Dur. Hatayı göster. Ledger'a yazma. |
| Source ambiguous | Kullanıcıya sor. Cevap yoksa dur. |
| OPEN COVERAGE boş ve argüman yok | "Açık coverage yok." de. Dur. |
| Event integrity (07 §E) FAIL | Pass dosyası ve queue §B yazma. Hatayı göster. Dur. |
| Sonraki protocol `NOT IMPLEMENTED YET` | Handoff'u göster (pass ID, disposition özeti, Next Stage). Adımın henüz implement edilmediğini bildir. Dur. Completion Commit yapma. |

## 3. Write rules

| Adım | Yazılan | Yazılmayan |
|---|---|---|
| Discovery / Scope | Ledger (Discovery Commit, Scope Commit) | — |
| Handoff | `docs/learning/passes/<learning-pass-id>.md` (`IN_PROGRESS`), queue §B `OPEN` debt | Ledger |
| Completion | Ledger `COVERED` / `PARTIAL` / `NOT_LEARNING_RELEVANT` | — |

- Ledger yalnız Discovery Commit, Scope Commit ve Completion Commit ile yazılır (02 §10).
- Phase 4 sınırında Completion Commit erişilemez. Bu nedenle `COVERED`, `PARTIAL` ve `NOT_LEARNING_RELEVANT` yazılmaz. Pass dosyası yalnız öneri taşır (03 §15).
- Her ledger commit sonrası state ve queue §A yeniden üretilir.

## 4. Steps after handoff

NOT IMPLEMENTED YET. Sıra `SKILL.md` Bölüm 7'dedir.

## Authoritative Source

- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §3A, §16, §37, §41, §42, §48.
- Manual timing: Phase 1 audit, Q4 ve Q10.
