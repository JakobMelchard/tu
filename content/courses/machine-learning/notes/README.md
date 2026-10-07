# 184.702 Machine Learning — notes

TISS names **no literature** — "No lecture notes are available." [S1] — the
material is TUWEL-only, and **no lecturer hosts anything publicly** [S5–S9]. So
the scope of these notes comes from three places: the TISS subject line [S1],
the lecture unit order of a student summary written from the slides [S18], and
**19 past exam papers** with two student answer catalogues and the course's own
formula sheet and how-to sheet [S11–S15, S43]. Everything is registered in
[`../refs/SOURCES.md`](../refs/SOURCES.md) and cited inline as `[S<n>]`.
The unit-by-unit correspondence is in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Logistics, state 2026-09-27** (TISS re-read that day, no field changed [S1]):
lectures Tue 08:00-10:00 and Thu 16:00-18:00 in HS 17. Exams 26.01.2027 and
04.03.2027, times not published. Everything runs in TUWEL from 01.10.2026
[S1]: slides, recordings, forum and exercise submission. TUWEL content was not
read for these notes; any "TUWEL" statement below is unverified.


**Read [00 Exam focus](00-exam-focus.md) first.** For this course the exam
archive *is* the syllabus, and the format changed fundamentally in 2022: the
paper is now entirely multiple choice, with negative marking, in three sections.

## The notes

`weight` is how heavily the topic appears across the 19 papers: `●●●` in nearly
every paper, `●●` recurring, `●` once or twice.

| # | Note | unit [S18] | weight | Contents |
|---|---|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | — | — | format and marking, the five hand calculations, the true/false topics, the section-3 lists, how to prepare |
| 01 | [Learning setup and workflow](01-learning-setup.md) | 1 | ●● | the three paradigms, tasks, **the four measurement scales**, train/validation/test, leakage, the experiment loop |
| 02 | [Preprocessing](02-preprocessing.md) | 2 | ●●● | scaling (**z-score vs min–max**, the recurring question), 1-of-$n$ and label encoding, **binning**, missing values, outliers, **filter/wrapper/embedded** feature selection, imbalance, **augmentation** |
| 03 | [Evaluation](03-evaluation.md) | 3 | ●●● | confusion matrix, precision/recall/F1, micro vs macro, ROC/PR, **the WEKA error family RAE/RSE/RRSE and the correlation coefficient**, CV protocols, **the paired-$t$-test trap**, McNemar, bias–variance |
| 04 | [Model selection](04-model-selection.md) | — | ●● | hyperparameters, grid/random/Bayesian search, nested CV, overfitting and its remedies, learning curves, **the pre-pruning depth puzzle** |
| 05 | [k-nearest neighbours](05-knn.md) | 4 | ●●● | distance metrics, choice of $k$, lazy learning, curse of dimensionality, **the kNN true/false bank** |
| 06 | [Decision trees](06-decision-trees.md) | 5 | ●●● | **0R, 1R and the covering algorithm**, entropy/information gain/Gini in the lecture's notation, **the three split scores**, CART, pruning |
| 07 | [Ensembles](07-ensembles.md) | 12 | ●●● | homogeneous vs heterogeneous, bagging and OOB, random forests and **their two sources of randomness**, AdaBoost in the course's own form, gradient boosting **from a zero-rule model** |
| 08 | [Linear models](08-linear-models.md) | — | ●●● | OLS/RSS, **normal equations vs gradient descent**, **ridge vs lasso**, **polynomial regression**, logistic regression |
| 09 | [Naive Bayes and Bayesian networks](09-bayes.md) | 6, 7 | ●●● | **the course's Laplace convention**, zero frequency, missing values, d-separation, enumeration, **structure learning by local search**, **HMMs (historical)** |
| 10 | [Support vector machines](10-svm.md) | 8 | ●●● | margin, primal/dual, kernels, $C$ and $\gamma$, **SVM vs perceptron**, **kernels in a perceptron** |
| 11 | [Neural networks](11-neural-networks.md) | 9 | ●●● | perceptron, MLP, backpropagation, activations, optimisers, dropout and the other regularisers |
| 12 | [Unsupervised learning](12-unsupervised.md) | — | ● | $k$-means, hierarchical, DBSCAN, PCA, cluster evaluation — examined mostly as "PCA is not supervised" |
| 13 | **[Deep learning](13-deep-learning.md)** | 10 | ●●● | **convolution arithmetic and the output-size formula**, pooling, CNN architectures, RNNs, **vanishing gradients and their fixes**, **transfer learning and freezing**, augmentation |
| 14 | **[Reinforcement learning](14-reinforcement-learning.md)** | 11 | ●●● | **$k$-armed bandits and the "which step was random?" calculation**, $\varepsilon$-greedy / optimistic / UCB, MDPs and Bellman, **Monte-Carlo prediction and control** |
| 15 | **[AutoML and metalearning](15-automl-and-metalearning.md)** | 13 | ●●● | **no-free-lunch**, **Rice's framework**, **metalearning feature families and landmarking**, hyperparameter optimisation, Auto-WEKA and auto-sklearn |
| 16 | **[ML security, privacy and MLOps](16-ml-security-privacy-and-mlops.md)** | 14, 15 | ● | attack taxonomy, adversarial examples and FGSM, backdoors, XAI, $k$-anonymity vs differential privacy, inference attacks, the ML lifecycle |
| 17 | [Exercise playbook](17-exercise-playbook.md) | — | — | the real assignment structure [S15], **the lecturer's own feedback as a rubric** [S10], report and presentation checklist |

**Bold** entries are notes or sections added in the 2026-09-22 source pass; see
CHANGELOG.md.

## Each note

Follows `../../../docs/coursework-conventions.md`:
what the topic is, definitions and results with formulas, a worked numeric
example, pitfalls, exam-style questions with answers, and pointers into
[`../src`](../src/README.md). Every exam-style question says which past paper it
is modelled on (by the label from [00 Exam focus](00-exam-focus.md), e.g.
*(modelled on E21b)*) or is marked *(ours)*.

Every claim carries a `[S<n>]` citation, or is explicitly marked
*(unsourced: …)* where it could not be traced.

## Why the numbering is not the lecture order

The numbering is topic-grouped and predates this pass. The lecture order —
which comes from a *single secondary source* [S18] and is not independently
confirmed — is the `unit` column above, and the two differ only in that
ensembles (07) are taught after the neural-network units, and linear regression
(08) is folded into the regression/gradient-descent thread rather than being its
own unit. Renumbering for that would have broken every cross-reference for one
uncorroborated source. See
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

## Do not study the sibling course's exam

VoWi files the exams of **192.183 Machine Learning** (6.0 ECTS, Bellec/Musliu/
Marty, new curricula, first run 2026S) on the *same* wiki page as ours [S4, S16].
Its June 2026 paper asks for int8 ranges, FLOP counts, initialisation scales and
Transformer losses — none of which has ever appeared in a 184.702 paper.

## Notation

$n$ samples, $d$ features, $K$ classes; $x_i$ a row, $y_i$ its label,
$\hat y$ a prediction. $H$ entropy (base 2), $IG$ information gain, $I_G$ the
Gini index — the lecture's letters [S13]. $\alpha$ is the learning rate in
gradient descent and the classifier weight in AdaBoost, $\lambda$ the
regularisation strength, $\varepsilon$ the exploration rate in RL, $\gamma$ the
RBF width in an SVM and the discount factor in RL. Where the course's notation
differs from the standard one — AdaBoost's $\tfrac12\log$, the Laplace
convention in naive Bayes, WEKA's relative error measures — the note says so and
uses the course's.
