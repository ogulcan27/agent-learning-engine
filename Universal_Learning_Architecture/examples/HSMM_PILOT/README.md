# HSMM ULA Pilot

## Scope Note

This pilot is **not** a complete representation of the full HSMM research paper or the full ULA-based study project.

It covers only a selected subset of the project, centered on the **Model / HSMM** section.

Its purpose is to demonstrate how the **Universal Learning Architecture (ULA)** should be applied in practice.

The pilot demonstrates:

- how an approved learning architecture is structured,
- how recursive zoom is used,
- how L1–L4 learning content is written,
- how important confusion boundaries are made explicit,
- how the resulting content is audited.

The full research paper contains additional stages, including:

- data preparation,
- validation and penalty selection,
- freeze and refit,
- holdout evaluation,
- retrospective analysis,
- walk-forward analysis,
- robustness and convergence checks,
- claims,
- limitations,
- reproducibility.

Therefore:

```text
HSMM_PILOT ≠ Full Paper Study Guide

HSMM_PILOT = Partial ULA Demonstration
```

---

## Files

### `01_ARCHITECTURE_EXAMPLE.md`
Shows a partial ULA architecture for the Model / HSMM section.

### `02_CONTENT_EXAMPLE.md`
Shows representative L1–L4 teaching content for selected blocks.

### `03_AUDIT_EXAMPLE.md`
Shows a compact audit of the pilot content.

---

## Important Rule

This folder is an **example package**.

It must not be treated as the frozen architecture for the full HSMM research project.

The real project must be processed separately through:

```text
PROJECT BRIEF
    ↓
LEARNING ARCHITECT
    ↓
HUMAN REVIEW
    ↓
FROZEN ARCHITECTURE
    ↓
CONTENT BUILDER
    ↓
LEARNING AUDITOR
    ↓
CONTENT FREEZE
    ↓
FINAL ARTIFACT
```
