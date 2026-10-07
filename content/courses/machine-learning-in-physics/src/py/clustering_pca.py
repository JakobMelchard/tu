"""k-means, Gaussian mixtures by EM, PCA and truncated SVD, from scratch.

Notes 06 and 07.
  k-means (Lloyd [S33]): minimise J = sum_n ||x_n - mu_{c(n)}||^2 by alternating
      assignment c(n) = argmin_k ||x_n - mu_k||, update mu_k = mean of cluster k.
      Each half-step cannot increase J, so J converges (to a local minimum).
  GMM by EM [S32, S7 ch. 11]: responsibilities r_nk = pi_k N(x_n|mu_k,S_k) / sum_j (...),
      then N_k = sum_n r_nk, mu_k = sum r x / N_k, S_k = sum r (x-mu)(x-mu)^T / N_k,
      pi_k = N_k / N. The log-likelihood is non-decreasing.
  PCA [S7 ch. 10]: centred X = U S V^T, principal axes = rows of V^T, scores = U S,
      explained variance lambda_k = s_k^2 / (N - 1). Eckart-Young [S29]:
      ||X - X_r||_F^2 = sum_{k >= r} s_k^2 is the minimum over all rank-r matrices.
"""
from __future__ import annotations

import numpy as np


def kmeans_pp_init(X, k, rng):
    """k-means++ seeding: next centre drawn with probability ~ D(x)^2."""
    C = [X[rng.integers(X.shape[0])]]
    for _ in range(1, k):
        d2 = np.min(((X[:, None, :] - np.array(C)[None]) ** 2).sum(-1), axis=1)
        C.append(X[rng.choice(X.shape[0], p=d2 / d2.sum())])
    return np.array(C)


def kmeans(X, k, rng=None, init=None, max_iter=300, n_init=1):
    """Lloyd's algorithm. Returns (centres, labels, inertia, inertia history of best run)."""
    rng = np.random.default_rng(0) if rng is None else rng
    best = None
    for _ in range(n_init):
        C = kmeans_pp_init(X, k, rng) if init is None else np.array(init, float)
        hist = []
        for _ in range(max_iter):
            d2 = ((X[:, None, :] - C[None]) ** 2).sum(-1)
            lab = np.argmin(d2, axis=1)
            hist.append(float(d2[np.arange(X.shape[0]), lab].sum()))
            newC = np.array([X[lab == j].mean(0) if np.any(lab == j) else C[j] for j in range(k)])
            if np.allclose(newC, C):
                break
            C = newC
        d2 = ((X[:, None, :] - C[None]) ** 2).sum(-1)
        lab = np.argmin(d2, axis=1)
        J = float(d2[np.arange(X.shape[0]), lab].sum())
        if best is None or J < best[2]:
            best = (C, lab, J, hist)
    return best


def _log_gauss(X, mu, S):
    d = X.shape[1]
    L = np.linalg.cholesky(S)
    z = np.linalg.solve(L, (X - mu).T)
    return -0.5 * (z * z).sum(0) - np.log(np.diag(L)).sum() - 0.5 * d * np.log(2 * np.pi)


def gmm_em(X, k, rng=None, max_iter=200, tol=1e-8, reg=1e-6):
    """Full-covariance GMM, initialised from k-means. Returns (pi, mu, S, resp, loglik history)."""
    rng = np.random.default_rng(0) if rng is None else rng
    N, d = X.shape
    mu, lab, _, _ = kmeans(X, k, rng)
    S = np.array([np.cov(X[lab == j].T) + reg * np.eye(d) for j in range(k)])
    pi = np.bincount(lab, minlength=k) / N
    hist = []
    for _ in range(max_iter):
        # E step in log space
        lp = np.stack([np.log(pi[j]) + _log_gauss(X, mu[j], S[j]) for j in range(k)], axis=1)
        m = lp.max(1, keepdims=True)
        lse = m[:, 0] + np.log(np.exp(lp - m).sum(1))
        hist.append(float(lse.sum()))
        R = np.exp(lp - lse[:, None])
        # M step
        Nk = R.sum(0)
        pi = Nk / N
        mu = (R.T @ X) / Nk[:, None]
        S = np.array([((R[:, j, None] * (X - mu[j])).T @ (X - mu[j])) / Nk[j] + reg * np.eye(d)
                      for j in range(k)])
        if len(hist) > 1 and hist[-1] - hist[-2] < tol * abs(hist[-1]):
            break
    return pi, mu, S, R, hist


def pca(X, r=None):
    """Returns (mean, components (r x d), explained variance, scores)."""
    mean = X.mean(0)
    U, s, VT = np.linalg.svd(X - mean, full_matrices=False)
    r = s.size if r is None else r
    return mean, VT[:r], s[:r] ** 2 / (X.shape[0] - 1), U[:, :r] * s[:r]


def pca_eig(X, r):
    """Same via the covariance eigendecomposition (squares the condition number)."""
    Xc = X - X.mean(0)
    lam, V = np.linalg.eigh(Xc.T @ Xc / (X.shape[0] - 1))
    order = np.argsort(lam)[::-1][:r]
    return V[:, order].T, lam[order]


def explained_variance_ratio(X):
    s = np.linalg.svd(X - X.mean(0), compute_uv=False)
    return s**2 / np.sum(s**2)


def truncated_svd(X, r):
    """Best rank-r approximation (no centring) and its relative Frobenius error from s alone."""
    U, s, VT = np.linalg.svd(X, full_matrices=False)
    Xr = (U[:, :r] * s[:r]) @ VT[:r]
    return Xr, float(np.sqrt(np.sum(s[r:] ** 2) / np.sum(s**2)))


def subspace_distance(A, B):
    """sin of the largest principal angle between row spaces of A and B."""
    Qa = np.linalg.qr(A.T)[0]
    Qb = np.linalg.qr(B.T)[0]
    c = np.linalg.svd(Qa.T @ Qb, compute_uv=False)
    return float(np.sqrt(max(0.0, 1.0 - c.min() ** 2)))


def three_blobs(rng, n=200):
    centres = np.array([[0, 0], [5, 0], [2.5, 4]])
    return np.vstack([rng.normal(size=(n, 2)) + c for c in centres]), np.repeat(np.arange(3), n)


def _demo() -> None:
    rng = np.random.default_rng(4711)
    X, y = three_blobs(rng)
    for k in [1, 2, 3, 4, 6]:
        _, _, J, _ = kmeans(X, k, np.random.default_rng(0), n_init=5)
        print(f"k-means k = {k}: inertia J = {J:9.1f}")
    print("  (elbow at k = 3; the optimal J is non-increasing in k, so J alone cannot pick k)")
    # anisotropic clusters: GMM beats k-means
    A = np.array([[3.0, 0.0], [0.0, 0.3]])
    Xa = np.vstack([rng.normal(size=(300, 2)) @ A + [0, 0], rng.normal(size=(300, 2)) @ A + [0, 2.0]])
    ya = np.repeat([0, 1], 300)
    _, lab, _, _ = kmeans(Xa, 2, np.random.default_rng(0), n_init=5)
    _, _, _, R, hist = gmm_em(Xa, 2, np.random.default_rng(0))
    agree = lambda l: max(np.mean(l == ya), np.mean(l != ya))
    print(f"elongated clusters: k-means agreement {agree(lab):.3f}, "
          f"GMM agreement {agree(np.argmax(R, 1)):.3f}, EM steps {len(hist)}")
    # PCA on a 3D cloud with one dominant direction
    Z = rng.normal(size=(500, 3)) * [5.0, 1.0, 0.2]
    Q = np.linalg.qr(rng.normal(size=(3, 3)))[0]
    Xp = Z @ Q.T
    _, comps, ev, _ = pca(Xp)
    print("PCA explained variance ratio:", np.round(explained_variance_ratio(Xp), 4).tolist())
    print(f"first axis vs generating axis: |cos| = {abs(comps[0] @ Q[:, 0]):.4f}")


if __name__ == "__main__":
    _demo()
