# PHASE 9 — Packaging + Installation + Distribution + Release Readiness

**Tarih:** 2026-10-27
**Version:** 1.0.0
**Architecture Status:** V1 FROZEN (değişmedi)

## 1. Status

**PASS. Release Status: RELEASE_READY.**

- Runtime skill `.claude/skills/learning/` HEAD (`a731966`) ile byte-identical. Runtime protocol değişikliği yok.
- Installer, updater, uninstaller, verifier, release build eklendi.
- Kalıcı distribution suite: 80/80 PASS. Full regression 557/557 PASS, mutation 18/18 CAUGHT.
- Gerçek Claude Code smoke PASS (OI-01 kapandı, smoke sınırında).
- GitHub remote yok: `GITHUB_REMOTE_NOT_CONFIGURED`. README `<OWNER>/<REPO>` placeholder kullanır. (Branding sonrası: `origin` yapılandırıldı, README gerçek repository kullanır; bkz. Branding alignment.)
- Commit, push, tag, GitHub Release yapılmadı.

## 2. V1 Package

| Alan | Değer |
|---|---|
| Runtime package | `.claude/skills/learning/` (38 dosya, yalnız `.md`) |
| Release ZIP | `dist/agent-learning-engine-v1.0.0.zip` |
| ZIP SHA256 | `e9f968189405f293b6f17b470f9e3fc77fc180578f79316656000db1166ab1cf` |
| ZIP içeriği | `.claude/skills/learning/**` (38) + `distribution/manifest.json` |
| Build | `scripts/build-release.ps1`. Ordinal sıra, sabit timestamp, `/` separator → deterministic. İki build aynı hash. |

ZIP içinde `tests/`, `docs/`, `scripts/`, construction source, `.git` yoktur (test B).

## 3. Repository Layout

```text
DEVELOPMENT REPOSITORY (source of truth)      RUNTIME PACKAGE
.claude/skills/learning/  ─────────────────→  .claude/skills/learning/
scripts/                  installer, build
distribution/manifest.json
tests/                    regression + distribution
docs/, docs/audit/
README.md, CHANGELOG.md, VERSION
dist/                     build çıktısı, Git'e girmez
```

`dist/` kararı: **track edilmez** (`.gitignore`). Release modeli: source repo + GitHub Release asset. ZIP tag'den deterministic olarak yeniden üretilir.

## 4. Version

- `VERSION` = `1.0.0`. Semantic Versioning kuralları README'de.
- Runtime protocol içine version yazılmadı. Version `VERSION` ve manifest içindedir.

## 5. Distribution Manifest

`distribution/manifest.json`:

| Alan | Değer |
|---|---|
| `version` | `1.0.0` |
| `skill_name` | `learning` |
| `entry_point` | `SKILL.md` |
| `package_root` | `.claude/skills/learning` |
| `files[]` | `path` (skill köküne göre) + `sha256` |

- Hash LF içerik üzerindedir. `.gitattributes` `*.md eol=lf` working copy'yi LF tutar; clone ve GitHub archive aynı byte'ları verir.
- Test A: repository manifest güncel olmalıdır. Runtime değişir ve build unutulursa suite FAIL verir.

## 6. Installer

`scripts/install.ps1` tek engine'dir. `update.ps1` ve `verify-install.ps1` onu `-Update` / `-VerifyOnly` ile çağırır. Logic duplicate değildir.

| Parametre | Anlam |
|---|---|
| `-Scope Project` / `Personal` | Canonical target. Başka target yok. |
| `-ProjectPath` | Yoksa current directory |
| `-Repository`, `-Ref` | REMOTE: `https://github.com/<repo>/archive/<ref>.zip` |
| `-Archive` | Release ZIP |
| `-Force` | Farklı install'ı açıkça değiştir |
| `-BaseUrl` | Varsayılan `https://github.com`. Test HTTP server için. |

Akış:

```text
SOURCE (local / archive / download → temp)
↓
MANIFEST + HASH VERIFY (fail → nothing written)
↓
TARGET CHECK (same → ALREADY INSTALLED; different → stop unless update / -Force)
↓
STAGE (<base>/.claude/.learning-install-<id>/stage) → VERIFY
↓
OLD TARGET → backup (rename) → STAGE → TARGET (rename) → VERIFY TARGET
↓
SUCCESS → delete backup     FAILURE → ROLLBACK
```

- Staging `.claude/skills/` dışındadır. Crash sonrası kalıntı ikinci bir `learning` skill olarak yüklenmez.
- Staging ve target aynı volume'dadır. Yer değiştirme tek rename'dir.
- Hata `throw` ile verilir, `exit` kullanılmaz. One-line (scriptblock) çalıştırmada kullanıcının console'u kapanmaz. `-File` ile exit code 1 olur.
- Script ASCII'dir (PowerShell 5.1 BOM'suz UTF-8'i ANSI okur).

Sahiplik: yalnız `.claude/skills/learning/`. `docs/learning/`, personal library, `CLAUDE.md`, source, git, başka skill ve `.claude` ayarlarına dokunmaz (test G, H, K, L hash karşılaştırması).

## 7. Project Install

Temp `git init` project. Target `<project>/.claude/skills/learning/`. `docs/learning/` installer tarafından oluşturulmaz. Mevcut install: same → `ALREADY INSTALLED`; different → durur (sessiz overwrite yok). Test D, E.

## 8. Personal Install

- Home: `USERPROFILE`, yoksa `HOME`. Claude Code'un home çözümü ile aynı kaynak. Hard-coded kullanıcı adı yok.
- Test: geçici HOME fixture. Target `<temp-home>/.claude/skills/learning/`. İki farklı project aynı personal target'ı çözer. Gerçek `~/.claude/skills/learning` testlerden önce de sonra da yoktu.
- Precedence (resmi Claude Code docs, `code.claude.com/docs/en/skills`): aynı isimde skill için **enterprise > personal > project**. Personal install varsa project-local `learning` kullanılmaz. README bunu yazar ve tek scope önerir.
- Önerilen "project-local canonical" kuralı Claude Code davranışına ters olduğu için yazılmadı (§20).

## 9. Update

`update.ps1`: mevcut install gerekir; source verify; atomic replace; rollback. `docs/learning/` ve library değişmez. State migration yok (1.0.0'da hedef yok). Future breaking state değişikliği MAJOR version ile gelir; updater skill engine dışında bir şey yazmaz, bu yüzden state'i bozamaz. Test G.

## 10. Uninstall

`uninstall.ps1`: target önce rename edilir, sonra silinir. Rename başarısızsa eski install aynı kalır. Çıktı `Learning state retained.` ve `Personal Technical Library retained.` Destructive state flag yok. Test K.

## 11. Verification

`verify-install.ps1` → `PASS` / `FAIL`. Kontrol: target var, `SKILL.md` var, file set = manifest, SHA256, fazladan dosya yok (project state skill içine yazılmışsa FAIL). Test C, D, J, L.

## 12. Remote / GitHub Install

- REMOTE mode GitHub source archive kullanır (`/archive/<ref>.zip`). Tag ve commit için çalışır. Top folder deterministic çözülür.
- Test L: README one-line syntax local HTTP server ile çalıştırıldı. Install, verify, tampered archive (red, yazma yok), 404 (yazma yok) PASS.
- One-line form `Restricted` execution policy altında çalışır. Dosya çalıştırma `-ExecutionPolicy Bypass` ister (process scope).
- Güvenlik notu README'de: remote script önce incelenmeli; hash kontrolü bütünlük sağlar, kaynak güveni sağlamaz.
- Gerçek GitHub URL ile test: remote yok. Publish sonrası checklist maddesi.

## 13. Clean Project Pilot

Release ZIP yeni temp dizine açıldı → `verify-install.ps1` PASS (test C). Temp git project'e LOCAL ve ARCHIVE install PASS.

## 14. Real Claude Code Pilot

Claude Code 2.1.311. Temp git project: `PLAN.md`, `src/features.py`, 1 commit. Skill `install.ps1 -Scope Project` ile kuruldu.

| Kontrol | Sonuç |
|---|---|
| Discovery: `init.skills` içinde `learning` | PASS |
| `claude -p "/learning"`: skill yüklendi, project-relative reference okundu (`02` §11) | PASS |
| First-run: `docs/learning/` yok → initialization önerisi, onay sorusu, git commit work unit olarak bulundu | PASS |
| Onaysız dosya yazılmadı | PASS |
| Learning OFF: normal prompt skill'i yüklemedi | PASS |
| Model `Skill(learning)` denedi → Claude Code `disable-model-invocation` ile engelledi | PASS |

Maliyet: yaklaşık 0.53 USD (4 çağrı). Full ULA çalıştırılmadı. OI-01: smoke sınırında kapandı. Gerçek project üzerinde uzun pilot kullanıcı kullanımında devam eder.

## 15. Self-Containment

Temp repository kopyası, construction source olmadan: full suite (mutation dahil) PASS, build aynı ZIP hash, install + verify PASS. **Runtime self-contained.**

## 16. Distribution Tests

`tests/distribution/run_tests.py`: 80 test, A–L. Ayrıntı: `PHASE_9_DISTRIBUTION_TESTS.md`. `run_all.py` bunu bir kez çalıştırır; mutation döngüsü yalnız protocol suite'lerini çalıştırır.

## 17. Full Regression

| Suite | Sonuç |
|---|---|
| phase3 / 4 / 5 / 6 / 7 | 24/24, 46/46, 74/74, 83/83, 163/163 PASS |
| integration | 141/141 PASS |
| static | 26/26 PASS |
| **Phase 8 baseline toplam** | **557/557 PASS** |
| distribution | 80/80 PASS |
| mutation | 18/18 CAUGHT |

- Komut: `uv run --no-project python tests/run_all.py`.
- `python tests/run_all.py`: bu makinede `python` PATH'te yok (yalnız Windows Store alias). Kök neden ortamdır, suite değil. Aynı komut `uv` olmadan, doğrudan bir CPython 3.14 yorumlayıcısı ile çalıştırıldı: PASS. Suite standard library dışında bir şey import etmez.
- Runtime protocol semantic diff: yok (`git diff HEAD -- .claude` boş).

## 18. Security / Privacy Audit

Kapsam: public olacak bütün tracked + yeni dosyalar (101), ayrıca `git log -p`.

| Kontrol | Sonuç |
|---|---|
| API key, token, private key, password | Yok |
| Email | Yok (yalnız test fixture `example.invalid`) |
| Absolute personal path, AppData, temp path | Yok |
| Private Jira / şirket URL | Yok |
| Machine-specific identifier | `tests/static/run_tests.py` portability regex'i geliştiricinin Windows kullanıcı adını literal içeriyordu. Kaldırıldı. Generic path pattern'leri (`X:\`, `/Users/`, `/home/`, `AppData`) kaldı; P8-M6 hâlâ yakalanır. |
| Git history | Aynı literal Phase 8 commit'inde bir kez var. Secret değildir; aynı isim commit author metadata'sında zaten vardır. History rewrite gerekmez. |

Sonuç: **PASS**. Secret yok. Not: push ile commit author email public olur (kullanıcı kararı).

## 19. Construction Source Policy

| Koşul | Durum |
|---|---|
| Runtime self-containment PASS | Evet (§15) |
| Source Git history'de | Evet: `002b8ab`. Working copy HEAD ile aynıydı. |

Karar: `StudySystem_WithAI.txt` ve `Universal_Learning_Architecture/` working tree'den `git rm` ile kaldırıldı (staged, commit yok). Geri alma: `git restore --staged --worktree StudySystem_WithAI.txt Universal_Learning_Architecture`. History'de kalır. Canonical runtime kopyaları: `references/00_MASTER_SYSTEM_SPEC.md`, `ula/`.

## 20. Deviations

| Spec | Uygulama | Gerekçe |
|---|---|---|
| §32 önerilen kural: project-local install canonical | README Claude Code'un gerçek kuralını yazar: personal > project. Tek scope önerilir. | Resmi docs. Yanlış davranış yazılmaz. |
| §7 ZIP içeriği `.claude/skills/learning/` | Ek: `distribution/manifest.json` | Installer ZIP'i hash ile doğrulayabilsin. |
| §9 iki source mode | Üç mode: LOCAL, ARCHIVE, REMOTE | README yöntem B (release package) için. |
| §26 gerçek precedence testi | Docs ile doğrulandı; ampirik test yapılmadı | Ampirik test gerçek `~/.claude/skills/` içine yazmayı gerektirir. Yasak. |
| §23 `python tests/run_all.py` | Doğrudan CPython yorumlayıcısı ile çalıştırıldı | Bu makinede `python` PATH'te yok. |

### Branding alignment (Phase 9 sonrası)

- Public product adı: **Agent Learning Engine**. Repository adı önerisi: `agent-learning-engine`.
- Release asset: `agent-learning-engine-v1.0.0.zip`. Eski `claude-learning-skill-v1.0.0.zip` kullanılmaz.
- Runtime identity değişmedi: `.claude/skills/learning/`, `/learning`, manifest `skill_name = learning`.
- V1 platform: yalnız Claude Code. Başka platform desteği iddia edilmez.

### Identity rename (release öncesi)

- Product: **Stay in the Loop** (tagline: "In the loop."). Repository adı değişmedi: `ogulcan27/agent-learning-engine`. Asset: `agent-learning-engine-v1.0.0.zip`.
- Skill: `.claude/skills/learning/` → `.claude/skills/stay-in-the-loop/`, `name: stay-in-the-loop`, komut `/stay-in-the-loop`. Manifest `skill_name` / `package_root` güncellendi.
- Değişmeyen: `docs/learning/`, learning domain terimleri, bütün protocol kuralları. 38 runtime dosyasının her biri HEAD sürümü + yalnız identity substitution ile birebir aynıdır (program ile doğrulandı).
- Bu rapordaki önceki `learning` / `/learning` ifadeleri o tarihteki identity'yi gösterir (historical).

## 21. Open Issues

| ID | Konu | Sınıf |
|---|---|---|
| OI-P9-01 | GitHub remote yok. Gerçek raw URL ile one-line install publish sonrası denenmeli. | EXTERNAL_ACTION |
| OI-P9-02 | LICENSE: NOT SELECTED. | USER_DECISION (bloklamaz) |
| OI-P9-03 | Installer yalnız Windows PowerShell 5.1 üzerinde test edildi. PowerShell 7 / macOS / Linux test edilmedi. | NON_BLOCKING_V1 |
| OI-P9-04 | Project + personal precedence ampirik olarak test edilmedi (docs ile doğrulandı). | NON_BLOCKING_V1 |
| OI-P9-05 | Real Claude Code pilot smoke sınırında. Full ULA ve persistence gerçek kullanımda doğrulanacak. | NON_BLOCKING_V1 |
| OI-P9-06 | Hash kontrolü bütünlük sağlar, authenticity sağlamaz (manifest aynı kaynaktan). İmza yok. | NON_BLOCKING_V1 |
| OI-08 (Phase 8) | Eski temp test dizinleri sistem temp'te. Phase 9 suite kendi dizinini siler. | housekeeping |

## 22. Release Readiness

| Kriter | Durum |
|---|---|
| full regression PASS | [x] |
| distribution tests PASS | [x] |
| clean project install PASS | [x] |
| personal temp install PASS | [x] |
| installer rollback PASS | [x] |
| secret audit PASS | [x] |
| self-containment PASS | [x] |
| real Claude Code smoke PASS | [x] |

**RELEASE_READY.** Remote yokluğu package readiness'i engellemez. One-line komut README'de placeholder ile kalır.

## 23. Exact Publish Steps

> Güncel (final identity): repository `ogulcan27/stay-in-the-loop`, asset `stay-in-the-loop-v1.0.0.zip`. Geçerli komutlar: `docs/GITHUB_RELEASE_CHECKLIST.md`. Aşağıdaki adımlar historical kayıttır.

Kullanıcı tarafından çalıştırılır.

Branding sonrası güncel: `origin` = `https://github.com/ogulcan27/agent-learning-engine.git` (yapılandırıldı, push yok). `main` Step 1'de; fast-forward mümkün.

```powershell
uv run --no-project python tests/run_all.py
powershell -ExecutionPolicy Bypass -File scripts\build-release.ps1
git add -A
git commit -m "Release 1.0.0: Agent Learning Engine"
git checkout main
git merge --ff-only Step9_Packaging_Installation_Distribution_ReleaseReadiness
git push -u origin main
git tag -a v1.0.0 -m "Agent Learning Engine 1.0.0"
git push origin v1.0.0
gh release create v1.0.0 dist/agent-learning-engine-v1.0.0.zip dist/SHA256SUMS.txt --repo ogulcan27/agent-learning-engine --title "Agent Learning Engine v1.0.0" --notes-file docs/RELEASE_NOTES_v1.0.0.md

# Publish sonrası, temp project içinde:
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/ogulcan27/agent-learning-engine/v1.0.0/scripts/install.ps1'))) -Scope Project -Repository ogulcan27/agent-learning-engine -Ref v1.0.0
```
