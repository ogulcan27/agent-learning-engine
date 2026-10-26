# PHASE 3 — Learning Coverage Engine Report

**Tarih:** 2026-10-27
**Constraint:** Phase 1 ve Phase 2 kararları (FROZEN). Hiçbiri değiştirilmedi.

# 1. Status

```text
PHASE 3 STATUS: PASS
PHASE 4 STATUS: READY
```

# 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `references/02_COVERAGE_PROTOCOL.md` | Skeleton → IMPLEMENTED |
| `references/01_OPERATIONAL_CORE.md` | Startup → Scope Resolution sınırı, stop rules, write rules |
| `references/07_INTEGRITY_CHECKS.md` | §C Coverage Integrity (C-01…C-12). §L NOT IMPLEMENTED YET. |
| `templates/LEARNING_CONFIG_TEMPLATE.md` | Gerçek template |
| `templates/COVERAGE_LEDGER_TEMPLATE.md` | Gerçek template |
| `templates/LEARNING_STATE_TEMPLATE.md` | Gerçek template |
| `templates/LEARNING_QUEUE_TEMPLATE.md` | §A gerçek; §B RESERVED |
| `SKILL.md` | Router durum sütunu, skeleton guard sınırı, load map, initialization, forbidden signals |
| `docs/audit/PHASE_3_COVERAGE_TESTS.md` | Yeni — test spesifikasyonu ve sonuçlar |
| `docs/audit/PHASE_3_COVERAGE_ENGINE_REPORT.md` | Yeni — bu rapor |

`SKILL.md` boyutu 6.6 KB'den 7.9 KB'ye çıktı. Protocol metni kopyalanmadı.

# 3. Coverage Model

- Coverage work-unit based ve set-based'dir.
- Tek canonical kayıt: ledger içindeki **Work Units** tablosu.
- Open / Skipped / Closed listeleri dosyada saklanmaz. Her çağrıda hesaplanır. Böylece duplicate truth oluşmaz.
- Satır silinmez. Yalnız status değişir.

```text
OPEN COVERAGE  = UNCOVERED ∪ PARTIAL ∪ DEFERRED
DEFAULT HIDDEN = COVERED ∪ SKIPPED_BY_USER ∪ NOT_LEARNING_RELEVANT
```

`last_covered_boundary` yalnız state içinde bilgi amaçlıdır. Gap kaynağı değildir.

Ledger üç commit noktasında yazılır:

| Commit | Yazılan |
|---|---|
| Discovery Commit | Yeni `UNCOVERED` satırlar, baseline |
| Scope Commit | `DEFERRED`, `SKIPPED_BY_USER`, reopen |
| Completion Commit | `COVERED`, `PARTIAL`, `NOT_LEARNING_RELEVANT` — yalnız pipeline başarılı + integrity PASS |

# 4. Work Unit Model

İstenen 9 alan + 2 ek alan:

| Alan | Not |
|---|---|
| `work_unit_id` | `<source_type>:<native-id>` |
| `seq` | **Ek.** `latest` ve aralık seçimi bir sıra ister. Sıra source'un doğal sırasından gelir. Filename sort yasak olduğu için açık alan gerekir. |
| `label`, `source_type`, `source_ref`, `status` | — |
| `discovered_at`, `last_evaluated_at` | `YYYY-MM-DD` |
| `learning_pass_id` | `LP-YYYYMMDD-NN` · `EXTERNAL` · `-` |
| `open_items` | **Ek.** `PARTIAL` biriminde "yalnız açık learning items görünür" kuralı için gerekir. |
| `notes` | `DEFERRED` reason, skip gerekçesi |

Normalization örnekleri: `jira:INC-44`, `git:3f2a9c1d0b7e`, `phase-doc:PLAN.md#step-10`, `user:cache-redesign`, `other:PR-118`.

# 5. Source Resolution

- **Discovery ≠ authority.** Explicit user scope her zaman en yüksek authority'dir.
- Universal priority (Phase 1 Q5) protokole yazıldı.
- `work_unit_source`: `auto` · `jira` · `git` · `phase-doc`. Bilinmeyen değer → CONFIG ERROR, fallback yok. Configured source evidence vermezse → CONFIG ERROR.
- Auto mode: Teknik olarak mevcut olmak yeterli değildir. Proje işinin o birimlerle ilerlediğine dair evidence gerekir. Birden fazla güçlü aday → kullanıcıya sor. İlk sonuç veya değişen sonuç → kullanıcı onayı. Kullanıcı isterse config'e sabitlenir.
- Issue key'ler commit / branch / doküman içinde tutarlıysa tracker API erişimi olmadan da work unit ID olabilir.
- Forbidden authority signals: file modification time, chat memory alone, directory listing order, arbitrary filename sort, Claude inference without persistent evidence.

# 6. Status Vocabulary

| Status | Default gap | Kim yazar |
|---|---|---|
| `UNCOVERED` | Görünür | Discovery |
| `COVERED` | Görünmez | Completion Commit |
| `PARTIAL` | Görünür (`open_items`) | Completion Commit |
| `DEFERRED` | Görünür | Scope Commit |
| `SKIPPED_BY_USER` | Görünmez (`show skipped`) | Explicit user decision |
| `NOT_LEARNING_RELEVANT` | Görünmez | Completion Commit (Phase 4 Knowledge Priority) |

Doğrulama: Skill dosyalarında bu altı terim dışında coverage status kelimesi yoktur. "PARTIAL" kelimesi daha önce implementation durumu için de kullanılıyordu. Bu kullanım kaldırıldı. Terim artık tek anlam taşır.

# 7. Scope Resolution

| Argüman | Scope | Soru |
|---|---|---|
| `latest` | En yüksek `seq` | Yok |
| `catch-up` | `UNCOVERED ∪ PARTIAL ∪ DEFERRED` | Yok |
| `pending` | `DEFERRED ∪ PARTIAL` | Yok |
| `<id>` / aralık | Eşleşen birimler | Ambiguity varsa |
| (boş) | Summary + 5 seçenekli menü | Evet |

Seçilmeyen `UNCOVERED` → `DEFERRED`. Seçilmeyen `PARTIAL` ve `DEFERRED` değişmez.

Ek: Ledger boşsa ve çok sayıda geçmiş birim bulunursa first-run baseline seçeneği sunulur. Seçenekler: hepsi UNCOVERED, `<ID>` öncesi SKIPPED_BY_USER (`note: baseline`), veya kullanıcı beyanı ile COVERED (`EXTERNAL`).

# 8. State Authority Model

```text
LEARNING_CONFIG   → project preferences
COVERAGE_LEDGER   → authoritative coverage truth
LEARNING_STATE    → derived runtime summary (rebuildable)
LEARNING_QUEUE §A → open-item convenience view (rebuildable, GENERATED VIEW)
LEARNING_QUEUE §B → Knowledge Debt — RESERVED
```

Çelişkide ledger kazanır. State ve queue §A her commit sonrası ledger'dan yeniden üretilir.

# 9. Transition Rules

Matrix: `02_COVERAGE_PROTOCOL.md` §9. Toplam 19 geçerli transition. Her transition bir tetikleyici koduna bağlıdır: D (discovery), B (baseline), S (scope), U (explicit user), C (completion).

İstenen 11 transition'ın hepsi var. Ek transition'lar:

| Transition | Gerekçe |
|---|---|
| `DEFERRED → DEFERRED` | Yeniden erteleme; `notes` güncellenir |
| `DEFERRED → NOT_LEARNING_RELEVANT` | Ertelenen birim sonra değerlendirilir ve yalnız implementation detail çıkabilir |
| `PARTIAL → PARTIAL` | `open_items` güncellenir |
| `PARTIAL → SKIPPED_BY_USER` | Kullanıcı kalan item'ları açıkça bırakabilir |
| `NOT_LEARNING_RELEVANT → UNCOVERED` | `SKIPPED_BY_USER` reopen ile simetrik; yalnız explicit user |
| (yeni satır) → `UNCOVERED` / `SKIPPED_BY_USER` / `COVERED` | Discovery ve baseline |

`COVERED` terminal durumdur. Geçersiz transition → C-10 FAIL. Ledger'a yazılmaz.

# 10. Test Results

Ayrıntı: `docs/audit/PHASE_3_COVERAGE_TESTS.md`.

- Test A–I: 17/17 kontrol PASS.
- Ek tutarlılık testleri: 7/7 PASS.
- **Toplam: 24/24 PASS.**
- Mutation check: Protokolden bir transition silinince test FAIL verdi. Test düzeneği hatayı yakalıyor.
- Transition matrix ve ledger kolonları test sırasında skill dosyalarından parse edildi. Testler yazılı protokolü doğrular, ayrı bir kopyayı değil.

Validation:

```text
[x] 02_COVERAGE_PROTOCOL artık NOT IMPLEMENTED YET değil
[x] LEARNING_CONFIG_TEMPLATE tamam
[x] LEARNING_STATE_TEMPLATE tamam
[x] COVERAGE_LEDGER_TEMPLATE tamam
[x] LEARNING_QUEUE_TEMPLATE work-unit kısmı tamam
[x] status vocabulary tek
[x] DEFERRED ≠ SKIPPED_BY_USER
[x] coverage truth ledger'da
[x] State derived summary
[x] Queue convenience view
[x] work unit source priority tanımlı
[x] auto mode tanımlı
[x] invalid authority sources yasak
[x] scope menu tanımlı
[x] latest behavior tanımlı
[x] catch-up behavior tanımlı
[x] pending behavior tanımlı
[x] transition matrix tanımlı
[x] synthetic tests geçiyor (24/24)
[x] Human Sync implement edilmedi
[x] ULA implement edilmedi
[x] MindMap implement edilmedi
[x] original sources değişmedi (sha256 eşit)
[x] Graphify kullanılmadı
```

Ek kontroller: 35 `.md` dosyası geçerli UTF-8 ve BOM yok. Skill içinde absolute / kişisel path yok. Development repo içinde `docs/learning/` oluşturulmadı.

# 11. Deviations

| ID | Sapma | Gerekçe |
|---|---|---|
| D-01 | `seq` ve `open_items` alanları eklendi | Bölüm 4 |
| D-02 | 6 ek transition | Bölüm 9 |
| D-03 | Üç commit noktası modeli (Discovery / Scope / Completion) | `COVERED` yalnız başarılı pipeline sonrası yazılır. `DEFERRED` ise kullanıcının scope kararıdır ve pipeline sonucuna bağlı değildir. Pipeline yarıda kalsa da 4–9 kaybolmaz. |
| D-04 | First-run baseline seçeneği | Mevcut bir projede ilk çağrı yüzlerce geçmiş commit'i `UNCOVERED` yapabilir. Seçenek yalnız mevcut status vocabulary'yi kullanır. |
| D-05 | `learning_pass_id: EXTERNAL` | Skill öncesi öğrenilmiş işi kullanıcı beyanı ile kaydetmek için. C-06 WARNING üretir. |
| D-06 | `resolved_work_unit_source` state alanı | Auto mode sonucu değiştiğinde kullanıcıya sormak için önceki sonucun bilinmesi gerekir. Bilgi amaçlıdır. |
| D-07 | Test I değeri 4 ≠ 2 (örnekte 3 ≠ 2) | Senaryo zinciri F ve G sonrası gerçek deferred sayısı 4'tür. Aynı mantık test edildi. |

Phase 1 veya Phase 2 kararı ile çelişen sapma yoktur.

# 12. Open Issues

| ID | Konu | Etki |
|---|---|---|
| OI-01 | Gerçek git / Jira / phase-doc discovery bir target project üzerinde test edilmedi | Phase 4 öncesi veya sırasında bir test projesi gerekir |
| OI-02 | Auto mode seçimi Claude yargısına dayanır. Kurallar ve kullanıcı onayı ile sınırlandırıldı, ancak deterministic değildir | Kabul edilen risk; ilk sonuç her zaman onaylatılır |
| OI-03 | Git rebase sonrası hash eşleştirme (C-12) yalnız WARNING + kullanıcıya sor | Otomatik eşleştirme yok; bilinçli tercih |
| OI-04 | Test scriptleri session scratchpad içindedir ve oturum sonunda kaybolur | Senaryolar `PHASE_3_COVERAGE_TESTS.md` içinde kayıtlıdır; gerekirse yeniden yazılabilir |
| OI-05 | Completion Commit kuralı yazıldı ancak tetikleyecek pipeline yok | Phase 4+ ile çözülür |

# 13. Phase 4 Readiness

**READY.**

Phase 4 için hazır olanlar:

- Selected scope, `03_HUMAN_SYNC_PROTOCOL.md` için input olarak tanımlı.
- `NOT_LEARNING_RELEVANT` status'u ve Completion Commit kuralı tanımlı. Knowledge Priority bu status'u üretecek.
- `PARTIAL.open_items` alanı learning event çıktısını bekliyor.
- Queue §B (Knowledge Debt) RESERVED olarak hazır.

Bugünkü `/learning` akışı:

```text
Coverage (Startup → Scope Resolution) → PASS
Human Synchronization → NOT IMPLEMENTED YET → STOP (Completion Commit yok)
```
