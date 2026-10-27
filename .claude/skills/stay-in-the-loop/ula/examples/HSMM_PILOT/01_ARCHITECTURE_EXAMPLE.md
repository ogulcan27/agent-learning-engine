# ULA Learning Architecture — HSMM Pilot

## Scope Note

This pilot is **not** the architecture of the full research paper.

It covers only a selected subset centered on the **Model / HSMM** section.

Its purpose is to demonstrate the structure expected from the ULA Learning Architect.

```text
HSMM_PILOT ≠ Full Paper Architecture

HSMM_PILOT = Partial Architecture Example
```

---

## Project

**Project:**  
HSMM ULA Pilot

**Architecture Version:**  
0.1

**Status:**  
EXAMPLE — NOT FROZEN FOR FULL PROJECT

---

# 1. Learning Goal

## Topic
Model / HSMM architecture used in the research project.

## Learner Goal
Build a top-down mental model of how the hidden-state model is structured, how duration is represented, how the model is fitted, and how a fitted model is read.

## Expected Depth
Research-oriented pilot.

## Use Case
- learning-method demonstration,
- oral explanation practice,
- ULA workflow example.

### Required Capabilities
1. Explain the difference between observed returns and hidden states.
2. Explain the main difference between HMM and HSMM duration logic.
3. Separate emission, transition, and duration roles.
4. Explain the basic fit loop.
5. Distinguish filtered, smoothed, and Viterbi outputs.

---

# 2. Topic Type and Adapter

**Primary Adapter:**  
Statistical / ML Model

**Secondary Adapter:**  
Process / Algorithm

**Horizontal relationship type:**  
Hybrid — hierarchy + sequence + recursive process

---

# 3. L0 Bird's-Eye Map

```text
                     MODEL / HSMM

                        RETURNS
                           │
                           ▼
                    HIDDEN STATE
                           │
                           ▼
                      HMM → HSMM
                           │
                           ▼
              ┌──────────────────────┐
              │ THREE MODEL MACHINES │
              │ emission             │
              │ transition           │
              │ duration             │
              └──────────┬───────────┘
                         │
                         ▼
               DURATION ARCHITECTURES
                         │
                         ▼
                        FIT
                         │
                         ▼
                    FIXED MODEL
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           Filtered   Smoothed   Viterbi
```

## Whole-System Explanation

The model observes returns but does not directly observe the regime that produced them.  
A hidden state represents that regime.  
HSMM separates return generation, next-state transition, and state duration.  
Different candidate models mainly differ in how duration is represented.  
The model is first fitted.  
After fitting, the parameters are fixed and the model is read using filtered, smoothed, or Viterbi outputs.

---

# 4. Major Block Definitions

## P2.A — Hidden Regime
**Role in the whole:** Connect observed returns to an unobserved regime.  
**Input / Precondition:** Observed return series.  
**Output / Result:** Latent-state representation with state-specific return behavior.  
**Previous Block:** None inside this local map.  
**Next Block:** P2.B — HMM → HSMM.

## P2.B — HMM → HSMM
**Role in the whole:** Explain why explicit duration modelling is introduced.  
**Input / Precondition:** Hidden-state model concept.  
**Output / Result:** Clear distinction between self-transition persistence and explicit duration.  
**Previous Block:** P2.A.  
**Next Block:** P2.C — Three Model Machines.

## P2.C — Three Model Machines
**Role in the whole:** Separate emission, transition, and duration responsibilities.  
**Input / Precondition:** HSMM concept.  
**Output / Result:** Three-part mental model.  
**Previous Block:** P2.B.  
**Next Block:** P2.D — Duration Architectures.

## P2.D — Duration Architectures
**Role in the whole:** Show how candidate models differ in duration representation.  
**Input / Precondition:** Duration is understood as a separate model object.  
**Output / Result:** Map of Primary, Exact-Geometric, Unpenalised, and Negative-Binomial roles.  
**Previous Block:** P2.C.  
**Next Block:** P2.E — Fit.

## P2.E — Fit
**Role in the whole:** Learn model parameters from observed data.  
**Input / Precondition:** Chosen model architecture and initial parameters.  
**Output / Result:** Final fitted parameters and final posterior quantities.  
**Previous Block:** P2.D.  
**Next Block:** P2.F — Read.

## P2.F — Read
**Role in the whole:** Interpret a fitted model.  
**Input / Precondition:** Fixed fitted parameters.  
**Output / Result:** Filtered probabilities, smoothed probabilities, or one Viterbi path.  
**Previous Block:** P2.E.  
**Next Block:** Outside this pilot.

---

# 5. Recursive Zoom Maps

## P2.D — Duration Architectures

```text
                 DURATION ARCHITECTURES

          ┌────────────┬─────────────┬──────────────┐
          ▼            ▼             ▼              ▼
       Primary       Exact       Unpenalised         NB
       L2 pull      geometric      free PMF      parametric
```

**Stop condition:**  
Stop after the learner can explain the role and mechanism of each duration treatment.

---

## P2.E — Fit

```text
CURRENT PARAMETERS
       │
       ▼
    E-STEP
       │
       ▼
    M-STEP
       │
       ▼
    CONTROL
       │
   continue?
    ↙    ↘
  yes     no
   │       │
   └──↺    ▼
       FINAL E-STEP
           │
           ▼
      FIXED MODEL
```

**Stop condition:**  
Stop after the learner can mentally simulate one complete fit iteration and explain why the final E-step exists.

---

# 6. L1–L4 Depth Plan

## P2.B — HMM → HSMM

### L1 — Simple Explanation
- Understand that HMM and HSMM differ mainly in duration representation.
- Understand that duration and transition answer different questions.

### L2 — Mechanism
**Input:** Current state.  
**Operation:** HMM repeatedly applies self-transition decisions. HSMM uses explicit duration.  
**Output:** A dwell-time structure.  
**Next Step:** Separate emission, transition, and duration roles.

### L3 — Theory
**Core concepts:** self-transition, geometric duration, memorylessness, explicit duration.  
**Important distinction:** duration ≠ transition.  
**Likely misunderstanding:** zero transition diagonal means no persistence.

### L4 — Math / Formalism
**Required formal objects:** HMM geometric duration formula and HSMM duration PMF definition.

### R — Reference
- long derivations,
- rare notation variants.

---

## P2.D.1 — Primary Duration

### L1 — Simple Explanation
- Understand flexible duration with geometric shrinkage.
- Understand that the model is neither exact geometric nor fully free.

### L2 — Mechanism
**Input:** Posterior duration evidence, geometric reference, penalty strength.  
**Operation:** Balance evidence against reference.  
**Output:** Updated duration PMF.

### L3 — Theory
**Core concepts:** regularisation, nonparametric duration PMF, geometric reference, simplex constraint.  
**Important distinction:** regularised flexible duration ≠ Exact-Geometric model.

### L4 — Math / Formalism
**Required formal objects:** penalised duration objective.

### R — Reference
- detailed derivation,
- implementation-level root-solving detail.

---

## P2.E — Fit

### L1 — Simple Explanation
- Understand fit as an estimate-update-check loop.
- Distinguish final posterior computation from another M-step.

### L2 — Mechanism
**Input:** Observed returns and current parameters.  
**Operation:** E-step → M-step → control → repeat → final E-step.  
**Output:** Final parameters and posterior quantities.

### L3 — Theory
**Core concepts:** EM, posterior expectations, penalised objective, safeguard, stopping, budget.  
**Important distinction:** safeguard ≠ stopping ≠ budget.

### L4 — Math / Formalism
**Required formal objects:** penalised objective \(J\), representative posterior quantities.

### R — Reference
- exact convergence tolerances if not central,
- long implementation details.

---

## P2.F — Read

### L1 — Simple Explanation
- Understand that the fitted model can be read in different ways.
- Understand that information set changes meaning.

### L2 — Mechanism
**Input:** Fixed fitted model and observed data.  
**Operation:** filtering, smoothing, or joint path decoding.  
**Output:** filtered probabilities, smoothed probabilities, or Viterbi path.

### L3 — Theory
**Core concepts:** causal inference, retrospective inference, posterior probability, joint path decoding.  
**Important distinction:** filtered ≠ smoothed ≠ Viterbi.

### L4 — Math / Formalism
**Required formal objects:** filtered probability, smoothed probability, Viterbi argmax.

### R — Reference
- decoding implementation detail.

---

# 7. Concept Home Registry

| Concept ID | Canonical Name | Home | Used Also In | Local Role |
|---|---|---|---|---|
| C001 | Explicit Duration | P2.B | P2.C, P2.D | Separates dwell from transition |
| C002 | Regularisation | P2.D.1 | P2.E | Controls duration flexibility |
| C003 | EM | P2.E | P2.D.1 | Fit framework |
| C004 | Filtering | P2.F | Later causal evaluation | Causal state reading |
| C005 | Smoothing | P2.F | Retrospective analysis | Full-sample state reading |
| C006 | Viterbi | P2.F | Segment diagnostics | Joint path decoding |

---

# 8. Critical Confusion Boundaries

```text
duration ≠ transition
zero transition diagonal ≠ zero persistence
geometric duration is memoryless ≠ "HMM has no memory"
regularised flexible duration ≠ Exact-Geometric implementation
safeguard ≠ stopping ≠ budget
filtered ≠ smoothed ≠ Viterbi
```

---

# 9. Learning Flow vs Reference Boundary

## Keep in Learning Flow
- hidden state vs observed return,
- HMM vs HSMM duration logic,
- emission / transition / duration separation,
- fit loop,
- filtered / smoothed / Viterbi distinction,
- core formulas tied directly to mechanisms.

## Move to Reference
- exact empirical scores,
- long derivations,
- source trace IDs,
- exhaustive notation,
- detailed audit history.

---

# 10. Learning Routes

## Quick View
L0 + L1.

## Standard Study
L0 + L1 + L2.

## Deep Study
L0 through L4.

## Retrieval Route
Redraw the P2 map, HMM vs HSMM mechanism, Fit loop, and Read branch.

---

# 11. Architecture Audit

| Check | Status | Notes |
|---|---|---|
| Whole before parts | PASS | L0 appears first |
| Natural block structure | PASS | Blocks follow model logic |
| Recursive zoom | PASS | Duration and Fit are expanded |
| L1–L4 allocation | PASS | Mechanism precedes theory and math |
| Reference separation | PASS | Precision-heavy detail moved out |
| One Concept — One Home | PASS | Registry included |
| Confusion boundaries | PASS | High-risk distinctions explicit |
| Progressive disclosure | PASS | Local maps precede deep content |
| Cognitive simplicity | PASS | Pilot remains intentionally partial |

---

# 12. Proposed Frozen Architecture

```text
P2 — MODEL / HSMM
│
├── P2.A — Hidden Regime
├── P2.B — HMM → HSMM
├── P2.C — Three Model Machines
│   ├── Emission
│   ├── Transition
│   └── Duration
├── P2.D — Duration Architectures
│   ├── Primary L2
│   ├── Exact-Geometric
│   ├── Unpenalised
│   └── Negative-Binomial
├── P2.E — Fit
│   ├── E-step
│   ├── M-step
│   ├── Control
│   └── Final E-step
└── P2.F — Read
    ├── Filtered
    ├── Smoothed
    └── Viterbi
```

**Frozen Status:**  
EXAMPLE ONLY — NOT FROZEN FOR FULL PROJECT
