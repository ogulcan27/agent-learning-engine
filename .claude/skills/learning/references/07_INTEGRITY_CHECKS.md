# 07 — Integrity Checks

**Status:** §C Coverage Integrity IMPLEMENTED (Phase 3). §E Event Integrity IMPLEMENTED (Phase 4). §U ULA / Pass Integrity IMPLEMENTED (Phase 5). §L NOT IMPLEMENTED YET.

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

## E. Learning Event and Knowledge Debt Integrity

Ne zaman çalışır:

- Handoff write'tan önce (`03_HUMAN_SYNC_PROTOCOL.md` §17). Pass ve queue §B taslağı üzerinde.
- Startup'ta, queue §B üzerinde (E-07, E-08, E-12).
- Ledger'da `PARTIAL` satırı varsa, `open_items` üzerinde (E-10).

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| E-01 | Duplicate `event_id` aynı pass içinde | FAIL | Dur. |
| E-02 | Event `work_unit_ids` boş veya selected scope dışında bir ID içeriyor | FAIL | Dur. |
| E-03 | Unknown `category` veya `secondary_tags` değeri | FAIL | Dur. |
| E-04 | Unknown `knowledge_priority` | FAIL | Dur. |
| E-05 | Unknown `disposition` | FAIL | Dur. |
| E-06 | Disposition Summary içinde `ULA_CANDIDATE` girdisi tanımlı bir `event_id` değil | FAIL | Dur. |
| E-07 | Debt `originating_event_id` boş veya tanımlı bir event değil | FAIL | Dur. |
| E-08 | Duplicate `debt_id` | FAIL | Dur. |
| E-09 | `IMPLEMENTATION_DETAIL` priority ile `ULA_CANDIDATE` veya `KNOWLEDGE_DEBT` disposition | FAIL | Dur. |
| E-10 | `PARTIAL.open_items` bilinmeyen bir `event_id` içeriyor | FAIL | Dur. |
| E-11 | `VERIFIED` iddia evidence ref içermiyor | FAIL | Ref ekle veya status'u düzelt. Sonra tekrar kontrol et. |
| E-12 | Unknown `evidence_status`, debt `priority` veya `debt_status` | FAIL | Dur. |
| E-13 | `KNOWLEDGE_DEBT` disposition event için §B kaydı yok | FAIL | Dur. |
| E-14 | `ULA_CANDIDATE` ve `knowledge_gap` `GAP` değil | WARNING | Kullanıcıya göster. Override kaydı yoksa sor. |
| E-15 | Aynı `concept` için birden fazla `OPEN` debt | WARNING | Kullanıcıya göster. Otomatik birleştirme yapma. |

E-10 için çözüm: `event_id` içindeki `<learning-pass-id>` ile `docs/learning/passes/<learning-pass-id>/LEARNING_PASS.md` bulunur. Event o dosyada yoksa FAIL.

FAIL olduğunda pass dosyası ve queue §B yazılmaz. Ledger zaten Phase 4'te yazılmaz.

Bu bölüm ULA content audit yapmaz.

---

## U. ULA and Pass Integrity

Ne zaman çalışır:

- Startup'ta, active pass taramasında (U-15).
- Her stage geçişinden önce (`04_ULA_PROTOCOL.md` §5).
- Completion Commit'ten önce ve pass `COMPLETE` yazılmadan önce.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| U-01 | Unknown `ula_mode` | FAIL | Dur. |
| U-02 | Unknown `ula_status`, `pass_status` veya `current_stage` | FAIL | Dur. |
| U-03 | Aynı event için birden fazla routing satırı veya aktif LIGHT + FULL artifact | FAIL | Dur. |
| U-04 | Routing satırı veya artifact tanımsız event'e ya da `ULA_CANDIDATE` olmayan event'e bağlı | FAIL | Dur. |
| U-05 | FULL `CONTENT.md` var, `ARCHITECTURE.md` `FROZEN` değil | FAIL | Builder çıktısını kullanma. Dur. |
| U-06 | FULL `AUDIT.md` var, `CONTENT.md` yok | FAIL | Dur. |
| U-07 | `architecture_status: FROZEN`, `approved_by: user` veya `approved_at` yok | FAIL | Dur. Kullanıcı review iste. |
| U-08 | LIGHT artifact'te L0, L1 veya L2 bölümü boş | FAIL | Dur. |
| U-09 | LIGHT `COMPLETE` ve self-check'te FAIL var | FAIL | Dur. |
| U-10 | FULL `COMPLETE` ve son audit round freeze-ready değil | FAIL | Dur. |
| U-11 | Pass `COMPLETE` ve scope unit'inin ledger `open_items` alanı dolu | FAIL | `COMPLETE` yazma. |
| U-12 | Pass `COMPLETE` ve bir ULA event `COMPLETE` değil | FAIL | `COMPLETE` yazma. |
| U-13 | Pass `ABANDONED` ve abandon sonrası ledger'da bu pass ID ile değişiklik var | FAIL | Dur. Kullanıcıya göster. |
| U-14 | Resume sırasında `COMPLETE` / `FROZEN` artifact revision route olmadan yeniden yazıldı | FAIL | Dur. |
| U-15 | İki active pass aynı work unit veya event'i içeriyor | FAIL | `CONFLICT` göster. Yeni pass'i başlatma. |
| U-16 | `ula_status` `PENDING` değil ve artifact path boş veya dosya yok | FAIL | Pass `BLOCKED`. |
| U-17 | Full trigger var ama mode `LIGHT` (user override) | WARNING | Sınırı kullanıcıya bir kez göster. Devam et. |
| U-18 | Event `BLOCKED` (revision limit veya reject) | WARNING | Kullanıcıya raporla. Diğer event'lere devam et. |

FAIL olduğunda stage geçişi, Completion Commit ve pass status değişikliği yapılmaz.

Bu bölüm ULA content audit yapmaz. Content audit `ula/LEARNING_AUDITOR.md` rolüne aittir.

---

## L. Learning State Integrity (pointer, passes, maps)

NOT IMPLEMENTED YET.

## Authoritative Source

- Phase 1 audit: Bölüm 15.1, 17 (M-16), 18.
- `references/02_COVERAGE_PROTOCOL.md` §1, §9, §10.
- `references/03_HUMAN_SYNC_PROTOCOL.md` §7, §9, §13, §14, §15.
- `references/04_ULA_PROTOCOL.md` §2, §5, §7, §9, §10, §11.
- Content audit: `ula/LEARNING_AUDITOR.md`.
