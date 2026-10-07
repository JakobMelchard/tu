# Textbook map — what the course covers, and where we cover it

**This course publishes no lecture notes.** TISS says "No lecture notes are
available" [S1] and every course page since 2021 says the material is in TUWEL
[S6, S7]. So there is no lecturer's script to map against, as there would be for
a course with a public PDF. What follows instead is a map of the **two standard
texts** onto the course's published topic list and onto our notes and code.

Sources: **S9** = Shalev-Shwartz & Ben-David, *Understanding Machine Learning*
(2014, 449 pp.); **S10** = Mohri, Rostamizadeh & Talwalkar, *Foundations of
Machine Learning*, 2nd ed. (2018, 505 pp.). See [`SOURCES.md`](SOURCES.md).

## The course's topic list, and which text owns each topic

TISS gives six tentative topics [S1, S2]. This is the whole examinable scope for
the 3 ECTS course number — it has not changed since 2022W.

| # | TISS topic | best source | our notes |
|---|---|---|---|
| 1 | Empirical risk minimisation and regularisation | S9 ch. 2, 4, 7, 13 | [01](../notes/01-statistical-learning-framework.md), [02](../notes/02-finite-classes-and-concentration.md), [06](../notes/06-regularisation-and-srm.md) |
| 2 | Probably approximately correct (PAC) learning | S9 ch. 3, 5; S10 ch. 2 | [03](../notes/03-pac-learning.md) |
| 3 | VC dimension | S9 ch. 6, 28; S10 ch. 3 | [04](../notes/04-vc-dimension.md), [05](../notes/05-rademacher-complexity.md) |
| 4 | Kernel-based learning (SVM) | S10 ch. 5–6; S9 ch. 15–16 | [08](../notes/08-kernels-and-rkhs.md), [09](../notes/09-svm.md) |
| 5 | Least squares regression | S10 ch. 11; S9 ch. 9.2, 13.4; S12 ch. 3 | [07](../notes/07-least-squares-regression.md) |
| 6 | Deep learning | S11 (Telgarsky); S9 ch. 20 | [10](../notes/10-deep-learning-theory.md) |
| — | "understand, summarise and present ML research papers" (a stated learning outcome, not a topic) | — | [11](../notes/11-research-topics-and-paper-reading.md) |

**Note 05 (Rademacher complexity) is not on the TISS list by name.** It is kept
because every generalisation bound in topics 3–5 is derived through it in both
texts, and because the 6 ECTS twin's outcomes ask for "generalization bounds"
explicitly [S4]. Treat it as machinery, not as a separate examinable topic.

## S9 (Understanding Machine Learning) — chapter by chapter

`•` marks a chapter that is *not* on the course's topic list. Read the unmarked
ones.

| ch. | title | • | our note | our code |
|---|---|---|---|---|
| 1 | A gentle start | | [01](../notes/01-statistical-learning-framework.md) | `framework.ThresholdProblem` |
| 2 | A formal learning model (Cor. 2.3) | | 01, [02](../notes/02-finite-classes-and-concentration.md) | `framework.erm_finite`, `concentration.sample_complexity_finite` |
| 3 | Learning via uniform convergence | | [03](../notes/03-pac-learning.md) | `pac.*` |
| 4 | The bias–complexity trade-off (Lemma 4.2, Lemma 4.5, Cor. 4.6) | | 02 | `concentration.hoeffding_bound`, `union_bound_experiment` |
| 5 | The VC-dimension — No-Free-Lunch (Thm 5.1) | | 03 | `pac.estimate_failure_probability` |
| 6 | The VC-dimension (Lemma 6.10 Sauer, Thm 6.7/6.8, Thm 6.11) | | [04](../notes/04-vc-dimension.md) | `vc.*`, `test_textbook_vc_theory.py` |
| 7 | Nonuniform learnability: SRM, MDL (Thm 7.4, 7.5, 7.7) | | [06](../notes/06-regularisation-and-srm.md) | `srm.*` (proven bound), `regularisation.srm_select` (heuristic) |
| 8 | The runtime of learning | | 03 (conjunctions, rectangles) | `pac.*` |
| 9 | Linear predictors (9.1.3 VC of halfspaces, 9.2 least squares) | | 04, [07](../notes/07-least-squares-regression.md) | `vc.halfspace_labelings`, `svm.perceptron`, `least_squares.ols` |
| 10 | Boosting | • | — | — |
| 11 | Model selection and validation | | 06 | `regularisation.validation_select` |
| 12 | Convex learning problems | | 06 | `regularisation.tikhonov` |
| 13 | Regularization and stability (Thm 13.2, Cor. 13.6/13.8/13.9) | | 06 | `regularisation.stability_experiment`, `regularisation.rlm_logistic` |
| 14 | Stochastic gradient descent | | 09 (Pegasos), 10 | `deep_theory.MLP` |
| 15 | Support vector machines (Thm 15.8, Lemma 15.9) | | [09](../notes/09-svm.md) | `svm.SVM` |
| 16 | Kernel methods (Thm 16.1 representer, Lemma 16.2) | | [08](../notes/08-kernels-and-rkhs.md) | `kernels.*` |
| 17 | Multiclass, ranking, complex prediction | • | — | — |
| 18 | Decision trees | • | — | — |
| 19 | Nearest neighbor | • | — | — |
| 20 | Neural networks | | [10](../notes/10-deep-learning-theory.md) | `deep_theory.*` |
| 21 | Online learning | • *(was on the topic list in era I, 2020W–2021S only — see [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) §2)* | — | — |
| 22 | Clustering | • *(era I only)* | — | — |
| 23 | Dimensionality reduction | • | — | — |
| 24 | Generative models | • | — | — |
| 25 | Feature selection and generation | • | — | — |
| 26 | Rademacher complexities (Lemma 26.2, Thm 26.5, Lemmas 26.8–26.11) | | [05](../notes/05-rademacher-complexity.md) | `rademacher.*` |
| 27 | Covering numbers | | 05 (Dudley) | — |
| 28 | Proof of the fundamental theorem (Thm 28.3, lower bounds) | | 04 | — |
| 29 | Multiclass learnability | • | — | — |
| A–C | Technical lemmas, measure concentration, linear algebra | | 02, 04 | `concentration.*` |

## S10 (Foundations of Machine Learning) — the chapters worth reading

S10 is better than S9 on margin theory, kernels and regression, and it is the
one whose constants the notes quote for Rademacher and margin bounds.

| ch. | title | our note | why read it here |
|---|---|---|---|
| 2 | The PAC learning framework | 03 | cleaner rectangle and finite-class proofs than S9 |
| 3 | Rademacher complexity and VC-dimension (Thm 3.3, 3.7, 3.13, 3.17, Cor. 3.18–3.19, Thm 3.20/3.23) | 04, 05 | **the reference for every constant in notes 04–05**; also the lower bounds |
| 4 | Model selection | 06 | SRM from a different angle |
| 5 | Support vector machines (Lemma 5.3, Thm 5.4, Lemma 5.7, Thm 5.8–5.10, Cor. 5.11) | 09 | **the margin bound and leave-one-out bound as the notes state them** |
| 6 | Kernel methods (Thm 6.2, 6.8, 6.10, 6.11, 6.12, Cor. 6.13, Thm 6.24) | 08 | Mercer, RKHS, closure properties, representer theorem, Bochner |
| 7 | Boosting | — | not on the topic list |
| 11 | Regression (Thm 11.3, 11.11, Lemma 11.12, Thm 11.15) | 07 | pseudo-dimension, kernel ridge, the push-through identity |
| D | Concentration inequalities (Thm D.8 McDiarmid, Lemma D.1) | 02, 05 | the appendix the notes lean on |

## Reading order for the oral exam

The two texts disagree on order. This is the sequence that makes the proofs
build on each other, and it is the order notes 01–12 are written in:

1. **S9 ch. 2–4** — ERM, uniform convergence, finite classes. Gets you Hoeffding,
   the union bound and both sample complexities. (Notes 01–02.)
2. **S9 ch. 3, 5** — PAC, agnostic PAC, No-Free-Lunch. (Note 03.)
3. **S9 ch. 6** + **S10 ch. 3** — VC dimension, Sauer–Shelah, the fundamental
   theorem. The single densest and most examinable block. (Note 04.)
4. **S9 ch. 26** + **S10 ch. 3.1** — Rademacher complexity. (Note 05.)
5. **S9 ch. 7, 11, 13** — SRM, MDL, stability. (Note 06.)
6. **S10 ch. 11** + **S9 ch. 9.2** — least squares and ridge. (Note 07.)
7. **S10 ch. 6** + **S9 ch. 16** — kernels and RKHS. (Note 08.)
8. **S10 ch. 5** + **S9 ch. 15** — SVM and margin bounds. (Note 09.)
9. **S11** (Telgarsky) — deep learning theory. (Note 10.)

## Where our code reproduces a textbook number

These are the checks in `src/py/test_textbook_vc_theory.py` (notes 02-04),
`test_textbook_algorithm_bounds.py` (notes 05-09) and `test_textbook_deep_theory.py`
(note 10); each test docstring names its source and locator. See [`../src/README.md`](../src/README.md).

| result | locator | what is checked numerically |
|---|---|---|
| Sauer–Shelah | S9 Lemma 6.10 | $\tau_{\mathcal H}(n)\le\sum_{i\le d}\binom ni$ by brute-force enumeration, and tightness for intervals |
| Polynomial form of Sauer | S10 Cor. 3.18 | $\sum_{i\le d}\binom ni\le(en/d)^d$ for $n\ge d$ |
| Finite-class sample complexity | S9 Cor. 4.6, Cor. 2.3 | the two closed forms, and that the realisable/agnostic ratio behaves as $\varepsilon^{-1}$ vs $\varepsilon^{-2}$ |
| Hoeffding | S9 Lemma 4.5 | the bound dominates the exact binomial tail |
| No-Free-Lunch | S9 Thm 5.1 | the reverse-Markov step $P(Z\ge 1/8)\ge 1/7$ from $\mathbb EZ\ge1/4$ |
| Massart | S10 Thm 3.7 | the bound against exactly computed $\mathfrak R_S$ for small classes |
| Linear Rademacher | S10 Thm 5.10 | $\mathfrak R_S\le r\Lambda/\sqrt m$, against the exact $\frac Bn\mathbb E\|\sum\sigma_ix_i\|$ |
| Fundamental theorem | S9 Thm 6.8 | the realisable/agnostic asymmetry is respected by our formulas |
| VC generalisation bound | S10 Cor. 3.19 | the worked numbers of note 04 |
| RLM stability | S9 Cor. 13.6, Cor. 13.9 | the $2\rho^2/(\lambda n)$ rate and the optimised $\sqrt{8\rho^2B^2/n}$ |
| Ridge bias bound | note 07 Thm 7.9(c) | $\|(I-H_\lambda)Xw^*\|^2\le\tfrac\lambda4\|w^*\|^2$, and that $\lambda/4$ is attained |
| SVM worked example | note 09 | $w^*=(\tfrac12,\tfrac12)$, $b=0$, $\alpha_1=\alpha_3=\tfrac14$, strong duality |
| Ridgeless asymptotics | S36 Thm 1 | both branches of $R(\gamma)$, and that the global minimum is underparameterised |
