"""Principal component analysis from scratch via the SVD of the centred data
matrix (equivalently the eigen-decomposition of the covariance), with
explained variance, projection / reconstruction, whitening and a choice of the
number of components by retained variance.

Serves note 12 (unsupervised learning).  Cross-checked in test_pca.py against
sklearn.decomposition.PCA (exact up to sign; iris eigenvalues quoted in note
12).  Run `python pca.py` for the demo.
"""
import numpy as np


class PCA:
    def __init__(self, n_components=None, whiten=False):
        self.n_components, self.whiten = n_components, whiten

    def fit(self, X):
        X = np.asarray(X, float)
        self.mean_ = X.mean(0)
        Xc = X - self.mean_
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)      # Xc = U S V^T; columns of V = principal axes
        # sign convention: largest-|entry| of each component positive (sklearn's svd_flip on V)
        signs = np.sign(Vt[np.arange(len(Vt)), np.abs(Vt).argmax(1)])
        Vt, U = Vt * signs[:, None], U * signs[None, :]
        var = S ** 2 / (len(X) - 1)                              # eigenvalues of the covariance
        k = self.n_components or len(S)
        if isinstance(k, float) and k < 1:                       # keep enough for this fraction of variance
            k = int(np.searchsorted(np.cumsum(var) / var.sum(), k) + 1)
        self.components_, self.singular_values_ = Vt[:k], S[:k]
        self.explained_variance_ = var[:k]
        self.explained_variance_ratio_ = var[:k] / var.sum()
        self.n_components_ = k
        return self

    def transform(self, X):
        Z = (np.asarray(X, float) - self.mean_) @ self.components_.T
        return Z / np.sqrt(self.explained_variance_) if self.whiten else Z

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def inverse_transform(self, Z):
        Z = np.asarray(Z, float)
        if self.whiten:
            Z = Z * np.sqrt(self.explained_variance_)
        return Z @ self.components_ + self.mean_

    def reconstruction_error(self, X):
        """Mean squared distance between X and its projection = sum of the dropped eigenvalues (up to n/(n-1))."""
        return float(np.mean(np.sum((np.asarray(X, float) - self.inverse_transform(self.transform(X))) ** 2, 1)))


def pca_eig(X, k):
    """Same thing via the covariance eigenproblem (for the derivation in the notes)."""
    Xc = np.asarray(X, float) - np.mean(X, 0)
    cov = Xc.T @ Xc / (len(Xc) - 1)
    lam, V = np.linalg.eigh(cov)
    order = np.argsort(lam)[::-1]
    return lam[order][:k], V[:, order][:, :k].T


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    # 3-d data living mostly on a 2-d plane
    latent = rng.normal(size=(300, 2)) * [3, 1]
    A = np.array([[1, 0.5, 0.2], [0.3, 1, -0.4]])
    X = latent @ A + rng.normal(0, 0.1, (300, 3)) + [5, -2, 1]
    p = PCA().fit(X)
    print("explained variance ratio", p.explained_variance_ratio_.round(4))
    p2 = PCA(0.95).fit(X)
    print("components for 95% variance:", p2.n_components_, " reconstruction MSE %.4f" % p2.reconstruction_error(X))
    lam, V = pca_eig(X, 2)
    print("eigen route: eigenvalues", lam.round(3), " |cos| between axes", np.abs(np.sum(V * p.components_[:2], 1)).round(4))
    Zw = PCA(2, whiten=True).fit_transform(X)
    print("whitened covariance\n", np.cov(Zw, rowvar=False).round(3))
