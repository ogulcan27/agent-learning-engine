# Universal Learning Architecture — v1.0 Specification

**Kısa ad:** ULA v1.0  
**Amaç:** Bir konuyu öğrencinin önce bütünü görmesini, sonra parçaları doğal ilişkileri içinde incelemesini ve yalnız gerektiğinde teknik derinliğe inmesini sağlayacak şekilde yapılandırmak.

---

## 1. Temel fikir

ULA lineer bir ders kitabı yapısı değildir.

Temel öğrenme hareketi şudur:

\[
\boxed{
\text{Bütünü gör}
\rightarrow
\text{Parçaları ayır}
\rightarrow
\text{Mekanizmayı anla}
\rightarrow
\text{Teoriyi bağla}
\rightarrow
\text{Matematiğe / formalizme in}
}
\]

Sistem iki ana eksen kullanır:

```text
YATAY EKSEN
"Bu sistemin parçaları nasıl ilişki kuruyor?"

                →

A ───── B ───── C ───── D ───── E
│       │       │       │       │
L1      L1      L1      L1      L1
│       │       │       │       │
L2      L2      L2      L2      L2
│       │       │       │       │
L3      L3      L3      L3      L3
│       │       │       │       │
L4      L4      L4      L4      L4

                ↓

DİKEY EKSEN
"Bu parçanın içine ne kadar derin giriyorum?"
```

Yatay eksen **bütünü** korur.

Dikey eksen **derinliği** kontrol eder.

---

# 2. Ana öğrenme ilkesi: Whole Before Parts

Bir konu ilk olarak ayrıntılar üzerinden anlatılmamalıdır.

Öğrenci önce:

> “Ben şu anda neye bakıyorum?”

sorusunu cevaplayabilmelidir.

Bu nedenle ULA'da hiçbir ana konu doğrudan formül, terminoloji listesi veya detaylı teori ile başlamaz.

Önce:

```text
KONU
 ↓
ÜSTTEN GÖRÜNÜM
 ↓
ANA PARÇALAR
```

kurulur.

Sonra parçalar açılır.

---

# 3. Ana öğrenme ilkesi: Mechanism Before Theory Before Math

Standart sıra:

\[
\boxed{
\text{Ne oluyor?}
\rightarrow
\text{Nasıl oluyor?}
\rightarrow
\text{Neden böyle oluyor?}
\rightarrow
\text{Matematikte nasıl yazılıyor?}
}
\]

Yani:

```text
L1 → Simple Explanation
L2 → Mechanism
L3 → Theory
L4 → Math / Formalism
```

Formül, mümkün olduğunca mekanizma anlaşılmadan önce gösterilmez.

Amaç formülü ezberletmek değildir.

Amaç:

> formül görüldüğünde öğrencinin onun hangi mekanizmayı sıkıştırdığını anlamasıdır.

---

# 4. Ana bilgi birimi: BLOCK

ULA'nın temel tasarım birimi **sayfa değildir**.

Temel birim:

\[
\boxed{\text{BLOCK}}
\]

Bir block:

- bir işlem,
- bir kavram,
- bir sistem bileşeni,
- bir karar noktası,
- bir teori,
- bir karşılaştırma,
- veya anlamlı bir alt sistem

olabilir.

Örneğin:

```text
Neural Network
│
├── Forward Pass
├── Loss
├── Backpropagation
└── Optimizer
```

Buradaki her kutu bir block'tur.

Bir block yeterince karmaşıksa kendi içinde yeniden açılabilir.

---

# 5. Recursive Zoom

ULA'nın en önemli özelliklerinden biri budur.

\[
\boxed{
\text{Büyük block}
\rightarrow
\text{Yeni bir üstten görünüm}
}
\]

Örneğin:

```text
SYSTEM DESIGN

Client → API → Service → Database
                          │
                          ▼
                      DATABASE
```

Database'e zoom:

```text
DATABASE

Storage
  ↓
Indexing
  ↓
Replication
  ↓
Partitioning
```

Replication'a zoom:

```text
REPLICATION

Write
 ↓
Leader
 ↓
Replicas
 ↓
Failover
```

Yani sistem:

\[
\text{zoom out}
\leftrightarrow
\text{zoom in}
\]

mantığıyla çalışır.

### Recursion ne zaman yapılır?

Bir block şu durumda alt haritaya dönüşmelidir:

- birden fazla önemli iç parçaya sahipse,
- öğrencinin block'u tek parça olarak zihinde simüle etmesi zorlaşıyorsa,
- içindeki parçaların kendi ilişkileri öğrenme açısından önemliyse,
- açıklaması diğer block'lardan belirgin biçimde büyüyorsa.

Sadece “daha fazla detay yazmak” için yeni alt seviye oluşturulmaz.

---

# 6. L0 — MAP

### Soru

> **Bu konu büyük resimde nasıl çalışıyor veya nasıl organize oluyor?**

L0'ın görevi **öğretmekten önce yön buldurmaktır**.

Burada:

- ana block'lar,
- ana ilişkiler,
- gerekirse başlangıç ve sonuç,
- önemli dallanmalar

gösterilir.

Burada normalde bulunmamalı:

- uzun açıklamalar,
- formüller,
- ayrıntılı sayılar,
- kaynak numaraları,
- edge case'ler,
- teorik tartışmalar.

Örnek:

```text
NEURAL NETWORK TRAINING

Input
 ↓
Forward
 ↓
Prediction
 ↓
Loss
 ↓
Backpropagation
 ↓
Optimizer
 ↓
Updated Network
 ↺
```

L0'ı gören öğrenci:

> “Sistemin ana parçaları bunlar ve kabaca böyle bağlanıyorlar.”

diyebilmelidir.

---

# 7. L1 — SIMPLE EXPLANATION

### Soru

> **Bu block basitçe ne yapıyor?**

L1 tek kelimelik etiket değildir.

Gerçek fakat sade bir konu anlatımıdır.

Örneğin kötü:

> **Backpropagation:** gradient hesaplama.

ULA L1:

> Ağ önce bir tahmin üretir. Loss bu tahminin ne kadar hatalı olduğunu ölçer. Backpropagation, bu hatanın ağın önceki katmanlarına nasıl dağıldığını hesaplar.

### L1 yazım kuralları

L1:

- yaklaşık 2–6 kısa cümle kullanmalıdır,
- bir cümlede bir ana fikir taşımalıdır,
- mekanizmayı sezgisel olarak anlatmalıdır,
- zorunlu olmayan sembollerden kaçınmalıdır,
- teknik terimi gerektiğinde korumalıdır,
- öğrencinin block'un görevini anlayabilmesini sağlamalıdır.

Amaç:

> “Ne yaptığını biliyorum.”

seviyesi.

---

# 8. L2 — MECHANISM

### Soru

> **İçeride gerçekten ne oluyor?**

L2 sistemin mekanik davranışını açar.

Varsayılan şablon:

```text
GİRDİ
  ↓
NE OLUYOR?
  ↓
ÇIKTI
  ↓
SONRA NEREYE?
```

Gerekirse ayrıca:

> “Bu işlem neden burada?”

sorusuna kısa cevap eklenebilir.

### Örnek

```text
GRADIENT DESCENT

Girdi
current parameters + gradient

        ↓

İşlem
gradient learning rate ile ölçeklenir

        ↓

parameter ters yönde değiştirilir

        ↓

Çıktı
new parameters

        ↓

Sonra
next forward pass
```

L2'nin amacı:

> “Bu sistemi zihnimde adım adım çalıştırabiliyorum.”

seviyesine ulaşmaktır.

---

# 9. L3 — THEORY

### Soru

> **Bu mekanizma neden böyle çalışıyor?**

Gerçek teorik eğitim esas olarak burada yapılır.

L3 aşağıdaki konuları gerektiği ölçüde açıklayabilir:

```text
Temel kavramlar
Varsayımlar
Neden bu mekanizma?
Alternatifler
Kavramlar arasındaki ilişki
Ne zaman kullanılır?
Hangi koşullarda çalışır?
Nerede sorun çıkar?
Ne değildir?
Sık karıştırılan kavramlar
```

### Örnek

Gradient Descent için L3:

```text
Objective function
Gradient
Local slope
Learning rate
Convexity
Local / global minimum
Stochastic gradient
```

ve kritik ayrımlar:

```text
gradient ≠ parameter update
loss ≠ gradient
local minimum ≠ global minimum
```

### L3 yazım stili

Detay arttığı için dil gereksiz yere akademikleşmemelidir.

ULA şu dönüşümü tercih eder:

Kötü:

> “The semi-Markovian specification relaxes the implicit memoryless sojourn-time restriction…”

ULA:

> HMM'de persistence self-transition ile modellenir. Bu nedenle implied duration geometric olur. HSMM duration'ı ayrı bir model nesnesi yapar. Böylece geometric duration varsayımı zorunlu değildir.

Teknik içerik korunur.

Bilişsel yük azaltılır.

---

# 10. L4 — MATH / FORMALISM

### Soru

> **Daha önce öğrendiğim mekanizma matematikte nasıl ifade ediliyor?**

L4'te formül yalnız gösterilmez.

Her önemli formül şu dört soruya cevap vermelidir:

```text
1. Formül ne yapıyor?
2. Semboller neyi temsil ediyor?
3. Formülün parçaları mekanizmada nereye karşılık geliyor?
4. Sonuç nasıl yorumlanıyor?
```

Örneğin:

\[
\theta_{t+1}
=
\theta_t-\eta\nabla_\theta L(\theta_t)
\]

Açılım:

```text
θ_t
→ mevcut parametre

∇L
→ loss'un hangi yönde arttığını gösteren bilgi

η
→ adım büyüklüğü

−
→ gradient'in ters yönünde hareket

θ_{t+1}
→ güncellenmiş parametre
```

Sonra mekanizmaya geri bağlanır:

```text
current parameters
+
gradient
↓
update
↓
new parameters
```

### Kritik kural

Her block'ta L4 olmak zorunda değildir.

Örneğin:

- bir proje yönetimi adımı,
- bir tarihsel olay,
- bir deployment workflow,
- bir research-design kararı

anlamlı bir formüle ihtiyaç duymayabilir.

ULA formülü zorla üretmez.

---

# 11. Examples ayrı bir katman değildir

Örnekler ULA'da destek aracıdır.

Gerektiğinde özellikle L1 veya L2'de kullanılır.

Örneğin HMM:

> Bir rejimin her gün %80 ihtimalle kendisinde kaldığını düşün. HMM her gün yeniden “bir gün daha kalacak mıyım?” sorusunu uygular.

Örnek mekanizmayı anlamayı kolaylaştırıyorsa kullanılır.

Ama:

```text
L5 = Example
```

gibi zorunlu yeni bir katman oluşturulmaz.

---

# 12. R — REFERENCE LAYER

ULA'nın kritik kurallarından biri:

\[
\boxed{
R\notin L0-L4
}
\]

Reference Layer öğrenme akışının dışındadır.

Buraya taşınabilecek bilgiler:

```text
exact numerical results
source IDs
citation details
long derivations
rare formulas
audit trails
conflicting sources
edge cases
implementation notes
appendix-level material
exact parameter tables
historical notes
```

Amaç:

> Bilgiyi kaybetmeden ana öğrenme akışını temiz tutmak.

Öğrenci ihtiyaç duyarsa L1–L4'ten R'ye geçebilir.

Ama R ana öğrenme ekranını işgal etmez.

Bu, HSMM Defense Guide deneyiminden çıkan önemli bir tasarım kuralıdır.

---

# 13. Progressive Disclosure

ULA'da:

\[
\boxed{
\text{Layered information}
\neq
\text{all layers visible at once}
}
\]

Öğrenci ilk bakışta L0–L4'ün tamamıyla karşılaşmamalıdır.

Varsayılan gösterim:

```text
önce L0

↓ block seç

L1

↓ daha derine git

L2

↓ gerekirse

L3

↓ gerekirse

L4
```

PDF gibi statik formatlarda bile aynı prensip korunmalıdır.

Örneğin:

```text
Sayfa 1 → map
Sayfa 2 → block A simple explanation
Sayfa 3 → block A mechanism
Sayfa 4 → block A theory/math
```

yerleşimi, tek sayfaya her şeyi sıkıştırmaktan genellikle daha uygundur.

---

# 14. Horizontal Relationship Rule

Her konu doğal olarak bir “flow” değildir.

ULA yatay ilişki türünü konuya göre seçmelidir.

Örneğin:

```text
Sequence:
A → B → C

Hierarchy:
A
├── B
├── C
└── D

Feedback:
A → B → C
↑       ↓
└───────┘

Comparison:
A ↔ B

Causal:
Cause → Mechanism → Outcome

Dependency:
A
├─requires→ B
└─requires→ C
```

Doğal olmayan bir flow zorla oluşturulmaz.

---

# 15. Topic Adapters

ULA'nın üst mimarisi evrenseldir.

Ancak her alan aynı yatay alt şablonu kullanmaz.

## A. Process / Algorithm

```text
Input
→ Operation
→ Decision
→ Output
→ Loop
```

Örnek:

- EM,
- neural network training,
- ETL,
- compiler pipeline.

---

## B. Statistical / ML Model

```text
Data
→ Representation
→ Model
→ Fit
→ Predict / Infer
→ Evaluate
```

Örnek:

- Regression,
- HMM,
- Random Forest,
- Neural Network.

---

## C. System / Software Architecture

```text
Actor
→ Entry
→ Components
→ Data Flow
→ Storage
→ Response
```

Sonra:

- scale,
- reliability,
- security,
- bottlenecks

gibi block'lar açılır.

---

## D. Mathematical Theory

Lineer process zorlanmaz.

Varsayılan:

```text
Problem
→ Assumptions
→ Objects
→ Claim
→ Why it works
→ Consequences
→ Examples
```

Proof gerekiyorsa:

```text
Proof Architecture
├── idea
├── intermediate result
└── conclusion
```

---

## E. Quantitative Finance

Örneğin pricing:

```text
Instrument
→ Underlying
→ Market assumptions
→ Stochastic model
→ Pricing logic
→ Price
→ Hedge / Risk
```

Portfolio konusu farklı adapter kullanabilir:

```text
Assets
→ Return / Risk
→ Dependence
→ Objective
→ Constraints
→ Allocation
→ Evaluation
```

---

## F. Research Paper / Research Project

```text
Question
→ Data
→ Method
→ Experimental Design
→ Evidence
→ Diagnostics
→ Claims
→ Limitations
```

HSMM çalışması bu adapter'ın örneğidir.

---

## G. Historical / Causal Subject

```text
Context
→ Actors
→ Pressures
→ Events
→ Causal branches
→ Outcome
→ Consequences
```

---

## H. Skill / Procedure

```text
Goal
→ Preconditions
→ Action
→ Feedback
→ Correction
→ Completion
```

---

# 16. Topic Type Inference

Bir AI, yeni bir konu aldığında doğrudan içerik yazmaya başlamamalıdır.

Önce:

> “Bu konu hangi yapıya sahip?”

sorusunu cevaplamalıdır.

Tek adapter yeterli değilse hibrit kullanılabilir.

Örneğin Black-Scholes:

```text
Mathematical Theory
+
Quant Pricing
+
Stochastic Process
```

olabilir.

System Design interview:

```text
System Architecture
+
Decision Process
```

olabilir.

ULA adaptasyon yapar.

Şablonu körü körüne uygulamaz.

---

# 17. One Concept — One Home

Aynı teori her yerde yeniden tam anlatılmaz.

Her önemli kavramın bir **Home** noktası vardır.

Örneğin:

```text
Gradient Descent
HOME → Optimisation
```

Neural Network içinde:

```text
Gradient Descent
Home: Optimisation
Buradaki görevi:
network loss'u azaltmak için parameters'ı güncellemek.
```

Ama gradient descent teorisi yeniden sıfırdan yazılmaz.

Başka örnek:

```text
Brownian Motion
HOME → Stochastic Processes
```

Black-Scholes:

> Buradaki görevi underlying fiyatının random component'ini modellemektir.

Bu kural:

- tekrarı azaltır,
- not şişmesini önler,
- konular arasında bağ kurar,
- uzun vadeli knowledge graph üretir.

---

# 18. Concept Registry

Büyük çalışma sistemlerinde kavramların Home noktaları bir registry'de tutulabilir.

Örneğin:

```text
C001 Gradient Descent
Home: Optimisation / Gradient Methods

C002 Brownian Motion
Home: Stochastic Processes

C003 EM
Home: Latent Variable Estimation

C004 Regularisation
Home: Statistical Learning / Model Control
```

Bir konu aynı kavramı kullanırsa registry'ye referans verir.

---

# 19. Writing Standard — ULA Simple Technical English / Turkish Style

ULA içeriği mümkün olduğunca **ASD-STE100 benzeri sade teknik anlatım** kullanmalıdır.

Temel kurallar:

- kısa cümle,
- bir cümlede bir ana fikir,
- aktif yapı tercih edilir,
- aynı kavram için aynı terim kullanılır,
- eş anlamlı teknik terimlerle gereksiz çeşitlilik yapılmaz,
- teknik İngilizce terim gerekiyorsa korunabilir,
- açıklama kullanıcının çalışma dilinde yapılır,
- soyut isim yığını yerine işlem anlatılır,
- gereksiz akademik süs kullanılmaz.

Örneğin kötü:

> Regularisation serves as a mechanism whereby parameter flexibility may be constrained in accordance with a predefined reference architecture.

ULA:

> Regularisation modelin serbestliğini sınırlar. Burada duration PMF'yi geometric referansa doğru çeker.

---

# 20. Canonical Vocabulary

Bir içerik içinde aynı nesne farklı isimlerle çağrılmamalıdır.

Örneğin:

```text
duration PMF
```

seçildiyse sürekli:

- dwell table,
- duration table,
- sojourn array,
- state duration vector

gibi isimlere rastgele geçilmez.

Alternatif isim gerekliyse ilk tanımda belirtilir.

Sonra canonical term kullanılır.

---

# 21. Boundary Statements

ULA yalnızca “nedir?” anlatmaz.

Önemli yerlerde:

```text
A ≠ B
```

ayrımları açıkça gösterilir.

Örnek:

```text
correlation ≠ causation

validation ≠ test

gradient ≠ parameter update

smoothed probability ≠ ground truth

replication ≠ backup

authentication ≠ authorization
```

Bu ayrımlar L2 veya L3'te görünmelidir.

---

# 22. “Ne değildir?” kuralı

Yanlış zihinsel model oluşturma riski varsa block şu soruya cevap vermelidir:

> **Bu kavram ne değildir?**

Örneğin:

> Viterbi günlük posterior argmax değildir.

> Redis yalnızca “hızlı database” değildir.

> Sharpe ratio toplam getiri değildir.

> Docker VM değildir.

Bu özellikle benzer kavramların çok olduğu alanlarda önemlidir.

---

# 23. Learning Routes

Aynı mimari farklı çalışma sürelerinde kullanılmalıdır.

### Quick View

```text
L0
+
L1
```

Amaç:

> Konunun yerini ve ana hikâyesini görmek.

---

### Standard Study

```text
L0
+
L1
+
L2
```

Amaç:

> Sistemi zihinde çalıştırabilmek.

---

### Deep Study

```text
L0
→
L1
→
L2
→
L3
→
L4
```

Amaç:

> teknik hakimiyet.

---

### Reference Mode

```text
Block
→
R
```

Amaç:

> sayı, kaynak, edge case veya detay bulmak.

---

# 24. Retrieval Mode

Öğrenme yalnızca okuma değildir.

Bir konu çalışıldıktan sonra öğrenci sistemi **yeniden üretmelidir**.

Önerilen retrieval zinciri:

```text
1. L0 haritasını kapat.
2. Ana block'ları kendin çiz.
3. Block'ların bağlantısını anlat.
4. Bir block seç.
5. L1'i kendi cümlelerinle anlat.
6. L2 mekanizmasını çiz.
7. L3 teorisini açıkla.
8. Gerekirse L4 formülünü mekanizmaya bağla.
```

Bu özellikle:

- sınav,
- interview,
- oral defense,
- presentation

için kullanılabilir.

---

# 25. Formula Rule

Her formül üç sınıftan birine ayrılabilir:

### Core

Mekanizmayı anlatmak için gerekli.

### Recognise

Görünce ne olduğunu bilmek yeterli.

### Reference

Nadiren gerekir. Ana öğrenme akışında bulunmaz.

Bu sayede öğrencinin:

> “Bu 40 formülün hepsini ezberlemem gerekiyor.”

yanılgısı azaltılır.

---

# 26. Number Density Rule

Exact numbers yalnızca öğrenme açısından işlevliyse ana katmanda tutulmalıdır.

Örneğin:

> “Dataset 1 milyon satır.”

mimariyi anlamak için önemli olabilir.

Ama:

> “Score = 2626.6978”

mekanizmayı anlamak için gerekli değilse Reference'a gider.

Sayılar öğrenme akışını domine etmemelidir.

---

# 27. Source-Based Learning Rule

Bir konu belirli kaynaklardan öğreniliyorsa ULA kaynakları değiştirmemelidir.

Sistem:

```text
source says X
→ ULA explains X clearly
```

yapmalıdır.

Şunu yapmamalıdır:

```text
source says X
→ AI silently replaces it with Y
```

Kaynak çatışması varsa:

> çatışma korunur ve Reference Layer'da belirtilir.

Bilgi eksikse:

> boşluk açıkça belirtilir.

AI boşluğu uydurmaz.

---

# 28. Architecture Before Content

ULA ile içerik üretirken ilk aşama **ders yazmak değildir**.

Sıra:

```text
1. Learning goal
2. Topic type
3. L0 map
4. Main blocks
5. Recursive submaps
6. L1–L4 allocation
7. Concept homes
8. Reference boundary
9. Architecture review
10. Content production
```

Mimari onaylanmadan uzun içerik üretilmemelidir.

Bu bizim HSMM deneyiminden çıkardığımız en önemli üretim kurallarından biri.

---

# 29. Architect ve Builder ayrı roller olmalıdır

AI workflow'u tercihen iki ayrı aşamada yürütülür.

## Role 1 — Learning Architect

Görevi:

```text
konuyu analiz et
↓
doğal yapısını bul
↓
L0 oluştur
↓
block'ları belirle
↓
recursive zoom noktalarını seç
↓
L1–L4 planını oluştur
```

**Uzun ders anlatımı yazmaz.**

---

## Role 2 — Learning Content Builder

Onaylanmış architecture'ı alır.

Sonra:

```text
L1 explanation
L2 mechanism
L3 theory
L4 math
Reference
```

içeriğini üretir.

**Architecture'ı kendi başına yeniden tasarlamaz.**

---

# 30. Üçüncü rol: Learning Auditor

Builder bittikten sonra Auditor kontrol eder:

```text
Büyük resim önce geliyor mu?
Mekanizma teoriden önce mi?
Formüller doğru katmanda mı?
Sayfa / ekran aşırı yoğun mu?
Aynı kavram tekrarlanıyor mu?
Block'lar doğal mı?
Recursive zoom doğru yerde mi?
A ≠ B sınırları yeterli mi?
Reference ana akışı işgal ediyor mu?
ASD-style dil korunmuş mu?
```

Auditor konu içeriğinin yanında **öğrenme UX'ini** de denetler.

---

# 31. Presentation Rule

ULA içerik mimarisi ile görsel tasarım aynı şey değildir.

Önce bilgi mimarisi oluşturulur.

Sonra:

- PDF,
- HTML,
- notebook,
- web app,
- handwritten notes,
- slides

gibi formatlardan biri seçilebilir.

Format mimariyi değiştirmemelidir.

Örneğin aynı ULA konusu:

```text
interactive HTML
→ block'a tıklayınca zoom

PDF
→ progressive pages

tablet notes
→ foldable tree

web app
→ expandable graph
```

olarak gösterilebilir.

---

# 32. Visual Density Rule

Bir ekran veya sayfada kullanıcı:

> “Önce nereye bakacağım?”

diye düşünüyorsa tasarım yeniden incelenmelidir.

Varsayılan hedef:

```text
1 dominant idea
+
1 dominant visual
+
az sayıda supporting explanation
```

Tek sayfada:

- overview,
- 5 kart,
- 3 tablo,
- formüller,
- source conflicts,
- exact scores

toplanmamalıdır.

---

# 33. ULA Anti-Patterns

Aşağıdaki davranışlar ULA'ya aykırıdır:

```text
✕ Formül ile başlamak

✕ Kitap sırasını otomatik olarak öğrenme sırası kabul etmek

✕ Her şeyi aynı anda göstermek

✕ Her konuya zorla flow uygulamak

✕ Bir block'u aşırı büyütüp zoom yapmamak

✕ Aynı teoriyi farklı konularda yeniden uzun uzun anlatmak

✕ Reference bilgisini ana öğrenme akışına doldurmak

✕ L1'i yalnızca bir kelimelik label yapmak

✕ L3'ü akademik jargon yığınına dönüştürmek

✕ Formülü açıklamadan göstermek

✕ Bir kaynak boşluğunu AI bilgisiyle sessizce doldurmak

✕ Her ayrıntıyı “must know” ilan etmek
```

---

# 34. Acceptance Test

Bir ULA çıktısı tamamlandığında öğrenci şu soruları cevaplayabilmelidir:

```text
Bu konu ne yapıyor?

Ana parçaları neler?

Bu parçalar nasıl bağlanıyor?

Bir block'un içine girdiğimde mekanizma nasıl çalışıyor?

Bu mekanizmanın teorik nedeni ne?

Formül mekanizmanın hangi kısmını ifade ediyor?

Benzer kavramlardan farkı ne?

Hangi ayrıntılar core, hangileri reference?

Bu block büyük sistemde nereye ait?

Bu haritayı kendim yeniden çizebilir miyim?
```

Bu soruların çoğuna cevap verilemiyorsa içerik tamamlanmış sayılmaz.

---

# 35. ULA'nın kısa tanımı

Bütün specification'ı tek paragrafta sıkıştırırsak:

> **Universal Learning Architecture, bir konuyu önce kuş bakışı bir sistem olarak gösteren, sonra doğal block'lara ayıran ve öğrencinin seçtiği block'a kontrollü biçimde zoom yapmasını sağlayan recursive bir öğrenme mimarisidir. Her block basit açıklama, mekanizma, teori ve matematik sırasıyla derinleşir. Büyük block'lar kendi alt haritalarına dönüşebilir. Aynı kavram tek bir Home altında tam anlatılır. Reference bilgisi ana öğrenme akışından ayrı tutulur. Mimari konu türüne göre adapte edilir; ancak whole-before-parts, mechanism-before-theory-before-math ve progressive disclosure ilkeleri değişmez.**

Ve sistemi tek görselde özetlersek:

```text
                         [ KONU ]
                            │
                            ▼
                    L0 · BIG PICTURE
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          BLOCK A         BLOCK B         BLOCK C
             │              │              │
             │         [çok büyük mü?]     │
             │              │              │
             │              ▼              │
             │       YENİ ALT HARİTA       │
             │                              │
             ▼                              ▼
       L1 · BASİT ANLATIM             L1 · BASİT ANLATIM
             │                              │
             ▼                              ▼
       L2 · MEKANİZMA                 L2 · MEKANİZMA
             │                              │
             ▼                              ▼
       L3 · TEORİ                     L3 · TEORİ
             │                              │
             ▼                              ▼
       L4 · MATEMATİK                 L4 · MATEMATİK

                       gerektiğinde
                            │
                            ▼
                       R · REFERENCE
```

Bence **ULA v1.0'ın çekirdeği artık yeterince net**. Bundan sonraki adım, bunu daha fazla teorileştirmek değil. Bu specification'dan üç operasyonel araç üretmek: **Learning Architect Prompt**, **Learning Content Builder Prompt** ve **Learning Auditor Prompt**. Ardından bu üçlüyle HSMM'ye geri dönüp P1–P9'u yeni sisteme göre üretebiliriz.