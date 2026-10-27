# Learning Skill — V1 Architecture Manifest

**Architecture Status:** V1 FROZEN (Phase 8, 2026-10-27)
**Identity (1.0.0 release):** skill `stay-in-the-loop`, komut `/stay-in-the-loop`, project state `docs/learning/` (değişmedi).
**Rol:** Maintenance haritası. Runtime protocol değildir. Kural burada değil, `Primary File` içindedir.

## Akış

```text
/stay-in-the-loop (manual)
↓
START → COVERAGE → HUMAN SYNC → ULA → COMPLETION → MAP SYNC → KNOWLEDGE PERSISTENCE → FINAL INTEGRITY → DONE
```

- Giriş noktası tek: `.claude/skills/stay-in-the-loop/SKILL.md`.
- Doğrudan komutlar: `map ...` (05 §15), `concept` / `library` / `experiences` / `debt` (06 §24), `integrity` (07 §L.6). Bunlar run loop'u çalıştırmaz.
- `DONE`: Bu Learning Pass için required pipeline ve blocking integrity checks tamamlandı (01 §5). Final integrity `PASS` veya `PASS_WITH_WARNINGS` olmalıdır.

## State layers

| Katman | Konum | Yazan |
|---|---|---|
| UNIVERSAL | `.claude/skills/stay-in-the-loop/` | Kimse (runtime'da read-only) |
| PROJECT | `docs/learning/` (target project) | `/stay-in-the-loop` |
| PERSONAL | `LEARNING_CONFIG.md → personal_library_path` | Persistence, yalnız configured ise, write lock ile |

## Layers

### 1. Manual Invocation

| Alan | Değer |
|---|---|
| Purpose | Learning yalnız kullanıcı `/stay-in-the-loop` yazınca çalışır. Passive tracking yok. |
| Primary File | `SKILL.md` (router), `references/01_OPERATIONAL_CORE.md` (run loop, stop / write rules, DONE) |
| Authoritative State | `state/LEARNING_CONFIG.md` |
| Input | Argüman, config |
| Output | Route edilen adım |

### 2. Coverage

| Alan | Değer |
|---|---|
| Purpose | Work unit discovery, gap detection, scope, unit bazında coverage truth. |
| Primary File | `references/02_COVERAGE_PROTOCOL.md` |
| Authoritative State | `state/COVERAGE_LEDGER.md` (yalnız Discovery / Scope / Completion Commit yazar) |
| Input | Project evidence (Jira, git, phase-doc), config `work_unit_source` |
| Output | Selected scope; derived `LEARNING_STATE.md`, queue §A |

### 3. Human Synchronization

| Alan | Değer |
|---|---|
| Purpose | AI ile üretilen değişikliği insan anlayışına sıkıştırmak. Scope başına tek çıktı. |
| Primary File | `references/03_HUMAN_SYNC_PROTOCOL.md` §1–§7 |
| Authoritative State | `passes/<learning-pass-id>/LEARNING_PASS.md` |
| Input | Selected work unit evidence |
| Output | Human Sync bölümü, evidence status |

### 4. Learning Events

| Alan | Değer |
|---|---|
| Purpose | Öğrenmeye değer değişikliği event yapmak; priority, gap, disposition. |
| Primary File | `references/03_HUMAN_SYNC_PROTOCOL.md` §8–§17 |
| Authoritative State | Pass `## Learning Events`; `state/LEARNING_QUEUE.md` §B (Knowledge Debt) |
| Input | Human Sync çıktısı |
| Output | Event'ler, `OPEN` debt, coverage outcome proposal |

### 5. ULA

| Alan | Değer |
|---|---|
| Purpose | Yalnız MUST UNDERSTAND + GAP event için öğretim içeriği. LIGHT veya FULL. |
| Primary File | `references/04_ULA_PROTOCOL.md` §1–§10; canonical kaynak `ula/` |
| Authoritative State | `passes/<id>/ula/<event-id>/`, pass `## ULA Routing`, `current_stage` |
| Input | `ULA_CANDIDATE` event'ler |
| Output | `LIGHT_ULA.md` veya `ARCHITECTURE.md` (user approval) → `CONTENT.md` → `AUDIT.md` |

### 6. Completion

| Alan | Değer |
|---|---|
| Purpose | Unit bazında Completion Commit ve pass sonucu. |
| Primary File | `references/04_ULA_PROTOCOL.md` §11 + `02` §9–§10 |
| Authoritative State | `COVERAGE_LEDGER.md`, pass `pass_status` |
| Input | Event disposition, ULA status |
| Output | `COVERED` / `PARTIAL` / `NOT_LEARNING_RELEVANT`; pass `COMPLETE` / `WAITING_USER` / `BLOCKED` |

### 7. Semantic Graph / MindMap

| Alan | Değer |
|---|---|
| Purpose | Project içi kavram graph'ı ve horizontal view. Post-completion enrichment. |
| Primary File | `references/05_MINDMAP_PROTOCOL.md` |
| Authoritative State | `maps/SEMANTIC_GRAPH.md` |
| Input | `COMPLETE` pass event'leri, ULA artifact depth |
| Output | Graph delta (atomic), derived `maps/HORIZONTAL_MAP.md`, pass `Map Sync` |

### 8. Knowledge Persistence

| Alan | Değer |
|---|---|
| Purpose | One Concept — One Home; project experience; cross-project experience index. Post-completion enrichment. |
| Primary File | `references/06_KNOWLEDGE_PERSISTENCE.md` |
| Authoritative State | Personal: `registry/CONCEPT_REGISTRY.md`, `concepts/<CH>.md`, `experience-maps/`. Project: `concepts/` pointer veya `LOCAL_TEMPORARY` Home, `experiences/EX-*`, `DR-*`, graph `home_ref`, queue §B debt status |
| Input | `COMPLETE` pass, map sync sonucu, ULA artifact |
| Output | Atomic transaction (write lock + ALL_OR_NOTHING); derived `LIBRARY_INDEX.md` |

### 9. Final Integrity

| Alan | Değer |
|---|---|
| Purpose | Bütün subsystem'leri tek sistem olarak denetlemek; yalnız derived artifact onarmak. |
| Primary File | `references/07_INTEGRITY_CHECKS.md` (§C, §E, §U, §M, §P, §L) |
| Authoritative State | Yok. Okur. Yalnız `DERIVED` artifact yazar. |
| Input | Config, state, ledger, queue, pass, graph, view, concepts, experiences; configured ise personal registry / Home / map / index |
| Output | `PASS` / `PASS_WITH_WARNINGS` / `FAIL`; derived rebuild listesi |

## Authority summary

| Class | Artifact |
|---|---|
| AUTHORITATIVE | `LEARNING_CONFIG`, `COVERAGE_LEDGER`, `LEARNING_QUEUE §B`, `LEARNING_PASS`, ULA artifact, `SEMANTIC_GRAPH`, `CONCEPT_REGISTRY`, Concept Home, Concept Pointer, Experience Note, Decision Record, Experience Map |
| DERIVED | `LEARNING_STATE`, `LEARNING_QUEUE §A`, `HORIZONTAL_MAP`, `LIBRARY_INDEX` |
| LOCK | `<personal_library_path>/.learning-write-lock/` |

Tam tablo: `07` §L.1.

## Identity

| ID | Format | Sahip |
|---|---|---|
| Project | `PRJ-xxxxxxxx` | config |
| Learning Pass | `LP-YYYYMMDD-NN` | 03 §3 |
| Learning Event | `LE-<learning-pass-id>-NN` | 03 §9.1 |
| Knowledge Debt | `KD-<learning-pass-id>-NN` | 03 §14 |
| Graph node | `KN-xxxxxxxx` | 05 §3.1 |
| Concept | `CH-xxxxxxxx` | 06 §4 |
| Experience | `EX-xxxxxxxx` | 06 §4 |
| Decision Record | `DR-xxxxxxxx` | 06 §4 |
| Write lock | `LK-xxxxxxxx` | 06 §22.1 |

Identity chain: `WORK UNIT → LEARNING EVENT → ULA ARTIFACT → GRAPH NODE → CONCEPT HOME → EXPERIENCE NOTE → EXPERIENCE MAP` (07 §L.5).

## Maintenance

- Regression: `uv run --no-project python tests/run_all.py` (`tests/README.md`).
- Bir kural değişirse: önce primary file, sonra `07` check, sonra test. Test kuralı runtime dosyadan okur.
- V1 dışı: global cross-project graph, HTML atlas, remote / multi-user library, database backend.
