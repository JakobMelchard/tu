# 17 Exercise playbook

> Not a lecture unit: the assignment half of the course, 46.5 h of the ECTS budget [S1]. Built from the public 2021S assignment sheet [S15] and the lecturer's own written feedback [S10]. **Verify against TUWEL in week 1** (TUWEL was not read for this note).

## State 2026-09-27

- Course registration closes 02.10.2026 12:00, deregistration 05.10.2026
  18:00 [S1].
- Everything runs in TUWEL from 01.10.2026, the forum included [S1]; the
  assignment material and exercise submission live there too.
- The 2 presentation classes (8 h in the ECTS breakdown [S1]) have no dates in
  TISS.


## What the exercises actually are

TISS gives the outline: "Solving of exercises regarding experiments in machine
learning, using a software toolkit of the student's choice (e.g. Python
scikit-learn, Matlab, R, WEKA, ...)", 46.5 h of the 112.5 h budget, plus 2
classes for presentations/discussions [S1]. The public 2021S assignment sheet
[S15] and a decade of student reports [S10] fill in the rest. **Verify against
TUWEL in the first week**; the structure
below is 2021S–2025S evidence, not a 2026W statement.

| | |
|---|---|
| **groups** | exactly **3** students [S15] |
| **assignments** | usually 4: a small **Exercise 0** (pass/fail, do not over-invest), then **1 Classification**, **2 Regression** or an implementation task, **3 a free topic** [S10, S15] |
| **deliverables per assignment** | a **10–15 page report** (tables and figures included, **no code in the report**) plus the code/scripts [S15] |
| **presentations** | you present **2 of the 3** big exercises, ≤ 10 minutes [S15]; in some years replaced by a submission interview with a tutor or a professor [S10] |
| **competition** | an in-class **Kaggle** competition on two of the provided data sets, with bonus points; upload limit per day, so start early [S15] |
| **tools** | "use APIs, not the GUI" — scikit-learn, WEKA's API, R, RapidMiner, MATLAB [S15] |
| **workload** | students consistently report the real effort is that of a 6 ECTS course, not 4.5 [S10] |

Two assignments deserve a warning from the reports [S10]:

- **Exercise 2** has in several years required **implementing two algorithms
  yourself** and comparing them with library versions. The submission interview
  (Musliu) goes through the **code line by line** — prepare to explain every
  line and both algorithms in detail. Choose simple algorithms.
- **Exercise 1**'s sheet asks for more than fits in the time budget. Cover
  everything it names *briefly* rather than a third of it deeply; the marking
  rewards a complete, consistent experiment design [S10].

## What Exercise 1 asks for, concretely

From the 2021S sheet [S15], which is the most detailed public statement of the
requirements:

- **4 data sets**, deliberately diverse: small vs large $n$, low vs high $d$,
  few vs many classes, different preprocessing needs. Two come from the course
  Kaggle competition, one from Exercise 0, one you find yourself.
- **3 classifiers "from different types of learning algorithms"** → 12
  data set × classifier combinations.
- **Several parameter settings per classifier per data set** — "not only
  random/best".
- **Multiple, justified performance measures**: say what each measures and why
  it is suitable for *this* task.
- **Significance testing against at least one baseline.**
- **Hold-out vs cross-validation** compared: are there differences, in which
  metrics, why?
- **Runtime** measured and discussed as the data set size changes.
- An **aggregated comparison table** of the best setting and result for every
  combination, plus conclusions *across* data sets, not only per data set.

## Rudolf Mayer's own feedback — the marking scheme in disguise

[S10] reproduces the feedback the lecturer gave after an exercise round. Read it
as a rubric; almost every point maps to a note.

**Preprocessing (note 01, 02).** Missing-value deletion, imbalance handling and
outlier removal done **before** the split modify the test set and make the task
easier; the estimate is then not realistic. The same holds for scaling and for
any hyperparameter tuning that touches test data.

**Experiment design (notes 01, 03, 04).**
- Comparing two algorithms → the **same test set**, the same instances, not just
  the same percentage. The same when changing one parameter of one model.
- Varying a hyperparameter → hold **all others fixed**, or no conclusion can be
  drawn.
- Grid search → make the space **large enough**, expand it if the best value is
  at the edge, stop when the score stops improving, and **visualise** the
  behaviour; zoom in on interesting regions.
- Comparing a classifier across data sets → the same (or at least similar)
  preprocessing and settings.
- **Always include a baseline**: the zero-rule / dummy classifier (majority
  class) is the natural one; a uniform random vote is usually too low a bar.
  (0R and 1R are implemented in `src/py/rules.py` precisely for this.)

**Metrics (note 03).** Ask what the metric measures and what the number means.
Consider: what is being predicted and why; binary, multi-class or multi-label;
is the data balanced (accuracy on imbalanced data is the majority classifier);
is one class more important. Think explicitly about FP and FN with the domain's
costs — the lecturer's own two examples are a disease test (a FN denies
treatment ⇒ favour recall) and advertising (a FP shows an ad to a
non-buyer ⇒ cheap).

**Report.** Several reports are **too long**: the goal is to extract the *main
interesting* points and discuss them, not to print results. Label every table
and figure, give legends and axis labels. Choose the right plot type — comparing
accuracy across scaling methods is a **bar** or scatter plot, **not** a line
graph, because there is no continuous change. Include an overall summary across
all data sets; per-data-set conclusions alone miss the point. Work as a group:
one uniform experiment design, not three concatenated sections with different
splits and preprocessing.

**Presentation.** Pick the interesting findings, the problems you hit,
comparisons, inconsistencies, pros and cons. **Do not re-explain the lecture's
algorithms.** Plots, tables and bullets, not text walls. Mind the time.

## The mechanics

```sh
cd src/py                       # from the course folder
uv run python exercise_template.py data.csv --target label --out results/   # full run
uv run python exercise_template.py data.csv --target label --quick --tune   # fast iteration
uv run python exercise_template.py --demo --quick --tune                    # synthetic smoke test
```

The script infers the task, builds a `ColumnTransformer` (median impute +
standardise numerics; most-frequent impute + one-hot categoricals), runs CV for
a dummy baseline, a linear model, kNN, a tree, a random forest, gradient
boosting, an RBF SVM and an MLP over several metrics, and writes
`cv_results.csv/.md`, a CV box plot, the best model's confusion matrix (or
residual plot), a learning curve and permutation importances, optionally
grid-searching the best model.

**The adaptation is the exercise work**, not the script: edit `model_zoo`
(models, grids, `scoring`) and `make_preprocessor` (log transforms, ordinal
columns, missing indicators, `class_weight`) per data set. Extend with
`GroupKFold` for grouped rows, `TimeSeriesSplit` for temporal data,
`class_weight="balanced"` or SMOTE-in-pipeline for imbalance, target encoding
for high-cardinality categoricals, feature selection inside the pipeline.

For the "implement it yourself" assignment, `src/py` already has from-scratch
versions of kNN, CART, random forest, AdaBoost, gradient boosting, linear and
logistic regression, naive Bayes, SVM (Pegasos and SMO), MLP, $k$-means, DBSCAN,
PCA, 0R/1R/PRISM and the bandit algorithms — all with the
`fit`/`predict`/`predict_proba` interface, so `cross_val_score` and
`grid_search` treat them exactly like sklearn estimators. They are a reference
to check your own implementation against, not something to hand in.

## Report structure

1. **Data and task** — audit table (rows, feature types, missing per column and
   the likely mechanism, class balance, duplicates, suspected leaks), target
   distribution, and the preprocessing decisions **with reasons**.
2. **Experimental setup** — splits, CV scheme, metrics and why, hyperparameter
   grids and ranges, seeds, library versions, hardware. State explicitly that
   every fitted step lives inside the pipeline.
3. **Results** — the CV table (mean ± std per metric, training score beside it
   to show over/underfitting, fit time), the box plot, the tuned model's test
   score reported **once**, and the baseline. A significance test when two
   models are close.
4. **Analysis** — confusion matrix and typical errors; learning curve (would
   more data help?); validation curve of the key hyperparameter; permutation
   importance on held-out data; a small ablation table for preprocessing
   choices (scaled vs not for kNN/SVM, weighted vs not for imbalance).
5. **Cross-data-set conclusions** — which method wins where and why; does any
   method dominate; how sensitive is each to its parameters; how does runtime
   scale.
6. **Conclusion and reproducibility** — the choice, its limits, what you would
   do with more time; commands, seeds, runtime.

## Checklist before submitting

- The test set was used exactly once, after every decision.
- No preprocessing step saw test data, including imputation, outlier removal,
  resampling and feature selection.
- The same test instances are used for every model being compared.
- Only one hyperparameter varies per comparison.
- Grids are log-scaled, their ranges are stated, and no optimum sits at an edge.
- A 0R/dummy baseline is present and beaten.
- Metrics match the task; imbalanced data is not judged by accuracy alone.
- Every number has an uncertainty (fold std) and a comparison point.
- Figures have axis labels, units, legends and captions saying what to see; plot
  types match the data (bars for categories, lines for continua).
- There is a conclusion **across** data sets, not only per data set.
- The report is 10–15 pages, contains no code, and reads as one document.
- The code runs from a clean checkout with one command.
- For the implementation assignment: you can explain every line of your code and
  both algorithms in detail, out loud.
