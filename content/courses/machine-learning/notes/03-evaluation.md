# 03 Evaluation of learning systems

> Lecture unit 3 [S18]. Exam weight ●●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## Classification metrics

Binary confusion matrix (rows = truth, columns = prediction):

|  | predicted + | predicted − |
|---|---|---|
| actual + | TP | FN |
| actual − | FP | TN |

$$\text{accuracy} = \frac{TP+TN}{n},\quad \text{precision} = \frac{TP}{TP+FP},\quad \text{recall (TPR, sensitivity)} = \frac{TP}{TP+FN},\quad \text{specificity (TNR)} = \frac{TN}{TN+FP},\quad \text{FPR} = 1 - \text{TNR}$$

$$F_1 = \frac{2PR}{P+R} = \frac{2TP}{2TP + FP + FN},\qquad F_\beta = (1+\beta^2)\frac{PR}{\beta^2 P + R}\ (\beta > 1 \text{ favours recall})$$

Balanced accuracy $= \tfrac12(\text{TPR} + \text{TNR})$. Matthews correlation $\text{MCC} = \frac{TP\cdot TN - FP\cdot FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}} \in [-1, 1]$, robust to imbalance. Cohen's $\kappa = \frac{p_o - p_e}{1 - p_e}$ corrects accuracy for chance agreement.

Multiclass: per-class one-vs-rest precision/recall, then **macro** (unweighted mean over classes, every class counts equally), **weighted** (by support), **micro** (pool TP/FP/FN; equals accuracy for single-label problems).

## Threshold-free curves

A scorer $s(x)$ gives a family of classifiers $s(x) > t$.

- **ROC curve**: TPR vs FPR as $t$ sweeps. Diagonal = random; (0,1) = perfect. **AUC** $= P(s(x_+) > s(x_-))$, the probability a random positive outranks a random negative (Mann–Whitney $U/(n_+ n_-)$). Invariant to class prior; can look good on very imbalanced data because FPR stays tiny in absolute FP counts.
- **Precision–recall curve**: precision vs recall as $t$ sweeps; baseline = prevalence $n_+/n$. **Average precision** $\text{AP} = \sum_k (R_k - R_{k-1}) P_k$. Preferred when positives are rare and false positives are costly.
- Choosing $t$: maximise Youden's $J = \text{TPR} - \text{FPR}$, fix a recall target, or minimise expected cost $c_{FP}\,FP + c_{FN}\,FN$.
- **Calibration**: a probabilistic classifier is calibrated if among samples with $\hat p = 0.7$ about 70 % are positive. Check with a reliability diagram; score with **log loss** $-\frac1n\sum_i [y_i \log \hat p_i + (1-y_i)\log(1-\hat p_i)]$ or **Brier** $\frac1n\sum (\hat p_i - y_i)^2$. SVMs and boosted trees are typically badly calibrated; Platt scaling / isotonic regression fix it.

## Regression metrics

$$\text{MSE} = \frac1n\sum (y_i - \hat y_i)^2,\quad \text{RMSE} = \sqrt{\text{MSE}},\quad \text{MAE} = \frac1n\sum|y_i - \hat y_i|,\quad R^2 = 1 - \frac{\sum(y_i - \hat y_i)^2}{\sum(y_i - \bar y)^2}$$

$R^2 \le 1$; equals 0 for predicting the mean, negative for worse. MAE is robust to outliers, MSE punishes them quadratically (and is what OLS minimises). MAPE $= \frac1n\sum |y_i - \hat y_i|/|y_i|$ breaks near $y = 0$. Adjusted $R^2 = 1 - (1-R^2)\frac{n-1}{n-p-1}$ penalises extra features.

**The course's regression metric set is WEKA's, not scikit-learn's** [S13, S22].
The formula sheet lists MAE and MSE together with three *relative* measures and
a correlation coefficient, and those are what a "name three methods to compute
the error in regression" question (E21b, E22a) is drawn from. Writing
$p_i$ for the prediction, $a_i$ for the actual value and $\bar a$ for the mean
of the actuals:

$$\text{RSE} = \frac{\sum_i (p_i - a_i)^2}{\sum_i (\bar a - a_i)^2},\qquad
  \text{RRSE} = \sqrt{\text{RSE}},\qquad
  \text{RAE} = \frac{\sum_i |p_i - a_i|}{\sum_i |\bar a - a_i|}$$

The denominator is the error of the **0R baseline** (predict the mean), so these
are unitless, comparable across data sets, and equal to 1 for a model no better
than the baseline. Note $R^2 = 1 - \text{RSE}$ for a model fitted with an
intercept: the same quantity, reported the other way up. The **correlation
coefficient** WEKA prints is Pearson's $r$ between $p$ and $a$,
$r = \frac{S_{pa}}{\sqrt{S_{pp}S_{aa}}} \in [-1, 1]$ [S13] — the source of the
true/false item "the Pearson coefficient has a value range from $-1$ to 1"
(E21d, **true**). Implemented in `metrics.py` as `rse`, `rrse`, `rae` and
`correlation_coefficient`.

$F_1$ and the other classification metrics are **not** regression metrics —
"F-score is an important performance metric used for evaluating regression
techniques" is **false** (E20c, E23c) [S12, S18].

## Estimating generalisation

- **Hold-out**: one split. Cheap; high variance for small $n$; every sample is either train or test.
- **$k$-fold CV** [S28]: partition into $k$ folds, train on $k-1$, test on 1, average. Each sample is tested exactly once. $k = 5$ or $10$ is standard; **stratified** for classification. Leave-one-out ($k = n$): nearly unbiased, expensive, high variance (folds almost identical).
- **Leave-$p$-out**: every subset of size $p$ is used as the test set in turn — $\binom np$ fits, so "leave-$p$-out CV is computationally expensive on large data sets" is **true** (E20c) [S12].
- **Repeated CV** ($r \times k$) reduces the variance of the estimate; **bootstrap** is an alternative: draw a sample of size $n$ **with replacement** as the training set and use the $\approx 36.8\,\%$ **out-of-bag** rows as the test set (the $.632$ rule corrects the resulting pessimism) [S18]. Note that the lecture describes the bootstrap set as the *test* set in places [S18]; the usual convention, and the one `ensemble.Bagging` uses, is bootstrap = train, OOB = test.
- Report **mean ± std over folds**; the std is the spread of the *fold* scores, not a confidence interval of the mean (folds are correlated).
- Remember: CV estimates the performance of the *procedure* (fit this model family with this preprocessing), not of one particular fitted model. The final model is refit on all training data.

## Comparing models statistically

Same folds for both models → paired scores $d_j = a_j - b_j$.

- **Paired $t$-test**: $t = \bar d / (s_d / \sqrt{k})$, $k-1$ dof — the formula
  sheet states this as "number of degrees of freedom = number of runs − 1"
  [S13]. Optimistic, because training sets overlap so the $d_j$ are not
  independent [S36 Dietterich].
- **Corrected resampled $t$-test** (Nadeau & Bengio [S36]): $\hat\sigma^2 \to \hat\sigma^2\,(\tfrac1k + \tfrac{n_{\text{test}}}{n_{\text{train}}})$; the standard recommendation with $k$-fold or repeated hold-out.
- **McNemar's test** on one test set: count $b$ = A right & B wrong, $c$ = A wrong & B right; $\chi^2 = \frac{(|b-c|-1)^2}{b+c}$ with 1 dof. Uses the disagreements only. Reject at the 5 % level when $\chi^2 > 3.84$ [S43]. "McNemar's test is used for significance testing" is **true** (E17b) [S12].
- Many models on many data sets: Friedman test on ranks, then Nemenyi post-hoc [S36 Demšar].
- Do not confuse "not significant" with "equal"; with 5 folds the power is low.

**The paired-$t$-test trap.** The archive asks, in several wordings, when a
paired $t$-test applies. The sources disagree and you should know both readings
before the exam:

| wording seen in a paper | [S12] | [S18] / [S36] |
|---|---|---|
| "…for results obtained with **cross-validation**" | True | True |
| "…for results obtained with **hold-out** validation" | True (E22a) | **False** (E23b): one split gives one number, not a paired sample |
| "paired t-tests used for **folds verification** in the holdout method (train/test split)" | **False** (E19b, E20b) | False |

The coherent reading, and the one to answer with: a paired test needs *several
matched pairs of scores*, which $k$-fold CV (or repeated hold-out) provides and
a **single** train/test split does not. Where the statement mentions "folds …
in the holdout method" it is self-contradictory and the expected answer is
**false**. See [`00-exam-focus.md`](00-exam-focus.md) §"Where the course's answer
is not the textbook answer".

## Bias–variance decomposition

For squared loss and $y = f(x) + \varepsilon$ [S23 §7.3], $\mathbb E\varepsilon = 0$, $\operatorname{Var}\varepsilon = \sigma^2$, the expected test error at $x$ over training sets $D$:

$$\mathbb E_D\big[(y - \hat f_D(x))^2\big] = \underbrace{\big(f(x) - \mathbb E_D \hat f_D(x)\big)^2}_{\text{bias}^2} + \underbrace{\mathbb E_D\big[(\hat f_D(x) - \mathbb E_D\hat f_D(x))^2\big]}_{\text{variance}} + \underbrace{\sigma^2}_{\text{irreducible}}$$

Derivation: add and subtract $\mathbb E_D \hat f_D(x)$ inside the square; the cross terms vanish because $\varepsilon$ is independent of $D$ and $\mathbb E_D[\hat f_D - \mathbb E_D \hat f_D] = 0$. Flexible models (deep trees, 1-NN, high-degree polynomials) have low bias and high variance; rigid ones (linear, large-$k$ kNN) the opposite. Bagging reduces variance; boosting reduces bias; regularisation trades variance for bias.

## Worked example

Test set with 100 positives and 900 negatives; classifier predicts 150 positives of which 80 are true.
TP = 80, FP = 70, FN = 20, TN = 830. Accuracy $= 910/1000 = 0.91$ (majority baseline 0.90). Precision $= 80/150 = 0.533$, recall $= 0.8$, $F_1 = 2\cdot0.533\cdot0.8/1.333 = 0.64$, FPR $= 70/900 = 0.078$, balanced accuracy $= (0.8 + 0.922)/2 = 0.861$. Accuracy barely beats the baseline while recall is high and precision mediocre: the useful summary is $F_1$ or the PR curve, not accuracy.

Bias–variance numerically: a 1-NN on $n = 200$ noisy points and a linear fit. Repeating the fit on 100 bootstrap training sets, the linear model's predictions at a fixed $x$ vary with std 0.05 but are off by 0.4 on average (bias); 1-NN varies with std 0.6 and is centred on the truth. Averaging 50 1-NN models (bagging) cuts the std to 0.15 at unchanged bias.

## Pitfalls

- Accuracy on imbalanced data; ROC-AUC when the positive class is rare and FP matter (use PR-AUC).
- Choosing the decision threshold on the test set.
- `cross_val_score` on data that was already scaled/resampled/feature-selected globally (leak, note 01).
- Comparing CV means without any notion of spread; declaring 0.912 better than 0.908.
- Using $R^2$ of training data to judge fit quality; adding features never lowers training $R^2$.
- Micro vs macro F1: micro is dominated by big classes; report macro when minority classes matter.

## Exam-style questions

1. **Compute precision, recall, F1 and specificity for TP = 30, FP = 10, FN = 20, TN = 940.** P $= 0.75$, R $= 0.6$, $F_1 = 2(0.75)(0.6)/1.35 = 0.667$, specificity $= 940/950 = 0.989$. Accuracy $0.97$ vs majority baseline $0.96$.
2. **What does AUC = 0.5 and AUC = 0.9 mean? Why can AUC mislead on imbalanced data?** AUC is the probability that a random positive scores higher than a random negative; 0.5 = random ranking, 0.9 = strong ranking. With 1 % positives, an FPR of 0.05 already means 5× more false than true positives; ROC looks fine, precision is terrible. Use the PR curve.
3. **Why is 10-fold CV preferred over a single 90/10 hold-out, and what does it estimate?** Every sample is used for testing once, so the estimate has lower variance and uses the data efficiently; it estimates the expected performance of the *training procedure* on data of size $\approx 0.9n$, not of one fitted model.
4. **Why is the plain paired t-test over CV folds anti-conservative? Name a fix.** The fold training sets overlap (each pair shares $(k-2)/(k-1)$ of the data), so fold scores are positively correlated and the variance estimate is too small → too many "significant" differences. Fix: corrected resampled t-test (variance factor $1/k + n_{\text{test}}/n_{\text{train}}$), or McNemar on a single test set.
5. **Describe three methods to compute the error in regression.** *(modelled on E21b, E22a.)* $\text{MAE} = \frac1n\sum|p_i - a_i|$ (robust to outliers); $\text{MSE} = \frac1n\sum(p_i-a_i)^2$ and its root RMSE (in the target's units, punishes large errors); and a *relative* measure — RAE or RRSE — which divides by the error of the mean-predicting baseline and is therefore unitless and comparable across data sets. $R^2 = 1 - \text{RSE}$ reports the same thing as the fraction of variance explained.
6. **What is the difference between micro- and macro-averaged performance measures?** *(E21b, E21d, E22a — asked three times.)* **Macro**: compute the metric separately for each class, then take the unweighted mean, so every class counts equally regardless of size. **Micro**: pool the TP/FP/FN counts over all classes first and compute the metric once, so large classes dominate (and for single-label problems micro-F1 equals accuracy). Report macro when minority classes matter.
7. **State the bias–variance decomposition and place kNN with $k = 1$ and $k = n$ on it.** *(ours.)* See formula above. $k = 1$: bias $\approx 0$ (interpolates), variance maximal (prediction depends on one noisy neighbour). $k = n$: predicts the global mean everywhere, variance $\approx 0$, bias maximal. Optimal $k$ balances the two; a learning/validation curve over $k$ finds it.

## Code

`src/py/metrics.py`: `confusion_matrix`, `precision_recall_f1(average=binary|macro|micro)`, `roc_curve`, `roc_auc`, `roc_auc_rank` (Mann–Whitney form), `precision_recall_curve`, `average_precision`, `log_loss`, `mse`, `rmse`, `mae`, `r2`, `classification_report`, and the WEKA family added in the source pass: **`rse`, `rrse`, `rae`, `correlation_coefficient`, `regression_report`** [S13].
`src/py/model_selection.py`: `kfold`, `stratified_kfold`, `cross_val_score`, `cross_val_predict`, `paired_t_test`, `corrected_resampled_t_test`, `mcnemar_test`.
