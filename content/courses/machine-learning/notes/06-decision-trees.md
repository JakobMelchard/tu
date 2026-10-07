# 06 Decision trees

> Lecture unit 5 [S18]. Exam weight ●●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

A tree of tests on single features (axis-parallel splits $x_j \le t$ for numeric, $x_j \in S$ for categorical) whose leaves carry a class distribution or a numeric value. Learned greedily top-down by choosing, at each node, the split that most reduces an impurity measure. Algorithms: ID3 (categorical, information gain [S27]), C4.5 (gain ratio, numeric thresholds, missing values, pruning), **CART** (binary splits, Gini / MSE, cost-complexity pruning; what sklearn implements).

## 0R, 1R and the covering algorithm — the rule learners around the tree

The course teaches three rule learners next to the tree, and **1R is asked more
often than any other calculation except naive Bayes** (E17b, E18a, E19a, E20b,
E21b, E24a, E26a) [S11].

- **0R (zero rule / ZeroR)**: predict the majority class (classification) or the
  mean (regression), always. It is the **baseline** every exercise report must
  beat [S10], and it is what gradient boosting starts from — the true/false item
  "the first model in gradient boosting is a zero rule model" is **true**
  (E23b, E24a, E26a) [S12], while "gradient boosting always starts with the
  *one*-rule model" is **false** [S18].
- **1R (one rule / OneR)** [S29, S22]: for each attribute $A$, build one rule per
  value of $A$ predicting the majority class among the training rows with that
  value; count how many training rows the resulting rule set gets wrong; choose
  the attribute with the fewest errors. Numeric attributes are discretised
  first, with a minimum bucket size to stop the split degenerating. **1R is a
  decision tree with only a root node** — a decision stump — which is the
  relation E21b asks for directly [S12].
- **The covering algorithm** (PRISM) [S22], asked in E19a ("generate covering
  algorithms to separate Martians from humans"): fix a class; start with an
  empty rule `IF ? THEN class`; greedily add the attribute test with the highest
  *accuracy* $p/t$ on the rows the rule still covers (ties broken by larger
  $t$); stop when the rule is pure; remove the covered rows and repeat until the
  class is exhausted; then move to the next class. Separate-and-conquer, as
  opposed to a tree's divide-and-conquer.

"A decision tree can be converted into a rule set" is **true** (E23a): one rule
per root-to-leaf path, at the cost of a large and redundant rule set [S12].

Implemented in [`../src/py/rules.py`](../src/py/rules.py) (`ZeroR`, `OneR`,
`Prism`), which also prints the per-attribute error table a 1R question wants.

## Impurity measures

For a node with class proportions $p_1, \dots, p_K$:

$$H = -\sum_c p_c \log_2 p_c \ (\text{entropy, bits}),\qquad G = 1 - \sum_c p_c^2 \ (\text{Gini}),\qquad E = 1 - \max_c p_c \ (\text{misclassification})$$

Both $H$ and $G$ are maximal at the uniform distribution ($H = \log_2 K$, $G = 1 - 1/K$), zero for a pure node, and strictly concave, so a split never increases them and a split that only changes proportions within one child gets credit (misclassification error does not, which is why it is not used for growing). $G \approx H/2$ in shape; they choose the same split almost always.

Regression: node impurity = variance $\frac{1}{n}\sum (y_i - \bar y)^2$ (squared error); leaf value $\bar y$. MAE variant uses the median.

## Split selection

Weighted child impurity $I_{\text{split}} = \sum_{k} \frac{n_k}{n} I(\text{child}_k)$, and

$$\text{information gain } IG = H(\text{parent}) - I_{\text{split}},\qquad \text{gain ratio} = \frac{IG}{\text{SplitInfo}},\quad \text{SplitInfo} = -\sum_k \frac{n_k}{n}\log_2\frac{n_k}{n}$$

The lecture's own notation, which a hand calculation should use [S13, S14]:
$IG(X_A, X_B) = H(X) - p(x_a)H(X_A) - p(x_B)H(X_B)$ for a binary split into
subsets $A$ and $B$, with $p(x_a) = |A|/(|A|+|B|)$ and each child's entropy
computed **over all classes**; and the identical form for Gini,
$GG(X_A,X_B) = I_G(X) - p(x_a)I_G(X_A) - p(x_B)I_G(X_B)$. [S14] names **three**
split scores, not two: **absolute error rate** (the absolute number of
misclassified samples in the subsets — lowest wins), **information gain**
(highest wins) and **Gini gain** (highest wins). The exam item "decision trees
using error rate vs entropy leads to different results" is **true** (E21b)
[S12], and "decision trees are learned by maximising information gain" is also
marked **true** (E23b) even though it is only one of the three criteria [S18].

Gain ratio (C4.5) penalises many-valued attributes (an ID column has maximal IG and is useless). For numeric features candidate thresholds are midpoints between sorted distinct values; with cumulative class counts all thresholds of one feature are scored in $O(n)$ after an $O(n\log n)$ sort (`tree.DecisionTree._best_split`). Cost per level $O(d\,n\log n)$.

## Stopping and pruning

Growing until leaves are pure overfits (a leaf per sample). Pre-pruning: `max_depth`, `min_samples_split`, `min_samples_leaf`, `min_impurity_decrease`, `max_leaf_nodes`. Post-pruning (grow fully, then cut):

- **Reduced-error pruning**: replace a subtree by a leaf if validation accuracy does not drop.
- **Minimal cost-complexity pruning** (CART): $R_\alpha(T) = R(T) + \alpha\,|\text{leaves}(T)|$ with $R(T) = \sum_{\text{leaves}} \frac{n_t}{n} I(t)$. For each internal node the effective $\alpha$ is $g(t) = \frac{R(t) - R(T_t)}{|\text{leaves}(T_t)| - 1}$; prune the weakest link (smallest $g$) repeatedly while $g \le \alpha$. $\alpha$ chosen by CV (`ccp_alpha`).
- C4.5 pessimistic pruning uses an upper confidence bound of the error at each node.

## Other details

- Categorical splits: CART finds the best binary partition of levels ($2^{m-1}-1$ possibilities; for binary targets sorting levels by target rate gives the optimum in $O(m\log m)$). ID3/C4.5 use one branch per level.
- Missing values: C4.5 fractional instances; CART surrogate splits; modern implementations learn a default direction.
- Probabilities: leaf class frequencies (poorly calibrated; a pure leaf says 100 %).
- Feature importance: total impurity decrease attributable to each feature, normalised (biased towards high-cardinality / continuous features; see note 07 for permutation importance).
- Instability: a small data change can change the root split and the whole tree (high variance) — the motivation for ensembles.
- Oblique trees (linear combinations in tests) and model trees (regression in leaves) exist but are not standard.

## Worked example

Play-tennis style: 14 samples, 9 yes / 5 no. $H(\text{root}) = -\frac9{14}\log_2\frac9{14} - \frac5{14}\log_2\frac5{14} = 0.940$.
Split on *Outlook* (sunny 2+/3−, overcast 4+/0−, rain 3+/2−): $H = 0.971, 0, 0.971$, weighted $\frac5{14}0.971 + 0 + \frac5{14}0.971 = 0.694$, $IG = 0.246$. Split on *Wind* (weak 6+/2−, strong 3+/3−): $\frac8{14}0.811 + \frac6{14}\cdot 1 = 0.892$, $IG = 0.048$. *Humidity*: $IG = 0.151$, *Temperature*: $0.029$. Root = Outlook; the overcast branch is a pure leaf; recurse on sunny and rain. Gini version: $G(\text{root}) = 1 - (9/14)^2 - (5/14)^2 = 0.459$; after Outlook: $\frac5{14}0.48 + 0 + \frac5{14}0.48 = 0.343$, decrease 0.116; same choice.

Numeric split: values $x = [1, 2, 3, 4, 5, 6]$, labels $[A, A, A, B, B, A]$. Candidate thresholds 1.5, 2.5, ..., 5.5. At $t = 3.5$: left $3A/0B$ ($G = 0$), right $1A/2B$ ($G = 0.444$), weighted $0.222$; at $t = 5.5$: left $3A/2B$ ($0.48$), right pure, weighted $0.4$. Best: $3.5$.

## Pitfalls

- Reading "feature importance" as causal or as stable: it flips between correlated features.
- Unpruned trees on noisy data: 100 % training accuracy, poor generalisation.
- Trees extrapolate as constants: regression trees never predict outside the training range.
- Axis-parallel splits need many levels for a diagonal boundary that a linear model gets in one step.
- One-hot encoding a high-cardinality categorical dilutes it over many binary features; trees can take integer codes directly if the implementation supports categorical splits.
- Information gain favours attributes with many values; use gain ratio or binary splits.

## Exam-style questions

1. **Compute entropy and Gini for a node with 6 positives and 2 negatives.** $p = 0.75$: $H = -0.75\log_2 0.75 - 0.25\log_2 0.25 = 0.311 + 0.5 = 0.811$ bits; $G = 1 - 0.5625 - 0.0625 = 0.375$.
2. **Why is classification error not used as a splitting criterion?** It is piecewise linear, not strictly concave: a split that moves from $(4+, 4-)$ to children $(4+, 2-)$ and $(0+, 2-)$ leaves the error at $2/8$ unchanged although the children are purer; entropy and Gini decrease and reward it.
3. **Explain cost-complexity pruning and how $\alpha$ is chosen.** Minimise $R(T) + \alpha|T|$; for increasing $\alpha$ a nested sequence of subtrees is obtained by repeatedly collapsing the internal node with the smallest $g(t) = (R(t) - R(T_t))/(|T_t| - 1)$; $\alpha$ is picked by cross-validation of the pruned trees (or the 1-SE rule).
4. **Why does ID3 prefer attributes with many values, and what does C4.5 do?** Splitting into many small groups makes children purer merely by chance (an ID attribute gives pure singleton leaves and $IG = H(\text{parent})$). C4.5 divides by the split information (entropy of the branch sizes), giving the gain ratio; CART sidesteps it with binary splits.
5. **1000 observations, minimum 200 to split a node, minimum 300 per leaf: what is the maximum depth, not counting the root? Explain.** *(modelled on E21a, E21b, E21c, E22a — asked four times, so learn the argument, not the number.)* **2.** Make the tree maximally unbalanced. Root (1000) splits into 300 — a leaf, since it cannot be split without violating the 300-per-leaf minimum — and 700. The 700 node has $\ge 200$ so it may split: into 300 (leaf) and 400. The 400 node has $\ge 200$ observations, so the *split* constraint permits a split, but any split would produce a child with fewer than 300 observations, so the *leaf* constraint forbids it. Depth 2.
6. **With $k$ binary features and $k \gg N$ samples, how many leaves and what maximum depth are possible? And with $k$ continuous features?** *(modelled on E19a.)* Binary: at most $2^k$ leaves and depth $k$ if every feature is used once on a path — but with $k \gg N$ the real bound is $N$ leaves, since a leaf needs at least one sample, and the depth is bounded by $N$ too. Continuous: a feature can be split repeatedly at different thresholds, so depth is not bounded by $k$ — but again at most $N$ leaves and depth $\le N - 1$ [S12].
7. **Compute 1R for a small table and say how 1R relates to a decision tree.** *(modelled on E18a, E20b, E26a.)* For each attribute, predict the majority class of each of its values, count total training errors, pick the attribute with the fewest. 1R is a decision tree of depth 1 — a decision stump — with one branch per attribute value, so 1R is the first split a tree would make if error rate were the split criterion.
8. **Give two reasons trees are high-variance models and one way to reduce it.** *(ours.)* Greedy top-down search: a slightly different sample can change the root split and everything beneath; leaves near the bottom are fitted on few samples. Reduce by pruning / minimum leaf size, or by averaging many trees (bagging, random forests, note 07).

## Code

`src/py/rules.py`: `ZeroR`, `OneR` (with `rule_table_` — the per-attribute error
table a 1R question asks for), `Prism` (the covering algorithm),
`discretize_1r`.

`src/py/tree.py`: `entropy`, `gini`, `information_gain`, `DecisionTree(criterion=gini|entropy|mse, max_depth, min_samples_leaf, max_features, ccp_alpha)` with `fit(X, y, sample_weight)`, `predict`, `predict_proba`, `apply`, `feature_importances_`, `to_text`, `_prune` (weakest-link). Test checks that the pruned leaf count equals sklearn's for the same `ccp_alpha`.
