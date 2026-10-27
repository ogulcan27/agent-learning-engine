# Claude Learning Skill v1.0.0 — Release Notes

## Highlights

- `/learning`: AI ile yapılan project çalışmasını anlamak için manual learning workflow.
- Coverage: hangi work unit'in öğrenilmediğini project evidence üzerinden bulur.
- Human Synchronization: ne değişti ve neden, kısa özet.
- Light / Full ULA: yalnız gerçekten gerekli konu için öğretim içeriği.
- Semantic Graph ve Knowledge Map: kavramlar ve ilişkiler.
- Personal Technical Library: kavram project'ler arasında tek bir Home'da saklanır.
- Final Integrity: her Learning Pass sonunda bütün state tutarlılık kontrolü.
- Installer: Project ve Personal scope, hash doğrulama, atomic install, rollback.

## Installation

Ayrıntı: `README.md` → Installation.

| Yöntem | Komut özeti |
|---|---|
| Clone + install | `scripts\install.ps1 -Scope Project` veya `-Scope Personal` |
| Release package | `install.ps1 -Archive claude-learning-skill-v1.0.0.zip` |
| One-line | `install.ps1` raw URL + `-Repository <OWNER>/<REPO> -Ref v1.0.0` |

Release asset hash: `SHA256SUMS.txt`.

## Compatibility

- Claude Code: project ve personal skills desteği. Claude Code 2.1.311 ile test edildi.
- Installer: Windows PowerShell 5.1 ile test edildi.
- Skill çalışması için Python, Git veya başka dependency gerekmez.
- Aynı isimde personal ve project skill varsa Claude Code personal olanı kullanır.

## Known Limitations

- Manual only. Passive tracking yoktur.
- Installer yalnız Windows PowerShell üzerinde test edildi. Diğer platformlarda skill dizinini elle kopyalayın.
- Personal library write lock tek makine içindir.
- Global cross-project Semantic Graph, HTML görünüm ve remote library yoktur.
- Kavram eşdeğerliği gibi kararlar Claude judgment'ıdır. Belirsiz durumda kullanıcıya sorulur.

## Upgrade Notes

- İlk sürüm. Önceki sürümden geçiş yoktur.
- Sonraki sürümlerde `scripts\update.ps1` yalnız skill engine'i değiştirir. `docs/learning/` ve Personal Technical Library korunur.
- Update sonrası açık Claude Code session'ını yeniden başlatın.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify-install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
```

Beklenen: `PASS`. Kontrol: file set ve her dosyanın SHA256 değeri `distribution/manifest.json` ile aynıdır.
