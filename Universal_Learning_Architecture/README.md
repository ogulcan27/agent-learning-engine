# Universal Learning Architecture — ULA

Universal Learning Architecture (ULA) is a reusable learning framework for complex technical subjects.

Its purpose is to organize knowledge so that the learner:

1. sees the whole system first,
2. understands the main blocks,
3. zooms into one block at a time,
4. understands mechanism before theory,
5. understands theory before mathematics,
6. keeps reference-heavy detail outside the main learning flow.

---

## Core Learning Principle

ULA uses the following learning order:

Whole
→ Parts
→ Mechanism
→ Theory
→ Math / Formalism

The system is recursive.

A complex block can become a new local map and repeat the same structure.

---

## Core Layers

### L0 — Map
Shows the whole topic or local system.

Question:

> Where am I and how is the system organized?

### L1 — Simple Explanation
Explains what a block basically does.

Question:

> What does this block do?

### L2 — Mechanism
Explains how the block works internally.

Default structure:

Input
→ Operation
→ Output
→ Next Step

Question:

> How does it work?

### L3 — Theory
Explains why the mechanism works this way.

Question:

> Why does it work?

### L4 — Math / Formalism
Expresses the mechanism precisely.

Question:

> How is this mechanism represented mathematically or formally?

### R — Reference
Stores precision-heavy information outside the main learning path.

Examples:

- exact numbers,
- citations,
- long derivations,
- audit details,
- rare formulas,
- source conflicts,
- implementation details.

R is not part of L0–L4.

---

## Main Design Principles

ULA follows these rules:

- Whole Before Parts
- Mechanism Before Theory Before Math
- Progressive Disclosure
- Recursive Zoom
- One Concept — One Home
- Stable Canonical Vocabulary
- Reference Separation
- Architecture Before Content
- Simple Technical Writing
- Explicit Concept Boundaries

---

## Core Files

### `ULA_SPECIFICATION_v1.0.md`

Defines the ULA system.

This is the authoritative specification.

It contains:

- layer definitions,
- block rules,
- recursive zoom rules,
- topic adapters,
- writing principles,
- concept-home rules,
- reference rules,
- quality requirements.

---

## Prompts

### `prompts/01_LEARNING_ARCHITECT.md`

Purpose:

Convert a subject into an approved ULA learning architecture.

It answers:

- What are the main blocks?
- How do they relate?
- Which blocks require recursive zoom?
- What belongs in L1, L2, L3, and L4?
- Which concepts have one canonical Home?
- What belongs in Reference?

The Architect does not write the full course.

---

### `prompts/02_CONTENT_BUILDER.md`

Purpose:

Convert a frozen architecture into full teaching content.

It produces:

- L1 simple explanations,
- L2 mechanisms,
- L3 theory,
- L4 math/formalism,
- examples when useful,
- oral explanations when required,
- retrieval support.

The Builder does not redesign the frozen architecture.

---

### `prompts/03_LEARNING_AUDITOR.md`

Purpose:

Audit both technical quality and learning quality.

It checks:

- architecture fidelity,
- whole-before-parts,
- progressive disclosure,
- layer separation,
- cognitive load,
- source fidelity,
- concept duplication,
- reference leakage,
- terminology stability,
- claim discipline,
- retrieval usability.

The Auditor does not rewrite the course by default.

---

## Standard Workflow

The standard ULA workflow is:

```text
PROJECT BRIEF
      ↓
LEARNING ARCHITECT
      ↓
ARCHITECTURE DRAFT
      ↓
HUMAN REVIEW
      ↓
FROZEN ARCHITECTURE
      ↓
CONTENT BUILDER
      ↓
LEARNING CONTENT
      ↓
LEARNING AUDITOR
      ↓
      ├── Content problem → Builder
      │
      ├── Architecture problem → Architect
      │
      └── PASS → Freeze
                    ↓
               Final Artifact
             PDF / HTML / Notes