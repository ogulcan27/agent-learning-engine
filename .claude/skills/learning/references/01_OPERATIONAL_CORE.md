# 01 — Operational Core

**Status:** Startup → Final Integrity IMPLEMENTED (Phase 3–7).

## Purpose

`/learning` run loop'unun genel akışını ve dur kurallarını tanımlar.

## Must Not

- Normal project work sırasında çalışmaz.
- Diğer protocol dosyalarının kurallarını tekrar etmez. Pointer verir.

---

## 1. Run loop

```text
/learning
↓
START
 1. STARTUP            config + state oku; yoksa initialization (02 §11)
 2. CONFIG CHECK       work_unit_source geçerli mi? (02 §3.3)
 3. INTEGRITY          ledger (07 §C) + queue §B (07 §E) + active pass (07 §U)
 4. ACTIVE PASS CHECK  resume / new / abandon (04 §10)
↓                      resume → pass'in current_stage noktasına git
COVERAGE
 5. DISCOVERY          current work units + Discovery Commit (02 §3–§6)
 6. COVERAGE CHECK     OPEN COVERAGE hesapla (02 §6)
 7. SCOPE RESOLUTION   argüman veya menü + Scope Commit (02 §8); active pass overlap → CONFLICT (04 §10.3)
↓
HUMAN SYNC
 8. PASS OPEN + EVIDENCE READ + scope-level çıktı (03 §3–§7)
↓
EVENTS
 9. extraction + priority + disposition + handoff (03 §8–§17)
↓
ULA ROUTING
10. early completion check (04 §3) → ULA yoksa 12'ye git
11. mode routing (04 §4) → LIGHT (04 §6) / FULL (04 §7), event başına sırayla
↓
COMPLETION
12. unit bazında Completion Commit + pass sonucu (04 §11)
↓                      pass COMPLETE değilse burada dur
MAP SYNC
13. eligibility + identity + delta + integrity (07 §M) + graph write + view (05 §6–§12)
↓                      post-completion enrichment; completion'ı geri alamaz
KNOWLEDGE PERSISTENCE
14. routing + resolution + delta + integrity (07 §P) + atomic write (06 §5–§22)
↓                      post-completion enrichment; completion'ı geri alamaz
FINAL INTEGRITY
15. 07 §C + §E + §U + §M + §P
↓
DONE

Map komutları (`/learning map ...`) bu akışı çalıştırmaz. Doğrudan 05 §15'e gider.
Persistence komutları (`concept`, `library`, `experiences`, `debt`) bu akışı çalıştırmaz. Doğrudan 06 §24'e gider.
```

## 2. Stop rules

| Durum | Davranış |
|---|---|
| State yok ve kullanıcı initialization'ı onaylamadı | Dur. Dosya oluşturma. |
| CONFIG ERROR | Dur. Hatayı göster. Fallback yapma. |
| Coverage integrity FAIL | Dur. Hatayı göster. Ledger'a yazma. |
| Source ambiguous | Kullanıcıya sor. Cevap yoksa dur. |
| OPEN COVERAGE boş ve argüman yok | "Açık coverage yok." de. Dur. |
| Active pass var ve kullanıcı seçim yapmadı | Resume / new / abandon sor. Cevap yoksa dur. |
| Event integrity (07 §E) FAIL | Pass dosyası ve queue §B yazma. Dur. |
| ULA / pass integrity (07 §U) FAIL | Stage geçişi ve Completion Commit yapma. Dur. |
| `pass_status: WAITING_USER` | Kullanıcı kararını iste. Pass'i kaydet. Dur. |
| `pass_status: BLOCKED` | Eksik evidence / artifact'i göster. Dur. |
| Map integrity (07 §M) FAIL veya identity AMBIGUOUS | Graph yazma. Event `map_sync_status: BLOCKED`. Coverage ve pass değişmez. Dur. |
| Persistence integrity (07 §P) FAIL, AMBIGUOUS veya CONFLICT | Write yok. Event persistence `BLOCKED`. Coverage, pass ve graph değişmez. Diğer event'lere devam et. |
| Personal library `UNCONFIGURED` ve personal write gerekli | 06 §2.2 seçeneklerini sor. Cevap yoksa event `PENDING`. Dur. |
| Final integrity FAIL | Hatayı göster. `DONE` deme. |

## 3. Write rules

| Adım | Yazılan | Yazılmayan |
|---|---|---|
| Discovery / Scope | Ledger (Discovery Commit, Scope Commit) | — |
| Handoff | `passes/<learning-pass-id>/LEARNING_PASS.md`, queue §B `OPEN` debt | Ledger |
| ULA | `passes/<learning-pass-id>/ula/<event-id>/`, pass routing tablosu ve metadata | Ledger |
| Completion | Ledger `COVERED` / `PARTIAL` / `NOT_LEARNING_RELEVANT`; pass status | — |
| Map sync | `maps/SEMANTIC_GRAPH.md` (delta, atomic), `maps/HORIZONTAL_MAP.md` (view), pass `## Map Sync` tablosu | Ledger, pass status, `current_stage` |
| Persistence | Personal: Concept Home, Registry, Experience Map, Index. Project: `concepts/`, `experiences/`, graph `home_ref`, queue §B debt status, pass `Experience Persistence` + `## Knowledge Persistence` | Ledger, pass status, `current_stage` |
| Abandon | Pass `pass_status: ABANDONED` | Ledger, queue §B |

- Ledger yalnız Discovery Commit, Scope Commit ve Completion Commit ile yazılır (02 §10).
- Her ledger commit sonrası state ve queue §A yeniden üretilir.

## 4. Steps after map sync

1. Knowledge Persistence: `06`. Event başına atomic transaction.
2. Final Integrity: `07` §C, §E, §U, §M, §P. FAIL yoksa run `DONE`.

§L Learning State Integrity henüz implement edilmedi. Final integrity'yi durdurmaz.

## Authoritative Source

- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §3A, §16, §36, §37, §41, §42, §48.
- Manual timing: Phase 1 audit, Q4 ve Q10.
