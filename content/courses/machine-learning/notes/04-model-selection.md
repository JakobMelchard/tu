# 04 Model selection

> Named in the TISS subject line [S1]; the course's own treatment of *automatic* model selection is [note 15](15-automl-and-metalearning.md). Exam weight ●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## What it is

Choosing the model family, its **hyperparameters** (set before fitting: $k$ in kNN, tree depth, $C$ and $\gamma$ of an SVM, learning rate, regularisation strength, number of hidden units) and the preprocessing, using only training data. Parameters are learned by the fit; hyperparameters are chosen by searching over validation performance.

## Overfitting, underfitting, capacity

Capacity (VC dimension, number of effective parameters, depth) controls where a model sits on the bias–variance curve (note 03). As capacity grows, training error decreases monotonically; validation error is U-shaped. Underfitting: both errors high (increase capacity, add features, reduce regularisation). Overfitting: training error ≪ validation error (more data, regularise, simplify, ensemble, early stopping).

Occam / MDL view: prefer the simplest hypothesis consistent with the data; structural risk minimisation bounds $R(h) \le \hat R(h) + \text{complexity term}(\mathcal H, n)$.

The long-answer form (E21b) is "**What is overfitting, when and why is it a
problem, and what measures against it exist for an algorithm discussed in the
lecture?**" The answer the course expects [S12]: the model learns noise and
irrelevant detail of the training data and therefore fails to generalise;
countermeasures named are regularisation (penalise complex models), dropout and
batch normalisation for neural nets (note 13), feature selection, pruning and
depth limits for trees (note 06), and more data. **Cross-validation is not a
countermeasure** — it only *measures* the problem (E23a) [S12].

## Regularisation

Add a penalty on parameter size or complexity to the training objective: $\min_w\ \hat R(w) + \lambda\,\Omega(w)$.

- $L_2$ (ridge, weight decay): $\Omega = \|w\|_2^2$; shrinks all coefficients, keeps them non-zero; closed form for least squares (note 08). Equivalent to a Gaussian prior on $w$ (MAP).
- $L_1$ (lasso): $\Omega = \|w\|_1$; produces exact zeros (feature selection); Laplace prior. Elastic net mixes both.
- Structural: max depth / min leaf size / pruning (trees), dropout, early stopping (neural nets), `min_samples_leaf`, margin softness $C$ (SVM: small $C$ = strong regularisation).
- $\lambda$ (or $C = 1/\lambda$, $\alpha$) is a hyperparameter chosen by CV, never by training loss (which always prefers $\lambda = 0$).

## Search strategies

- **Grid search**: Cartesian product of candidate values; exhaustive, exponential in the number of hyperparameters; use log-spaced grids ($C \in \{10^{-2}, \dots, 10^{3}\}$).
- **Random search** [S37]: sample configurations from distributions; with a fixed budget it explores more distinct values of each hyperparameter than a grid, which matters because usually only one or two hyperparameters are important. This is why "state-of-the-art AutoML systems usually use grid search" is marked **false** in the exams (E21b, E21c, E23c) [S12].
- **Successive halving / Hyperband**: allocate a small budget (few epochs, subsample) to many configurations, keep the best fraction, repeat.
- **Bayesian optimisation**: model the validation score as a function of hyperparameters (Gaussian process / TPE) and query where the expected improvement is largest.
- Coarse-to-fine: wide log grid, then a finer grid around the optimum.

## Nested cross-validation

Selecting hyperparameters by CV and then reporting that best CV score is optimistically biased: the score is a maximum over many noisy estimates. Correct protocol:

```
for each outer fold (k_out):
    inner CV (k_in) on the outer-train part → choose hyperparameters
    refit on outer-train with them, score on outer-test
report mean ± std over outer folds
```

The outer score estimates the performance of the *whole procedure* (search + fit). The chosen hyperparameters may differ across outer folds; that is expected. For the final model, run the inner search once on all data and refit. Cost: $k_{\text{out}} \cdot k_{\text{in}} \cdot |\text{grid}|$ fits.

## Learning and validation curves

- **Learning curve**: score vs number of training samples, train and validation. Both curves converging at a low score → high bias (more data will not help; increase capacity). Large persistent gap → high variance (more data helps; regularise). Estimate of whether collecting more data is worth it.
- **Validation curve**: train and validation score vs one hyperparameter (e.g. $k$, depth, $C$). Training score improves with capacity; the validation optimum is the choice. Reading it: left = underfit, right = overfit.

## Worked example

kNN on 300 samples, grid $k \in \{1, 3, 5, 9, 15\}$, 5-fold CV. Scores: 0.920, 0.930, 0.937, 0.940, 0.927 → pick $k = 9$ with "0.940". Nested CV (outer 5, inner 3) chooses $k = 5$ in every outer fold, not the $k = 9$ of the full-data search, and reports $0.937 \pm 0.027$. The small drop is the selection bias; with 50 grid points instead of 5 it would be larger. A learning curve for an unpruned tree on the same data: train 1.0 everywhere, validation 0.68 → 0.89 from 24 to 240 samples and still rising: variance-dominated, more data or pruning helps. (`model_selection.py` `__main__` produces these numbers.)

## Pitfalls

- Reporting the best grid-search CV score as the generalisation estimate.
- Tuning on the test set "just to check".
- Linear grids over parameters that act multiplicatively ($C$, $\gamma$, $\lambda$, learning rate).
- Grid search with 6 hyperparameters × 10 values = $10^6$ fits; use random search.
- Forgetting that preprocessing choices (scaling, feature selection, SMOTE) are hyperparameters too and belong inside the search.
- Early stopping on the test set is tuning on the test set.
- Refitting with the tuned hyperparameters on all data changes the effective regularisation slightly (more data → could use a bit less); acceptable and standard.

## Exam-style questions

1. **Why is the score of the best configuration found by grid search a biased estimate of its generalisation?** It is the maximum of many noisy CV estimates; the winner is partly the configuration whose noise happened to be favourable ("winner's curse"). Nested CV removes the bias by evaluating the selection procedure on data it never saw.
2. **Random vs grid search with a budget of 60 fits over 3 hyperparameters.** Grid: $\approx 4$ values per hyperparameter, each value tried 15 times. Random: 60 distinct values of every hyperparameter; if only one hyperparameter matters, random search resolves it 15× finer. Random search also allows stopping any time.
3. **Sketch train/validation learning curves for a high-variance and a high-bias model and say what to do in each case.** High variance: training curve near 1, validation far below, gap closing slowly with $n$ → more data, regularise, simplify, ensemble. High bias: both curves converge quickly to the same mediocre value → richer model, better features; more data will not help.
4. **What is the effect of $\lambda$ in $\min \hat R(w) + \lambda\|w\|^2$ as $\lambda \to 0$ and $\lambda \to \infty$? How is it chosen?** $\lambda \to 0$: unregularised fit, minimum training error, maximal variance. $\lambda \to \infty$: $w \to 0$, predicts the intercept, maximal bias. Chosen by CV on a log grid (validation curve), never by training loss.
5. **Name four regularisation mechanisms that are not $L_1/L_2$ penalties.** *(ours.)* Early stopping, dropout, tree pruning / depth limits / min leaf size, data augmentation, bagging/ensembling, small $C$ in an SVM, reducing $k$-NN capacity by increasing $k$.
6. **Describe at least three methods used for hyperparameter optimisation.** *(modelled on E20b, E21b, E21c — asked three times.)* Grid search (exhaustive over a Cartesian product; exponential in the number of hyperparameters), random search (sample from distributions; more distinct values per hyperparameter at the same budget [S37]), and Bayesian optimisation / SMBO (fit a surrogate to the observed scores and evaluate where expected improvement is largest). See note 15.
7. **"Which of these can a validation set be used for: early stopping, hyperparameter tuning, significance testing?"** *(E23a, a section-3 list — all-or-nothing marking.)* **All three** [S12]. The validation set is the data you are allowed to make decisions on; the test set is not.
8. **1000 observations; pre-pruning requires at least 200 observations to split a node and at least 300 observations per leaf. What is the maximum depth, not counting the root?** *(E21a, E21b, E21c, E22a — the single most-repeated question in the archive.)* **2.** Push the tree as unbalanced as possible: split the root into 300 (a leaf, stop) and 700; split the 700 into 300 (leaf) and 400 — depth 2. The 400-node cannot split again, because any split would leave a child below the 300-observation minimum leaf size. See note 06.

## Code

`src/py/model_selection.py`: `grid_search`, `random_search`, `nested_cv`, `learning_curve`, `validation_curve`, `param_grid`, `BaseEstimator` (clone/set_params for the from-scratch models). sklearn: `GridSearchCV`, `RandomizedSearchCV`, `learning_curve` used in `exercise_template.py` (`tune_best`, `inspect_best`). The automatic version of this note — Rice's framework, metalearning features, AutoML systems — is [note 15](15-automl-and-metalearning.md).
