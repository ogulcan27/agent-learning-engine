# 06 — Knowledge Persistence

**Status:** IMPLEMENTED (Phase 7). §22.1 write lock: Phase 8.

## Purpose

Learning pipeline çıktısını doğru kalıcı konuma yazar.

```text
GENERAL KNOWLEDGE  ≠  PROJECT EXPERIENCE
ONE CONCEPT        →  ONE HOME
```

- General knowledge → Concept Home (Personal Technical Library).
- Project experience → Experience Note (project).
- Cross-project reuse → Concept Registry + Experience Maps (Personal Technical Library).

## Responsibility

- Persistence routing ve event bazında persistence status.
- Concept identity, resolution, Concept Home create / delta update.
- Concept Registry, Library Index, project pointer.
- `LOCAL_TEMPORARY` mode ve promotion.
- Experience Note, Decision Record, System Design ve DSA Experience Map.
- Knowledge Debt `RESOLVED` lifecycle.
- Graph `home_ref` ataması.
- `/stay-in-the-loop concept`, `/stay-in-the-loop library`, `/stay-in-the-loop experiences`, `/stay-in-the-loop debt` komutları.

## Must Not

- Aynı teoriyi ikinci kez yazmaz. Mevcut Concept Home'a delta ekler.
- Concept Home'u baştan rewrite etmez. Teoriyi sessizce değiştirmez.
- Yeni teori üretmez. İçeriği yalnız `COMPLETE` ULA artifact'ten taşır.
- `personal_library_path` değerini hard-code etmez. Absolute path seçmez.
- Library yapılandırılmadıysa hata vermez ve personal write yapmaz.
- Coverage, ledger, pass status veya `current_stage` değiştirmez.
- Global cross-project Semantic Graph, HTML veya database oluşturmaz.
- Normal project work sırasında personal library yüklemez.

---

## 1. Three state layers

| Katman | Konum | İçerik |
|---|---|---|
| UNIVERSAL SKILL LOGIC | `.claude/skills/stay-in-the-loop/` | Kurallar, template'ler, universal DSA pattern vocabulary (§17.3). Runtime'da read-only. |
| PROJECT-SPECIFIC STATE | `docs/learning/` | Pass, graph, Experience Note, Decision Record, concept pointer, state. |
| PERSONAL CROSS-PROJECT STATE | `LEARNING_CONFIG.personal_library_path` | Concept Home, Concept Registry, Library Index, Experience Maps. |

Personal library path yalnız config'ten okunur. Skill dosyalarında, pointer'larda veya graph'ta absolute personal path yazılmaz.

---

## 2. Config

`docs/learning/state/LEARNING_CONFIG.md` (template: `templates/LEARNING_CONFIG_TEMPLATE.md`).

| Alan | Değer | Kural |
|---|---|---|
| `project_id` | `PRJ-xxxxxxxx` veya `UNCONFIGURED` | Kalıcı. Rename ile değişmez. |
| `project_name` | Serbest metin veya `UNCONFIGURED` | Değişebilir. Identity değildir. |
| `personal_library_path` | Path veya `UNCONFIGURED` | Kullanıcı belirler. |
| `work_unit_source` | `auto` · `jira` · `git` · `phase-doc` | `02` §3 |

### 2.1 project_id

- Format: `PRJ-` + 8 lowercase hex. Opaque. Project name'den türetilmez.
- `UNCONFIGURED` ise persistence ilk çalıştığında bir ID üretir ve kullanıcıya gösterir. Config yalnız kullanıcı onayı ile yazılır. Onay yoksa event `BLOCKED` (config).
- Bir kez yazılan `project_id` değişmez.
- `project_name` değişirse yeni appearance'lar yeni adı kullanır. Eski kayıtlar değişmez. Identity `project_id` ile yapılır.

### 2.2 Personal library unconfigured

`personal_library_path: UNCONFIGURED` ve persistence bir Concept Home veya Experience Map yazmak istiyorsa kullanıcıya sor:

```text
Personal Technical Library yapılandırılmadı.

1. Personal Technical Library path yapılandır.
2. Project-local temporary Concept Home kullan.
3. Persistence işlemini şimdilik ertele.
```

| Seçim | Sonuç |
|---|---|
| 1 | Kullanıcı path verir. Config kullanıcı onayı ile yazılır. Library yoksa §3.1 yapısı oluşturulur. Persistence devam eder. |
| 2 | `LOCAL_TEMPORARY` mode (§13). Personal write yok. |
| 3 | Event `PENDING` kalır. Write yok. |

Skill kendi başına path seçmez. Seçim yalnız bu run için geçerlidir; kalıcı tercih yalnız config ile yapılır.

### 2.3 Project isolation

Personal library project dışında olabilir. Active project root'u değiştirmez (01 §0).

| Durum | Sonuç |
|---|---|
| Path explicit configured ve bir project state dizini değil | Library olarak kullanılır. Root değişmez. |
| Path bir `docs/learning/` dizinini veya altını gösteriyor | CONFIG ERROR |
| Library içeriği project adı, `project_id` veya pass içeriyor | Root seçimi için kullanılmaz. |

---

## 3. Storage layout

### 3.1 Personal library

```text
<personal_library_path>/
├── LIBRARY_INDEX.md                         generated view      templates/PERSONAL_LIBRARY_INDEX_TEMPLATE.md
├── concepts/
│   └── <concept-id>.md                      Concept Home        templates/CONCEPT_HOME_TEMPLATE.md
├── experience-maps/
│   ├── SYSTEM_DESIGN_EXPERIENCE_MAP.md      cross-project index templates/SYSTEM_DESIGN_EXPERIENCE_MAP_TEMPLATE.md
│   └── DSA_EXPERIENCE_MAP.md                cross-project index templates/DSA_EXPERIENCE_MAP_TEMPLATE.md
├── registry/
│   └── CONCEPT_REGISTRY.md                  identity registry   templates/CONCEPT_REGISTRY_TEMPLATE.md
└── .learning-write-lock/                    yalnız write sırasında (§22.1)
    └── LOCK.md
```

Markdown canonical storage'dır. HTML, application veya database yoktur.

### 3.2 Project

```text
docs/learning/
├── concepts/<concept-id>.md        pointer (PERSONAL) veya full temporary home (LOCAL_TEMPORARY)
├── experiences/<experience-id>.md  Experience Note           templates/EXPERIENCE_NOTE_TEMPLATE.md
├── experiences/<decision-id>.md    Decision Record           templates/DECISION_RECORD_TEMPLATE.md
├── maps/                           Semantic Graph (05)
├── passes/                         Learning Pass (03, 04)
└── state/                          config, ledger, queue
```

Dosya adı ID'dir. İsim değişse de dosya adı değişmez.

---

## 4. Identity

| ID | Format | Kapsam | Üretim |
|---|---|---|---|
| `project_id` | `PRJ-` + 8 hex | Project | §2.1 |
| `concept_id` | `CH-` + 8 hex | Personal library (cross-project) | §7 NEW |
| `experience_id` | `EX-` + 8 hex | Project | §15.1 |
| `decision_id` | `DR-` + 8 hex | Project | §16 |

Ortak kurallar:

- Lowercase hex. Rastgele. Opaque. İsimden türetilmez.
- Collision kontrolü: `CH` için registry + project `concepts/`; `EX` ve `DR` için project `experiences/`.
- Bir kez atanan ID değişmez ve yeniden kullanılmaz. Rename, promotion ve project rename ID'yi değiştirmez.

### 4.1 Home locator

Concept Home konumu portable logical locator ile yazılır:

| Locator | Çözüm |
|---|---|
| `personal:CH-xxxxxxxx` | `<personal_library_path>/concepts/CH-xxxxxxxx.md` |
| `local-temporary:CH-xxxxxxxx` | `docs/learning/concepts/CH-xxxxxxxx.md` |

- Graph `home_ref` yalnız bare `CH-xxxxxxxx` saklar. Mode, project pointer'dan okunur.
- Path çözümü config ile yapılır. Locator absolute path taşımaz.

---

## 5. Persistence routing

Yalnız `pass_status: COMPLETE` pass'lerin event'leri işlenir. Satır sırası önemlidir. İlk eşleşen satır uygulanır.

| disposition | condition | concept_home | experience_note | status |
|---|---|---|---|---|
| IMPLEMENTATION_DETAIL | - | NO | NO | NOT_APPLICABLE |
| EXPERIENCE_ONLY | reusable signal yok | NO | NO | NOT_APPLICABLE |
| EXPERIENCE_ONLY | reusable signal var | EXISTING_ONLY | YES | PENDING |
| ULA_CANDIDATE | ula_status COMPLETE | YES | IF_PROJECT_EXPERIENCE | PENDING |
| ULA_CANDIDATE | ula_status not COMPLETE | NO | NO | BLOCKED |
| KNOWLEDGE_DEBT | - | NO | NO | NOT_APPLICABLE |
| UNRESOLVED | - | NO | NO | BLOCKED |

Değerler:

| Değer | Anlam |
|---|---|
| `YES` | Concept Home oluştur veya mevcut Home'a delta / appearance ekle. |
| `EXISTING_ONLY` | Concept mevcut bir Home'a çözülürse yalnız Project Appearance ekle. Yeni Home açma. Çözülmezse `concept_id: UNASSIGNED`. |
| `IF_PROJECT_EXPERIENCE` | Event project problem ve (selected decision veya observed behaviour) taşıyorsa ve bu alanlar `UNRESOLVED` değilse Experience Note yaz. Saf teorik öğrenme → note yok. |
| `NO` | Yazma. |

Notlar:

- Pass `COMPLETE` olması bu routing'i değiştirmez.
- `KNOWLEDGE_DEBT`: debt referansı queue §B ve graph `DEBT` node içinde kalır. Learned Concept Home içeriği yazılmaz.
- `UNRESOLVED` → `BLOCKED` (not ready). Teori veya experience yazılmaz.
- Graph node'u olan event için map sync önce `COMPLETE` olmalıdır. Map sync `PENDING` / `BLOCKED` ise persistence `PENDING` kalır. Map sync `NOT_APPLICABLE` ise graph adımı atlanır.

---

## 6. Persistence flow

Event bazında. Pass içindeki event sırası ile.

```text
ROUTING            (§5)
↓
CONFIG CHECK       project_id, personal_library_path (§2)
↓
CONCEPT RESOLUTION (§7)            yalnız registry okunur
↓
READ CANDIDATE HOME                yalnız eşleşen Home
↓
COMPARE            APPEARANCE_ONLY / ENRICH / CONFLICT (§9)
↓
BUILD CANDIDATES   Home, Registry, pointer, Experience Note, Decision Record,
                   map row, graph home_ref, debt status
↓
INTEGRITY          07 §P (+ 07 §M graph değişiyorsa)
↓
WRITE              §22 sırası, all-or-nothing
↓
STATUS             pass ## Map Sync → Experience Persistence
```

Checkpoint: pass başına bir kez. Write'tan önce kısa plan gösterilir: yeni Home, enrichment, appearance, Experience Note, map row. Conflict (§10) ve config sorusu (§2.2) ayrıca sorulur. Kullanıcı onayı yoksa write yok; event'ler `PENDING` kalır.

---

## 7. Concept resolution

Yeni Concept Home açmadan önce sırayla. İlk eşleşen satır uygulanır.

| step | match | result |
|---|---|---|
| GRAPH_HOME_REF | Event'in graph node'u `home_ref: CH-...` taşıyor | Aynı concept |
| CONCEPT_ID | Event, artifact veya project pointer exact `concept_id` taşıyor | Aynı concept |
| NAME | Registry `Canonical Name` + equivalent meaning | Aynı concept |
| ALIAS | Registry `Aliases` + equivalent meaning | Aynı concept |
| AMBIGUOUS | İsim veya alias eşleşiyor, meaning farklı veya belirsiz | Kullanıcı kararı. Event `BLOCKED`. |
| NEW | Eşleşme yok | Yeni `concept_id` + yeni Concept Home |

- No silent merge. Aynı isim farklı meaning taşıyabilir (`Application State ≠ Statistical State`).
- Meaning karşılaştırması registry `Short Meaning` ile yapılır. Home dosyası yalnız eşleşme sonrası okunur.
- `MERGED` registry satırı eşleşirse hedef `concept_id` kullanılır (§14.2).
- `LOCAL_TEMPORARY` mode: registry yerine project `docs/learning/concepts/*.md` Identity blokları kullanılır.
- `AMBIGUOUS` seçenekleri: aynı concept, yeni concept (farklı canonical name ile), iptal.

---

## 8. Concept Home

Template: `templates/CONCEPT_HOME_TEMPLATE.md`.

Concept Home general technical knowledge'dır. Project story değildir.

### 8.1 Source rule

| Kaynak | Home'a taşınan |
|---|---|
| LIGHT `LIGHT_ULA.md`, `status: COMPLETE` | Mevcut L0, L1, L2 ve doluysa L3; Boundary, Retrieval, Reference |
| FULL `CONTENT.md`, audit freeze-ready | Audited / frozen içerikteki mevcut L0–L4; Critical Distinctions / What It Is Not; Retrieval Check; R — Reference |
| Human Sync, event, Experience Note | Hiçbir general theory. Yalnız appearance ve experience. |

- Persistence içerik üretmez. Yalnız artifact'teki bilgiyi taşır ve düzenler.
- Olmayan depth uydurulmaz. Section gövdesi `N/A` olur.
- Project-specific cümle (bu projede, bu dosyada, bu sayı) Home'a girmez. Experience Note'a gider.
- Artifact içindeki `Example`, `Project`, `Transition to Next Block`, `Oral Version` bölümleri Home'a taşınmaz.

Section eşlemesi:

| Home section | LIGHT kaynak | FULL kaynak |
|---|---|---|
| L0 — Map / Context | L0 — Local Map | Local Map |
| L1 — Simple Explanation | L1 — Simple Explanation | L1 — Simple Explanation |
| L2 — Mechanism | L2 — Mechanism | L2 — Mechanism |
| L3 — Theory | L3 — Theory (doluysa) | L3 — Theory |
| L4 — Math / Formalism | - | L4 — Math / Formalism |
| Confusion Boundaries | Boundary / Confusion Check | L3 → Critical Distinctions + What It Is Not |
| Retrieval | Retrieval | Retrieval Check |
| Reference | Reference | R — Reference Links |

`System Position`: concept'in genel bilgi alanındaki yeri. Tek satır (ör. `Async Processing → Queue`). Graph `parent_id` zincirinden önerilir; project-specific component adı yazılmaz.

### 8.2 Provenance

Her dolu content section ilk satırda provenance taşır:

```text
Provenance: <LABEL> (<source>)
```

| Label | Anlam |
|---|---|
| `ULA-DERIVED` | `COMPLETE` ULA artifact'ten taşındı. |
| `PROJECT-DERIVED` | Project gözleminden çıkan genel bilgi. ULA artifact içinde doğrulanmış olmalı. |
| `GENERAL THEORY` | Artifact içinde dış bilgi olarak etiketlenmiş bilgi. |
| `USER-CONFIRMED` | Kullanıcı conflict veya ekleme kararı ile onayladı. |

- `<source>` = `PRJ-xxxxxxxx:passes/<pass-id>/ula/<event-id>/<file>` veya `user:YYYY-MM-DD`.
- Yeni dış bilgi Home'a sessizce eklenmez. Artifact'te yoksa yalnız kullanıcı onayı ile ve `USER-CONFIRMED` etiketi ile eklenir.

---

## 9. Update = delta

Mevcut Home baştan yazılmaz.

```text
READ HOME → COMPARE NEW LEARNING (section bazında) → OUTCOME
```

| outcome | condition | home_change | version |
|---|---|---|---|
| APPEARANCE_ONLY | Yeni general knowledge yok | Yalnız Project Appearances | SAME |
| ENRICH | Eksik section dolar veya mevcut section çelişmeyen ek bilgi alır | Section eklenir / genişler; Source Artifacts; Change History | +1 |
| CONFLICT | Yeni bilgi mevcut section ile çelişir | Yok. Event `BLOCKED`. §10. | SAME |

Version kuralı (tek ve deterministic):

- Versioned alanlar: content section'ları (System Position, L0–L4, Confusion Boundaries, Retrieval, Reference), Identity içinde `Canonical Name`, `Aliases`, `Short Meaning`, `Status`, ve Source Artifacts.
- Versioned alan değişirse `Version` +1 ve bir Change History satırı.
- Yalnız Project Appearances, `Home Mode`, `Updated At` veya Change History değişirse `Version` aynı kalır.
- Yeni Home `Version: 1` ile başlar.

Equivalence ve conflict kararı judgment'tır. Belirsizse `CONFLICT` kabul et ve kullanıcıya sor.

---

## 10. Conflict handling

Sessiz overwrite yok. Event `BLOCKED`. Kullanıcıya kısa gösterim:

```text
Concept: <CH-id> <Canonical Name> — <section>

Existing:
<mevcut ifade>

New:
<yeni ifade>

Evidence:
<artifact path / ref>

1. Existing'i koru.
2. New bilgiyi kabul et.
3. İki durumu boundary olarak sakla.
4. Şimdilik block et.
```

| Seçim | Sonuç | Version |
|---|---|---|
| 1 | APPEARANCE_ONLY | SAME |
| 2 | Section güncellenir. Eski ifade Change History'ye yazılır. Provenance `USER-CONFIRMED`. | +1 |
| 3 | İki ifade koşulları ile `Confusion Boundaries` içine yazılır. Provenance `USER-CONFIRMED`. | +1 |
| 4 | Event `BLOCKED` kalır. Write yok. | SAME |

---

## 11. Project Appearance

Concept Home `## Project Appearances` tablosu:

| Alan | Değer |
|---|---|
| `project_id` | `PRJ-...` |
| `project_name` | Yazım anındaki ad |
| `event_id` | `LE-...` |
| `learning_pass_id` | `LP-...` |
| `experience_id` | `EX-...` veya `-` |
| `date` | `YYYY-MM-DD` |

- Dedupe anahtarı: (`project_id`, `event_id`). Aynı appearance ikinci kez eklenmez.
- Appearance general theory taşımaz.

---

## 12. Project concept pointer

Template: `templates/CONCEPT_POINTER_TEMPLATE.md`. Konum: `docs/learning/concepts/<concept-id>.md`.

| Alan | Değer |
|---|---|
| `Concept ID` | `CH-...` |
| `Canonical Name` | Registry'deki ad (label; registry kazanır) |
| `Home Mode` | `PERSONAL` |
| `Home Ref` | `personal:CH-...` |
| `Project Node IDs` | Graph `node_id` listesi |
| `Project Appearances` | Bu project'teki `event_id` listesi |
| `Local Delta` | Bu project'e özgü kısa davranış farkı veya `-`. Teori değildir. |

- Pointer full theory kopyalamaz. L0–L4 section'ı taşımaz.
- Absolute personal path yazılmaz.

---

## 13. LOCAL_TEMPORARY mode ve promotion

### 13.1 Home mode

| Mode | Full Home konumu | Project dosyası |
|---|---|---|
| `PERSONAL` | `<personal_library_path>/concepts/<concept-id>.md` | Pointer |
| `LOCAL_TEMPORARY` | `docs/learning/concepts/<concept-id>.md` | Full temporary Home |

`LOCAL_TEMPORARY` kuralları:

- Identity içinde `Home Mode: LOCAL_TEMPORARY` zorunlu.
- Pointer alanları Home içindeki `## Local Pointer` bölümünde tutulur.
- `concept_id` normal `CH-` formatındadır. Promotion sırasında değişmez.
- Personal library'ye write yok. Experience Map satırları `Map Status: DEFERRED` olarak Experience Note'ta bekler.

### 13.2 Promotion

Tetik: `personal_library_path` yapılandırıldı ve project'te `LOCAL_TEMPORARY` Home var. Persistence adımı veya `/stay-in-the-loop library` promotion önerir. Kullanıcı onayı gerekir.

```text
1. Registry'de resolution (§7) — aynı concept başka ID ile var mı?
   evet → BLOCKED, kullanıcı: merge (§14.2) veya ayrı concept
2. Global Home candidate = local Home içeriği, Home Mode: PERSONAL, aynı concept_id
3. Registry candidate satırı
4. Project dosyası candidate = pointer (Home Ref: personal:<aynı concept_id>)
5. DEFERRED Experience Map satırları
6. INTEGRITY 07 §P
7. WRITE (§22) — all-or-nothing
```

Sonuç: aynı `concept_id`, global Home var, project dosyası pointer, theory tek yerde.

Promotion versioned alan değiştirmez. `Version` aynı kalır. Change History'ye `PROMOTED` satırı yazılır.

---

## 14. Rename ve merge

### 14.1 Rename

- `concept_id` değişmez.
- Eski canonical name → `Aliases`. Registry ve Home aynı transaction ile yazılır.
- Home `Version` +1 (Identity değişti).
- Pointer'lar ID ile çözülür. Pointer `Canonical Name` label'ı sonraki persistence'ta yenilenir (`07` P-24 WARNING).
- Graph `canonical_name` project-local'dır. Otomatik değişmez.

### 14.2 Merge

Yalnız kullanıcı onayı ile. Biri canonical kalır. Diğer registry satırı `Status: MERGED`, `Home: merged:<canonical-id>` olur. Diğer Home dosyası silinmez; Identity `Status: MERGED`. ID yeniden kullanılmaz. Resolution `MERGED` satırında hedefe gider.

---

## 15. Experience Note

Template: `templates/EXPERIENCE_NOTE_TEMPLATE.md`. Konum: `docs/learning/experiences/<experience-id>.md`.

Experience Note concept'in bu projede nasıl ve neden kullanıldığını saklar. General theory tekrar etmez.

| Alan | Kaynak |
|---|---|
| `experience_id`, `event_id`, `concept_id`, `project_id`, `project_name`, `work_unit_ids` | Identity |
| `problem`, `constraint`, `why_it_appeared`, `alternatives`, `selected`, `why_selected`, `trade_off`, `failure_mode`, `observed_result`, `reusable_signal` | Event `decision_or_mechanism` (03 §10.2 / §10.3), Human Sync |
| `concept_home_ref` | `personal:CH-...`, `local-temporary:CH-...` veya `-` |
| `evidence` | Claim bazında evidence status + ref (§15.2) |

- `concept_id: UNASSIGNED` geçerlidir. Saf decision / failure experience için Home zorunlu değildir.
- Evidence bir alanı desteklemiyorsa alan `UNRESOLVED` yazılır. Uydurulmaz.
- L0–L4 başlığı veya Concept Home section metni note içine kopyalanmaz (`07` P-11).

### 15.1 Experience identity

- Bir event → en fazla bir Experience Note.
- Eşleme pass `## Knowledge Persistence` tablosunda tutulur: `event_id → experience_id`. Bu tablo deterministic lookup'tır.
- Event için tabloda `experience_id` varsa yeni note açılmaz. Mevcut note yalnız eksik alanlar için güncellenir.
- Tabloda yoksa `experiences/*.md` içinde aynı `Event ID` aranır. Bulunursa o ID kullanılır.

### 15.2 Evidence

Human Sync evidence modeli korunur (`03` §7): `VERIFIED` · `INFERRED` · `ASSUMED` · `UNRESOLVED`.

- Önemli project claim için `## Evidence` tablosu satırı yazılır.
- `VERIFIED` evidence ref zorunlu.
- Note claim status'u kaynak event'in evidence status'undan güçlü olamaz. `UNRESOLVED` project fact `VERIFIED` experience olarak yazılmaz.

---

## 16. Decision Record

Template: `templates/DECISION_RECORD_TEMPLATE.md`. Konum: `docs/learning/experiences/<decision-id>.md`.

| Type | Ne zaman |
|---|---|
| `ADR` | Primary category `SYSTEM_DESIGN` |
| `DSA_DR` | Primary category `DSA` |

Significant decision kuralı. Hepsi gerekir:

1. Experience Note yazılıyor.
2. Category `SYSTEM_DESIGN` veya `DSA`.
3. Project içinde en az iki alternatif değerlendirildi (yalnız `GENERAL THEORY` alternatif yetmez).
4. Selected decision evidence `VERIFIED` veya `INFERRED`.
5. `knowledge_priority: MUST_UNDERSTAND` veya kullanıcı istedi.

Her event için Decision Record üretilmez. Experience Note `Decision Record` alanı `DR-...` veya `-` taşır.

---

## 17. Experience Maps

Experience Map cross-project experience index'tir. General theory taşımaz. Satır kısa ifadelerden oluşur.

### 17.1 System Design Experience Map

Konum: `<personal_library_path>/experience-maps/SYSTEM_DESIGN_EXPERIENCE_MAP.md`.

Satır şartı: Experience Note var + primary category `SYSTEM_DESIGN` + reusable signal var.

Kolonlar: template. `Experience Note` = `PRJ-.../EX-...`. `Concept Home` = `CH-...` veya `-`. `Depth Reached` = Home `L` seviyeleri veya `-`.

### 17.2 DSA Experience Map

Konum: `<personal_library_path>/experience-maps/DSA_EXPERIENCE_MAP.md`.

Satır şartı: Experience Note var + primary category `DSA` + reusable signal var. DSA event yoksa satır üretilmez.

`Pattern` §17.3 vocabulary'sinden gelir.

### 17.3 Universal DSA pattern vocabulary

Bu tablo UNIVERSAL SKILL LOGIC'tir (master §8). Problem tanıma sözlüğüdür. Personal DSA Experience Map yalnız kullanıcının gerçekten karşılaştığı satırları biriktirir. İki liste karışmaz.

| Pattern | Tipik yapı |
|---|---|
| `Fast Lookup` | Hash Map / Set |
| `FIFO Processing` | Queue |
| `Priority Processing` | Heap / Priority Queue |
| `Top-K` | Heap |
| `Recent-N Observations` | Sliding Window / Deque |
| `Relationships` | Graph |
| `Dependencies` | DAG |
| `Shortest Path` | Graph Algorithms |
| `Repeated Subproblems` | Dynamic Programming |
| `Local Optimization` | Greedy |
| `Sorted Lookup` | Binary Search / Tree |
| `Similarity Search` | Nearest Neighbor / ANN |
| `Streaming Events` | Queue + Window + Online Algorithm |
| `Data Distribution` | Hashing / Partitioning |
| `Ranking` | Sorting / Heap |
| `OTHER` | Listede yok. Kısa ad parantez içinde. |

### 17.4 Map row kuralları

- Dedupe anahtarı: `Experience Note` (`PRJ-.../EX-...`). Aynı note ikinci satır almaz.
- Library `UNCONFIGURED` veya `LOCAL_TEMPORARY` → satır yazılmaz. Note `Map Status: DEFERRED`. Promotion sırasında yazılır.
- Map row yazıldı → note `Map Status: WRITTEN`. Satır şartı yok → `NOT_APPLICABLE`.

---

## 18. Concept Registry ve Library Index

### 18.1 Concept Registry

Template: `templates/CONCEPT_REGISTRY_TEMPLATE.md`. Identity resolution için canonical registry.

| Kolon | Değer |
|---|---|
| `Concept ID` | `CH-...` |
| `Canonical Name` | Home Identity ile aynı |
| `Aliases` | `; ` listesi veya `-` |
| `Short Meaning` | Tek cümle. Resolution meaning karşılaştırması için. Teori değildir. |
| `Home` | `concepts/<concept-id>.md` veya `merged:<concept-id>` |
| `Status` | `ACTIVE` · `MERGED` |

- Registry teori taşımaz.
- Registry ve Home Identity (`Canonical Name`, `Aliases`, `Status`) aynı olmalıdır. Çelişki → `07` P-23 FAIL.

### 18.2 Library Index

Template: `templates/PERSONAL_LIBRARY_INDEX_TEMPLATE.md`. **GENERATED VIEW.**

- Concept Home dosyalarından yeniden üretilir: `Concept ID`, `Canonical Name`, `Status`, `Depth`, `Project Count`, `Last Updated`.
- `Project Count` = Home'daki farklı `project_id` sayısı.
- Duplicate theory taşımaz. Index ile Home çelişirse Home kazanır, index yeniden üretilir (`07` P-24 WARNING).

---

## 19. Persistence status

Pass `## Map Sync` tablosundaki `Experience Persistence` kolonu. Event bazında.

| Status | Anlam |
|---|---|
| `PENDING` | Persistence gerekli. Henüz yapılmadı veya ertelendi. |
| `COMPLETE` | Gerekli Concept / Experience persistence başarılı. |
| `NOT_APPLICABLE` | Persistence gerekmiyor (§5). |
| `BLOCKED` | Identity, config, conflict veya integrity problemi. |

Geçişler:

| from | to | ne zaman |
|---|---|---|
| PENDING | COMPLETE | Write başarılı |
| PENDING | BLOCKED | AMBIGUOUS, CONFLICT, config onayı yok, §P FAIL, write hatası |
| PENDING | NOT_APPLICABLE | Routing (§5) persistence gerektirmiyor |
| BLOCKED | PENDING | Kullanıcı kararı veya config düzeldi; tekrar dene |
| BLOCKED | COMPLETE | Tekrar deneme başarılı |

- `COMPLETE` event tekrar işlenirse no-op (idempotent).
- Pass `## Knowledge Persistence` tablosu ID'leri tutar: `Concept ID`, `Experience ID`, `Decision Record`.

### 19.1 Coverage independence

Persistence post-completion enrichment'tır.

```text
PASS COMPLETE + PERSISTENCE BLOCKED  → geçerli
```

- Pass `COMPLETE` kalır. `current_stage` değişmez.
- Ledger `COVERED` kalır. Learning yeniden açılmaz.

---

## 20. Knowledge Debt lifecycle

Kayıt: `docs/learning/state/LEARNING_QUEUE.md` §B (authoritative). `03` §14 yalnız `OPEN` oluşturur.

| from | to | guard |
|---|---|---|
| OPEN | RESOLVED | resolution event ULA COMPLETE + event persistence COMPLETE + concept_home CH assigned + DEBT node ACTIVE |
| OPEN | DISMISSED | explicit user decision |
| DISMISSED | OPEN | explicit user decision |

Diğer geçişler geçersizdir. `RESOLVED` terminaldir.

### 20.1 RESOLVED

Bütün şartlar aynı transaction içinde doğrulanır:

1. `resolution_ref` = bir `ULA_CANDIDATE` event; `ula_status: COMPLETE`; pass `COMPLETE`.
2. Bu event'in persistence status'u `COMPLETE`.
3. Debt `concept_home` = çözülebilir `CH-...`.
4. Graph'ta `debt_id` taşıyan node varsa `node_status: ACTIVE` ve `home_ref` = aynı `CH-...`.

Concept Home dosyasının var olması tek başına yeterli değildir.

Debt ↔ event bağı:

- Öncelik: graph node `debt_id` (map sync DEBT → ACTIVE promotion, `05` §7.4).
- Graph bağı yoksa: debt `concept` + meaning eşleşmesi → kullanıcı onayı. Sessiz eşleştirme yok.

### 20.2 DISMISSED

Yalnız kullanıcının açık kararı. `resolution_ref: user:YYYY-MM-DD`.

### 20.3 DEBT → ACTIVE

- Map sync (`05` §7.4) aynı `node_id` ile `DEBT → ACTIVE` yapar.
- Persistence `home_ref` atar.
- Node `debt_id` historical reference olarak korunur.

---

## 21. Graph integration

Concept Home ataması başarılı olunca:

```text
Semantic Graph node.home_ref:  UNASSIGNED → CH-xxxxxxxx
```

- Hedef: event'in `source_event_ids` içinde olduğu ve aynı concept'i temsil eden node. Birden fazla aday varsa kullanıcıya sor.
- `node_id`, `canonical_name`, edge'ler ve semantic identity değişmez.
- Update `05` §8–§9 kurallarına uyar: aday graph, `07` §M, write, `graph_version` +1, view regeneration.
- Node zaten aynı `CH-...` taşıyorsa no-op. Farklı `CH-...` taşıyorsa → `BLOCKED`, kullanıcı.
- `DEBT` node `home_ref` almaz.

---

## 22. Atomic write

Event başına transaction.

| rule | value |
|---|---|
| write_mode | ALL_OR_NOTHING |
| integrity | BEFORE_ANY_WRITE |
| on_write_error | RESTORE_PRE_IMAGES |

Sıra:

```text
LOCK        personal write varsa ACQUIRE (§22.1); alınamazsa BLOCKED
↓
READ        bütün hedef dosyaların pre-image'ı
↓
BUILD       bütün candidate'ler bellekte
↓
INTEGRITY   07 §P (+ §M) bütün candidate set üzerinde
↓
WRITE       1. Concept Home  2. Concept Registry  3. Experience Map row
            4. project pointer / temporary Home  5. Experience Note  6. Decision Record
            7. SEMANTIC_GRAPH home_ref  8. queue §B debt  9. pass tablosu
↓
INDEX       LIBRARY_INDEX ve graph değiştiyse HORIZONTAL_MAP yeniden üretilir (derived; hata → WARNING)
↓
VERIFY      07 §P yazılmış dosyalar üzerinde
↓
RELEASE     lock varsa sil (§22.1)
```

- Integrity FAIL → hiçbir dosya yazılmaz. Event `BLOCKED`.
- Write hatası → bu transaction'da yazılan dosyalar pre-image ile geri yüklenir. Event `BLOCKED`.
- Concept Home yazılıp registry yazılmadan kalmaz.
- Persistence `BLOCKED` coverage'ı değiştirmez (§19.1).

### 22.1 Personal library write lock

Amaç: İki project session aynı personal library'ye aynı anda yazarsa sessiz data corruption olmaz.

Transaction en az bir `L:` (personal) dosya yazacaksa lock gerekir. Yalnız project dosyası yazan transaction lock almaz.

| rule | value |
|---|---|
| lock_path | `<personal_library_path>/.learning-write-lock/` |
| lock_file | `LOCK.md` |
| acquire | EXCLUSIVE_CREATE |
| on_existing | BLOCKED |
| stale_lock | USER_DECISION |
| release | AFTER_VERIFY_OR_ROLLBACK |
| on_release_error | WARNING |

`LOCK.md` alanları:

```text
lock_id:          LK-xxxxxxxx
project_id:       PRJ-xxxxxxxx
learning_pass_id: LP-YYYYMMDD-NN
created_at:       YYYY-MM-DDTHH:MM
operation:        PERSIST <event-id> | PROMOTE | RENAME <concept-id>
```

Akış:

```text
ACQUIRE   lock dizinini exclusive create ile oluştur (dizin varsa create başarısız olur)
          → LOCK.md yaz
↓
READ → BUILD → INTEGRITY → WRITE → VERIFY    (§22)
↓
RELEASE   LOCK.md ve lock dizinini sil (rollback sonrası da)
```

Kurallar:

- Dizin zaten varsa overwrite yapma. Lock alınmadı.
- Lock alınamadı → persistence dosyası yazılmaz (personal ve project). Yalnız pass `Experience Persistence: BLOCKED` yazılır. Pass `COMPLETE` ve ledger değişmez (§19.1). Kısa lock bilgisini göster.
- Lock yaşlı görünse bile otomatik silme. Kullanıcıya sor:

```text
Lock bulundu.
Owner project: <project_id>
Pass:          <learning_pass_id>
Created:       <created_at>
Operation:     <operation>

1. Lock'u koru.
2. Stale olduğunu onayla ve temizle.
```

| Seçim | Sonuç |
|---|---|
| 1 | Lock kalır. Event `BLOCKED`. Kullanıcı sonra tekrar dener. |
| 2 | Kullanıcı onayı ile lock silinir. Sonra normal ACQUIRE. |
| cevap yok | Seçim 1 |

- Release başarısız → WARNING (07 L-21). Data write başarılı olabilir. Lock cleanup kullanıcı kararı ile yapılır.
- Lock yalnız tek bir personal library transaction'ı korur. Distributed lock veya remote library desteği yoktur.

---

## 23. Identity link

```text
WORK UNIT        work_unit_id
↓
LEARNING EVENT   event_id            (pass)
↓
ULA ARTIFACT     passes/<pass>/ula/<event-id>/
↓
GRAPH NODE       node_id → home_ref: CH-...
↓
CONCEPT HOME     concept_id → Project Appearances (event_id, experience_id)
↓
EXPERIENCE NOTE  experience_id → event_id, concept_id, work_unit_ids
↓
EXPERIENCE MAP   PRJ-.../EX-...
```

Her katman yalnız ID / pointer taşır. Full content tek yerdedir.

---

## 24. Commands

Tek entry point: `/stay-in-the-loop`. Ayrı skill yok. Bu komutlar coverage, Human Sync veya ULA çalıştırmaz. Read-only'dir; promotion yalnız kullanıcı onayı ile write yapar.

| Komut | Davranış |
|---|---|
| `/stay-in-the-loop concept <concept-id>` | Project pointer'ı ve Home'u gösterir. `LOCAL_TEMPORARY` ise local Home. Yalnız bu Home yüklenir. |
| `/stay-in-the-loop library` | Config durumu, Library Index özeti, `LOCAL_TEMPORARY` concept sayısı. Varsa promotion önerir (§13.2). |
| `/stay-in-the-loop experiences` | Project Experience Note listesi: ID, concept, category, map status. Personal map istenirse yalnız ilgili map. |
| `/stay-in-the-loop debt` | Queue §B içindeki `OPEN` debt: debt_id, concept, priority, originating event. |

---

## 25. Token / context rules

| Durum | Yükle | Yükleme |
|---|---|---|
| Normal project work | Hiçbiri | Personal library |
| Persistence | Bu dosya + pass + registry + yalnız candidate Home + yalnız ilgili Experience Map + gerekli template | Diğer Home'lar, Library Index, diğer map |
| `/stay-in-the-loop concept <id>` | Bu dosya §24 + pointer + o Home | Registry dışındaki Home'lar |
| `/stay-in-the-loop library` | Config + `LIBRARY_INDEX.md` | Home'lar |
| `/stay-in-the-loop experiences` | Project `experiences/` Identity blokları | Personal library |
| `/stay-in-the-loop debt` | Queue §B | Graph, personal library |

`00_MASTER_SYSTEM_SPEC.md`, `ula/` rol dosyaları ve example / historical material yüklenmez. ULA artifact yalnız Home candidate kurulurken ve yalnız ilgili section'lar okunur.

---

## 26. Scope boundary

- Project Semantic Graph `05`'te kalır. Global cross-project graph yoktur.
- Cross-project reuse yalnız Concept Registry, Concept Home ve Experience Maps ile yapılır.
- HTML Atlas yoktur.

---

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §5, §8, §9, §32, §33, §38, §39, §45.
- `ula/ULA_SPECIFICATION.md` §17, §18.
- Phase 1 audit: Bölüm 10, 11, Q2, Q12.
- `03_HUMAN_SYNC_PROTOCOL.md` §7, §9, §10, §14. `05_MINDMAP_PROTOCOL.md` §3, §7.4, §8–§10.
