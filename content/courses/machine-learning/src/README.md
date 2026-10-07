# 184.702 Machine Learning — reference implementations

Python only (the course's exercises use a toolkit of the student's choice —
scikit-learn, WEKA, R, MATLAB [S1, S15]; the from-scratch numpy versions here
exist to make the exam material concrete). Every module cross-references
[`../refs/SOURCES.md`](../refs/SOURCES.md) as `[S<n>]` and, where a function
exists because a past paper asks for it, names the paper by its label from
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

```sh
# from the course folder, repo venv (`uv sync` at the repo root)
uv run pytest src -q           # 183 tests, ~10 s
uv run python src/py/bandits.py           # any module runs a demo
uv run python src/py/exercise_template.py # quick demo into a temp dir
uv run python src/py/exercise_template.py --demo --quick --tune
uv run python src/exercises/2026-01-27/solution.py   # prints, then check()s
```

## py/

| Module | Implements | Note | Test cross-checks against |
|---|---|---|---|
| `metrics.py` | confusion matrix, precision/recall/F1 (binary/macro/micro), ROC + AUC (trapezoid and Mann–Whitney), PR curve + AP, log loss, MSE/MAE/R²; **RAE, RSE, RRSE, correlation coefficient, `regression_report`** — the WEKA family the course's formula sheet prints [S13, S22] | 03 | `sklearn.metrics` (exact); RSE $= 1 - R^2$; all three relative errors $= 1$ for the 0R baseline |
| `preprocessing.py` | standard/min-max/robust scalers, one-hot/ordinal encoders, simple + kNN imputation, z-score/IQR outliers, winsorising, variance/correlation/ANOVA-F/MI filters, over/undersampling, SMOTE, class weights | 02 | `sklearn.preprocessing`, `impute`, `feature_selection` (exact) |
| `model_selection.py` | stratified split, k-fold, CV score/predict, grid and random search, nested CV, learning/validation curves, paired and corrected t-tests, McNemar; `BaseEstimator` (clone/params) | 01, 03, 04, 15 | `sklearn.model_selection`, `scipy.stats` |
| `knn.py` | distance metrics (L1/L2/Lp/Chebyshev/cosine/Hamming/Mahalanobis), kNN classifier/regressor, k by CV | 05 | `sklearn.neighbors` (exact probabilities) |
| **`rules.py`** | **`ZeroR`** (the baseline every report must beat, and gradient boosting's $F_0$), **`OneR`** with its per-attribute error table [S29], **`Prism`** (the covering algorithm) [S22], `discretize_1r` | 06 | the algorithm's own invariants: 1R uses exactly one attribute, every PRISM rule is pure, 1R ≥ 0R |
| `tree.py` | CART with Gini/entropy/MSE, sample weights, weakest-link (ccp) pruning, feature importance, text dump | 06 | `sklearn.tree` (same root split, same pruned leaf count) |
| `ensemble.py` | bagging with OOB, random forest, permutation importance, AdaBoost (SAMME), gradient boosting (squared and log loss with Newton leaves) | 07 | `sklearn.ensemble` (accuracy within 0.08, first stump error exact) |
| `linear.py` | OLS (lstsq/normal equations/GD), ridge closed form, lasso coordinate descent, logistic regression (GD/Newton), softmax regression, polynomial features | 08 | `sklearn.linear_model` (coefficients to 1e-2) |
| `bayes.py` | Gaussian/multinomial/Bernoulli NB; **`CategoricalNB`** with the course's Laplace convention and a `likelihoods()` view [S14] | 09 | `sklearn.naive_bayes` (exact, incl. `CategoricalNB` on the textbook path), **[S14]'s worked numbers** |
| **`bayesnet.py`** | `BayesianNetwork` with joint, `enumeration_ask`, `d_separated` (moralised ancestral graph), `markov_blanket`, `fit_cpts`, `sample`, `alarm_network`; **`score_structure` / `neighbourhood` / `hill_climb_structure`** — the course's own structure search, maximise $\log P(D\mid M) - \alpha\,\#M$ over add/remove/reverse-arc moves [S14] | 09 | brute-force joint, the six textbook independences, CPT recovery from samples, and hill climbing landing within 1 % of the generating structure's score |
| `svm.py` | primal linear SVM (Pegasos SGD on hinge loss), dual SVM via SMO (Platt's second-choice heuristic) with linear/poly/RBF kernels | 10 | `sklearn.svm.SVC` (objective within 2 %, predictions ≥ 95 %) |
| `mlp.py` | perceptron; MLP with manual backprop, ReLU/tanh/sigmoid, softmax-CE or MSE, SGD+momentum / Adam, L2, dropout, early stopping; numerical gradient check | 11 | finite differences (1e-6), `sklearn.neural_network` |
| **`conv.py`** | **`output_size`** (the one formula the exam tests), `pad2d`, `conv2d` (cross-correlation, `flip=True` for true convolution), `max_pool2d` / `avg_pool2d`, `conv_params` / `dense_params`, `receptive_field`, `same_padding` | 13 | `scipy.signal.correlate2d` (exact); the E20c $7\times7$/$3\times3$/stride-2 question |
| **`bandits.py`** | [S21] ch. 2: **`bandit_random_action_analysis`** (the "which step was definitely random?" calculation) and `definitely_random_steps`, `sample_average_update` / `constant_step_update`, `greedy_set`, `epsilon_greedy`, `ucb_select`, `Bandit` / `run_bandit` | 14 | the closed forms of [S21] §2.4–2.5; $\varepsilon$-greedy beats pure greedy on the 10-armed testbed |
| **`rl.py`** | [S21] ch. 3, 5, 6: `GridWorld`, `first_visit_mc_prediction`, `mc_control_es` (exploring starts), `td0_prediction` | 14 | MC control recovers the optimal grid policy; MC and TD(0) agree on $v_\pi$ |
| `clustering.py` | k-means++ , elbow, agglomerative (single/complete/average/Ward via Lance–Williams), DBSCAN, silhouette, Davies–Bouldin, ARI, NMI, purity | 12 | `sklearn.cluster` (DBSCAN exact), `sklearn.metrics` (exact) |
| `pca.py` | PCA via SVD (and via covariance eigenproblem), explained variance, fraction-of-variance selection, whitening, reconstruction error | 12 | `sklearn.decomposition.PCA` (exact up to sign) |
| `exercise_template.py` | scikit-learn pipeline for the assignments: CSV → `ColumnTransformer` → CV comparison of 8 models → table, box plot, confusion matrix/residuals, learning curve, permutation importance, grid search; `--demo` generates data, no arguments runs a quick demo into a temporary directory | 17 | end-to-end run on synthetic data; the dummy baseline scores the majority-class share |

**Bold** modules and entries were added or extended in the 2026-09-22 source
pass; see `../notes/CHANGELOG.md`.

`test_note_pointers.py` holds the suite together: every backticked name in a
note's `## Code` section must resolve to a real function, class or attribute of
the module it points at, and every module above must name its note in the
docstring, run a demo under `__main__`, have a `test_<module>.py` and stay under
300 lines. All randomness is seeded (`rng=0` / `random_state=0` defaults).

Conventions: every model exposes `fit`/`predict` (and `predict_proba` where
meaningful); the from-scratch models inherit `model_selection.BaseEstimator`, so
`cross_val_score` and `grid_search` work on them and on sklearn estimators
alike — which is also what makes `ZeroR` and `OneR` usable as the two standard
*landmarkers* of note 15. Datasets are generated (`sklearn.datasets.make_*`,
`load_iris`) or written out inline; nothing is downloaded and there is no
network access at test time.

## What the tests check

Besides the sklearn cross-checks, the suite pins **the numbers the course's own
material prints**, which is the only way to tell a correct reading of a source
from a plausible one:

| reference | what is reproduced | where |
|---|---|---|
| [S14] "How to Predict a Class with Naive Bayes" | the sheet's printed $0.05555$ — **and the fact that it belongs to a different sample than the one the sheet states**; with the stated sample the likelihood is $0.01852$ and the prediction flips to B | `test_bayes.py` |
| [S14] "How to Construct a Bayesian Network", case B | the score $\log P(D\mid M) - \alpha\,\#M$ really does penalise a denser network, the neighbourhood really is one arc away and acyclic, and hill climbing from the empty network reaches within 1 % of the generating structure | `test_bayesnet.py` |
| [S14] Laplace convention | $(n_{cv}+1)/(n_c+1)$ with an unsmoothed prior, contrasted with the textbook add-$\alpha$ rule, which is then checked against `sklearn.naive_bayes.CategoricalNB` exactly | `test_bayes.py` |
| [S13] the WEKA error block | RSE $= 1 - R^2$; RAE/RSE/RRSE $= 1$ for the mean-predicting baseline and $0$ for a perfect model; scale invariance; Pearson $r$ against `np.corrcoef` | `test_metrics.py` |
| [S11] E20c | a $7\times7$ input with a $3\times3$ window at stride 2 gives a $3\times3$ output, for both convolution and max pooling | `test_conv.py`, `exercises/2020-09-09` |
| [S11] E25b, E26a | "the output is larger when padding increases / stride decreases", verified from $O=\lfloor(I-K+2P)/S\rfloor+1$ rather than recalled | `test_conv.py` |
| [S11] E20b | 1R picks the attribute with the fewest training errors and reaches 1.0 on the held-out rows — the transcript's own surprising finding, on a table of the same shape | `test_rules.py`, `exercises/2020-06-25` |
| [S12] AdaBoost | the graded answer "each point's weight before classification is $1/n$", and the $(0.5, 0.25, 0.25)$ weights after one stump on $-1, +1, -1$ | `exercises/2019-10-18`, `exercises/2020-06-25` |
| [S21] §2.4–2.5 | the incremental sample average equals the arithmetic mean; the constant-$\alpha$ update equals its closed-form exponentially weighted average and its weights sum to 1 | `test_bandits.py` |
| [S21] §5.3 | Monte-Carlo control with exploring starts recovers an optimal grid-world policy (every greedy action reduces the Manhattan distance) | `test_rl.py` |
| [S11] E22b | with all weights at zero the two gradient-descent conventions differ by exactly $2m$ — which changes the answer to the paper's question | `exercises/2022-06-30` |
| [S11] E26a | all four section-2 calculations, plus the section-3 lists as an explicit answer key | `exercises/2026-01-27` |
| [S12, S13] AdaBoost, E19b | SAMME's $\alpha = \ln 2$ is twice the course's $\tfrac12\ln 2$ and gives the same weights $(\tfrac14, \tfrac14, \tfrac12)$ after normalisation | `test_ensemble.py` |
| note 04 / note 15 [S37] | the grid scores $0.920 \ldots 0.927$, nested CV choosing $k = 5$ in every fold, and random search trying 13 distinct $k$ against the grid's 4 at 16 evaluations | `test_model_selection.py` |
| note 12 | iris covariance eigenvalues $4.23, 0.24, 0.08, 0.02$; 92.5 % / 97.8 % explained | `test_pca.py` |
| note 14 | the worked bandit table, arms labelled 1..4 as in the papers, $Q$ before every step | `test_bandits.py` |

One source number did **not** reproduce, and the test says so: **[S14]'s worked
naive-Bayes example**, see the row above.

## Worked past papers (`exercises/`)

There are no public exercise sheets for the current course — the assignments are
in TUWEL. What is public is the exam archive, and
[`exercises/`](exercises/README.md) holds our solutions to five papers with a
description of each **in our own words**; the papers are not reproduced. They
are run by `py/test_exercises.py`, so `pytest src` covers them. Each one's
docstring lists the questions it answers with the numbers, and its `check()`
asserts those numbers (with a library cross-check where one exists: SVC for
E19b's support vectors, `scipy.signal.correlate2d` for E20c's convolution).

| folder | paper | label | why |
|---|---|---|---|
| `2019-10-18` | 18.10.2019 | E19b | the long-answer era: kNN + naive Bayes by hand, AdaBoost, support vectors |
| `2020-06-25` | 25.06.2020 | E20b | 1R with precision/accuracy; LOOCV for 1-NN vs 3-NN |
| `2020-09-09` | 09.09.2020 | E20c | convolution and max pooling; naive Bayes with Laplace |
| `2022-06-30` | 30.06.2022 | E22b | the first all-MC paper: $k$-armed bandit, one gradient-descent step |
| `2026-01-27` | 27.01.2026 | E26a | **the closest model for 2026W**: all four calculations and the section-3 lists |

## Not implemented

Note 16 (ML security, privacy, explainability, MLOps) is conceptual and the exam
archive asks no calculation from it, so it has no module. Hidden Markov models
(note 09) are historical — asked in 2017 and in no paper since — and are
likewise left unimplemented. Transformers are out of scope for 184.702; they
belong to the sibling course 192.183 [S4, S16].
