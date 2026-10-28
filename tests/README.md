# Learning Skill — Permanent Regression Suite

Development repository test altyapısıdır. Runtime skill paketinin parçası değildir. Target project'e kopyalanmaz.

## Çalıştırma

```text
uv run --no-project python tests/run_all.py                    # bütün suite'ler + mutation check
uv run --no-project python tests/run_all.py --no-mutations     # yalnız suite'ler
uv run --no-project python tests/run_all.py <skill_dir>        # başka bir skill kopyası
uv run --no-project python tests/integration/run_tests.py      # tek suite
```

Yalnız Python standard library kullanılır.

## Yapı

| Dizin | İçerik | Kural kaynağı |
|---|---|---|
| `common/` | `harness.py` (skill path, rapor), `safe_run.py` (senaryo başına crash izolasyonu) | - |
| `phase3/` | Coverage model + testler | `02`, ledger template |
| `phase4/` | Human Sync model + testler | `03`, pass / queue template |
| `phase5/` | ULA routing / completion model + testler | `04`, `02` §9 |
| `phase6/` | Semantic Graph model + testler (hierarchy amendment dahil) | `05`, `07` §M, graph template |
| `phase7/` | Knowledge Persistence model + testler | `06`, `07` §P, persistence template'leri |
| `integration/` | E2E driver, `07` §L final integrity modeli, `06` §22.1 lock modeli | `06`, `07` §L |
| `static/` | Router, cross reference, portability, encoding, dil kontrolü, development-project contamination | bütün skill dosyaları |
| `sync/` | Standalone incremental Human Sync: routing, first catch-up, incremental run, stale / scoped invalidation, dependency freshness (direct, transitive, non-material, unrelated), dependency retrieval, full mode reuse, coverage / debt / graph / library independence, corruption, token audit | `08`, `07` §S, `03` §6 |
| `view/` | Unified Knowledge View: creation rule, incremental HS sections (1–3 then 4–5), stale presentation, Light / Full ULA in one concept section, full-mode reuse, sync-only scope, section-level retrieval and write stability on a large view, Mermaid map derivation, recursive zoom, breadcrumbs, §V integrity, write failure, migration, README diagrams | `09`, `07` §V, view template |
| `isolation/` | Cross-project isolation: fresh Project B hiçbir zaman Project A state'ini seçmez (sentinel `V8_Clean_Validation` yalnız test data) | `01` §0, `02` §3.4 / §11, `06` §2.3, SKILL.md §9 |
| `mutation.py` | Geçici skill kopyasında bir kuralı bozar; suite yakalamalıdır | - |

## Kurallar

- Test kuralı runtime protocol ve template dosyalarından parse eder. Kural test içinde ikinci kez yazılmaz.
- Her senaryo yeni geçici dizin kullanır. Development repository içinde `docs/learning/` oluşturulmaz.
- Judgment girdileri (meaning eşdeğerliği, section conflict, project experience) fixture olarak verilir.
- Bir test FAIL ise önce kök nedeni bul: protocol hatası mı, model hatası mı, beklenti hatası mı.
