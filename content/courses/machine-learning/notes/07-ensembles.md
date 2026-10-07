# 07 Ensembles: bagging, random forests, boosting

> Lecture unit 12, “combining models” [S18] — taught *after* the neural-network units. Exam weight ●●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## Why ensembles work

Average of $M$ predictors with individual variance $\sigma^2$ and pairwise correlation $\rho$:
$$\operatorname{Var}\Big(\frac1M\sum_m \hat f_m\Big) = \rho\sigma^2 + \frac{1-\rho}{M}\sigma^2 .$$
Averaging kills the second term; the first survives, so ensembles need *diverse* (decorrelated) members [S23]. For majority voting of $L$ independent classifiers each with accuracy $p$, the lecture writes the **compounded accuracy** the other way up [S18]:
$$p_{\text{maj}} = \sum_{m = \lfloor L/2\rfloor + 1}^{L}\binom Lm p^m(1-p)^{L-m},$$
which exceeds $p$ whenever $p > 0.5$ (Condorcet) — and which, as the lecture is careful to say, *does not hold up in practice*, because the independence assumption fails. Two families: **parallel** (bagging, forests: reduce variance) and **sequential** (boosting: reduce bias by fitting residual errors).

**Homogeneous vs heterogeneous.** An ensemble is *homogeneous* when all members
are the same kind of learner and *heterogeneous* when they are not. A **random
forest is homogeneous** — only trees — which is the answer to a question asked
in three papers (E17b, E19b, E21a) [S12]. Stacking a logistic regression, an SVM
and an MLP is heterogeneous.

**Bagging parallelises, boosting does not.** "Boosting is easily
parallelisable" is **false** and appears in E20b, E20c, E21c and E22a: each
boosting round is fitted to the previous rounds' errors, so the rounds are
sequential by construction. Bagging's members are independent and embarrassingly
parallel [S12].

## Bagging [S33]

For $m = 1..M$: draw a bootstrap sample (size $n$, with replacement: each sample left out with probability $(1 - 1/n)^n \to e^{-1} \approx 0.368$), fit the base learner, aggregate by vote / averaged probabilities / mean. Works for unstable, low-bias learners (unpruned trees, neural nets); does nothing for stable ones (kNN with large $k$, linear models). **Out-of-bag (OOB) score**: predict each sample only from the models that did not see it; a free CV-like estimate.

## Random forests [S33]

Bagging of deep trees plus **random feature subsets at every split** ($m_{\text{try}} = \sqrt d$ for classification, $d/3$ for regression), which decorrelates trees that would otherwise all pick the same strong feature at the root (lowers $\rho$ above). Typically hundreds of trees; more trees never overfit (the average converges), only cost more. Hyperparameters: $m_{\text{try}}$, `min_samples_leaf`, `max_depth`, `n_estimators`. Robust defaults, little tuning, handles mixed features, no scaling. Loses interpretability of a single tree.

**Feature importance**:
- *Impurity (MDI)*: mean over trees of the total impurity decrease per feature; fast; biased towards high-cardinality and continuous features; computed on training data.
- *Permutation (MDA)*: drop in a held-out score when one column is shuffled; model-agnostic; correlated features share/hide importance. Use permutation on validation data for reporting (`ensemble.permutation_importance`).

Extremely randomised trees also randomise the thresholds. Isolation forests use random trees for anomaly detection.

## AdaBoost [S34]

Sequential reweighting. Start $w_i = 1/n$ — **uniform, not random**: "in AdaBoost
the weights are uniformly initialised" is **true** and "randomly initialised" is
**false**, both asked repeatedly (E21b, E21d, E22a, E24a) [S12]. The course's
own recipe [S13, S14] matches the formulation below exactly, with the classifier
weight written $\alpha^{(t)} = \tfrac12\log\frac{1 - \text{TotalError}}{\text{TotalError}}$
and the sample update $D_{t+1}(i) = D_t(i)e^{\mp\alpha^{(t)}}$ ($-$ if correct,
$+$ if wrong), followed by renormalisation to sum 1.

For $m = 1..M$:
1. fit weak learner $h_m$ (usually a stump) to the weighted data; weighted error $\epsilon_m = \sum_i w_i [h_m(x_i) \ne y_i] / \sum_i w_i$;
2. $\alpha_m = \frac12\ln\frac{1 - \epsilon_m}{\epsilon_m}$ (binary, $y \in \{\pm1\}$); multiclass SAMME: $\alpha_m = \ln\frac{1-\epsilon_m}{\epsilon_m} + \ln(K-1)$;
3. $w_i \leftarrow w_i \exp(-\alpha_m y_i h_m(x_i))$ (up-weight mistakes), normalise.

Final $H(x) = \operatorname{sign}\sum_m \alpha_m h_m(x)$. Stops making sense when $\epsilon_m \ge 0.5$. AdaBoost is coordinate descent on the exponential loss $\sum_i e^{-y_i F(x_i)}$; the training error is bounded by $\prod_m 2\sqrt{\epsilon_m(1-\epsilon_m)}$, decreasing exponentially if every $\epsilon_m \le 0.5 - \gamma$. Sensitive to label noise (outliers get ever larger weights).

## Gradient boosting [S34]

Generalises boosting to any differentiable loss: fit an additive model $F_M(x) = F_0 + \nu\sum_{m=1}^M h_m(x)$ by steepest descent in function space.

1. $F_0 = \operatorname{argmin}_c \sum_i L(y_i, c)$ (mean for squared loss, log-odds of the prior for log loss) — **this is the zero-rule model**, and the exam asks it as "Is gradient boosting 0 Rule?" / "The first model in gradient boosting is a zero rule model", answer **true** (E23b, E24a, E26a) [S12]. The variant "gradient boosting for classification always starts with the *one*-rule model" is **false** [S18]. The other recurring item, "gradient boosting minimises the residual of the previous classifiers", is **true** (E21b) — and it is what distinguishes gradient boosting from AdaBoost, which reweights *misclassified samples* rather than fitting *residuals* [S18].
2. For $m = 1..M$: pseudo-residuals $r_i = -\partial L(y_i, F)/\partial F|_{F = F_{m-1}(x_i)}$ (squared loss: $y_i - F(x_i)$; log loss: $y_i - \sigma(F(x_i))$); fit a small regression tree $h_m$ to $(x_i, r_i)$; set each leaf value to the loss-optimal constant (squared loss: the mean; log loss: one Newton step $\sum r_i / \sum p_i(1-p_i)$); $F_m = F_{m-1} + \nu h_m$.

Hyperparameters interact: learning rate $\nu$ (0.01–0.3), number of trees $M$ (choose by early stopping on validation loss), tree depth (2–8; depth $d$ captures interactions of order $d$), subsampling rows (stochastic GB, 0.5–0.8) and columns, $L_2$ on leaf values ($\lambda$ in XGBoost), minimum child weight. Smaller $\nu$ needs larger $M$ and generalises better. Modern implementations (XGBoost, LightGBM, CatBoost, sklearn `HistGradientBoosting`) add second-order (Newton) steps, histogram binning of features, native categorical and missing-value handling; they are the default strong learner for tabular data.

Boosting *can* overfit with too many rounds (unlike bagging); monitor validation loss.

## Stacking

Train a meta-learner on out-of-fold predictions of several base models (their predictions become features). Must use OOF predictions, otherwise the meta-learner just trusts the most overfitted base model. Voting (hard/soft) is stacking with a fixed meta-rule.

## Worked example

500 samples, 10 features, 4 informative (`ensemble.py` `__main__`): single unpruned tree 0.78 test accuracy; bagging of 30 trees 0.81 (OOB 0.84); random forest of 50 trees 0.86; AdaBoost with 50 stumps 0.81 (first weighted errors 0.31, 0.35, 0.36 — the stumps get weaker as weights concentrate on hard points); gradient boosting with 100 depth-3 trees at $\nu = 0.1$: 0.87. Impurity importance ranks the four informative features (0, 1, 4, 7) at the top; permutation importance on the test set agrees on the strongest ones and gives $\approx 0$ for the noise features.

AdaBoost by hand, one round: 5 samples, $w = 0.2$ each; stump misclassifies sample 3: $\epsilon = 0.2$, $\alpha = \frac12\ln 4 = 0.693$; weights: wrong sample $0.2 e^{0.693} = 0.4$, right ones $0.2 e^{-0.693} = 0.1$; normalise by $0.8$: $[0.125, 0.125, 0.5, 0.125, 0.125]$. The next stump must get sample 3 right to have $\epsilon < 0.5$.

## Pitfalls

- Bagging a linear model or a heavily pruned tree: nothing to gain (low variance already).
- Judging a forest by OOB *and* tuning on OOB, then reporting OOB: it is now a validation score.
- Impurity importance on training data with a high-cardinality ID-like feature: it looks important.
- AdaBoost on noisy labels; GB with $\nu = 1$ and hundreds of trees (overfits); GB without early stopping.
- Stacking with in-sample base predictions (leak).
- Forgetting that random forests do not extrapolate (piecewise constant) and are hard to deploy at very low latency.

## Exam-style questions

1. **Why does a random forest use random feature subsets in addition to bootstrapping?** Bootstrap alone leaves the trees correlated because a dominant feature wins the root split in almost every tree; averaging correlated predictors leaves $\rho\sigma^2$ of the variance. Restricting each split to $m_{\text{try}}$ random features decorrelates the trees and lowers $\rho$ at a small bias cost.
2. **Derive $\alpha_m$ in AdaBoost from the exponential loss.** With $F = F_{m-1} + \alpha h$, $\sum_i w_i e^{-\alpha y_i h(x_i)} = e^{-\alpha}\sum_{\text{right}} w_i + e^{\alpha}\sum_{\text{wrong}} w_i = e^{-\alpha}(1-\epsilon) + e^{\alpha}\epsilon$ (normalised weights). Setting the derivative to zero: $-e^{-\alpha}(1-\epsilon) + e^{\alpha}\epsilon = 0 \Rightarrow \alpha = \frac12\ln\frac{1-\epsilon}{\epsilon}$.
3. **Contrast bagging and boosting in what they reduce, how members are trained, and sensitivity to noise.** Bagging: variance; independent parallel fits on bootstraps of full-depth trees; robust to noise. Boosting: bias (and variance with shrinkage); sequential fits on reweighted data or residuals with shallow trees; sensitive to label noise, can overfit with many rounds.
4. **What are the pseudo-residuals of gradient boosting for the logistic loss, and what is $F_0$?** $L = -[y\log\sigma(F) + (1-y)\log(1-\sigma(F))]$, $-\partial L/\partial F = y - \sigma(F)$; $F_0 = \log\frac{\bar y}{1 - \bar y}$, the log-odds of the positive rate.
5. **What is an out-of-bag estimate and why is it "free"?** *(ours.)* Each bootstrap leaves out $\approx 37\%$ of the samples; predicting those samples with only the trees that did not train on them gives a held-out estimate without a separate validation set or extra fits.
6. **Describe the random forest algorithm in detail. What is the randomness in it?** *(modelled on E17a, E21b, E21c — asked three times.)* Draw $n$ bootstrap samples (with replacement) from the training set; grow one unpruned decision tree on each; **at every node, restrict the split search to a random subset of the features** ($\sqrt d$ for classification); predict by majority vote over the trees. The two sources of randomness are therefore the bootstrap *rows* and the per-split *feature* subset; the second is what accentuates the differences between trees [S12, S33].
7. **AdaBoost by hand: three points on a line at $x = 1, 3, 5$ with labels $-1, +1, -1$, using decision stumps. What weight does each point carry before the first round? Draw the first stump's boundary and mark the point whose weight grows.** *(modelled on E19b, E20b, E21a.)* Each point starts at $1/n = 1/3$ [S12]. A single split cannot separate $\{-1, +1, -1\}$, so the best stump — say at $x = 2$ or $x = 4$ — gets two of the three right, $\epsilon = 1/3$, $\alpha = \tfrac12\ln 2 = 0.347$. The one misclassified point (the outer $-1$ on the far side of the boundary) has its weight multiplied by $e^{\alpha} = 1.41$ and the other two by $e^{-\alpha} = 0.707$; after renormalising the weights are $(0.25, 0.25, 0.5)$ and the next stump must get that point right to beat $\epsilon = 0.5$.
8. **"If several linear weak learners are combined by boosting, is the resulting classifier linear?"** *(E21a.)* **No.** The ensemble is $\operatorname{sign}\sum_m\alpha_m h_m(x)$; the sign of a sum of thresholded linear functions is piecewise linear, not linear — which is exactly why boosting stumps can fit XOR-like data.

## Code

`src/py/ensemble.py`: `Bagging(base, n_estimators)` with `oob_score_`, `RandomForest(max_features="sqrt")` with `feature_importances_`, `permutation_importance`, `AdaBoost` (SAMME on `tree.DecisionTree` stumps with `sample_weight`), `GradientBoosting(loss="squared"|"log")` with Newton leaf values. Tests compare accuracy, OOB score, first-stump error and decision-function correlation with `sklearn.ensemble`.
