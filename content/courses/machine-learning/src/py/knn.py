"""k-nearest neighbours, brute force: classification (majority / distance-
weighted vote) and regression, with the distance metrics the course uses
(L1, L2, Lp, Chebyshev, cosine, Hamming, Mahalanobis) and k chosen by CV.
Lazy learner: fit() only stores the data.

Serves note 05 (kNN).  Cross-checked in test_knn.py against
sklearn.neighbors (identical probabilities).  Run `python knn.py` for the
moons demo.
"""
import numpy as np
from model_selection import BaseEstimator


def pairwise_distances(A, B, metric="euclidean", p=2):
    """Distance matrix D[i, j] = d(A[i], B[j]) for the metrics used in the course."""
    A, B = np.asarray(A, float), np.asarray(B, float)
    if metric == "euclidean":
        # ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a.b  (fast, but can go slightly negative)
        sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
        return np.sqrt(np.maximum(sq, 0))
    diff = A[:, None, :] - B[None, :, :]
    if metric == "manhattan":
        return np.abs(diff).sum(2)
    if metric == "chebyshev":
        return np.abs(diff).max(2)
    if metric == "minkowski":
        return (np.abs(diff) ** p).sum(2) ** (1 / p)
    if metric == "cosine":
        na, nb = np.linalg.norm(A, axis=1)[:, None], np.linalg.norm(B, axis=1)[None, :]
        return 1 - (A @ B.T) / (na * nb)
    if metric == "hamming":
        return (diff != 0).mean(2)
    raise ValueError(metric)


def mahalanobis(A, B, cov):
    """d(a,b) = sqrt((a-b)^T S^-1 (a-b)); accounts for feature correlation/scale."""
    L = np.linalg.cholesky(np.linalg.inv(cov))
    return pairwise_distances(np.asarray(A) @ L, np.asarray(B) @ L)


class KNNClassifier(BaseEstimator):
    def __init__(self, k=5, metric="euclidean", weights="uniform", p=2):
        self.k, self.metric, self.weights, self.p = k, metric, weights, p

    def fit(self, X, y):
        self.X_, y = np.asarray(X, float), np.asarray(y)
        self.classes_, self.y_ = np.unique(y, return_inverse=True)
        return self

    def _neighbours(self, X):
        D = pairwise_distances(X, self.X_, self.metric, self.p)
        idx = np.argpartition(D, self.k - 1, axis=1)[:, :self.k]       # k smallest, unordered
        return idx, np.take_along_axis(D, idx, 1)

    def predict_proba(self, X):
        idx, d = self._neighbours(X)
        w = 1.0 / np.maximum(d, 1e-12) if self.weights == "distance" else np.ones_like(d)
        P = np.zeros((len(idx), len(self.classes_)))
        for c in range(len(self.classes_)):
            P[:, c] = np.sum(w * (self.y_[idx] == c), 1)
        return P / P.sum(1, keepdims=True)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), 1)]


class KNNRegressor(BaseEstimator):
    def __init__(self, k=5, metric="euclidean", weights="uniform", p=2):
        self.k, self.metric, self.weights, self.p = k, metric, weights, p

    def fit(self, X, y):
        self.X_, self.y_ = np.asarray(X, float), np.asarray(y, float)
        return self

    def predict(self, X):
        D = pairwise_distances(X, self.X_, self.metric, self.p)
        idx = np.argpartition(D, self.k - 1, axis=1)[:, :self.k]
        d = np.take_along_axis(D, idx, 1)
        w = 1.0 / np.maximum(d, 1e-12) if self.weights == "distance" else np.ones_like(d)
        return np.sum(w * self.y_[idx], 1) / w.sum(1)


def choose_k_by_cv(X, y, ks=(1, 3, 5, 7, 11, 15, 21), folds=5, rng=0):
    """Pick k by stratified CV accuracy: small k = low bias/high variance, large k = the opposite."""
    from model_selection import cross_val_score
    from metrics import accuracy
    scores = {k: cross_val_score(KNNClassifier(k), X, y, accuracy, folds, rng=rng).mean() for k in ks}
    return max(scores, key=scores.get), scores


if __name__ == "__main__":
    from sklearn.datasets import make_moons
    from preprocessing import StandardScaler
    from model_selection import train_test_split
    from metrics import accuracy

    X, y = make_moons(400, noise=0.3, random_state=0)
    X = StandardScaler().fit_transform(X)
    Xtr, Xte, ytr, yte = train_test_split(X, y, 0.25, stratify=True, rng=0)
    for k in (1, 5, 25):
        for metric in ("euclidean", "manhattan"):
            acc = accuracy(yte, KNNClassifier(k, metric).fit(Xtr, ytr).predict(Xte))
            print(f"k={k:2d} {metric:10s} test acc {acc:.3f}")
    best, scores = choose_k_by_cv(Xtr, ytr)
    print("CV-chosen k =", best, {k: round(v, 3) for k, v in scores.items()})
    yr = np.sin(X[:, 0] * 2) + X[:, 1]
    print("regression MSE (k=5, distance weights): %.3f" %
          np.mean((KNNRegressor(5, weights="distance").fit(Xtr, yr[:len(Xtr)]).predict(Xte) - yr[len(Xtr):]) ** 2))
