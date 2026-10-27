# PHASE 6 — MindMap / Semantic Graph Tests

**Tarih:** 2026-10-27
**Yöntem:** Deterministic synthetic simulation.
**Neden:** Gerçek project state oluşturulmaz.

## Test düzeneği

- Reference model: `05_MINDMAP_PROTOCOL.md` kurallarının küçük bir Python modeli.
- Model şu değerleri doğrudan skill dosyalarından parse eder:
  - `05` §3.2 node type, §3.3 node status, §4.1 relation vocabulary,
  - §6 eligibility tablosu, §7 identity step sırası, §7.1 merge kuralları,
  - `07` §M içindeki aktif check ID'leri (bir satır silinirse o check devre dışı kalır),
  - `templates/SEMANTIC_GRAPH_TEMPLATE.md` node ve edge kolonları.
- Graph Markdown tablolarına yazılır ve tekrar okunur (roundtrip).
- Sync atomiktir: model aday graph'ı kopya üzerinde kurar, integrity sonrası döner. Orijinal graph değişmez.
- Node ID üretimi seed'li random kaynak kullanır. Testler deterministic'tir.
- Judgment girdileri fixture'dan gelir: aday node / edge, meaning eşdeğerliği (`short_meaning` eşitliği), reusable signal.
- Script'ler session scratchpad içindedir. `run_safe.py` her senaryoyu ayrı çalıştırır; çöken senaryo FAIL sayılır.

## Senaryolar ve sonuçlar

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | İlk build: Queue + Background Worker | root + 3 node; `USES`, `NEXT` edge; version 1; sync `COMPLETE`; appearance tek; integrity temiz; root map `[Async Processing] (+2)`; orijinal graph değişmedi | PASS (8/8) |
| B | İkinci pass: Consumer Lag | Queue ID reuse; yalnız +1 node, +1 edge; version 2; appearances `LP-1; LP-2` | PASS (4/4) |
| C | Aynı pass tekrar sync | node / edge sayısı aynı; appearance duplicate yok; version aynı; ilk pass re-sync no-op | PASS (5/5) |
| D | Aynı meaning ile Queue | Aynı `node_id`; yeni node yok | PASS (2/2) |
| E | İki farklı `State` meaning | `BLOCKED`; graph değişmez | PASS (2/2) |
| F | Async Queue → Job Queue | Aynı `node_id`; eski isim alias; eski isim alias üzerinden aynı node'a çözülür | PASS (3/3) |
| G | Knowledge Debt: Vector Index | `DEBT`; depth `-`; `debt_id` var; map'te `(DEBT)`; `debt_id` yoksa M-20 FAIL; sonra ULA COMPLETE → `ACTIVE`, aynı ID | PASS (6/6) |
| H | IMPLEMENTATION_DETAIL | `NOT_APPLICABLE`; graph değişmez | PASS |
| I | UNRESOLVED | Pass `COMPLETE` değil → sync yok; `COMPLETE` pass'te bile WAIT; sahte ACTIVE node → M-19 FAIL | PASS (3/3) |
| J | `MAGICALLY_CONNECTS` | Sync `BLOCKED`, version aynı; M-05 FAIL | PASS (2/2) |
| K | Orphan edge | M-04 FAIL; delta içinde orphan → `BLOCKED` | PASS (2/2) |
| L | A PART_OF B, B PART_OF A | M-08 FAIL; self parent M-09 FAIL | PASS (2/2) |
| M | Karşılıklı `DEPENDS_ON` | FAIL yok | PASS |
| N | 30 node (12 domain) | Root map 4–10 block; kalan `… +N block` özeti | PASS (3/3) |
| O | Consumer Lag zoom | Breadcrumb `Project → Async Processing → Queue → Consumer Lag`; local children; relation token ile | PASS (3/3) |
| P | Queue L1/L2; L3 istendi | `L3 unavailable. Mevcut: L1, L2.`; L2 → artifact pointer; içerik olmadan depth → M-14 FAIL | PASS (3/3) |
| Q | Delta: geçerli node + geçersiz edge | Version aynı; partial write yok; `LE-22 BLOCKED`, `LE-21 PENDING` | PASS (3/3) |
| R | Pass COMPLETE, map sync FAIL | Sync `BLOCKED`; pass `COMPLETE`, ledger `COVERED` kalır | PASS (2/2) |
| S | Graph v4, view v3 | M-16 WARNING; regeneration sonrası temiz; view v5 → M-15 FAIL | PASS (3/3) |

**A–S: 58/58 PASS.**

## Ek testler

| Test | Beklenen | Sonuç |
|---|---|---|
| Markdown roundtrip | Graph aynı kalır | PASS |
| Node ID formatı | `KN-` + 8 hex | PASS |
| ID isimden türetilmez | Aynı isim, farklı graph → farklı ID | PASS |
| ID collision | Mevcut ID atlanır | PASS |
| Vocabulary | 8 node type, 3 status, 12 relation | PASS (3/3) |
| Edges tablosunda `PART_OF` | M-21 FAIL | PASS |
| Duplicate semantic edge | M-11 FAIL | PASS |
| `SUPERSEDED` pointer yok | M-10 FAIL | PASS |
| Sync `COMPLETE`, event graph'ta yok | M-18 FAIL | PASS |
| Duplicate appearance | M-17 FAIL | PASS |
| View bilinmeyen node gösteriyor | M-12 WARNING | PASS |

**Ek: 13/13 PASS. Toplam: 71/71 PASS.**

Amendment sonrası: eski "PART_OF edge row → M-21" testi yeni semantiğe göre "self PART_OF → M-09" ile değiştirildi. 12 amendment testi eklendi. Güncel toplam: **83/83 PASS**. Ayrıntı: `PHASE_6_HIERARCHY_AMENDMENT.md`.

Testler ilk çalıştırmada geçti. Bu nedenle parse edilen kurallar ve üretilen view'lar elle kontrol edildi: 22 check aktif, 7 identity step doğru sırada, 6 merge kuralı, 7 eligibility satırı. Root map ve local zoom çıktıları beklenen biçimde.

## Mutation check

Geçici kopyalar üzerinde. Diff yalnız hedef satırları içerir (line ending farkı hariç). Orijinal runtime dosyaları değişmedi.

| Mutation | Değişiklik | Sonuç |
|---|---|---|
| M1 | Orphan edge validation kaldırıldı (`07` M-04 satırı) | 65/71. K, Q, R FAIL: orphan edge graph'a yazıldı. |
| M2 | PART_OF cycle validation kaldırıldı (`07` M-08 satırı) | 70/71. L FAIL. |
| M3 | Idempotent merge bozuldu (`05` §7.1 `source_event_ids`, `project_appearances`: UNION → APPEND) | 6/27. A'da duplicate appearance (M-17) sync'i blokladı; sonraki senaryolar zincirleme düştü. |

## Regression

| Phase | Sonuç |
|---|---|
| Phase 3 coverage | 24/24 PASS |
| Phase 4 human sync | 46/46 PASS |
| Phase 5 ULA routing | 74/74 PASS |

## Kapsam dışı

- Gerçek pass ve ULA artifact'lerinden node / edge çıkarımı (judgment; fixture ile verildi).
- Meaning eşdeğerliği kararı (judgment; checkpoint ile kullanıcıya sorulur).
- Concept Home, Experience Map, cross-project graph (Phase 7).
