---
role: Authoritative master archive
runtime_loading: NEVER BY DEFAULT
source: StudySystem_WithAI.txt
authority_domain: project-learning (Phase 1 Q1)
---

> Bu dosya `StudySystem_WithAI.txt` kaynağının değiştirilmemiş arşiv kopyasıdır.
> Runtime sırasında otomatik yüklenmez. Yalnız ambiguity, audit, maintenance veya explicit deep verification için okunur.
> Manual invocation ve coverage kuralları bu dosyada değil, `SKILL.md` ve `references/01`–`07` içindedir.

# AI DESTEKLİ DATA SCIENCE + SYSTEM DESIGN + PROBLEM-PATTERN DSA + ULA ÖĞRENME SİSTEMİ

## 1. ANA AMAÇ

Amaç, Data Science, Machine Learning, System Design, Software Engineering ve DSA konularını birbirinden ayrı dersler gibi bitirmek değildir.

Amaç gerçek projeler geliştirirken:

- Data Science / ML problemlerini çözmek,
- gerçek uygulamalar geliştirmek,
- System Design kararları vermek,
- gerektiğinde Data Structures & Algorithms kullanmak,
- AI coding agent'larını etkili biçimde yönetmek,
- AI'ın yaptığı teknik işi gerçekten anlamak,
- projelerden kalıcı teknik bilgi üretmek,
- tekrar kullanılabilir mental modeller geliştirmek,
- CV ve portföye konabilecek çalışan ürünler ortaya çıkarmaktır.

Temel hedef:

> **AI'ın üretim hızından yararlanırken teknik anlayışı kaybetmemek.**

Bu nedenle proje yalnızca ürün üretme aracı değildir.

Her proje aynı zamanda:

> **kişisel mühendislik ve öğrenme laboratuvarıdır.**

---

# 2. SİSTEMİN TEMEL MİMARİSİ

Sistem birbirine bağlı altı katmandan oluşur.

```text
REAL PROJECT / DATA PROBLEM
        │
        ▼
DATA SCIENCE / ML
        │
        │ Problemi ve hedefi tanımlar.
        ▼
SYSTEM DESIGN
        │
        │ Çözümün sistem içindeki yerini belirler.
        ▼
DSA / COMPUTATIONAL THINKING
        │
        │ Gerekiyorsa hesaplama yapısını çözer.
        ▼
AI-ASSISTED ENGINEERING
        │
        │ Çözümü araştırır, üretir ve uygular.
        ▼
HUMAN SYNCHRONIZATION
        │
        │ AI'ın yaptığı işi insanın yönetebileceği
        │ mental modele sıkıştırır.
        ▼
ULA LEARNING
        │
        │ Öğrenilmesi gereken kritik bilgiyi
        │ doğru zihinsel sırayla öğretir.
        ▼
EXPERIENCE MAPS / TECHNICAL LIBRARY
        │
        ▼
REUSABLE KNOWLEDGE
```

Bu katmanlar ayrı dersler değildir.

Aynı proje içinde birbirlerini beslerler.

---

# 3. ANA ÖĞRENME FELSEFESİ

Eski yaklaşım:

```text
System Design öğren
→ DSA öğren
→ Software Engineering öğren
→ sonra proje yap
```

Yeni yaklaşım:

```text
Gerçek proje yap
→ gerçek problem ortaya çıksın
→ problemi tanı
→ alternatifleri üret
→ trade-off'ları değerlendir
→ çözümü seç
→ AI ile uygula
→ test et
→ sonucu gözlemle
→ yapılan işi insan için sıkıştır
→ öğrenme değeri olan bilgiyi seç
→ ULA ile öğren
→ Experience Map'e ekle
→ tekrar kullan
```

Ana döngü:

```text
PROBLEM
↓
UNDERSTAND
↓
DESIGN
↓
SELECT
↓
IMPLEMENT
↓
VERIFY
↓
SYNCHRONIZE
↓
LEARN
↓
DOCUMENT
↓
REUSE
```

Ana prensip:

> **Önce ihtiyaç ortaya çıkar. Sonra teori o ihtiyeti açıklamak için öğrenilir.**



# 3A. PRIMARY LEARNING AXIS — SYSTEM DESIGN THROUGH PROJECTS

Bu sistem birçok alanı birlikte kullanır.

Ancak ana mühendislik öğrenme ekseni:

> **Gerçek Data Science / ML projeleri içinde System Design öğrenmektir.**

Bu nedenle katmanların rolleri eşit değildir.

```text
DATA SCIENCE / ML
→ gerçek problemi ve domain bağlamını üretir.

SYSTEM DESIGN
→ ANA ENGINEERING LEARNING AXIS'tir.
→ çözümün gerçek sistem içinde nasıl yaşayacağını öğretir.

DSA
→ System Design veya Data Science problemi içinde
  computational ihtiyaç ortaya çıktığında kullanılan
  problem-pattern toolbox'ıdır.

SOFTWARE / PRODUCTION ENGINEERING
→ seçilmiş tasarımın gerçek sistemde uygulanmasını sağlar.

AI
→ araştırma ve implementation kapasitesini büyütür.

HUMAN SYNCHRONIZATION
→ AI'ın hızlı ürettiği işi insanın yönetebileceği
  mental modele sıkıştırır.

ULA
→ öğrenilmesine karar verilen System Design,
  DSA veya ilgili teknik bilgiyi doğru zihinsel
  sırayla öğretir.

EXPERIENCE MAP
→ gerçek projelerde yaşanmış System Design
  ve computational kararları kalıcı hale getirir.
```

Ana öğrenme döngüsü bu nedenle mümkün olduğunca şu yapıyı izlemelidir:

```text
REAL PROJECT
↓
REAL ENGINEERING PROBLEM
↓
SYSTEM DESIGN QUESTION
↓
CONSTRAINTS
↓
ALTERNATIVES
↓
TRADE-OFFS
↓
SELECTED DESIGN
↓
IMPLEMENTATION WITH AI
↓
OBSERVED BEHAVIOUR / FAILURE
↓
HUMAN SYNCHRONIZATION
↓
gerekirse ULA LEARNING PASS
↓
SYSTEM DESIGN EXPERIENCE
```

Bir System Design problemi ortaya çıktığında temel öğrenme soruları:

```text
Problem neydi?

Bu neden bir system-design problemiydi?

Hangi constraint problemi doğurdu?

Sistemin hangi component'i etkilendi?

Hangi alternatifler vardı?

Neden bu çözüm seçildi?

Ne kazandık?

Ne kaybettik?

Hangi failure mode ortaya çıkabilir?

Scale veya requirement değişirse
karar nasıl değişirdi?

Bu deneyim gelecekte hangi problemi
tanımama yardımcı olur?
```

DSA yalnız computational yapı gerçekten önemli olduğunda devreye girer.

ULA yalnız öğrenmeye değer bir knowledge gap olduğunda devreye girer.

Knowledge Map yalnız bilgiyi konumlandırmak ve öğrenmeyi kolaylaştırmak için kullanılır.

Hiçbiri ana hedef değildir.

Ana hedef:

> **System Design düşünme biçimini gerçek Data Science / ML projeleri içinde deneyimleyerek kazanmak ve zamanla yeni bir sistem problemiyle karşılaşıldığında hangi mimari soruların sorulması gerektiğini sezgisel olarak tanıyabilmektir.**

Kısa kural:

> **Project problemi üretir. System Design ana öğrenmeyi üretir. Diğer katmanlar System Design öğrenimini destekler.**




---

# 4. PROBLEM-FIRST SYSTEM DESIGN

System Design müfredatı baştan sona sırayla tamamlanacak bir ders listesi değildir.

Müfredat şu sorunun haritasıdır:

> **Bu problem ortaya çıktığında hangi sistem kavramlarını düşünmeliyim?**

Örneğin:

```text
API çok yavaş
→ cache düşün

Uzun işlem HTTP request'i blokluyor
→ background job / queue düşün

Veri düzenli güncellenmeli
→ scheduler / pipeline düşün

Sistem büyüyor
→ scaling / partitioning düşün

Aynı veri çok okunuyor
→ caching / read replica düşün

Hata olduğunda nedenini göremiyorum
→ logging / observability düşün

Tek node kritik hata noktası
→ replication / redundancy düşün
```

System Design böyle öğrenilir.

Önce:

> **problem**

gelir.

Sonra:

> **system concept**

ortaya çıkar.

---

# 5. SYSTEM DESIGN EXPERIENCE MAP

Hazırlanmış System Design müfredatı korunur.

Ancak görevi:

> "Bu konuları sırayla bitir."

değildir.

Görevi:

> **"Projeler boyunca bu problem ve kavramlarla karşılaş."**

demektir.

Her önemli System Design deneyiminde şu bilgiler tutulur:

```text
Concept:
Project:
Problem:
Constraint:
Why did we need it?
Alternatives:
Selected solution:
Why:
Trade-off:
Failure mode:
What happened in practice?
What did I learn?
Depth reached:
Reusable signal:
Can I use it again?
```

Örnek:

```text
Concept:
Caching

Project:
Music Momentum App

Problem:
Aynı pahalı sorgu tekrar tekrar çalışıyordu.

Alternatives:
1. Her request'te yeniden hesaplama
2. Local memory cache
3. Redis

Selected:
Redis

Why:
Birden fazla process arasında paylaşılabilir.

Trade-off:
Cache invalidation gerekir.

Failure:
Stale data riski oluştu.

Reusable signal:
Repeated expensive read görürsem cache düşün.
```

Zamanla bu kayıtlar kişisel:

# SYSTEM DESIGN EXPERIENCE MAP

haline gelir.

---

# 6. DSA'NIN ROLÜ

DSA da baştan sona klasik müfredat şeklinde çalışılmaz.

Amaç:

```text
Array
→ Linked List
→ Tree
→ Graph
→ DP
```

sırasını tamamlamak değildir.

Amaç:

> **Bir computational problem gördüğümde onun hangi pattern'e benzediğini fark etmek ve uygun veri yapısı veya algoritmayı seçebilmek.**

Bu yaklaşım:

# PROBLEM-PATTERN-BASED DSA

olarak kullanılır.

---

# 7. PROBLEM-PATTERN DSA DÖNGÜSÜ

Her anlamlı DSA learning event şu zincir üzerinden incelenir:

```text
REAL PROBLEM
↓
NAIVE SOLUTION
↓
BOTTLENECK
↓
COMPUTATIONAL PATTERN
↓
CANDIDATE STRUCTURES / ALGORITHMS
↓
CHOSEN STRUCTURE / ALGORITHM
↓
TIME COMPLEXITY
↓
SPACE COMPLEXITY
↓
TRADE-OFF
↓
REAL SYSTEM USE
```

Örnek:

```text
Problem:
1 milyon artist içinde artist_id ile sürekli arama.

Naive:
Listeyi sırayla tara.

Cost:
O(n)

Bottleneck:
Repeated lookup.

Pattern:
Fast lookup.

Candidate:
Hash Map.

Expected average lookup:
O(1)

Trade-off:
Daha fazla memory.

System use:
Entity lookup / cache / feature lookup.
```

Amaç:

> "Hash Map nedir?"

sorusunu ezberlemek değildir.

Amaç:

```text
FAST LOOKUP
→ HASH MAP
```

çağrışımını oluşturmaktır.

---

# 8. DSA PROBLEM PATTERN MAP

DSA haritasının ilk seviyesi algoritma isimlerinden değil, problem pattern'lerinden oluşur.

```text
PROBLEM PATTERNS
│
├── Fast Lookup
│      └── Hash Map / Set
│
├── FIFO Processing
│      └── Queue
│
├── Priority Processing
│      └── Heap / Priority Queue
│
├── Top-K
│      └── Heap
│
├── Recent-N Observations
│      └── Sliding Window / Deque
│
├── Relationships
│      └── Graph
│
├── Dependencies
│      └── DAG
│
├── Shortest Path
│      └── Graph Algorithms
│
├── Repeated Subproblems
│      └── Dynamic Programming
│
├── Local Optimization
│      └── Greedy
│
├── Sorted Lookup
│      └── Binary Search / Tree
│
├── Similarity Search
│      └── Nearest Neighbor / ANN
│
├── Streaming Events
│      └── Queue + Window + Online Algorithm
│
├── Data Distribution
│      └── Hashing / Partitioning
│
└── Ranking
       └── Sorting / Heap
```

Bu liste ders sırası değildir.

Bu liste:

> **problem tanıma sözlüğüdür.**

---

# 9. DSA EXPERIENCE MAP

System Design gibi DSA için de yaşanmış problem kayıtları tutulur.

Örnek:

```text
Pattern:
Top-K

Project:
Artist Discovery System

Problem:
Her gün en hızlı yükselen 100 artist bulunmalı.

Naive:
Bütün artistleri tamamen sırala.

Bottleneck:
Tam sıralamaya ihtiyaç yok.

Chosen structure:
Heap

Why:
Yalnızca en yüksek K öğe gerekiyor.

Complexity insight:
Full sort gereksiz.

Reusable signal:
"Bütün veriyi sıralamak istemiyorum.
Yalnız en yüksek K öğe gerekiyor."

Where else?
Ranking
Recommendations
Alerts
```

Amaç:

> "Heap nedir?"

notu oluşturmak değil,

> **"Ben Heap'e neden ihtiyaç duydum?"**

sorusunun cevabını kalıcı hale getirmektir.

---

# 10. SYSTEM DESIGN × DSA KESİŞİMİ

DSA teorisi gerçek sistem component'lerine bağlanır.

```text
Hash Map
→ cache / lookup

Queue
→ background jobs

Priority Queue
→ scheduler

Graph
→ workflow relationships

DAG
→ pipelines

Tree
→ database indexes

Hashing
→ partitioning / sharding

Sliding Window
→ streaming metrics

ANN
→ vector search
```

Hedef:

> "Bu veri yapısını biliyorum."

değildir.

Hedef:

> **"Bu sistem component'inin altında hangi computational logic'in çalıştığını anlayabiliyorum."**

seviyesidir.

---

# 11. DATA SCIENCE × SYSTEM DESIGN × DSA

Alanlar mümkün olduğunca aynı gerçek proje içinde birleşir.

Örneğin:

```text
User Events
↓
Queue
↓
Stream Processing
↓
Sliding Window Features
↓
Feature Store
↓
ML Model
↓
Ranking
↓
Top-K
↓
API
↓
Application
```

Burada:

```text
Queue
→ DSA + System Design

Sliding Window
→ DSA + Time Series

Feature Store
→ ML System Design

Model
→ Data Science

Top-K
→ DSA

API
→ System Design
```

aynı sistem içinde birlikte yaşar.

Bu nedenle alanlar ayrı dünyalar gibi düşünülmez.

---

# 12. PROJE SEÇİMİ

Projeler rastgele seçilmez.

Her proje mümkün olduğunca üç gelişim alanına hizmet eder.

## DATA SCIENCE

Örnek:

- data collection,
- data cleaning,
- SQL,
- EDA,
- statistical modelling,
- feature engineering,
- machine learning,
- time series,
- prediction,
- experimentation,
- model evaluation.

## ENGINEERING / SYSTEM DESIGN

Örnek:

- API,
- database,
- Docker,
- deployment,
- pipeline,
- background jobs,
- caching,
- monitoring,
- queue,
- authentication,
- observability,
- scaling,
- CI/CD,
- reliability.

## COMPUTATIONAL THINKING / DSA

Örnek:

- lookup,
- ranking,
- streaming,
- graph relationships,
- scheduling,
- similarity search,
- window processing,
- efficient storage,
- optimization.

Her proje her konuyu içermek zorunda değildir.

---

# 13. PROJE ZORLUK ARTIŞI

Her yeni proje bir öncekinin üzerine yaklaşık:

> **2–4 yeni büyük engineering veya computational concept**

eklemelidir.

Tek projeye bütün teknolojiler doldurulmaz.

Örnek ilerleme:

```text
PROJECT 1
Database
API
Docker
Deployment

PROJECT 2
ETL
Scheduler
Data Validation
Background Jobs

PROJECT 3
Model Serving
Caching
Monitoring
Experiment Tracking

PROJECT 4
Queue
Async Processing
Streaming
Reliability

PROJECT 5
CI/CD
Cloud
Scaling
Security
Observability
```

DSA pattern'leri de doğal ihtiyaçtan ortaya çıkar:

```text
Project 1
→ lookup

Project 2
→ graph dependencies

Project 3
→ top-k

Project 4
→ sliding window / queue

Project 5
→ partitioning / hashing
```

Hiçbir pattern yalnızca müfredatta olduğu için projeye zorla sokulmaz.

---

# 14. AI'IN ROLÜ

AI yalnızca kod üreticisi değildir.

Altı ana rolü vardır.

## ENGINEER

Kod ve altyapıyı oluşturur.

## ARCHITECT

Alternatif mimariler önerir.

## REVIEWER

Kod, mimari, güvenlik ve metodoloji sorunlarını arar.

## DEBUGGER

Hataları reproduce eder, root cause araştırır ve fix'i doğrular.

## TEACHER — ULA MODE

Öğrenilmesine karar verilen teknik bilgiyi ULA protokolü ile öğretir.

## COMPRESSOR / TRANSLATOR

Saatler süren AI çalışmasını insanın birkaç dakika içinde kavrayabileceği mental modele sıkıştırır.

Teacher ile Compressor aynı görev değildir.

```text
COMPRESSOR
→ Şu anda ne olduğunu anlamamı sağlar.

ULA TEACHER
→ Önemli konuyu kalıcı bilgiye dönüştürür.
```

---

# 15. ANA PROBLEM: AI PRODUCTION SPEED > HUMAN COMPREHENSION SPEED

AI birkaç saat içinde:

- araştırma,
- kod,
- test,
- debugging,
- refactoring,
- documentation,
- analysis

üretebilir.

İnsan aynı miktarda teknik işi aynı sürede anlayamaz.

Bu durum:

# COGNITIVE THROUGHPUT GAP

oluşturur.

Yani:

> **AI'ın üretebildiği teknik iş miktarı, insanın aynı sürede anlayabileceği teknik iş miktarından büyüktür.**

Bu nedenle amaç yalnız AI'ı hızlandırmak değildir.

İkinci amaç:

> **İnsanın AI'ın hızına zihinsel olarak yetişmesini sağlamaktır.**

---

# 16. HUMAN SYNCHRONIZATION LAYER

Önemli task veya milestone yalnız implementation tamamlandığı için learning açısından DONE sayılmaz.

Yeni süreç:

```text
IMPLEMENT
↓
TEST
↓
REVIEW
↓
HUMAN SYNCHRONIZATION
↓
KNOWLEDGE PRIORITY
↓
DONE veya LEARNING PASS
```

Human Synchronization'ın amacı:

> yapılan bütün işi öğretmek değildir.

Amaç:

> **projeyi güvenli şekilde yönetmeye devam etmek için bilinmesi gereken minimum yeterli mental modeli üretmektir.**

---

# 17. HUMAN SYNCHRONIZATION ÇIKTISI

Her önemli task sonunda AI gerektiğinde şu yüksek sinyalli çıktıyı üretir.

## 1. ONE-SENTENCE SUMMARY

```text
Problem
→ Action
→ Result
```

## 2. SIMPLE CAUSAL EXPLANATION

3–6 kısa cümle.

```text
Bir problem vardı.
↓
Neden önemliydi?
↓
Ne yaptık?
↓
Neden bunu yaptık?
↓
Artık ne değişti?
```

## 3. MENTAL MODEL

```text
INPUT
↓
PROCESS
↓
DECISION
↓
OUTPUT
```

veya:

```text
Problem
├── Option A
├── Option B
└── Option C
      ↓
   Selected
```

## 4. TECHNICAL TRANSLATION

Basit sezgi gerçek teknik terimle eşleştirilir.

```text
"Son döneme bakmak"
→ Recent observation window

"Normal davranış"
→ Historical baseline

"Devam ediyor mu?"
→ Persistence

"Geleceği yanlışlıkla kullanmak"
→ Temporal leakage
```

Amaç:

```text
INTUITION
↕
TECHNICAL TERM
```

bağlantısı kurmaktır.

## 5. IMPORTANT DECISIONS

```text
Decision:
Alternatives:
Why:
Trade-off:
```

Routine implementation detayı dahil edilmez.

## 6. WHAT CHANGED?

Dosya listesi yerine sistem davranışı açıklanır.

## 7. EVIDENCE

Sonucun nasıl doğrulandığı belirtilir:

- tests,
- experiments,
- diagnostics,
- comparisons,
- manual checks.

Ve epistemik durum açık tutulur:

```text
VERIFIED
INFERRED
ASSUMED
UNRESOLVED
```

---

# 18. KNOWLEDGE PRIORITY

AI'ın kullandığı her bilgi hemen öğrenilmez.

Her önemli task sonunda bilgi üç gruba ayrılır.

```text
MUST UNDERSTAND
USEFUL TO KNOW
IMPLEMENTATION DETAIL
```

## MUST UNDERSTAND

Projeyi doğru yönetmek veya benzer kararları gelecekte verebilmek için gereken bilgidir.

Gerekirse:

```text
→ ULA LEARNING PASS
```

alır.

## USEFUL TO KNOW

Faydalıdır ancak şu anda derinleşmek gerekmez.

```text
→ kısa açıklama
veya
→ Knowledge Debt
```

olarak tutulur.

## IMPLEMENTATION DETAIL

AI'ın çözebileceği ve şu anda öğrenilmesi gerekmeyen ayrıntıdır.

Bunun için ULA çalıştırılmaz.

Ana kural:

> **Her teknik ayrıntı öğrenme borcu değildir.**

---

# 19. KNOWLEDGE DEBT

AI'ın kullandığı fakat henüz tam anlaşılmayan önemli kavramlar ayrı backlog'da tutulur.

Format:

```text
Concept:
Why did it appear?
One-sentence explanation:
Why does it matter?
Priority:
NOW / LATER / OPTIONAL
```

Örnek:

```text
Concept:
Temporal leakage

Why:
Modelin geleceği görmesini engellemek gerekiyor.

Priority:
NOW
```

Amaç şu durumu engellemektir:

> "AI'ın hangi önemli bilgiyi kullandığını bile bilmiyorum."

---

# 20. ULA'NIN ROLÜ

ULA yeni bir ders alanı değildir.

ULA:

# LEARNING CONTENT PROTOCOL

olarak çalışır.

System Design yine problem-first'tür.

DSA yine pattern-first'tür.

Projeler yine öğrenme laboratuvarıdır.

ULA şu soruyu kontrol eder:

> **AI, gerçekten öğrenmeye karar verdiğim bilgiyi bana hangi sırayla ve hangi derinlikte öğretmelidir?**

Varsayılan ULA sırası:

```text
WHOLE / MAP
↓
L1 — SIMPLE MEANING
↓
L2 — MECHANISM
↓
L3 — THEORY
↓
L4 — FORMALISM / MATH
↓
CONFUSIONS
↓
RETRIEVAL
↓
REFERENCE
```

Ana kural:

> **Mekanizma anlaşılmadan teoriye, teori anlaşılmadan formalizme geçilmez.**

---

# 21. ULA HORIZONTAL KNOWLEDGE MAP

ULA'nın varsayılan görsel biçimi:

# NOTEBOOKLM-STYLE HORIZONTAL KNOWLEDGE MAP

olacaktır.

NotebookLM Mind Map görsel referanstır.

Ancak ULA haritası semantic olarak daha kontrollüdür.

Amaç, öğrenme içeriğini uzun lineer belge gibi göstermek yerine:

> **birbirine bağlı, açılabilir ve zoom yapılabilir bir bilgi sistemi**

olarak göstermektir.

---

## 21.1 TEMEL GEOMETRİ

ULA iki eksen kullanır.

```text
X EKSENİ
=
konunun doğal ilişkisi / akışı

Y EKSENİ
=
seçilen node'un öğrenme derinliği
```

Kısa kural:

> **Sağa gitmek = sistemde ilerlemek.**

> **Aşağı gitmek = aynı node'u daha derin öğrenmek.**

---

## 21.2 HORIZONTAL AXIS

Yatay eksen şu tür ilişkileri taşıyabilir:

- time flow,
- causal flow,
- data flow,
- reasoning flow,
- dependency,
- process sequence,
- comparison,
- branching decision,
- parent-child relationship,
- evidence chain.

Makale örneği:

```text
RESEARCH
→ DATA
→ MODEL
→ FIT
→ READ
→ DESIGN & SELECTION
║ INFORMATION WALL
→ HOLDOUT
→ EVIDENCE
→ CLAIMS
```

System Design örneği:

```text
CLIENT
→ API
→ SERVICE
├── CACHE
├── DATABASE
└── QUEUE
      → WORKER
```

DSA örneği:

```text
REAL PROBLEM
→ NAIVE SOLUTION
→ BOTTLENECK
→ PATTERN
→ STRUCTURE
→ COMPLEXITY
→ TRADE-OFF
```

---

## 21.3 VERTICAL AXIS

Dikey eksen yalnız seçilmiş node'un öğrenme derinliğini gösterir.

```text
SELECTED NODE
      │
      ▼
L1 — SIMPLE
      │
      ▼
L2 — MECHANISM
      │
      ▼
L3 — THEORY
      │
      ▼
L4 — FORMALISM
```

Gerekirse:

```text
CONFUSIONS
↓
RETRIEVAL
↓
REFERENCE
```

eklenir.

Depth yatay eksene konmaz.

---

# 22. NOTEBOOKLM-BENZERİ BRANCHING VE RECURSIVE ZOOM

Karmaşık konu tek seferde açılmaz.

Örnek:

```text
DATABASE
│
├── Storage
├── Index
├── Transactions
├── Replication
└── Partitioning
```

Replication seçilirse:

```text
REPLICATION
│
├── Leader / Follower
├── Replication Lag
├── Failover
└── Consistency
```

Sonra `Replication Lag` seçilirse o node'un öğrenme depth'i açılır.

Ana kural:

> **Alt dala inerken üst haritadaki konum kaybolmaz.**

Kullanıcı her zaman şunu bilmelidir:

```text
WORLD
→ REGION
→ CURRENT NODE
→ CURRENT DEPTH
```

Örnek:

```text
SYSTEM DESIGN
→ DATABASE
→ REPLICATION
→ MECHANISM
```

---

# 23. PROGRESSIVE EXPANSION

İlk ekran bütün bilgiyi göstermez.

İlk ekran:

```text
HIGH-LEVEL MAP
```

gösterir.

Sonra:

```text
select branch
↓
open children
↓
select node
↓
open depth
```

şeklinde ilerlenir.

Ana kural:

> **Harita genişler. İçerik dökülmez.**

İlk görünümde uzun teori, formül, kaynak veya implementation detail gösterilmez.

---

# 24. NODE TASARIMI

İlk görünümde bir node kısa ve yüksek sinyalli olmalıdır.

Örnek:

```text
┌─────────────────────────┐
│ CACHE                   │
│                         │
│ Tekrarlanan pahalı      │
│ erişimi azaltır.        │
└─────────────────────────┘
```

Node ilk görünümde mümkün olduğunca yalnız:

- canonical name,
- short meaning,
- sistemdeki rol

gösterir.

Detaylar node açıldıkça gelir.

---

# 25. EDGE SEMANTICS

Her edge gerçek bir anlam taşımalıdır.

Örnek relation type'ları:

```text
NEXT
REQUIRES
PRODUCES
CAUSES
USES
DEPENDS ON
ALTERNATIVE TO
COMPARED WITH
PART OF
EVIDENCE FOR
FAILS WHEN
IMPLEMENTED BY
```

Bir bağlantının neden var olduğu açıklanamıyorsa bağlantı çizilmez.

> **Dekoratif connector kullanılmaz.**

---

# 26. SEMANTIC GRAPH LAYER

Görsel harita serbest metinden doğrudan çizilmez.

Önce knowledge graph oluşturulur.

Her node mümkün olduğunca:

```text
NODE ID
NAME
PARENT
CHILDREN
HOME
SHORT MEANING
RELATION TO PARENT
PREVIOUS
NEXT
AVAILABLE DEPTH
CONFUSIONS
REFERENCE
PROJECT APPEARANCES
```

alanlarını taşır.

Her edge:

```text
SOURCE
TARGET
RELATION TYPE
MEANING
```

taşır.

Üretim sırası:

```text
KNOWLEDGE ARCHITECTURE
↓
SEMANTIC GRAPH
↓
HORIZONTAL KNOWLEDGE MAP
↓
INTERACTIVE LEARNING VIEW
```

Böylece:

```text
KNOWLEDGE
≠
PRESENTATION
```

ayrımı korunur.

---

# 27. ULA L1 — SIMPLE MEANING

L1 şu soruya cevap verir:

> **Bu şey temelde ne yapıyor?**

Format:

```text
TÜRKÇE KISA ANLAM

NE İŞE YARAR?

SİSTEMDEKİ YERİ
```

Yaklaşık 2–6 kısa cümle kullanılır.

Teknik jargon minimum tutulur.

Öğrenci L1 sonrasında kavramı gündelik ama doğru biçimde anlatabilmelidir.

---

# 28. ULA L2 — MECHANISM

L2 şu soruya cevap verir:

> **Bu şey gerçekten nasıl çalışıyor?**

Varsayılan yapı:

```text
INPUT
↓
OPERATION
↓
DECISION
↓
OUTPUT
↓
NEXT STEP
```

Örnek Cache:

```text
REQUEST
↓
CACHE LOOKUP
↓
HIT?
├── YES → RETURN
└── NO
      ↓
   DATABASE
      ↓
   CACHE WRITE
      ↓
   RETURN
```

DSA örneği:

```text
UNSORTED ITEMS
↓
Need only Top-K?
↓
Maintain K candidates
↓
Heap
↓
Return Top-K
```

Amaç:

> **öğrencinin mekanizmayı zihninde simüle edebilmesidir.**

---

# 29. ULA L3 — THEORY

L3 şu soruya cevap verir:

> **Mekanizma neden böyle tasarlanmıştır?**

Burada:

- principles,
- assumptions,
- constraints,
- invariants,
- alternatives,
- trade-offs,
- failure modes,
- neden seçildiği,
- ne zaman seçilmemesi gerektiği

anlatılır.

System Design için L3 özellikle:

```text
CONSTRAINT
TRADE-OFF
ALTERNATIVE
FAILURE MODE
```

üzerine kurulur.

DSA için:

```text
PROBLEM PATTERN
WHY NAIVE FAILS
WHY THIS STRUCTURE FITS
COMPLEXITY TRADE-OFF
```

üzerine kurulur.

L3 jargon listesi değildir.

L2 mekanizmasının **nedenini** açıklar.

---

# 30. ULA L4 — FORMALISM / MATH

L4 yalnız gerektiğinde açılır.

Sorusu:

> **Anladığım mekanizma teknik olarak nasıl ifade edilir?**

DSA için:

- time complexity,
- space complexity,
- recurrence,
- invariants,
- formal properties.

Data Science için:

- equations,
- objectives,
- probability,
- statistical formulation.

System Design için:

- formal consistency model,
- capacity reasoning,
- queueing approximation,
- availability calculations

gibi formalizm ancak gerçekten yararlıysa kullanılır.

Gerekli değilse:

```text
L4 — NO FORMALISM REQUIRED
```

denir.

Formül varsa:

```text
PURPOSE
SYMBOLS
MECHANISM MAPPING
INTERPRETATION
```

sırasıyla açıklanır.

Ana kural:

> **Formül, daha önce anlaşılmış mekanizmanın resmi gösterimidir.**

Formül yeni fikri ilk kez tanıtmamalıdır.

---

# 31. CONFUSION BOUNDARIES

Yüksek riskli karışıklıklar açıkça ayrılır.

Format:

```text
A ≠ B
```

Örnek:

```text
CACHE ≠ DATABASE

Cache:
hız için geçici veya türetilmiş state tutabilir.

Database:
ana persistent state'i tutar.
```

DSA:

```text
HEAP ≠ SORTED ARRAY

Heap:
extreme elemanı hızlı erişilebilir tutar.

Sorted array:
tüm ordering'i korur.
```

Bu bölüm yalnız gerçekten karıştırılabilecek kavramlarda kullanılır.

---

# 32. ONE CONCEPT — ONE HOME

Aynı kavram her projede tekrar tekrar baştan öğretilmez.

Her önemli kavramın bir:

# CONCEPT HOME

kaydı bulunur.

Örnek:

```text
Concept:
Caching

Home:
Personal Technical Library / Caching

Project Appearances:
- Music Momentum App
- Recommendation API
- Feature Serving System
```

Yeni projede Cache tekrar ortaya çıkarsa genel teori yeniden yazılmaz.

Yalnız:

```text
Bu projede neden ortaya çıktı?
Nasıl kullandık?
Ne farklıydı?
Hangi yeni failure oluştu?
Ne öğrendik?
```

eklenir.

Böylece:

```text
GENERAL KNOWLEDGE
≠
PROJECT EXPERIENCE
```

ayrımı korunur.

---

# 33. CONCEPT HOME NOTE VE PROJECT EXPERIENCE NOTE

İki farklı doküman türü vardır.

## A. CONCEPT HOME NOTE

Genel öğrenme bilgisidir.

```text
HORIZONTAL MAP
↓
L1 — SIMPLE
↓
L2 — MECHANISM
↓
L3 — THEORY
↓
L4 — FORMALISM if needed
↓
CONFUSIONS
↓
RETRIEVAL
↓
REFERENCE
```

## B. PROJECT EXPERIENCE NOTE

Yaşanmış bağlamdır.

```text
Concept:
Project:
Problem:
Constraint:
Why did it appear?
Alternatives:
Selected:
Why:
Trade-off:
Failure:
Observed result:
Reusable signal:
Concept Home:
```

Kısa ayrım:

> **ULA kavramı öğretir.**

> **Experience Map kavramın gerçek hayatta neden kullanıldığını hatırlatır.**

---

# 34. REFERENCE LAYER

Ana öğrenme yolu ayrıntıyla boğulmaz.

Şunlar gerektiğinde Reference'a taşınır:

- exact API options,
- library-specific syntax,
- uzun kod blokları,
- bütün benchmark tabloları,
- edge-case katalogları,
- kaynak linkleri,
- ayrıntılı matematik türetmeleri,
- implementation-specific configuration.

Ana yol:

> **ANLAMAK**

içindir.

Reference:

> **BAKMAK / GERİ DÖNMEK**

içindir.

---

# 35. ZOOM VE DEPTH CONTROL

Her konu aynı derinlikte öğrenilmez.

## ZOOM 1 — QUICK ORIENTATION

Amaç:

```text
Bu şey nedir?
Sistemin neresindedir?
Neden karşıma çıktı?
```

Çıktı:

```text
MAP
+
L1 SIMPLE
```

Yaklaşık 30 saniye–2 dakika.

---

## ZOOM 2 — WORKING MODEL

Amaç:

```text
Neden buna ihtiyaç duyduk?
Nasıl çalışıyor?
Alternatifler ne?
Trade-off ne?
```

Çıktı:

```text
MAP
↓
L1 SIMPLE
↓
L2 MECHANISM
↓
gerekirse L3 THEORY
↓
CONFUSION CHECK
```

System Design ve çoğu DSA konusu için varsayılan seviye budur.

---

## ZOOM 3 — DEEP LEARNING

Amaç:

```text
Teknik olarak nasıl çalışıyor?
Neden böyle tasarlanmış?
Formal yapısı nedir?
Failure davranışı nedir?
```

Çıktı:

```text
MAP
↓
L1
↓
L2
↓
L3
↓
L4
↓
CONFUSIONS
↓
RETRIEVAL
↓
REFERENCE
```

Zoom 3 yalnız:

- kritik teori,
- kariyer açısından merkezi konu,
- sık kullanılan yapı,
- önemli mimari karar,
- önemli DSA pattern,
- ciddi failure veya performance davranışı,
- gerçekten anlaşılmayan kritik mekanizma

için açılır.

Ana kural:

> **Derinlik değişebilir. Öğretim sırası değişmez.**

---

# 36. LEARNING EVENT

AI yaptığı her şeyi öğretmez.

Yalnız anlamlı öğrenme noktaları:

```text
LEARNING_EVENT
```

olarak işaretlenir.

Örnek:

- yeni architecture decision,
- yeni DSA pattern,
- database seçimi,
- caching ihtiyacı,
- queue kullanımı,
- critical bug,
- performance bottleneck,
- security decision,
- scaling problemi,
- ML serving yaklaşımı,
- önemli statistical assumption.

Amaç:

```text
100 küçük açıklama
```

değil,

```text
10–20 yüksek değerli öğrenme olayı
```

üretmektir.

Learning Event iki şekilde sonuçlanabilir:

```text
LEARNING EVENT
│
├── EXPERIENCE ONLY
│   → Experience Map
│
└── KNOWLEDGE GAP
    ↓
    ULA LEARNING PASS
    ↓
    Experience Map
```

ULA özellikle şu durumlarda tetiklenir:

- kavram ilk kez karşılaşılıyorsa,
- karar kritikse,
- tekrar kullanılacaksa,
- yanlış anlaşılması riskliyse,
- system behaviour'ı etkiliyorsa,
- performance/failure açısından önemliyse,
- kullanıcı kavramı açıklayamıyorsa.

---

# 37. JIRA KARTI YAŞAM DÖNGÜSÜ

Önemli Jira kartı için ideal akış:

```text
TO DO
↓
RESEARCH / PLAN
↓
IMPLEMENTATION
↓
TEST
↓
AUDIT / REVIEW
↓
HUMAN SYNCHRONIZATION
↓
KNOWLEDGE PRIORITY
↓
LEARNING EVENT EXTRACTION
↓
gerekirse ULA LEARNING PASS
↓
EXPERIENCE MAP UPDATE
↓
DONE
```

Kart teknik olarak bitmiş olsa bile:

> insan temel mental modeli kuramıyorsa,

learning kısmı tamamlanmamış sayılır.

Ancak her Jira kartı derse dönüştürülmez.

---

# 38. ARCHITECTURE DECISION RECORD

Önemli mimari kararlar küçük ADR belgelerine dönüştürülebilir.

```text
Problem
Constraints
Alternatives
Selected Solution
Why
Trade-offs
Failure Modes
Future Trigger
```

Amaç fazla dokümantasyon değildir.

Amaç:

> **karar verme mantığını kalıcı hale getirmektir.**

---

# 39. DSA DECISION RECORD

Önemli computational seçimlerde:

```text
Problem Pattern:
Naive Solution:
Bottleneck:
Candidate Structures:
Chosen Structure:
Complexity:
Trade-off:
Where It Appeared:
Reusable Signal:
Concept Home:
```

kullanılabilir.

En önemli alan:

```text
Reusable Signal
```

örneğin:

> "Bütün veriyi sıralamak istemiyorum. Yalnız en yüksek K öğe gerekiyor."

Bu sinyal gelecekte:

```text
→ Top-K
→ Heap
```

çağrışımı oluşturmalıdır.

---

# 40. RETRIEVAL

Bir konu okunmuş olmakla öğrenilmiş sayılmaz.

ULA Learning Pass sonunda mümkün olduğunca:

```text
1. Haritayı bakmadan yeniden çiz.

2. Mekanizmayı kendi cümlelerinle anlat.

3. En önemli trade-off'u söyle.

4. En önemli A ≠ B ayrımını açıkla.

5. Bu bilgiyi başka nerede kullanabileceğini söyle.
```

DSA için:

```text
Problem pattern neydi?

Naive çözüm neden yetersizdi?

Chosen structure neden uygundu?

Time / space trade-off neydi?
```

System Design için:

```text
Hangi constraint bu tasarımı doğurdu?

Alternatif neydi?

Bu tasarım ilk nerede kırılır?

Hangi constraint değişirse
başka çözüm seçerdim?
```

---

# 41. AI'A BAĞIMLILIK KONTROLÜ

AI yoğun biçimde kullanılacaktır.

Ancak önemli kararların sonunda kullanıcı şunları cevaplayabilmelidir:

```text
Ne yaptık?

Neden yaptık?

Alternatif neydi?

Ne kazandık?

Ne kaybettik?
```

DSA kararı varsa:

```text
Bu hangi pattern'di?

Naive çözüm neden yetmedi?
```

ULA Learning Pass tamamlandıysa:

```text
Haritayı bakmadan çizebilir miyim?

Mekanizmayı simüle edebilir miyim?

Teoriyi mekanizmaya bağlayabilir miyim?

Varsa formülü mekanizmaya bağlayabilir miyim?

En önemli confusion boundary'yi açıklayabilir miyim?

Bu bilgiyi başka probleme transfer edebilir miyim?
```

Kodun her satırını ezberlemek gerekmez.

Ama:

- system behaviour,
- data flow,
- important decisions,
- failure points,
- computational patterns

anlaşılmalıdır.

---

# 42. HUMAN REVIEW CHECK

Milestone sonunda şu sorular sorulur:

```text
Sistemin büyük resmini çizebilir miyim?

Data nereden geliyor?

Nereye gidiyor?

Model nerede çalışıyor?

State nerede tutuluyor?

En önemli mimari kararlar neydi?

Alternatifleri neydi?

Sistem büyürse ilk neresi kırılır?

Hangi DSA pattern'lerini kullandık?

Neden?

AI'ın hangi kararlarını gerçekten anlıyorum?

Hangilerini yalnız kabul ettim?

Knowledge Debt'im ne?

Projeyi başka birine basitçe anlatabilir miyim?
```

---

# 43. META-WORK SINIRI

Çalışma sistemi projenin kendisinden büyük hale gelmemelidir.

Yeni:

- template,
- agent,
- markdown,
- workflow,
- automation,
- dashboard,
- knowledge graph

yalnız gerçek problemi çözüyorsa eklenir.

Ana kural:

> **Çalışma sistemini geliştirmek, çalışmanın kendisinin önüne geçemez.**

NotebookLM-benzeri Knowledge Map de amaç değildir.

Amaç:

> **öğrenmeyi kolaylaştırmaktır.**

---

# 44. PROJE BAŞARI KRİTERİ

System Design başarısı:

> "System Design müfredatını bitirdim."

değildir.

Başarı:

> **"Bir problem gördüğümde hangi sistem parçalarını düşünmem gerektiğini biliyorum."**

seviyesine gelmektir.

DSA başarısı:

> "50 algoritma biliyorum."

değildir.

Başarı:

> **"Bir computational problem gördüğümde hangi pattern'e benzediğini fark ediyorum."**

seviyesidir.

AI kullanımı başarısı:

> "AI çok kod yazdı."

değildir.

Başarı:

> **"AI çok hızlı üretmesine rağmen sistemin önemli kararlarını ve davranışını anlayabiliyorum."**

seviyesidir.

ULA başarısı:

> "Çok fazla öğrenme notu ürettim."

değildir.

Başarı:

> **"Bir konunun bütününü görebiliyor, doğru node'a zoom yapabiliyor, mekanizmasını anlayabiliyor ve bilgiyi başka probleme taşıyabiliyorum."**

seviyesidir.

---

# 45. UZUN VADELİ ÇIKTILAR

Bu sistem birkaç proje boyunca kullanıldığında şu varlıklar oluşur.

## 1. PORTFOLIO

Gerçek çalışan data / ML ürünleri.

## 2. SYSTEM DESIGN EXPERIENCE MAP

Gerçek problemlerde karşılaşılan engineering kararları.

## 3. DSA PATTERN MAP

Gerçek computational problemlerde kullanılan pattern'ler.

## 4. PERSONAL TECHNICAL LIBRARY

ULA formatında oluşturulmuş Concept Home'lar.

## 5. KNOWLEDGE DEBT BACKLOG

Henüz derin öğrenilmemiş önemli kavramlar.

## 6. SEMANTIC KNOWLEDGE GRAPH

Kavramların birbirleriyle gerçek ilişkilerini tutan graph.

## 7. INTERACTIVE ULA KNOWLEDGE ATLAS

NotebookLM-benzeri yatay ve recursive öğrenme haritası.

---

# 46. FINAL INTERACTIVE ULA KNOWLEDGE ATLAS

Uzun vadeli nihai görsel hedef tek tek lineer learning note'lar değildir.

Hedef:

# INTERACTIVE ULA KNOWLEDGE ATLAS

İlk ekran NotebookLM Mind Map benzeri yatay bir overview gösterir.

Makale örneği:

```text
RESEARCH
→ DATA
→ MODEL
→ FIT
→ READ
→ SELECTION
║ WALL
→ HOLDOUT
→ DIAGNOSTICS
→ CLAIMS
```

System Design örneği:

```text
CLIENT
→ API
→ SERVICE
├── CACHE
├── DATABASE
└── QUEUE
      → WORKER
```

DSA:

```text
PROBLEM PATTERNS
├── Fast Lookup → Hash Map
├── Top-K → Heap
├── FIFO → Queue
├── Recent-N → Sliding Window
├── Dependencies → DAG
└── Repeated Subproblems → DP
```

Node seçildiğinde aşağı doğru:

```text
Simple
↓
Mechanism
↓
Theory
↓
Formalism
```

açılır.

Ana sistem haritası görünür kalır.

---

# 47. DEFAULT VISUAL EXPERIENCE

Artifact açıldığında:

```text
1. Whole Map görünür.

2. Kullanıcı branch seçer.

3. Branch yatay olarak açılır.

4. Kullanıcı node seçer.

5. Short Meaning görünür.

6. Kullanıcı istediği depth'i açar.

7. Simple → Mechanism → Theory → Formalism
   dikey olarak genişler.

8. Confusions ve Retrieval açılabilir.

9. Reference yalnız gerekirse açılır.

10. Üst harita kaybolmaz.
```

Amaç:

> **Kullanıcının hiçbir zaman "Şu anda sistemin neresindeyim?" diye düşünmek zorunda kalmamasıdır.**

---

# 48. ANA ÜRETİM HATTI

Bütün sistem tek akışta:

```text
BUILD
↓
ENCOUNTER
↓
IDENTIFY THE PROBLEM
↓
UNDERSTAND
↓
DESIGN
↓
RECOGNIZE THE PATTERN
↓
COMPARE ALTERNATIVES
↓
SELECT
↓
IMPLEMENT WITH AI
↓
TEST
↓
REVIEW
↓
HUMAN SYNCHRONIZATION
↓
KNOWLEDGE PRIORITY
↓
LEARNING EVENT?
│
├── NO
│   ↓
│   CONTINUE
│
└── YES
    ↓
    SELECT DEPTH
    ↓
    ULA LEARNING PASS
    │
    ├── BUILD SEMANTIC GRAPH
    │
    ├── SHOW HORIZONTAL MAP
    │
    ├── SELECT NODE
    │
    └── OPEN VERTICAL DEPTH
    │       │
    │       ├── SIMPLE
    │       ├── MECHANISM
    │       ├── THEORY
    │       ├── FORMALISM if needed
    │       ├── CONFUSIONS
    │       └── RETRIEVAL
    │
    ↓
DOCUMENT EXPERIENCE
↓
UPDATE CONCEPT HOME
↓
UPDATE EXPERIENCE / PATTERN MAP
↓
REUSE
↓
REPEAT
```

---

# 49. HER KATMANIN TEK CÜMLELİK ROLÜ

## PROJECT

> Gerçek problemi üretir.

## DATA SCIENCE

> Ne ölçüleceğini ve hangi problemi çözmeye çalıştığımızı belirler.

## SYSTEM DESIGN

> Çözümün sistem içinde nasıl yaşayacağını belirler.

## DSA

> Problemin computational yapısını çözer.

## AI

> Üretim kapasitesini büyütür.

## HUMAN SYNCHRONIZATION

> AI'ın üretim hızı ile insan anlayış hızı arasındaki farkı kapatır.

## KNOWLEDGE PRIORITY

> Neyin gerçekten öğrenilmeye değer olduğunu seçer.

## ULA

> Seçilmiş bilgiyi doğru zihinsel sırayla öğretir.

## HORIZONTAL KNOWLEDGE MAP

> Bilginin sistemde nereye bağlandığını gösterir.

## EXPERIENCE MAP

> Bilginin gerçek projede nerede ve neden kullanıldığını saklar.

## PERSONAL TECHNICAL LIBRARY

> Genel bilgiyi Concept Home'larda kalıcı hale getirir.

---

# 50. AI İÇİN VARSAYILAN ULA CONTENT PROMPT

Bir System Design, DSA, Data Science veya Software Engineering konusu gerçekten öğrenilecekse AI şu protokolü uygular:

> Bu konuyu ULA Learning formatında öğret.
>
> Önce whole system veya relevant local map'i göster.
>
> İçeriği mümkün olduğunda NotebookLM-style horizontal knowledge map mantığıyla yapılandır.
>
> Önce semantic graph kur.
>
> Yatay eksende doğal system, problem, causal, dependency veya reasoning flow'u göster.
>
> Parent-child ilişkilerini branch'ler halinde göster.
>
> Bir alt dala inerken parent context'i kaybetme.
>
> Sonra seçilmiş node için dikey olarak:
>
> L1 — Simple Meaning  
> L2 — Mechanism  
> L3 — Theory  
> L4 — Math / Formalism, yalnız gerekiyorsa
>
> sırasını kullan.
>
> Formülü mekanizmadan önce verme.
>
> Aynı bilgiyi farklı teknik kelimelerle tekrar etme.
>
> Teknik terimi ilk kez sezgisel anlamıyla eşleştir.
>
> High-risk Confusion Boundaries ekle.
>
> Ana öğrenme yüzeyini Reference ayrıntılarıyla doldurma.
>
> System Design'da problem, constraint, alternatives, trade-off ve failure mode'ları öne çıkar.
>
> DSA'da:
>
> real problem → naive solution → bottleneck → pattern → chosen structure → complexity → trade-off → real use
>
> zincirini koru.
>
> Aynı kavramın genel teorisini yalnız Concept Home'da öğret.
>
> Başka projelerde yalnız gerekli reminder ve yeni project experience'ı ekle.
>
> Learning Pass sonunda retrieval soruları üret.
>
> Amaç textbook completeness değildir.
>
> Amaç:
>
> **kullanılabilir, yeniden çizilebilir, transfer edilebilir ve sistem içindeki yeri görülebilir bir mental model üretmektir.**

---

# 51. SON HEDEF

Uzun vadede hedef:

> Statistics ve Data Science temeli güçlü,

> gerçek bir veri problemini teknik ürüne çevirebilen,

> sistemin component'lerini ve data flow'unu anlayan,

> System Design problemlerini tanıyabilen,

> computational problem pattern'lerini görebilen,

> temel DSA seçimlerinin nedenlerini açıklayabilen,

> AI coding agent'larını yüksek verimle yöneten,

> AI'ın ürettiği işi eleştirebilen,

> test ve review yapabilen,

> production engineering'e yabancı olmayan,

> deployment, monitoring, reliability ve scaling kavramlarını anlayan,

> mimari kararların trade-off'larını tartışabilen,

> öğrendiği bilgiyi birbirinden kopuk notlar değil bağlantılı knowledge graph olarak görebilen,

> ihtiyaç olduğunda bir node'a zoom yapıp basit anlamdan mekanizma, teori ve formalizme inebilen,

> AI'ın hızından yararlanırken teknik anlayışını kaybetmeyen

bir Data Scientist / ML-AI practitioner olmaktır.

---

# 52. EN TEMEL PRENSİP

Bütün sistem tek cümlede:

> **AI hızlı üretsin. İnsan doğru problemi seçsin. Human Synchronization yapılan işi insan hızına sıkıştırsın. ULA önemli bilgiyi doğru sırada öğretsin. Horizontal Knowledge Map bilginin bütündeki yerini göstersin. Experience Map ise bu bilginin gerçek hayatta nerede ve neden kullanıldığını hatırlatsın.**

Daha kısa hali:

```text
PROJECT
→ PROBLEMİ ÜRETİR

AI
→ ÜRETİMİ HIZLANDIRIR

HUMAN SYNCHRONIZATION
→ ANLAYIŞI ÜRETİME YETİŞTİRİR

ULA
→ KRİTİK BİLGİYİ ÖĞRETİR

HORIZONTAL KNOWLEDGE MAP
→ BİLGİLERİ BAĞLAR

EXPERIENCE MAP
→ YAŞANMIŞ DENEYİMİ SAKLAR

RETRIEVAL
→ BİLGİNİN GERÇEKTEN ÖĞRENİLDİĞİNİ TEST EDER

REUSE
→ BİLGİYİ YENİ PROBLEME TAŞIR
```

Nihai öğrenme ilkesi:

> **Bütünü gör → doğru probleme zoom yap → mekanizmayı anla → teoriyi bağla → gerekirse formalizme in → kendin yeniden üret → gerçek projede tekrar kullan.**