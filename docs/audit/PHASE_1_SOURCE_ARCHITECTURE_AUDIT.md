# PHASE 1 — SOURCE & ARCHITECTURE AUDIT

**Proje:** Taşınabilir Claude Code `/learning` skill
**Aşama:** 1 — Source & Architecture Audit
**Tarih:** 2026-10-27
**Kapsam:** READ → ANALYZE → CLASSIFY → MAP → REPORT
**Kaynak durumu:** Read-only. Hiçbir kaynak dosya değiştirilmedi.

```text
PHASE 1 STATUS: FROZEN / PASS
PHASE 2 STATUS: READY
```

**Freeze notu:** Q1–Q12 kararları kullanıcı tarafından verildi ve Bölüm 21'de `RESOLVED` olarak kaydedildi. Bölüm 19 onaylanmış hedef mimaridir. Önceki bölümlerdeki "öneri" ifadeleri, Bölüm 21 kararları ile çelişirse Bölüm 21 geçerlidir.

---

## Durum etiketleri

Bu raporda şu etiketler kullanılır.

| Bağlam | Etiketler |
|---|---|
| Master inventory | `FOUND` · `PARTIAL` · `MISSING` |
| MindMap gap | `ALREADY PRESENT` · `PARTIAL` · `MISSING` |
| Coverage, Token, Light/Full | `PRESENT` · `PARTIAL` · `ABSENT` / `MISSING` |
| Classification | `KEEP` · `MOVE` · `MERGE` · `REWRITE` · `REMOVE` · `MISSING` |

Kaynak atıfları şu kısaltmaları kullanır.

| Kısaltma | Dosya |
|---|---|
| `MASTER §n` | `StudySystem_WithAI.txt`, bölüm n |
| `SPEC §n` | `Universal_Learning_Architecture/ULA_SPECIFICATION_v1.0.md`, bölüm n |
| `ARCH §n` | `Universal_Learning_Architecture/prompts/01_LEARNING_ARCHITECT.md` |
| `BUILD §n` | `Universal_Learning_Architecture/prompts/02_CONTENT_BUILDER.md` |
| `AUDIT §n` | `Universal_Learning_Architecture/prompts/03_LEARNING_AUDITOR.md` |
| `ULA README` | `Universal_Learning_Architecture/README.md` |

---

# 1. Executive Summary

Repository iki kaynak sistem içerir.

1. **Project-Driven Learning System** — `StudySystem_WithAI.txt` (2750 satır, Türkçe).
2. **Universal Learning Architecture (ULA) v1.0** — `Universal_Learning_Architecture/` (14 dosya, çoğu İngilizce).

İki sistemin rolü farklıdır.

- Master sistem **ne zaman** ve **neyin** öğrenileceğini belirler.
- ULA seçilmiş konunun **hangi sırayla** ve **hangi derinlikte** öğretileceğini belirler.

Ana bulgular:

1. Master sistemin 52 bileşeninin 50'si `FOUND`, 2'si `PARTIAL` durumundadır. `MISSING` bileşen yoktur.
2. ULA üç rolü (Architect, Builder, Auditor) eksiksiz tanımlar. Rol sınırları açıktır.
3. NotebookLM-benzeri MindMap **kavram düzeyinde** büyük ölçüde mevcuttur. **Operasyonel düzeyde** (graph schema, ID sistemi, terminal rendering, incremental update) eksiktir.
4. Master sistem learning lifecycle'ı **otomatik** tasarlar. Yeni skill bunu **manuel** `/learning` çağrısına taşımalıdır. Logical flow korunur. Invocation timing değişir.
5. **Learning Coverage Management kaynaklarda `ABSENT` durumundadır.** Bu, Aşama 2 için en büyük yeni bileşendir.
6. Concept Home, kaynakta **projeler arası kişisel kütüphane** olarak tanımlanır (`MASTER §32`: "Personal Technical Library"). Önerilen hedef mimari Concept Home'u **proje içine** koyar. Bu bir mimari çakışmadır.
7. Önerilen `state/` klasörü skill klasörünün içindedir. Bu, portability ilkesini bozar. State proje tarafına taşınmalıdır.
8. Light ULA / Full ULA ayrımı `PARTIAL` durumundadır. **Depth** ayrımı vardır (Zoom 1/2/3, Quick/Standard/Deep). **Process** ayrımı (tek geçiş vs üç rol) yoktur.
9. Kaynaklarda dört kalite sorunu vardır: bozuk LaTeX escape karakterleri, chat artığı metin ve terminoloji kayması. Bunlar düzeltilmedi. Yalnız raporlandı.

**Phase 1 sonucu:** FROZEN / PASS.
**Phase 2 hazırlığı:** READY. Bölüm 21'deki bütün sorular (Q1–Q12) `RESOLVED` durumundadır.

---

# 2. Sources Found

## 2.1 Bulunan kaynaklar

| # | Dosya | Boyut | Rol | Dil |
|---|---|---|---|---|
| 1 | `StudySystem_WithAI.txt` | 44.6 KB / 2750 satır | **Master system spec** | TR |
| 2 | `ULA/ULA_SPECIFICATION_v1.0.md` | 25.9 KB / 1495 satır | **ULA authoritative spec** (`ULA README` böyle tanımlar) | TR |
| 3 | `ULA/README.md` | 4.1 KB | ULA özeti ve standard workflow | EN |
| 4 | `ULA/CHANGELOG.md` | 2.6 KB | Sürüm geçmişi, Planned listesi | EN |
| 5 | `ULA/prompts/01_LEARNING_ARCHITECT.md` | 13.8 KB | Learning Architect rolü | EN |
| 6 | `ULA/prompts/02_CONTENT_BUILDER.md` | 21.8 KB | Content Builder rolü | EN |
| 7 | `ULA/prompts/03_LEARNING_AUDITOR.md` | 20.9 KB | Learning Auditor rolü | EN |
| 8 | `ULA/templates/PROJECT_BRIEF_TEMPLATE.md` | 6.2 KB | Architect input şablonu | EN |
| 9 | `ULA/templates/ARCHITECTURE_OUTPUT_TEMPLATE.md` | 4.0 KB | Architect output şablonu | EN |
| 10 | `ULA/templates/CONTENT_BUILD_TEMPLATE.md` | 2.7 KB | Builder output şablonu | EN |
| 11 | `ULA/templates/AUDIT_REPORT_TEMPLATE.md` | 3.8 KB | Auditor output şablonu | EN |
| 12 | `ULA/examples/HSMM_PILOT/README.md` | 1.7 KB | Pilot kapsam notu | EN |
| 13 | `ULA/examples/HSMM_PILOT/01_ARCHITECTURE_EXAMPLE.md` | 12.1 KB | Architect örnek çıktısı | EN |
| 14 | `ULA/examples/HSMM_PILOT/02_CONTENT_EXAMPLE.md` | 8.2 KB | Builder örnek çıktısı | EN |
| 15 | `ULA/examples/HSMM_PILOT/03_AUDIT_EXAMPLE.md` | 5.9 KB | Auditor örnek çıktısı | EN |

Toplam: 15 dosya, yaklaşık 178 KB. Kaba token tahmini: 45k–55k token.

## 2.2 Bulunamayan kaynaklar

| Aranan | Durum |
|---|---|
| `StudySystem_WithAI*.txt` varyantları (tek dosya dışında) | `SOURCE NOT FOUND` |
| Mevcut learning skill dosyaları | `SOURCE NOT FOUND` |
| Mevcut `SKILL.md` | `SOURCE NOT FOUND` |
| `.claude/` klasörü | `SOURCE NOT FOUND` |
| Ayrı learning protocol dosyası | `SOURCE NOT FOUND` (protocol master içinde gömülüdür) |
| Learning queue / state dosyaları | `SOURCE NOT FOUND` |
| ZIP dosyası | `SOURCE NOT FOUND` (ULA klasörü zaten açılmış halde) |
| Ayrı tasarım notu | `SOURCE NOT FOUND` |

Ek gözlem: Repository bir git repository değildir. Bu durum Bölüm 8 için önemlidir.

## 2.3 Kaynak kalite sorunları (düzeltilmedi)

| ID | Dosya | Konum | Sorun | Kanıt |
|---|---|---|---|---|
| SQ-01 | `examples/HSMM_PILOT/02_CONTENT_EXAMPLE.md` | satır 233, 234, 365, 367, 371, 457 | LaTeX escape'leri control character'a dönüşmüş. `\right` → `CR + "ight"`, `\vartheta` → `VT + "artheta"`, `\arg` → `BEL + "rg"`, `\Vert` → `CR + "Vert"`. | `grep -P '[\x07\x0b\x0d]'` eşleşmesi |
| SQ-02 | `CHANGELOG.md` | satır 1–8 | Gerçek changelog, chat artığı metin ile sarılmış: `` # `CHANGELOG.md` ``, "Başlangıçta çok basit tutalım.", `` ```markdown `` | Dosya başı |
| SQ-03 | `ULA_SPECIFICATION_v1.0.md` | satır 1495 | Spec sonunda konuşma artığı paragraf: "Bence ULA v1.0'ın çekirdeği artık yeterince net…" | Son satır |
| SQ-04 | `StudySystem_WithAI.txt` | satır 133 | Yazım hatası: "ihtiyeti" | Satır 133 |
| SQ-05 | `03_LEARNING_AUDITOR.md` | §3 | Audit boyutu "R. Visual / Structural Density" harfi, "R — Reference" katman adıyla çakışır | §3 listesi |

Bu sorunlar ULA mantığını değiştirmez. Aşama 2'de kopyalama sırasında nasıl ele alınacağı bir karar sorusudur (Bölüm 21, Q9).

---

# 3. Master System Inventory

Kaynak: `StudySystem_WithAI.txt`.

| # | Bileşen | Durum | Kaynak | Not |
|---|---|---|---|---|
| 1 | Ana amaç | FOUND | §1 | "AI'ın üretim hızından yararlanırken teknik anlayışı kaybetmemek." |
| 2 | System architecture | FOUND | §2 | Altı katmanlı akış diyagramı |
| 3 | Project-driven learning philosophy | FOUND | §3 | "Önce ihtiyaç ortaya çıkar. Sonra teori…" |
| 4 | System Design as primary learning axis | FOUND | §3A | "Project problemi üretir. System Design ana öğrenmeyi üretir." |
| 5 | Problem-first System Design | FOUND | §4 | Problem → system concept eşleşme listesi |
| 6 | System Design Experience Map | FOUND | §5 | 15 alanlı kayıt formatı + örnek |
| 7 | Problem-Pattern DSA | FOUND | §6, §7 | 10 adımlı DSA zinciri |
| 8 | DSA Pattern Map | FOUND | §8 | 15 pattern; "problem tanıma sözlüğü" |
| 9 | DSA Experience Map | FOUND | §9 | Kayıt formatı + Top-K örneği |
| 10 | System Design × DSA ilişkisi | FOUND | §10 | DSA → sistem component eşleşmesi |
| 11 | Data Science × System Design × DSA | FOUND | §11 | Event → ranking pipeline örneği |
| 12 | Project selection | FOUND | §12 | Üç gelişim alanı |
| 13 | Project difficulty progression | FOUND | §13 | "2–4 yeni büyük concept" kuralı |
| 14 | AI roles | FOUND | §14 | Altı rol; Teacher ≠ Compressor |
| 15 | Cognitive Throughput Gap | FOUND | §15 | Tanım ve ikinci amaç |
| 16 | Human Synchronization | FOUND | §16 | IMPLEMENT → … → HS → KP → DONE/LEARNING PASS |
| 17 | Human Synchronization output | FOUND | §17 | 7 bölümlü çıktı + epistemik durum (VERIFIED/INFERRED/ASSUMED/UNRESOLVED) |
| 18 | Knowledge Priority | FOUND | §18 | MUST UNDERSTAND / USEFUL TO KNOW / IMPLEMENTATION DETAIL |
| 19 | Knowledge Debt | PARTIAL | §19, §45.5 | Kayıt formatı var. Kapanma kuralı, saklama yeri ve durum geçişi yok. |
| 20 | ULA role | FOUND | §20 | "LEARNING CONTENT PROTOCOL" |
| 21 | Horizontal Knowledge Map | FOUND | §21 | X/Y geometri, örnekler |
| 22 | Recursive zoom | FOUND | §22 | WORLD → REGION → CURRENT NODE → CURRENT DEPTH |
| 23 | Progressive expansion | FOUND | §23 | "Harita genişler. İçerik dökülmez." |
| 24 | Node design | FOUND | §24 | Canonical name + short meaning + rol |
| 25 | Edge semantics | FOUND | §25 | 12 relation type; dekoratif connector yasak |
| 26 | Semantic graph layer | FOUND | §26 | 13 node alanı, 4 edge alanı, üretim sırası |
| 27 | L1 — Simple Meaning | FOUND | §27 | 2–6 cümle |
| 28 | L2 — Mechanism | FOUND | §28 | INPUT → OPERATION → DECISION → OUTPUT → NEXT |
| 29 | L3 — Theory | FOUND | §29 | SD ve DSA için ayrı odak |
| 30 | L4 — Formalism | FOUND | §30 | PURPOSE / SYMBOLS / MAPPING / INTERPRETATION |
| 31 | Confusion Boundaries | FOUND | §31 | `A ≠ B` formatı |
| 32 | One Concept — One Home | FOUND | §32 | Project Appearances + delta kuralı |
| 33 | Concept Home vs Project Experience | FOUND | §33 | İki ayrı doküman türü |
| 34 | Reference Layer | FOUND | §34 | ANLAMAK ≠ BAKMAK |
| 35 | Zoom / Depth Control | FOUND | §35 | Zoom 1 / 2 / 3 |
| 36 | Learning Event | FOUND | §36 | EXPERIENCE ONLY vs KNOWLEDGE GAP; ULA tetik kriterleri |
| 37 | Jira / task lifecycle | FOUND | §37 | 12 adımlı kart akışı |
| 38 | Architecture Decision Record | FOUND | §38 | 8 alan |
| 39 | DSA Decision Record | FOUND | §39 | 10 alan; Reusable Signal vurgusu |
| 40 | Retrieval | FOUND | §40 | Genel, DSA ve SD soru setleri |
| 41 | AI dependency control | FOUND | §41 | Karar sonu soru seti |
| 42 | Human Review | FOUND | §42 | Milestone soru seti |
| 43 | Meta-work boundary | FOUND | §43 | "Çalışma sistemini geliştirmek, çalışmanın önüne geçemez." |
| 44 | Project success criteria | FOUND | §44 | SD, DSA, AI, ULA başarı tanımları |
| 45 | Long-term outputs | FOUND | §45 | 7 varlık. Saklama formatı tanımlı değil. |
| 46 | Interactive Knowledge Atlas | PARTIAL | §46 | Vizyon var. Veri modeli ve rendering spec yok. |
| 47 | Default visual experience | FOUND | §47 | 10 adımlı etkileşim |
| 48 | Main production pipeline | FOUND | §48 | Uçtan uca akış |
| 49 | Layer roles | FOUND | §49 | Tek cümlelik roller |
| 50 | Default ULA content rules | FOUND | §50 | AI için varsayılan ULA content prompt |
| 51 | Final target | FOUND | §51 | Practitioner profili |
| 52 | Fundamental principle | FOUND | §52 | Tek cümle + kısa hal |

**Toplam:** 50 FOUND · 2 PARTIAL (#19, #46) · 0 MISSING.

Not: #26 Semantic Graph kavram olarak FOUND'dur. Serialization formatı yoktur. Bu operasyonel boşluk Bölüm 5'te ele alınır.

---

# 4. ULA Inventory

## 4.1 Core teaching sequence

| Adım | Master adı | ULA v1.0 adı | ULA kaynak | Durum |
|---|---|---|---|---|
| Whole / Map | WHOLE / MAP | L0 — MAP | SPEC §6 | PRESENT |
| Simple | L1 — SIMPLE MEANING | L1 — SIMPLE EXPLANATION | SPEC §7 | PRESENT (ad farkı) |
| Mechanism | L2 — MECHANISM | L2 — MECHANISM | SPEC §8 | PRESENT |
| Theory | L3 — THEORY | L3 — THEORY | SPEC §9 | PRESENT |
| Formalism | L4 — FORMALISM / MATH | L4 — MATH / FORMALISM | SPEC §10 | PRESENT (sıra farkı) |
| Confusions | Ayrı adım (§20) | L2/L3 içinde Boundary Statements | SPEC §21, §22 | PRESENT (konum farkı) |
| Retrieval | Ayrı adım (§20) | Retrieval Mode | SPEC §24 | PRESENT (mod olarak) |
| Reference | REFERENCE | R — REFERENCE (`R ∉ L0–L4`) | SPEC §12 | PRESENT |

**Önemli fark:** Master sekiz adımlı lineer sıra verir. ULA v1.0 beş katman (L0–L4) + ayrı R verir. Confusions ULA'da bir katman değildir. L2/L3 içinde yaşar. Retrieval ULA'da bir öğrenme modudur. Bu fark çelişki değildir. Ancak canonical vocabulary kararı gerektirir (Bölüm 16, C-08).

## 4.2 Roles

### Learning Architect (`prompts/01_LEARNING_ARCHITECT.md`)

```text
Purpose:
  Konuyu, uzun içerik üretilmeden önce onaylanabilir bir
  ULA learning architecture'a dönüştürmek.

Input:
  TOPIC, LEARNER GOAL, EXPECTED DEPTH, USE CASE, SOURCES,
  OUTSIDE KNOWLEDGE policy, LEARNER BACKGROUND, SPECIAL CONSTRAINTS.
  (PROJECT_BRIEF_TEMPLATE bu input'u yapılandırır.)

Operation:
  11 adım: learning goal → topic type/adapter → L0 →
  block definitions → recursive zoom points → L1–L4 depth plan →
  concept home registry → confusion boundaries →
  reference boundary → learning routes → 20 maddelik architecture audit.

Output:
  12 bölümlü architecture (ARCHITECTURE_OUTPUT_TEMPLATE).
  Son bölüm: Proposed Frozen Architecture.

Boundary:
  Tam ders yazmaz. PDF üretmez. Sayfa düzeni tasarlamaz.
  Kaynak sırasını otomatik öğrenme sırası kabul etmez.
  Kaynak boşluğunu sessizce doldurmaz.
```

### Content Builder (`prompts/02_CONTENT_BUILDER.md`)

```text
Purpose:
  FROZEN architecture'ı tam öğretim içeriğine dönüştürmek.

Input:
  TOPIC, FROZEN ULA ARCHITECTURE, LEARNER GOAL, DEPTH, USE CASE,
  SOURCES, AUTHORITATIVE CORRECTIONS, CONCEPT HOME REGISTRY,
  CANONICAL VOCABULARY, REFERENCE BOUNDARY, OUTSIDE KNOWLEDGE policy.

Operation:
  Her block için: Orientation → L1 → L2 (diagram + ok açıklaması)
  → L3 (+ A ≠ B, What It Is Not) → L4 (Purpose/Symbols/Mapping/
  Interpretation veya NO L4) → Example → Oral → Retrieval → R links.
  Recursive block'ta önce local map.

Output:
  Block sırasıyla öğretim içeriği + Learning Integrity Check
  (10 PASS/FAIL maddesi).

Boundary:
  Architecture'ı yeniden tasarlamaz.
  Ciddi sorun görürse ARCHITECTURE ISSUE / CONTENT DENSITY WARNING
  yazar ve frozen architecture ile devam eder.
```

### Learning Auditor (`prompts/03_LEARNING_AUDITOR.md`)

```text
Purpose:
  Tamamlanmış artifact'i iki bağımsız eksende denetlemek:
  A. Content Integrity, B. Learning Integrity.

Input:
  ULA spec, FROZEN ARCHITECTURE, GENERATED CONTENT, SOURCES,
  AUTHORITATIVE CORRECTIONS, REGISTRY, VOCABULARY,
  REFERENCE BOUNDARY, USE CASE, DEPTH, OUTPUT FORMAT.

Operation:
  20 audit boyutu (A–T). Her biri PASS / PASS WITH NOTES /
  NEEDS REVISION / FAIL. Severity: CRITICAL / HIGH / MEDIUM / LOW.
  10 maddelik öncelik sırası.

Output:
  13 bölümlü audit raporu (AUDIT_REPORT_TEMPLATE).
  Son bölüm: Freeze Recommendation (4 seçenek).

Boundary:
  Architecture tasarlamaz. Ders yazmaz.
  Varsayılan olarak içeriği yeniden yazmaz.
  Content problem → Builder. Architecture problem → Architect.
```

## 4.3 Architecture rules

| Kural | Durum | Kaynak |
|---|---|---|
| Whole before parts | PRESENT | SPEC §2, ARCH §1, BUILD §3, AUDIT §5 |
| Mechanism before theory | PRESENT | SPEC §3, ARCH §4, BUILD §2 |
| Theory before formalism | PRESENT | SPEC §3, SPEC §10, BUILD §12 |
| Freeze rules | PRESENT | ULA README workflow; BUILD §1 (frozen öğeler listesi); ARCHITECTURE_OUTPUT_TEMPLATE §12 ("No Builder may change this architecture without reopening the Architect stage"); AUDIT §36.13 |
| Content generation rules | PRESENT | BUILD §2–§35 |
| Audit rules | PRESENT | AUDIT §3–§35 |
| Learning quality checks | PRESENT | ARCH §11 (20 madde), BUILD §36–§37, SPEC §34 Acceptance Test |
| Terminology consistency | PRESENT | SPEC §20, BUILD §5, AUDIT §15 |
| Repetition control | PRESENT | SPEC §17, BUILD §2 ("each layer must add a new type of understanding"), AUDIT §29 |
| Reference separation | PRESENT | SPEC §12, ARCH §8 + Step 9, BUILD §23, AUDIT §19 |

Ek ULA kuralları (skill için önemli):

- Topic Adapters A–H (SPEC §15) ve Topic Type Inference (SPEC §16).
- Formula Rule: CORE / RECOGNISE / REFERENCE (SPEC §25).
- Number Density Rule (SPEC §26).
- Source-Based Learning Rule ve SOURCE GAP (SPEC §27).
- Architecture Before Content (SPEC §28).
- Presentation Rule: format mimariyi değiştirmez (SPEC §31).
- Anti-Patterns (SPEC §33).

---

# 5. MindMap / NotebookLM Gap Analysis

Hedef davranış:

```text
WHOLE MAP → BRANCH → CHILDREN → SELECT NODE → DEPTH
X AXIS = doğal flow       Y AXIS = seçilmiş node'un derinliği
```

| Alan | Durum | Kanıt | Eksik olan |
|---|---|---|---|
| Semantic graph | PARTIAL | MASTER §26 alanları tanımlar. ULA v1.0'da yok; CHANGELOG "cross-topic knowledge graph support" maddesini **Planned** listeler. | Serialization formatı. Saklama yeri. Pass'ler arası birleştirme (merge) kuralı. |
| Node specification | PARTIAL | MASTER §24 (ilk görünüm), §26 (13 alan). ARCH Step 4 (block metadata). | Kalıcı ve projeler arası benzersiz node ID şeması. HSMM örneği yerel ID kullanır (`P2.B`, `C001`). |
| Edge semantics | ALREADY PRESENT | MASTER §25 (12 relation type). SPEC §14 (horizontal relationship types). BUILD §32 ("Every arrow must have a meaning"). | İki listenin birleşik kontrollü sözlüğü. |
| Parent-child hierarchy | ALREADY PRESENT | MASTER §22. SPEC §5. Block ID hiyerarşisi (`P2.D.1`). | — |
| Recursive zoom | ALREADY PRESENT | MASTER §22. SPEC §5 (ne zaman yapılır kuralları). ARCH Step 5 (STOP CONDITION). | — |
| Parent context korunması | ALREADY PRESENT | MASTER §22 (WORLD → REGION → NODE → DEPTH). BUILD §3 ("You are here:"). | Standart breadcrumb formatı. |
| Progressive expansion | ALREADY PRESENT | MASTER §23. SPEC §13. AUDIT §6. | — |
| Map ve learning depth ayrımı | ALREADY PRESENT | MASTER §21.3 ("Depth yatay eksene konmaz"). SPEC §1 iki eksen. | — |
| Knowledge ve presentation ayrımı | ALREADY PRESENT | MASTER §26 (`KNOWLEDGE ≠ PRESENTATION`). SPEC §31. | — |
| Interactive atlas fikri | PARTIAL | MASTER §45.7, §46, §47. CHANGELOG Planned: "interactive HTML rendering rules". | Rendering spec. Veri modeli. Claude Code terminal karşılığı. |

## 5.1 Operasyonel boşluklar

Kavram düzeyi güçlüdür. Aşağıdaki operasyonel parçalar kaynaklarda yoktur:

1. **Graph serialization.** Node ve edge'lerin dosyada nasıl tutulacağı tanımlı değil.
2. **Persistent node ID.** Projeler arası tekrar kullanılabilir ID şeması yok.
3. **Incremental graph update.** Yeni learning pass mevcut map'e nasıl eklenir, tanımlı değil.
4. **Text-mode interaction.** "Branch seç / node seç / depth aç" etkileşiminin chat/terminal karşılığı tanımlı değil. Claude Code'da etkileşim bir sohbet turudur. Tıklama yoktur.
5. **Terminal rendering kuralı.** ASCII map'in genişlik ve yoğunluk sınırı tanımlı değil.
6. **Relation type birleşimi.** MASTER §25 edge türleri ile SPEC §14 horizontal relationship türleri ayrı listelerdir.

---

# 6. Manual Invocation Analysis

## 6.1 Kaynaklardaki otomatik davranışlar

Aşağıdaki davranışlar **hata değildir**. Kaynak sistemin orijinal mantığıdır.

| # | Otomatik davranış | Kaynak | Tetikleyici |
|---|---|---|---|
| A1 | Task sonunda Human Synchronization | MASTER §16 | "Önemli task veya milestone" bitişi |
| A2 | Human Synchronization çıktısı üretimi | MASTER §17 | "Her önemli task sonunda AI gerektiğinde…" |
| A3 | Knowledge Priority sınıflandırması | MASTER §18 | "Her önemli task sonunda…" |
| A4 | Learning Event tespiti ve işaretleme | MASTER §36 | AI'ın kendi değerlendirmesi |
| A5 | Otomatik ULA tetiklemesi | MASTER §36 | "ULA özellikle şu durumlarda tetiklenir" |
| A6 | Jira kartı içinde learning adımları | MASTER §37 | Kart AUDIT/REVIEW sonrası |
| A7 | Learning tamamlanmadan kart DONE sayılmaz | MASTER §37 | "learning kısmı tamamlanmamış sayılır" |
| A8 | Karar sonu checkpoint soruları | MASTER §41 | "önemli kararların sonunda" |
| A9 | Milestone sonunda Human Review | MASTER §42 | Milestone bitişi |
| A10 | Knowledge Debt backlog güncellemesi | MASTER §18, §19 | USEFUL TO KNOW sınıflandırması |
| A11 | Pipeline içinde inline learning | MASTER §3A, §48 | IMPLEMENT → TEST → REVIEW → HS |
| A12 | Experience Map / Concept Home güncellemesi | MASTER §48 | Learning pass bitişi |

ULA tarafında otomatik tetikleme yoktur. ULA her zaman açık bir konu ile çağrılır. ULA workflow'u ayrıca bir **HUMAN REVIEW** kapısı içerir (ULA README). Bu kapı manuel modele zaten uygundur.

## 6.2 Yeni skill için çözüm

```text
LOGICAL FLOW      → KORUNUR
INVOCATION TIMING → /learning içine taşınır
```

| Mod | Davranış |
|---|---|
| NORMAL PROJECT WORK | Learning OFF. A1–A12 çalışmaz. Learning çıktısı üretilmez. |
| `/learning` çağrısı | Learning ON. A1–A12 mantığı **seçilen scope** üzerinde sırayla çalışır. |

`/learning` içindeki mantıksal sıra MASTER §48 ile aynı kalır:

```text
SCOPE RESOLUTION (yeni)
↓
HUMAN SYNCHRONIZATION (A1, A2)
↓
KNOWLEDGE PRIORITY (A3)
↓
LEARNING EVENT EXTRACTION (A4)
↓
SELECT DEPTH → LIGHT / FULL ULA (A5)
↓
RETRIEVAL / CHECKPOINT (A8)
↓
EXPERIENCE + CONCEPT HOME UPDATE (A12)
↓
QUEUE / DEBT UPDATE (A10)
↓
COVERAGE LEDGER UPDATE (yeni)
```

A7 (DONE semantiği) özel karar gerektirir. Bkz. Bölüm 16, C-07.

## 6.3 Teknik uygulama notu

Claude Code skill frontmatter'ı model tarafından otomatik çağrıyı kapatan bir alan destekler (`disable-model-invocation`). Bu alan manuel invocation kuralını platform düzeyinde zorlar. Aşama 2'de güncel dokümantasyonla doğrulanmalıdır.

---

# 7. Learning Coverage Gap Analysis

## 7.1 Durum

**Learning Coverage Management: ABSENT.**

Kaynaklarda en yakın parçalar:

| Parça | İlişki | Neden yeterli değil |
|---|---|---|
| Knowledge Debt (MASTER §19) | Ertelenen **kavramları** tutar | Ertelenen **work unit'leri** tutmaz. Kapanma kuralı yok. |
| Jira lifecycle (MASTER §37) | Kart başına learning adımı | Learning her kartta inline olur. Gap oluşmaz. Ledger gerekmez. |
| Learning Event (MASTER §36) | Öğrenme noktalarını işaretler | Kalıcı ID ve durum yok. |
| ULA Project Brief §22 "Current Status" | Proje aşaması | ULA projesinin durumudur. Coverage değildir. |

Kaynak sistem inline learning varsaydığı için coverage boşluğu hiç oluşmaz. Manuel invocation bu boşluğu **yaratır**. Bu nedenle coverage yeni skill'in zorunlu yeni bileşenidir.

## 7.2 Gerekli yeni kavramlar

| Kavram | Tanım | Durum |
|---|---|---|
| Learning State | Projenin learning özet durumu: son pass, son boundary, açık queue sayısı | MISSING |
| Coverage Ledger | Her work unit için kalıcı kayıt: ID, kaynak, durum, pass referansı | MISSING |
| Last covered boundary | En son COVERED olan work unit | MISSING |
| Current project boundary | Şu anki en son work unit | MISSING |
| Deferred coverage | Kullanıcının bilinçli olarak ertelediği work unit | MISSING |
| Skipped-by-user | Kullanıcının öğrenme gerektirmez dediği work unit | MISSING |
| Partial coverage | Work unit'in bazı learning event'leri işlendi, bazıları ertelendi | MISSING |
| Scope resolution | 5 seçenekli kullanıcı menüsü ve seçimin ledger'a yazılması | MISSING |
| Gap detection | Ledger ile mevcut work unit listesinin karşılaştırılması | MISSING |
| Persistent identifiers | Work unit'in oturumlar arası sabit kimliği | MISSING |

## 7.3 Kritik tasarım bulgusu: boundary yeterli değildir

Kullanıcı örneği:

```text
Step 1–3  → COVERED   (1. /learning)
Step 10   → COVERED   (2. /learning, kullanıcı yalnız son adımı seçti)
Step 4–9  → DEFERRED
```

Bu durumda `last covered boundary = Step 10` olur. Ancak Step 4–9 hâlâ açıktır.

Sonuç:

```text
Tek bir high-water mark (last covered boundary)
≠
doğru gap bilgisi
```

Coverage Ledger **küme tabanlı** olmalıdır. Her work unit kendi durumunu taşımalıdır. Gap şu formülle bulunur:

```text
GAP = { current work units } − { COVERED ∪ SKIPPED_BY_USER ∪ NOT_LEARNING_RELEVANT }
```

DEFERRED ve PARTIAL birimler her `/learning` çağrısında görünür kalır.

## 7.4 Önerilen durum sözlüğü (henüz implement edilmedi)

| Durum | Anlam | Sonraki `/learning`'de görünür mü? |
|---|---|---|
| UNCOVERED | Henüz hiç değerlendirilmedi | Evet |
| COVERED | Learning pass tamamlandı | Hayır |
| PARTIAL | Bazı learning event'ler ertelendi | Evet (yalnız açık event'ler) |
| DEFERRED | Kullanıcı scope dışında bıraktı | Evet |
| SKIPPED_BY_USER | Kullanıcı açıkça "öğrenme gerekmez" dedi | Hayır (varsayılan) |
| NOT_LEARNING_RELEVANT | Human Sync + Knowledge Priority sonucu yalnız IMPLEMENTATION DETAIL | Hayır |

`DEFERRED ≠ SKIPPED_BY_USER`. DEFERRED geri gelir. SKIPPED geri gelmez.

`NOT_LEARNING_RELEVANT` kaynak mantığından gelir: MASTER §18 "IMPLEMENTATION DETAIL → ULA çalıştırılmaz" ve MASTER §36 "EXPERIENCE ONLY".

## 7.5 Scope menüsü

Kullanıcı gereksinimi ile uyumlu menü:

```text
LAST COVERED: <id>
CURRENT:      <id>
UNCOVERED:    <liste veya aralık>
DEFERRED:     <liste>

1. Yalnız son adımı işle.
2. Belirli adımları veya aralığı işle.
3. Tüm arayı kapat.
4. Pending / deferred queue'yu işle.
5. Custom scope belirt.
```

Seçim sonrası kural: Seçilmeyen UNCOVERED birimler **DEFERRED** olarak ledger'a yazılır. Hiçbir birim kaybolmaz.

---

# 8. Work Unit Identification Analysis

## 8.1 Öncelik sırası değerlendirmesi

| # | Kaynak | Ne zaman güvenilir | Risk | Değerlendirme |
|---|---|---|---|---|
| 1 | Explicit user scope | Her zaman | Kullanıcı hatası | En yüksek otorite. Belirsizliği her zaman çözer. |
| 2 | Jira issue / milestone ID | Jira kullanılıyor ve key'ler commit/branch/doc içinde görünüyor | Bu ortamda Jira connector yok. Claude kart içeriğini okuyamayabilir. | Key sabit ve benzersizdir. Erişim varsa güvenilir. |
| 3 | Git commit / range | Proje git repository'si | Rebase/squash hash'leri değiştirir. Commit edilmemiş iş görünmez. Büyük commit birden fazla unit içerir. | Sıralı ve doğrulanabilir. Hash + mesaj + tarih birlikte saklanmalı. **Bu repository git değildir.** |
| 4 | Project phase / numbered step | Numaralar kalıcı bir dokümanda tanımlı | Yeniden numaralandırma | Doküman stabil ise güvenilir. Örnek: `V8_Clean_Validation/outputs/stage_08_*` gibi stage klasörleri. |
| 5 | Persistent project document | PLAN.md, CHANGELOG, ADR listesi | Doküman güncel değilse eksik | Destekleyici kaynak. |
| 6 | Other stable identifier | PR numarası, git tag, ADR ID | Projeye bağlı | Durum bazlı kullanılır. |
| 7 | Ambiguous | Yukarıdakiler sonuç vermiyor | — | Kullanıcıya sor. Tahmin etme. |

## 8.1A Onaylanmış universal priority (Q5 — RESOLVED)

Bölüm 8.1 analiz tablosudur. Uygulanacak sıra aşağıdaki sıradır. Tek bir kaynak global olarak hard-code edilmez.

```text
1. Explicit user scope
↓
2. Project-configured work unit source   (LEARNING_CONFIG.md → work_unit_source)
↓
3. Jira / issue tracker, erişilebiliyorsa
↓
4. Persistent task / phase document
↓
5. Git commit / commit range
↓
6. Other stable identifier
↓
7. Ambiguous → ask user
```

Varsayılan config:

```text
work_unit_source: auto
```

Proje override değerleri: `jira`, `git`, `phase-doc` veya ileride desteklenen başka bir source.

## 8.2 Kesin kurallar

1. **File modification time kritik coverage kararında kullanılmaz.** mtime kopyalama, checkout, formatter ve editör kaydı ile değişir. İş birimini temsil etmez.
2. **Konuşma geçmişi tek başına kalıcı kaynak değildir.** Claude Code context'i özetlenebilir. Oturum biter. Work unit ID dosyaya yazılmadıkça kalıcı değildir.
3. Her ledger kaydı kaynağını taşımalıdır: `source_type` (user / jira / git / phase / doc / other) + `id` + `label`.
4. Birden fazla kaynak çelişirse kullanıcıya sorulur.

## 8.3 Açık tasarım sorusu

Learning OFF iken Claude work unit'leri pasif olarak kaydetmeli mi?

- **Seçenek A — Pasif kayıt yok.** `/learning` çağrısında work unit'ler git/Jira/doc üzerinden yeniden çıkarılır. Learning OFF kuralı tam korunur.
- **Seçenek B — Hafif pasif kayıt.** Normal iş sırasında yalnız work unit ID kaydı tutulur. Bu "Learning OFF" kuralını zayıflatır. Hook veya ek davranış gerektirir.

Öneri: **Seçenek A.** Gerekçe: meta-work sınırı (MASTER §43) ve manuel invocation kuralı.

**Karar (Q4 — RESOLVED): Seçenek A.** Learning OFF iken passive tracking yoktur. Work unit history `/learning` anında mevcut project evidence üzerinden reconstruct edilir.

---

# 9. Human Synchronization Analysis

| Öğe | Durum | Kaynak |
|---|---|---|
| Amaç (minimum yeterli mental model) | PRESENT | MASTER §16 |
| One-sentence summary | PRESENT | MASTER §17.1 |
| Simple causal explanation (3–6 cümle) | PRESENT | MASTER §17.2 |
| Mental model diyagramı | PRESENT | MASTER §17.3 |
| Technical translation (intuition ↔ term) | PRESENT | MASTER §17.4 |
| Important decisions | PRESENT | MASTER §17.5 |
| What changed (davranış, dosya listesi değil) | PRESENT | MASTER §17.6 |
| Evidence + epistemik durum | PRESENT | MASTER §17.7 |
| Compressor ≠ ULA Teacher ayrımı | PRESENT | MASTER §14 |
| Çoklu work unit üzerinde HS | ABSENT | Kaynak tek task varsayar |

Değerlendirme:

- Human Synchronization skill'in en hafif ve en sık kullanılacak parçasıdır.
- Çıktı formatı tam tanımlıdır. Doğrudan template'e dönüşebilir.
- Yeni ihtiyaç: Scope birden fazla work unit içerdiğinde HS'nin **toplu** mu yoksa **unit başına** mı yapılacağı. Öneri: Önce scope seviyesinde tek bir sıkıştırılmış HS. Sonra yalnız MUST UNDERSTAND event'leri için ayrıntı.
- HS, ULA'dan bağımsız çalışabilir. Bir `/learning` çağrısı yalnız HS ile bitebilir (tüm event'ler EXPERIENCE ONLY ise).

Classification: **KEEP** (mantık) + **MOVE** (`03_HUMAN_SYNC_PROTOCOL.md` + `HUMAN_SYNC_TEMPLATE.md`).

---

# 10. Knowledge Priority / Debt Analysis

## 10.1 Knowledge Priority

| Öğe | Durum | Not |
|---|---|---|
| Üç sınıf | PRESENT | MUST UNDERSTAND / USEFUL TO KNOW / IMPLEMENTATION DETAIL |
| Sınıf → aksiyon eşlemesi | PRESENT | ULA pass / kısa açıklama veya Debt / hiçbir şey |
| "Her teknik ayrıntı öğrenme borcu değildir." | PRESENT | Token efficiency için temel kural |

## 10.2 Knowledge Debt

| Öğe | Durum | Not |
|---|---|---|
| Kayıt formatı | PRESENT | Concept, Why, One-sentence, Why matters, Priority |
| Öncelik | PRESENT | NOW / LATER / OPTIONAL |
| Backlog olarak uzun vadeli varlık | PRESENT | MASTER §45.5 |
| Saklama yeri | ABSENT | — |
| Kapanma kuralı (debt → COVERED) | ABSENT | — |
| Work unit'e bağlantı | ABSENT | Hangi work unit'te ortaya çıktığı tutulmaz |
| Deferred coverage ile ilişki | ABSENT | — |

## 10.3 Kritik ayrım

```text
KNOWLEDGE DEBT   = ertelenmiş KAVRAM        (concept-level)
DEFERRED UNIT    = ertelenmiş İŞ BİRİMİ     (work-unit-level)
```

İki kayıt farklıdır. Ancak aynı `LEARNING_QUEUE` dosyasında iki ayrı bölüm olarak yaşayabilir. Bir DEFERRED work unit işlendiğinde yeni Knowledge Debt kayıtları üretebilir.

Classification: Knowledge Priority **KEEP**. Knowledge Debt **REWRITE** (lifecycle ve saklama eklenmeli).

---

# 11. Concept Home / Experience Analysis

| Öğe | Durum | Kaynak |
|---|---|---|
| One Concept — One Home | PRESENT | MASTER §32, SPEC §17, ARCH §7, BUILD §18, AUDIT §16 |
| Project Appearances | PRESENT | MASTER §32, MASTER §26 node alanı |
| Reusable signal | PRESENT | MASTER §5, §9, §39 |
| New project delta | PRESENT | MASTER §32: "Yalnız … eklenir" (5 soru) |
| Duplicate theory prevention | PRESENT | SPEC §17, AUDIT §16 (DUPLICATED THEORY), AUDIT §29 |
| Knowledge debt | PARTIAL | Bkz. Bölüm 10 |
| Experience map | PRESENT | MASTER §5, §33.B |
| DSA pattern map | PRESENT | MASTER §8 |
| System Design experience map | PRESENT | MASTER §5 |
| Concept Registry | PRESENT | SPEC §18, HSMM örneği §7 |

## 11.1 Kritik bulgu: Concept Home'un yeri

Kaynak Concept Home'u **projeler üstü** tanımlar:

```text
Concept: Caching
Home:    Personal Technical Library / Caching        ← MASTER §32
Project Appearances:
- Music Momentum App
- Recommendation API
- Feature Serving System
```

MASTER §45 "PERSONAL TECHNICAL LIBRARY" kavramını ayrı uzun vadeli varlık olarak listeler.

Önerilen hedef mimari (`docs/learning/concepts/`) Concept Home'u **proje içine** koyar. Bu durumda:

- Proje A'da öğrenilen Caching, Proje B'de görünmez.
- Proje B aynı teoriyi yeniden yazar.
- One Concept — One Home ilkesi projeler arası düzeyde bozulur.

Çözüm seçenekleri (Bölüm 21, Q2):

| Seçenek | Yapı | Artı | Eksi |
|---|---|---|---|
| A — Global library | Concept Home'lar kullanıcı düzeyinde tek bir konumda. Proje yalnız Experience Note tutar. | Kaynak niyetine tam uyum | Proje repository'si dışında state. Konum seçimi gerekir. |
| B — Project-local | Her proje kendi Concept Home'unu tutar | Basit. Tek repo. | Projeler arası tekrar. Kaynak ilkesine aykırı. |
| C — Hybrid | Global library + proje içinde pointer (Concept ID + link) | Hem tekrar yok hem proje bağımsız okunabilir | İki konum yönetimi |

Öneri: **C — Hybrid.** Global library kaynak niyetini korur. Projedeki pointer, proje okuyucusuna bağlam verir.

**Karar (Q2 — RESOLVED): HYBRID.**

- Gerçek Concept Home, Personal Technical Library içinde yaşar.
- Library konumu skill içinde hard-code edilmez. Konum `LEARNING_CONFIG.md → personal_library_path` ile tanımlanır.
- Proje içinde yalnız şunlar tutulur: Concept ID, Concept Home pointer, Project Appearance, project-specific delta, Experience Note.
- Library yapılandırılmadıysa skill hata vermez. Concept geçici olarak `docs/learning/concepts/` içinde project-local tutulur. Library yapılandırılınca concept library'ye promote edilir.

## 11.2 Universal logic vs project state ayrımı

| Parça | Sınıf |
|---|---|
| Concept Home kuralı, delta kuralı, duplicate prevention | UNIVERSAL SKILL LOGIC |
| Concept Home / Experience Note / Decision Record şablonları | UNIVERSAL SKILL LOGIC |
| DSA Pattern Map **iskeleti** (15 pattern sözlüğü) | UNIVERSAL SKILL LOGIC |
| Concept Home **içeriği** | PERSONAL STATE (projeler arası) |
| Experience Map **birikimi**, DSA Pattern Map **doldurulmuş hali** | PERSONAL STATE (projeler arası) |
| Experience Note, ADR, DSA Decision Record | PROJECT-SPECIFIC STATE |

Not: Kaynak sistem üç katman ima eder: **universal logic**, **personal (cross-project) state**, **project state**. Kullanıcının ikili ayrımı (universal vs project) bu üçüncü katmanı gizler.

---

# 12. Token & Context Efficiency Analysis

| İlke | Durum | Kaynak / kanıt |
|---|---|---|
| Compress before teaching | PRESENT | MASTER §14 Compressor, §16, §17. HS, ULA'dan önce gelir. |
| Minimum sufficient explanation | PRESENT | MASTER §16 "minimum yeterli mental model" |
| Teach only important information | PRESENT | MASTER §18, §36 ("10–20 yüksek değerli öğrenme olayı") |
| Implementation detail suppression | PRESENT | MASTER §17.5, §18, §34. SPEC §12. |
| Progressive disclosure | PRESENT | MASTER §23. SPEC §13. AUDIT §6. |
| Reference instead of repetition | PRESENT | BUILD §18 "REQUIRED REMINDER: 1–3 short sentences" |
| Concept Home reuse | PRESENT | MASTER §32. SPEC §17. |
| Delta instead of full rewrite | PARTIAL | Kavram bilgisi için var (MASTER §32). Dosya/map/ledger güncellemesi için yok. |
| Avoid unnecessary HTML generation | PARTIAL | MASTER §43 meta-work sınırı ve SPEC §31 format bağımsızlığı var. Ancak MASTER §46–§47 interactive atlas'ı varsayılan görsel hedef yapar. Gerilim var. |
| Avoid loading full master spec every run | MISSING | Kaynak bir skill runtime'ı varsaymaz. Bu kavram yeni gereksinimdir. |

## 12.1 Yükleme maliyeti

| Grup | Boyut | Kaba token |
|---|---|---|
| Master spec | 44.6 KB | ~12k–15k |
| ULA spec | 25.9 KB | ~7k–8k |
| Üç ULA rol prompt'u | 56.4 KB | ~14k–16k |
| ULA templates | 16.6 KB | ~4k–5k |
| HSMM examples | 27.9 KB | ~7k–8k |

Her `/learning` çağrısında tümünü yüklemek ~45k–55k token harcar. Bu kabul edilemez.

Öneri:

- `SKILL.md` kısa kalır. Yalnız invocation kuralı, run loop ve load map içerir.
- Light ULA yalnız `01_OPERATIONAL_CORE` + ilgili protocol dosyasını yükler.
- Full ULA rol dosyalarını **sırayla ve tek tek** yükler. Üçünü aynı anda yüklemez.
- Master spec ve HSMM examples otomatik yüklenmez. Yalnız açık ihtiyaçta okunur.

---

# 13. Light ULA vs Full ULA Analysis

**Durum: PARTIAL.**

## 13.1 Kaynaklarda bulunan

| Kaynak | Ayrım | Tür |
|---|---|---|
| MASTER §35 | Zoom 1 Quick Orientation / Zoom 2 Working Model / Zoom 3 Deep Learning | **Depth** |
| SPEC §23, ARCH Step 10, BUILD §26 | Quick / Standard / Deep / Reference route | **Depth** |
| BUILD §25 | Beginner / Intermediate / Advanced / Research | **Depth** |
| MASTER §35 | Zoom 3 açılma kriterleri (7 madde) | **Seçim kuralı** |
| MASTER §48 | "SELECT DEPTH → ULA LEARNING PASS" | Depth seçimi var, process seçimi yok |
| ULA README | PROJECT BRIEF → ARCHITECT → HUMAN REVIEW → FROZEN → BUILDER → AUDITOR → FREEZE | **Tek process** (her zaman tam) |

## 13.2 Kaynaklarda bulunmayan

- Üç rolün **ne zaman atlanabileceği** tanımlı değil.
- Tek geçişlik (Architect + Builder birleşik) hafif mod tanımlı değil.
- Audit'in hafif hali (self-check) tanımlı değil.

## 13.3 Eşleştirme önerisi

| Kullanıcı modu | Kaynak karşılığı | Process |
|---|---|---|
| LIGHT ULA | Zoom 1 / Zoom 2 (Quick / Standard) | Tek geçiş: Local Map → L1 → L2 → gerekirse L3 → Confusion check → Retrieval. Builder §36 Content Quality Test'in kısa hali self-check olarak. |
| FULL ULA | Zoom 3 (Deep) | Architect → Human Review (freeze) → Builder → Auditor → Final Artifact |

Fark notu: Kullanıcının Light ULA tanımında "Retrieval" vardır. MASTER Zoom 2 tanımında "Confusion Check" vardır. Öneri: Light ULA ikisini de kısa biçimde içerir.

Full ULA seçim kuralı MASTER §35 Zoom 3 kriterlerinden türetilmelidir: kritik teori, kariyer açısından merkezi konu, sık kullanılan yapı, önemli mimari karar, önemli DSA pattern, ciddi failure/performance davranışı, anlaşılmayan kritik mekanizma. Kullanıcı her zaman modu override edebilir.

---

# 14. Universal Logic vs Project State

| Bileşen | UNIVERSAL SKILL LOGIC | PERSONAL STATE (cross-project) | PROJECT-SPECIFIC STATE |
|---|---|---|---|
| Manual invocation kuralı | ✔ | | |
| Run loop (`/learning` adımları) | ✔ | | |
| Coverage logic, durum sözlüğü, gap formülü | ✔ | | |
| Scope resolution menüsü | ✔ | | |
| Work unit identification priority | ✔ | | |
| Human Synchronization protocol + template | ✔ | | |
| Knowledge Priority kuralları | ✔ | | |
| Learning Event kriterleri | ✔ | | |
| ULA spec, üç rol, ULA templates | ✔ | | |
| Light / Full seçim kuralı | ✔ | | |
| MindMap protocol, node/edge schema | ✔ | | |
| Audit rules | ✔ | | |
| Concept Home / Experience / Decision Record şablonları | ✔ | | |
| DSA Pattern Map iskeleti | ✔ | | |
| Concept Home içerikleri (Personal Technical Library) | | ✔ | |
| Birikmiş SD Experience Map / DSA Experience Map | | ✔ | |
| Global semantic graph | | ✔ | |
| Learning State | | | ✔ |
| Coverage Ledger (covered Jira kartları, commit'ler, step'ler) | | | ✔ |
| Current learning boundary | | | ✔ |
| Deferred work units, Learning Queue | | | ✔ |
| Knowledge Debt (proje kaynaklı) | | | ✔ (öneri; global de olabilir) |
| Learning pass çıktıları | | | ✔ |
| Project Experience Notes, ADR, DSA Decision Records | | | ✔ |
| Project maps | | | ✔ |
| Project audits | | | ✔ |

---

# 15. Source → Target Architecture Mapping

## 15.1 Önerilen yapının değerlendirmesi

| Kriter | Değerlendirme |
|---|---|
| Separation of concerns | İyi. references / ula / templates ayrımı nettir. Sorun: `07_AUDIT_PROTOCOL.md` ile `ula/LEARNING_AUDITOR.md` aynı işi yapma riski taşır. `04_ULA_PROTOCOL.md` ile `ula/ULA_SPECIFICATION.md` aynı riski taşır. |
| Portability | **Sorunlu.** `skills/learning/state/` skill klasörünün içindedir. Skill başka projeye kopyalanınca eski projenin state'i de kopyalanır. GitHub'a konunca kişisel state yayınlanır. |
| Token efficiency | İyi, şu koşulla: `00_MASTER_SYSTEM_SPEC.md` asla otomatik yüklenmez. SKILL.md bir load map içerir. |
| State management | **Sorunlu.** State konumu (skill içi) yanlış. Concept Home konumu (proje içi) kaynak niyetine aykırı (Bölüm 11.1). |
| Maintainability | İyi. Numaralı reference dosyaları okunabilir. ULA dosyalarının ayrı klasörde kalması ULA'nın değiştirilmemesini kolaylaştırır. |
| Claude Code usability | İyi. `SKILL.md` + `references/` yapısı Claude Code skill düzenine uyar. Templates eksik: Human Sync, Decision Record, Learning State, Learning Queue. ULA'nın kendi 4 template'i yerleştirilmemiş. |
| Duplication risk | Orta. 04 ↔ ULA_SPECIFICATION, 07 ↔ LEARNING_AUDITOR, 00 ↔ 01–06. Kural gerekir: 01–07 yalnız **operasyonel delta** içerir. Kaynak metni tekrar etmez. Pointer verir. |

## 15.2 Kaynak dosya → hedef konum

| Kaynak | Hedef | Sınıf |
|---|---|---|
| `StudySystem_WithAI.txt` | `references/00_MASTER_SYSTEM_SPEC.md` (verbatim arşiv, otomatik yüklenmez) | MOVE |
| MASTER §16–§19, §36 | `references/03_HUMAN_SYNC_PROTOCOL.md` | REWRITE (manual timing) |
| MASTER §20, §27–§31, §34–§35, §40, §50 | `references/04_ULA_PROTOCOL.md` (Light ULA + Full routing) | REWRITE |
| MASTER §21–§26, §46–§47 | `references/05_MINDMAP_PROTOCOL.md` | REWRITE + MISSING parçalar |
| MASTER §5, §8, §9, §32, §33, §38, §39 | `references/06_KNOWLEDGE_PERSISTENCE.md` + templates | REWRITE |
| MASTER §37, §41, §42, §48 | `references/01_OPERATIONAL_CORE.md` (run loop) | REWRITE |
| MASTER §1–§4, §6–§7, §10–§15, §43–§45, §49, §51–§52 | `00_MASTER_SYSTEM_SPEC.md` içinde kalır; `SKILL.md` içinde 3–5 satırlık özet | KEEP (archive) |
| — | `references/02_COVERAGE_PROTOCOL.md` | MISSING (yeni) |
| `ULA_SPECIFICATION_v1.0.md` | `ula/ULA_SPECIFICATION.md` | KEEP |
| `prompts/01_LEARNING_ARCHITECT.md` | `ula/LEARNING_ARCHITECT.md` | KEEP |
| `prompts/02_CONTENT_BUILDER.md` | `ula/CONTENT_BUILDER.md` | KEEP |
| `prompts/03_LEARNING_AUDITOR.md` | `ula/LEARNING_AUDITOR.md` | KEEP |
| `templates/*.md` (4 dosya) | `ula/templates/` | MOVE |
| `ULA/README.md` | Workflow kısmı `04_ULA_PROTOCOL.md` içine | MERGE |
| `ULA/CHANGELOG.md` | Skill dışı (repo kökü veya `ula/` altında, otomatik yüklenmez) | MOVE |
| `examples/HSMM_PILOT/` | `ula/examples/` (otomatik yüklenmez) | MOVE |

## 15.3 Hedef yapıda eksik template'ler

| Template | Kaynak | Sınıf |
|---|---|---|
| `HUMAN_SYNC_TEMPLATE.md` | MASTER §17 | MISSING |
| `DECISION_RECORD_TEMPLATE.md` (ADR + DSA DR) | MASTER §38, §39 | MISSING |
| `LEARNING_CONFIG_TEMPLATE.md` (`personal_library_path`, `work_unit_source`) | Q2, Q5 kararları | MISSING |
| `LEARNING_STATE_TEMPLATE.md` | — | MISSING |
| `LEARNING_QUEUE_TEMPLATE.md` (Deferred + Knowledge Debt) | MASTER §19 | MISSING |

---

# 16. Conflicts

### C-01 — Automatic lifecycle vs manual invocation

```text
Conflict:
  Master learning'i her önemli task/milestone sonunda otomatik çalıştırır.
  Yeni skill yalnız /learning ile çalışmalıdır.
Why:
  Kaynak inline learning varsayar (MASTER §16, §17, §18, §36, §37, §42, §48).
Keep:
  HS → KP → Learning Event → ULA → Experience → Reuse mantıksal sırası.
Change:
  Tetikleme zamanı. Normal iş sırasında learning çıktısı yok.
Recommended resolution:
  Logical flow /learning içinde aynen çalışır. Coverage Ledger,
  inline çalışmanın bıraktığı boşluğu takip eder.
  disable-model-invocation ile platform düzeyinde zorlanır.
```

### C-02 — Full ULA every time vs token-efficient selective learning

```text
Conflict:
  ULA README tek ve tam bir workflow verir (Architect → Review → Builder → Auditor).
  Yeni skill token-efficient olmalıdır.
Why:
  ULA büyük, tekil konular (ör. HSMM paper) için tasarlanmıştır.
  Master ise "10–20 learning event" ve Zoom 1/2/3 ile seçici öğrenme ister.
Keep:
  ULA öğretim sırası. Üç rol. Freeze kuralı.
Change:
  Process seçimi. Varsayılan Light ULA. Full ULA kriterle veya kullanıcı isteğiyle.
Recommended resolution:
  Bölüm 13.3 eşlemesi. Full ULA yalnız MASTER §35 Zoom 3 kriterlerinde.
```

### C-03 — Linear learning note vs NotebookLM-style MindMap

```text
Conflict:
  ULA templates lineer markdown üretir. Master varsayılan görseli
  interactive atlas olarak tanımlar.
Why:
  ULA v1.0 rendering'i Planned bırakır (CHANGELOG). Master vizyonu ileridedir.
Keep:
  KNOWLEDGE ≠ PRESENTATION ilkesi. Semantic graph önce.
Change:
  Kaynak gerçeği: semantic graph. Lineer not ve ASCII map yalnız birer view.
Recommended resolution:
  Aşama 2: graph schema + terminal ASCII map + breadcrumb.
  HTML atlas sonraki aşama ve yalnız istek üzerine (MASTER §43 meta-work sınırı).
```

### C-04 — One-time learning pass vs persistent learning coverage

```text
Conflict:
  Kaynakta learning pass tek seferlik bir olaydır. Kalıcı coverage kaydı yoktur.
Why:
  Inline modelde gap oluşmaz.
Keep:
  Learning pass yapısı ve çıktıları.
Change:
  Her pass bir Coverage Ledger kaydı üretir. Ledger küme tabanlıdır.
Recommended resolution:
  02_COVERAGE_PROTOCOL.md + COVERAGE_LEDGER. Bölüm 7.3–7.5.
```

### C-05 — Universal skill logic vs project-specific state

```text
Conflict:
  Önerilen yapı state/ klasörünü skill klasörü içine koyar.
Why:
  Skill klasörü kopyalanır ve GitHub'a konur. State projeye aittir.
Keep:
  state dosya isimleri (LEARNING_STATE, COVERAGE_LEDGER, LEARNING_QUEUE).
Change:
  Konum. Skill içinde yalnız *_TEMPLATE dosyaları kalır.
Recommended resolution:
  State → docs/learning/state/. Skill klasörü runtime'da read-only kabul edilir.
```

### C-06 — Personal Technical Library vs project-local Concept Home

```text
Conflict:
  MASTER §32, §45 Concept Home'u projeler üstü kişisel kütüphane yapar.
  Önerilen yapı docs/learning/concepts/ ile proje içine koyar.
Why:
  Portability hedefi tek repo düşünür. Kaynak ise birden fazla proje boyunca birikim ister.
Keep:
  One Concept — One Home.
Change:
  Üç katmanlı state modeli: universal / personal / project.
Recommended resolution:
  Hybrid (Bölüm 11.1, Seçenek C). Karar: Q2.
```

### C-07 — "Learning olmadan DONE yok" vs Learning OFF

```text
Conflict:
  MASTER §37: insan mental modeli kuramıyorsa kart learning açısından tamamlanmamıştır.
  Yeni skill normal işte learning yapmaz.
Why:
  Kaynak teknik DONE ile learning DONE'ı tek kartta birleştirir.
Keep:
  "Learning tamamlanmadı" bilgisinin kaybolmaması.
Change:
  İki ayrı durum: TECHNICAL DONE (proje akışı) ve LEARNING COVERAGE (ledger).
Recommended resolution:
  Kart teknik olarak DONE olabilir. Ledger'da UNCOVERED / DEFERRED kalır.
  Gap bir sonraki /learning'de görünür.
```

### C-08 — Terminoloji kayması (Master vs ULA)

```text
Conflict:
  Aynı kavram için farklı adlar:
  - L1 "Simple Meaning" (MASTER) vs "Simple Explanation" (ULA)
  - "Whole / Map" (MASTER) vs "L0 — Map" (ULA)
  - "L4 Formalism / Math" vs "L4 Math / Formalism"
  - Zoom 1/2/3 (MASTER §35) vs Quick/Standard/Deep (ULA)
  - Confusions: ayrı adım (MASTER §20) vs L2/L3 içi (SPEC §21)
  - L2: INPUT→OPERATION→DECISION→OUTPUT→NEXT (MASTER §28)
        vs INPUT→OPERATION→OUTPUT→NEXT (ULA README; BUILD §7 complex variant DECISION içerir)
Why:
  İki kaynak ayrı zamanlarda yazılmış.
Keep:
  Anlam aynıdır. Hiçbir kural değişmez.
Change:
  Skill dosyalarında tek canonical vocabulary + eşleme tablosu.
Recommended resolution:
  ULA terimleri canonical (ULA kendi alanında authoritative).
  Master terimleri ilk kullanımda eşlenir. Karar: Q1.
```

### C-09 — Source-based ULA vs project-learning knowledge policy

```text
Conflict:
  ULA kaynak sadakati ve OUTSIDE KNOWLEDGE politikasını zorunlu tutar (ARCH, BUILD §19–§20).
  Proje learning'inde "kaynak" proje kodu/dokümanıdır. Kavram teorisi genel bilgidir.
Why:
  ULA paper-merkezli bir pilotla tasarlanmış.
Keep:
  SOURCE GAP ve epistemik etiketler (VERIFIED / INFERRED / ASSUMED / UNRESOLVED).
Change:
  /learning için varsayılan politika tanımlanmalı.
Recommended resolution:
  Proje gerçekleri için: proje dosyaları authoritative.
  Genel teori için: ALLOWED WITH LABELS. Karar: Q6.
```

### C-10 — Interactive atlas default vs meta-work boundary

```text
Conflict:
  MASTER §46–§47 atlas'ı varsayılan görsel deneyim yapar.
  MASTER §43 meta-work'ün projeyi aşmasını yasaklar.
Why:
  Vizyon ile pratik sınır aynı belgede.
Keep:
  İkisi de.
Change:
  Sıralama: önce veri (graph), sonra text view, en son HTML.
Recommended resolution:
  HTML atlas Aşama 2 kapsamı dışında. Karar: Q8.
```

---

# 17. Missing Components

| # | Bileşen | Neden gerekli | Öncelik |
|---|---|---|---|
| M-01 | Coverage Protocol | Manuel invocation gap üretir | CRITICAL |
| M-02 | Coverage Ledger (küme tabanlı) + durum sözlüğü | Gap tespiti ve DEFERRED korunumu | CRITICAL |
| M-03 | Work unit ID şeması + kaynak önceliği | Kalıcı ve doğrulanabilir birimler | CRITICAL |
| M-04 | Scope resolution menüsü | Kullanıcı kontrollü işleme | CRITICAL |
| M-05 | Learning State dosyası | Hızlı özet; ledger'ı tam okumadan başlangıç | HIGH |
| M-06 | `SKILL.md` load map | Token efficiency | HIGH |
| M-07 | Light / Full ULA seçim kuralı | Token efficiency | HIGH |
| M-08 | Semantic graph serialization + node ID şeması | MindMap'in kalıcı veri modeli | HIGH |
| M-09 | Text-mode MindMap interaction (terminal) | Claude Code'da tıklama yok | HIGH |
| M-10 | Knowledge Debt lifecycle (açılış, kapanış, link) | Debt kaybolmaması | MEDIUM |
| M-11 | Personal library konumu ve pointer formatı | Projeler arası Concept Home | HIGH (karar) |
| M-12 | Human Sync template + çoklu unit kuralı | Scope > 1 unit | MEDIUM |
| M-13 | Decision Record template (ADR + DSA DR) | Kaynakta format var, template yok | MEDIUM |
| M-14 | Canonical vocabulary eşleme tablosu | C-08 | MEDIUM |
| M-15 | Incremental map / graph update kuralı | Delta instead of rewrite | MEDIUM |
| M-16 | Skill-level integrity check (ledger/state tutarlılığı) | Ledger bozulması | LOW |
| M-17 | `LEARNING_CONFIG.md` + template | Library konumu ve work unit source proje düzeyinde ayarlanır (Q2, Q5) | HIGH |

---

# 18. KEEP / MOVE / MERGE / REWRITE / REMOVE / MISSING Matrix

| Bileşen | Sınıf | Gerekçe |
|---|---|---|
| Ana amaç, felsefe, SD primary axis (MASTER §1–§4) | KEEP | Temel prensip. SKILL.md'de kısa özet. |
| SD Experience Map formatı (§5) | MOVE | → template + 06 |
| DSA rolü, DSA döngüsü (§6–§7) | MOVE | → 04 (DSA L3 odağı) + 06 |
| DSA Pattern Map (§8) | MOVE | → universal iskelet olarak 06 |
| DSA Experience Map (§9) | MOVE | → template |
| SD × DSA, DS × SD × DSA (§10–§11) | KEEP | Arşivde kalır. Runtime gerektirmez. |
| Project selection, difficulty (§12–§13) | KEEP | Arşivde. `/learning` kapsamı dışında. |
| AI roles (§14) | MERGE | Compressor → 03, Teacher → 04 |
| Cognitive Throughput Gap (§15) | KEEP | SKILL.md özetinde gerekçe |
| Human Synchronization + output (§16–§17) | REWRITE | Mantık aynen. Timing manuel. Çoklu unit. |
| Knowledge Priority (§18) | KEEP | Aynen → 03 |
| Knowledge Debt (§19) | REWRITE | Lifecycle + saklama eklenir |
| ULA role + sequence (§20) | KEEP | → 04 |
| Horizontal Map, recursive zoom, progressive expansion, node, edge, semantic graph (§21–§26) | REWRITE | → 05. Kavram aynen; operasyonel parçalar eklenir. |
| L1–L4, Confusions (§27–§31) | MERGE | ULA spec ile birleşik canonical ad |
| One Concept — One Home, Concept Home vs Experience (§32–§33) | KEEP | → 06. Konum kararı Q2. |
| Reference Layer (§34) | MERGE | SPEC §12 ile aynı kural |
| Zoom / Depth Control (§35) | REWRITE | Light/Full seçim kuralının temeli |
| Learning Event (§36) | REWRITE | Mantık aynen; otomatik tespit → /learning içi |
| Jira lifecycle (§37) | REWRITE | TECHNICAL DONE ≠ LEARNING COVERAGE |
| ADR, DSA DR (§38–§39) | MOVE | → DECISION_RECORD template |
| Retrieval (§40) | MERGE | SPEC §24 ile |
| AI dependency control, Human Review (§41–§42) | REWRITE | /learning içi checkpoint; milestone review = custom scope |
| Meta-work boundary (§43) | KEEP | Skill tasarım kısıtı |
| Success criteria, long-term outputs (§44–§45) | KEEP | Arşiv; §45 üç katmanlı state'in kaynağı |
| Interactive Atlas, default visual (§46–§47) | KEEP | Vizyon olarak. Implementation ertelenir. |
| Production pipeline (§48) | REWRITE | → 01 run loop |
| Layer roles, default ULA prompt, final target, principle (§49–§52) | KEEP | §50 → 04'e kaynak |
| ULA spec v1.0 | KEEP | Değiştirilmez |
| Learning Architect | KEEP | Değiştirilmez |
| Content Builder | KEEP | Değiştirilmez |
| Learning Auditor | KEEP | Değiştirilmez |
| ULA templates (4) | MOVE | → ula/templates |
| ULA README | MERGE | Workflow → 04 |
| ULA CHANGELOG | MOVE | Runtime dışı |
| HSMM examples | MOVE | → ula/examples, otomatik yüklenmez |
| SQ-01 bozuk LaTeX | REWRITE (karar Q9) | Kopyada düzeltme önerilir; kaynak dokunulmaz |
| SQ-02 CHANGELOG chat sarmalı | REMOVE (kopyada; karar Q9) | Neden: içerik değil, konuşma artığı |
| SQ-03 Spec sonu konuşma paragrafı | REMOVE (kopyada; karar Q9) | Neden: kural değil; "sonraki adım" notudur ve zaten gerçekleşmiştir (üç prompt mevcut) |
| `skills/learning/state/` konumu | MOVE | → docs/learning/state |
| `07_AUDIT_PROTOCOL.md` adı/kapsamı | REWRITE | Yalnız skill-level integrity; içerik audit'i → LEARNING_AUDITOR |
| Coverage Protocol, Ledger, State, Queue, scope menüsü | MISSING | Bölüm 7 |
| Graph schema, node ID, text interaction | MISSING | Bölüm 5.1 |
| Light/Full seçim kuralı | MISSING | Bölüm 13 |
| HUMAN_SYNC / DECISION_RECORD / LEARNING_STATE / LEARNING_QUEUE templates | MISSING | Bölüm 15.3 |

REMOVE notu: Hiçbir öğrenme prensibi REMOVE edilmedi. Yalnız kaynak artığı metinler, kopyalanacak sürümde kaldırılmak üzere önerildi.

---

# 19. Recommended Final Architecture

**Durum: APPROVED** (kullanıcı onayı, `LEARNING_CONFIG` eklemesi ile).

```text
<project>/
├── .claude/
│   └── skills/
│       └── learning/                         UNIVERSAL — runtime'da read-only
│           ├── SKILL.md                      kısa: invocation kuralı, run loop, load map
│           ├── references/
│           │   ├── 00_MASTER_SYSTEM_SPEC.md  verbatim arşiv — OTOMATİK YÜKLENMEZ
│           │   ├── 01_OPERATIONAL_CORE.md    /learning run loop (MASTER §48 manuel sürüm)
│           │   ├── 02_COVERAGE_PROTOCOL.md   work unit ID, ledger, gap, scope menü
│           │   ├── 03_HUMAN_SYNC_PROTOCOL.md HS + Knowledge Priority + Learning Event + Debt
│           │   ├── 04_ULA_PROTOCOL.md        Light ULA + Full ULA routing + vocabulary eşleme
│           │   ├── 05_MINDMAP_PROTOCOL.md    graph schema, edge sözlüğü, text rendering
│           │   ├── 06_KNOWLEDGE_PERSISTENCE.md  3 katmanlı state, Concept Home, Experience
│           │   └── 07_INTEGRITY_CHECKS.md    yalnız ledger/state/map tutarlılığı
│           ├── ula/                          ULA v1.0 — DEĞİŞTİRİLMEZ
│           │   ├── ULA_SPECIFICATION.md
│           │   ├── LEARNING_ARCHITECT.md
│           │   ├── CONTENT_BUILDER.md
│           │   ├── LEARNING_AUDITOR.md
│           │   ├── templates/                4 ULA template
│           │   └── examples/HSMM_PILOT/      OTOMATİK YÜKLENMEZ
│           └── templates/
│               ├── LEARNING_CONFIG_TEMPLATE.md
│               ├── LEARNING_PASS_TEMPLATE.md
│               ├── HUMAN_SYNC_TEMPLATE.md
│               ├── CONCEPT_HOME_TEMPLATE.md
│               ├── EXPERIENCE_NOTE_TEMPLATE.md
│               ├── DECISION_RECORD_TEMPLATE.md
│               ├── KNOWLEDGE_MAP_TEMPLATE.md
│               ├── COVERAGE_LEDGER_TEMPLATE.md
│               ├── LEARNING_STATE_TEMPLATE.md
│               └── LEARNING_QUEUE_TEMPLATE.md
│
└── docs/
    └── learning/                             PROJECT-SPECIFIC STATE
        ├── state/
        │   ├── LEARNING_CONFIG.md            personal_library_path, work_unit_source
        │   ├── LEARNING_STATE.md
        │   ├── COVERAGE_LEDGER.md
        │   └── LEARNING_QUEUE.md             Deferred units + Knowledge Debt
        ├── passes/
        ├── experiences/                      Experience Notes + Decision Records
        ├── maps/
        ├── concepts/                         pointer veya temporary local concept (Hybrid)
        └── audits/

<PERSONAL LIBRARY — konum: LEARNING_CONFIG.md → personal_library_path>
                                              PERSONAL (cross-project) STATE
├── concepts/                                 Concept Home'lar
├── maps/                                     global semantic graph
└── experience-maps/                          SD / DSA birikimi
```

Yükleme kuralı (load map):

| `/learning` adımı | Yüklenen dosya |
|---|---|
| Başlangıç | `SKILL.md` + `docs/learning/state/LEARNING_CONFIG.md` + `LEARNING_STATE.md` |
| Scope resolution | `02_COVERAGE_PROTOCOL.md` + `COVERAGE_LEDGER.md` |
| Human Sync | `03_HUMAN_SYNC_PROTOCOL.md` |
| Light ULA | `04_ULA_PROTOCOL.md` (+ gerekirse `05`) |
| Full ULA | Sırayla: `LEARNING_ARCHITECT` → (onay) → `CONTENT_BUILDER` → `LEARNING_AUDITOR` |
| Persist | `06_KNOWLEDGE_PERSISTENCE.md` + ilgili template |
| Asla otomatik değil | `00_MASTER_SYSTEM_SPEC.md`, `ula/examples/`, `ULA_SPECIFICATION.md` (Full ULA rolleri kendi kurallarını taşır) |

Tekrar önleme kuralı: `01`–`07` dosyaları kaynak metni kopyalamaz. Yalnız operasyonel kuralı ve kaynağa pointer'ı içerir.

---

# 20. Risks

| ID | Risk | Etki | Azaltma |
|---|---|---|---|
| R-01 | Ledger ile gerçek proje durumu ayrışır (rebase, yeniden numaralandırma) | Yanlış gap | Kaynak tipi + ID + label birlikte saklanır; çelişkide kullanıcıya sor |
| R-02 | Skill dosyaları kaynak metni tekrar eder | Token israfı, sürüm kayması | Pointer kuralı; 07 integrity check |
| R-03 | Full ULA gereksiz yere seçilir | Yüksek token maliyeti | Zoom 3 kriterleri + kullanıcı onayı |
| R-04 | Meta-work projeyi aşar (MASTER §43) | Kullanım bırakılır | Aşama 2'de HTML yok; minimum dosya seti |
| R-05 | Concept Home konumu yanlış seçilir | Projeler arası tekrar veya bulunamayan bilgi | Q2 kararı Aşama 2 öncesi |
| R-06 | State skill klasörüne yazılır | Portability bozulur; kişisel veri yayınlanır | State yalnız docs/learning/ |
| R-07 | Model skill'i otomatik çağırır | Learning OFF ihlali | `disable-model-invocation` (doğrulanacak) |
| R-08 | Bozuk LaTeX örnekleri Builder'a kötü örnek olur | Hatalı formül çıktısı | Q9 kararı; örnekler otomatik yüklenmez |
| R-09 | Çok uzun scope (ör. 50 commit) tek pass'te işlenir | Context taşması, yüzeysel öğrenme | Scope menüsünde boyut uyarısı; HS önce sıkıştırır |
| R-10 | Terminoloji kayması skill dosyalarına taşınır | Tutarsız çıktı | Q1 + eşleme tablosu |

---

# 21. Resolved Decisions (Q1–Q12)

Bütün sorular kullanıcı kararı ile kapatıldı. Durum: **RESOLVED**.

## Q1 — Source precedence — RESOLVED

Kural:

> **Domain ownership determines authority.**

Bir kaynak diğerini global olarak override etmez.

| Domain | Authoritative kaynak | Kapsam |
|---|---|---|
| Project-learning | `StudySystem_WithAI.txt` | project-driven learning, System Design primary learning axis, Human Synchronization, Knowledge Priority, Learning Event, Experience Map, Concept Home prensibi, Jira / task lifecycle mantığı, DSA problem-pattern yaklaşımı, overall learning lifecycle |
| ULA | `ULA_SPECIFICATION_v1.0.md` + ULA rol dosyaları | learning architecture, L0–L4 yapısı, teaching sequence, Architect, Builder, Auditor, freeze rules, content generation rules, learning audit rules, ULA terminology |

Terminoloji: ULA vocabulary canonical'dır. Master terimleri alias olarak korunur.

| Canonical (ULA) | Alias (Master) |
|---|---|
| L0 — Map | Whole / Map |
| L1 — Simple Explanation | Simple Meaning |
| L2 — Mechanism | Mechanism |
| L3 — Theory | Theory |
| L4 — Math / Formalism | Formalism / Math |
| Boundary Statements (`A ≠ B`) | Confusions / Confusion Boundaries |
| Retrieval Mode | Retrieval |
| R — Reference | Reference Layer |
| Quick View / Standard Study / Deep Study | Zoom 1 / Zoom 2 / Zoom 3 |

Bu karar C-08'i kapatır.

## Q2 — Concept Home location — RESOLVED

Karar: **HYBRID.** Üç state katmanı:

```text
UNIVERSAL SKILL LOGIC
PERSONAL CROSS-PROJECT STATE
PROJECT-SPECIFIC STATE
```

- Gerçek Concept Home, Personal Technical Library içinde yaşar.
- Library konumu skill içinde hard-code edilmez. `LEARNING_CONFIG.md → personal_library_path` ile tanımlanır.
- Projede yalnız: Concept ID, Concept Home pointer, Project Appearance, project-specific delta, Experience Note.
- Library yapılandırılmadıysa skill hata vermez. Concept geçici olarak project-local tutulur. Sonra library'ye promote edilir.

Bu karar C-06'yı kapatır.

## Q3 — Project state location — RESOLVED

Karar: `docs/learning/state/`.

```text
.claude/skills/learning/   → universal engine, portable, runtime'da read-only
docs/learning/state/       → project-specific state
```

State dosyaları: `LEARNING_CONFIG.md`, `LEARNING_STATE.md`, `COVERAGE_LEDGER.md`, `LEARNING_QUEUE.md`.

Skill klasöründe project state tutulmaz. Bu karar C-05'i kapatır.

## Q4 — Learning OFF davranışı — RESOLVED

Karar: Learning OFF iken passive learning tracking **yoktur**.

Normal çalışma sırasında Claude:

- learning event kaydetmez,
- queue güncellemez,
- coverage ledger güncellemez,
- Human Synchronization çalıştırmaz,
- ULA çalıştırmaz,
- learning checkpoint sormaz.

Learning engine yalnız `/learning` çağrısında aktif olur. Work unit history bu anda mevcut project evidence üzerinden reconstruct edilir. Bu karar C-01'i kapatır.

## Q5 — Work unit source — RESOLVED

Tek bir source global olarak hard-code edilmez. Universal priority Bölüm 8.1A'dadır:

```text
1. Explicit user scope
2. Project-configured work unit source
3. Jira / issue tracker, erişilebiliyorsa
4. Persistent task / phase document
5. Git commit / commit range
6. Other stable identifier
7. Ambiguous → ask user
```

Default: `work_unit_source: auto`. Override: `jira`, `git`, `phase-doc` veya ileride desteklenen source.

- File modification time coverage için authoritative source değildir.
- Chat context tek başına persistent coverage source değildir.

## Coverage model — APPROVED

Bölüm 7'deki set-based ledger modeli onaylandı.

| Durum | Sonraki `/learning` gap listesinde |
|---|---|
| UNCOVERED | Görünür |
| COVERED | Görünmez |
| PARTIAL | Görünür (yalnız açık learning event'ler) |
| DEFERRED | Görünür |
| SKIPPED_BY_USER | Varsayılan görünmez; `show skipped` ile görünür |
| NOT_LEARNING_RELEVANT | Görünmez |

Kurallar:

- `DEFERRED ≠ SKIPPED_BY_USER`.
- `NOT_LEARNING_RELEVANT` yalnız Knowledge Priority sonucu IMPLEMENTATION DETAIL olan work unit için kullanılır.
- Tek bir `last covered boundary` coverage gerçeği olarak kullanılmaz. Ledger work-unit bazlı ve set-based'dir.

Bu karar C-04'ü ve C-07'yi kapatır (TECHNICAL DONE ≠ LEARNING COVERAGE).

## LEARNING_CONFIG — APPROVED (mimari karar)

| Dosya | Katman |
|---|---|
| `docs/learning/state/LEARNING_CONFIG.md` | PROJECT-SPECIFIC STATE |
| `.claude/skills/learning/templates/LEARNING_CONFIG_TEMPLATE.md` | UNIVERSAL SKILL LOGIC |

Config en az şu alanları taşıyabilir:

```text
personal_library_path
work_unit_source
```

Gerçek config Phase 1 içinde implement edilmedi.

## Q6 — Outside Knowledge — RESOLVED

Karar: `ALLOWED WITH LABELS`.

- Project facts için project sources authoritative'dir.
- General theory gerektiğinde kullanılabilir.
- Source-derived bilgi ile outside knowledge açık biçimde ayrılır.

Bu karar C-09'u kapatır.

## Q7 — Dil — RESOLVED

Bütün user-facing learning content:

```text
Türkçe açıklama
+ İngilizce canonical technical term
+ ASD-STE100 yaklaşımı
```

## Q8 — HTML Atlas — RESOLVED

Phase 2 kapsamında HTML atlas yoktur. Sıra:

```text
semantic graph → Markdown / text view → terminal-friendly MindMap
```

HTML daha sonraki aşamada ve yalnız açık kullanıcı isteğiyle değerlendirilir. Bu karar C-03'ü ve C-10'u kapatır.

## Q9 — Source quality problems — RESOLVED

- Original source dosyalarına dokunulmaz.
- Skill içine kopyalanan canonical sürümlerde: bozuk LaTeX escape'leri düzeltilir (SQ-01), chat artifact metinleri kaldırılır (SQ-02), conversational metinler kaldırılır (SQ-03).
- Her düzeltme changelog veya migration note içinde kaydedilir.
- Bu karar sonraki aşamalar içindir. Phase 1 içinde düzeltme yapılmadı.

## Q10 — Invocation — RESOLVED

Ana giriş: `/learning`. Optional argument desteklenebilir:

```text
/learning
/learning latest
/learning pending
/learning catch-up
/learning INC-44
```

Ayrı skill komutları oluşturulmaz.

## Q11 — SKIPPED_BY_USER — RESOLVED

Varsayılan gap listesinde gösterilmez. Kullanıcı isterse (`show skipped`) tekrar görüntülenir.

## Q12 — Knowledge Debt — RESOLVED

- Knowledge Debt project context içinde doğar.
- Concept daha sonra Concept Home kazanırsa personal library ile bağlanır.
- İki kavram ayrıdır:

```text
KNOWLEDGE DEBT       → ertelenmiş kavram
DEFERRED WORK UNIT   → ertelenmiş proje işi
```

## Conflict kapanış özeti

| Conflict | Kapatan karar |
|---|---|
| C-01 Automatic vs manual | Q4 |
| C-02 Full ULA vs token-efficient | Bölüm 13.3 eşlemesi (Light default, Full kriterle) |
| C-03 Linear note vs MindMap | Q8 |
| C-04 One-time pass vs persistent coverage | Coverage model |
| C-05 Universal vs project state | Q3 |
| C-06 Personal library vs project-local | Q2 |
| C-07 DONE semantiği | Coverage model |
| C-08 Terminology drift | Q1 |
| C-09 Knowledge policy | Q6 |
| C-10 Atlas vs meta-work | Q8 |

Açık source conflict kalmadı.

---

# 22. Phase 2 Entry Criteria

```text
[x] Authoritative source identified
      Master: StudySystem_WithAI.txt. ULA: ULA_SPECIFICATION_v1.0.md + rol dosyaları.
[x] Source precedence rule confirmed                      → Q1 (domain ownership)
[x] ULA roles identified
      Architect, Builder, Auditor — Purpose/Input/Operation/Output/Boundary çıkarıldı.
[x] Automatic behaviors catalogued (A1–A12)
[x] Manual invocation rule confirmed by user              → Q4, Q10
[x] Coverage model drafted
[x] Coverage model reviewed by user                       → Coverage model, Q5, Q11
[x] Universal vs personal vs project state separated      → Q2, Q3
[x] Concept Home location decided                         → Q2 (HYBRID)
[x] Project state location confirmed                      → Q3 (docs/learning/state/)
[x] LEARNING_CONFIG added to architecture                 → Bölüm 19
[x] MindMap missing pieces identified (Bölüm 5.1)
[x] Target architecture reviewed (Bölüm 15, 19)
[x] Revised target architecture approved by user          → Bölüm 19 APPROVED
[x] No unresolved source conflict                         → C-01..C-10 kapalı
[x] Source quality issues logged (SQ-01..05)              → Q9 ile ele alınacak
```

**Sonuç:**

```text
PHASE 1 STATUS: FROZEN / PASS
PHASE 2 STATUS: READY
```

Bu doküman frozen'dır. Değişiklik ancak açık kullanıcı kararı ile yapılır.
