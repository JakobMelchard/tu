# Notes: 138.129 Machine Learning and Data Compression in Physics

PR (project), 10 ECTS = 250 h, **mandatory in QIST 066 558, 3rd semester**, offered
every semester. **Graded on the protocol only**; no dates; **no TISS registration**:
contact the lecturers (Tomczak, Wallerberger, E138) to arrange a topic [S1, S2].
The 2027W page is not published; facts are from 2026W. TISS recommends
138.128 Machine Learning in Physics first, notes in
[`../../../ss2027/machine-learning-in-physics/`](../../machine-learning-in-physics/index.md) [S4].

**Start with [00](00-project-focus.md), then [01](01-project-playbook.md).**
Notes 02-07 are the technical background the likely projects need (compression
of data and Green's functions, learned compression, tensor trains, inverse
problems, prediction of observables); 08 is how to write the graded protocol.

| # | note | one line |
|---|---|---|
| **00** | [**Project focus**](00-project-focus.md) | What is graded (protocol only), course facts, the lecturers as of 2026-09-28, 250 h budget, timeline from the end of 138.128 (June 2027) to a topic agreement in September 2027, checklist for the 2027W page |
| **01** | [**Project playbook**](01-project-playbook.md) | Topic criteria, six candidate topics mapped to the lecturers' research, first-contact e-mail draft, milestones, experiment loop, results log, reproducibility checklist |
| 02 | [Low-rank compression](02-low-rank-compression.md) | SVD truncation, Eckart-Young (proved), PCA, randomised SVD with the HMT bound, error vs rank: analytic kernels, noise edge, denoising optimum |
| 03 | [Intermediate representation](03-intermediate-representation.md) | Logistic kernel from Lehmann, SVE, why $L\sim\log\Lambda$, parity, discretised SVE, sparse sampling in $\tau$ and $i\nu$, single-pole cross-check |
| 04 | [Autoencoders and learned compression](04-autoencoders-and-learned-compression.md) | Rate-distortion, quantisation, linear AE = PCA (proved), VAE and the KL as rate, where AEs beat PCA (single poles) and where not (Ising) |
| 05 | [Tensor-network compression](05-tensor-network-compression.md) | MPS/TT, TT-SVD error identity (proved), area law vs random states, quantics tensor trains of functions, TFIM worked example |
| 06 | [Analytic continuation as an inverse problem](06-analytic-continuation-as-inverse-problem.md) | Ill-posedness, Tikhonov filter factors, discrepancy principle, MaxEnt and its convex dual, learned linear inverse, uncertainty is mostly bias |
| 07 | [Pattern recognition and observables](07-pattern-recognition-and-observables.md) | $Z_2$ symmetry forbids linear predictors, bond features, kernel norm as sample cost, phase classification and the $T_c$ crossing |
| 08 | [Writing the protocol](08-writing-the-protocol.md) | Structure, error bars (binning, bootstrap), figures, code and data availability |
| | [`protocol_template.md`](protocol_template.md) | Skeleton to copy into the project repository |
| | `CHANGELOG.md` | What was written when, and what is unverified |

Each topic note has definitions, derivations, a worked example whose numbers
come from running the code, pitfalls, five questions with answers, and pointers
into [`../src/py`](../src/README.md).

**Sources.** `[S<n>]` refers to [`../refs/SOURCES.md`](../refs/SOURCES.md) (36
entries: TISS records, lecturer pages, the IR / sparse-ir / quantics papers,
ML and tensor-network references). [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md)
maps the 138.128 exercise notebooks and the key papers onto these notes. TUWEL was
not used.
