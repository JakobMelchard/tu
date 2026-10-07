# Notes: 194.100 Theoretical Foundations and Research Topics in ML

Ordered by the course's tentative topic list (ERM and regularisation, PAC learning, VC dimension, kernels and SVM, least squares, deep learning). Notes 01–10 each carry definitions, theorems with proofs, a worked example, pitfalls, oral-exam questions with answers, and pointers into [`../src/py`](../src/README.md).

**Start with [00](00-exam-focus.md).** TISS names no literature, so every claim here is cited as `[S<n>]` against [`../refs/SOURCES.md`](../refs/SOURCES.md), chiefly S9 (Shalev-Shwartz & Ben-David, *UML*) and S10 (Mohri et al., *FoML*), with the primary paper for each named result. Theorem locators were read out of the retrieved PDFs on 2026-09-22; what changed is in `CHANGELOG.md`. [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) maps textbook chapters onto these notes.

| # | Note | One line |
|---|---|---|
| **00** | [**Exam focus**](00-exam-focus.md) | **Read first.** Coursework + practical project + **final oral exam**, two independent 50 % hurdles; *not* a presentation-graded seminar. Dates in §4. The three assessment eras since 2020W, the 6 ECTS twin 194.201, and why no past exam questions exist anywhere public. |
| 01 | [Statistical learning framework](01-statistical-learning-framework.md) | Distribution, hypothesis class, loss, true vs empirical risk, Bayes optimality (proved), ERM, approximation/estimation split, optimism of training error, overfitting. |
| 02 | [Finite classes and concentration](02-finite-classes-and-concentration.md) | Markov, Chebyshev, Hoeffding's lemma and inequality (proved), union bound, uniform convergence, $\log(2\lvert\mathcal H\rvert/\delta)/(2\varepsilon^2)$ vs $\log(\lvert\mathcal H\rvert/\delta)/\varepsilon$, McDiarmid statement. |
| 03 | [PAC learning](03-pac-learning.md) | PAC and agnostic PAC definitions, sample complexity, conjunctions and rectangles as PAC learners, No-Free-Lunch theorem with proof, why inductive bias is unavoidable. |
| 04 | [VC dimension](04-vc-dimension.md) | Shattering, VC dimension of thresholds/intervals/rectangles/halfspaces (proved, Radon), growth function, Sauer–Shelah (full proof), double-sample argument, fundamental theorem of statistical learning, VC bound. |
| 05 | [Rademacher complexity](05-rademacher-complexity.md) | Definition, symmetrisation (proved), McDiarmid-based generalisation bound, contraction, Massart, linear classes $BR/\sqrt n$, relation to VC, covering numbers and Dudley. |
| 06 | [Regularisation and SRM](06-regularisation-and-srm.md) | Bias–complexity trade-off, SRM and Occam/MDL bounds (proved), Tikhonov/RLM, stability implies generalisation and RLM is $2\rho^2/(\lambda n)$-stable (proved), validation and cross-validation. |
| 07 | [Least squares regression](07-least-squares-regression.md) | Normal equations, hat matrix geometry, Gauss–Markov, ridge via SVD, bias–variance decomposition (derived), kernel ridge via push-through identity, regression generalisation bounds. |
| 08 | [Kernels and RKHS](08-kernels-and-rkhs.md) | PSD kernels ⇔ feature maps, RKHS construction and reproducing property, Mercer, closure properties (Schur), common kernels, kernel trick, representer theorem (proved). |
| 09 | [SVM](09-svm.md) | Margins, hard/soft-margin primal, Lagrangian duals derived, KKT and support vectors, kernel SVM, leave-one-out and margin bounds (proved), perceptron bound, SMO. |
| 10 | [Deep learning theory](10-deep-learning-theory.md) | Universal approximation (idea + constructive ReLU proof), depth separation, VC of nets, optimisation landscape, NTK, implicit regularisation (proved for least squares), norm/PAC-Bayes bounds, double descent, what is proven vs open. |
| 11 | [Research topics and paper reading](11-research-topics-and-paper-reading.md) | How to read, summarise and present a theory paper; claim-evaluation checklist; filled-in summary of Belkin et al. 2019; classic papers per topic; open directions. |
| 12 | [Oral exam question bank](12-oral-exam-question-bank.md) | 40 questions with model answers across all topics; the twelve proofs to rehearse. |

Suggested order for the oral exam: 00 first, then 01 → 02 → 03 → 04 → 05 → 06 (the theory core), then 07 → 08 → 09 (kernel methods), then 10, and use 12 to test yourself; 11 is for the paper summary and the project.

Also here: `CHANGELOG.md`, the record of what the 2026-09-22 source-verification pass changed (and, just as usefully, which constants were checked and found correct), and of the 2026-09-27 status and code pass.


**Format.** One timetabled slot, the Wed 10:00-12:00 exercise session [S1]. Nothing TUWEL-side (units, forum, coursework and oral dates) was accessed; see [00](00-exam-focus.md) §4.

**Code.** Each note's *Code* section names functions in [`../src/py`](../src/README.md) that exist (checked 2026-09-27); every module demo reproduces one of the note's bounds numerically over many resamples. `srm.py` (note 06) is new: SRM with a proven, exactly checkable bound.
