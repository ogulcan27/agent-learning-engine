# PHASE 6 — Persistent Semantic Graph + NotebookLM-Style MindMap + Recursive Zoom Report

## 1. Status

**PHASE 6 STATUS: FROZEN / PASS** (hierarchy amendment uygulandı: `PHASE_6_HIERARCHY_AMENDMENT.md`)
**PHASE 7 STATUS: READY**

```text
START → COVERAGE → HUMAN SYNC → ULA → COMPLETION → MAP SYNC
→ [KNOWLEDGE PERSISTENCE: NOT IMPLEMENTED YET → STOP]
```

## 2. Files Changed

| Dosya | Değişiklik |
|---|---|
| `.claude/skills/learning/references/05_MINDMAP_PROTOCOL.md` | Skeleton → IMPLEMENTED (17 bölüm) |
| `.claude/skills/learning/templates/SEMANTIC_GRAPH_TEMPLATE.md` | Yeni (canonical storage) |
| `.claude/skills/learning/templates/KNOWLEDGE_MAP_TEMPLATE.md` | Skeleton → generated view template |
| `.claude/skills/learning/templates/LEARNING_PASS_TEMPLATE.md` | `## Map Sync` tablosu; Next Stage değerleri |
| `.claude/skills/learning/references/07_INTEGRITY_CHECKS.md` | §M eklendi (M-01…M-22) |
| `.claude/skills/learning/references/01_OPERATIONAL_CORE.md` | Flow Map Sync'e kadar; stop ve write rules |
| `.claude/skills/learning/references/04_ULA_PROTOCOL.md` | Tek satır: pass COMPLETE sonrası Next Stage = MAP SYNC |
| `.claude/skills/learning/references/06_KNOWLEDGE_PERSISTENCE.md` | Kısa Phase 6 boundary pointer. Logic yok. |
| `.claude/skills/learning/SKILL.md` | Router 11 IMPLEMENTED; guard Persistence'ta; `map ...` argümanları; load map |
| `docs/audit/PHASE_6_MINDMAP_TESTS.md` | Yeni |
| `docs/audit/PHASE_6_MINDMAP_REPORT.md` | Yeni |

Değişmeyen: `02`, `03`, `ula/`, original sources.

## 3. Graph Architecture

```text
KNOWLEDGE ≠ PRESENTATION
docs/learning/maps/SEMANTIC_GRAPH.md   → authoritative
docs/learning/maps/HORIZONTAL_MAP.md   → generated view
```

- Görsel harita bilgi kaynağı değildir. Graph'tan yeniden üretilir.
- Graph iki registry taşır: Nodes, Edges.
- Local zoom ve depth view kalıcı dosya değildir.
- Graph L1–L4 içeriğini kopyalamaz. ULA artifact'e pointer tutar.

## 4. Node Model

- 13 istenen alan + `debt_id` + `superseded_by`.
- `node_id = KN-` + 8 hex. Opaque, isimden türetilmez, collision kontrollü, yeniden kullanılmaz.
- Node type: `ROOT`, `DOMAIN`, `CONCEPT`, `SYSTEM_COMPONENT`, `DECISION`, `PATTERN`, `FAILURE_MODE`, `OTHER`.
- Node status: `ACTIVE`, `DEBT`, `SUPERSEDED` (pointer zorunlu).
- `available_depth` yalnız artifact'te gerçekten var olan seviyeler.
- `home_ref: UNASSIGNED` (Phase 7).
- CHILDREN ve PREVIOUS / NEXT saklanmaz. `parent_id` ve `NEXT` edge'lerinden türetilir.

## 5. Edge Model

- `edge_id = KE-NNNN`. Alanlar: source, relation, target, meaning, events, evidence.
- 12 canonical relation. Her biri master'daki horizontal relation türlerine eşlendi (§4.1 tablosu). Yeni relation eklenmedi.
- Dekoratif connector yasak. `NEXT` yalnız gerçek progression. `UNRESOLVED` evidence ile edge yok.
- Hierarchy (amendment sonrası): `parent_id` = primary navigation parent; `PART_OF` edge = secondary semantic membership. Primary parent `PART_OF` edge olarak tekrar yazılamaz (M-21). Combined hierarchy acyclic'tir (M-08). Diğer relation'lar cycle içerebilir.

## 6. Identity Resolution

- Sıra: EVENT (idempotence) → HOME → NODE_ID → NAME + meaning → ALIAS + meaning → AMBIGUOUS → NEW.
- No silent merge. İsim eşleşip meaning farklıysa kullanıcı kararı; event `BLOCKED`.
- Rename: `node_id` aynı, eski isim alias.
- İki node merge: yalnız kullanıcı onayı; biri `SUPERSEDED`.
- DEBT → ACTIVE: aynı node, aynı ID.

## 7. Incremental Update

- READ → DELTA → MATCH → ADD/UPDATE → INTEGRITY → WRITE → VIEW.
- Merge kuralları: liste alanları UNION, edge'ler DEDUPE (source, relation, target).
- Idempotent: aynı pass tekrar sync → değişiklik yok, version aynı.
- Atomic: delta pass başına. FAIL veya AMBIGUOUS → graph yazılmaz, version değişmez, view üretilmez. Sorunlu event `BLOCKED`, diğerleri `PENDING`.
- `graph_version` her başarılı mutation'da +1.

## 8. Map Eligibility

| INCLUDE | EXCLUDE | WAIT |
|---|---|---|
| ULA COMPLETE; EXPERIENCE_ONLY + reusable signal; KNOWLEDGE_DEBT (§B kaydı var) | IMPLEMENTATION_DETAIL; reusable signal olmayan EXPERIENCE_ONLY | UNRESOLVED; ULA not COMPLETE |

- Yalnız `COMPLETE` pass sync edilir.
- Node value testi ve clutter kontrolü: navigation, reusable learning, decision, dependency, failure, transfer değerinden en az biri.
- EXPERIENCE_ONLY önce mevcut node'a bağlanır. Yeni node yalnız DECISION / PATTERN / FAILURE_MODE değeri varsa.

## 9. Map Sync Lifecycle

- Pass `## Map Sync` tablosu: `PENDING`, `COMPLETE`, `NOT_APPLICABLE`, `BLOCKED`.
- `experience_persistence_status`: `PENDING` / `NOT_APPLICABLE`. Phase 5 OI-03 handoff marker'ı.
- Coverage independence: map sync `BLOCKED` olsa da pass `COMPLETE`, unit `COVERED` kalır. Post-completion enrichment.

## 10. Horizontal Map

- X axis = doğal knowledge / system flow. Y axis = seçilen node'un depth'i.
- Root map: ROOT child'ları, `NEXT` sırası, 4–10 block. Fazlası `… +N block` özeti.
- `(DEBT)` text label. Renk yok. `(+N)` açılmamış child sayısı.
- View `generated_from_graph_version` taşır.

## 11. Recursive Zoom

- `/learning map <node-id>`: breadcrumb (`parent_id` zinciri) + node + bir seviye child + relation'lar + depth satırı.
- Üst haritadaki konum kaybolmaz. Torunlar yalnız sayı olarak.

## 12. Depth View

- `/learning map <node-id> Lx`: yalnız `available_depth` içindeki seviye.
- Yoksa `Lx unavailable. Mevcut: ...`. İçerik uydurulmaz.
- Varsa kısa breadcrumb + yalnız ilgili artifact bölümü. Map tekrar basılmaz.

## 13. Commands

`/learning map` · `/learning map <node-id>` · `/learning map <node-id> L1…L4` · `/learning map debt` · `/learning map sync`.

- Tek `/learning` entry point korundu. Ayrı skill yok.
- Map komutları coverage veya ULA çalıştırmaz. Yalnız `map sync` graph yazar.
- Token: map komutları yalnız `05` + graph (+ view) yükler; depth view yalnız ilgili artifact bölümünü.

## 14. Integrity Rules

07 §M: 20 FAIL + 2 WARNING.

- (Amendment: M-08 combined hierarchy cycle, M-09 self parent / self PART_OF, M-21 primary parent duplicated as PART_OF.)
- FAIL: M-01 duplicate node_id, M-02 duplicate edge_id, M-03/M-04 orphan source/target, M-05 relation, M-06 node type, M-07 node status, M-08 hierarchy cycle, M-09 self parent, M-10 SUPERSEDED pointer, M-11 duplicate semantic edge, M-13 artifact path, M-14 depth without content, M-15 view > graph version, M-17 duplicate event/appearance, M-18 sync COMPLETE but absent, M-19 UNRESOLVED as ACTIVE, M-20 DEBT without debt_id, M-21 PART_OF edge row, M-22 multiple ROOT.
- WARNING: M-12 view unknown node, M-16 stale view (regenerate).

## 15. Test Results

- 71/71 PASS (A–S: 58; ek: 13).
- İlk çalıştırmada geçti. Parse edilen kurallar ve view çıktıları elle doğrulandı.
- Mutation: M1 orphan validation (65/71), M2 PART_OF cycle validation (70/71), M3 idempotent merge UNION → APPEND (6/27). Üçü yakalandı.
- Validation: source sha256 15/15 aynı; 56 `.md` UTF-8, BOM yok; `docs/learning/` yok; HTML yok; Graphify yok; personal path yok.

## 16. Regression

Phase 3 24/24, Phase 4 46/46, Phase 5 74/74 PASS.

## 17. Deviations

| ID | Sapma | Gerekçe |
|---|---|---|
| D-01 | Yeni `SEMANTIC_GRAPH_TEMPLATE.md` | Storage (authoritative) ile view (derived) ayrımı. User tercihi ile uyumlu. |
| D-02 | **AMENDED** — bkz. `PHASE_6_HIERARCHY_AMENDMENT.md`. İlk karar: hierarchy yalnız `parent_id`; Edges tablosunda `PART_OF` satırı yok | `parent_id` ile `PART_OF` edge aynı bilgiyi iki yerde tutardı. Tek authoritative yer: `parent_id`. Map'teki parent-child bağı yine semantic `PART_OF` ilişkisidir. Sonuç: tek parent'lı ağaç. |
| D-03 | Node'a `debt_id` ve `superseded_by` eklendi | §20 ve §11 gereksinimleri. Diğer node'larda `-`. |
| D-04 | Identity sırasına `EVENT` adımı eklendi (en başa) | Idempotence için. Aynı event tekrar sync'te node'a dokunmaz. |
| D-05 | `/learning map sync` argümanı | `BLOCKED` / `PENDING` event'leri tekrar denemek için. Ayrı skill yok. |
| D-06 | `KE-NNNN` sıralı edge ID; `KN-` random node ID | Node identity opaque olmalı (§10). Edge'in doğal anahtarı (source, relation, target) zaten var; sıralı ID yeterli. |
| D-07 | Edge `evidence_status` içinde `GENERAL THEORY` etiketi kabul edilir | Graph'ta dış bilgiye dayalı ilişki olabilir. Phase 4 kuralı gibi etiketli. Project fact iddiası değildir. |
| D-08 | `M-22` multiple ROOT check | Root map tek köke dayanır. |
| D-09 | AMBIGUOUS için ayrı `WAITING_USER` map status yok; `BLOCKED` + kullanıcı sorusu | Map sync vocabulary'si 4 değer ile sınırlı tutuldu. |

## 18. Open Issues

| ID | Konu |
|---|---|
| OI-01 | Gerçek target project ile end-to-end map sync yapılmadı. |
| OI-02 | Node / edge extraction ve meaning eşdeğerliği Claude judgment'ına dayanır. Kontrol: AMBIGUOUS → kullanıcı kararı. |
| OI-03 | KAPANDI (amendment). Secondary membership artık `PART_OF` edge ile ifade edilir. `DEPENDS_ON` / `USES` membership için kullanılmaz. |
| OI-04 | Root map'te 10'dan fazla block için DOMAIN gruplaması önerilir ama otomatik yapılmaz. |
| OI-05 | `home_ref`, Experience persistence ve debt `RESOLVED` lifecycle Phase 7'ye bırakıldı. |
| OI-06 | Working copy'de karışık line ending (CRLF / LF). `core.autocrlf=true` commit'te normalize eder; içerik farkı yok. |
| OI-07 | Test script'leri session scratchpad içinde. Spec kalıcı dokümanda. |

## 19. Phase 7 Readiness

**READY.**

Phase 7 girdileri:

- Graph node'larında `home_ref: UNASSIGNED` → Concept Home ataması.
- Pass `## Map Sync` tablosunda `Experience Persistence: PENDING` → Experience Note / Map.
- `DEBT` node'ları ve §B kayıtları → debt `RESOLVED` lifecycle.
- `project_appearances` → cross-project genişleme noktası.
- Router guard Knowledge Persistence adımında duruyor.
