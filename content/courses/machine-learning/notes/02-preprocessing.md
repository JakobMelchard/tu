# 02 Preprocessing and data preparation

> Lecture unit 2 [S18]. Exam weight ●●● — encoding, scaling and feature selection are asked in almost every paper, and the exercise reports are marked on it [S10, S15]. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

Turning raw columns into a numeric matrix a learner can use, without leaking test information. Every step below is a *fitted transformation*: statistics are computed on the training fold and applied to the validation/test fold.

## Scaling

Needed by distance- and gradient-based methods (kNN, SVM, logistic regression with regularisation, neural nets, PCA, k-means); irrelevant for trees and forests (splits are order-based).

| Method | Formula | Use |
|---|---|---|
| Standardisation | $z = (x - \mu)/\sigma$ | default; keeps outliers as large $|z|$ |
| Min–max | $x' = (x - x_{\min})/(x_{\max} - x_{\min})$ | bounded inputs (images, sigmoid nets); sensitive to outliers |
| Robust | $(x - \text{median})/\text{IQR}$ | heavy tails |
| Log / Box–Cox | $\log(1+x)$ | right-skewed positive quantities (counts, incomes) |
| Unit norm (per row) | $x / \|x\|_2$ | text vectors, cosine similarity |
| **Binning / discretisation** | map value ranges to discrete buckets | turns a numeric attribute into a nominal one; the lecture lists it as a preprocessing step in its own right [S18] |

The course's min–max formula, verbatim from the formula sheet [S13]:
$z_i = \frac{x_i - \min(X)}{\max(X) - \min(X)}$, "multiply by the new range if
different from $0..1$".

**The recurring exam question is "z-score vs min–max: what are they, when do you
use which, on which feature types?"** (E17b, E18a, E22a — asked three times).
The answer the course expects [S12, S43]: both are for **numerical** features
whose ranges differ, so that no feature dominates a distance computation and
hence the prediction. Min–max maps to a fixed range, usually $[0,1]$, and is
recommended when the data are skewed or bounded (and for neural-network inputs,
to avoid saturating an activation); it is sensitive to outliers, since one
extreme value compresses everything else. The z-score centres and scales,
assumes roughly Gaussian data, preserves the shape of the distribution and is
more robust to outliers. For **categorical** features neither applies —
*encode* them instead.

## Encoding categorical features

The lecture calls one-hot encoding **1-of-$n$ encoding** and ordinal encoding
**label / distance encoding** [S18]. Two exam items follow directly:
"1-hot encoding is used to transform numerical into categorical attributes" —
**false**, it is the other way round (E21d); and "when kNN is used with 1-of-$n$
encoding, min–max scaling is needed to perform the Euclidean distance" —
**false** *on its own*, because a one-hot column is already in $[0,1]$; it
becomes true only if other attributes have different ranges [S12, S43] (E18a).

- **One-hot** (dummy): $k$ categories → $k$ indicator columns (or $k-1$ to avoid collinearity in unregularised linear models). Safe default; blows up for high-cardinality columns.
- **Ordinal / label encoding**: integer codes. Only for ordered categories (small < medium < large); otherwise it invents distances. Trees tolerate it, linear models and kNN do not.
- **Target encoding**: replace category by mean target in training data, with smoothing $\tilde\mu_c = \frac{n_c \bar y_c + m \bar y}{n_c + m}$. Powerful and a classic leak: must be computed out-of-fold.
- **Binary / hashing** for very high cardinality; embeddings in neural nets.
- Unseen categories at test time: map to all-zero (`handle_unknown="ignore"`) or an "other" bucket.

## Missing values

First ask *why* they are missing: MCAR (completely at random), MAR (depends on observed values), MNAR (depends on the missing value itself, e.g. high incomes not reported). Only MCAR is harmless to drop.

- Drop rows (if few and MCAR) or columns (if mostly missing).
- Simple imputation: mean/median (numeric), most frequent (categorical), constant + **missing indicator column** (lets the model use missingness, which is often informative).
- kNN imputation: average of the $k$ nearest rows on the shared coordinates, distance rescaled by $\sqrt{d / d_{\text{shared}}}$ (`preprocessing.knn_impute`).
- Model-based / iterative (MICE): regress each column on the others, iterate.
- Trees with native missing handling (surrogate splits, or "missing goes left/right" learned as in HistGradientBoosting).

## Outliers

- Detect: $|z| > 3$; Tukey fences $[Q_1 - 1.5\,\text{IQR},\, Q_3 + 1.5\,\text{IQR}]$; isolation forest / LOF for multivariate.
- Treat: verify (measurement error vs real), remove, winsorise (clip to percentiles), or use robust models/losses (Huber, MAE, trees). Never remove outliers from the *test* set to improve a score.

## Feature selection and construction

- **Filter** methods score features independently of the model: variance threshold, correlation with target, ANOVA $F = \frac{\text{between-class var}}{\text{within-class var}}$, $\chi^2$ for counts, mutual information $I(X;Y) = \sum p(x,y)\log\frac{p(x,y)}{p(x)p(y)}$. Cheap; ignore interactions. Drop one of two features with $|\rho| > 0.95$ for linear models (collinearity inflates coefficient variance).
- **Wrapper** methods search subsets with the model in the loop: forward selection, backward elimination, recursive feature elimination (RFE). Expensive; must be nested inside CV.
- **Embedded** methods select while fitting: lasso ($L_1$ zeroes coefficients, note 08), tree importance / information gain (note 07), ridge.
- Construction: polynomial/interaction terms, ratios, dates → (weekday, month), text → bag of words / TF-IDF $w_{td} = \text{tf}_{td}\log\frac{N}{\text{df}_t}$, PCA (note 12).

Three true/false items live here [S12]:

- "**Information gain** is an unsupervised feature-selection method" — **false**,
  it uses the target, so it is supervised (E22a, E19b).
- "**PCA** is a supervised feature-selection method" — **false**: PCA is
  unsupervised, and strictly it is *feature extraction* rather than selection,
  because it builds new combined features instead of keeping a subset. [S43]
  makes exactly that distinction: "PCA combines similar (correlated) attributes
  and creates new ones; feature selection doesn't combine attributes"
  (E17b, E22a).
- "Feature selection is primarily useful to improve the **effectiveness** of
  machine learning" — **false**: the primary gain is **efficiency** (fewer
  dimensions, less computation, less redundancy and noise); better predictions
  are a possible by-product, not the main purpose [S12] (E22a).

**Data augmentation** (note 13) belongs to preprocessing too: extending the
training set with label-preserving transformations. Asked as "What is data
augmentation?" in E24a [S12].

## Imbalanced data

With a $99{:}1$ class ratio the majority classifier has 99 % accuracy. Options:

- Metric first: precision, recall, $F_1$, balanced accuracy, PR-AUC, MCC (note 03).
- **Class weights**: weight class $c$ by $\frac{n}{K n_c}$ in the loss ("balanced"); the cleanest fix.
- **Resampling** (training fold only): random undersampling of the majority (loses data), random oversampling (duplicates → overfitting), **SMOTE** [S41]: synthetic minority points $x_{\text{new}} = x_i + \lambda (x_{nn} - x_i)$, $\lambda \sim U(0,1)$, between a minority point and one of its $k$ minority neighbours.
- Threshold moving: predict positive when $p > t$ with $t$ chosen on validation data for the desired precision/recall; equivalent to changing the cost matrix.
- Anomaly-detection framing when positives are extremely rare.

## Worked example

Column `income` with 5 % NaN, skewed, one value of $10^9$; column `city` with 300 levels; target `default` with 4 % positives. Pipeline (train fold only): `income` → median imputation + missing indicator → $\log(1+x)$ → standardise; `city` → target encoding computed out-of-fold with smoothing $m = 20$; classifier with `class_weight="balanced"`; evaluate PR-AUC; choose threshold for recall $\ge 0.8$ on validation. The $10^9$ value is checked against the source: a data-entry error, replaced by NaN before imputation.

## Pitfalls

- `scaler.fit(X)` before `train_test_split`. Small leak for scaling, large leak for target encoding, feature selection with the target, SMOTE.
- SMOTE applied to the test set, or before CV (synthetic points of a test sample end up in training).
- One-hot without `handle_unknown` → crash on a new category in production.
- Ordinal-encoding nominal categories for kNN/SVM/linear models.
- Dropping rows with NaN when missingness is MNAR: biases the sample.
- Standardising *binary* one-hot columns is harmless but pointless; standardising *before* PCA is essential (otherwise the largest-variance feature dominates).

## Exam-style questions

1. **Which models need feature scaling and why? Name two that do not.** kNN, SVM, k-means, PCA, neural nets and regularised linear models: distances, kernels, penalties and gradient steps depend on the units. Decision trees and random forests do not: splits only use the ordering within a feature.
2. **Explain SMOTE and one danger of it.** For a minority sample $x_i$ pick one of its $k$ minority nearest neighbours $x_{nn}$ and create $x_i + \lambda(x_{nn} - x_i)$, $\lambda \in [0,1]$. Danger: applied before the split it leaks test information; it interpolates through majority regions when classes overlap; it does not add new information, only reshapes the loss.
3. **Why is target encoding prone to leakage and how is it done correctly?** The encoding of a row contains that row's own label; the model can read the label back. Compute the encoding out-of-fold (each fold encoded with statistics from the other folds), add smoothing towards the global mean for rare categories.
4. **Contrast filter, wrapper and embedded feature selection.** Filter: model-free scores per feature (correlation, MI, ANOVA F), fast, ignores interactions. Wrapper: search over subsets evaluated by the model's CV score (forward/backward, RFE), expensive, must be nested. Embedded: selection is a by-product of fitting (lasso, tree splits).
5. **Which data preparation / preprocessing steps were mentioned in the lecture? Describe them.** *(modelled on E21d.)* Encoding (label encoding turns a category into an integer; 1-of-$n$ encoding gives each value its own 0/1 feature); missing-value removal or imputation; standardisation (z-score) or min–max scaling; binning; definition of a custom distance function where the default does not fit the feature types; feature selection; and the train/validate/test split done **without leakage from the test set** [S12].
6. **"PCA is a supervised feature-selection method." True or false, and what is it instead?** *(E17b, E22a.)* **False** on both counts: PCA never looks at the target, and it *extracts* new features (linear combinations of the originals ordered by explained variance) rather than *selecting* a subset. Feature selection keeps original attributes and so stays interpretable; PCA components are usually not.
7. **A column is missing for 30 % of rows, and missingness correlates with the target. What do you do?** Do not drop rows. Impute (median/most frequent) *and* add a missing-indicator column so the model can exploit the informative missingness; document the MNAR suspicion.

## Code

`src/py/preprocessing.py`: `StandardScaler`, `MinMaxScaler`, `RobustScaler`, `OneHotEncoder`, `OrdinalEncoder`, `SimpleImputer`, `knn_impute`, `zscore_outliers`, `iqr_outliers`, `winsorize`, `variance_threshold`, `correlation_filter`, `anova_f`, `mutual_information_discrete`, `random_oversample`, `random_undersample`, `smote`, `class_weights`. sklearn equivalents used in `exercise_template.make_preprocessor`.
