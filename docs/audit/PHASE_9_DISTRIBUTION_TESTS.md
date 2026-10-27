# PHASE 9 — Distribution Tests

**Tarih:** 2026-10-27
**Suite:** `tests/distribution/run_tests.py` (kalıcı). `tests/run_all.py` içinde çalışır. Mutation döngüsüne girmez.
**Kural:** Her senaryo package source'un geçici kopyasını kullanır. Gerçek repository, gerçek user home ve gerçek `~/.claude` yazılmaz. HOME geçici fixture'dır (`USERPROFILE` / `HOME`).
**Gereksinim:** Windows PowerShell 5.1+, Python standard library.

## Package Tests

| Test | Kontrol | Sonuç |
|---|---|---|
| A | Manifest: `version` = `VERSION`; `skill_name` / `entry_point`; file set ve SHA256 = runtime skill; `SKILL.md` listede; yalnız `.md`; repository `distribution/manifest.json` güncel | 7/7 PASS |
| B | ZIP: yalnız skill + manifest; `tests/`, `docs/`, construction source, `.git`, `scripts/` yok; backslash entry yok; `SHA256SUMS.txt` doğru; deterministic rebuild (aynı hash) | 5/5 PASS |
| C | Clean package: ZIP yeni dizine açılır; içerik = manifest; `verify-install.ps1` PASS | 2/2 PASS |

## Project Install

| Test | Kontrol | Sonuç |
|---|---|---|
| D | Gerçek `git init` temp project. LOCAL install exit 0; target = manifest; `docs/learning/` oluşmaz; staging kalıntısı yok; verify PASS; `-ProjectPath` yok → current directory | 6/6 PASS |
| E | Aynı package → `ALREADY INSTALLED`; farklı skill → durur, target değişmez; `-Force` → değiştirir | 4/4 PASS |

## Personal Install

| Test | Kontrol | Sonuç |
|---|---|---|
| F | Target `<temp-home>/.claude/skills/learning/`; iki farklı project aynı personal target'ı çözer; project'lere dosya yazılmaz; gerçek `~/.claude/skills/learning` durumu değişmez | 5/5 PASS |

## Update

| Test | Kontrol | Sonuç |
|---|---|---|
| G | Controlled v1.0.1 package (SKILL.md değişti + yeni template). Update exit 0; skill = v2; `docs/learning/`, `CLAUDE.md`, başka skill, `settings.json` aynı; `.git` aynı; personal library aynı; kalıntı yok; install yokken update reddedilir; aynı package → `ALREADY INSTALLED`; personal update + library aynı | 10/10 PASS |

## Rollback

| Test | Kontrol | Sonuç |
|---|---|---|
| H | Fault `stage`, `replace`, `verify` (her biri: update FAIL, eski install aynı, state aynı, kalıntı yok); fresh install `verify` fault → yarım skill yok; gerçek replacement hatası (açık dosya handle'ı directory rename'i engeller) → eski install aynı, kalıntı yok | 16/16 PASS |

Fault injection test-only env değişkenidir: `LEARNING_SKILL_TEST_FAULT`.

## Uninstall

| Test | Kontrol | Sonuç |
|---|---|---|
| K | Project: skill silinir; `docs/learning/`, `CLAUDE.md`, başka skill kalır; `Learning state retained.` + `Personal Technical Library retained.`; tekrar → `NOT INSTALLED`. Personal: skill silinir, library kalır, gerçek home değişmez | 8/8 PASS |

## State Preservation

G, H, K ve L her adımda target dışındaki bütün project dosyalarının SHA256 değerini karşılaştırır. Fark yok. `.git` dizini update sırasında değişmez. Personal library fixture hiçbir adımda değişmez.

## Failure Injection

| Test | Senaryo | Sonuç |
|---|---|---|
| I | Bad hash (source dosyası manifest'ten farklı) → red, hiçbir şey yazılmaz | PASS |
| I | Missing `SKILL.md` → red, hiçbir şey yazılmaz | PASS |
| I | Bad hash ile update → eski install aynı | PASS |
| I | Önceki kesilmiş çalıştırmadan kalan `.claude/.learning-install-*` → install engellenmez; kalıntı `.claude/skills/` dışında (skill olarak yüklenmez) | PASS |
| I | Olmayan project path → red | PASS |
| H | Interrupted staging (`stage`), target replacement failure (`replace` + açık dosya), post-replace verify failure (`verify`) | PASS |
| J | Verify: install yok → FAIL; skill içinde project state → FAIL; eksik `SKILL.md` → FAIL | 3/3 PASS |

Toplam I: 8/8 PASS.

## Remote Bootstrap

| Test | Kontrol | Sonuç |
|---|---|---|
| L | README one-line syntax (`& ([scriptblock]::Create((Invoke-RestMethod ...))) -Repository -Ref`) local HTTP server ile. GitHub source archive biçimi (`<repo>-<ref>/` top folder). Install exit 0; target = manifest; state aynı; remote verify PASS; tampered archive → hash mismatch, hiçbir şey yazılmaz; 404 → hiçbir şey yazılmaz | 6/6 PASS |

Ek manual kontrol: one-line form `-ExecutionPolicy Restricted` altında da çalışır (scriptblock, dosya değil). Dosya ile çalıştırma `-ExecutionPolicy Bypass` ister.
Gerçek GitHub URL testi: remote yok (`GITHUB_REMOTE_NOT_CONFIGURED`). Publish sonrası yapılacak.

Bulunan hata: `Get-SourceRoot` içindeki `Write-Output "Download: ..."` function return değerine karıştı. `$root` array oldu ve `Join-Path` `Download:` değerini drive saydı. Düzeltme: `Write-Host`. Sonra 80/80 PASS.

## Claude Code Smoke

Gerçek Claude Code 2.1.311, `claude -p` + `--output-format stream-json`, temp git project (PLAN.md + 1 commit), skill installer ile kuruldu.

| Kontrol | Kanıt | Sonuç |
|---|---|---|
| Skill discovery | `system/init` event `skills` listesinde `learning` var | PASS |
| `/learning` invocation | Skill yüklendi; `.claude/skills/learning/references/02_COVERAGE_PROTOCOL.md` §11 project-relative path ile okundu | PASS |
| First-run initialization | `docs/learning/` yok tespit edildi; dört state dosyası + template listelendi; onay istendi; git commit work unit evidence olarak bulundu | PASS |
| Onaysız yazma yok | Çalıştırma sonrası project'te yalnız `.claude/`, `.git`, `PLAN.md`, `src` | PASS |
| Learning OFF | Normal prompt → yalnız `Read`; skill yüklenmedi | PASS |
| Model invocation blocked | Model Skill tool ile `learning` denedi → Claude Code: `cannot be used with Skill tool due to disable-model-invocation` | PASS |

Not: İlk deneme Git Bash path conversion nedeniyle `/learning` yerine `C:/Program Files/Git/learning` gönderdi. Test harness sorunu. `MSYS_NO_PATHCONV=1` ile tekrarlandı.

Tam ULA çalıştırılmadı (maliyet). Smoke sınırı: discovery + invocation + first-run path.

## Self-Containment

Repository geçici kopyası. `StudySystem_WithAI.txt` ve `Universal_Learning_Architecture/` yok (`.git`, `dist` de yok).

| Adım | Sonuç |
|---|---|
| `tests/run_all.py` | 557/557 + distribution 80/80 PASS, mutation 18/18 CAUGHT |
| `build-release.ps1` | 38 dosya; ZIP SHA256 repository build ile aynı |
| `install.ps1 -Archive` + `verify-install.ps1` | INSTALLED, PASS |

Sonuç: runtime self-contained.

## Regression

Sonuçlar: `PHASE_9_PACKAGING_REPORT.md` §17.
