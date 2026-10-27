# 04 — ULA Protocol

**Status:** IMPLEMENTED (Phase 5)

## Purpose

`ULA_CANDIDATE` event'leri doğru ULA process'ine yönlendirir: Light veya Full.
Yarım kalan Learning Pass'i devam ettirir.
ULA gerekmeyen scope'u açık bırakmadan Completion'a taşır.

## Responsibility

- ULA mode routing ve user override.
- Light ULA flow ve self-check.
- Full ULA flow: Architect → Human Review → Builder → Auditor.
- Audit result ve revision routing.
- Pass lifecycle: status, current stage, resume / new / abandon.
- Early completion.
- Unit bazında Coverage Completion Commit.
- Token load rules.

## Must Not

- Work unit discovery, coverage discovery, event extraction veya Knowledge Priority yapmaz. Bunlar `02` ve `03` görevidir.
- Experience Note, Experience Map, Concept Home veya persistent MindMap yazmaz.
- ULA rol dosyalarının kurallarını değiştirmez veya tekrar yazmaz. `ula/` dosyalarına pointer verir.
- Full ULA rol dosyalarını aynı anda yüklemez.
- Mechanism'den önce theory, theory'den önce formalism vermez.
- Interactive quiz veya spaced repetition oturumu başlatmaz. Yalnız retrieval prompt üretir.

---

## 1. ULA role

ULA bir **Learning Content Protocol**'dür.
Görevi: öğrenilmesine karar verilmiş bilgiyi doğru zihinsel sırayla öğretmek.

Canonical learning order:

```text
L0 — MAP
↓
L1 — SIMPLE EXPLANATION
↓
L2 — MECHANISM
↓
L3 — THEORY
↓
L4 — MATH / FORMALISM
↓
BOUNDARY / CONFUSION CHECK
↓
RETRIEVAL
↓
R — REFERENCE
```

Ana kural: Mechanism before Theory. Theory before Formalism. Formül yeni fikri ilk kez tanıtmaz.

Authority: ULA terimleri ve katman kuralları `ula/ULA_SPECIFICATION.md` ve `ula/` rol dosyalarına aittir.

```text
DEPTH   → hangi katmanlar açılır (L0–L4)
PROCESS → içerik nasıl üretilir (LIGHT / FULL)
DEPTH ≠ PROCESS
```

---

## 2. Vocabulary

### 2.1 ULA mode

| Mode | Anlam |
|---|---|
| `LIGHT` | Tek geçiş. Rol ayrımı yok. Self-check var. |
| `FULL` | Architect → Human Review → Builder → Auditor. |

### 2.2 ULA status (event bazında)

| Status | Anlam |
|---|---|
| `PENDING` | Route edildi. Henüz başlamadı. |
| `WAITING_USER` | Kullanıcı kararı gerekli (review, routing uncertain, override). |
| `IN_PROGRESS` | İçerik üretiliyor. |
| `NEEDS_REVISION` | Self-check veya audit revision istedi. |
| `COMPLETE` | Light self-check PASS veya Full audit freeze-ready. |
| `BLOCKED` | Aynı sorun ikinci kez tekrar etti veya evidence / artifact eksik. |

### 2.3 Pass status

| Status | Anlam |
|---|---|
| `IN_PROGRESS` | Pipeline aktif. |
| `WAITING_USER` | Devam etmek için kullanıcı kararı gerekli. |
| `BLOCKED` | Required evidence veya artifact eksik. |
| `COMPLETE` | Required learning pipeline tamamlandı. Açık item yok. |
| `ABANDONED` | Kullanıcı pass'i bilinçli olarak bıraktı. |

Active pass = `IN_PROGRESS` ∪ `WAITING_USER` ∪ `BLOCKED`.

### 2.4 Current stage

| Stage | Anlam |
|---|---|
| `COVERAGE` | Scope resolution (`02`) |
| `HUMAN_SYNC` | Human Sync, event, priority, disposition (`03`) |
| `ULA_ROUTING` | Mode seçimi; sıradaki event'i seç |
| `LIGHT_ULA` | Light içerik + self-check |
| `FULL_ULA_ARCHITECT` | Project Brief + Architect |
| `FULL_ULA_REVIEW` | Kullanıcı architecture review |
| `FULL_ULA_BUILD` | Builder |
| `FULL_ULA_AUDIT` | Auditor |
| `COMPLETION` | Coverage Completion Commit |
| `COMPLETE` | Pass bitti |

---

## 3. Entry: early completion check

Handoff sonrası (`03` §17) pass içindeki disposition sayılarına bak:

| ULA_CANDIDATE | UNRESOLVED | Sonraki stage |
|---|---|---|
| 0 | 0 | `COMPLETION` (early completion) |
| 0 | > 0 | Kullanıcıya UNRESOLVED kararlarını sor (§11.3). Karar yoksa `COMPLETION`. |
| > 0 | any | `ULA_ROUTING` |

Early completion durumunda ULA dosyası yüklenmez. Örnek: bütün event'ler `EXPERIENCE_ONLY` / `KNOWLEDGE_DEBT` / `IMPLEMENTATION_DETAIL` veya bütün unit'ler `NOT_LEARNING_RELEVANT`.

---

## 4. Mode routing

Her `ULA_CANDIDATE` event için sırayla:

```text
1. Explicit user override  → LIGHT veya FULL
2. Full trigger check      → en az bir trigger güçlü biçimde var → FULL
3. Otherwise               → LIGHT (default)
```

### 4.1 Full triggers

| Trigger |
|---|
| `CRITICAL_THEORY` |
| `CAREER_CENTRAL_CONCEPT` |
| `HIGH_REUSE` |
| `IMPORTANT_ARCHITECTURE_DECISION` |
| `IMPORTANT_DSA_PATTERN` |
| `SERIOUS_FAILURE_OR_PERFORMANCE_BEHAVIOUR` |
| `HIGH_RISK_MISUNDERSTANDING` |
| `MULTI_CONCEPT_DEPENDENCY` |
| `RECURSIVE_TOPIC_STRUCTURE` |
| `FORMALISM_REQUIRED` |
| `SOURCE_ARCHITECTURE_REQUIRED` |
| `USER_REQUESTS_DEEP_LEARNING` |

Kurallar:

- Trigger yalnız event kaydı veya project evidence ile desteklenirse sayılır. Trigger uydurma.
- `routing_reason` alanına trigger kodlarını yaz. Örnek: `FULL: IMPORTANT_ARCHITECTURE_DECISION, RECURSIVE_TOPIC_STRUCTURE`.
- Event bilgisi trigger kararına yetmiyorsa: `routing_reason: ROUTING UNCERTAIN`, `ula_status: WAITING_USER`. Kullanıcıya sor.
- Trigger yoksa `LIGHT`. Amaç: Full ULA'yı gereksiz çalıştırmamak. Token efficiency bir design constraint'tir.

### 4.2 User override

- Kullanıcının açık `LIGHT` veya `FULL` tercihi en yüksek authority'dir.
- `user_override` alanına `LIGHT` veya `FULL` yaz. Override yoksa `-`.
- Kullanıcı `LIGHT` seçti ve Full trigger var: Light'ın sınırını tek cümle ile açıkla (ör. L4 açılmaz, architecture review yok). Kullanıcının seçimini sessizce değiştirme.

### 4.3 Routing checkpoint

Routing tablosunu kullanıcıya göster. Kullanıcı mode'u değiştirebilir. Sonra event'leri tablo sırasıyla işle. Aynı anda tek event işlenir.

---

## 5. Stage transitions

Pass bir anda tek `current_stage` taşır. Bu stage işlenen event'in stage'idir.
Tabloda olmayan geçiş yapılmaz.

| from | trigger | to | requires | ula_status |
|---|---|---|---|---|
| ULA_ROUTING | mode LIGHT | LIGHT_ULA | - | IN_PROGRESS |
| ULA_ROUTING | mode FULL | FULL_ULA_ARCHITECT | project_brief | IN_PROGRESS |
| ULA_ROUTING | no open ULA event | COMPLETION | - | - |
| LIGHT_ULA | self-check PASS | ULA_ROUTING | light_core | COMPLETE |
| LIGHT_ULA | self-check FAIL | LIGHT_ULA | - | NEEDS_REVISION |
| FULL_ULA_ARCHITECT | architecture proposed | FULL_ULA_REVIEW | proposed_architecture | WAITING_USER |
| FULL_ULA_REVIEW | user approve | FULL_ULA_BUILD | user_approval | IN_PROGRESS |
| FULL_ULA_REVIEW | user revise | FULL_ULA_ARCHITECT | user_feedback | IN_PROGRESS |
| FULL_ULA_REVIEW | user reject | ULA_ROUTING | user_decision | BLOCKED |
| FULL_ULA_BUILD | content generated | FULL_ULA_AUDIT | frozen_architecture | IN_PROGRESS |
| FULL_ULA_BUILD | minor fixes applied | ULA_ROUTING | minor_fix_list | COMPLETE |
| FULL_ULA_AUDIT | READY TO FREEZE | ULA_ROUTING | audit_report | COMPLETE |
| FULL_ULA_AUDIT | FREEZE AFTER MINOR FIXES | FULL_ULA_BUILD | audit_report | NEEDS_REVISION |
| FULL_ULA_AUDIT | DO NOT FREEZE — REVISION REQUIRED | FULL_ULA_BUILD | audit_report | NEEDS_REVISION |
| FULL_ULA_AUDIT | DO NOT FREEZE — ARCHITECTURE REVISIT REQUIRED | FULL_ULA_ARCHITECT | audit_report | NEEDS_REVISION |
| COMPLETION | commit done, no open item | COMPLETE | integrity_pass | - |

Pass status kuralı:

| Durum | pass_status |
|---|---|
| `current_stage = FULL_ULA_REVIEW` veya bir event `WAITING_USER` | `WAITING_USER` |
| Required evidence / artifact eksik | `BLOCKED` |
| `current_stage = COMPLETE` | `COMPLETE` |
| Diğer | `IN_PROGRESS` |

---

## 6. Light ULA

### 6.1 Ne zaman

- local ve sınırlı concept,
- tek mekanizma,
- küçük reusable pattern,
- kısa System Design concept,
- küçük DSA pattern,
- kısa hatırlatma,
- architecture tasarımı gerektirmeyen knowledge gap.

### 6.2 Flow

```text
L0 — LOCAL MAP
↓
L1 — SIMPLE EXPLANATION
↓
L2 — MECHANISM
↓
L3 — THEORY                    yalnız gerekirse
↓
BOUNDARY / CONFUSION CHECK     yalnız gerekirse
↓
RETRIEVAL
↓
R — REFERENCE                  yalnız gerekirse
↓
SELF-CHECK
```

Kurallar:

- Artifact: `templates/LIGHT_ULA_TEMPLATE.md` → `ula/<event-id>/LIGHT_ULA.md`.
- L4 default olarak açılmaz. Formalism gerçekten gerekirse Light'ı durdur. Kullanıcıya Full öner (§4.2).
- Architect, Builder veya Auditor ayrı stage olarak çalışmaz. Rol dosyaları yüklenmez.
- L0 Local Map yalnız öğrenme orientation içindir. Persistent MindMap değildir.
- Dil: Türkçe açıklama, İngilizce canonical technical term (Q7).
- Outside knowledge `ALLOWED WITH LABELS`. Project fact için project evidence authoritative.

### 6.3 Self-check

| # | Kontrol |
|---|---|
| 1 | Whole / local context (L0) var mı? |
| 2 | Simple explanation (L1) var mı? |
| 3 | Mechanism (L2) açık mı? |
| 4 | Theory mekanizmayı tekrar etmiyor, nedenini açıklıyor mu? |
| 5 | Gereksiz jargon yok mu? |
| 6 | Gerekli confusion boundary var mı? |
| 7 | Retrieval sorusu var mı? |
| 8 | Reference detayı ana içeriğe sızmamış mı? |

- Bir madde FAIL ise output'u bir kez düzelt. `ula_status: NEEDS_REVISION`.
- Aynı madde tekrar FAIL ise `ula_status: BLOCKED`. Kullanıcıya raporla.
- Self-check Full Learning Auditor yerine geçmez.

---

## 7. Full ULA

### 7.1 Ne zaman

En az bir Full trigger (§4.1) güçlü biçimde varsa veya kullanıcı `FULL` istediyse.

### 7.2 Flow

```text
PROJECT / EVENT BRIEF
↓
LEARNING ARCHITECT        → PROPOSED ARCHITECTURE
↓
HUMAN REVIEW              → approve / revise / reject
↓
FROZEN ARCHITECTURE
↓
CONTENT BUILDER           → CONTENT
↓
LEARNING AUDITOR          → AUDIT RESULT
↓
FREEZE / REVISION ROUTING
```

Rol sınırları `ula/` dosyalarındaki gibidir. Bu protocol onları değiştirmez.

### 7.3 Project Brief

- Template: `ula/templates/PROJECT_BRIEF_TEMPLATE.md` → `ula/<event-id>/PROJECT_BRIEF.md`.
- Event kaydından doldur: topic, learner goal, expected depth, use case, sources, outside knowledge policy, learner background, constraints.
- Bilinmeyen alanı boş bırak veya `UNRESOLVED` yaz. Uydurma.
- Sources iki gruba ayrılır: project evidence (authoritative, project facts) ve general theory (`ALLOWED WITH LABELS`). Karıştırma.
- Learner background: yalnız `knowledge_gap` ve önceki learning artifact'ten. Tahmin yok.

### 7.4 Architect

- Yükle: `ula/LEARNING_ARCHITECT.md` + `PROJECT_BRIEF.md` + `ula/templates/ARCHITECTURE_OUTPUT_TEMPLATE.md`.
- Çıktı: `ula/<event-id>/ARCHITECTURE.md`, `architecture_status: PROPOSED`.
- Sonra: `current_stage: FULL_ULA_REVIEW`, `pass_status: WAITING_USER`. Dur.

### 7.5 Human Review gate

Architecture otomatik freeze edilmez. Kullanıcı kararı olmadan Builder çalışmaz.

| Karar | Sonuç |
|---|---|
| approve | `architecture_status: FROZEN`, `approved_by: user`, `approved_at` yazılır. → `FULL_ULA_BUILD` |
| revise | Kullanıcı notu `ARCHITECTURE.md` revision log'a eklenir. → `FULL_ULA_ARCHITECT` |
| reject | `ula_status: BLOCKED`. Kullanıcı isterse event'i `03` §13.2 ile başka disposition'a taşı (ör. `KNOWLEDGE_DEBT`). |

### 7.6 Builder

- Ön koşul: `architecture_status: FROZEN` ve user approval kaydı.
- Yükle: `ula/CONTENT_BUILDER.md` + frozen `ARCHITECTURE.md` + `ula/templates/CONTENT_BUILD_TEMPLATE.md`. Architect dosyasını tekrar yükleme.
- Çıktı: `ula/<event-id>/CONTENT.md`.
- Architecture'ı sessizce değiştirme. Architecture sorunu görülürse Builder durur ve raporlar.

### 7.7 Auditor

- Ön koşul: `CONTENT.md` var.
- Yükle: `ula/LEARNING_AUDITOR.md` + `ARCHITECTURE.md` + `CONTENT.md` + `ula/templates/AUDIT_REPORT_TEMPLATE.md`. Builder dosyasını tekrar yükleme.
- Çıktı: `ula/<event-id>/AUDIT.md`. Her audit round dosyaya eklenir. Eski round silinmez.
- Auditor'ın severity scale ve Freeze Recommendation kuralları korunur.

### 7.8 Audit result routing

| Freeze Recommendation | Route | Sonuç |
|---|---|---|
| READY TO FREEZE | Freeze | `ula_status: COMPLETE` |
| FREEZE AFTER MINOR FIXES | Builder yalnız listedeki minor fix'leri uygular | `COMPLETE` (yeniden audit yok) |
| DO NOT FREEZE — REVISION REQUIRED | BUILDER REVISION → AUDIT | `NEEDS_REVISION` |
| DO NOT FREEZE — ARCHITECTURE REVISIT REQUIRED | ARCHITECTURE REOPEN → HUMAN REVIEW → BUILDER → AUDIT | `NEEDS_REVISION`; architecture `PROPOSED` olur |

Freeze-ready = `READY TO FREEZE` veya minor fix'leri uygulanmış `FREEZE AFTER MINOR FIXES`.

Revision limit:

- Her route türü (builder revision, architecture revisit) event başına bir kez çalışır.
- Aynı route ikinci kez istenirse: `ula_status: BLOCKED`. Kullanıcıya raporla. Döngüye girme.

---

## 8. Retrieval

- Light ve Full artifact içinde retrieval prompt bulunur.
- System Design için: Hangi constraint bu tasarımı doğurdu? Alternatif neydi? Tasarım ilk nerede kırılır? Hangi constraint değişirse başka çözüm seçilir?
- DSA için: Pattern neydi? Naive çözüm neden yetmedi? Chosen structure neden uygundu? Time / space trade-off neydi?
- Interactive quiz, scoring veya spaced repetition yok.

---

## 9. Runtime artifact structure

```text
docs/learning/passes/
└── <learning-pass-id>/
    ├── LEARNING_PASS.md
    └── ula/
        └── <event-id>/
            ├── LIGHT_ULA.md            (LIGHT)
            ├── PROJECT_BRIEF.md        (FULL)
            ├── ARCHITECTURE.md         (FULL)
            ├── CONTENT.md              (FULL)
            └── AUDIT.md                (FULL)
```

Kurallar:

- Bir event için tek mode klasörü vardır. LIGHT ve FULL artifact aynı event'te birlikte bulunmaz. Mode değişirse eski artifact silinmez; `<event-id>/superseded/` altına taşınır ve routing reason'a yazılır.
- Full artifact'lerin başında kısa header bulunur:

```yaml
event_id: LE-<learning-pass-id>-NN
artifact: PROJECT_BRIEF | ARCHITECTURE | CONTENT | AUDIT
artifact_status: DRAFT | PROPOSED | FROZEN | COMPLETE
approved_by: user            # yalnız ARCHITECTURE, FROZEN ise
approved_at: YYYY-MM-DD      # yalnız ARCHITECTURE, FROZEN ise
updated_at: YYYY-MM-DD
```

- Learning Pass içine artifact içeriği kopyalanmaz. Routing tablosu pointer verir.
- Development repository içinde runtime pass oluşturulmaz.

---

## 10. Pass lifecycle: resume / new / abandon

### 10.1 Startup check

Her `/stay-in-the-loop` çağrısında, discovery'den önce, `docs/learning/passes/*/LEARNING_PASS.md` içinde active pass ara.

Active pass varsa yeni pass'i sessizce başlatma. Göster:

```text
Incomplete Learning Pass bulundu.

Pass:          LP-...
Scope:         ...
Current Stage: ...
Open Events:   ...

1. Bu pass'e devam et.
2. Yeni Learning Pass başlat.
3. Bu pass'i abandon et.
```

Argüman seçimi zaten belirtiyorsa (`resume`, `new`, `abandon <pass-id>` veya bir pass ID) soru sorma.

### 10.2 Resume

Resume = continue, not regenerate.

- Pass ID aynı kalır.
- `COMPLETE` / `FROZEN` artifact yeniden üretilmez.
- Tamamlanan stage tekrar çalışmaz.
- `current_stage` noktasından devam edilir. Yalnız o stage'in dosyaları yüklenir.
- `FULL_ULA_REVIEW` stage'inde resume: mevcut `ARCHITECTURE.md` gösterilir. Kullanıcı kararı istenir.

### 10.3 New pass

- Eski pass active kalabilir.
- Yeni pass'in selected scope'u ile active pass'lerin scope'u kesişirse: `CONFLICT` göster.
- Seçenekler: eski pass'e devam, kesişen unit'leri yeni scope'tan çıkar, eski pass'i abandon et.
- Aynı work unit veya event iki active pass'te işlenmez.

### 10.4 Abandon

- `pass_status: ABANDONED`, `updated_at` güncellenir.
- Ledger'a yazılmaz. Open unit'ler kapanmaz.
- `PARTIAL.open_items` silinmez.
- Knowledge Debt silinmez.
- Event kayıtları ve artifact'ler silinmez.
- Yeni pass aynı work unit'leri daha sonra yeniden seçebilir.

---

## 11. Completion

### 11.1 Ne zaman

`current_stage: COMPLETION` şu durumlarda başlar:

- early completion (§3), veya
- `ULA_ROUTING` içinde işlenecek ULA event kalmadı: her `ULA_CANDIDATE` event `COMPLETE`, `BLOCKED` veya kullanıcı tarafından ertelenmiş (`PENDING` kalır).

`WAITING_USER` sırasında pipeline durur. Kullanıcı "şimdilik bitir" derse `COMPLETION`'a geçilir. Bekleyen event'ler açık kalır.

### 11.2 Unit blocking rule

| disposition | condition | blocks_unit |
|---|---|---|
| IMPLEMENTATION_DETAIL | - | no |
| EXPERIENCE_ONLY | - | no |
| KNOWLEDGE_DEBT | §B kaydı OPEN | no |
| ULA_CANDIDATE | ula_status COMPLETE | no |
| ULA_CANDIDATE | ula_status not COMPLETE | yes |
| UNRESOLVED | - | yes |

- `EXPERIENCE_ONLY` completion'ı bloklamaz. Event pass içinde kayıtlıdır. Persistence sonraki phase'dedir.
- `KNOWLEDGE_DEBT` completion'ı bloklamaz. Kavram queue §B'de `OPEN` kalır.
- `UNRESOLVED` default olarak bloklar.

### 11.3 UNRESOLVED kararları

Kullanıcı şu kararlardan birini verebilir. Sessiz kapatma yok.

| Karar | Sonuç |
|---|---|
| resolve | Kullanıcı bilgiyi verir. `03` §13.1 tekrar uygulanır. |
| defer as Knowledge Debt | `KNOWLEDGE_DEBT` + §B `OPEN` kaydı |
| dismiss | priority ve disposition `IMPLEMENTATION_DETAIL`; event'e `dismissed by user` notu |
| reclassify | Kullanıcı priority / gap verir. `03` §13.1 tekrar uygulanır. |

Yeni sonuç `ULA_CANDIDATE` ise event `ULA_ROUTING`'e gider.

### 11.4 Unit bazında Completion Commit

Her selected work unit ayrı değerlendirilir. Scope-level tek status kullanılmaz.

| Unit durumu | Ledger status | open_items |
|---|---|---|
| Learning event yok veya yalnız `IMPLEMENTATION_DETAIL`; evidence yeterli | `NOT_LEARNING_RELEVANT` | `-` |
| Event var; bloklayan event yok | `COVERED` | `-` |
| En az bir bloklayan event | `PARTIAL` | Bloklayan event ID'leri |
| Evidence okunamadı ve event yok | Commit yok | - |

Kurallar:

- Commit yalnız integrity PASS ise yapılır: `07` §C, §E, §U.
- Transition `02` §9 matrix'ine uymalıdır (trigger `C`). Geçersiz transition yazılmaz (C-10).
- `learning_pass_id` = bu pass ID.
- `open_items` yalnız event ID taşır.
- ULA event `COMPLETE` olunca ID `open_items` listesinden çıkar. Liste boşalırsa unit `COVERED` için eligible olur. Bu commit sonraki resume'da yapılır (`PARTIAL → COVERED`).

### 11.5 Pass sonucu

| Durum | pass_status | current_stage |
|---|---|---|
| Bütün unit'ler commit aldı ve açık item yok | `COMPLETE` | `COMPLETE` |
| Açık `UNRESOLVED` var | `WAITING_USER` | `HUMAN_SYNC` |
| Açık ULA event var, `BLOCKED` yok | `WAITING_USER` | `ULA_ROUTING` |
| `BLOCKED` ULA event var | `BLOCKED` | `ULA_ROUTING` |

Açık ULA veya `UNRESOLVED` event varken `COMPLETE` yazılmaz.

Pass `COMPLETE` sonrası Next Stage: MAP SYNC (`05_MINDMAP_PROTOCOL.md` §8). Map sync pass status'u değiştirmez.

---

## 12. Token load rules

| Stage | Yükle | Yükleme |
|---|---|---|
| ULA_ROUTING | Bu dosya + `LEARNING_PASS.md` | `ula/` |
| LIGHT_ULA | Bu dosya + `templates/LIGHT_ULA_TEMPLATE.md` + gerekli project evidence | `ula/` rol dosyaları, `ula/ULA_SPECIFICATION.md` |
| FULL_ULA_ARCHITECT | `ula/LEARNING_ARCHITECT.md` + brief + architecture template | Builder, Auditor |
| FULL_ULA_REVIEW | `ARCHITECTURE.md` | Rol dosyaları |
| FULL_ULA_BUILD | `ula/CONTENT_BUILDER.md` + frozen architecture + content template | Architect, Auditor |
| FULL_ULA_AUDIT | `ula/LEARNING_AUDITOR.md` + architecture + content + audit template | Architect, Builder |
| COMPLETION | `02_COVERAGE_PROTOCOL.md` §9–§10 + ledger + `07` | `ula/` |

- Üç rol dosyası aynı anda yüklenmez.
- `ula/ULA_SPECIFICATION.md` yalnız rol dosyası bir kuralı belirsiz bıraktığında okunur.
- `00_MASTER_SYSTEM_SPEC.md` ve example / historical material default load dışındadır.

---

## Authoritative Source

- ULA domain: `ula/ULA_SPECIFICATION.md` §3, §23, §24, §28–§30; `ula/LEARNING_ARCHITECT.md`; `ula/CONTENT_BUILDER.md`; `ula/LEARNING_AUDITOR.md` §34, §36 (Freeze Recommendation).
- Lifecycle: `00_MASTER_SYSTEM_SPEC.md` §20, §36, §40.
- Phase 1 audit: Bölüm 13, Q1, Q6, Q7.
- Coverage: `02_COVERAGE_PROTOCOL.md` §9, §10.
