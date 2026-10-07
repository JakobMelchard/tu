# 05 k-nearest neighbours and distance metrics

> Lecture unit 4 [S18]. Exam weight ●●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

A lazy, non-parametric, instance-based learner: store the training set; to predict $x$, find the $k$ training points closest to $x$ and vote (classification) or average (regression). No training cost, all cost at query time. Inductive bias: the target is locally constant / smooth in the chosen metric.

## Definitions

- Prediction: $\hat y(x) = \operatorname{argmax}_c \sum_{i \in N_k(x)} w_i\,[y_i = c]$, or $\hat y(x) = \frac{\sum_{i \in N_k(x)} w_i y_i}{\sum w_i}$. Uniform weights $w_i = 1$ or distance weights $w_i = 1/d(x, x_i)$.
- Posterior estimate $\hat p(c \mid x) = \frac{1}{k}\sum_{i \in N_k(x)}[y_i = c]$; kNN is a plug-in Bayes classifier with a locally uniform density estimate.
- **Cover & Hart (1967)**: as $n \to \infty$ the 1-NN error is at most twice the Bayes error; with $k \to \infty$, $k/n \to 0$ the kNN error approaches the Bayes error.

**The true/false bank for this note** [S12] — kNN generates more section-1 items
than any other model:

| statement | answer | why |
|---|---|---|
| The error of a 1-NN classifier on the training set is 0 | **T** | each point is its own nearest neighbour |
| kNN is based on a supervised paradigm | **T** | it uses labels; the unsupervised analogue is $k$-means (note 12) |
| kNN is recommended for large data sets / lazy learners are good for big data | **F** | every prediction costs $O(nd)$ and the whole data set must stay in memory |
| Majority voting is *not* used when kNN predicts numeric values | **T** | regression averages the neighbours (E22a, E21d, E23c) |
| A k-d tree can be used as a search-space optimisation for kNN | **T** | $O(\log n)$ queries for small $d$ (E21b) |
| Categorical features should be normalised before training a kNN | **F** | they should be **encoded**; normalisation is for numeric features (E18a, E21d) |
| Training time of kNN depends on the chosen distance metric | **F** | there is no training; the *prediction* time does (E23b) [S18] |

"Which classification methods use majority voting?" is a section-3 list in E26a;
**kNN** and **random forests** are in, decision trees and Bayesian networks are
out, and so is an ensemble that outputs the single most confident model's
prediction.

## Distance metrics

For $a, b \in \mathbb R^d$:

| Metric | Formula | Notes |
|---|---|---|
| Euclidean ($L_2$) | $\sqrt{\sum_j (a_j - b_j)^2}$ | default; rotation invariant; scale sensitive |
| Manhattan ($L_1$) | $\sum_j |a_j - b_j|$ | less affected by single large coordinates |
| Minkowski ($L_p$) | $(\sum_j |a_j - b_j|^p)^{1/p}$ | $p = 1, 2$ above; $p \to \infty$ Chebyshev $\max_j |a_j - b_j|$ |
| Mahalanobis | $\sqrt{(a-b)^\top \Sigma^{-1}(a-b)}$ | whitens by the covariance; equals Euclidean after the transform $x \mapsto \Sigma^{-1/2}x$ |
| Cosine distance | $1 - \frac{a\cdot b}{\|a\|\|b\|}$ | direction only; text, sparse vectors |
| Hamming | $\frac1d\sum_j [a_j \ne b_j]$ | binary/categorical |
| Gower | mean of per-feature dissimilarities (range-normalised numeric, mismatch for nominal) | mixed types |

A metric satisfies $d(a,b) \ge 0$, $d(a,b) = 0 \Leftrightarrow a = b$, symmetry, triangle inequality. Cosine "distance" violates the triangle inequality but works fine for kNN.

Fast $L_2$: $\|a - b\|^2 = \|a\|^2 + \|b\|^2 - 2a\cdot b$, one matrix product for all pairs (`knn.pairwise_distances`); `sklearn.neighbors` uses the same identity [S42].

## Choosing $k$ and complexity

- $k = 1$: zero training error, jagged boundary, high variance. Large $k$: smooth boundary, high bias; $k = n$ predicts the majority class. Odd $k$ avoids ties in binary problems. Choose by CV (`knn.choose_k_by_cv`); rule of thumb $k \approx \sqrt n$ is a starting point only.
- Query cost brute force $O(nd)$ per query; KD-trees give $O(\log n)$ for small $d$ ($\lesssim 20$), ball trees somewhat higher, approximate methods (LSH, HNSW) beyond. Memory $O(nd)$.
- Editing / condensing (Hart's CNN) removes training points that do not change the decision boundary.

## Curse of dimensionality

In high $d$ all pairwise distances concentrate: for i.i.d. coordinates $\frac{\max d - \min d}{\min d} \to 0$. The fraction of the unit cube's volume within a cube of edge $r$ is $r^d$, so to capture 1 % of uniformly spread points in $d = 10$ you need $r = 0.01^{1/10} = 0.63$ of *each* edge, i.e. the "neighbourhood" spans most of the range. Remedies: feature selection, PCA, metric learning, or models with a stronger bias.

## Worked example

Two classes in $\mathbb R^2$, query $x = (0, 0)$, training points and $L_2$ distances: $(0.1, 0.2)\to$A, $d = 0.22$; $(-0.3, 0.1)\to$B, $0.32$; $(0.4, 0)\to$B, $0.40$; $(0, -0.5)\to$A, $0.50$; $(1, 1)\to$B, $1.41$. 1-NN: A. 3-NN uniform: A, B, B → B. 3-NN distance-weighted: A gets $1/0.22 = 4.5$, B gets $1/0.32 + 1/0.40 = 5.6$ → B. 5-NN: 2 A vs 3 B → B. If the second feature were measured in cm instead of m (×100), the $y$ coordinate would dominate every distance and the ranking would change: scale first.

## Pitfalls

- Unscaled features (a feature in the thousands swamps the rest); one-hot columns and numeric columns mixed without thought (a category mismatch counts as $\sqrt 2$).
- Even $k$ with binary classes → ties (sklearn breaks them by class order).
- Slow at prediction time on large $n$; memory-bound.
- Irrelevant features add noise to every distance; kNN has no built-in feature weighting.
- Distance weighting with duplicate points ($d = 0$) → infinite weight; clip.
- Using kNN as a "no-assumption" method: it assumes smoothness in the chosen metric, which is a strong assumption in high dimensions.

## Exam-style questions

1. **Why is kNN called a lazy learner and what are the consequences?** No model is built at training time; the data is the model. Training is $O(1)$, prediction $O(nd)$ per query and memory $O(nd)$; retraining with new data is trivial; the decision boundary can be arbitrarily complex.
2. **Bias and variance as a function of $k$.** Small $k$: low bias, high variance (noisy neighbours decide). Large $k$: high bias (averages over distant, differently-labelled points), low variance. Pick $k$ by CV; the validation curve is U-shaped.
3. **Give the Mahalanobis distance and explain when it is preferable to Euclidean.** $d = \sqrt{(a-b)^\top\Sigma^{-1}(a-b)}$. When features have different variances and are correlated: it whitens the data so that one unit along any direction means one standard deviation, removing the double counting of correlated features. Costs $O(d^2)$ per distance and needs a well-conditioned $\Sigma$.
4. **Explain the curse of dimensionality for kNN with a numerical argument.** For uniform data in $[0,1]^d$ the edge of a hypercube containing a fraction $p$ of the data is $p^{1/d}$; with $p = 0.01$, $d = 100$: $0.955$. Neighbourhoods are no longer local, nearest and farthest neighbours have almost the same distance, and the locality assumption fails.
5. **Compare kNN with a decision tree on: training cost, prediction cost, need for scaling, interpretability.** *(ours.)* kNN: none / $O(nd)$ / yes / low (only examples). Tree: $O(dn\log n)$ per level / $O(\text{depth})$ / no / high (rules).
6. **Ten labelled points in the plane; compute the average error rate under leave-one-out CV for 1-NN and for 3-NN.** *(modelled on E20b; E17a and E19b are the same question with 7 and 9 points.)* LOOCV with $n$ points is $n$-fold CV: for each point, find its $k$ nearest neighbours **among the other nine**, vote, and compare with its true label; the error rate is the fraction misclassified. 1-NN is *not* 0 % here, because a point's own label is excluded — that is the whole point of the question. `knn.choose_k_by_cv` does this with `cv=n`.
7. **Given a data set with categorical attributes, define a suitable distance function for kNN and justify it.** *(modelled on E17a, E19b.)* Use the **Hamming** distance — 0 if two attribute values are equal, 1 otherwise, summed over attributes — because nominal values have no order and no spacing, so any numeric coding would invent distances. For mixed numeric and nominal columns use **Gower**: range-normalise each numeric column to $[0,1]$ and average the per-feature dissimilarities, so every attribute contributes equally. Euclidean is the default only when all attributes are numeric and comparably scaled [S12].

## Code

`src/py/knn.py`: `pairwise_distances(metric=euclidean|manhattan|chebyshev|minkowski|cosine|hamming)`, `mahalanobis`, `KNNClassifier(k, metric, weights)`, `KNNRegressor`, `choose_k_by_cv`. Test compares to `sklearn.neighbors` on the same data.
