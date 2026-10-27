---
name: learning
description: Run the project's manual System Design + Problem-Pattern DSA + ULA learning workflow and maintain project learning coverage.
disable-model-invocation: true
user-invocable: true
argument-hint: "[latest | pending | catch-up | show skipped | resume | new | abandon <pass-id> | map [<node-id> [L1-L4] | debt | sync] | concept <concept-id> | library | experiences | debt | <work-unit-id>]"
---

# /learning — Entry Router

Bu dosya `/learning` için tek giriş noktasıdır.
Ayrıntılı kurallar burada değildir. Her adım ilgili reference dosyasına route edilir.

Argüman: `$ARGUMENTS`

---

## 1. Manual only

```text
Normal project work → Learning OFF
/learning           → Learning ON
```

- Bu skill yalnız kullanıcı `/learning` yazdığında çalışır.
- Model bu skill'i kendisi çağıramaz (`disable-model-invocation: true`).
- Learning OFF iken passive tracking yoktur. Learning event, queue, coverage ledger, Human Synchronization, ULA ve checkpoint sorusu yoktur.
- Work unit history `/learning` anında project evidence üzerinden reconstruct edilir.

## 2. Primary learning axis

```text
Real Data Science / ML project
↓
System Design = PRIMARY ENGINEERING LEARNING AXIS
↓
DSA only when computationally relevant
↓
AI-assisted implementation
↓
Human Synchronization
↓
ULA only when a knowledge gap exists
```

## 3. Authority

Domain ownership determines authority.

| Domain | Authoritative kaynak |
|---|---|
| Project-learning lifecycle | `references/00_MASTER_SYSTEM_SPEC.md` |
| Learning architecture, L0–L4, ULA roles, ULA terminology | `ula/ULA_SPECIFICATION.md` + `ula/` rol dosyaları |

ULA terimleri canonical'dır. Master terimleri alias olarak kabul edilir (ör. `L1 — Simple Explanation`, alias: Simple Meaning).

## 4. Language

User-facing learning content:

- Türkçe açıklama,
- İngilizce canonical technical term,
- ASD-STE100 yaklaşımı: kısa cümle, bir cümlede bir fikir, sabit terim.

Outside knowledge: `ALLOWED WITH LABELS`. Project facts için project sources authoritative'dir. Source-derived bilgi ile outside knowledge ayrı etiketlenir.

## 5. State layers

| Katman | Konum | Yazma |
|---|---|---|
| UNIVERSAL SKILL LOGIC | Bu skill klasörü | Runtime'da read-only kabul edilir. Buraya state yazma. |
| PROJECT-SPECIFIC STATE | `docs/learning/` (project root'a göre) | `/learning` yazar |
| PERSONAL CROSS-PROJECT STATE | `LEARNING_CONFIG.md → personal_library_path` | Yalnız yapılandırılmışsa |

`personal_library_path` hard-code edilmez. Yapılandırılmadıysa hata verme. Kullanıcıya sor: yapılandır / `LOCAL_TEMPORARY` / ertele (`references/06_KNOWLEDGE_PERSISTENCE.md` §2.2).

## 6. Arguments

| Argüman | Anlam |
|---|---|
| (boş) | Tam router. Gap varsa scope sor. |
| `latest` | Scope = son work unit |
| `pending` | Scope = DEFERRED / PARTIAL queue |
| `catch-up` | Scope = bütün açık gap |
| `show skipped` | SKIPPED_BY_USER birimlerini de göster |
| `<work-unit-id>` | Scope = bu work unit (ör. issue key, commit, phase step) |
| `resume` | Active pass'e devam et (`04` §10.2) |
| `new` | Active pass varken yeni pass başlat; overlap → CONFLICT (`04` §10.3) |
| `abandon <pass-id>` | Pass'i `ABANDONED` yap; ledger açık kalır (`04` §10.4) |
| `map` | Root Knowledge Map (`05` §12). Coverage çalışmaz. |
| `map <node-id>` | Recursive local zoom (`05` §13) |
| `map <node-id> L1`…`L4` | Depth view; yalnız mevcut seviye (`05` §14) |
| `map debt` | `DEBT` node listesi |
| `map sync` | `COMPLETE` pass'lerde bekleyen map sync (`05` §8) |
| `concept <concept-id>` | Pointer + Concept Home (`06` §24) |
| `library` | Personal library status / index; promotion önerisi (`06` §24) |
| `experiences` | Experience Note listesi (`06` §24) |
| `debt` | `OPEN` Knowledge Debt (`06` §24) |

Argüman belirsizse tahmin etme. Kullanıcıya sor.

## 7. Run router

| # | Adım | Reference | Durum |
|---|---|---|---|
| 1 | LOAD PROJECT CONFIG / STATE | `references/01_OPERATIONAL_CORE.md` §1 | IMPLEMENTED |
| 2 | DISCOVER CURRENT WORK UNITS | `references/02_COVERAGE_PROTOCOL.md` §3–§6 | IMPLEMENTED |
| 3 | COVERAGE CHECK | `references/02_COVERAGE_PROTOCOL.md` §6 | IMPLEMENTED |
| 4 | SCOPE RESOLUTION | `references/02_COVERAGE_PROTOCOL.md` §8 | IMPLEMENTED |
| 5 | HUMAN SYNCHRONIZATION | `references/03_HUMAN_SYNC_PROTOCOL.md` §3–§7 | IMPLEMENTED |
| 6 | LEARNING EVENT EXTRACTION | `references/03_HUMAN_SYNC_PROTOCOL.md` §8–§10 | IMPLEMENTED |
| 7 | KNOWLEDGE PRIORITY + EVENT DISPOSITION + HANDOFF | `references/03_HUMAN_SYNC_PROTOCOL.md` §11–§17 | IMPLEMENTED |
| 8 | ULA ROUTING + EARLY COMPLETION CHECK | `references/04_ULA_PROTOCOL.md` §3–§5 | IMPLEMENTED |
| 9 | LIGHT ULA / FULL ULA (retrieval prompt dahil) | `references/04_ULA_PROTOCOL.md` §6–§8 | IMPLEMENTED |
| 10 | COVERAGE COMPLETION COMMIT (unit bazında) | `references/04_ULA_PROTOCOL.md` §11 + `references/02_COVERAGE_PROTOCOL.md` §9–§10 | IMPLEMENTED |
| 11 | MAP SYNC: SEMANTIC GRAPH + HORIZONTAL MAP | `references/05_MINDMAP_PROTOCOL.md` §6–§12 | IMPLEMENTED (yalnız pass COMPLETE ise; completion'ı geri almaz) |
| 12 | KNOWLEDGE PERSISTENCE | `references/06_KNOWLEDGE_PERSISTENCE.md` §5–§22 | IMPLEMENTED (post-completion; completion'ı geri almaz) |
| 13 | FINAL INTEGRITY → DONE | `references/07_INTEGRITY_CHECKS.md` §C, §E, §U, §M, §P | IMPLEMENTED (§L henüz yok; guard değildir) |

Startup'ta active pass varsa önce resume / new / abandon sorulur (`references/04_ULA_PROTOCOL.md` §10). Resume, pass'in `current_stage` adımından devam eder.

`map ...` argümanları run loop'u çalıştırmaz. Doğrudan `references/05_MINDMAP_PROTOCOL.md` §15'e gider.
`concept`, `library`, `experiences`, `debt` argümanları run loop'u çalıştırmaz. Doğrudan `references/06_KNOWLEDGE_PERSISTENCE.md` §24'e gider.

Genel akış ve dur kuralları: `references/01_OPERATIONAL_CORE.md`.

**Skeleton kuralı:** Bir adımın reference dosyası o adım için `NOT IMPLEMENTED YET` diyorsa:

1. O adımın davranışını uydurma.
2. Selected scope'u göster. Kullanıcıya hangi adımın henüz implement edilmediğini bildir.
3. Bu adımda ve sonraki adımlarda project state yazma. Completion Commit yapma.
4. Dur.

Adım 1–13 implement edilmiştir. Skeleton kuralı bugün run loop'ta hiçbir adımda tetiklenmez. Ledger yalnız Discovery, Scope ve Completion Commit ile yazılır (`02_COVERAGE_PROTOCOL.md` §10). Retrieval yalnız ULA artifact içindeki prompt'tur; interactive retrieval session yoktur. Bugünkü akış:

```text
Coverage              → IMPLEMENTED
Human Sync            → IMPLEMENTED
ULA                   → IMPLEMENTED
Completion            → IMPLEMENTED
MindMap               → IMPLEMENTED
Knowledge Persistence → IMPLEMENTED
FINAL INTEGRITY       → DONE
```

## 8. Load map

Token kuralı: Yalnız aktif adımın dosyasını oku. Bir dosyayı aynı çağrıda tekrar okuma.

| Durum | Oku |
|---|---|
| Startup | Bu dosya + `docs/learning/state/LEARNING_CONFIG.md` + `docs/learning/state/LEARNING_STATE.md` |
| Coverage | `references/01_OPERATIONAL_CORE.md` + `references/02_COVERAGE_PROTOCOL.md` + `references/07_INTEGRITY_CHECKS.md` §C + `docs/learning/state/COVERAGE_LEDGER.md` |
| Human Sync | `references/03_HUMAN_SYNC_PROTOCOL.md` + `templates/LEARNING_PASS_TEMPLATE.md` + `templates/HUMAN_SYNC_TEMPLATE.md` + `references/07_INTEGRITY_CHECKS.md` §E + `docs/learning/state/LEARNING_QUEUE.md` §B |
| ULA Routing / Completion | `references/04_ULA_PROTOCOL.md` + pass `LEARNING_PASS.md` + `references/07_INTEGRITY_CHECKS.md` §U |
| Light ULA | `references/04_ULA_PROTOCOL.md` + `templates/LIGHT_ULA_TEMPLATE.md` + gerekli project evidence |
| Full ULA | Sırayla, aynı anda değil: `ula/LEARNING_ARCHITECT.md` → user review → `ula/CONTENT_BUILDER.md` → `ula/LEARNING_AUDITOR.md`. Stage başına dosyalar: `references/04_ULA_PROTOCOL.md` §12 |
| Map sync / `map ...` | `references/05_MINDMAP_PROTOCOL.md` + `docs/learning/maps/SEMANTIC_GRAPH.md` (+ `HORIZONTAL_MAP.md`) + `references/07_INTEGRITY_CHECKS.md` §M. Depth view: yalnız ilgili artifact bölümü. |
| Persistence | `references/06_KNOWLEDGE_PERSISTENCE.md` + `references/07_INTEGRITY_CHECKS.md` §P + registry + yalnız candidate Concept Home + yalnız ilgili Experience Map + gerekli `templates/` dosyası (`06` §25) |
| `concept` / `library` / `experiences` / `debt` | `06` §24–§25 içindeki dosyalar. Bütün personal library yüklenmez. |
| Integrity | `references/07_INTEGRITY_CHECKS.md` |

**Default olarak ASLA otomatik yükleme:**

- `references/00_MASTER_SYSTEM_SPEC.md`
- `ula/examples/`
- Full ULA source set (spec + üç rol + `ula/templates/` birlikte)
- Personal Technical Library (normal project work sırasında hiç; persistence sırasında yalnız `06` §25 kadar)

Master yalnız ambiguity, audit, maintenance veya explicit deep verification gerektiğinde okunur.

## 9. Project-state initialization

Startup'ta `docs/learning/state/` veya içindeki dosyalardan biri yoksa proje initialize edilmemiştir. Ayrıntı: `references/02_COVERAGE_PROTOCOL.md` §11.

1. Kullanıcıya initialization gerektiğini bildir.
2. Kullanıcı onayı olmadan dosya oluşturma.
3. Onay varsa yalnız eksik dosyaları `templates/` üzerinden oluştur. Mevcut dosyayı overwrite etme.

```text
docs/learning/
├── state/
│   ├── LEARNING_CONFIG.md     ← templates/LEARNING_CONFIG_TEMPLATE.md
│   ├── LEARNING_STATE.md      ← templates/LEARNING_STATE_TEMPLATE.md
│   ├── COVERAGE_LEDGER.md     ← templates/COVERAGE_LEDGER_TEMPLATE.md
│   └── LEARNING_QUEUE.md      ← templates/LEARNING_QUEUE_TEMPLATE.md
├── passes/
├── experiences/
├── concepts/
├── maps/
└── audits/
```

Config default değerleri:

```text
project_id            = UNCONFIGURED   (06 §2.1)
project_name          = UNCONFIGURED
personal_library_path = UNCONFIGURED
work_unit_source      = auto
```

Authority: `COVERAGE_LEDGER.md` coverage truth taşır. `LEARNING_STATE.md` ve `LEARNING_QUEUE.md` §A ledger'dan türetilir ve yeniden üretilebilir.

Development repository kuralı: Bu skill'in kendi geliştirme repository'sinde project state oluşturma.

## 10. Must not

- Normal project work sırasında çalışma.
- Skill klasörüne project state yazma.
- File modification time, directory listing order, filename sort veya persistent evidence olmayan çıkarım ile coverage kararı verme.
- Chat context'i tek başına persistent coverage source kabul etme.
- Tek bir `last covered boundary` değerini coverage gerçeği kabul etme.
- Her teknik ayrıntıyı öğretme. Yalnız MUST UNDERSTAND + knowledge gap olan event ULA adayı olur.
- Kullanıcı istemeden HTML üretme.
