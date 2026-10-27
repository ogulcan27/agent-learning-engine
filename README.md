# Claude Learning Skill

Version: see [`VERSION`](VERSION) · Changelog: [`CHANGELOG.md`](CHANGELOG.md) · Release notes: [`docs/RELEASE_NOTES_v1.0.0.md`](docs/RELEASE_NOTES_v1.0.0.md)

## What is Claude Learning Skill?

Claude Learning Skill, Claude Code için manual bir learning workflow'dur (`/learning`).

AI ile bir project üzerinde çalışırsınız. Kod hızlı değişir. Siz her değişikliği anlamayabilirsiniz.
`/learning` bu açığı kapatır:

- Project evidence üzerinden ne değiştiğini bulur (git commit, plan / phase doc, issue key).
- Değişikliği size kısa ve anlaşılır biçimde özetler.
- Yalnız gerçekten anlamanız gereken konu için öğretim içeriği üretir.
- Öğrendiğiniz kavramı project'ler arasında yeniden kullanılabilir biçimde saklar.

Ana öğrenme ekseni System Design'dır. DSA yalnız hesaplama açısından ilgili olduğunda girer.
Kullanıcı içeriği Türkçedir. Technical term İngilizce canonical biçimde kalır.

## Core Architecture

```text
Human Synchronization
→ understand what happened

Light / Full ULA (Universal Learning Architecture)
→ learn what matters

Semantic Graph + Persistence
→ organize and retain reusable knowledge
```

## Requirements

| Gerekli | Ne için | Not |
|---|---|---|
| Claude Code | Skill'i çalıştırmak | Project / personal skills desteği. Claude Code 2.1.311 ile test edildi. |
| Windows PowerShell 5.1+ | Installer script'leri | Windows PowerShell 5.1 ile test edildi. PowerShell 7 test edilmedi. |
| Git | Opsiyonel | Install için gerekmez. Skill, varsa git history'yi evidence olarak okur. |
| Python 3 | Yalnız development testleri | Standard library. **Python is not required to use the skill.** |

Runtime skill yalnız Markdown dosyalarından oluşur. Binary, dependency veya network çağrısı yoktur.

## Installation

İki canonical install scope vardır:

| Scope | Target | Kapsam |
|---|---|---|
| Project | `<project>/.claude/skills/learning/` | Yalnız bu repository |
| Personal | `~/.claude/skills/learning/` | Bu makinedeki bütün local Claude Code project'leri |

Üç kurulum yöntemi vardır. En denetlenebilir yöntem A'dır.

### A. Clone + install (recommended)

```powershell
git clone https://github.com/<OWNER>/<REPO>.git
cd <REPO>
git checkout v1.0.0
# Review scripts\install.ps1 first.

# Project
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Project -ProjectPath C:\path\to\your-project

# Personal
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Personal
```

- `-ProjectPath` verilmezse current directory kullanılır.
- `-ExecutionPolicy Bypass` yalnız bu process için geçerlidir. Sistem policy'sini değiştirmez.

### B. Release package

1. GitHub Release sayfasından `claude-learning-skill-v1.0.0.zip`, `SHA256SUMS.txt` ve aynı tag'deki `scripts/install.ps1` dosyasını indirin.
2. Hash'i kontrol edin:

   ```powershell
   (Get-FileHash .\claude-learning-skill-v1.0.0.zip -Algorithm SHA256).Hash.ToLower()
   Get-Content .\SHA256SUMS.txt
   ```

3. Script'i inceleyin. Sonra çalıştırın:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1 -Scope Project -ProjectPath C:\path\to\your-project -Archive .\claude-learning-skill-v1.0.0.zip
   ```

ZIP içeriği yalnız `.claude/skills/learning/` ve `distribution/manifest.json` dosyasıdır.

### C. Quick Install (one-line PowerShell)

> Remote script çalıştırmadan önce kaynağı incelemek daha güvenlidir. Bu yöntem kolaylık içindir. İnceleme için A veya B yöntemini kullanın.

Safer: önce indirin, inceleyin, sonra çalıştırın:

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/<OWNER>/<REPO>/v1.0.0/scripts/install.ps1 -OutFile install.ps1
notepad install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Scope Project -Repository <OWNER>/<REPO> -Ref v1.0.0
```

One-line, Project (current directory):

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/<OWNER>/<REPO>/v1.0.0/scripts/install.ps1'))) -Scope Project -Repository <OWNER>/<REPO> -Ref v1.0.0
```

One-line, Personal:

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/<OWNER>/<REPO>/v1.0.0/scripts/install.ps1'))) -Scope Personal -Repository <OWNER>/<REPO> -Ref v1.0.0
```

- `-Ref` bir tag veya commit olmalıdır. Branch adı kullanmayın; içerik değişebilir.
- Installer `https://github.com/<OWNER>/<REPO>/archive/<Ref>.zip` arşivini indirir.
- Bu syntax Windows PowerShell 5.1 ile test edildi (test HTTP server ile).

### Installer güvenlik kuralları

```text
DOWNLOAD → TEMP STAGING → MANIFEST / HASH VERIFY → TARGET CHECK → ATOMIC INSTALL
```

- Hash doğrulaması geçmezse target'a hiçbir şey yazılmaz.
- Aynı package zaten kuruluysa: `ALREADY INSTALLED`.
- Farklı bir skill kuruluysa: installer durur. Değiştirmek için `update.ps1` veya `install.ps1 -Force` kullanın.
- Hata olursa eski install geri yüklenir (rollback). Yarım skill kalmaz.
- Installer yalnız `.claude/skills/learning/` dizininin sahibidir. `docs/learning/`, Personal Technical Library, `CLAUDE.md`, application source, git history, başka skill ve başka `.claude` ayarına dokunmaz.

## Usage

Normal çalışma sırasında skill kapalıdır. Passive tracking yoktur.

```text
Normal project work → Learning OFF
/learning           → Learning ON
```

Claude bu skill'i kendisi çağıramaz (`disable-model-invocation: true`). Yalnız siz `/learning` yazınca çalışır.

İlk `/learning` çağrısında skill project state'in olmadığını görür. Onayınızı ister. Onay verirseniz `docs/learning/` oluşturulur. Installer bu dizini oluşturmaz.

## Main Commands

| Komut | Ne yapar |
|---|---|
| `/learning` | Tam akış. Açık work unit varsa scope sorar. |
| `/learning latest` | Yalnız son work unit. |
| `/learning pending` | Ertelenmiş (`DEFERRED`) veya yarım (`PARTIAL`) work unit'ler. |
| `/learning catch-up` | Bütün açık gap'ler. |
| `/learning resume` | Yarım kalan Learning Pass'e devam eder. |
| `/learning map` | Root Knowledge Map. |
| `/learning map <node-id>` | Bir node'a zoom. `L1`–`L4` ile depth view. |
| `/learning concept <concept-id>` | Concept Home ve project pointer. |
| `/learning library` | Personal Technical Library durumu ve index. |
| `/learning experiences` | Project Experience Note listesi. |
| `/learning debt` | Açık Knowledge Debt listesi. |
| `/learning integrity` | Final Integrity check. Yalnız derived artifact onarımı önerir. |

Diğer argümanlar: `show skipped`, `new`, `abandon <pass-id>`, `map debt`, `map sync`, `<work-unit-id>`. Tam liste: `.claude/skills/learning/SKILL.md` §6.

## How /learning Works

```text
/learning
↓
Coverage            → hangi work unit öğrenilmedi?
↓
Human Sync          → ne değişti, neden?
↓
Learning Event      → öğrenmeye değer olan değişiklik
↓
Light / Full ULA    → yalnız MUST UNDERSTAND + knowledge gap varsa
↓
Semantic Graph      → kavramlar ve ilişkiler
↓
Concept Home / Experience → yeniden kullanılabilir bilgi
↓
Integrity           → PASS / PASS_WITH_WARNINGS / FAIL
```

- Coverage, work unit history'yi `/learning` anında project evidence üzerinden yeniden kurar.
- Light ULA kısa bir öğretim notudur. Full ULA üç aşamalıdır (Architect → Builder → Auditor) ve mimari için onayınızı ister.
- Gereksiz öğretim yoktur. Rutin değişiklik `NOT_LEARNING_RELEVANT` olur.

## State vs Skill

```text
SKILL INSTALL / UPDATE ≠ LEARNING STATE RESET
```

| Katman | Konum | Yazan |
|---|---|---|
| Skill (engine) | `.claude/skills/learning/` | Installer. Runtime'da read-only. |
| Project state | `<project>/docs/learning/` | `/learning` |
| Personal state | `personal_library_path` (project config içinde) | `/learning`, yalnız yapılandırılmışsa |

Update yalnız skill engine'i değiştirir. Project state ve personal library korunur.
`docs/learning/` dizinini kendi project repository'nizde commit etmek sizin kararınızdır.

## Personal Technical Library

- Project'ler arasında paylaşılan kavram deposudur: One Concept — One Home.
- Konumu `docs/learning/state/LEARNING_CONFIG.md` içindeki `personal_library_path` değeridir. Hard-coded değildir.
- Yapılandırılmadıysa skill sorar: yapılandır, `LOCAL_TEMPORARY` (yalnız bu project) veya ertele.
- Yazma işlemi tek makine write lock ve all-or-nothing transaction ile yapılır.
- Installer ve uninstaller bu dizine hiçbir zaman dokunmaz.

## Updating

```powershell
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Personal -Repository <OWNER>/<REPO> -Ref v1.0.1
```

- Mevcut install gerekir.
- Akış: stage → verify → eski skill backup → yeni skill → verify → backup sil. Hata olursa rollback.
- 1.0.0 için state migration yoktur. Gelecekte breaking state değişikliği MAJOR version ile gelir ve release notes içinde belirtilir.
- Update sonrası açık Claude Code session'ını yeniden başlatın.

## Uninstalling

```powershell
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Personal
```

Yalnız skill dizini silinir. Çıktı:

```text
Learning state retained.
Personal Technical Library retained.
```

Learning state'i silmek isterseniz `docs/learning/` dizinini kendiniz silin.

## Verifying an install

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify-install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
```

Kontrol: target var, `SKILL.md` var, file set manifest ile aynı, her dosyanın SHA256 değeri aynı, skill içinde project state yok. Sonuç: `PASS` veya `FAIL`.

### Project ve Personal aynı anda

Claude Code resmi kuralı: aynı isimde skill birden çok seviyede varsa **personal, project'ten önce gelir** (enterprise > personal > project). Yani personal `learning` kuruluysa, project-local `learning` kullanılmaz.

V1 önerisi:

- Bir scope seçin. Aynı makinede project ve personal install'ı birlikte kullanmayın.
- Project'e özel version gerekiyorsa personal install'ı kaldırın.
- İkisini birlikte kullanıyorsanız ikisinin de aynı version olduğunu `verify-install.ps1` ile kontrol edin.

## Testing

Development repository için. Runtime skill'in parçası değildir.

```text
uv run --no-project python tests/run_all.py
```

`uv` yoksa (Python 3 PATH'te ise):

```text
python tests/run_all.py
```

- Yalnız Python standard library. Dependency yok.
- Suite'ler: subsystem modelleri (phase3–phase7), end-to-end integration, static audit, distribution (installer), mutation check.
- Distribution suite Windows PowerShell gerektirir. Gerçek user home veya gerçek project'e yazmaz.
- Release package üretmek: `powershell -ExecutionPolicy Bypass -File scripts\build-release.ps1`

## Versioning

Semantic Versioning: `MAJOR.MINOR.PATCH`.

```text
MAJOR → breaking state / protocol compatibility change
MINOR → backward-compatible capability
PATCH → compatible fix
```

## Limitations

- Manual only. Otomatik veya arka planda öğrenme yoktur.
- Installer Windows PowerShell için yazıldı ve test edildi. macOS / Linux için `.claude/skills/learning/` dizinini elle kopyalayın.
- Personal library write lock tek makine içindir. Remote / multi-user library yoktur.
- Global cross-project Semantic Graph ve HTML görünüm yoktur.
- Kavram eşdeğerliği gibi bazı kararlar Claude judgment'ıdır. Belirsiz durumda skill size sorar.
- Full ULA token açısından maliyetlidir. Yalnız gerekli konular için çalışır.

## Security

- Skill yalnız Markdown talimatıdır. Kendi başına kod çalıştırmaz ve network'e erişmez.
- Remote install bir PowerShell script'i indirir ve çalıştırır. Önce kaynağı inceleyin. Sabit bir tag veya commit kullanın.
- Installer her dosyanın SHA256 değerini manifest ile doğrular. Bu kontrol bozuk veya eksik package'i yakalar. Manifest aynı kaynaktan gelir; bu yüzden kaynağın kendisine güvenmeniz gerekir.
- Release ZIP için `SHA256SUMS.txt` ile karşılaştırın.

## License

LICENSE: NOT SELECTED. Lisans seçilmeden public repository içeriğini başkalarının yeniden kullanma hakları belirsizdir.

## Repository Structure

```text
.claude/skills/learning/   RUNTIME PACKAGE (dağıtılan tek ürün)
  SKILL.md                 entry point (/learning router)
  references/              protocol 00–07
  templates/               state ve artifact template'leri
  ula/                     Universal Learning Architecture rolleri
scripts/                   install, update, uninstall, verify, build-release
distribution/manifest.json runtime file listesi + SHA256
tests/                     regression + distribution suite (development)
docs/                      release notes, release checklist
docs/audit/                phase audit raporları (development)
VERSION, CHANGELOG.md
```

Development repository source of truth'tur. Installer yalnız runtime package'i target'a kopyalar.
