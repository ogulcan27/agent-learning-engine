# Agent Learning Engine

Turn AI-assisted project work into knowledge you can understand, retain, and reuse.

Agent Learning Engine is a project-driven learning system for AI-assisted development. It converts completed project work into structured understanding, targeted learning, semantic knowledge, and reusable technical experience.

Agent Learning Engine is designed as a platform-neutral learning architecture. **Version 1.0.0 ships with a Claude Code skill integration**: you install the `learning` skill and start it with `/learning`.

```powershell
# Install into the current project (works once v1.0.0 is published)
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/ogulcan27/agent-learning-engine/v1.0.0/scripts/install.ps1'))) -Scope Project -Repository ogulcan27/agent-learning-engine -Ref v1.0.0
```

Then, in Claude Code: `/learning`

## What It Does

When an AI agent writes much of your code, the project moves faster than your understanding of it. Agent Learning Engine closes that gap on demand:

- It finds the project work you have not reviewed yet, using persistent evidence such as git commits, plan or phase documents, and issue keys.
- It summarizes what changed and why, in a short, human-readable form.
- It teaches only the concepts you actually need, and only to the depth you need.
- It stores what you learned as reusable knowledge that carries across projects.

System Design is the primary learning axis. Data structures and algorithms appear only when they are computationally relevant to the work.

## How It Works

```text
Project Work
    ↓
/learning
    ↓
Coverage                         which work units have not been learned yet?
    ↓
Human Synchronization            what changed, and why?
    ↓
Learning Events                  which changes are worth learning?
    ↓
Light / Full ULA when needed     targeted teaching material
    ↓
Semantic Graph                   concepts and their relationships
    ↓
Concept Home / Experience Notes  reusable knowledge
    ↓
Final Integrity                  PASS / PASS_WITH_WARNINGS / FAIL
```

Routine changes are marked as not learning-relevant. Nothing is taught just because it changed.

## Core Learning Model

```text
Human Synchronization
→ Understand what the AI-assisted project work actually changed and why.

Light / Full ULA (Universal Learning Architecture)
→ Learn only the concepts that matter and only to the depth required.

Semantic Graph + Persistence
→ Connect reusable concepts, decisions, and project experience into persistent knowledge.
```

Light ULA produces a short learning note. Full ULA is a three-stage process (Architect, Builder, Auditor) and asks for your approval of the learning architecture before building content.

## Requirements

| Component | Requirement |
|---|---|
| Runtime | Claude Code with project / personal skills (tested with Claude Code 2.1.311) |
| Installer | Windows PowerShell 5.1+ (tested on 5.1; PowerShell 7, macOS and Linux are untested) |
| Git | Optional. Not needed to install. When present, git history is used as project evidence. |
| Development tests | Python 3, standard library only |

Python is not required to use the learning skill itself. The skill consists only of Markdown files: no binaries, no dependencies, no network calls.

## Installation

There are two installation scopes:

| Scope | Location | Available in |
|---|---|---|
| Project | `<project>/.claude/skills/learning/` | That repository only |
| Personal | `~/.claude/skills/learning/` | All local Claude Code projects on this machine |

The remote commands below work only after the `v1.0.0` tag and release have been published.

### Project Installation

The most inspectable path is to clone the repository, review `scripts/install.ps1`, and run it locally:

```powershell
git clone https://github.com/ogulcan27/agent-learning-engine.git
cd agent-learning-engine
git checkout v1.0.0

powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
```

If `-ProjectPath` is omitted, the current directory is used. `-ExecutionPolicy Bypass` applies only to that single PowerShell process.

### Personal Installation

From the cloned repository:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 -Scope Personal
```

This installs the skill into `~/.claude/skills/learning/` and makes it available to all local Claude Code projects.

### Quick Install

Running a remote script executes code from the referenced repository. For the most inspectable installation path, clone the repository, review `scripts/install.ps1`, and run it locally. Always pin `-Ref` to a tag or commit, not a branch.

Project (installs into `<current-project>/.claude/skills/learning/`):

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/ogulcan27/agent-learning-engine/v1.0.0/scripts/install.ps1'))) -Scope Project -Repository ogulcan27/agent-learning-engine -Ref v1.0.0
```

Personal (installs into `~/.claude/skills/learning/`):

```powershell
& ([scriptblock]::Create((Invoke-RestMethod 'https://raw.githubusercontent.com/ogulcan27/agent-learning-engine/v1.0.0/scripts/install.ps1'))) -Scope Personal -Repository ogulcan27/agent-learning-engine -Ref v1.0.0
```

The installer downloads the source archive for the given ref, verifies every file against `distribution/manifest.json`, and only then installs.

### Release Package

Each GitHub Release provides `agent-learning-engine-v1.0.0.zip` and `SHA256SUMS.txt`. Check the hash, then install with the `install.ps1` from the same tag:

```powershell
(Get-FileHash .\agent-learning-engine-v1.0.0.zip -Algorithm SHA256).Hash.ToLower()
Get-Content .\SHA256SUMS.txt

powershell -ExecutionPolicy Bypass -File .\install.ps1 -Scope Project -ProjectPath C:\path\to\your-project -Archive .\agent-learning-engine-v1.0.0.zip
```

### Installer behavior

- If hash verification fails, nothing is written.
- If the same package is already installed, the installer reports `ALREADY INSTALLED`.
- If a different version is installed, the installer stops. Use `update.ps1` (or `install.ps1 -Force`) to replace it.
- Installation is staged and verified first. On failure the previous install is restored; no partial skill is left behind.
- The installer only owns `.claude/skills/learning/`. It never touches `docs/learning/`, the Personal Technical Library, `CLAUDE.md`, your source code, git history, other skills, or other `.claude` settings.

### Project and Personal at the same time

Claude Code resolves skills with the same name as **enterprise > personal > project**. If `learning` exists in both scopes, Claude Code uses the Personal one.

Use one installation scope for `learning` unless you intentionally manage version precedence.

### Other platforms

The installer is tested only on Windows PowerShell. On macOS or Linux you can copy `.claude/skills/learning/` from a release manually; this path is untested.

## Usage

The learning workflow runs only when you explicitly invoke `/learning`. Normal project work never starts it, and there is no passive tracking. This is an intentional design property: the skill sets `disable-model-invocation: true`, so the agent cannot start it on its own.

On the first `/learning` run in a project, the skill detects that no learning state exists and asks for your approval before creating `docs/learning/`. The installer never creates this directory.

## Commands

| Command | Description |
|---|---|
| `/learning` | Run the full workflow; asks for scope if several work units are open. |
| `/learning latest` | Learn from the most recent work unit only. |
| `/learning pending` | Return to deferred or partially learned work units. |
| `/learning catch-up` | Work through all open learning gaps. |
| `/learning resume` | Continue an unfinished learning pass. |
| `/learning map` | Show the root knowledge map. |
| `/learning map <node-id>` | Zoom into one node of the map (add `L1`–`L4` for a depth view). |
| `/learning concept <concept-id>` | Show a concept's home page and its project pointer. |
| `/learning library` | Show Personal Technical Library status and index. |
| `/learning experiences` | List project experience notes. |
| `/learning debt` | List open knowledge debt. |
| `/learning integrity` | Run the final integrity check and suggest repairs for derived files. |

Further arguments (`show skipped`, `new`, `abandon <pass-id>`, `map debt`, `map sync`, `<work-unit-id>`) are listed in `.claude/skills/learning/SKILL.md`.

## Skill State vs Project State

| Layer | Location | Written by |
|---|---|---|
| Skill engine | `.claude/skills/learning/` | Installer only; read-only at runtime |
| Project learning state | `docs/learning/` in your project | `/learning` |
| Personal Technical Library | Configured separately through `personal_library_path` | `/learning`, only when configured |

Updating or uninstalling the skill does not delete project learning state or the Personal Technical Library. Whether you commit `docs/learning/` to your own repository is your choice.

## Personal Technical Library

The Personal Technical Library is a cross-project knowledge store built on the principle *One Concept, One Home*: each concept has one canonical page, and projects link to it.

- Its location is the `personal_library_path` value in `docs/learning/state/LEARNING_CONFIG.md`. Nothing is hard-coded.
- If it is not configured, the skill asks you to configure it, keep knowledge local to the project (`LOCAL_TEMPORARY`), or defer the decision.
- Writes use a single-machine write lock and an all-or-nothing transaction.

## Updating

```powershell
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\update.ps1 -Scope Personal -Repository ogulcan27/agent-learning-engine -Ref <tag>
```

An update requires an existing install and replaces only the skill engine, atomically and with rollback. Version 1.0.0 has no state migration. Restart any open Claude Code session after updating.

## Uninstalling

```powershell
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Project -ProjectPath C:\path\to\your-project
powershell -ExecutionPolicy Bypass -File scripts\uninstall.ps1 -Scope Personal
```

Only the skill directory is removed. The script confirms:

```text
Learning state retained.
Personal Technical Library retained.
```

To discard project learning state, delete `docs/learning/` yourself.

## Verification

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify-install.ps1 -Scope Project -ProjectPath C:\path\to\your-project
```

The check confirms that the skill exists, `SKILL.md` is present, the file set matches the manifest, every SHA256 matches, and no project state has been written inside the skill directory. The result is `PASS` or `FAIL`.

## Development and Testing

The test suite lives in the development repository and is not part of the installed skill.

```text
uv run --no-project python tests/run_all.py
```

Without `uv`, with Python 3 on your `PATH`:

```text
python tests/run_all.py
```

- Standard library only; no dependencies.
- Suites: subsystem models, end-to-end integration, static audit, distribution (installer), and mutation checks.
- The distribution suite requires Windows PowerShell and never writes to your real home directory or projects.
- Build the release package with `powershell -ExecutionPolicy Bypass -File scripts\build-release.ps1`.

## Current Limitations

- **Language.** Version 1.0.0 currently uses Turkish for the learning workflow and generated learning explanations. Technical terms stay in canonical English. Language configuration is not yet part of V1.
- **Platform.** Claude Code is the only supported integration. Other agents (for example Codex, Gemini CLI, or Cursor) are not supported; they are possible future adapters, not current features.
- **Manual only.** There is no automatic or background learning.
- **Installer.** Tested only on Windows PowerShell 5.1.
- **Single machine.** The Personal Technical Library write lock is local; there is no remote or multi-user library.
- **No global graph.** The semantic graph is per project. There is no cross-project graph or HTML view.
- **Judgment.** Some decisions, such as whether two concepts are equivalent, rely on the agent's judgment. When unsure, the skill asks you.
- **Cost.** Full ULA uses significant tokens; it runs only for concepts that need it.

## Security

- The skill is Markdown instructions only. It runs no code of its own and makes no network requests.
- Remote installation downloads and runs a PowerShell script. Review it first and pin a tag or commit.
- SHA256 verification against the manifest protects package integrity: it detects corrupted, incomplete, or modified files. It is not a cryptographic publisher-authentication system, because the manifest comes from the same source. Trust in the repository itself is still required.
- For release archives, compare the ZIP hash with `SHA256SUMS.txt`.

## Versioning

Agent Learning Engine follows Semantic Versioning (`MAJOR.MINOR.PATCH`):

```text
MAJOR → breaking state or protocol compatibility change
MINOR → backward-compatible capability
PATCH → compatible fix
```

See [`CHANGELOG.md`](CHANGELOG.md) and [`docs/RELEASE_NOTES_v1.0.0.md`](docs/RELEASE_NOTES_v1.0.0.md).

## Repository Structure

```text
.claude/skills/learning/     Runtime package (the only thing that gets installed)
  SKILL.md                   Entry point and /learning router
  references/                Protocol files
  templates/                 State and artifact templates
  ula/                       Universal Learning Architecture roles
scripts/                     install, update, uninstall, verify, build-release
distribution/manifest.json   Runtime file list with SHA256 hashes
tests/                       Regression and distribution test suites
docs/                        Release notes and release checklist
docs/audit/                  Development audit records
VERSION, CHANGELOG.md
```

## License

No license has been selected yet. Until a license is added, no reuse rights are granted beyond what GitHub's terms allow.
