"""Clustering from scratch: k-means (Lloyd iterations, k-means++ D^2 seeding),
agglomerative hierarchical clustering (single / complete / average / Ward via
the Lance-Williams update), DBSCAN [S41], and internal / external evaluation
(silhouette, Davies-Bouldin, adjusted Rand index, normalised mutual
information, purity).

Serves note 12 (unsupervised learning).  The archive examines this unit mostly
as recall, e.g. "PCA is not supervised" [S11].  Cross-checked in
test_clustering.py against sklearn.cluster (DBSCAN labels exact, k-means
inertia within 2 %) and sklearn.metrics (exact).

Run `python clustering.py` for the blobs / moons numbers quoted in note 12.
"""
import numpy as np
from knn import pairwise_distances


class KMeans:
    def __init__(self, k=3, n_init=5, max_iter=100, tol=1e-6, init="k-means++", rng=0):
        self.k, self.n_init, self.max_iter, self.tol, self.init, self.rng = k, n_init, max_iter, tol, init, rng

    def _init_centers(self, X, r):
        if self.init == "random":
            return X[r.choice(len(X), self.k, replace=False)]
        centers = [X[r.integers(len(X))]]                       # k-means++: D^2 sampling
        for _ in range(1, self.k):
            d2 = pairwise_distances(X, np.array(centers)).min(1) ** 2
            centers.append(X[r.choice(len(X), p=d2 / d2.sum())])
        return np.array(centers)

    def fit(self, X):
        X = np.asarray(X, float)
        r = np.random.default_rng(self.rng)
        best = (np.inf, None, None)
        for _ in range(self.n_init):
            C = self._init_centers(X, r)
            for _ in range(self.max_iter):
                labels = pairwise_distances(X, C).argmin(1)     # assignment step
                C_new = np.array([X[labels == j].mean(0) if np.any(labels == j) else C[j] for j in range(self.k)])
                shift = np.linalg.norm(C_new - C); C = C_new     # update step
                if shift < self.tol:
                    break
            inertia = np.sum((X - C[labels]) ** 2)
            if inertia < best[0]:
                best = (inertia, C, labels)
        self.inertia_, self.cluster_centers_, self.labels_ = best
        return self

    def predict(self, X):
        return pairwise_distances(X, self.cluster_centers_).argmin(1)


def elbow(X, ks=range(1, 10), rng=0):
    return {k: KMeans(k, rng=rng).fit(X).inertia_ for k in ks}


class Agglomerative:
    """Bottom-up merging with Lance-Williams updates of the cluster distance matrix.
    linkage: 'single' (min), 'complete' (max), 'average', 'ward' (increase in within-cluster SSE)."""

    def __init__(self, k=2, linkage="average"):
        self.k, self.linkage = k, linkage

    def fit(self, X):
        X = np.asarray(X, float)
        n = len(X)
        D = pairwise_distances(X, X)
        if self.linkage == "ward":
            D = D ** 2                                          # work with squared distances
        np.fill_diagonal(D, np.inf)
        size = np.ones(n)
        active = np.ones(n, bool)
        labels = np.arange(n)
        self.merges_ = []
        for _ in range(n - self.k):
            i, j = np.unravel_index(np.argmin(D), D.shape)      # closest pair of clusters
            self.merges_.append((i, j, D[i, j]))
            for m in np.where(active)[0]:                        # Lance-Williams update of d(i+j, m)
                if m in (i, j):
                    continue
                if self.linkage == "single":
                    d = min(D[i, m], D[j, m])
                elif self.linkage == "complete":
                    d = max(D[i, m], D[j, m])
                elif self.linkage == "average":
                    d = (size[i] * D[i, m] + size[j] * D[j, m]) / (size[i] + size[j])
                else:  # ward
                    ni, nj, nm = size[i], size[j], size[m]
                    d = ((ni + nm) * D[i, m] + (nj + nm) * D[j, m] - nm * D[i, j]) / (ni + nj + nm)
                D[i, m] = D[m, i] = d
            size[i] += size[j]; active[j] = False
            D[j, :] = D[:, j] = np.inf
            labels[labels == j] = i
        self.labels_ = np.unique(labels, return_inverse=True)[1]
        return self


class DBSCAN:
    """Core point: >= min_samples points within eps (itself included). Clusters = connected
    components of core points via eps-reachability; border points join a neighbouring core; rest is noise (-1)."""

    def __init__(self, eps=0.5, min_samples=5):
        self.eps, self.min_samples = eps, min_samples

    def fit(self, X):
        X = np.asarray(X, float)
        n = len(X)
        D = pairwise_distances(X, X)
        neigh = [np.where(D[i] <= self.eps)[0] for i in range(n)]
        core = np.array([len(nb) >= self.min_samples for nb in neigh])
        labels = np.full(n, -1)
        c = 0
        for i in range(n):
            if labels[i] != -1 or not core[i]:
                continue
            labels[i] = c
            stack = list(neigh[i])
            while stack:                                          # expand the cluster from core points
                j = stack.pop()
                if labels[j] == -1:
                    labels[j] = c
                    if core[j]:
                        stack.extend(neigh[j])
            c += 1
        self.labels_, self.core_ = labels, core
        return self


# ----------------------------------------------------------------- evaluation
def silhouette_score(X, labels):
    """s_i = (b_i - a_i) / max(a_i, b_i): a = mean intra-cluster distance, b = mean distance to nearest other cluster."""
    X, labels = np.asarray(X, float), np.asarray(labels)
    D = pairwise_distances(X, X)
    ks = np.unique(labels)
    s = np.zeros(len(X))
    for i in range(len(X)):
        own = labels == i * 0 + labels[i]
        if own.sum() == 1:
            continue
        a = D[i, own].sum() / (own.sum() - 1)
        b = min(D[i, labels == k].mean() for k in ks if k != labels[i])
        s[i] = (b - a) / max(a, b)
    return float(s.mean())


def davies_bouldin(X, labels):
    """Mean over clusters of max_j (s_i + s_j) / d(c_i, c_j); lower is better."""
    X, labels = np.asarray(X, float), np.asarray(labels)
    ks = np.unique(labels)
    C = np.array([X[labels == k].mean(0) for k in ks])
    s = np.array([np.linalg.norm(X[labels == k] - C[i], axis=1).mean() for i, k in enumerate(ks)])
    Dc = pairwise_distances(C, C); np.fill_diagonal(Dc, np.inf)
    R = (s[:, None] + s[None, :]) / Dc
    return float(np.max(R, 1).mean())


def contingency(a, b):
    ua, ia = np.unique(a, return_inverse=True); ub, ib = np.unique(b, return_inverse=True)
    M = np.zeros((len(ua), len(ub)), int)
    np.add.at(M, (ia, ib), 1)
    return M


def adjusted_rand_index(a, b):
    """ARI = (RI - E[RI]) / (max RI - E[RI]) using pair counts from the contingency table."""
    M = contingency(a, b)
    comb2 = lambda x: x * (x - 1) / 2
    sum_ij, sum_a, sum_b, n = comb2(M).sum(), comb2(M.sum(1)).sum(), comb2(M.sum(0)).sum(), comb2(M.sum())
    expected = sum_a * sum_b / n
    return float((sum_ij - expected) / (0.5 * (sum_a + sum_b) - expected))


def normalized_mutual_info(a, b):
    """NMI = I(a;b) / mean(H(a), H(b))  (sklearn's arithmetic default)."""
    M = contingency(a, b) / len(a)
    pa, pb = M.sum(1, keepdims=True), M.sum(0, keepdims=True)
    nz = M > 0
    I = np.sum(M[nz] * np.log(M[nz] / (pa @ pb)[nz]))
    H = lambda p: -np.sum(p[p > 0] * np.log(p[p > 0]))
    return float(I / (0.5 * (H(pa) + H(pb))))


def purity(labels, truth):
    M = contingency(labels, truth)
    return float(M.max(1).sum() / M.sum())


if __name__ == "__main__":
    from sklearn.datasets import make_blobs, make_moons

    X, y = make_blobs(300, centers=4, cluster_std=0.9, random_state=1)
    km = KMeans(4).fit(X)
    print("k-means: inertia %.1f  ARI %.3f  silhouette %.3f  DB %.3f" %
          (km.inertia_, adjusted_rand_index(y, km.labels_), silhouette_score(X, km.labels_), davies_bouldin(X, km.labels_)))
    print("elbow:", {k: round(v) for k, v in elbow(X, range(1, 8)).items()})
    for link in ("single", "complete", "average", "ward"):
        ag = Agglomerative(4, link).fit(X)
        print(f"agglomerative {link:8s}: ARI {adjusted_rand_index(y, ag.labels_):.3f}  NMI {normalized_mutual_info(y, ag.labels_):.3f}")
    Xm, ym = make_moons(300, noise=0.08, random_state=0)
    db = DBSCAN(0.2, 5).fit(Xm)
    print("DBSCAN on moons: clusters %d, noise %d, ARI %.3f  (k-means ARI %.3f)" %
          (db.labels_.max() + 1, np.sum(db.labels_ == -1), adjusted_rand_index(ym, db.labels_), adjusted_rand_index(ym, KMeans(2).fit(Xm).labels_)))
