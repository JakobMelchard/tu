# 01 Learning setup and workflow

> Lecture unit 1 [S18]. Exam weight ●● — the paradigm/task/data-type vocabulary is section-1 material. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

Machine learning fits a function from data instead of specifying it. The standard framing (Mitchell [S27]): a program learns from experience $E$ with respect to task $T$ and performance measure $P$ if its performance at $T$, measured by $P$, improves with $E$. The three ingredients recur in every exercise: the **task** (what is predicted), the **data** (what is observed), the **measure** (how success is scored, note 03).

**The three paradigms**, which the course opens with and examines [S18, S12]:
**supervised** learning (labelled data: classification, regression),
**unsupervised** learning (no labels: clustering, dimensionality reduction,
anomaly detection — note 12), and **reinforcement learning** (no labels either,
only a reward signal for actions taken in an environment — note 14). The
long-answer question "describe the goal and setting of classification; to which
tasks does it relate and from which does it differ?" (E21b, E21c, E22a) wants
exactly this trichotomy plus the classification/regression split inside
supervised learning [S12].

## Definitions

- **Instance / sample** $x_i \in \mathcal X$: one row; **feature / attribute** $x_{ij}$: one column.
- **The four measurement scales**, in the course's own order [S18] — the vocabulary a section-1 statement will use:

  | scale | what it adds | example | distances meaningful? |
  |---|---|---|---|
  | **nominal** (categorical) | unique names only | colour, city | no |
  | **ordinal** | an order | small < medium < large, school grades | **no** — the exam item "ordinal data does not allow distances to be computed between data points" is marked **true** [S12] |
  | **interval** | a scale with meaningful differences, arbitrary zero | temperature in °C, dates | differences yes, ratios no |
  | **ratio** | an absolute zero | length, count, income | yes |

  Nominal and ordinal are *qualitative*; interval and ratio are *quantitative*.
- **Target / label** $y_i$. Supervised learning has targets; unsupervised has none.
- **Supervised tasks**: classification ($y$ discrete — **binary** 1 of 2, **multi-class** 1 of $n$, **multi-label** $m$ of $n$) and regression ($y \in \mathbb R$, continuous). "Classification is a machine learning task where the target attribute is nominal" is a true/false item, answer **true** [S12]. Ranking and structured prediction are variants.
- **Unsupervised tasks**: clustering, dimensionality reduction, density estimation, anomaly detection (note 12). Semi-supervised learning sits in between; **reinforcement learning is a paradigm of its own and is examined in every recent paper** (note 14).
- **Hypothesis space** $\mathcal H$: the set of functions a model family can represent (all linear functions, all depth-$\le d$ trees, ...). The **inductive bias** is what makes a learner prefer some hypotheses over others; without a bias there is no generalisation — this is the no-free-lunch theorem [S31], which the course examines in its own right (note 15).
- **Empirical risk** $\hat R(h) = \frac1n \sum_i L(y_i, h(x_i))$ vs **true risk** $R(h) = \mathbb E_{(x,y)\sim p}\,L(y, h(x))$. Training minimises $\hat R$; we care about $R$. The gap is the **generalisation gap**; large gap = **overfitting**, large $\hat R$ = **underfitting**.
- **i.i.d. assumption**: train and future data drawn independently from the same distribution $p$. Violated by time drift, duplicated rows, grouped samples (several rows per patient).
- **Parametric vs non-parametric**: a fixed number of parameters (linear model) vs parameters growing with data (kNN, trees). **Eager vs lazy**: model built at training time vs at query time (kNN).
- **Generative vs discriminative**: model $p(x, y)$ (naive Bayes, note 09) vs $p(y \mid x)$ or the decision boundary directly (logistic regression, SVM).

## Data splits

| Split | Used for | Never used for |
|---|---|---|
| Training set | fitting parameters | reporting |
| Validation set (or CV folds) | choosing hyperparameters, model, features, early stopping | fitting the final parameters *of the reported model*... except in a final refit |
| Test set | one final estimate of $R$ | any decision |

Typical: 60/20/20 or 80/20 with $k$-fold cross-validation inside the 80 (note 03). Stratify classification splits so class proportions match. Group-aware splitting when rows are not independent (`GroupKFold`); chronological splitting for time series.

**Leakage** = information from outside the training fold entering the fit. This
is the single point the lecturer's own written exercise feedback hammers on —
"missing value deletion … taking care of imbalanced data … removing outliers was
done before splitting: this way you are modifying your *test* set before it was
created, and you implicitly simplify your task" [S10]. Sources: (1) fitting preprocessing (scaler, imputer, feature selection, PCA, target encoding) on all data before splitting; (2) features that are proxies for the target and unavailable at prediction time (e.g. "treatment given" when predicting a diagnosis); (3) duplicates or near-duplicates across splits; (4) tuning on the test set. Symptom: test score much better than what the model achieves on genuinely new data. Cure: put every fitted step into a pipeline and fit the pipeline inside the CV loop (`src/py/exercise_template.py` does exactly this with `Pipeline([("pre", ColumnTransformer), ("model", ...)])`).

## The workflow used in the exercises

1. Define task, target, performance measure and a baseline (majority class, mean, a simple rule).
2. Explore: shapes, types, missing values, class balance, obvious leaks, duplicates.
3. Split off the test set (stratified) and do not look at it again.
4. Preprocessing pipeline (note 02) fitted on train only.
5. Compare model families with CV (notes 03, 04); tune the promising ones.
6. Refit the chosen pipeline on the full training data; evaluate once on the test set; report with uncertainty (std over folds, confidence interval).
7. Inspect: confusion matrix, errors, feature importance; sanity-check against the baseline.

## Worked example

200 patients, features age, blood pressure, "days since admission", target "readmitted". Naively fitting a scaler and a random forest on all 200 rows and reporting 5-fold CV accuracy gives 0.93. Doing it right: the scaler is inside the pipeline (score barely changes, scaling leaks little), but "days since admission" is only known *after* the outcome — removing it drops accuracy to 0.71, which is the honest figure. The majority-class baseline is 0.65, so the model is useful but far less impressive than the leaked 0.93.

## Pitfalls

- Reporting training accuracy. 1-NN and unpruned trees score 100 % on training data (`model_selection.learning_curve` shows this).
- Fitting anything on the test set, including choosing which of two final models to report.
- Random splits of time-ordered or grouped data.
- Accuracy on imbalanced classes (note 02, 03): 99 % accuracy with 1 % positives is the trivial classifier.
- Confusing the sample size needed for a stable *estimate* (test set) with that for a good *model* (training set).

## Exam-style questions

1. **Define overfitting in terms of empirical and true risk. How do you detect it?** Overfitting: $\hat R(h)$ small while $R(h) - \hat R(h)$ large; the model fits noise. Detect by the gap between training score and validation/CV score, or a learning curve where the training curve stays high and the validation curve plateaus far below.
2. **Give three sources of data leakage and the general remedy.** Preprocessing fitted on all data before the split; target-proxy features unavailable at prediction time; duplicates across splits (also: tuning on the test set). Remedy: split first, put every fitted transformation in a pipeline and fit it inside each CV fold, audit features for availability at prediction time.
3. **Why do we need both a validation and a test set?** Hyperparameters and model choice are fitted to the validation data, so the validation score is optimistically biased (it is a maximum over many trials). The test set is touched once and gives an unbiased estimate of the chosen procedure.
4. **Classify: predicting house prices; grouping customers by purchase history; flagging fraudulent transactions with 0.1 % positives.** Regression (supervised); clustering (unsupervised); binary classification, heavily imbalanced, evaluate with precision/recall or PR-AUC rather than accuracy. *(ours.)*
5. **What is the inductive bias of a linear classifier and of 1-NN?** Linear: the classes are separated by a hyperplane (strong bias, low variance). 1-NN: the label is locally constant, nearby points share a label (weak bias, high variance). *(ours.)*
6. **Describe the goal and setting of classification. To which tasks does it relate, and from which does it differ?** *(modelled on E21b, E21c, E22a — asked three times.)* Supervised: both inputs and labels are given and the program learns the mapping, aiming at high accuracy on unseen inputs. It relates to **regression**, which is also supervised but predicts a continuous target instead of one of a fixed set of classes. It differs from **unsupervised** learning, where no labels exist and the algorithm groups by similarity, and from **reinforcement learning**, where only rewards and penalties for actions are available and the system learns to maximise reward.
7. **"Ordinal data does not allow distances to be computed between data points." True or false?** *(E21b, E22a.)* **True** as the course marks it: an ordinal scale fixes the order but not the spacing, so a numeric difference between "small" and "medium" is not meaningful — which is why ordinal encoding for kNN or a linear model invents distances that are not in the data (note 02).

## Code

- `src/py/model_selection.py`: `train_test_split(stratify=True)`, `stratified_kfold`, `learning_curve`.
- `src/py/exercise_template.py`: the leak-free pipeline skeleton (`make_preprocessor`, `compare_models`).
