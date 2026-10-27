# 07 — Integrity Checks

**Status:** §C Coverage Integrity IMPLEMENTED (Phase 3). §E Event Integrity IMPLEMENTED (Phase 4). §U ULA / Pass Integrity IMPLEMENTED (Phase 5). §M MindMap / Semantic Graph Integrity IMPLEMENTED (Phase 6). §P Knowledge Persistence Integrity IMPLEMENTED (Phase 7). §L NOT IMPLEMENTED YET.

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

## M. MindMap / Semantic Graph Integrity

Ne zaman çalışır:

- Map sync sırasında, aday graph üzerinde, write'tan önce (`05_MINDMAP_PROTOCOL.md` §8–§9).
- `/learning map` komutlarında, mevcut graph ve view üzerinde (M-12, M-15, M-16).

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| M-01 | Duplicate `node_id` | FAIL | Write yok. Event `BLOCKED`. |
| M-02 | Duplicate `edge_id` | FAIL | Write yok. |
| M-03 | Edge `source_node_id` graph'ta yok | FAIL | Write yok. |
| M-04 | Edge `target_node_id` graph'ta yok | FAIL | Write yok. |
| M-05 | Unknown `relation_type` | FAIL | Write yok. |
| M-06 | Unknown `node_type` | FAIL | Write yok. |
| M-07 | Unknown `node_status` | FAIL | Write yok. |
| M-08 | Combined hierarchy cycle (`parent_id` + `PART_OF` edge birlikte) | FAIL | Write yok. |
| M-09 | Node kendi parent'ı veya kendi `PART_OF` hedefi | FAIL | Write yok. |
| M-10 | `SUPERSEDED` ve `superseded_by` boş veya geçersiz | FAIL | Write yok. |
| M-11 | Duplicate semantic edge (aynı source, relation, target) | FAIL | Write yok. |
| M-12 | View graph'ta olmayan node gösteriyor | WARNING | View'ı yeniden üret. |
| M-13 | `source_artifacts` path'i yok | FAIL | Write yok. |
| M-14 | `available_depth` içindeki seviye için artifact / bölüm yok | FAIL | Write yok. |
| M-15 | `generated_from_graph_version > graph_version` | FAIL | View'ı yeniden üret. Kullanıcıya bildir. |
| M-16 | Stale `HORIZONTAL_MAP` (`generated_from_graph_version < graph_version`) | WARNING | View'ı yeniden üret. |
| M-17 | Bir node veya edge listesinde duplicate `source_event_id` / appearance | FAIL | Write yok. |
| M-18 | `map_sync_status: COMPLETE` ama event graph'ta hiçbir node veya edge'de yok | FAIL | Status'u `PENDING` yap. Sync tekrar. |
| M-19 | `ACTIVE` node veya edge kaynağı `UNRESOLVED` veya tamamlanmamış ULA event | FAIL | Write yok. |
| M-20 | `DEBT` node ve `debt_id` boş ya da §B'de yok | FAIL | Write yok. |
| M-21 | Primary parent ayrıca `PART_OF` edge olarak yazılmış (`node.parent_id = X` ve `node PART_OF X`) | FAIL | Write yok. |
| M-22 | Birden fazla `ROOT` node | FAIL | Write yok. |

FAIL olduğunda graph overwrite edilmez, `graph_version` değişmez, view yeniden üretilmez. Coverage ve pass status değişmez.

---

## P. Knowledge Persistence Integrity

Ne zaman çalışır:

- Persistence sırasında, bütün candidate set üzerinde, write'tan önce (`06_KNOWLEDGE_PERSISTENCE.md` §22).
- Final integrity'de, project state ve yüklenmiş personal dosyalar üzerinde.

Kapsam: Personal library yalnız registry + işlemdeki Home + ilgili map ile kontrol edilir. Bütün library yüklenmez. Map satırlarında yalnız current `project_id` satırları doğrulanır.

| ID | Kontrol | Sonuç | Aksiyon |
|---|---|---|---|
| P-01 | Duplicate `concept_id` (registry satırı veya Home dosyası) | FAIL | Write yok. Event `BLOCKED`. |
| P-02 | Duplicate `experience_id` | FAIL | Write yok. |
| P-03 | Registry satırı var, Home dosyası yok | FAIL | Write yok. |
| P-04 | Home dosyası var, registry satırı yok | FAIL | Write yok. |
| P-05 | İki `ACTIVE` registry satırı aynı `Canonical Name` | FAIL | Write yok. Kullanıcı: farklı canonical name veya merge. |
| P-06 | Alias başka bir `ACTIVE` concept'in canonical name veya alias'ı ile çakışıyor | FAIL | Write yok. Kullanıcı kararı. |
| P-07 | Project pointer bilinmeyen `concept_id` gösteriyor | FAIL | Write yok. |
| P-08 | Graph `home_ref` bilinmeyen `concept_id` gösteriyor | FAIL | Write yok. |
| P-09 | Aynı `event_id` için birden fazla Experience Note | FAIL | Write yok. |
| P-10 | Concept Home içinde duplicate Project Appearance (`project_id`, `event_id`) | FAIL | Write yok. |
| P-11 | Experience Note `L0`–`L4` başlığı veya Home section metni taşıyor | FAIL | Write yok. Teoriyi çıkar. |
| P-12 | `RESOLVED` debt: `resolution_ref` ULA `COMPLETE` event değil veya event persistence `COMPLETE` değil veya `concept_home` çözülemiyor | FAIL | Write yok. |
| P-13 | `RESOLVED` debt ve `debt_id` taşıyan graph node hâlâ `DEBT` | FAIL | Write yok. |
| P-14 | Promoted `ACTIVE` node (`debt_id` var, debt `RESOLVED`) ve `home_ref: UNASSIGNED` | FAIL | Write yok. |
| P-15 | `DISMISSED` debt ve `resolution_ref` `user:` kararı değil | FAIL | Write yok. |
| P-16 | Persistence `COMPLETE` ama pass tablosundaki Home / pointer / Experience Note / Decision Record dosyası yok | FAIL | Status `PENDING`. Tekrar persistence. |
| P-17 | `personal_library_path: UNCONFIGURED` ve personal write candidate'i var | FAIL | Write yok. `06` §2.2. |
| P-18 | `LOCAL_TEMPORARY` concept `personal:` olarak işaretli veya personal Home'u yok iken pointer `PERSONAL` | FAIL | Write yok. |
| P-19 | Promotion `concept_id` değiştirdi | FAIL | Write yok. |
| P-20 | SD Experience Map satırı olmayan Experience Note gösteriyor | FAIL | Write yok. |
| P-21 | DSA Experience Map satırı olmayan Experience Note gösteriyor | FAIL | Write yok. |
| P-22 | DSA Experience Map satırı primary category `DSA` olmayan event'e ait | FAIL | Write yok. |
| P-23 | Registry ile Home Identity uyuşmuyor (`Canonical Name`, `Aliases`, `Status`, `Home`) | FAIL | Write yok. |
| P-24 | Library Index veya pointer `Canonical Name` label'ı registry / Home ile uyuşmuyor | WARNING | Index'i ve label'ı yeniden üret. |
| P-25 | Version kuralı ihlali (`06` §9): versioned alan değişti ve `Version` +1 değil, veya versioned alan değişmedi ve `Version` değişti | FAIL | Write yok. |
| P-26 | Dolu Concept Home content section'ında `Provenance:` etiketi yok veya label bilinmiyor | FAIL | Write yok. |
| P-27 | Experience Note claim `VERIFIED` ve ref yok, veya claim status kaynak event'ten güçlü | FAIL | Write yok. |
| P-28 | Project pointer (`Home Mode: PERSONAL`) L0–L4 theory section'ı taşıyor (promotion sonrası duplicate theory) | FAIL | Write yok. |

FAIL olduğunda hiçbir persistence dosyası yazılmaz. Event persistence `BLOCKED`. Coverage, ledger ve pass status değişmez.

---

## L. Learning State Integrity (pointer, passes, maps)

NOT IMPLEMENTED YET.

## Authoritative Source

- Phase 1 audit: Bölüm 15.1, 17 (M-16), 18.
- `references/02_COVERAGE_PROTOCOL.md` §1, §9, §10.
- `references/03_HUMAN_SYNC_PROTOCOL.md` §7, §9, §13, §14, §15.
- `references/04_ULA_PROTOCOL.md` §2, §5, §7, §9, §10, §11.
- `references/05_MINDMAP_PROTOCOL.md` §3–§11.
- `references/06_KNOWLEDGE_PERSISTENCE.md` §4–§22.
- Content audit: `ula/LEARNING_AUDITOR.md`.
