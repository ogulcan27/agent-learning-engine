# Changelog

All notable changes to Stay in the Loop are documented here. The project follows [Semantic Versioning](https://semver.org/).

## 1.0.0

First stable release. Current integration: Claude Code (runtime skill `stay-in-the-loop`).

- Manual, project-driven learning workflow started with `/stay-in-the-loop`.
- Coverage Engine: work unit discovery, gap detection, and per-unit coverage ledger.
- Human Synchronization: short summaries of what AI-assisted work changed and why.
- Standalone incremental Human Sync (`/stay-in-the-loop sync`) with persistent per-work-unit records, scoped staleness and reuse in the full workflow.
- Light / Full ULA: targeted learning content only for concepts that matter.
- Semantic Graph and knowledge map views.
- Concept Home and experience persistence, including the Personal Technical Library.
- Cross-layer integrity checks with derived-file repair.
- Project isolation: learning state is read and written only under the active project root.
- Project and Personal installation.
- Atomic update and rollback, uninstall, and install verification.
