# 12 Unsupervised learning: clustering and PCA

> Named in the TISS subject line [S1]; not a separate unit in [S18]. Exam weight ● — in 184.702 clustering and PCA appear almost only as true/false items. They are examined properly in the *sibling* course 192.183 [S4, S16]. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## What it is

No targets. Find structure: groups (clustering), low-dimensional coordinates (dimensionality reduction), density / outliers. Evaluation is harder because there is no ground truth; the choice of similarity measure *is* the modelling decision. Scale features first (all methods below are distance- or variance-based).

## k-means

Partition into $k$ clusters minimising the within-cluster sum of squares (inertia) [S28 ch. 12]
$$J = \sum_{j=1}^k \sum_{x_i \in C_j}\|x_i - \mu_j\|^2 .$$
Lloyd's algorithm: (1) assign each point to the nearest centroid, (2) recompute centroids as cluster means; repeat. Each step does not increase $J$, so it converges (to a local minimum) in finitely many steps; $O(nkd)$ per iteration. Initialisation matters: **k-means++** picks the next seed with probability $\propto D(x)^2$ (distance to the nearest chosen seed), giving an $O(\log k)$-competitive expected solution; run several inits and keep the lowest $J$. Choosing $k$: elbow of $J(k)$ (always decreasing; look for the knee), silhouette, gap statistic, domain knowledge. Assumes convex, isotropic, similar-sized clusters; fails on elongated / nested shapes; sensitive to outliers (k-medoids / PAM uses medoids, k-medians the $L_1$). Gaussian mixture models with EM are the soft, anisotropic generalisation; k-means is EM with hard assignments and spherical unit covariances.

## Hierarchical clustering

Agglomerative (bottom-up): start with $n$ singletons, repeatedly merge the two closest clusters, record the merge distance → **dendrogram**; cut at a height (or at $k$ clusters). Linkage = inter-cluster distance:

| linkage | $d(A, B)$ | behaviour |
|---|---|---|
| single | $\min_{a \in A, b \in B} d(a, b)$ | chains through bridges; finds elongated clusters; = MST |
| complete | $\max d(a, b)$ | compact, similar-diameter clusters; sensitive to outliers |
| average (UPGMA) | mean $d(a, b)$ | compromise |
| Ward | increase in total within-cluster SSE $= \frac{|A||B|}{|A| + |B|}\|\mu_A - \mu_B\|^2$ | k-means-like compact clusters; most used |

Lance–Williams gives the updated distance after merging $A, B$ from $d(A, C), d(B, C), d(A, B)$ without recomputation (`clustering.Agglomerative`). Complexity $O(n^2\log n)$ time, $O(n^2)$ memory: fine to $\sim 10^4$ points. Divisive (top-down) is rarer. No need to fix $k$ in advance; deterministic; the dendrogram is interpretable.

## DBSCAN

Density-based [S41]: parameters $\varepsilon$ and `min_samples`. A **core point** has $\ge$ `min_samples` points within $\varepsilon$ (itself included); a **border point** is within $\varepsilon$ of a core point but not core; the rest is **noise** (label $-1$). Clusters = connected components of core points under "within $\varepsilon$", plus their border points. Finds arbitrarily shaped clusters, handles noise, no $k$; struggles with varying densities (a single $\varepsilon$) and high dimensions. Choose $\varepsilon$ from the knee of the sorted $k$-distance plot ($k$ = `min_samples`). Border points can be reachable from two clusters (assignment order-dependent). OPTICS and HDBSCAN relax the single-$\varepsilon$ limitation.

## Evaluating clusterings

Internal (no labels):
- **Silhouette** $s_i = \frac{b_i - a_i}{\max(a_i, b_i)} \in [-1, 1]$, $a_i$ = mean distance to own cluster, $b_i$ = mean distance to the nearest other cluster; average over points; $\approx 1$ tight and separated, $< 0$ probably misassigned. $O(n^2)$; favours convex clusters.
- **Davies–Bouldin** $\frac1k\sum_i \max_{j \ne i}\frac{s_i + s_j}{d(\mu_i, \mu_j)}$ (scatter over separation), lower is better; **Calinski–Harabasz** $\frac{\text{between-SS}/(k-1)}{\text{within-SS}/(n-k)}$, higher is better; inertia (only comparable at fixed $k$).

External (labels available, for benchmarking; labels are invariant to permutation):
- **Rand index** = fraction of pairs on which the two partitions agree; **adjusted Rand (ARI)** corrects for chance: $\frac{RI - \mathbb E[RI]}{\max RI - \mathbb E[RI]}$, 0 for random, 1 for identical.
- **(Normalised) mutual information** $\text{NMI} = \frac{I(U; V)}{\tfrac12(H(U) + H(V))}$; adjusted MI corrects for chance.
- **Purity** $\frac1n\sum_j \max_c |C_j \cap L_c|$: rises trivially with $k$; homogeneity/completeness/V-measure are the entropy-based pair.

## PCA

Find orthonormal directions of maximal variance. Centre $X$ ($n \times d$), covariance $S = \frac{1}{n-1}X^\top X$. The first component $v_1 = \operatorname{argmax}_{\|v\| = 1} v^\top S v$ is the top eigenvector (Lagrangian $v^\top S v - \lambda(v^\top v - 1) \Rightarrow Sv = \lambda v$); subsequent ones are the next eigenvectors, orthogonal. Equivalent: SVD $X = U\Sigma V^\top$, components = columns of $V$, eigenvalues $\lambda_j = \sigma_j^2/(n-1)$, scores $Z = XV = U\Sigma$. **Explained variance ratio** $\lambda_j / \sum_k\lambda_k$; keep $m$ components for 90–99 % or by the scree plot's elbow. Projection $Z_m = X V_m$, reconstruction $\hat X = Z_m V_m^\top$, error $\|X - \hat X\|_F^2 = (n-1)\sum_{j > m}\lambda_j$: PCA is also the optimal linear least-squares reconstruction (Eckart–Young). **Whitening**: $Z_m\Lambda_m^{-1/2}$ has identity covariance. Uses: decorrelation and noise reduction before kNN/SVM/regression, visualisation (2-d), compression, collinearity removal. Signs of components are arbitrary. Standardise first unless the features share units, otherwise PCA finds the largest-unit feature. Nonlinear relatives: kernel PCA, t-SNE / UMAP (visualisation only, not for downstream metrics), autoencoders.

## Worked example

k-means, 1-d: points $\{1, 2, 3, 10, 11, 12\}$, $k = 2$, init centroids $1$ and $2$ (a poor init, both in one true cluster). Assign: $\{1\}, \{2, 3, 10, 11, 12\}$ → centroids $1, 7.6$. Assign: $\{1, 2, 3\}, \{10, 11, 12\}$ → centroids $2, 11$; stable. $J = 2 + 2 = 4$. Here even the poor init recovers, but in 2-d bad inits regularly split one true cluster and merge two others; k-means++ ($D^2$ sampling would almost surely pick a second seed from the far group) avoids most of that.

Silhouette for point $x = 3$ above: $a = (2 + 1)/2 = 1.5$, $b = (7 + 8 + 9)/3 = 8$, $s = (8 - 1.5)/8 = 0.81$.

`clustering.py` `__main__`: four Gaussian blobs: k-means ARI 0.97, silhouette 0.66; single linkage ARI 0.33 (chaining), complete/average/Ward 0.96; two moons: DBSCAN($\varepsilon = 0.2$, 5) ARI 0.99 with 1 noise point vs k-means 0.23 (non-convex clusters).

PCA on iris (4 features): eigenvalues $4.23, 0.24, 0.08, 0.02$; the first component explains 92.5 %, two explain 97.8 % (`test_pca.py`).

## Pitfalls

- Not scaling before k-means/DBSCAN/PCA.
- Trusting the elbow; it is often absent. Combine with silhouette and domain sense.
- k-means on non-convex or unequal-density clusters; single linkage on noisy data (chaining).
- Using purity to choose $k$ (monotone in $k$); comparing inertia across different $k$.
- PCA on unstandardised mixed-unit features; interpreting components causally; using t-SNE distances quantitatively.
- Fitting PCA / clustering on train+test and then training a classifier on the components (leak of test distribution: mild but real; fit on train).

## Exam-style questions

1. **Show that Lloyd's algorithm converges.** Both steps minimise $J$ over one block of variables with the other fixed (assignment: nearest centroid minimises each term; update: the mean minimises $\sum\|x - \mu\|^2$), so $J$ is non-increasing; there are finitely many partitions, so the algorithm stops. It stops at a local minimum, not necessarily the global one.
2. **Compare k-means, agglomerative (Ward) and DBSCAN on: need for $k$, cluster shape, noise handling, complexity.** k-means: $k$ needed / convex / none / $O(nkd)$ per iteration. Ward: cut the dendrogram / compact / none / $O(n^2\log n)$. DBSCAN: no $k$ ($\varepsilon$, min_samples) / arbitrary / explicit noise label / $O(n\log n)$ with an index, $O(n^2)$ brute force.
3. **Define the silhouette coefficient and its range; what does a negative value mean?** $s_i = (b_i - a_i)/\max(a_i, b_i)$ with $a_i$ the mean intra-cluster distance and $b_i$ the smallest mean distance to another cluster; $s_i \in [-1, 1]$; negative means the point is on average closer to another cluster than to its own.
4. **Derive that the first principal component is the top eigenvector of the covariance matrix.** Maximise $v^\top Sv$ subject to $v^\top v = 1$: $\nabla_v[v^\top Sv - \lambda(v^\top v - 1)] = 2Sv - 2\lambda v = 0 \Rightarrow Sv = \lambda v$, and the objective equals $\lambda$, so the largest eigenvalue's eigenvector wins; the variance captured is $\lambda_1$.
5. **"PCA is a supervised feature-selection method." True or false?** *(E17b, E22a — the only PCA question the 184.702 archive contains.)* **False twice over.** PCA never looks at the target, so it is unsupervised; and it *extracts* new features — linear combinations of the originals, ordered by variance — rather than *selecting* a subset of the originals. [S43] states the contrast the course wants: "PCA combines similar (correlated) attributes and creates new ones … feature selection doesn't combine attributes, it just evaluates their quality and selects the best set." The cost is interpretability, which is why the two are sometimes combined (PCA first, then selection).
6. **Which quantity does $k$-means minimise, and which matrix does PCA need the eigenvectors of?** *(modelled on [S16], the sibling course's 2026S paper — not seen in a 184.702 paper, included because the two courses share a lecturer and a syllabus.)* $k$-means minimises the **sum of squared distances from each point to its assigned centroid** (not the distance between centroids, not the total variance). For a data matrix $X$ of shape $(B, d)$, PCA needs the eigenvectors of $X^\top X$ — the $d\times d$ covariance (up to a factor $1/(n-1)$ on centred data) — not of $XX^\top$.
7. **Why is ARI preferred over the Rand index, and over purity?** *(ours.)* Random partitions already get a high Rand index (most pairs are "different cluster" in both); ARI subtracts the expected value under random labelling so 0 = chance. Purity can be driven to 1 by using $n$ singleton clusters; ARI and NMI penalise over-splitting.

## Code

`src/py/clustering.py`: `KMeans(init="k-means++", n_init)`, `elbow`, `Agglomerative(linkage=single|complete|average|ward)` (Lance–Williams), `DBSCAN`, `silhouette_score`, `davies_bouldin`, `adjusted_rand_index`, `normalized_mutual_info`, `purity`. `src/py/pca.py`: `PCA(n_components=int|fraction, whiten)` via SVD with `explained_variance_ratio_`, `inverse_transform`, `reconstruction_error`; `pca_eig` via the covariance eigenproblem. Tests match sklearn (DBSCAN labels exactly; PCA up to sign).
