# 02 — Coverage Protocol

**Status:** IMPLEMENTED (Phase 3)

## Purpose

`/learning` çağrıları arasında project work unit'lerinin learning coverage durumunu takip eder.

## Responsibility

- Work unit discovery ve normalization.
- Coverage ledger kuralları.
- Gap detection.
- Scope resolution.
- Status transitions.
- State ve queue rebuild.

## Must Not

- Human Synchronization, Knowledge Priority, ULA, MindMap veya Concept Home işi yapmaz.
- `COVERED`, `PARTIAL` veya `NOT_LEARNING_RELEVANT` durumunu kendi başına yazmaz. Bu durumlar yalnız Completion Commit ile yazılır (Bölüm 10).
- Mevcut bir state dosyasını overwrite etmez.

---

## 1. Authority model

| Dosya | Rol | Authority |
|---|---|---|
| `LEARNING_CONFIG.md` | Project preferences | Kullanıcı tercihi |
| `COVERAGE_LEDGER.md` | Coverage truth | **Authoritative** |
| `LEARNING_STATE.md` | Runtime summary | Derived. Ledger'dan yeniden üretilir. |
| `LEARNING_QUEUE.md` §A | Open-item view | Derived. Ledger'dan yeniden üretilir. |

Kural: Coverage truth lives in `COVERAGE_LEDGER.md`.

Çelişki varsa ledger kazanır. State ve queue ledger'dan yeniden üretilir.

---

## 2. Work unit model

Ledger'da her work unit tek bir satırdır.

| Alan | Anlam |
|---|---|
| `work_unit_id` | Normalized kalıcı ID (Bölüm 4). Ledger içinde benzersiz. |
| `seq` | Source'un doğal sırasındaki pozisyon. Tam sayı. Aynı `source_type` içinde benzersiz. |
| `label` | Kısa insan-okunur ad. |
| `source_type` | `user` · `jira` · `phase-doc` · `git` · `other` |
| `source_ref` | Evidence pointer: issue key, commit hash + subject, doküman path + step başlığı. |
| `status` | Bölüm 7 status vocabulary. |
| `discovered_at` | İlk discovery tarihi (`YYYY-MM-DD`). |
| `last_evaluated_at` | Son status değişikliği tarihi. Boş olabilir. |
| `learning_pass_id` | `LP-YYYYMMDD-NN`, `EXTERNAL` veya boş. |
| `open_items` | Yalnız `PARTIAL` için açık learning item listesi. Diğer durumlarda `-`. |
| `notes` | Kısa not. `DEFERRED` için reason, `SKIPPED_BY_USER` için kullanıcı gerekçesi. |

`seq` neden gerekir: `latest` ve aralık seçimi bir sıra ister. Sıra source'un kendi sırasından gelir. Dosya sırası veya ad sıralaması kullanılmaz.

---

## 3. Source resolution

### 3.1 Discovery ≠ authority

- **Discovery:** Work unit'leri project evidence içinde bulmak.
- **Authority:** Hangi work unit'in seçileceğine karar vermek.

Explicit user scope her zaman en yüksek authority'dir. Discovery sonucu kullanıcı kararını override etmez.

### 3.2 Universal priority

```text
1. Explicit user scope
2. Project-configured work unit source   (LEARNING_CONFIG → work_unit_source)
3. Jira / issue tracker, erişilebiliyorsa
4. Persistent task / phase document
5. Git commit / commit range
6. Other stable identifier
7. Ambiguous → ask user
```

### 3.3 `work_unit_source` değerleri

| Değer | Davranış |
|---|---|
| `auto` | Bölüm 3.4 |
| `jira` | Issue key'ler work unit'tir. |
| `phase-doc` | Persistent doküman içindeki numaralı phase / step'ler work unit'tir. |
| `git` | Commit'ler work unit'tir. |
| Diğer değer | **CONFIG ERROR.** Kullanıcıya bildir. Dur. Fallback yapma. |

Configured source evidence vermezse (ör. `git` seçili ama repository git değil): **CONFIG ERROR**. Dur.

### 3.4 Auto mode

Sıra:

```text
explicit user scope
↓
available stable issue/task source
↓
persistent phase/task documentation
↓
git
↓
other stable source
↓
ambiguous → ask user
```

Kurallar:

1. Bir source yalnız teknik olarak mevcut diye seçilmez. Projenin işi gerçekten o birimlerle ilerlemelidir.
2. Issue source sinyali: issue key'ler commit mesajlarında, branch adlarında veya planning dokümanlarında tutarlı biçimde görünür. Tracker API erişimi zorunlu değildir. Erişim yalnız label'ı zenginleştirir.
3. Phase-doc sinyali: Bir doküman numaralı phase / step listesi tutar ve iş bu listeye göre ilerler.
4. Git sinyali: Commit'ler anlamlı ve ayrık iş birimleridir. Commit mesajları anlamsızsa (ör. "wip", "fix") git düşük kaliteli kaynaktır.
5. Birden fazla güçlü aday varsa: **ambiguous**. Kullanıcıya sor.
6. Auto sonucu ilk kez bulunduysa veya önceki çağrıdan farklıysa: Sonucu kullanıcıya göster ve onay iste. Kullanıcı isterse değeri `LEARNING_CONFIG.md` içine sabitle.
7. Sonuç önceki çağrı ile aynı ve tek anlamlıysa: Soru sorma. Devam et.

### 3.5 Forbidden authority signals

Aşağıdakiler work unit boundary veya coverage kararı için tek başına kullanılmaz:

- file modification time,
- chat memory alone,
- directory listing order,
- arbitrary filename sort,
- Claude inference without persistent evidence.

Bu sinyaller yalnız yardımcı evidence olabilir.

---

## 4. Work unit normalization

ID formatı: `<source_type>:<native-id>`

| Source | Native ID | Örnek | `seq` kaynağı |
|---|---|---|---|
| `jira` | Issue key, büyük harf | `jira:ABC-44` | Issue'nun ilk görüldüğü commit / doküman sırası |
| `phase-doc` | Doküman path + step ID (dokümanda yazıldığı gibi) | `phase-doc:PLAN.md#step-10` | Doküman içindeki sıra |
| `git` | Commit hash'in ilk 12 karakteri, küçük harf | `git:3f2a9c1d0b7e` | Commit tarihi sırası (ancestry) |
| `user` | Kullanıcının verdiği kısa slug | `user:cache-redesign` | Kayıt sırası |
| `other` | Stabil identifier (PR no, tag, ADR ID) | `other:PR-118` | Source'un kendi sırası |

Kurallar:

1. Aynı iş bir kez kaydedilir. Birden fazla commit tek bir issue'ya aitse work unit issue'dur. Commit'ler `source_ref` içinde listelenir.
2. `git` için `source_ref` hash + commit subject içerir. Rebase sonrası hash kaybolursa subject ile eşleştirme önerilir. Karar kullanıcıya aittir.
3. Native ID değişmez. Label değişebilir.

---

## 5. Ledger record rules

1. Ledger'da tek canonical kayıt yapısı vardır: **Work Units** tablosu.
2. Open / Skipped / Closed listeleri dosyada saklanmaz. Her çağrıda tablodan hesaplanır.
3. Satır silinmez. Status değişir.
4. Yeni discovery satırı `UNCOVERED` ile eklenir.

---

## 6. Gap detection

```text
OPEN COVERAGE   = UNCOVERED ∪ PARTIAL ∪ DEFERRED
DEFAULT HIDDEN  = COVERED ∪ SKIPPED_BY_USER ∪ NOT_LEARNING_RELEVANT
```

- `show skipped` argümanı `SKIPPED_BY_USER` birimlerini ayrı listede gösterir.
- `last_covered_boundary` (en yüksek `seq` ile COVERED birim) yalnız bilgi amaçlıdır. Gap kaynağı değildir.

Adımlar:

1. Configured / resolved source üzerinden current work unit listesini çıkar.
2. Ledger'da olmayan birimleri `UNCOVERED` olarak ekle (Discovery Commit, Bölüm 10).
3. OPEN COVERAGE'ı ledger'dan hesapla.

---

## 7. Status vocabulary

| Status | Anlam | Default gap'te |
|---|---|---|
| `UNCOVERED` | Keşfedildi. Henüz değerlendirilmedi. | Görünür |
| `COVERED` | Learning pass başarıyla tamamlandı. | Görünmez |
| `PARTIAL` | Bazı learning item'lar işlendi. `open_items` açık. | Görünür (yalnız `open_items`) |
| `DEFERRED` | Kullanıcı scope'u dışında kaldı. | Görünür |
| `SKIPPED_BY_USER` | Kullanıcı açıkça "learning açısından işleme" dedi. | Görünmez; `show skipped` ile görünür |
| `NOT_LEARNING_RELEVANT` | Değerlendirildi. Yalnız routine implementation detail var. | Görünmez |

```text
DEFERRED ≠ SKIPPED_BY_USER
```

- `DEFERRED` geri gelir. Karar scope seçiminden doğar.
- `SKIPPED_BY_USER` geri gelmez. Karar kullanıcının açık ifadesinden doğar.

`NOT_LEARNING_RELEVANT` Knowledge Priority (`03` §11) sonucu ile Completion Commit (`04` §11) tarafından yazılır. Discovery bu durumu otomatik atamaz.

---

## 8. Scope resolution

### 8.1 Argument mapping

| Argüman | Selected scope | Soru |
|---|---|---|
| `latest` | En yüksek `seq` ile current work unit | Sorma |
| `catch-up` | `UNCOVERED ∪ PARTIAL ∪ DEFERRED` | Sorma |
| `pending` | `DEFERRED ∪ PARTIAL` | Sorma |
| `show skipped` | Yalnız listeleme | Scope menüsüne geç |
| `<work-unit-id>` / aralık | Eşleşen birimler | Eşleşme yoksa veya birden fazla anlam varsa sor |
| (boş) | — | OPEN COVERAGE varsa menüyü göster |

`catch-up` ve `pending` `SKIPPED_BY_USER` birimlerini otomatik almaz.

Argüman ile ledger çelişirse sor. Örnekler:

- `latest` birimi zaten `COVERED`: Kullanıcıya bildir. Menüyü göster.
- ID ledger'da `SKIPPED_BY_USER`: Yeniden açmak isteyip istemediğini sor.
- ID hiçbir source'ta yok: Tahmin etme. Sor.

### 8.2 Summary

Ardışık `seq` değerleri aralık olarak yazılır.

```text
Learning coverage gap bulundu.

Covered:   Step 1–3
Open:      Step 4–10
Deferred:  Step 4–9
Partial:   —
Current:   Step 10
Skipped:   1 birim (show skipped ile görünür)
```

### 8.3 Menu

```text
1. Yalnız son work unit'i işle.
2. Belirli work unit veya aralığı işle.
3. Tüm açık coverage'ı işle.
4. Pending / deferred queue'yu işle.
5. Custom scope belirt.
```

Seçenek 5: Kullanıcının serbest metni mevcut birimlerle eşleştirilir. Eşleşme yoksa kullanıcı onayı ile yeni `user:` work unit oluşturulur.

Kullanıcı bu adımda birimleri açıkça skip edebilir. Bu işlem `SKIPPED_BY_USER` yazar.

### 8.4 Unselected units

Scope seçildikten sonra:

| Seçilmeyen birimin durumu | Sonuç |
|---|---|
| `UNCOVERED` | → `DEFERRED`. `notes` = "not selected: <argüman veya menü seçimi>" |
| `PARTIAL` | Değişmez. `open_items` korunur. |
| `DEFERRED` | Değişmez. |

Örnek — `latest`:

```text
Önce:  1–3 COVERED, 4–10 UNCOVERED
Sonra: 10 selected (UNCOVERED kalır), 4–9 DEFERRED
```

Step 4–9 kaybolmaz. Sonraki `/learning` çağrısında OPEN COVERAGE içinde görünür.

### 8.5 First run baseline

Ledger boşsa ve discovery çok sayıda geçmiş birim bulursa kullanıcıya sor:

```text
Geçmiş iş için baseline seçin:
1. Hepsini UNCOVERED olarak ekle.
2. <ID> öncesini SKIPPED_BY_USER olarak ekle (note: baseline).
3. Daha önce öğrenilmiş birimleri COVERED olarak işaretle (learning_pass_id: EXTERNAL).
```

Seçenek 3 yalnız kullanıcının açık beyanı ile kullanılır.

---

## 9. Status transitions

Satır = önceki status. Sütun = yeni status.

| From \ To | UNCOVERED | COVERED | PARTIAL | DEFERRED | SKIPPED_BY_USER | NOT_LEARNING_RELEVANT |
|---|---|---|---|---|---|---|
| (yeni satır) | D | B¹ | — | — | B | — |
| UNCOVERED | — | C | C | S | U | C |
| DEFERRED | — | C | C | S² | U | C |
| PARTIAL | — | C | C³ | U | U | — |
| COVERED | — | — | — | — | — | — |
| SKIPPED_BY_USER | U⁴ | — | — | — | — | — |
| NOT_LEARNING_RELEVANT | U⁴ | — | — | — | — | — |

Tetikleyici kodları:

| Kod | Tetikleyici | Commit |
|---|---|---|
| D | Discovery | Discovery Commit |
| B | First run baseline (kullanıcı onayı) | Discovery Commit |
| S | Scope resolution (seçilmeyen birim) | Scope Commit |
| U | Explicit user decision | Scope Commit |
| C | Learning pipeline başarıyla bitti + integrity PASS | Completion Commit |

Notlar:

1. ¹ `learning_pass_id: EXTERNAL` zorunlu.
2. ² Yeniden erteleme. Yalnız `notes` güncellenir.
3. ³ `open_items` güncellenir.
4. ⁴ Yalnız kullanıcı birimi açıkça yeniden açarsa.
5. `COVERED` terminal durumdur.
6. Tabloda olmayan transition **geçersizdir**. Yazma yapılmaz. Integrity FAIL üretilir (`07_INTEGRITY_CHECKS.md`, C-10).

---

## 10. Commit points

Ledger yalnız üç noktada yazılır.

| Commit | Ne zaman | Yazılan |
|---|---|---|
| Discovery Commit | Gap detection sonrası | Yeni `UNCOVERED` satırlar; baseline satırları |
| Scope Commit | Kullanıcı scope'u onayladıktan sonra | `DEFERRED` (seçilmeyen), `SKIPPED_BY_USER`, reopen |
| Completion Commit | Learning pipeline başarıyla bitti ve integrity PASS | `COVERED`, `PARTIAL`, `NOT_LEARNING_RELEVANT` + `learning_pass_id` |

`COVERED` yazma sırası:

```text
selected scope
↓
learning pipeline success
↓
integrity check PASS
↓
COVERED
```

Pipeline yarıda kesilirse Completion Commit yapılmaz. Selected birimler önceki durumunda kalır.

Her commit sonrası:

1. `LEARNING_STATE.md` ledger'dan yeniden üretilir.
2. `LEARNING_QUEUE.md` §A ledger'dan yeniden üretilir.
3. Coverage integrity checks çalışır.

---

## 11. First run initialization

Startup'ta `docs/learning/state/` veya içindeki dört dosyadan biri yoksa:

1. Kullanıcıya initialization gerektiğini bildir. Eksik dosyaları listele.
2. Kullanıcı onayı olmadan dosya oluşturma.
3. Onay varsa yalnız **eksik** dosyaları template'ten oluştur. Mevcut dosyayı overwrite etme.
4. Şu klasörleri oluştur: `state/`, `passes/`, `experiences/`, `concepts/`, `maps/`, `audits/`.
5. Template placeholder'larını doldur: project adı, tarih.
6. Discovery'ye geç. Gerekirse baseline sor (Bölüm 8.5).

---

## Authoritative Source

- Phase 1 audit: Bölüm 7, 8, 8.1A, 21 (Q3, Q4, Q5, Q11, Coverage model, LEARNING_CONFIG).
- Master kaynakta coverage kavramı yoktur (ABSENT). Bu protocol yeni bileşendir.
