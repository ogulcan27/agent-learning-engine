# 05 — MindMap Protocol

**Status:** IMPLEMENTED (Phase 6)

## Purpose

`COMPLETE` Learning Pass'lerden yüksek değerli bilgiyi project-local Semantic Graph içine yerleştirir.
Graph'tan horizontal, recursive ve progressive-disclosure kullanan bir Knowledge Map üretir.

## Responsibility

- Map eligibility ve node / edge extraction.
- Identity resolution ve merge.
- Incremental, idempotent ve atomic graph update.
- Map sync status.
- Horizontal root map, recursive zoom, depth view.
- `/learning map ...` komutları.

## Must Not

- HTML üretmez (Phase 1 Q8). Harici graph tool'u kullanmaz.
- Dekoratif edge çizmez.
- Depth'i horizontal axis'e koymaz.
- L1–L4 içeriğini graph'a kopyalamaz. Pointer tutar.
- Concept Home, Personal Technical Library veya Experience Map yazmaz (`06`).
- Coverage, ledger veya pass status'unu değiştirmez.
- İsim eşleşmesi ile sessiz merge yapmaz.

---

## 1. Graph vs view

```text
KNOWLEDGE ≠ PRESENTATION

SEMANTIC GRAPH    → source of truth (authoritative)
HORIZONTAL MAP    → graph view (derived, yeniden üretilebilir)
```

- Görsel harita bilgi kaynağı değildir.
- Harita bozulursa graph'tan yeniden üretilir.
- Haritada görünen her bağlantı graph'ta semantic bir ilişkidir.

Üretim sırası:

```text
LEARNING PASS → KNOWLEDGE EXTRACTION → SEMANTIC GRAPH → HORIZONTAL MAP → RECURSIVE VIEW
```

---

## 2. Runtime paths

```text
docs/learning/maps/
├── SEMANTIC_GRAPH.md    authoritative      templates/SEMANTIC_GRAPH_TEMPLATE.md
└── HORIZONTAL_MAP.md    generated view     templates/KNOWLEDGE_MAP_TEMPLATE.md
```

- Local zoom ve depth view kalıcı dosya değildir. Terminal / chat view olarak üretilir.
- Dosya yoksa ilk sync'te template'ten oluşturulur. Mevcut dosya overwrite edilmez; delta yazılır (§8).

---

## 3. Node model

| Alan | Değer |
|---|---|
| `node_id` | `KN-xxxxxxxx` (§3.1) |
| `canonical_name` | Canonical technical term |
| `node_type` | §3.2 |
| `parent_id` | Primary navigation parent `node_id` veya `-` (§5) |
| `short_meaning` | Tek kısa cümle (Türkçe) |
| `system_role` | Sistemdeki rolü, tek kısa cümle |
| `home_ref` | Concept ID `CH-xxxxxxxx` veya `UNASSIGNED`. Yalnız `06` §21 atar. |
| `available_depth` | `L1`…`L4` alt kümesi veya `-` (§3.4) |
| `source_event_ids` | Kaynak `event_id` listesi |
| `source_artifacts` | ULA artifact veya pass path listesi |
| `project_appearances` | `learning_pass_id` listesi |
| `aliases` | Eski veya alternatif isimler |
| `node_status` | §3.3 |
| `debt_id` | `DEBT` node: `KD-...` zorunlu. `DEBT → ACTIVE` promoted node: historical reference olarak korunur. Diğerleri `-`. |
| `superseded_by` | Yalnız `SUPERSEDED` node: canonical `node_id`. Diğerleri `-`. |

Liste alanları `; ` ile ayrılır.

Derived alanlar saklanmaz:

| Master alanı | Türetme |
|---|---|
| CHILDREN | `parent_id` = bu node olan node'lar |
| PREVIOUS / NEXT | `NEXT` edge'leri |

### 3.1 Node ID

- Format: `KN-` + 8 lowercase hex. Örnek: `KN-3fa91c07`.
- Opaque. `canonical_name`'den türetilmez. Canonical name değişebilir; knowledge identity değişmez.
- Rastgele üretilir. Graph'taki bütün `node_id` değerleri ile (SUPERSEDED dahil) collision kontrolü yapılır.
- Bir kez atanan ID yeniden kullanılmaz. Node satırı silinmez.

### 3.2 Node type

| Type | Anlam |
|---|---|
| `ROOT` | Project graph kökü. Graph başına bir tane. |
| `DOMAIN` | Büyük alan (ör. Async Processing) |
| `CONCEPT` | Reusable kavram |
| `SYSTEM_COMPONENT` | Sistemdeki somut bileşen |
| `DECISION` | Önemli tasarım kararı |
| `PATTERN` | Reusable problem pattern |
| `FAILURE_MODE` | Önemli hata davranışı |
| `OTHER` | Yukarıdakilere uymayan, ama değerli |

Mechanism ayrı type değildir. Çoğu durumda bir concept'in L2 içeriğidir. Bağımsız ve reusable ise `CONCEPT` olur.

### 3.3 Node status

| Status | Anlam |
|---|---|
| `ACTIVE` | Öğrenilmiş veya güvenilir project knowledge |
| `DEBT` | Knowledge Debt olarak bilinen, henüz öğrenilmemiş kavram |
| `SUPERSEDED` | Artık canonical değil. `superseded_by` zorunlu. Silinmez. |

### 3.4 Available depth

Yalnız gerçekten var olan içerik işaretlenir.

| Kaynak | available_depth |
|---|---|
| `LIGHT_ULA.md` | `L1; L2`, L3 bölümü doluysa `L3` eklenir |
| Full `CONTENT.md` | İçerikte bulunan katmanlar (L1–L4) |
| `EXPERIENCE_ONLY` event | `-` (pointer pass event'ine) |
| `DEBT` | `-` |

Graph depth içeriği taşımaz. `source_artifacts` pointer verir.

```text
GRAPH        → WHERE / WHAT / RELATION
ULA ARTIFACT → DETAILED LEARNING CONTENT
```

---

## 4. Edge model

| Alan | Değer |
|---|---|
| `edge_id` | `KE-NNNN`. Graph içinde benzersiz. Max + 1. Yeniden kullanılmaz. |
| `source_node_id` | Var olan `node_id` |
| `relation_type` | §4.1 |
| `target_node_id` | Var olan `node_id` |
| `meaning` | `SOURCE → RELATION → TARGET` cümlesi |
| `source_event_ids` | Kaynak event listesi |
| `evidence_status` | `VERIFIED (ref)` · `INFERRED` · `GENERAL THEORY` |

### 4.1 Canonical relation vocabulary

| Relation | Anlam | Horizontal relation karşılığı |
|---|---|---|
| `NEXT` | Doğal process / reasoning / data / time ilerlemesi | time flow, process, reasoning flow, data flow |
| `REQUIRES` | Source çalışmak için target'a ihtiyaç duyar | dependency (ön koşul) |
| `PRODUCES` | Source target'ı üretir | data flow (çıktı) |
| `CAUSES` | Source target'ı doğurur | causal flow |
| `USES` | Source target'ı kullanır | dependency (kullanım) |
| `DEPENDS_ON` | Source'un davranışı target'a bağlı | dependency |
| `ALTERNATIVE_TO` | Aynı problem için alternatif | branching decision |
| `COMPARED_WITH` | Bilinçli karşılaştırma | comparison |
| `PART_OF` | Source target'ın parçası. Edge olarak yalnız secondary membership (§5). | parent-child |
| `EVIDENCE_FOR` | Source target iddiasını destekler | evidence chain |
| `FAILS_WHEN` | Source target koşulunda bozulur | failure behaviour |
| `IMPLEMENTED_BY` | Source kavram target bileşeni ile gerçeklenir | concept → component |

Kurallar:

- Stored `relation_type` yalnız bu 12 token'dan biridir. User-facing map Türkçe açıklama kullanabilir.
- Yeni relation eklemeden önce bu set ile ifade edilip edilemeyeceği kontrol edilir. Sessiz vocabulary expansion yok.
- Açıklanamayan bağlantı eklenmez. `A --- B` gibi dekoratif connector yasaktır.
- `NEXT` yalnız gerçek semantic progression içindir. Görsel sıralama için kullanılmaz.
- `UNRESOLVED` evidence ile edge eklenmez.

---

## 5. Hierarchy

Membership iki türdür. Her membership tek yerde saklanır.

```text
parent_id     = PRIMARY NAVIGATION PARENT     (node satırında, en fazla bir tane)
PART_OF edge  = SECONDARY SEMANTIC MEMBERSHIP (Edges tablosunda, sıfır veya daha fazla)
```

Örnek:

```text
Kalman Filter   parent_id → State Estimation        primary
Kalman Filter   PART_OF   → Bayesian Filtering      secondary
```

### 5.1 Kurallar

- Primary parent yalnız `parent_id` içinde tutulur. Aynı membership ayrıca `PART_OF` edge olarak yazılmaz. `node.parent_id = X` ve `node PART_OF X` birlikte → FAIL (duplicate membership).
- `node.parent_id = X` ve `node PART_OF Y` (Y ≠ X) geçerlidir.
- Bir node birden fazla secondary `PART_OF` edge taşıyabilir.
- Node kendisinin parent'ı veya `PART_OF` hedefi olamaz.
- `ROOT` parent'ı `-`. Diğer node'lar için `-` yalnız geçici olarak kabul edilir ve root map'te "unplaced" olarak görünür.

### 5.2 Combined hierarchy cycle

Primary `parent_id` bağları ve secondary `PART_OF` edge'leri birlikte semantic hierarchy oluşturur. Bu combined hierarchy acyclic olmalıdır.

| Örnek | Sonuç |
|---|---|
| `A parent_id → B`, `B PART_OF A` | FAIL (cycle) |
| `A PART_OF B`, `B PART_OF A` | FAIL (cycle) |
| `A PART_OF B`, `A PART_OF C` | Geçerli |
| `A DEPENDS_ON B`, `B DEPENDS_ON A` | Hierarchy FAIL değil |

Diğer relation'lar cycle içerebilir. Yalnız combined hierarchy acyclic olmalıdır.

### 5.3 Doğru relation

- Taxonomic veya compositional membership yalnız `parent_id` veya `PART_OF` ile ifade edilir.
- `DEPENDS_ON` veya `USES` yalnız gerçek dependency veya kullanım ilişkisi varsa eklenir. Membership yerine otomatik üretilmez.

### 5.4 Navigation

- Recursive zoom ve breadcrumb yalnız `parent_id` zincirini kullanır. Her node'un tek primary navigation location'ı vardır.
- Secondary `PART_OF` breadcrumb'ı değiştirmez. Local view içinde `Also Part Of:` altında gösterilir (§13).
- CHILDREN (derived) = `parent_id` bu node olan node'lar. Secondary üyeler local view içinde `Secondary Members:` altında gösterilir.

---

## 6. Map eligibility

Yalnız `pass_status: COMPLETE` pass'lerin event'leri sync edilir.

| disposition | condition | map |
|---|---|---|
| ULA_CANDIDATE | ula_status COMPLETE | INCLUDE |
| ULA_CANDIDATE | ula_status not COMPLETE | WAIT |
| EXPERIENCE_ONLY | reusable signal var | INCLUDE |
| EXPERIENCE_ONLY | reusable signal yok | EXCLUDE |
| KNOWLEDGE_DEBT | §B kaydı var | INCLUDE |
| IMPLEMENTATION_DETAIL | - | EXCLUDE |
| UNRESOLVED | - | WAIT |

`NOT_LEARNING_RELEVANT` unit'lerin event'i yoktur. Graph'a bir şey eklemez.

### 6.1 Node extraction

Bir event'ten çıkarılabilir: canonical concept, system component, important decision, reusable pattern, important failure mode.

Node value testi: Bu node gelecekte bilgi üzerinde yön bulmayı veya transfer yapmayı kolaylaştırıyor mu?

En az biri gerekir: navigation, reusable learning, decision, dependency, failure understanding, transfer.

- Her heading veya her teknik terim node olmaz.
- `EXPERIENCE_ONLY` önce mevcut node'a bağlanmayı dener. Yeni node yalnız event anlamlı bir `DECISION`, `PATTERN` veya `FAILURE_MODE` ise açılır.
- `KNOWLEDGE_DEBT` → `node_status: DEBT`, `debt_id` zorunlu, `available_depth: -`. Theory üretilmez.
- `UNRESOLVED` veya tamamlanmamış ULA bilgisi `ACTIVE` knowledge olarak yazılmaz.

### 6.2 Edge extraction

Edge yalnız event, Human Sync Mental Model veya ULA artifact bir ilişkiyi açıkça gösteriyorsa eklenir. Evidence status event'ten taşınır. Project'te yapılmamış ilişki "yaptık" diye yazılmaz; dış bilgi `GENERAL THEORY` etiketlenir.

---

## 7. Identity resolution

Her aday node için sırayla. İlk eşleşen satır uygulanır.

| step | match | result |
|---|---|---|
| EVENT | Aday event zaten bu node'un `source_event_ids` içinde | Aynı node. Değişiklik yok. |
| HOME | Exact `home_ref` eşleşmesi (`UNASSIGNED` hariç) | Aynı node |
| NODE_ID | Event / artifact var olan bir `node_id` referansı taşıyor | Aynı node |
| NAME | Exact `canonical_name` + equivalent meaning | Aynı node |
| ALIAS | Alias + equivalent meaning | Aynı node |
| AMBIGUOUS | İsim veya alias eşleşiyor, meaning farklı veya belirsiz | Kullanıcı kararı. Event `BLOCKED`. |
| NEW | Eşleşme yok | Yeni node |

Kurallar:

- No silent merge. Örnek: `Application State ≠ Statistical State`.
- `AMBIGUOUS` durumunda pass delta'sı yazılmaz (§9). Kullanıcı seçer: aynı node, yeni node (farklı canonical name ile) veya iptal.
- `SUPERSEDED` node eşleşirse `superseded_by` hedefi kullanılır.

### 7.1 Merge rules

| field | merge |
|---|---|
| source_event_ids | UNION |
| source_artifacts | UNION |
| project_appearances | UNION |
| aliases | UNION |
| available_depth | UNION |
| edges | DEDUPE (source, relation, target) |

Edge dedupe: aynı `(source, relation, target)` varsa yeni edge açılmaz. `source_event_ids` UNION ile güncellenir.

### 7.2 Rename

- `node_id` değişmez.
- Eski `canonical_name` → `aliases`.
- Kullanıcı isteği veya ULA canonical term değişikliği ile yapılır. Sessiz rename yok.

### 7.3 Merge of two nodes

Yalnız kullanıcı onayı ile. Biri canonical kalır. Diğeri `SUPERSEDED` olur, `superseded_by` yazılır. Edge'ler canonical node'a taşınır. Satır silinmez.

### 7.4 DEBT → ACTIVE

Aynı concept için ULA `COMPLETE` event gelirse DEBT node `ACTIVE` olur. `node_id` değişmez. `available_depth` artifact'ten yazılır. Debt kaydının `RESOLVED` lifecycle'ı `06`'ya aittir.

---

## 8. Incremental update

```text
READ EXISTING GRAPH
↓
EXTRACT DELTA        (yalnız map_sync_status PENDING / BLOCKED event'ler)
↓
MATCH EXISTING NODES (§7)
↓
ADD / UPDATE NODES
↓
ADD / UPDATE EDGES
↓
INTEGRITY CHECK      (07 §M, aday graph üzerinde)
↓
WRITE GRAPH          graph_version + 1
↓
REGENERATE VIEW
```

- DELTA UPDATE ≠ FULL REWRITE. Mevcut satırlar yalnız merge kuralları ile değişir.
- Idempotence: aynı pass tekrar sync edilirse duplicate node, edge veya appearance oluşmaz. Delta boşsa graph yazılmaz ve `graph_version` artmaz.

---

## 9. Atomic update

- Delta pass başına atomiktir.
- Aday graph integrity FAIL verirse veya bir aday `AMBIGUOUS` ise:
  - mevcut graph overwrite edilmez,
  - `graph_version` değişmez,
  - map regeneration yapılmaz,
  - sorunlu event `map_sync_status: BLOCKED`; diğer event'ler `PENDING` kalır.
- Partial graph write yoktur.

---

## 10. Map sync status

Pass içinde `## Map Sync` tablosunda event bazında tutulur.

| Status | Anlam |
|---|---|
| `PENDING` | Eligible. Henüz sync edilmedi. |
| `COMPLETE` | Graph update başarılı. Event graph'ta en az bir node veya edge'de görünür. |
| `NOT_APPLICABLE` | Map'e dahil edilmez (EXCLUDE veya node value yok). |
| `BLOCKED` | Identity veya integrity problemi. |

`WAIT` event'ler pass `COMPLETE` olana kadar tabloya girmez.

### 10.1 Experience persistence marker

Aynı tabloda `experience_persistence_status`:

| Değer | Ne zaman |
|---|---|
| `PENDING` | `EXPERIENCE_ONLY` veya `COMPLETE` ULA event |
| `NOT_APPLICABLE` | Diğerleri |

Map sync yalnız başlangıç değerini yazar. Tam lifecycle (`PENDING` · `COMPLETE` · `NOT_APPLICABLE` · `BLOCKED`) `06` §19'dadır.

### 10.2 Coverage independence

Map sync post-completion enrichment'tır.

- Map sync `BLOCKED` olsa da coverage yeniden açılmaz.
- Work unit `COVERED` durumundan dönmez.
- Pass `COMPLETE` kalır. `current_stage` değişmez.

---

## 11. Graph version ve stale view

- Her başarılı graph mutation `graph_version` değerini 1 artırır. İlk graph `1`.
- `HORIZONTAL_MAP.md` `generated_from_graph_version` taşır.
- `generated_from_graph_version < graph_version` → stale → WARNING, view yeniden üretilir.
- `generated_from_graph_version > graph_version` → FAIL (view graph'tan yeni olamaz).

---

## 12. Horizontal map

### 12.1 Geometry

```text
X AXIS = doğal knowledge / system flow      (sağa → sistemde veya reasoning'de ilerle)
Y AXIS = seçilmiş node'un depth'i           (aşağı → aynı node'u derin öğren)
```

Depth horizontal axis'e konmaz.

### 12.2 Root map

- `ROOT` node'un child'ları major block'tur. Hedef 4–10 block.
- Sıra `NEXT` edge'lerinden gelir. `NEXT` zinciri `→` ile tek satırda çizilir.
- Zincir dışındaki block'lar ayrı satırda listelenir.
- 10'dan fazla block varsa: en çok descendant taşıyan 9 block gösterilir. Kalanı tek satır özet: `… +N block (map <root-id>)`. Kullanıcıya `DOMAIN` gruplaması önerilir.
- Her block: `[Canonical Name] (+child sayısı)`. Bütün graph dökülmez.
- `DEBT` node: `[Name] (DEBT)`. Renk kullanılmaz.
- `parent_id: -` olan node'lar `Unplaced:` satırında gösterilir.

Örnek:

```text
[Long Request] → [Background Queue] (+3) → [Worker] (+2) → [Result]

                     ┌→ [Synchronous Call]      ALTERNATIVE_TO
[Decision Point] ────┼→ [Background Queue]      selected
                     └→ [Batch Job]             ALTERNATIVE_TO
```

### 12.3 Legend

| Sembol | Relation |
|---|---|
| `→` | NEXT |
| `↳` | Primary child (`parent_id`) |
| `-USES→`, `-REQUIRES→`, … | Diğer relation, token adı ile |
| `(DEBT)` | `node_status: DEBT` |

---

## 13. Recursive zoom

Komut: `/learning map <node-id>`.

```text
<WORLD> → <REGION> → <CURRENT NODE>        breadcrumb (parent_id zinciri)

[CURRENT NODE] — short_meaning
├── ↳ [CHILD A]
├── ↳ [CHILD B]
└── ↳ [CHILD C]

Also Part Of:
- [Secondary Domain]

Secondary Members:
- [Node whose PART_OF → this node]

Relations:
-USES→ [X]
-FAILS_WHEN→ [Y]

Depth: ✓ L1  ✓ L2  — L3  — L4
```

- Üst haritadaki konum kaybolmaz. Breadcrumb her zaman gösterilir.
- Breadcrumb yalnız primary `parent_id` zincirinden üretilir. Secondary `PART_OF` breadcrumb'ı değiştirmez.
- `Also Part Of` ve `Secondary Members` boşsa gösterilmez.
- Yalnız bir seviye child açılır.
- Torunlar `(+N)` sayısı ile gösterilir.

---

## 14. Depth view

Komut: `/learning map <node-id> L1|L2|L3|L4`.

- Yalnız `available_depth` içindeki seviye açılır.
- Seviye yoksa: `L3 unavailable. Mevcut: L1, L2.` İçerik uydurulmaz. Kullanıcı isterse yeni learning pass önerilir.
- Seviye varsa: kısa breadcrumb + `source_artifacts` içindeki ilgili bölüm. Yalnız o bölüm okunur ve gösterilir.
- Bütün map tekrar basılmaz.

---

## 15. Commands

| Komut | Davranış |
|---|---|
| `/learning map` | Root map. Stale ise önce view regeneration. |
| `/learning map <node-id>` | Recursive local zoom |
| `/learning map <node-id> L1`…`L4` | Depth view |
| `/learning map debt` | `DEBT` node listesi: name, debt_id, parent |
| `/learning map sync` | `COMPLETE` pass'lerde `PENDING` / `BLOCKED` event'leri sync et |

- Map komutları coverage, discovery veya ULA çalıştırmaz.
- Yalnız `map sync` graph yazar. Diğerleri yalnız stale view'ı yeniden üretebilir.

Progressive expansion: Map expands. Content does not dump. Bir çağrıda bütün branch, depth veya reference açılmaz.

---

## 16. Token / context rules

| Komut / stage | Yükle |
|---|---|
| Map sync | Bu dosya + `SEMANTIC_GRAPH.md` + pass `LEARNING_PASS.md` + `07` §M. ULA artifact yalnız depth tespiti için başlık düzeyinde. |
| `map`, `map <node-id>` | Bu dosya + `SEMANTIC_GRAPH.md` (+ `HORIZONTAL_MAP.md`) |
| `map <node-id> Lx` | Yukarıdaki + yalnız ilgili artifact bölümü |

`00_MASTER_SYSTEM_SPEC.md`, `ula/` rol dosyaları ve `ula/examples/` yüklenmez.

---

## 17. Persistence boundary

```text
Semantic Graph                        → project-local knowledge structure (bu dosya)
Concept Home / Experience persistence → 06_KNOWLEDGE_PERSISTENCE.md
```

`home_ref` yalnız `06` §21 ile atanır. Bu update `node_id` ve semantic identity'yi değiştirmez. Global cross-project graph yoktur.

---

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §21–§26, §32, §46, §47.
- `ula/ULA_SPECIFICATION.md` §5, §13, §14, §31.
- Phase 1 audit: Bölüm 5, Q8.
