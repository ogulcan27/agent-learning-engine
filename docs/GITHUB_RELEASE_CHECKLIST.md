# GitHub Release Checklist — v1.0.0

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
- [ ] LICENSE selected (şu an: NOT SELECTED; teknik olarak bloklamaz)

## Publish

- [ ] remote configured (`git remote add origin https://github.com/<OWNER>/<REPO>.git`)
- [ ] README `<OWNER>/<REPO>` placeholder'ları gerçek değerle değiştirildi
- [ ] commit ready (değişiklikler working tree'de; commit yapılmadı)
- [ ] tag v1.0.0 ready
- [ ] push ready
- [ ] GitHub Release asset ready (`dist/claude-learning-skill-v1.0.0.zip` + `dist/SHA256SUMS.txt`)
- [ ] publish sonrası: gerçek GitHub URL ile one-line install bir temp project'te denendi

## Kural

- Runtime skill değişirse: `scripts\build-release.ps1` tekrar çalıştır. `distribution/manifest.json` güncel olmalıdır (test A bunu kontrol eder).
- `dist/` Git'e commit edilmez. ZIP tag'den deterministic olarak yeniden üretilir.
