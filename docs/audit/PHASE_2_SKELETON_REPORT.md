# PHASE 2 — Skill Skeleton + Entry Router Report

**Tarih:** 2026-10-27
**Constraint:** Phase 1 audit (FROZEN / PASS). Phase 1 kararları değiştirilmedi.

```text
PHASE 2 STATUS: PASS
PHASE 3 STATUS: READY
```

---

# 1. Created files

Skill root: `.claude/skills/learning/` — 31 dosya.

| Grup | Dosya | İçerik seviyesi |
|---|---|---|
| Entry | `SKILL.md` | Tam operational entry / router |
| References | `00_MASTER_SYSTEM_SPEC.md` | Authoritative archive (metadata + birebir kaynak) |
| References | `01_OPERATIONAL_CORE.md` … `07_INTEGRITY_CHECKS.md` (7) | Skeleton |
| ULA | `ULA_SPECIFICATION.md`, `LEARNING_ARCHITECT.md`, `CONTENT_BUILDER.md`, `LEARNING_AUDITOR.md` | Canonical copy |
| ULA | `ula/templates/` (4) | Canonical copy |
| ULA | `ula/examples/HSMM_PILOT/` (4) | Canonical copy, otomatik yüklenmez |
| Templates | `templates/` (10) | Skeleton: purpose + future schema + `NOT IMPLEMENTED YET` |

Audit dosyaları:

- `docs/audit/PHASE_2_MIGRATION_NOTES.md`
- `docs/audit/PHASE_2_SKELETON_REPORT.md`

Skeleton reference dosyaları şu bölümleri içerir: Status, Planned Phase, Purpose, Responsibility, Inputs, Outputs, Must Not, Authoritative Source.

Planned Phase değerleri `tentative` olarak işaretlidir: 01–02 → Phase 3, 03 → Phase 4, 04 → Phase 5, 05 → Phase 6, 06 → Phase 7, 07 → Phase 8.

# 2. Migrated canonical sources

| Kaynak | Hedef | Durum |
|---|---|---|
| `StudySystem_WithAI.txt` | `references/00_MASTER_SYSTEM_SPEC.md` | Metadata + birebir (diff = 0) |
| `ULA_SPECIFICATION_v1.0.md` | `ula/ULA_SPECIFICATION.md` | MIG-02 hariç birebir |
| `prompts/01..03` | `ula/LEARNING_ARCHITECT.md`, `CONTENT_BUILDER.md`, `LEARNING_AUDITOR.md` | Birebir (`cmp` identical) |
| `templates/*.md` (4) | `ula/templates/` | Birebir (`cmp` identical) |
| `examples/HSMM_PILOT/*` | `ula/examples/HSMM_PILOT/` | MIG-01 hariç birebir |
| `ULA README.md` | — | Kopyalanmadı. Workflow içeriği Phase 5'te `04_ULA_PROTOCOL.md` içine MERGE edilecek (Phase 1 matrisi). |
| `CHANGELOG.md` | — | Kopyalanmadı (MIG-03) |

Construction sources repository'de kalır.

# 3. Migration fixes

Ayrıntı: `docs/audit/PHASE_2_MIGRATION_NOTES.md`.

| ID | Düzeltme |
|---|---|
| MIG-01 | `02_CONTENT_EXAMPLE.md` içinde 6 bozuk LaTeX escape geri yüklendi |
| MIG-02 | ULA spec sonundaki conversational paragraf kaldırıldı |
| MIG-03 | CHANGELOG chat wrapper runtime içine alınmadı |

# 4. SKILL.md routing summary

Frontmatter:

```yaml
name: learning
disable-model-invocation: true
user-invocable: true
argument-hint: "[latest | pending | catch-up | show skipped | <work-unit-id>]"
```

Frontmatter doğrulaması: Kurulu Claude Code 2.1.310 binary'sindeki frontmatter şeması `disable-model-invocation` ("If true, the model cannot invoke this via the Skill tool; only users can type the slash command."), `user-invocable` ve `argument-hint` alanlarını içerir. Alanlar tahminle eklenmedi.

`SKILL.md` bölümleri:

1. Manual only — Learning OFF / ON kuralı, passive tracking yok.
2. Primary learning axis — System Design primary axis.
3. Authority — domain ownership.
4. Language — Türkçe + İngilizce canonical term + ASD-STE100; outside knowledge `ALLOWED WITH LABELS`.
5. State layers — universal / project / personal.
6. Arguments — boş, `latest`, `pending`, `catch-up`, `show skipped`, `<work-unit-id>`.
7. Run router — 13 adım; her adım bir reference dosyasına route edilir.
8. Load map.
9. Project-state initialization — kullanıcı onayı olmadan dosya oluşturulmaz.
10. Must not.

**Skeleton kuralı:** Bir adımın reference veya template dosyası `NOT IMPLEMENTED YET` ise model o adımı uydurmaz, kullanıcıya bildirir, state yazmaz ve durur. Bu kural, skeleton aşamasında yanlış state oluşmasını engeller.

Run router sırası:

```text
LOAD CONFIG / STATE → DISCOVER WORK UNITS → COVERAGE CHECK → SCOPE RESOLUTION
→ HUMAN SYNCHRONIZATION → KNOWLEDGE PRIORITY → LEARNING EVENT EXTRACTION
→ LIGHT or FULL ULA → MINDMAP / SEMANTIC GRAPH UPDATE → KNOWLEDGE PERSISTENCE
→ RETRIEVAL → COVERAGE UPDATE → INTEGRITY CHECK
```

# 5. Token load map

| Durum | Yüklenen | Boyut |
|---|---|---|
| Startup | `SKILL.md` + `LEARNING_CONFIG.md` + `LEARNING_STATE.md` | `SKILL.md` = 6.6 KB |
| Coverage | `02_COVERAGE_PROTOCOL.md` + `COVERAGE_LEDGER.md` | skeleton |
| Human Sync | `03_HUMAN_SYNC_PROTOCOL.md` | skeleton |
| Light ULA | `04_ULA_PROTOCOL.md` (+ `05` gerekirse) | skeleton |
| Full ULA | Architect → user review → Builder → Auditor (sırayla) | 13.8 / 21.8 / 20.9 KB |
| Persistence | `06_KNOWLEDGE_PERSISTENCE.md` + template | skeleton |
| Integrity | `07_INTEGRITY_CHECKS.md` | skeleton |

Default olarak asla otomatik yüklenmez: `00_MASTER_SYSTEM_SPEC.md` (~45 KB), `ula/examples/` (~28 KB), Full ULA source set birlikte.

Startup maliyeti: önceki "her şeyi yükle" senaryosunda ~178 KB idi. Şimdi `SKILL.md` + iki küçük state dosyası.

# 6. Validation

```text
[x] .claude/skills/learning/SKILL.md var
[x] manual invocation frontmatter var (disable-model-invocation: true, user-invocable: true)
[x] skill klasöründe project state yok (state/ klasörü yok)
[x] references/ yapısı var (00–07)
[x] ula/ canonical copies var
[x] templates/ yapısı var (10 dosya)
[x] LEARNING_CONFIG_TEMPLATE var
[x] SKILL.md load map içeriyor
[x] master spec default load dışında
[x] ULA examples default load dışında
[x] Graphify kullanılmadı
[x] application code değişmedi (repository'de application code yok)
[x] source files değişmedi (15 dosya sha256 öncesi/sonrası eşit)
```

Ek kontroller:

| Kontrol | Sonuç | Yöntem |
|---|---|---|
| UTF-8 | 31/31 geçerli, BOM yok | Strict UTF-8 decode |
| Control character | 0 | `grep -P '[\x00-\x08\x0b-\x1f]'` |
| Absolute path, kullanıcı adı, proje-özel path, Jira key | Yok | `grep` (master archive hariç) |
| Development repo içinde `docs/learning/` | Oluşturulmadı | `ls docs` → yalnız `audit/` |
| Türkçe + ASD-STE100 | Yeni yazılan 18 dosyada uygulandı | Manuel gözden geçirme |
| Canonical term tutarlılığı | ULA canonical terimleri kullanıldı (`L1 — Simple Explanation`, `Boundary Statements`, `R — Reference`) | Manuel gözden geçirme |

Not: İlk UTF-8 kontrolü `iconv` ile yapıldı ve bütün dosyalar BAD göründü. Kök neden: `iconv` bu ortamda kurulu değil (exit 127). Kontrol strict decode ile tekrarlandı.

# 7. Deviations

| ID | Sapma | Gerekçe |
|---|---|---|
| D-01 | `argument-hint` frontmatter alanı eklendi | İstenen frontmatter'da yoktu. Kurulu sürümde destekleniyor. Q10 optional argument kararını kullanıcıya gösterir. Davranış değiştirmez. |
| D-02 | `SKILL.md` içine "Skeleton kuralı" eklendi | Protocol dosyaları skeleton iken modelin adımları uydurmasını ve yanlış state yazmasını engeller. |
| D-03 | ULA canonical copy dosyaları İngilizce kaldı | Q1: ULA domain authoritative. ULA dosyaları değiştirilmez. Türkçe kuralı yeni yazılan dosyalar ve user-facing learning content için geçerlidir. |
| D-04 | Master archive başına YAML metadata + 3 satır Türkçe not eklendi | İstenen metadata formatı. Kaynak metin birebir korunur (diff = 0). |
| D-05 | Planned Phase numaraları `tentative` | Phase 3 sonrası sıra henüz onaylanmadı. |

Phase 1 kararı ile çelişen sapma yoktur.

# 8. Phase 3 readiness

**READY.**

Phase 3 için hazır olanlar:

- `02_COVERAGE_PROTOCOL.md` skeleton ve authoritative pointer'lar.
- State template skeleton'ları: `LEARNING_CONFIG`, `LEARNING_STATE`, `COVERAGE_LEDGER`, `LEARNING_QUEUE`.
- Router ve load map sınırları.

Phase 3 öncesi bilinmesi gerekenler:

- Bu repository bir git repository değildir. Coverage protocol'ü uçtan uca test etmek için ayrı bir target project (git ve/veya phase document içeren) gerekir.
- Skill şu anda bu repository'de `/learning` olarak görünür. Skeleton kuralı nedeniyle ilk adımda durur ve state yazmaz.
