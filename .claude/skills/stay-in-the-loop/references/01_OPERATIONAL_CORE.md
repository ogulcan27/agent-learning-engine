# 01 — Operational Core

**Status:** Startup → Final Integrity → DONE IMPLEMENTED (Phase 3–8).

## Purpose

`/stay-in-the-loop` run loop'unun genel akışını ve dur kurallarını tanımlar.

## Must Not

- Normal project work sırasında çalışmaz.
- Diğer protocol dosyalarının kurallarını tekrar etmez. Pointer verir.

---

## 0. Active project root

Invariant: Bir `/stay-in-the-loop` çağrısı project state'i yalnız active project root içinde okur ve yazar.

```text
Project state = <ACTIVE_PROJECT_ROOT>/docs/learning/
```

Çözüm:

1. Çağrı başındaki Claude Code primary working directory değerini al.
2. Bu dizin bir git repository içindeyse `git rev-parse --show-toplevel` sonucunu kullan. Değilse dizinin kendisini kullan.
3. Sonucu kullanıcıya göster: `Active project: <klasör adı> (<root>)`.
4. Root çağrı boyunca sabittir. Shell `cd` veya environment güncellemesi root'u değiştirmez.

| Sinyal | Root kaynağı |
|---|---|
| Primary working directory (çağrı başı) | YES |
| Additional working directories | NO |
| Çağrı sırasında değişen shell cwd | NO |
| Skill base directory | NO |
| `personal_library_path` | NO |
| Personal library içeriği | NO |
| Example, audit veya historical artifact | NO |
| Önceki project adı, chat memory, example path | NO |
| Diskteki diğer repository'ler | NO |

- `NO` sinyali başka bir project'i seçmez, önermez ve okutmaz.
- Root içinde `docs/learning/state/` yoksa first run initialization bu root için başlar (02 §11). Başka project aranmaz.
- Root içinde work unit evidence yoksa başka dizine geçilmez.
- Primary working directory bilinmiyor veya erişilemiyorsa: `BLOCKED`. Dur. Fallback yapma.
- Personal library root'u değiştirmez (06 §2.3).

---

## 1. Run loop

```text
/stay-in-the-loop
↓
START
 1. STARTUP            active project root (01 §0); config + state oku; yoksa initialization (02 §11)
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
14. routing + resolution + delta + integrity (07 §P) + lock + atomic write (06 §5–§22.1)
↓                      post-completion enrichment; completion'ı geri alamaz
FINAL INTEGRITY
15. 07 §L.3: §C + §E + §U + §M + §P + §L → derived repair → tekrar check
↓                      sonuç PASS / PASS_WITH_WARNINGS → DONE; FAIL → DONE yok
DONE

Map komutları (`/stay-in-the-loop map ...`) bu akışı çalıştırmaz. Doğrudan 05 §15'e gider.
Persistence komutları (`concept`, `library`, `experiences`, `debt`) bu akışı çalıştırmaz. Doğrudan 06 §24'e gider.
`/stay-in-the-loop integrity` bu akışı çalıştırmaz. Doğrudan 07 §L.6'ya gider.
`/stay-in-the-loop sync ...` bu akışı çalıştırmaz. Doğrudan 08 §11'e gider. Human Sync sonrası STOP.
```

## 2. Stop rules

| Durum | Davranış |
|---|---|
| Active project root belirlenemedi | `BLOCKED`. Dur. Başka project seçme. |
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
| Personal library write lock alınamadı | Lock bilgisini göster (06 §22.1). Event persistence `BLOCKED`. Lock silme yalnız kullanıcı onayı ile. Diğer event'lere devam et. |
| Final integrity `FAIL` | Hatayı göster. Repair yapma. `DONE` deme. Authoritative artifact'i kullanıcı review eder. |

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
| Final integrity / `/stay-in-the-loop integrity` | Yalnız `DERIVED` artifact (07 §L.1): `LEARNING_STATE`, queue §A, `HORIZONTAL_MAP`, `LIBRARY_INDEX` | Bütün authoritative artifact |

- Ledger yalnız Discovery Commit, Scope Commit ve Completion Commit ile yazılır (02 §10).
- Her ledger commit sonrası state ve queue §A yeniden üretilir.

## 4. Steps after map sync

1. Knowledge Persistence: `06`. Event başına lock (personal write varsa) + atomic transaction.
2. Final Integrity: `07` §L.3. Sonuç `PASS`, `PASS_WITH_WARNINGS` veya `FAIL` (07 §L.2).

## 5. DONE

`DONE` anlamı: Bu Learning Pass için required pipeline ve blocking integrity checks tamamlandı.

- `DONE` yalnız final integrity `PASS` veya `PASS_WITH_WARNINGS` ise yazılır.
- `DONE`, bütün Knowledge Debt'in kapandığı anlamına gelmez. `OPEN` debt kalabilir.
- `DONE`, bütün post-completion enrichment'ın bittiği anlamına gelmez. `Map Sync` veya `Experience Persistence` `BLOCKED` / `PENDING` kalabilir (07 L-08, WARNING).
- `DONE`, bir sonraki `/stay-in-the-loop` çağrısında açık coverage olmadığı anlamına gelmez. `DEFERRED` / `PARTIAL` birimler görünür kalır.

## Authoritative Source

- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §3A, §16, §36, §37, §41, §42, §48.
- Manual timing: Phase 1 audit, Q4 ve Q10.
