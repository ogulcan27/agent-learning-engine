# 07 — Integrity Checks

**Status:** §C Coverage Integrity IMPLEMENTED (Phase 3). Diğer bölümler NOT IMPLEMENTED YET.

## Purpose

Project learning state tutarlılığını kontrol eder.

## Must Not

- Öğretim içeriğinin learning quality audit'ini yapmaz. Bu iş `ula/LEARNING_AUDITOR.md` rolüne aittir.
- Ledger'daki hatayı sessizce düzeltmez. Raporlar.

---

## C. Coverage Integrity

Ne zaman çalışır:

- Startup'ta, discovery'den önce.
- Her ledger commit'inden sonra.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| C-01 | Duplicate `work_unit_id` | FAIL | Dur. Kullanıcıya göster. |
| C-02 | Unknown `status` | FAIL | Dur. |
| C-03 | Unknown `source_type` | FAIL | Dur. |
| C-04 | Duplicate `seq` aynı `source_type` içinde | FAIL | Dur. |
| C-05 | `COVERED` / `PARTIAL` / `NOT_LEARNING_RELEVANT` ve `learning_pass_id` boş | FAIL | Dur. |
| C-06 | `learning_pass_id: EXTERNAL` | WARNING | Bilgi ver. Devam et. |
| C-07 | `PARTIAL` ve `open_items` boş | WARNING | Bilgi ver. Devam et. |
| C-08 | State sayıları ledger ile uyuşmuyor | WARNING | State'i ledger'dan yeniden üret. `status: REBUILT`. |
| C-09 | Queue §A ile ledger'ın `DEFERRED ∪ PARTIAL` kümesi farklı (fazla veya eksik birim) | WARNING | Queue §A'yı ledger'dan yeniden üret. |
| C-10 | Geçersiz status transition istendi | FAIL | Yazma yapma. Dur. |
| C-11 | Hesaplanan OPEN COVERAGE, ledger'daki bir `DEFERRED` / `UNCOVERED` / `PARTIAL` birimi içermiyor | FAIL | Gap hesaplaması hatalı. Dur. |
| C-12 | `source_ref` artık çözülemiyor (ör. rebase sonrası commit yok) | WARNING | Kullanıcıya sor. Otomatik eşleştirme yapma. |

FAIL olduğunda hiçbir ledger commit'i yapılmaz.

---

## L. Learning State Integrity (pointer, passes, maps)

NOT IMPLEMENTED YET.

## Authoritative Source

- Phase 1 audit: Bölüm 15.1, 17 (M-16), 18.
- `references/02_COVERAGE_PROTOCOL.md` §1, §9, §10.
- Content audit: `ula/LEARNING_AUDITOR.md`.
