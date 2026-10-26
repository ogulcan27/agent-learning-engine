# PHASE 2 — Migration Notes

**Kapsam:** Construction sources → `.claude/skills/learning/` canonical runtime copies.
**Yetki:** Phase 1 audit, Q9 (RESOLVED).
**Kural:** Original source dosyaları değişmedi. Düzeltmeler yalnız canonical copy içindedir. Hiçbir öğrenme kuralı değişmedi.

---

## MIG-01 — Bozuk LaTeX escape düzeltmesi (SQ-01)

| Alan | Değer |
|---|---|
| Kaynak | `Universal_Learning_Architecture/examples/HSMM_PILOT/02_CONTENT_EXAMPLE.md` |
| Hedef | `.claude/skills/learning/ula/examples/HSMM_PILOT/02_CONTENT_EXAMPLE.md` |
| Satırlar | 233, 234, 365, 367, 371, 457 |
| İşlem | Control character → LaTeX escape geri yüklendi |

| Byte | Adet | Geri yüklenen | Sonuç |
|---|---|---|---|
| `0x0D` (CR) | 3 | `\r` | `\right)`, `\right]`, `\rVert` |
| `0x0B` (VT) | 2 | `\v` | `\vartheta` (2 kez) |
| `0x07` (BEL) | 1 | `\a` | `\arg\max` |

Doğrulama: Hedef dosyada `[\x00-\x08\x0b-\x1f]` eşleşmesi = 0.

Yöntem notu: `sed` ve `perl` Windows satır sonu katmanı nedeniyle CR karakterlerini değiştiremedi. Düzeltme binary modda çalışan tek amaçlı bir script ile yapıldı. Script repository'ye eklenmedi.

## MIG-02 — Conversational artifact kaldırma (SQ-03)

| Alan | Değer |
|---|---|
| Kaynak | `Universal_Learning_Architecture/ULA_SPECIFICATION_v1.0.md` |
| Hedef | `.claude/skills/learning/ula/ULA_SPECIFICATION.md` |
| Kaldırılan | Satır 1494 (boş satır) ve satır 1495 ("Bence **ULA v1.0'ın çekirdeği artık yeterince net**…") |
| Neden | Kural değil. Sohbet artığı "sonraki adım" notudur. Not edilen adım (üç rol prompt'u) zaten mevcuttur. |

Doğrulama: `diff` yalnız bu iki satırı gösterir. Spec'in geri kalanı birebir aynıdır.

## MIG-03 — CHANGELOG runtime dışında bırakıldı (SQ-02)

| Alan | Değer |
|---|---|
| Kaynak | `Universal_Learning_Architecture/CHANGELOG.md` |
| Hedef | Yok |
| İşlem | Runtime skill içine kopyalanmadı |
| Neden | Chat wrapper metni içerir. Runtime içerik değildir. Construction source olarak repository'de kalır. |

## Değişmeden kopyalanan dosyalar

| Kaynak | Hedef |
|---|---|
| `StudySystem_WithAI.txt` | `references/00_MASTER_SYSTEM_SPEC.md` (başa metadata bloğu eklendi; kaynak metin birebir aynı) |
| `prompts/01_LEARNING_ARCHITECT.md` | `ula/LEARNING_ARCHITECT.md` |
| `prompts/02_CONTENT_BUILDER.md` | `ula/CONTENT_BUILDER.md` |
| `prompts/03_LEARNING_AUDITOR.md` | `ula/LEARNING_AUDITOR.md` |
| `templates/*.md` (4) | `ula/templates/` |
| `examples/HSMM_PILOT/README.md`, `01_*`, `03_*` | `ula/examples/HSMM_PILOT/` |

## Bilinçli olarak düzeltilmeyen sorunlar

| ID | Sorun | Neden düzeltilmedi |
|---|---|---|
| SQ-04 | Master satır 133 "ihtiyeti" yazım hatası | Q9 kapsamı dışında. Master birebir archive kalır. |
| SQ-05 | Auditor "R. Visual Density" harf çakışması | Q9 kapsamı dışında. ULA rol dosyası değiştirilmez. |
