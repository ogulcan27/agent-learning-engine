# GitHub Release Checklist — Agent Learning Engine v1.0.0

Repository: `https://github.com/ogulcan27/agent-learning-engine`

Durum: Phase 9 sonunda (2026-10-27). `[x]` = doğrulandı. `[ ]` = kullanıcı action'ı bekliyor.
Kanıt: `docs/audit/PHASE_9_PACKAGING_REPORT.md`, `docs/audit/PHASE_9_DISTRIBUTION_TESTS.md`.

## Content

- [x] git status reviewed
- [x] full tests PASS (`uv run --no-project python tests/run_all.py`)
- [x] distribution tests PASS (`tests/distribution/`)
- [x] VERSION = 1.0.0
- [x] README final
- [x] CHANGELOG final
- [x] release package hash verified (`dist/SHA256SUMS.txt`, deterministic rebuild)
- [x] no secrets
- [x] no absolute personal path (tracked files ve runtime skill)
- [x] construction source policy resolved
- [x] clean project install PASS
- [x] personal temp install PASS
- [x] real Claude Code smoke PASS
- [ ] LICENSE: License not yet selected. (teknik olarak bloklamaz)

## Publish

- [x] remote configured (`origin` = `https://github.com/ogulcan27/agent-learning-engine.git`)
- [x] README repository değerleri gerçek: `ogulcan27/agent-learning-engine`
- [ ] commit ready (değişiklikler working tree'de; commit yapılmadı)
- [ ] tag v1.0.0 ready
- [ ] push ready
- [ ] GitHub Release asset ready (`dist/agent-learning-engine-v1.0.0.zip` + `dist/SHA256SUMS.txt`)
- [ ] GitHub repository description ayarlandı: "Turn AI-assisted project work into structured, reusable knowledge through human synchronization, adaptive learning, semantic graphs, and persistent memory."
- [ ] publish sonrası: gerçek GitHub URL ile one-line install bir temp project'te denendi

## Kural

- Runtime skill değişirse: `scripts\build-release.ps1` tekrar çalıştır. `distribution/manifest.json` güncel olmalıdır (test A bunu kontrol eder).
- `dist/` Git'e commit edilmez. ZIP tag'den deterministic olarak yeniden üretilir.

## Publish commands

```powershell
uv run --no-project python tests/run_all.py
powershell -ExecutionPolicy Bypass -File scriptsuild-release.ps1
git add -A
git commit -m "Release 1.0.0: Agent Learning Engine"
git checkout main
git merge --ff-only Step9_Packaging_Installation_Distribution_ReleaseReadiness
git push -u origin main
git tag -a v1.0.0 -m "Agent Learning Engine 1.0.0"
git push origin v1.0.0
gh release create v1.0.0 dist/agent-learning-engine-v1.0.0.zip dist/SHA256SUMS.txt --repo ogulcan27/agent-learning-engine --title "Agent Learning Engine v1.0.0" --notes-file docs/RELEASE_NOTES_v1.0.0.md
```
