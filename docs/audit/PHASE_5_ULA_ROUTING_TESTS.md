# PHASE 5 — ULA Routing Tests

**Tarih:** 2026-10-27
**Yöntem:** Deterministic synthetic simulation.
**Neden:** Gerçek project state oluşturulmaz. ULA içerik kalitesi bu testlerin konusu değildir.

## Test düzeneği

- Reference model: `04_ULA_PROTOCOL.md` kurallarının küçük bir Python modeli.
- Model şu değerleri doğrudan skill dosyalarından parse eder:
  - `04` §2.1–§2.4 vocabulary (mode, ULA status, pass status, current stage),
  - §4.1 Full trigger set,
  - §5 stage transition tablosu (from, trigger, to, requires, ula_status),
  - §11.2 unit blocking tablosu,
  - §12 token load tablosu,
  - `templates/LIGHT_ULA_TEMPLATE.md` L0/L1/L2 başlıkları,
  - `templates/LEARNING_PASS_TEMPLATE.md` ULA Routing başlığı.
- Stage geçişleri yalnız §5 tablosundaki satırla yapılır. Satır yoksa veya `requires` sağlanmıyorsa geçiş reddedilir.
- Completion Commit, Phase 3 transition matrix'i (`02` §9) ile doğrulanır. Geçersiz transition C-10 verir.
- Judgment girdileri fixture'dan gelir: disposition, trigger listesi, self-check sonucu, audit Freeze Recommendation, kullanıcı kararı.
- Script'ler session scratchpad içindedir. Repository'ye eklenmedi.
- `run_safe.py` her senaryoyu ayrı çalıştırır. Çöken senaryo FAIL olarak raporlanır.

## Senaryolar ve sonuçlar

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | EXPERIENCE_ONLY + KNOWLEDGE_DEBT | Early completion; ULA dosyası yüklenmez; unit `COVERED`; pass `COMPLETE` | PASS (3/3) |
| B | Bütün unit'ler routine | ULA'ya girilmez; hepsi `NOT_LEARNING_RELEVANT`; pass `COMPLETE` | PASS (3/3) |
| C | Cache invalidation basic mechanism, trigger yok | `LIGHT`; Light `COMPLETE`; rol dosyası yüklenmez; integrity temiz; bilinmeyen trigger sayılmaz | PASS (5/5) |
| D | Kritik, recursive, architecture-level | `FULL`; yetersiz bilgi → `ROUTING UNCERTAIN` | PASS (2/2) |
| E | Override | Auto LIGHT + user FULL → FULL; auto FULL + user LIGHT → LIGHT + U-17 WARNING | PASS (3/3) |
| F | Architect bitti, user approval yok | `FULL_ULA_REVIEW`; `WAITING_USER`; Builder reddedilir; approval olmadan approve reddedilir; CONTENT yok | PASS (5/5) |
| G | Architect → approve → Builder → Auditor READY TO FREEZE | Architecture `FROZEN` (user); `COMPLETE`; integrity temiz; rol yükleme sırası Architect → Builder → Auditor; minor fixes → `COMPLETE`, yeniden audit yok | PASS (5/5) |
| H | Audit: REVISION REQUIRED | `FULL_ULA_BUILD`; architecture açılmaz; aynı route ikinci kez → `BLOCKED` | PASS (3/3) |
| I | Audit: ARCHITECTURE REVISIT REQUIRED | Architect reopen → `FULL_ULA_REVIEW` + `WAITING_USER`; architecture `PROPOSED`; approval'a kadar Builder reddedilir | PASS (3/3) |
| J | Pass `WAITING_USER` @ `FULL_ULA_REVIEW`, yeni `/learning` | resume/new/abandon sorusu; explicit arg → soru yok; aynı pass ID ve stage; architecture yeniden üretilmez; temiz; completed artifact yeniden yazılırsa U-14 FAIL | PASS (6/6) |
| K | Abandon | `ABANDONED`; ledger ve `open_items` değişmez; event'ler kalır; abandon sonrası ledger değişirse U-13 FAIL | PASS (4/4) |
| L | `PARTIAL`, `open_items = LE-02`; LE-02 Light `COMPLETE` | İlk commit `PARTIAL` + LE-02; pass açık; sonra `COVERED`, `open_items` boş; pass `COMPLETE`, temiz | PASS (4/4) |
| M | UNRESOLVED event | ULA'ya girilmez, `WAITING_USER`; `PARTIAL`, `open_items` kalır; pass `COMPLETE` değil | PASS (3/3) |
| N | Knowledge Debt `OPEN` | Unit `COVERED`; debt `OPEN` kalır | PASS |
| O | EXPERIENCE_ONLY | Unit `COVERED` | PASS |
| P | Aynı unit iki active pass'te | U-15 FAIL; yeni pass → `CONFLICT` | PASS (2/2) |

**A–P: 53/53 PASS.**

## Ek testler

| Test | Beklenen | Sonuç |
|---|---|---|
| 5 unit örneği (`04` §11.4) | A `NOT_LEARNING_RELEVANT`, B `COVERED`, C `COVERED`, D `PARTIAL`, E `PARTIAL`; pass `COMPLETE` değil | PASS (2/2) |
| Açık item varken zorla `COMPLETE` | U-11 + U-12 FAIL | PASS |
| Light self-check bir kez FAIL → düzeltme | `COMPLETE` | PASS (2/2) |
| Aynı self-check maddesi iki kez FAIL | `BLOCKED` | PASS |
| Light `COMPLETE` + self-check FAIL | U-09 FAIL | PASS |
| Light L2 boş | U-08 FAIL | PASS |
| Builder stage'inde architecture `FROZEN` değil | Builder reddedilir | PASS |
| CONTENT var, architecture `FROZEN` değil | U-05 FAIL | PASS |
| `FROZEN` ama user approval kaydı yok | U-07 FAIL | PASS |
| Vocabulary: 2 mode, 6 ULA status, 5 pass status, 10 stage, 12 trigger | Doğru | PASS (5/5) |
| Transition tablosu yalnız bilinen stage kullanır | Doğru | PASS |
| Hiçbir stage iki rol dosyası yüklemez | Doğru | PASS |
| Master load tablosunda yok | Doğru | PASS |
| Light template core = L0, L1, L2 | Doğru | PASS |
| Routing tablosu başlığı | 6 kolon | PASS |

**Ek: 21/21 PASS. Toplam: 74/74 PASS.**

## Düzenek hataları (test sırasında bulundu ve düzeltildi)

İlk çalıştırma 69/71 verdi. İki FAIL'in root cause'u protokol değil, test modeliydi:

1. Tablo parser'ı §5'teki ikinci tabloyu (pass status kuralı) transition tablosuna ekliyordu. Parser yalnız ilk tabloyu okuyacak şekilde düzeltildi.
2. Model, Builder gate reddetmeden önce rol dosyasını "yüklenmiş" kaydediyordu. Sıra düzeltildi: önce geçiş kontrolü, sonra yükleme. Bu, protokoldeki "gate geçmeden rol yükleme" kuralı ile uyumludur.

## Mutation check

Geçici kopyalar üzerinde. Orijinal runtime dosyaları değişmedi.

| Mutation | Değişiklik | Sonuç |
|---|---|---|
| M1 | Review gate kaldırıldı: `architecture proposed → FULL_ULA_BUILD` | 61/66. F, G, H, I, J FAIL. |
| M2 | `ULA_CANDIDATE` + not COMPLETE artık bloklamıyor (COMPLETE pass açık item ile) | 69/73. L ve 5-unit testi FAIL. Phase 3 matrix ayrıca `COVERED → COVERED` geçişini C-10 ile reddetti. |
| M3 | Builder frozen architecture olmadan: `user_approval` ve `frozen_architecture` gereksinimleri kaldırıldı | 67/70. F, G ve "Builder without Frozen Architecture" FAIL. |

Not (M3): İlk M3 çalıştırması `frozen_architecture` gereksinimini tek başına test etmiyordu. Yalnız review gate yakalanıyordu. Doğrudan test eklendi. Sonra M3 bu gereksinimi de yakaladı.

## Regression

| Phase | Sonuç |
|---|---|
| Phase 3 coverage | 24/24 PASS |
| Phase 4 human sync | 46/46 PASS |

## Kapsam dışı

- Gerçek ULA içerik üretimi ve içerik kalitesi (Auditor'ın işi).
- Gerçek kullanıcı etkileşimi (review, override): fixture ile simüle edildi.
- Full trigger tanıma: fixture girdisi. Claude judgment'ına dayanır.
- MindMap, Knowledge Persistence (Phase 6+).
