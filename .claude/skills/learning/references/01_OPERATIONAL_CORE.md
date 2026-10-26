# 01 — Operational Core

**Status:** Startup → Scope Resolution IMPLEMENTED (Phase 3). Sonraki adımlar NOT IMPLEMENTED YET.

## Purpose

`/learning` run loop'unun genel akışını ve dur kurallarını tanımlar.

## Must Not

- Normal project work sırasında çalışmaz.
- Diğer protocol dosyalarının kurallarını tekrar etmez. Pointer verir.

---

## 1. Implemented boundary (Phase 3)

```text
/learning
↓
1. STARTUP            config + state oku; yoksa initialization (02 §11)
↓
2. CONFIG CHECK       work_unit_source geçerli mi? (02 §3.3)
↓
3. COVERAGE INTEGRITY ledger kontrolü (07 §C)
↓
4. DISCOVERY          current work units + Discovery Commit (02 §3–§6)
↓
5. COVERAGE CHECK     OPEN COVERAGE hesapla (02 §6)
↓
6. SCOPE RESOLUTION   argüman veya menü + Scope Commit (02 §8)
↓
7. [NEXT PROTOCOL]    03_HUMAN_SYNC_PROTOCOL.md
```

## 2. Stop rules

| Durum | Davranış |
|---|---|
| State yok ve kullanıcı initialization'ı onaylamadı | Dur. Dosya oluşturma. |
| CONFIG ERROR | Dur. Hatayı göster. Fallback yapma. |
| Coverage integrity FAIL | Dur. Hatayı göster. Ledger'a yazma. |
| Source ambiguous | Kullanıcıya sor. Cevap yoksa dur. |
| OPEN COVERAGE boş ve argüman yok | "Açık coverage yok." de. Dur. |
| Sonraki protocol `NOT IMPLEMENTED YET` | Selected scope'u göster. Adımın henüz implement edilmediğini bildir. Dur. Completion Commit yapma. |

## 3. Write rules

- Ledger yalnız Discovery Commit, Scope Commit ve Completion Commit ile yazılır (02 §10).
- Phase 3 sınırında Completion Commit erişilemez. Bu nedenle `COVERED`, `PARTIAL` ve `NOT_LEARNING_RELEVANT` yazılmaz.
- Her commit sonrası state ve queue §A yeniden üretilir.

## 4. Steps after scope resolution

NOT IMPLEMENTED YET. Sıra `SKILL.md` Bölüm 7'dedir.

## Authoritative Source

- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §3A, §37, §41, §42, §48.
- Manual timing: Phase 1 audit, Q4 ve Q10.
