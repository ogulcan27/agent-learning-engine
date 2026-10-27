# Stay in the Loop v1.0.0

**In the loop.** Stay aligned with AI-assisted project work. Understand what changed, learn what matters, and retain what you learn.

- **Skill:** `stay-in-the-loop`
- **Command:** `/stay-in-the-loop`
- **Current integration:** Claude Code

## Highlights

- **Manual learning workflow.** Run `/stay-in-the-loop` when you want to catch up on what your AI-assisted work changed. Nothing runs in the background.
- **Coverage.** Finds unlearned work units from persistent project evidence such as git commits, plan documents, and issue keys.
- **Human Synchronization.** Short summaries of what changed and why.
- **Light / Full ULA.** Teaching material only for concepts you need, at the depth you need.
- **Semantic Graph.** A per-project concept graph with knowledge map views.
- **Personal Technical Library.** Each concept lives in one canonical home that is reused across projects.
- **Final Integrity.** Every learning pass ends with a cross-layer consistency check.
- **Installer.** Project and Personal scopes, SHA256 verification, atomic install and update, rollback on failure.

## Installation

See the [README](../README.md#installation) for full instructions.

| Method | Summary |
|---|---|
| Clone and install | `scripts\install.ps1 -Scope Project` or `-Scope Personal` |
| Release package | `install.ps1 -Archive stay-in-the-loop-v1.0.0.zip` |
| Quick install | `irm https://raw.githubusercontent.com/ogulcan27/stay-in-the-loop/v1.0.0/scripts/install.ps1 \| iex` (asks for Project or Personal scope) |

Release assets: `stay-in-the-loop-v1.0.0.zip` and `SHA256SUMS.txt`.

## Compatibility

- Claude Code with project / personal skills support (tested with 2.1.311). No other agent platform is supported in this release.
- Installer tested on Windows PowerShell 5.1.
- Using the skill requires no Python, Git, or other dependency.
- If `stay-in-the-loop` is installed in both Personal and Project scope, Claude Code uses the Personal one.

## Known Limitations

- The learning workflow and generated explanations are in Turkish. Language configuration is not yet available.
- Manual only; there is no passive tracking.
- The installer is untested on PowerShell 7, macOS, and Linux. On those systems, copy the skill directory manually.
- The Personal Technical Library write lock is single-machine.
- No global cross-project graph, HTML view, or remote library.
- Some decisions, such as concept equivalence, rely on the agent's judgment; the skill asks you when unsure.

## Upgrade Notes

- This is the first release; there is nothing to migrate.
- Future updates via `scripts\update.ps1` replace only the skill engine. `docs/learning/` and the Personal Technical Library are preserved.
- Restart any open Claude Code session after updating.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify-install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
```

Expected result: `PASS`. The file set and the SHA256 of every file match `distribution/manifest.json`.
