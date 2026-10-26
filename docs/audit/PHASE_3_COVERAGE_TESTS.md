# PHASE 3 — Coverage Tests

**Tarih:** 2026-10-27
**Yöntem:** Deterministic synthetic simulation.
**Neden:** Development repository git değildir. Gerçek project state oluşturulmaz.

## Test düzeneği

- Reference model: `02_COVERAGE_PROTOCOL.md` kurallarının küçük bir Python modeli.
- Model, transition matrix'i doğrudan `references/02_COVERAGE_PROTOCOL.md` §9 tablosundan parse eder.
- Model, ledger kolonlarını doğrudan `templates/COVERAGE_LEDGER_TEMPLATE.md` "Work Units" tablosundan okur.
- Her adımda ledger Markdown tabloya yazılır ve tekrar okunur (roundtrip). Böylece template formatı da test edilir.
- Fixture: `phase-doc` source, `PLAN.md#step-N`, `seq = N`.
- Script ve fixture'lar geçici session scratchpad içindedir. Repository'ye eklenmedi. Runtime dosyası değildir.

Test düzeneği doğrulaması (mutation check): Protokolün geçici bir kopyasında `DEFERRED → COVERED` hücresi silindi. Test "required transitions present" adımında FAIL verdi. Düzenek gerçek hatayı yakalar.

## Senaryolar ve sonuçlar

| Test | Senaryo | Beklenen | Sonuç |
|---|---|---|---|
| A | Boş ledger, current = 1–3 | 1–3 `UNCOVERED` | PASS |
| B | Ledger 1–3 `COVERED` (`EXTERNAL`), current = 1–10 | Open gap = 4–10; integrity FAIL yok | PASS (2/2) |
| C | `/learning latest` | Selected = 10; 4–9 `DEFERRED`; 10 completion öncesi `UNCOVERED` | PASS (3/3) |
| C+ | 10 için simüle Completion Commit | `UNCOVERED → COVERED` (trigger C, `LP-20261027-01`) | Simülasyon (gerçek state yok) |
| D | Sonraki çağrı, current = 1–10 | 4–9 hâlâ open | PASS |
| E | `/learning catch-up` | Selected = 4–9 | PASS |
| F | 5 → `SKIPPED_BY_USER` | Default gap'te yok; `show skipped` içinde var; catch-up almaz | PASS (3/3) |
| G | 6 → `PARTIAL` (simüle completion, `open_items`) | Open coverage içinde; `pending` = 4, 6, 7, 8, 9 | PASS (2/2) |
| H | Duplicate `work_unit_id` | C-01 FAIL | PASS |
| I | Ledger `deferred = 4`, state `deferred_count = 2` | C-08 WARNING; rebuild sonrası temiz | PASS (3/3) |

Not (Test I): Kullanıcı örneğinde ledger deferred = 3 idi. Senaryo zincirinde F ve G sonrası gerçek değer 4'tür. Test aynı uyuşmazlık mantığını 4 ≠ 2 ile doğrular.

## Ek tutarlılık testleri

| Test | Beklenen | Sonuç |
|---|---|---|
| `COVERED → DEFERRED` | C-10 reddedilir | PASS |
| `DEFERRED → COVERED` scope trigger ile | C-10 reddedilir (yalnız Completion Commit) | PASS |
| `SKIPPED_BY_USER → UNCOVERED` explicit reopen | Open coverage'a döner | PASS |
| Queue ile ledger farklı | C-09 WARNING | PASS |
| Queue rebuild | `DEFERRED ∪ PARTIAL` | PASS |
| `COVERED` ve `learning_pass_id` boş | C-05 FAIL | PASS |
| Phase 3 zorunlu transition listesi matrix içinde | Eksik yok | PASS |

**Toplam: 24/24 PASS.**

## Kapsam dışı

- Gerçek git / Jira / phase-doc discovery (target project gerektirir).
- Auto mode source seçimi (project evidence ve kullanıcı onayı gerektirir).
- Completion Commit'in gerçek pipeline ile tetiklenmesi (Phase 4+).
