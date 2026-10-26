# PHASE 4 — Human Synchronization Tests

**Tarih:** 2026-10-27
**Yöntem:** Deterministic synthetic simulation.
**Neden:** Gerçek project state oluşturulmaz. Development repository bir target project değildir.

## Test düzeneği

- Reference model: `03_HUMAN_SYNC_PROTOCOL.md` kurallarının küçük bir Python modeli.
- Model şu değerleri doğrudan skill dosyalarından parse eder:
  - evidence status (§7.1), category (§10.1), System Design sinyalleri (§10.1), priority (§11), knowledge gap (§12), disposition (§13), disposition rule table (§13.1), filter listesi (§8.2), debt priority ve debt status (§14.1),
  - event alan etiketleri: `templates/LEARNING_PASS_TEMPLATE.md`,
  - debt kolonları: `templates/LEARNING_QUEUE_TEMPLATE.md` §B.
- Event'ler ve debt kayıtları Markdown olarak yazılır ve tekrar okunur (roundtrip).
- Judgment girdileri fixture'dan gelir: değişiklik türü, filter cevapları, System Design / MUST / gap sinyalleri, kullanıcı bilgisi. Model bu girdilere protocol kurallarını uygular.
- Script'ler session scratchpad içindedir. Repository'ye eklenmedi. Runtime dosyası değildir.

## Senaryolar ve sonuçlar

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | Scope: rename, format, import fix | Event = 0; öneri `NOT_LEARNING_RELEVANT` | PASS (2/2) |
| B | Long request API'yi bloklar → background queue | `SYSTEM_DESIGN`, `MUST_UNDERSTAND`, gap → `ULA_CANDIDATE`; integrity temiz | PASS (4/4) |
| B+ | Aynı event, önceki learning artifact var | `KNOWN` → `EXPERIENCE_ONLY` | PASS |
| B+ | Aynı event, kullanıcı bilgisi için evidence yok | `UNKNOWN` → `UNRESOLVED` (tahmin yok) | PASS |
| C | Yalnız Top-K gerekli → heap | `DSA` + reusable signal | PASS (2/2) |
| C+ | Computational need yok | DSA değil | PASS |
| D | 10 routine değişiklik + 1 yüksek değerli | 1 event; 10 suppressed | PASS (2/2) |
| E | `USEFUL_TO_KNOW` + `GAP` kavram | `KNOWLEDGE_DEBT`; §B `OPEN`, `LATER`; event ref; `UNASSIGNED`; integrity temiz | PASS (5/5) |
| E+ | Kullanıcı `MUST_UNDERSTAND` event'i erteler | Debt priority `NOW` | PASS |
| F | 4 work unit (2'si aynı karar, 2'si routine) | 1 Human Sync; 1 event, 2 unit'e bağlı; unit bazında öneri (2 `PARTIAL`, 2 `NOT_LEARNING_RELEVANT`); integrity temiz | PASS (5/5) |
| G | Leakage iddiası, evidence net değil | `UNRESOLVED`; unit açık kalır | PASS (2/2) |
| G+ | `VERIFIED` ref olmadan | E-11 FAIL | PASS |
| G+ | Evidence okunamadı, event yok | `NOT_LEARNING_RELEVANT` önerilmez | PASS |
| H | LE-01 `EXPERIENCE_ONLY`, LE-02 `ULA_CANDIDATE` | `open_items` = yalnız LE-02; ref'ler çözülür; bilinmeyen ID → E-10 FAIL | PASS (5/5) |
| I | Duplicate `event_id` | E-01 FAIL | PASS |
| J | Debt var, originating event yok | E-07 FAIL | PASS |

H notu: Gerçek Completion Commit çalışmaz. Test yalnız Coverage Outcome Proposal'ı doğrular.

## Ek tutarlılık testleri

| Test | Beklenen | Sonuç |
|---|---|---|
| Disposition set | 5 canonical değer | PASS |
| Priority set | 3 değer | PASS |
| Evidence status set | 4 değer | PASS |
| Category set | 9 değer | PASS |
| Rule table çıktıları | Hepsi bilinen disposition | PASS |
| `IMPLEMENTATION_DETAIL` + `ULA_CANDIDATE` | E-09 FAIL | PASS |
| ULA listesinde bilinmeyen ID | E-06 FAIL | PASS |
| Duplicate `debt_id` | E-08 FAIL | PASS |
| `KNOWLEDGE_DEBT` event, §B kaydı yok | E-13 FAIL | PASS |
| Unknown category | E-03 FAIL | PASS |
| Event scope dışı unit'e bağlı | E-02 FAIL | PASS |

**Toplam: 46/46 PASS.**

## Mutation check

Testler ilk çalıştırmada geçti. Düzeneğin hata yakaladığı geçici kopyalar üzerinde doğrulandı. Orijinal runtime dosyaları değişmedi.

| Mutation | Nerede | Sonuç |
|---|---|---|
| M1: `ULA_CANDIDATE` disposition satırı silindi | Geçici `03` kopyası | 41/46. E-05 FAIL, vocabulary ve rule table testleri FAIL. |
| M2: `originating_event_id` kolonu bozuldu | Geçici queue template kopyası | 44/46. E-07 ve E-13 FAIL. |
| M3: Render edilen pass'a duplicate event eklendi | Roundtrip fixture | 41/46. E-01 FAIL. |

Not (M2): İlk çalıştırmada test script'i `KeyError` ile durdu. Hata yakalandı ama rapor edilmedi. Script `.get` kullanacak şekilde düzeltildi. Sonra FAIL düzgün raporlandı.

## Regression

Phase 3 coverage testleri tekrar çalıştı: 24/24 PASS. `02_COVERAGE_PROTOCOL.md` değişmedi.

## Kapsam dışı

- Gerçek project evidence okuma (target project gerektirir).
- Human Sync metin kalitesi. Bu bir judgment çıktısıdır. Deterministic test ile ölçülmez.
- Priority ve gap sinyallerinin doğru tanınması. Testte fixture girdisidir.
- ULA routing, Completion Commit, Persistence (Phase 5+).
