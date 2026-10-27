# PHASE 7 — Knowledge Persistence Tests

**Tarih:** 2026-10-27
**Yöntem:** Deterministic synthetic simulation.
**Neden:** Gerçek project state veya gerçek personal library oluşturulmaz.

## Test düzeneği

- Reference model: `06_KNOWLEDGE_PERSISTENCE.md` kurallarının küçük bir Python modeli.
- Model şu değerleri doğrudan skill dosyalarından parse eder:
  - `06` §4 ID prefix'leri, §5 routing tablosu, §7 resolution sırası, §8.1 section eşlemesi, §8.2 provenance label'ları, §9 outcome / version tablosu, §13.1 home mode, §17.3 DSA pattern vocabulary, §19 status, §20 debt transition + guard, §22 atomic kuralları,
  - `07` §P içindeki aktif check ID'leri (bir satır silinirse o check devre dışı kalır),
  - template başlıkları ve kolonları: Concept Home, pointer, Experience Note, Decision Record, Registry, Index, SD / DSA map, queue §B, pass `## Map Sync` + `## Knowledge Persistence`, config.
- Graph için Phase 6 modeli (`graph_model.py`) kullanılır. `home_ref` update'i `07` §M ile de kontrol edilir.
- Her senaryo geçici fixture dizini kullanır: `project/` ve `library/`. Dosyalar Markdown olarak yazılır ve tekrar parse edilir.
- Write failure injection: belirli dosyaya write `OSError` verir.
- ID üretimi seed'li random. Testler deterministic.
- Judgment girdileri fixture'dan gelir: meaning eşdeğerliği (`Short Meaning` eşitliği), section karşılaştırması (`SAME` / `ADD` / `EXTEND` / `CONFLICT`), project experience varlığı.
- Script'ler session scratchpad içindedir. `run_safe.py` her senaryoyu ayrı çalıştırır; çöken senaryo FAIL sayılır.

## Senaryolar ve sonuçlar

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | ULA COMPLETE, yeni concept (Queue) | `CH-` 8 hex; registry satırı; personal Home (v1, PERSONAL, ULA-DERIVED); L3/L4 `N/A`; pointer (`personal:CH`, theory yok, absolute path yok); graph `home_ref = CH`, aynı node, version +1; tek appearance; Experience Note; index; integrity temiz; ledger değişmez | PASS (17/17) |
| B | Project B aynı concept | Aynı CH; tek registry satırı; theory değişmez ve tek dosyada; version aynı; yeni appearance; B'de yeni Experience Note; B graph `home_ref`; Project Count 2 | PASS (11/11) |
| C | Aynı event tekrar persistence | `COMPLETE` → no-op (snapshot aynı); zorla retry → duplicate appearance / note yok; version aynı; library byte'ları aynı | PASS (6/6) |
| D | Project delta (EXPERIENCE_ONLY, mevcut concept) | Theory ve version aynı; Experience Note CH ile; pointer `Local Delta`; appearance | PASS (5/5) |
| E | Mevcut L1/L2 + audited Full L3 | Aynı CH; L3 eklendi (ULA-DERIVED); version +1; L1 aynı; history `ENRICH`; index depth `L1; L2; L3` | PASS (8/8) |
| F | Çelişen L2 | `BLOCKED`; Home, registry, pointer, graph değişmez; kullanıcı seçenek 3 → boundary (USER-CONFIRMED), version +1, L2 overwrite yok | PASS (6/6) |
| G | Library `UNCONFIGURED` | Seçim yok / ertele → `PENDING`; local → `COMPLETE`; `Home Mode: LOCAL_TEMPORARY`; full Home project'te; library'de dosya yok; graph `home_ref`; note `local-temporary:CH`, map `DEFERRED` | PASS (10/10) |
| H | Sonra library configured → promotion | Aynı CH; global Home PERSONAL; project dosyası pointer; node ID'ler korunur; theory tek dosyada; version aynı + `PROMOTED`; deferred SD satırı yazıldı; integrity temiz | PASS (10/10) |
| I | EXPERIENCE_ONLY reusable decision | Experience Note; `concept_id: UNASSIGNED`; Concept Home yok; SD satırı `Concept Home: -` | PASS (4/4) |
| J | IMPLEMENTATION_DETAIL | `NOT_APPLICABLE`; hiçbir dosya değişmez | PASS (2/2) |
| K | KNOWLEDGE_DEBT (OPEN) | `NOT_APPLICABLE`; learned Home yok; debt `OPEN` / `UNASSIGNED`; DEBT node değişmez | PASS (5/5) |
| L | Debt sonra öğrenildi | Phase 6 map sync DEBT → ACTIVE (aynı node); persistence → debt `RESOLVED` (`resolution_ref`, `concept_home`); node ACTIVE, aynı ID, `home_ref`; `debt_id` history olarak kalır; integrity temiz | PASS (6/6) |
| M | Home var ama learning complete değil | Resolve isteği reddedilir; debt `OPEN` kalır; elle `RESOLVED` → P-12 FAIL | PASS (4/4) |
| N | SD Experience Map | Kolonlar template ile aynı; değerler doğru; note çözülür; note başına tek satır; theory yok | PASS (5/5) |
| O | DSA event (Top-K) | DSA kolonları; `Top-K`, `O(n log k)`, `O(k)`; pattern universal vocabulary içinde; `DSA_DR`; SD map'te satır yok | PASS (6/6) |
| P | DSA map'te SD note | P-22 FAIL | PASS |
| Q | Aynı event ikinci sync, pass mapping satırı kayıp | Event ID lookup ile aynı EX; note sayısı aynı; mapping geri yazıldı; aynı event için ikinci note → P-09 FAIL | PASS (4/4) |
| R | Graph `home_ref` bilinmeyen CH | P-08 FAIL | PASS |
| S | Home candidate geçerli, registry candidate geçersiz (alias collision) + registry write I/O hatası | `BLOCKED`; sebep P-06; yalnız pass status satırı değişti; ledger ve pass `COMPLETE` aynı; I/O hatasında rollback, Home registry'siz kalmaz; library integrity temiz | PASS (7/7) |
| T | Rename Queue → Message Queue | Aynı CH; eski ad alias; version +1; A ve B pointer'ları çözülür; eski ad ALIAS step ile aynı CH; FAIL yok, stale pointer label → P-24 WARNING | PASS (6/6) |

**A–T: 124/124 PASS.**

## Ek testler

| Grup | Kontroller | Sonuç |
|---|---|---|
| Vocabulary | 4 ID türü, 4 persistence status, 2 home mode, 4 provenance label, 6 resolution step, 28 §P check, 16 DSA pattern, config alanları, 3 debt transition, pointer template'te theory yok, note alanları, ADR / DSA_DR alanları, skill içinde absolute library path yok | PASS (13/13) |
| Project rename | `project_id` aynı kalır; yeni appearance yeni `project_name` taşır | PASS (2/2) |
| Index | Silinen `LIBRARY_INDEX.md` Home'lardan aynı içerikle yeniden üretilir | PASS |
| Unconfigured personal write | P-17 → `BLOCKED`; library'de dosya yok | PASS (2/2) |
| Promotion ID değişimi | P-19 → `BLOCKED`; library'de dosya yok | PASS (2/2) |
| Crafted integrity | P-01, P-03, P-04, P-05, P-07, P-10, P-11, P-15, P-16, P-18, P-20, P-23, P-26, P-27 (ref yok), P-27 (UNRESOLVED → VERIFIED), P-28, P-25 (bump without change), P-25 (change without bump), appearance-only → P-25 yok | PASS (19/19) |

**Ek: 39/39 PASS. Toplam: 163/163 PASS.**

İlk çalıştırmada 5 FAIL vardı. Beşi de test harness hatasıydı; protocol değişmedi:

| Hata | Kök neden | Düzeltme |
|---|---|---|
| F snapshot sayısı | `Store.snapshot` project ve library root'larında aynı relative path'i (`concepts/CH-....md`) tek key yaptı | Key'e root prefix (`P:` / `L:`) eklendi |
| J beklenti | Initial marker zaten `NOT_APPLICABLE`; dosya değişmemesi doğru davranış | Beklenti "hiçbir dosya değişmez" oldu |
| Provenance / DSA pattern parse | `ticks` regex boşluk kabul etmiyordu (`GENERAL THEORY`, `Fast Lookup`) | Regex'e boşluk eklendi |
| Pointer theory testi | `startswith("L")` `Local Delta` alanını yakaladı | `^L[0-4]` kontrolü |

Üretilen dosyalar elle kontrol edildi: Concept Home (provenance, appearances, source artifacts, change history), pointer, Experience Note, `DSA_DR`, SD / DSA map satırları, promotion sonrası pointer, DEBT → ACTIVE graph satırı ve `RESOLVED` debt.

## Mutation check

Geçici kopyalar üzerinde. Diff yalnız hedef satırları içerir. Orijinal runtime dosyaları değişmedi.

| Mutation | Değişiklik | Sonuç |
|---|---|---|
| M1 | Duplicate Concept Home prevention kaldırıldı (`06` §7 `NAME` satırı) | 132/147. Project B `AMBIGUOUS` → `BLOCKED`; Home reuse yok; B, C, D, N, T ve rename testleri FAIL. |
| M2 | Debt `RESOLVED` guard kaldırıldı (`06` §20 guard → `-`, `07` P-12 satırı) | 159/163. M: resolve kabul edildi, debt `RESOLVED`, P-12 yakalanmadı. |
| M3 | Atomic registry / home koruması kaldırıldı (`06` §22 `ALL_OR_NOTHING` → `SEQUENTIAL`, `RESTORE_PRE_IMAGES` → `NONE`) | 154/163. S: Home + registry + pointer partial write; I/O hatasında Home registry'siz kaldı; P-17 / P-19 senaryolarında library dosyaları yazıldı. |

## Regression

| Phase | Sonuç |
|---|---|
| Phase 3 coverage | 24/24 PASS |
| Phase 4 human sync | 46/46 PASS |
| Phase 5 ULA routing | 74/74 PASS |
| Phase 6 mindmap (amendment dahil) | 83/83 PASS |

## Kapsam dışı

- Gerçek ULA artifact'ten section çıkarma ve project-specific cümle ayıklama (judgment; fixture ile verildi).
- Meaning eşdeğerliği ve conflict kararı (judgment; checkpoint ile kullanıcıya sorulur).
- Gerçek dosya sisteminde çok-process eşzamanlı write.
- Global cross-project graph (scope dışı).
