# ULA Learning Content — HSMM Pilot

## Scope Note

This pilot is **not** the complete learning content for the full HSMM research paper.

It contains selected examples from the **Model / HSMM** part of the project.

Its purpose is to demonstrate the expected writing style and L1–L4 progression for the ULA Content Builder.

```text
HSMM_PILOT ≠ Full Paper Study Guide

HSMM_PILOT = Partial Content Example
```

---

# Local Map

```text
P2 — MODEL / HSMM
│
├── P2.B — HMM → HSMM
├── P2.D — Duration Architectures
│   └── P2.D.1 — Primary L2 Duration
├── P2.E — Fit
└── P2.F — Read
```

---

# P2.B — HMM → HSMM

## L1 — Simple Explanation

HMM and HSMM both use hidden states.

The main difference is how they represent the time spent in a state.

In an HMM, persistence is created by repeated self-transitions.

In an HSMM, state duration is represented explicitly.

This separates two questions:

```text
duration = How long?

transition = Where next?
```

---

## L2 — Mechanism

### HMM

```text
STATE c
  ↓
stay?
  ├── yes → c
  ↓
stay?
  ├── yes → c
  ↓
leave
  ↓
NEXT STATE
```

Repeated self-transitions create the implied duration.

### HSMM

```text
ENTER STATE c
      ↓
REPRESENT DURATION
      ↓
remain in c for that visit
      ↓
duration ends
      ↓
choose NEXT STATE
```

Therefore:

```text
duration ≠ transition
```

---

## L3 — Theory

In an HMM, persistence is represented through the self-transition probability.

Repeated stay/leave decisions imply a geometric duration distribution.

The geometric duration is memoryless.

This does **not** mean that an HMM has no dependence or no persistence.

The safe statement is:

> The implied geometric duration is memoryless.

An HSMM represents persistence through an explicit duration distribution.

In this project, the HSMM transition diagonal is zero.

That does not remove persistence.

Persistence is represented by the duration PMF.

### Critical Distinction

```text
zero transition diagonal ≠ zero persistence
```

---

## L4 — Math / Formalism

### HMM Implied Duration

\[
P(D_c=s)=a_{cc}^{\,s-1}(1-a_{cc})
\]

**Purpose:**  
Represent the probability that state \(c\) lasts exactly \(s\) periods.

**Mechanism Mapping:**  
\(a_{cc}^{s-1}\) represents repeated stays.  
\(1-a_{cc}\) represents exit.

### HSMM Duration

\[
d_c(s)=P(D_c=s)
\]

**Purpose:**  
Represent duration directly as its own model object.

**Formula Class:**  
CORE

---

## Oral Version

HMM and HSMM differ mainly in how they represent duration. In an HMM, repeated self-transitions create an implied geometric dwell time. In an HSMM, duration is modelled explicitly. Duration answers "how long?" and transition answers "where next?"

---

# P2.D.1 — Primary L2 Duration

## L1 — Simple Explanation

The Primary model learns a flexible duration PMF.

The PMF is not completely free.

An L2 penalty pulls it toward a geometric reference.

The model balances flexibility against a simpler geometric structure.

---

## L2 — Mechanism

```text
POSTERIOR DURATION EVIDENCE
             │
             ▼
             ⇄
             ▲
             │
      GEOMETRIC REFERENCE
             │
             ▼
      penalty strength λ
             │
             ▼
      UPDATED DURATION PMF
```

The posterior duration evidence pushes the PMF toward durations supported by the data.

The geometric reference pulls the PMF toward a simpler shape.

The penalty strength controls the balance.

---

## L3 — Theory

This is a regularisation problem.

A flexible duration PMF can adapt strongly to the data.

That flexibility can be useful.

It can also create unstable shapes.

The L2 penalty limits unnecessary movement away from a geometric reference.

The Primary model is not the same as an Exact-Geometric model.

### Critical Distinction

```text
regularised flexible duration ≠ Exact-Geometric implementation
```

---

## L4 — Math / Formalism

\[
\max_{d_c}
\left[
\sum_s \eta_c(s)\log d_c(s)
-
\lambda_c
\sum_s
\left(d_c(s)-d_c^0(s)ight)^2
ight]
\]

**Purpose:**  
Balance fit to posterior duration evidence against distance from the geometric reference.

**Symbols:**

- \(d_c(s)\): duration PMF,
- \(\eta_c(s)\): posterior duration information,
- \(d_c^0(s)\): geometric reference PMF,
- \(\lambda_c\): penalty strength.

**Formula Class:**  
CORE

---

# P2.E — Fit

## L1 — Simple Explanation

The model parameters are not known in advance.

Fit is a repeated estimation loop.

The model estimates hidden information under the current parameters.

It then updates the parameters.

The new step is checked.

The process repeats.

A final E-step is run under the final parameters.

---

## L2 — Mechanism

```text
CURRENT PARAMETERS
       │
       ▼
     E-STEP
       │
       ▼
POSTERIOR INFORMATION
       │
       ▼
     M-STEP
       │
       ▼
NEW PARAMETERS
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
   FINAL POSTERIOR OUTPUT
```

### E-step

Parameters stay fixed.

Posterior state and duration information is computed.

### M-step

Posterior information is used to update parameters.

### Control

```text
SAFEGUARD
Is the candidate step acceptable?

STOPPING
Should the loop end?

BUDGET
Has the maximum iteration count been reached?
```

Therefore:

```text
safeguard ≠ stopping ≠ budget
```

### Final E-step

The final parameters are fixed.

Posterior quantities are recomputed under those parameters.

No new M-step follows.

---

## L3 — Theory

The fit uses the EM idea because hidden states and durations are not directly observed.

The E-step computes posterior information.

The M-step updates model parameters.

The penalised model uses a penalised objective.

Safeguard, stopping, and budget have different jobs.

Reaching the iteration budget does not prove convergence.

It also does not automatically prove that the fit is invalid.

The final E-step aligns reported posterior quantities with the returned final parameters.

---

## L4 — Math / Formalism

\[
J(artheta)
=
\ell(artheta)
-
\sum_c
\lambda_c
\lVert d_c-d_c^0Vert^2
\]

**Purpose:**  
Combine likelihood contribution with duration regularisation.

### Critical Boundary

```text
J ≠ raw log-likelihood
J ≠ predictive validation score
```

---

# P2.F — Read

## L1 — Simple Explanation

After fitting, the model parameters are fixed.

The same model can be read in different ways.

Filtered probabilities use information available up to the current time.

Smoothed probabilities use the full sample.

Viterbi returns one joint state path.

---

## L2 — Mechanism

```text
                 FIXED MODEL
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     FILTERED      SMOOTHED     VITERBI
        │            │            │
      y1:t          y1:T         y1:T
        │            │            │
        ▼            ▼            ▼
 causal state   retrospective   one joint
 probability     probability     path
```

---

## L3 — Theory

Filtered probabilities are causal.

Smoothed probabilities are retrospective.

Viterbi is a joint path-decoding problem.

Therefore:

```text
filtered ≠ smoothed ≠ Viterbi
```

A high smoothed probability does not make a state label ground truth.

---

## L4 — Math / Formalism

### Filtered

\[
P(S_t=c\mid y_{1:t})
\]

### Smoothed

\[
P(S_t=c\mid y_{1:T})
\]

### Viterbi

\[
\hat S_{1:T}
=
rg\max_{s_{1:T}}
P(S_{1:T}=s_{1:T}\mid y_{1:T})
\]

**Formula Class:**  
CORE

---

# Pilot Reference Boundary

The following details are intentionally excluded:

- exact validation scores,
- holdout scores,
- penalty grid results,
- sample counts,
- full formula inventory,
- source trace IDs,
- convergence sensitivity results,
- retrospective diagnostics,
- walk-forward results,
- paper-wide claims and non-claims.

These belong to the full research project, not this partial example.
