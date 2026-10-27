# PHASE 8 — End-to-End Tests

**Tarih:** 2026-10-27
**Komut:** `uv run --no-project python tests/run_all.py`
**Kural:** Gerçek project state ve gerçek personal library oluşturulmaz. Her senaryo yeni geçici dizin kullanır. Development repository içinde `docs/learning/` yoktur.

## 1. Permanent Harness

Phase 3–7 test script'leri session scratchpad'den `tests/` altına taşındı. Kalıcıdır ve tekrar çalışır.

| Dizin | İçerik |
|---|---|
| `tests/common/` | `harness.py`: skill path, `report()`. `safe_run.py`: senaryo başına crash izolasyonu (crash → o senaryo FAIL). |
| `tests/phase3/`–`tests/phase7/` | Subsystem model + test script'i. Mantık korundu; yalnız import path, rapor ve geçici fixture dizini değişti. |
| `tests/integration/` | `lifecycle.py` (E2E driver), `final_integrity.py` (`07` §L modeli), `lock.py` (`06` §22.1 modeli), `files.py` (Markdown render / parse), `run_tests.py` (senaryolar). |
| `tests/static/` | Router, cross reference, portability, encoding, dil kontrolü. |
| `tests/mutation.py` | Geçici skill kopyasında bir kuralı bozar. Beklenen suite FAIL vermelidir. |
| `tests/run_all.py` | Bütün suite'ler + mutation check. Exit code 0 = PASS. |

Source of truth:

- Her model kuralı runtime dosyadan parse eder: `02` §9 matrix, `03` §13.1 rule table, `04` §5 transitions ve §11.2 blocking, `05` §6 / §7 / §7.1, `06` §5 / §7 / §8.1 / §9 / §20 / §22 / §22.1, `07` §C–§L check tabloları, template başlıkları.
- `07` §L modeli authority tablosunu (§L.1), result vocabulary'yi (§L.2) ve check tablosunu (§L.5) okur. Check satırı yoksa check çalışmaz. Severity ve rebuild hedefi satırdan gelir.
- `06` §22.1 lock modeli `acquire`, `on_existing`, `stale_lock`, `on_release_error` değerlerini ve `LOCK.md` alanlarını okur.
- Judgment girdileri fixture'dır: meaning eşdeğerliği, section `CONFLICT`, project experience.
- Dependency: yalnız Python standard library.

## 2. Subsystem Regression

| Suite | Kaynak test dokümanı | Sonuç |
|---|---|---|
| phase3 | `PHASE_3_COVERAGE_TESTS.md` (A–I + consistency) | 24/24 PASS |
| phase4 | `PHASE_4_HUMAN_SYNC_TESTS.md` (A–J + consistency) | 46/46 PASS |
| phase5 | `PHASE_5_ULA_ROUTING_TESTS.md` (A–P + consistency) | 74/74 PASS |
| phase6 | `PHASE_6_MINDMAP_TESTS.md` + `PHASE_6_HIERARCHY_AMENDMENT.md` (A–S, HA) | 83/83 PASS |
| phase7 | `PHASE_7_KNOWLEDGE_PERSISTENCE_TESTS.md` (A–T + 39 ek) | 163/163 PASS |

Sayılar kopyalanmadı. Suite'ler Phase 8 runtime dosyalarına karşı yeniden çalıştırıldı.

Phase 7 modelinde iki düzeltme yapıldı. İkisi de E2E zincirinde bulundu. Protocol metni zaten doğruydu:

| Bulgu | Kök neden | Düzeltme |
|---|---|---|
| Persistence pass dosyasındaki Human Sync, event ve routing bölümlerini siliyordu | Model pass dosyasını yalnız `## Map Sync` + `## Knowledge Persistence` ile yeniden yazıyordu; queue için yalnız §B | `replace_section`: yalnız sahip olunan bölüm değişir. Diğer bölümler byte-identical. |
| Map sync `BLOCKED` olan event için persistence `PENDING` değil `BLOCKED` döndü | Model bekleme kararını yalnız `concept_nodes` doluysa veriyordu; `BLOCKED` event'te node yoktur | `Map Sync` `PENDING` / `BLOCKED` → `PENDING` (`06` §5 notu). |

Phase 7 suite iki düzeltmeden sonra 163/163 PASS.

## 3. E2E Scenarios

Driver her aşamada ilgili phase modelini çağırır: coverage → human sync → ULA + completion → map sync → persistence (+ lock) → final integrity. State yalnız geçici Markdown dosyalarındadır.

| Test | Senaryo | Doğrulanan | Sonuç |
|---|---|---|---|
| A | Routine work | Event yok; `NOT_LEARNING_RELEVANT`; map boş; final `PASS`; library yazılmadı | PASS (6/6) |
| B | Light ULA golden path (SYSTEM_DESIGN) | Pass `COMPLETE`, ledger `COVERED`, map `COMPLETE`, persistence `COMPLETE`, final `PASS` (CHECK 1 boş), identity chain | PASS (6/6) |
| C | Full ULA + resume | Review'da `WAITING_USER`; yeni `/learning` → `ASK`; resume aynı pass ID ve stage; `PROJECT_BRIEF` tekrar yazılmadı; ULA `COMPLETE`; Home L0–L4; final `PASS` | PASS (9/9) |
| D | Coverage gap | 1–3 `COVERED`; 4–10 açık; `/latest` → 10; 4–9 `DEFERRED`; 10 tam pipeline; sonraki çağrıda 4–9 görünür; `pending` = 4–9; final `PASS` | PASS (9/9) |
| E | Knowledge Debt | `USEFUL_TO_KNOW` + GAP → debt `OPEN`; unit `COVERED`; `DEBT` node; persistence `NOT_APPLICABLE`; final `PASS`; sonra ULA → aynı node `ACTIVE`; debt `RESOLVED` (`concept_home` = node `home_ref`, `resolution_ref`); final `PASS` | PASS (9/9) |
| F | LOCAL_TEMPORARY → personal | Seçim yok → `PENDING`; local → `COMPLETE`, `LOCAL_TEMPORARY`; final `PASS`; library configured → promotion; aynı CH; Home personal, project pointer; graph `home_ref` aynı; theory tek dosyada; final `PASS` | PASS (9/9) |
| G | Map ambiguity | Aynı isim, farklı meaning → map `BLOCKED`; persistence `PENDING`; pass `COMPLETE`; ledger `COVERED`; final `PASS_WITH_WARNINGS`, CHECK 2 = yalnız L-08 | PASS (4/4) |
| H | Persistence conflict | `CONFLICT` → `BLOCKED`; Home byte-identical; pass `COMPLETE`; ledger `COVERED`; final `PASS_WITH_WARNINGS`, FAIL yok | PASS (4/4) |
| I | Abandon | LIGHT tamam, FULL review'da; completion → `PARTIAL` (`open_items` = FULL event); abandon → `ABANDONED`; ledger ve `open_items` korunur; final `PASS`; yeni pass aynı unit'i seçer ve `COVERED` yapar | PASS (6/6) |
| J | Derived corruption | `LEARNING_STATE` sayısı, stale `HORIZONTAL_MAP`, boş `LIBRARY_INDEX` → CHECK 1: L-01, L-18, L-19 WARNING; repair = 3 derived; CHECK 2 boş → `PASS`; authoritative dosyalar byte-identical | PASS (4/4) |
| K | Authoritative corruption | Note `Concept ID: CH-deadbeef` → L-22 FAIL; sonuç `FAIL`; repair yok; derived bozukluk da onarılmadı (hiçbir dosya değişmedi). Ledger duplicate `work_unit_id` → C-01 FAIL, repair yok | PASS (4/4) |
| L | Concurrent personal write | A lock tutar; B → `BLOCKED`, owner bilgisi görünür; library değişmez; B pass `COMPLETE`, ledger `COVERED`; A release; A ve B retry `COMPLETE`; lock kalmaz; registry 2 concept; final ikisi `PASS` | PASS (11/11) |
| M | Stale lock | Eski lock → `BLOCKED`; lock bilgisi (owner, created, operation); otomatik silme yok → `WAITING_USER`; seçim 1 → `KEPT`; seçim 2 → `REMOVED`; retry `COMPLETE`; final `PASS` | PASS (7/7) |
| N | Cross-project reuse | Aynı CH iki project'te; tek registry satırı; theory tek dosyada; 2 appearance; project başına 1 Experience Note; SD map'te iki project satırı; final ikisi `PASS`; iki identity chain | PASS (8/8) |

**A–N: 96/96 PASS.**

## 4. Lock Tests

| Kontrol | Sonuç |
|---|---|
| `06` §22.1 kuralları parse: `EXCLUSIVE_CREATE`, `BLOCKED`, `USER_DECISION`, `WARNING`; lock path; `LOCK.md` alanları (5) | PASS (3/3) |
| İlk acquire; ikinci acquire `BLOCKED` ve mevcut lock overwrite edilmez | PASS (2/2) |
| Owner olmayan release reddedilir | PASS |
| Release hatası → `WARNING`; owner release | PASS (2/2) |
| Release başarısız, data write başarılı → persistence `COMPLETE`; final L-21 WARNING → `PASS_WITH_WARNINGS` (DONE mümkün) | PASS (2/2) |
| Senaryo L ve M (§3) | PASS (18/18) |

Lock acquire `os.mkdir` ile yapılır (exclusive directory creation). Dizin varsa `FileExistsError` → `BLOCKED`.

## 5. Final Integrity Tests

Golden project her test için geri yüklenir. Tek bir bozulma yapılır. CHECK 1 sonucu kontrol edilir.

| Kontrol | Beklenen | Sonuç |
|---|---|---|
| Golden base | Bulgu yok | PASS |
| L-03 debt origin event yok | FAIL | PASS |
| L-04 sahte `RESOLVED` debt | FAIL | PASS |
| L-05 pass scope unit ledger'da yok | FAIL | PASS |
| L-06 event pass scope dışında | FAIL | PASS |
| L-07 `COMPLETE` pass + `PARTIAL` unit | FAIL | PASS |
| L-08 persistence `BLOCKED` | WARNING | PASS |
| L-09 `Map Sync: COMPLETE`, node yok | FAIL | PASS |
| L-10 persistence `COMPLETE`, note yok | FAIL | PASS |
| L-11 graph `home_ref` bilinmiyor | FAIL | PASS |
| L-12 pointer bilinmeyen personal CH | FAIL | PASS |
| L-12 library erişilemiyor | WARNING | PASS |
| L-13 map satırı olmayan note | FAIL | PASS |
| L-14 DR note'u geri göstermiyor (DSA event, `DSA_DR`) | FAIL | PASS |
| L-15 iki active pass aynı unit | FAIL | PASS |
| L-16 `ABANDONED` pass ledger'ı kapatmış | FAIL | PASS |
| L-17 config `project_id` değişti | FAIL | PASS |
| L-17 project rename (`project_name`) | Bulgu yok | PASS |
| L-18 stale view | WARNING | PASS |
| L-19 stale index | WARNING | PASS |
| L-20 etkisiz repair (rebuild başarı der, yazmaz) | CHECK 2 L-01 WARNING; `PASS` verilmez | PASS |
| L-23 note event bilinmiyor | FAIL | PASS |
| Identity chain kırık (Experience Note silindi) | İlk kırık halka `EXPERIENCE NOTE`; final `FAIL` | PASS (2/2) |
| DSA event + `DSA_DR`; note → DR; final `PASS` | - | PASS (3/3) |
| Vocabulary: DERIVED set (4), required AUTHORITATIVE (9), result vocabulary (3), 23 L check, rebuild hedefleri yalnız DERIVED, authoritative rebuild reddedilir | - | PASS (6/6) |
| Runtime'da `NOT IMPLEMENTED YET` yok; SKILL `integrity` route eder | - | PASS (2/2) |

**Ek: 45/45 PASS. Integration toplam: 141/141 PASS.**

Static suite (`tests/static/`):

| Kontrol | Sonuç |
|---|---|
| Section reference'lar çözülür (`0N §x`, `references/...md §x`, `ula/...md §x`, aynı dosya `§x`) | PASS |
| `references/`, `templates/`, `ula/` path'leri var | PASS |
| Router 13 adım, hepsi IMPLEMENTED, adım 13 → `07` §L; manual-only; argument hint ve argüman tablosu (`map`, `concept`, `library`, `experiences`, `debt`, `integrity`); SKILL.md ≤ 220 satır; final flow satırı; `01` DONE tanımı | PASS (8/8) |
| `NOT IMPLEMENTED YET` yok; davranış metninde stale phase numarası yok; `07` status §L | PASS (3/3) |
| Absolute path, user name, scratchpad, Incubator, project Jira key yok; project state yok; yalnız `.md`; Graphify ve HTML gerekmez; `personal_library_path` hard-code yok | PASS (6/6) |
| UTF-8, BOM yok; emoji yok; operational dosyalar Türkçe; `01` ve `07` cümle ≤ 30 kelime; ULA canonical copy İngilizce kaldı | PASS (6/6) |

**Static: 26/26 PASS.**

## 6. Mutation Tests

Her mutation geçici skill kopyasında yapılır. Bütün suite'ler kopyaya karşı çalışır. Beklenen suite en az bir FAIL vermelidir. Orijinal runtime dosyaları değişmez.

| ID | Mutation | Sonuç |
|---|---|---|
| P4-M1 | `03` §13.1 `MUST_UNDERSTAND / GAP → ULA_CANDIDATE` satırı silindi | CAUGHT: phase4 24/30, integration 27/44 |
| P5-M1 | Review gate kaldırıldı | CAUGHT: phase5 61/66, integration 132/135 |
| P5-M2 | Açık ULA event unit'i bloklamıyor | CAUGHT: phase5 69/73, integration 135/140 |
| P5-M3 | Builder frozen architecture olmadan | CAUGHT: phase5 67/70 |
| P6-M1 | `07` M-04 silindi | CAUGHT: phase6 77/83 |
| P6-M2 | `07` M-08 silindi | CAUGHT: phase6 80/83 |
| P6-M3 | `05` §7.1 UNION → APPEND | CAUGHT: phase6 6/28 |
| P7-M1 | `06` §7 `NAME` satırı silindi | CAUGHT: phase7 132/147, integration 134/140 |
| P7-M2 | `06` §20 guard + `07` P-12 silindi | CAUGHT: phase7 159/163 |
| P7-M3 | `06` §22 `SEQUENTIAL`, rollback yok | CAUGHT: phase7 154/163 |
| P8-M1 | `07` L-04 silindi | CAUGHT: integration 138/140 |
| P8-M2 | `06` §22.1 `on_existing: OVERWRITE` | CAUGHT: integration 116/123 |
| P8-M3 | `06` §22.1 `stale_lock: AUTO_REMOVE` | CAUGHT: integration 136/140 |
| P8-M4 | `07` L-08 WARNING → FAIL (coverage independence) | CAUGHT: integration 137/140 |
| P8-M5 | `07` §L.1 `COVERAGE_LEDGER` → DERIVED | CAUGHT: integration 138/140 |
| P8-M6 | Config template'e absolute library path | CAUGHT: static 24/26 |
| P8-M7 | `07` §L.6 yeniden numaralandı (SKILL pointer stale) | CAUGHT: static 25/26 |
| P8-M8 | `07` L-20 silindi (repair CHECK 2 olmadan kabul) | CAUGHT: integration 139/141 |

**18/18 CAUGHT.** Phase 4 M3 (roundtrip fixture'a duplicate event) dosya mutation'ı değildir. Phase 4 suite'inde `--mutate dup-event` seçeneği olarak kalır.

Crash içeren mutation sayıları senaryo bazındadır. `safe_run.py` çöken senaryoyu tek FAIL sayar. Bu yüzden toplam sayı mutation'a göre değişir.

## 7. Results

| Grup | Sonuç |
|---|---|
| Phase 3–7 regression | 390/390 PASS |
| Phase 8 integration (E2E + lock + final integrity) | 141/141 PASS |
| Static audit | 26/26 PASS |
| **Toplam** | **557/557 PASS** |
| Mutation | 18/18 CAUGHT |

İlk E2E çalıştırmalarındaki hatalar ve kök nedenleri:

| Hata | Kök neden | Düzeltme |
|---|---|---|
| B: CHECK 1 L-18 WARNING | `06` §21 view regeneration ister; `06` §22 write sırası `HORIZONTAL_MAP`'i saymıyordu; model view üretmiyordu | `06` §22 INDEX adımı `HORIZONTAL_MAP`'i kapsar. Driver view'ı yeniden üretir. |
| J: P-24 beklendi, gelmedi | P-24 modeli yalnız dolu index'i karşılaştırır; boş index'i L-19 yakalar | Beklenti düzeltildi. Cross-layer değer budur. |
| D: L-08 WARNING | Senaryo persistence çağırmadı (spec: pipeline tamamlanır) | Senaryo persistence içerir; final `PASS`. |
| Integration crash `KeyError: 'Event ID'` | Routing render template kolonunu event dict'te aradı | Driver düzeltildi. |
| Mutation runner: `ModuleNotFoundError` | `safe_run.py` altında script dizini sys.path'te değildi | `safe_run.py` hedef dizini ekler. |
| P8-M2 crash `last_lock` | Lock hiç bloklanmayınca attribute yoktu | `Project.__init__` attribute'u başlatır. |
| Static: 8 false positive | ULA dosyası referansları prefix olarak tanınmıyordu; regex backtracking; `✓` emoji sayıldı | Checker ULA dosyalarını çözer; regex düzeltildi; emoji aralığı pictographic. |
