# 06 Unsupervised learning and clustering

TISS topic 6, "Unsupervised learning, clustering" [S2]; 2021S videos Learning 6,
"Clustering with k-Means"; exercise 10 (k-means on Ising observables) [S5, S11].
Texts: [S6 sec. XIII, XIV.B], [S7 ch. 11], [S8 sec. 8.5, 14.3.6-14.3.7], [S9 sec. 12.4].
Hierarchical clustering, DBSCAN, cluster validity indices:
[CSE note 12](../../machine-learning/notes/12-unsupervised.md).

## Definitions

- **Unsupervised learning:** only $\{x_n\}$, no labels; find structure: clusters,
  low-dimensional manifolds (note 07), densities.
- **k-means objective (inertia):** $J(\mu,c)=\sum_n\|x_n-\mu_{c(n)}\|^2$ with
  assignments $c(n)\in\{1..k\}$ and centres $\mu_j$.
- **Lloyd's algorithm** [S33]: alternate (A) $c(n)=\arg\min_j\|x_n-\mu_j\|^2$,
  (U) $\mu_j=$ mean of $\{x_n:c(n)=j\}$. **k-means++**: seed centres with
  probability $\propto D(x)^2$, the squared distance to the nearest chosen centre.
- **Gaussian mixture model (GMM):** $p(x)=\sum_j\pi_j\,\mathcal N(x|\mu_j,\Sigma_j)$,
  latent label $z\in\{1..k\}$, $p(z=j)=\pi_j$.
- **Responsibility:** $r_{nj}=p(z_n=j|x_n)=\pi_j\mathcal N(x_n|\mu_j,\Sigma_j)/\sum_i\pi_i\mathcal N(x_n|\mu_i,\Sigma_i)$.

## Derivations

**Lloyd decreases $J$ monotonically.** (A) minimises $J$ over $c$ for fixed $\mu$
pointwise. (U): $\partial_{\mu_j}\sum_{c(n)=j}\|x_n-\mu_j\|^2=0\Rightarrow\mu_j=\bar x_j$,
the minimiser over $\mu$ for fixed $c$. Both steps are non-increasing and there
are finitely many partitions, so the algorithm terminates, at a **local** minimum
(NP-hard globally). Restarts (`n_init`) and k-means++ mitigate.

**EM for the GMM** [S32, S7 sec. 11.3]. For any distribution $q_n(z)$, Jensen:

$$\log p(x_n)=\log\sum_zq_n(z)\frac{p(x_n,z)}{q_n(z)}\ge\sum_zq_n(z)\log\frac{p(x_n,z)}{q_n(z)}=:\mathcal L_n(q,\theta),$$

with equality iff $q_n(z)=p(z|x_n)$. **E step:** set $q=r$ (bound becomes tight).
**M step:** maximise $\sum_n\sum_jr_{nj}\log[\pi_j\mathcal N(x_n|\mu_j,\Sigma_j)]$:

$$N_j=\sum_nr_{nj},\quad\pi_j=\frac{N_j}N,\quad\mu_j=\frac1{N_j}\sum_nr_{nj}x_n,\quad\Sigma_j=\frac1{N_j}\sum_nr_{nj}(x_n-\mu_j)(x_n-\mu_j)^T .$$

Log-likelihood never decreases: $\log p(\theta^{t+1})\ge\mathcal L(r^t,\theta^{t+1})\ge\mathcal L(r^t,\theta^t)=\log p(\theta^t)$.
Physics reading: $\mathcal L=-(\text{energy})+\text{entropy}$ of $q$, a free energy;
EM is coordinate ascent on it, like variational mean-field theory [S6 sec. XIV].

**k-means as a limit.** $\Sigma_j=\varepsilon\mathbb 1$, $\pi_j$ equal,
$\varepsilon\to0$: $r_{nj}\to$ one-hot on the nearest centre ("zero-temperature" EM), so
k-means is hard-assignment EM with isotropic equal clusters [S8 sec. 14.3.7]. Hence
k-means assumes roughly spherical, equally sized clusters; GMM with full
$\Sigma_j$ does not.

**Choosing $k$.** Optimal $J(k)$ is non-increasing in $k$ ($J=0$ at $k=N$): look for an
elbow, use the GMM likelihood with a penalty (BIC $=-2\log L+p\log N$), or
silhouette scores. Physics: let the known symmetry and phases suggest $k$
(exercise 10 [S5]).

**Singularities.** GMM likelihood is unbounded: a component collapsing on one
point with $\Sigma\to0$ gives $\log L\to\infty$. Add $\epsilon\mathbb 1$ to $\Sigma_j$
(`reg=1e-6`, sklearn's `reg_covar`).

## Exercise 10 [S5]

Clusters Ising snapshots by hand-made order parameters with k-means; it is a
graded exercise and is not solved here. General lesson: encode known
symmetries in the features before clustering. Ising background: note 10.

## Worked example (`src/py/clustering_pca.py`, seed 4711)

Three unit Gaussians at $(0,0),(5,0),(2.5,4)$, 200 each; best of 5 k-means++ runs:

| $k$ | 1 | 2 | 3 | 4 | 6 |
|---|---|---|---|---|---|
| $J$ | 5852 | 3405 | **1135** | 973 | 721 |

Elbow at $k=3$ (drop 2270, then 162). Two elongated clusters,
$\mathrm{std}=(3,0.3)$, centres $2$ apart along the short axis: k-means agreement
with the truth $0.505$ (it cuts along the long axis, which lowers $J$), GMM with
full covariance $0.998$ after 164 EM steps.

## Pitfalls

- Feature scaling changes k-means results (Euclidean distance).
- Cluster labels are arbitrary: compare by best permutation, not by index.
- k-means always returns $k$ clusters, even for structureless data.
- Initialisation dependence: always several restarts.
- EM converges to a local maximum; initialise from k-means.

## Test-style questions

**Q1.** Prove Lloyd's algorithm terminates.
**A.** Both steps are exact minimisations of $J$ in one block of variables, so
$J$ is non-increasing; $J$ takes finitely many values (one per partition) and
ties are broken consistently, so it stops after finitely many steps.

**Q2.** Do one k-means step by hand: points $0,1,4,5$ on a line, centres $0,1$.
**A.** Assign: $0\to0$; $1,4,5\to1$. Update: $\mu=(0,\ 10/3)$. Assign: $0,1\to0$;
$4,5\to10/3$. Update: $\mu=(0.5,4.5)$. Converged, $J=4\cdot0.25=1$.

**Q3.** Derive the M-step update for $\mu_j$.
**A.** $\partial_{\mu_j}\sum_nr_{nj}\big(-\frac12(x_n-\mu_j)^T\Sigma_j^{-1}(x_n-\mu_j)\big)=\Sigma_j^{-1}\sum_nr_{nj}(x_n-\mu_j)=0$
$\Rightarrow\mu_j=\sum_nr_{nj}x_n/N_j$.

**Q4.** In what limit is k-means the GMM, and what does that imply?
**A.** Equal weights, isotropic $\Sigma=\varepsilon\mathbb 1$, $\varepsilon\to0$. So
k-means fails on elongated or unequal-size clusters (our example: 0.505 vs 0.998).

**Q5.** Why cluster Ising configurations on $(|m|,|m'|)$ rather than $(m,m')$?
**A.** $H$ is invariant under $\sigma\to-\sigma$; $\pm m$ states are one phase.
Clustering on $m$ splits the ordered phase in two; $|m|$ quotients out the symmetry.

## Code

`src/py/clustering_pca.py`: `kmeans_pp_init`, `kmeans` (Lloyd, `n_init`,
inertia history; equals `sklearn.cluster.KMeans` from the same init), `gmm_em`
(full covariance, log-space E step, monotone log-likelihood; matches
`sklearn.mixture.GaussianMixture.score` to $10^{-3}$), `three_blobs`.
