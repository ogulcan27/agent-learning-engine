"""Realistic Human Sync fixture: a music-listening research project with sequential work units.

UNITS[n] is the record content the sync judge writes for Step n (record section -> body).
Steps 1-3 are the three quality-test types: research definition, data audit, methodological freeze.
Step 4 is an old-style record written before the human-first rule (IDs, unexplained symbols).
Step 7 has no judge content (sparse default record). CONTEXT is a full PROJECT_SYNC_CONTEXT body.
"""

TYPES = {1: "research definition", 2: "data audit", 3: "methodological freeze"}

UNITS = {
    1: {
        "Purpose": "Projede artist activity'nin ölçüm standardı belirlendi: ana ölçü haftalık benzersiz dinleyici sayısı (N), "
                   "toplam dinleme sayısı (C) ise yardımcı sinyal oldu.",
        "Why It Changed": "İki ölçü farklı sanatçıları öne çıkarıyordu. C, az sayıda tekrar dinleyen kitlesi olan sanatçıyı şişiriyordu. "
                          "N geniş kitleyi daha dürüst gösterir. Tek bir ana ölçü olmadan sonraki kararlar tutarsız kalırdı.",
        "How It Works": "```text\nDİNLEME OLAYI → HAFTALIK TOPLAMA → N (ana) + C (yardımcı) → ACTIVITY\n```",
        "Technical Translation": "```text\n\"haftalık benzersiz dinleyici sayısı\" ↔ N\n\"haftalık toplam dinleme sayısı\" ↔ C\n"
                                 "\"veri yok, sıfır değil\" ↔ empty ≠ zero\n```",
        "Key Decisions": "```text\nDecision: Activity ana ölçüsü\nAlternatives: C (VERIFIED doc:research/activity.md); N ve C ağırlıklı toplam (GENERAL THEORY)\n"
                         "Selected: N\nWhy: Tekrar dinleme kitleyi şişirmez.\nTrade-off: Sadık küçük kitleler düşük görünür.\n```",
        "What Changed": "```text\nÖNCE  → activity iki ölçü arasında belirsizdi\nSONRA → N ana ölçü, C yardımcı sinyal\n```",
        "Dependencies": "Yok.",
        "Downstream Impact": "Bundan sonraki population seçimi (TF-03), momentum ve target kararları (TF-05) aynı activity tanımını kullanacak.",
        "Open / Uncertain Points": "- Haftalık pencere yeterince kısa mı?",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| N ana ölçü seçildi | VERIFIED (doc:research/activity.md#decision) |\n"
                                 "| C kitleyi şişiriyor | INFERRED |",
    },
    2: {
        "Purpose": "Dinleme verisi denetlendi: 2019 öncesi haftaların %18'inde dinleyici sayısı eksik; bu haftalar sıfır değil, boş kabul edildi.",
        "Why It Changed": "Eksik hafta sıfır sayılırsa sanatçı o hafta dinlenmemiş gibi görünür. Bu sahte düşüşler üretir. Önce verinin nerede eksik olduğu bilinmeliydi.",
        "How It Works": "- Her hafta için iki sayı kontrol edildi.\n- Eksik hafta boş işaretlendi, sıfır yazılmadı.\n- Boş hafta sonraki hesaplara girmez.",
        "Technical Translation": "```text\n\"kayıt yok, dinleme sıfır değil\" ↔ missing-not-zero\n\"verinin dolu olduğu hafta oranı\" ↔ coverage ratio\n```",
        "What Changed": "```text\nÖNCE  → eksik hafta 0 dinleme sayılıyordu\nSONRA → eksik hafta boş (NA) ve hesap dışı\n```",
        "Dependencies": "Step 1: activity ölçüsü (N ve C) bu denetimin konusu.",
        "Downstream Impact": "Momentum hesabı boş haftaları atlayacak; eksik veriyi dinleyici kaybı sanmayacak.",
        "Open / Uncertain Points": "Yok.",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| %18 eksik hafta | VERIFIED (diagnostic:reports/coverage_2019.md) |",
    },
    3: {
        "Purpose": "Tahmin anında kullanılabilecek bilgi sınırı donduruldu: model yalnız tahmin haftasından önce yayımlanmış veriyi görür; "
                   "böylece geleceğe ait bilgi tahmine sızmaz.",
        "Why It Changed": "Bazı özellikler hafta bittikten sonra yayımlanan verilerle hesaplanıyordu. Bu, skoru gerçekte olduğundan iyi gösterirdi. "
                          "Sınır yazılı bir kural olmalıydı.",
        "How It Works": "```text\nVERİ → FİLTRE: yayın tarihi < tahmin haftası → ÖZELLİK → M(W) → TAHMİN\n```",
        "Technical Translation": "```text\n\"tahmin anında bilinebilen bilgi sınırı\" ↔ prediction-time information boundary (S-B)\n"
                                 "\"geleceğe ait bilginin modele karışması\" ↔ temporal leakage\n\"son haftalardaki dinleyici değişimi\" ↔ M(W)\n"
                                 "\"verinin yayımlandığı an\" ↔ publication timestamp\n\"tahminin yapıldığı hafta\" ↔ forecast origin\n"
                                 "\"geçmişe dönük düzeltilmiş veri\" ↔ revised data\n```",
        "Key Decisions": "```text\nDecision: Bilgi sınırı\nAlternatives: Olay tarihi sınırı (GENERAL THEORY)\nSelected: Yayın tarihi < tahmin haftası\n"
                         "Why: Gerçek zamanda bilinmeyen veri kullanılmaz.\nTrade-off: Geç yayımlanan veri bir hafta kaybolur.\n```",
        "What Changed": "```text\nÖNCE  → özellikler olay tarihine göre seçiliyordu\nSONRA → özellikler yayın tarihine göre filtreleniyor\n```",
        "Dependencies": "Step 2: boş haftalar filtreden önce işaretlenir.",
        "Downstream Impact": "Bütün özellik ve hedef hesapları bu sınırın içinde kalacak; sınırı aşan bir özellik reddedilecek.",
        "Open / Uncertain Points": "- Geçmişe dönük düzeltilen veri hangi yayın tarihini alır?",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| Sınır yayın tarihi | VERIFIED (doc:research/S-B.md) |\n"
                                 "| Geç veri kaybı bir hafta | UNRESOLVED |",
    },
    4: {
        "Purpose": "TF-04 measurement backbone freeze edildi.",
        "How It Works": "```text\nN → C → TF-04\n```",
        "Downstream Impact": "TF-05 and TF-06 depend on this.",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| backbone frozen | VERIFIED (commit:4b1e9a0c2d3f) |",
    },
    5: {
        "Purpose": "İncelenecek sanatçı kümesi seçildi: son 52 haftada en az 40 haftası dolu olan 1.200 sanatçı.",
        "Why It Changed": "Verisi seyrek sanatçılar momentum ölçüsünü gürültülü yapıyordu.",
        "How It Works": "```text\nTÜM SANATÇILAR → 52 HAFTA KAPSAMI ≥ 40 → 1.200 SANATÇI\n```",
        "Technical Translation": "```text\n\"incelenen sanatçı kümesi\" ↔ population\n```",
        "Dependencies": "Step 2: kapsam oranı.",
        "Downstream Impact": "Momentum ve hedef yalnız bu 1.200 sanatçı için hesaplanacak.",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| 1.200 sanatçı | VERIFIED (doc:research/population.md) |",
    },
    6: {
        "Purpose": "Momentum ölçüsü tanımlandı: pencere uzunluğu (W) 8 hafta; momentum (M(W)) bu penceredeki dinleyici sayısının göreli değişimi.",
        "How It Works": "- W haftalık pencere kayar.\n- Pencerenin başı ve sonu karşılaştırılır.\n- Boş hafta pencereyi geçersiz kılar.",
        "Technical Translation": "```text\n\"son haftalardaki dinleyici değişimi\" ↔ M(W)\n\"pencere uzunluğu (hafta)\" ↔ W\n```",
        "Dependencies": "Step 3: bilgi sınırı. Step 5: sanatçı kümesi.",
        "Downstream Impact": "Hedef tanımı momentumun gelecekteki değerini tahmin etmeye dayanacak.",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| M(W) formülü | VERIFIED (code:src/features/momentum.py) |",
    },
    8: {
        "Purpose": "Tahmin hedefi belirlendi: bir sanatçının önümüzdeki 12 haftadaki dinleyici artış oranı (K(t)).",
        "Why It Changed": "Model neyi tahmin ettiğini bilmeden değerlendirilemezdi. 12 hafta, plak şirketinin karar döngüsüne uyuyor.",
        "How It Works": "```text\nN(t) → 12 HAFTA → N(t+12) → ORAN → K(t)\n```",
        "Technical Translation": "```text\n\"t haftasındaki benzersiz dinleyici sayısı\" ↔ N(t)\n\"tahminin yapıldığı hafta\" ↔ t\n```",
        "Dependencies": "Step 3: bilgi sınırı. Step 6: momentum.",
        "Downstream Impact": "Model seçimi ve değerlendirme bu hedefi kullanacak; hedef değişirse önceki skorlar karşılaştırılamaz.",
        "Open / Uncertain Points": "- 12 hafta tüm türler için uygun mu?",
        "Evidence / Provenance": "| Claim | Evidence Status |\n|---|---|\n| 12 haftalık hedef | VERIFIED (doc:research/target.md) |",
    },
}

CONTEXT = """## Objective

- Bir sanatçının önümüzdeki 12 haftada dinleyici kazanıp kazanmayacağını tahmin etmek.

## Architecture

- Haftalık veri hattı → özellikler → tahmin modeli → değerlendirme.

## Components

- Activity ölçüsü (benzersiz dinleyici sayısı)
- Veri kapsamı denetimi
- Momentum özelliği

## Data / Control Flow

```text
DİNLEME → HAFTALIK N → FİLTRE (bilgi sınırı) → MOMENTUM → HEDEF → MODEL
```

## Active Decisions

- Ana ölçü benzersiz dinleyici sayısı, toplam dinleme yardımcı.
- Hedef 12 haftalık dinleyici artışı.
- İnceleme kümesi 1.200 sanatçı.
- Momentum penceresi kayar.

## Invariants

- Eksik hafta sıfır değil, boştur.
- Model yalnız tahmin haftasından önce yayımlanmış veriyi görür.
- Her özellik aynı activity tanımını kullanır.

## Dependencies

- Haftalık dinleme dökümü (dış kaynak).

## Current Position

- Hedef tanımlandı; model seçimi henüz başlamadı.

## Open Points

- 12 hafta tüm türler için uygun mu?
"""
