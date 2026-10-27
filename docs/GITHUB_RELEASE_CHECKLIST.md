# GitHub Release Checklist: Stay in the Loop v1.0.0

Internal release checklist. `[x]` = verified, `[ ]` = pending maintainer action.

- Repository: `https://github.com/ogulcan27/stay-in-the-loop`
- Release asset: `dist/stay-in-the-loop-v1.0.0.zip` + `dist/SHA256SUMS.txt`
- Evidence: `docs/audit/PHASE_9_PACKAGING_REPORT.md`, `docs/audit/PHASE_9_DISTRIBUTION_TESTS.md`

## Content

- [x] Full test suite PASS (`uv run --no-project python tests/run_all.py`)
- [x] Distribution tests PASS (`tests/distribution/`)
- [x] Mutation checks CAUGHT
- [x] `VERSION` = 1.0.0
- [x] README, CHANGELOG and release notes final
- [x] Release package rebuilt and hash recorded (`dist/SHA256SUMS.txt`, deterministic build)
- [x] No secrets, no absolute personal paths
- [x] Clean project install, personal temp install, interactive install PASS
- [x] Real Claude Code smoke PASS (`stay-in-the-loop` discovered, `/stay-in-the-loop` first run)
- [x] License: MIT (`LICENSE`)

## Publish

- [ ] `origin` points to `https://github.com/ogulcan27/stay-in-the-loop.git`
- [ ] Commit ready
- [ ] `v1.0.0` tag moved to the release commit
- [ ] Pushed
- [ ] GitHub Release created with the asset and `SHA256SUMS.txt`
- [ ] Repository description set: "Turn AI-assisted project work into structured, reusable knowledge through human synchronization, adaptive learning, semantic graphs, and persistent memory."
- [ ] After release: Quick Install tested in a temp project (choose `1`, then run `/stay-in-the-loop`)

## Commands

```powershell
git remote set-url origin https://github.com/ogulcan27/stay-in-the-loop.git
uv run --no-project python tests/run_all.py
powershell -ExecutionPolicy Bypass -File scripts/build-release.ps1
git add -A
git commit -m "Release 1.0.0: Stay in the Loop"
git checkout main
git merge --ff-only Step9_Packaging_Installation_Distribution_ReleaseReadiness
git push -u origin main
git tag -f -a v1.0.0 -m "Stay in the Loop 1.0.0"
git push -f origin v1.0.0
gh release create v1.0.0 dist/stay-in-the-loop-v1.0.0.zip dist/SHA256SUMS.txt --repo ogulcan27/stay-in-the-loop --title "Stay in the Loop v1.0.0" --notes-file docs/RELEASE_NOTES_v1.0.0.md
```

After release, in a temp project:

```powershell
irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1 | iex
```

## Rules

- If the runtime skill changes, run `scripts/build-release.ps1` again. `distribution/manifest.json` must be current (distribution test A checks it).
- `dist/` is not committed. The ZIP is rebuilt deterministically from the tag.
