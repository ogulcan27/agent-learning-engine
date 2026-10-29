# 03 — Human Synchronization Protocol

**Status:** IMPLEMENTED (Phase 4)

## Purpose

Selected coverage scope'u insanın yönetebileceği minimum yeterli mental modele sıkıştırır.
Anlamlı Learning Event'leri çıkarır.
Hangi bilginin gerçekten öğrenilmesi gerektiğini belirler.

## Responsibility

- Project evidence okuma.
- Human Synchronization çıktısı (scope-level).
- Learning Event extraction ve filter.
- Knowledge Priority ve Knowledge Gap.
- Event disposition.
- Knowledge Debt kaydı (`LEARNING_QUEUE.md` §B).
- Coverage outcome önerisi ve pipeline handoff.

## Must Not

- ULA content üretmez. Architect, Builder veya Auditor çağırmaz.
- Light / Full ULA seçmez. Bu seçim `04_ULA_PROTOCOL.md` görevidir.
- MindMap, Concept Home, Experience Note veya Experience Map oluşturmaz.
- Ledger'a yazmaz. Completion Commit yapmaz (`02_COVERAGE_PROTOCOL.md` §10).
- Her work unit için ayrı uzun anlatım üretmez.
- Dosya listesi anlatmaz. Sistem davranışını anlatır.
- Kullanıcının bilgisini tahmin etmez.
- Evidence yoksa methodological karar uydurmaz.

---

## 1. Rol: Compressor

Ana problem:

```text
AI PRODUCTION SPEED > HUMAN COMPREHENSION SPEED
→ COGNITIVE THROUGHPUT GAP
```

Human Synchronization bu farkı küçültür. Bu katman **COMPRESSOR** rolüdür. ULA Teacher değildir.

```text
HUMAN SYNCHRONIZATION → Şu anda ne olduğunu anlamamı sağlar.
ULA                   → Önemli bilgiyi kalıcı biçimde öğrenmemi sağlar.
```

Amaç bütün teknik işi öğretmek değildir.
Amaç projeyi güvenli biçimde yönetmeye devam etmek için minimum yeterli mental modeli üretmektir.

---

## 2. Flow

```text
SELECTED COVERAGE SCOPE        (02 §8 çıktısı)
↓
1. PASS OPEN                   Learning Pass ID ata (§3)
↓
2. PROJECT EVIDENCE READ       (§4)
↓
3. HUMAN SYNCHRONIZATION       scope-level, tek çıktı (§5, §6); geçerli unit record reuse (08 §12)
↓
4. LEARNING EVENT EXTRACTION   filter + event model (§8–§10)
↓
5. KNOWLEDGE PRIORITY          + knowledge gap (§11, §12)
↓
6. EVENT DISPOSITION           (§13)
↓
7. USER CHECKPOINT             (§16)
↓
8. INTEGRITY                   07 §E
↓
9. HANDOFF WRITE               pass dosyası + queue §B (§14, §15, §17)
↓
NEXT STAGE: ULA ROUTING        (04_ULA_PROTOCOL.md)
```

---

## 3. Learning Pass ID

Format:

```text
LP-YYYYMMDD-NN
```

- `YYYYMMDD` = pass tarihi.
- `NN` = aynı tarih için `docs/learning/passes/` içindeki pass klasörlerinin en büyük `NN` + 1. İlk pass `01`.
- ID pass açılınca bir kez atanır. Pass boyunca değişmez.
- Pass klasörü: `docs/learning/passes/<learning-pass-id>/` (`04` §9).

Active pass kontrolü ve resume / new / abandon: `04_ULA_PROTOCOL.md` §10.

---

## 4. Project evidence read

Yalnız selected scope'un evidence'ını oku:

| source_type | Evidence |
|---|---|
| `jira` | Issue başlığı, açıklama, yorumlar, bağlı commit'ler |
| `git` | Commit mesajı, diff, ilgili test |
| `phase-doc` | Step metni, ilgili rapor veya audit |
| `user` | Kullanıcının tanımı + belirttiği dosyalar |
| `other` | `source_ref` içindeki pointer |

Kurallar:

- Project facts için project evidence authoritative'dir.
- Önce özet kaynağı oku (issue, commit mesajı, step). Diff ve kodu yalnız iddiayı doğrulamak için oku.
- Bütün repository'yi okuma.
- Okunamayan evidence'ı `UNRESOLVED` işaretle. İçeriğini tahmin etme.

---

## 5. Human Synchronization output

Scope başına **bir** çıktı üretilir. Format: `templates/HUMAN_SYNC_TEMPLATE.md`.

| # | Alan | Kural |
|---|---|---|
| 5.1 | One-Sentence Summary | `Problem → Action → Result`. Tek cümle veya tek kısa zincir. Konu + işlem veya karar + sonuç. İç ID özne olmaz. |
| 5.2 | Simple Causal Explanation | 3–6 kısa cümle. Problem neydi? Neden önemliydi? Ne yaptık? Neden? Ne değişti? Implementation ayrıntısı minimum. |
| 5.3 | Mental Model | Kullanıcı sistemi zihninde simüle edebilmeli. Şekil seçimi aşağıda. |
| 5.4 | Technical Translation | `"Basit anlam" ↔ Canonical Technical Term`. Bir kavram = bir isim. 2–5 çift. Önemli proje sembolü burada tanımlanır. |
| 5.5 | Important Decisions | `Decision / Alternatives / Selected / Why / Trade-off`. Routine karar yok. |
| 5.6 | What Changed? | `ÖNCE → … / SONRA → …`. System behaviour değişimi. Dosya listesi yok. |
| 5.7 | Evidence | Her önemli iddia için evidence status + ref (§7). |
| — | Unresolved Questions | Evidence ile karar verilemeyen sorular. Yoksa `Yok.` |

Mental Model şekli:

| Durum | Şekil |
|---|---|
| Veri veya istek bir hattan geçiyor | `INPUT → PROCESS → DECISION → OUTPUT` |
| Alternatifler arasından seçim yapıldı | `PROBLEM ├── OPTION A ├── OPTION B └── OPTION C ↓ SELECTED` |
| Diğer | Doğal system / causal / data flow diyagramı |

Human-first yazım (scope çıktısı ve unit record):

- Okuyucu iç ID'leri ve proje kısaltmalarını bilmez. Haftalar sonra dönmüş olabilir.
- Önce düz anlam, sonra iç terim yazılır: `benzersiz dinleyici sayısı (N)`. Sembol ilk geçtiği yerde tanımlanır.
- Record Purpose = One-Sentence Summary kuralı (5.1).
- Record Downstream Impact önce düz dille yazılır: sonraki iş neyi kullanacak veya neyle sınırlanacak? ID'ler sonra gelir.
- Mental Model 2–6 kısa satırdır. Audit ve provenance dili taşımaz.
- Human Sync terimi işi anlamaya yetecek kadar açıklar. Teori öğretmez. Teori ULA'nın işidir (`04`).
- View Purpose, Technical Translation, How It Works ve Downstream Impact'i HUMAN katmanında gösterir (`09` §5).

Important Decisions içinde `Alternatives` alanı:

- Project'te gerçekten değerlendirilen alternatif → `VERIFIED` + ref.
- Dış bilgiye dayalı alternatif → `GENERAL THEORY` etiketi.
- Project'te yapılmamış bir alternatifi "yaptık" diye yazma.

---

## 6. Multi-work-unit compression

Selected scope birden fazla work unit içerebilir.

```text
MULTIPLE WORK UNITS
↓
ONE SCOPE-LEVEL MODEL
↓
HIGH-SIGNAL EVENTS
```

Kurallar:

1. Önce scope-level Human Synchronization üret. Work unit başına ayrı summary üretme.
2. Sonra yalnız anlamlı Learning Event'leri ayrıştır.
3. Her event hangi work unit'lerden geldiğini `work_unit_ids` ile gösterir. Bir event birden fazla unit'e bağlı olabilir.
4. Routine file-by-file narration yapma.
5. Sabit event quota kullanma. Event sayısını yapay olarak artırma.
6. Kalıcı unit record (`08` §4) kullanıcıya gösterilen çıktı değildir. Kullanıcı yine scope başına tek çıktı görür.

§4–§7 Human Synchronization içeriği için tek kaynaktır. Full mode ve `/stay-in-the-loop sync` aynı kuralları kullanır (`08` §2).

```text
100 technical changes
↓
meaningful changes
↓
high-value learning events
↓
reusable mental models
```

Hedef: minimum sufficient high-signal output.

---

## 7. Evidence model

### 7.1 Evidence status

| Status | Anlam |
|---|---|
| `VERIFIED` | Project evidence iddiayı doğrudan destekliyor. Ref zorunlu. |
| `INFERRED` | Project evidence güçlü biçimde işaret ediyor. Açık kayıt yok. |
| `ASSUMED` | Çalışmak için bir varsayım gerekiyor. Varsayım açık yazılır. |
| `UNRESOLVED` | Mevcut evidence ile karar verilemiyor. |

### 7.2 Evidence ref

Format: `<kind>:<pointer>`.

| kind | Örnek |
|---|---|
| `work-unit` | `work-unit:jira:ABC-44` |
| `commit` | `commit:9f3a1c2b7d4e` |
| `issue` | `issue:ABC-44` |
| `doc` | `doc:docs/PLAN.md#step-10` |
| `test` | `test:tests/test_worker.py` |
| `diagnostic` | `diagnostic:logs/latency_report.md` |
| `code` | `code:src/api/jobs.py` |

Yazım: `VERIFIED (commit:9f3a1c2b7d4e; test:tests/test_worker.py)`.

### 7.3 General theory

Outside knowledge `ALLOWED WITH LABELS` kuralına uyar. Dış bilgi `GENERAL THEORY` etiketi alır.
`GENERAL THEORY` bir evidence status değildir. Project fact iddiası için kullanılmaz.

```text
VERIFIED       → Project'te gerçekten değerlendirildi.
INFERRED       → Muhtemel reasoning.
GENERAL THEORY → Dış bilgiye dayalı açıklama veya alternatif.
```

### 7.4 No silent methodological decisions

Şu konularda evidence yetersizse karar uydurma. `UNRESOLVED` yaz:

- statistical assumption,
- data leakage,
- causal interpretation,
- validation design,
- security,
- destructive operation.

Bu konularda `ASSUMED` kullanma.

---

## 8. Learning Event

### 8.1 Tanım

Learning Event: Projede karşılaşılan ve gelecekte karar verme, sistem anlama veya problem tanıma kapasitesini artırabilecek yüksek değerli teknik olaydır.

Her technical change learning event değildir.

Örnek türler (liste kapalı değildir):

```text
architecture decision          system-design decision
DSA / computational pattern    database decision
caching decision               queue / async decision
performance bottleneck         critical bug with reusable lesson
security decision              scaling problem
ML serving decision            important statistical assumption
data leakage risk              validation / causality decision
reliability decision
```

### 8.2 Filter

Bir değişiklik şu iki sorudan en az birine `evet` cevap vermelidir:

1. Kullanıcı gelecekte benzer bir kararı kendisi verebilir mi?
2. Kullanıcı system behaviour'ı veya bir problem pattern'ini bu olay olmadan yanlış anlar mı?

İkisi de `hayır` ise event değildir.

Genelde event **değildir**:

| Değişiklik |
|---|
| file rename |
| routine CRUD |
| formatting |
| import change |
| trivial syntax fix |
| mechanical refactor |
| AI'ın kolayca tekrar yapabileceği project-specific detail |
| reusable mental model üretmeyen implementation detail |

Filter dışında kalan değişiklikler event olmaz. Pass dosyasında yalnız sayı ve tek satır özet olarak `Implementation Details Suppressed` altında görünür.

---

## 9. Event model

| Alan | Değer |
|---|---|
| `event_id` | `LE-<learning-pass-id>-NN` (§9.1) |
| `title` | Kısa ad |
| `work_unit_ids` | Selected scope içindeki bir veya daha fazla `work_unit_id` |
| `category` | Primary category (§10). Gerekirse `secondary_tags`. |
| `problem` | Gerçek problem |
| `why_it_matters` | Projeyi yönetmek için neden önemli |
| `decision_or_mechanism` | Seçilen karar veya mekanizma. SYSTEM_DESIGN ve DSA için §10.2 / §10.3 formatı. |
| `reusable_signal` | Başka problemde bu pattern'i tanıtan sinyal |
| `evidence_status` | §7 formatı |
| `knowledge_priority` | §11 |
| `knowledge_gap` | §12 |
| `disposition` | §13 |
| `open_question` | Opsiyonel. Yalnız gerekirse. |

### 9.1 Event ID

- Format: `LE-<learning-pass-id>-NN`. Örnek: `LE-LP-20261027-01-01`.
- `NN` pass içinde `01`'den başlar ve sırayla artar.
- Pass içinde duplicate ID yasaktır.
- Atanan ID değişmez. Event silinirse ID tekrar kullanılmaz.
- Bu ID ULA, Knowledge Debt, Experience Note, Concept Home ve MindMap tarafından referans olarak kullanılır.

---

## 10. Event category

### 10.1 Canonical category set

| Category |
|---|
| `SYSTEM_DESIGN` |
| `DSA` |
| `DATA_SCIENCE` |
| `STATISTICS` |
| `SOFTWARE_ENGINEERING` |
| `PRODUCTION_ENGINEERING` |
| `SECURITY` |
| `RELIABILITY` |
| `OTHER` |

- Her event tek primary category alır.
- `secondary_tags` opsiyoneldir. Aynı set içinden seçilir.

Category seçme sırası:

```text
1. Bu olay bir System Design problemi mi?
   constraint, component, interface, state, flow, reliability, scaling,
   storage, communication, deployment, performance, failure behaviour
   → evet: SYSTEM_DESIGN
2. Gerçek computational need var mı? → evet: DSA
3. Diğer category'ler.
```

System Design primary engineering learning axis'tir. Ancak event System Design değilse bu category'ye zorla koyma.

### 10.2 SYSTEM_DESIGN format

`decision_or_mechanism` içinde mümkün olduğunda:

```text
REAL PROBLEM
↓
CONSTRAINT
↓
AFFECTED COMPONENT
↓
ALTERNATIVES
↓
SELECTED DESIGN
↓
WHY
↓
TRADE-OFF
↓
FAILURE MODE
↓
OBSERVED BEHAVIOUR
↓
REUSABLE SIGNAL
```

Evidence bir alanı desteklemiyorsa alanı uydurma. `UNRESOLVED` yaz.

### 10.3 DSA format

DSA yalnız gerçek computational need varsa kullanılır. Yoksa DSA event üretme.

```text
REAL PROBLEM
↓
NAIVE SOLUTION
↓
BOTTLENECK
↓
PROBLEM PATTERN
↓
CANDIDATE STRUCTURES / ALGORITHMS
↓
CHOSEN STRUCTURE
↓
TIME COMPLEXITY
↓
SPACE COMPLEXITY
↓
TRADE-OFF
↓
REAL SYSTEM USE
↓
REUSABLE SIGNAL
```

Evidence bir alanı desteklemiyorsa `UNRESOLVED` yaz.

---

## 11. Knowledge Priority

| Priority | User-facing | Anlam |
|---|---|---|
| `MUST_UNDERSTAND` | MUST UNDERSTAND | Projeyi doğru yönetmek veya benzer kararı gelecekte vermek için gerekli. |
| `USEFUL_TO_KNOW` | USEFUL TO KNOW | Faydalı. Şu anda derin öğrenmek şart değil. |
| `IMPLEMENTATION_DETAIL` | IMPLEMENTATION DETAIL | AI çözebilir. Şu anda öğrenmeye gerek yok. |

`MUST_UNDERSTAND` sinyalleri:

- projeyi doğru yönetmek için gerekli,
- yanlış anlaşılması yanlış tasarım yaratabilir,
- system behaviour'ı etkiliyor,
- reusable architecture decision,
- kritik statistical assumption,
- leakage / causality / validation riski,
- failure / performance açısından önemli,
- tekrar karşılaşılabilecek temel pattern,
- kullanıcı bu kararı ileride kendisi vermeli.

`IMPLEMENTATION_DETAIL` için: ULA yok, Knowledge Debt yok, uzun açıklama yok.

Ana kural: Her teknik ayrıntı öğrenme borcu değildir.

`MUST_UNDERSTAND` otomatik olarak ULA demek değildir. Önce knowledge gap kontrol edilir.

---

## 12. Knowledge Gap

Priority ile knowledge gap aynı şey değildir.

```text
PRIORITY       → Bu bilgi ne kadar önemli?
KNOWLEDGE GAP  → Kullanıcı bu bilgiyi şu anda biliyor mu?
```

| Değer | Anlam |
|---|---|
| `GAP` | Yeni, belirsiz veya açıklanamayan mekanizma. |
| `KNOWN` | Kullanıcı biliyor. Evidence var. |
| `UNKNOWN` | Karar için evidence yok. |

`GAP` sinyalleri:

- concept first appearance,
- kullanıcı açıklayamıyor,
- mekanizma kritik ama anlaşılmamış,
- reusable ancak yeni,
- yanlış anlaşılması yüksek riskli,
- serious performance / failure behaviour,
- önemli statistical / causal assumption bilinmiyor.

`KNOWN` için kabul edilen evidence:

- kullanıcının açık ifadesi,
- daha önceki learning artifact (`docs/learning/passes/`, `concepts/`, `experiences/`, queue §B `RESOLVED`) bu kavramı kapsıyor.

Kural: Claude kullanıcının bilgisini tahmin etmez. Evidence yoksa değer `UNKNOWN` olur. `MUST_UNDERSTAND` + `UNKNOWN` için kullanıcıya sorulur (§16).

`IMPLEMENTATION_DETAIL` için gap değerlendirilmez. Değer `-`.

---

## 13. Event disposition

| Disposition | Anlam | Sonraki stage |
|---|---|---|
| `EXPERIENCE_ONLY` | Event değerli. Yeni teori gerekmiyor. | Knowledge Persistence (Experience Map) |
| `ULA_CANDIDATE` | Meaningful knowledge gap var. | ULA ROUTING (`04`). Light / Full burada seçilmez. |
| `KNOWLEDGE_DEBT` | Kavram öğrenmeye değer. Şimdi ertelendi. | Queue §B |
| `IMPLEMENTATION_DETAIL` | Öğrenme değeri düşük. | Yok. Pipeline biter. |
| `UNRESOLVED` | Evidence veya kullanıcı bilgisi yetersiz. | Kullanıcı kararı bekler. |

### 13.1 Disposition rule

Satır sırayla değerlendirilir. İlk eşleşen satır uygulanır.

| knowledge_priority | knowledge_gap | evidence | disposition |
|---|---|---|---|
| any | any | event'in özü `UNRESOLVED` | UNRESOLVED |
| IMPLEMENTATION_DETAIL | - | any | IMPLEMENTATION_DETAIL |
| MUST_UNDERSTAND | GAP | yeterli | ULA_CANDIDATE |
| MUST_UNDERSTAND | KNOWN | yeterli | EXPERIENCE_ONLY |
| MUST_UNDERSTAND | UNKNOWN | yeterli | UNRESOLVED |
| USEFUL_TO_KNOW | GAP | yeterli | KNOWLEDGE_DEBT |
| USEFUL_TO_KNOW | KNOWN | yeterli | EXPERIENCE_ONLY |
| USEFUL_TO_KNOW | UNKNOWN | yeterli | EXPERIENCE_ONLY |

Açıklama:

- `MUST_UNDERSTAND` + `UNKNOWN` sessizce karar almaz. Checkpoint'te kullanıcıya sorulur. Cevap yoksa `UNRESOLVED` kalır.
- `USEFUL_TO_KNOW` + `UNKNOWN` için brief reminder yeterlidir. Bu nedenle `EXPERIENCE_ONLY`.

### 13.2 User override (checkpoint)

| Kullanıcı kararı | Sonuç |
|---|---|
| `ULA_CANDIDATE` event'i şimdi öğrenmek istemiyor | `KNOWLEDGE_DEBT`, debt priority `NOW` |
| `USEFUL_TO_KNOW` event'i şimdi öğrenmek istiyor | priority `MUST_UNDERSTAND`, disposition `ULA_CANDIDATE` |
| `UNKNOWN` için "biliyorum" | gap `KNOWN`, kural tablosu tekrar uygulanır |
| `UNKNOWN` için "bilmiyorum" | gap `GAP`, kural tablosu tekrar uygulanır |

Kısıt: `IMPLEMENTATION_DETAIL` priority ile `ULA_CANDIDATE` veya `KNOWLEDGE_DEBT` olmaz. Kullanıcı isterse önce priority değişir.

---

## 14. Knowledge Debt

```text
DEFERRED WORK UNIT → ertelenmiş proje işi   (ledger, queue §A)
KNOWLEDGE DEBT     → ertelenmiş kavram      (queue §B)
```

İki kayıt ayrıdır. Birbirinin status'unu değiştirmez.

### 14.1 Debt record

Format: `templates/LEARNING_QUEUE_TEMPLATE.md` §B.

| Alan | Değer |
|---|---|
| `debt_id` | `KD-<learning-pass-id>-NN`. Pass içinde benzersiz. |
| `concept` | Canonical technical term |
| `originating_event_id` | Debt'i doğuran `event_id`. Zorunlu. |
| `work_unit_ids` | Event'in `work_unit_ids` değeri |
| `one_sentence_explanation` | Tek cümle |
| `why_it_matters` | Neden önemli |
| `priority` | `NOW` · `LATER` · `OPTIONAL` |
| `debt_status` | `OPEN` · `RESOLVED` · `DISMISSED` |
| `created_at` | `YYYY-MM-DD` |
| `concept_home` | Concept Home pointer veya `UNASSIGNED` |

Debt priority:

| Durum | priority |
|---|---|
| `MUST_UNDERSTAND` event kullanıcı tarafından ertelendi | `NOW` |
| `USEFUL_TO_KNOW` + `GAP` | `LATER` |
| Kullanıcı "isteğe bağlı" dedi | `OPTIONAL` |

### 14.2 Lifecycle (Human Sync sınırı)

- Human Sync yalnız `OPEN` kayıt oluşturur.
- `DISMISSED`: yalnız kullanıcının açık kararı ile.
- `RESOLVED`: yalnız `06_KNOWLEDGE_PERSISTENCE.md` §20 guard'ı ile. Human Sync yazmaz.
- `concept_home`: Concept Home henüz yoksa `UNASSIGNED`.
- Aynı `concept` için `OPEN` debt zaten varsa yeni kayıt açma. Mevcut kaydı kullanıcıya göster.

Queue §B bir generated view değildir. Knowledge Debt için authoritative kayıttır.

---

## 15. Coverage outcome proposal

Human Sync ledger'a yazmaz. Yalnız her selected work unit için Completion Commit'in kullanacağı **önerilen** sonucu hazırlar. Değerlendirme unit bazındadır. Scope-level sonuç bütün unit'lere zorlanmaz.

| Unit'in event'leri | Önerilen status | `open_items` |
|---|---|---|
| Event yok veya yalnız `IMPLEMENTATION_DETAIL`; evidence yeterli | `NOT_LEARNING_RELEVANT` | `-` |
| Event yok ama evidence okunamadı | Öneri yok. Unit mevcut status'unda kalır. | - |
| Bütün event'ler `EXPERIENCE_ONLY` / `KNOWLEDGE_DEBT` / `IMPLEMENTATION_DETAIL` | `COVERED` | `-` |
| En az bir `ULA_CANDIDATE` veya `UNRESOLVED` event | `PARTIAL` (sonraki stage kapatırsa `COVERED`) | Açık event ID listesi |

`open_items` kuralı:

- Yalnız event ID yazılır. Free-text tekrar yazılmaz.
- Örnek: `LE-LP-20261027-01-02; LE-LP-20261027-01-04`.
- Sonraki stage (ULA, Persistence) bir event'i kapatırsa ID listeden çıkar. Liste boşalırsa öneri `COVERED` olur.

Gerçek status değişikliği yalnız Completion Commit ile olur (`02_COVERAGE_PROTOCOL.md` §10). Completion kuralları: `04_ULA_PROTOCOL.md` §11.

---

## 16. User checkpoint

Handoff write'tan önce kullanıcıya kısa özet göster:

1. Human Synchronization çıktısı.
2. Event listesi: `event_id · title · category · priority · disposition`.
3. `MUST_UNDERSTAND` + `UNKNOWN` event'ler için soru: "Bu kavramı açıklayabilir misin?"
4. Önerilen Knowledge Debt kayıtları.
5. Coverage outcome önerisi.

Kullanıcı disposition'ı §13.2 kuralları ile değiştirebilir. Kullanıcı cevap vermezse sessiz varsayım yapma. İlgili event `UNRESOLVED` kalır.

---

## 17. Handoff write

Sıra:

```text
07 §E integrity
↓ PASS
docs/learning/passes/<learning-pass-id>/LEARNING_PASS.md yaz (templates/LEARNING_PASS_TEMPLATE.md)
↓
KNOWLEDGE_DEBT event'leri için queue §B'ye OPEN kayıt ekle
↓
Üretilen / refresh edilen unit record'ları yaz (08 §12)
↓
Knowledge view: HS + DEBT section'ları (09 §8; derived)
↓
Pipeline Handoff: Next Stage = 04 §3 early completion check
```

Kurallar:

- Integrity FAIL ise hiçbir dosya yazılmaz.
- Pass dosyası `pass_status: IN_PROGRESS` ile yazılır. Pass lifecycle: `04` §2.3, §11.5.
- Ledger yazılmaz.
- Mevcut bir pass dosyası overwrite edilmez. Devam eden pass güncellenir.
- `ULA_CANDIDATE` ve `UNRESOLVED` yoksa ULA stage'e girilmez. Early completion: `04` §3.

---

## Authoritative Source

- `00_MASTER_SYSTEM_SPEC.md` §14, §15, §16, §17, §18, §19, §36.
- Phase 1 audit: Bölüm 9, 10, Q6, Q7, Q12.
- `02_COVERAGE_PROTOCOL.md` §9, §10 (Completion Commit).
