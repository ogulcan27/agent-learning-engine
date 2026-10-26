---
name: learning
description: Run the project's manual System Design + Problem-Pattern DSA + ULA learning workflow and maintain project learning coverage.
disable-model-invocation: true
user-invocable: true
argument-hint: "[latest | pending | catch-up | show skipped | <work-unit-id>]"
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

`personal_library_path` yapılandırılmadıysa hata verme. Concept'i geçici olarak `docs/learning/concepts/` içinde tut.

## 6. Arguments

| Argüman | Anlam |
|---|---|
| (boş) | Tam router. Gap varsa scope sor. |
| `latest` | Scope = son work unit |
| `pending` | Scope = DEFERRED / PARTIAL queue |
| `catch-up` | Scope = bütün açık gap |
| `show skipped` | SKIPPED_BY_USER birimlerini de göster |
| `<work-unit-id>` | Scope = bu work unit (ör. issue key, commit, phase step) |

Argüman belirsizse tahmin etme. Kullanıcıya sor.

## 7. Run router

| # | Adım | Reference |
|---|---|---|
| 1 | LOAD PROJECT CONFIG / STATE | Bölüm 9 |
| 2 | DISCOVER CURRENT WORK UNITS | `references/02_COVERAGE_PROTOCOL.md` |
| 3 | COVERAGE CHECK | `references/02_COVERAGE_PROTOCOL.md` |
| 4 | SCOPE RESOLUTION | `references/02_COVERAGE_PROTOCOL.md` |
| 5 | HUMAN SYNCHRONIZATION | `references/03_HUMAN_SYNC_PROTOCOL.md` |
| 6 | KNOWLEDGE PRIORITY | `references/03_HUMAN_SYNC_PROTOCOL.md` |
| 7 | LEARNING EVENT EXTRACTION | `references/03_HUMAN_SYNC_PROTOCOL.md` |
| 8 | LIGHT or FULL ULA | `references/04_ULA_PROTOCOL.md` |
| 9 | MINDMAP / SEMANTIC GRAPH UPDATE | `references/05_MINDMAP_PROTOCOL.md` |
| 10 | KNOWLEDGE PERSISTENCE | `references/06_KNOWLEDGE_PERSISTENCE.md` |
| 11 | RETRIEVAL | `references/04_ULA_PROTOCOL.md` |
| 12 | COVERAGE UPDATE | `references/02_COVERAGE_PROTOCOL.md` |
| 13 | INTEGRITY CHECK | `references/07_INTEGRITY_CHECKS.md` |

Genel akış kuralları: `references/01_OPERATIONAL_CORE.md`.

**Skeleton kuralı:** Bir adımın reference veya template dosyası `Status: NOT IMPLEMENTED YET` içeriyorsa:

1. O adımın davranışını uydurma.
2. Kullanıcıya hangi adımın henüz implement edilmediğini bildir.
3. Bu adımda ve sonraki adımlarda project state yazma.
4. Dur.

## 8. Load map

Token kuralı: Yalnız aktif adımın dosyasını oku. Bir dosyayı aynı çağrıda tekrar okuma.

| Durum | Oku |
|---|---|
| Startup | Bu dosya + `docs/learning/state/LEARNING_CONFIG.md` + `docs/learning/state/LEARNING_STATE.md` |
| Coverage | `references/02_COVERAGE_PROTOCOL.md` + `docs/learning/state/COVERAGE_LEDGER.md` |
| Human Sync | `references/03_HUMAN_SYNC_PROTOCOL.md` |
| Light ULA | `references/04_ULA_PROTOCOL.md` (gerekirse `references/05_MINDMAP_PROTOCOL.md`) |
| Full ULA | Sırayla, aynı anda değil: `ula/LEARNING_ARCHITECT.md` → user review → `ula/CONTENT_BUILDER.md` → `ula/LEARNING_AUDITOR.md` |
| Persistence | `references/06_KNOWLEDGE_PERSISTENCE.md` + gerekli `templates/` dosyası |
| Integrity | `references/07_INTEGRITY_CHECKS.md` |

**Default olarak ASLA otomatik yükleme:**

- `references/00_MASTER_SYSTEM_SPEC.md`
- `ula/examples/`
- Full ULA source set (spec + üç rol + `ula/templates/` birlikte)

Master yalnız ambiguity, audit, maintenance veya explicit deep verification gerektiğinde okunur.

## 9. Project-state initialization

Startup'ta `docs/learning/state/` yoksa proje initialize edilmemiştir.

1. Kullanıcıya initialization gerektiğini bildir.
2. Kullanıcı onayı olmadan dosya oluşturma.
3. Onay varsa şu yapıyı `templates/` üzerinden oluştur:

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
personal_library_path = UNCONFIGURED
work_unit_source      = auto
```

Skeleton kuralı burada da geçerlidir. Template `NOT IMPLEMENTED YET` ise initialization yapma.

## 10. Must not

- Normal project work sırasında çalışma.
- Skill klasörüne project state yazma.
- File modification time ile coverage kararı verme.
- Chat context'i tek başına persistent coverage source kabul etme.
- Tek bir `last covered boundary` değerini coverage gerçeği kabul etme.
- Her teknik ayrıntıyı öğretme. Yalnız MUST UNDERSTAND bilgi ULA alır.
- Kullanıcı istemeden HTML üretme.
