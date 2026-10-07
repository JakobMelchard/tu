"""Kernels, Gram matrices, feature maps, the representer theorem, kernel complexity.

Note 08 (kernels and RKHS), section Results:
- Theorem 8.1: k is PSD iff k(x,x') = <phi(x), phi(x')> (`poly2_feature_map` makes phi explicit).
- Theorems 8.4, 8.5: closure properties, the standard kernels are PSD; tanh is not (`is_psd`).
- Theorem 8.6: kernel trick, feature-space distances, centring (`feature_distance`, `centre_gram`).
- Theorem 8.7: representer theorem, w* = Phi^T alpha (`representer_demo`).
- Note 05, Theorem 5.7 in an RKHS (used by note 09's margin bound): for
  F = {f : ||f||_H <= B}, R_S(F) = (B/n) E_sigma sqrt(sigma^T K sigma) <= B sqrt(tr K) / n
  (`kernel_rademacher_mc`, `kernel_rademacher_bound`).

Run `python kernels.py`.
"""
from __future__ import annotations

import numpy as np


def _pair_sqdist(X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    X = np.atleast_2d(X); Y = np.atleast_2d(Y)
    return np.sum(X**2, 1)[:, None] - 2 * X @ Y.T + np.sum(Y**2, 1)[None, :]


def linear_kernel(X, Y):
    return np.atleast_2d(X) @ np.atleast_2d(Y).T


def polynomial_kernel(X, Y, degree: int = 2, c: float = 1.0):
    return (linear_kernel(X, Y) + c) ** degree


def rbf_kernel(X, Y, gamma: float = 1.0):
    return np.exp(-gamma * np.maximum(_pair_sqdist(X, Y), 0.0))


def laplacian_kernel(X, Y, gamma: float = 1.0):
    X = np.atleast_2d(X); Y = np.atleast_2d(Y)
    return np.exp(-gamma * np.sum(np.abs(X[:, None, :] - Y[None, :, :]), axis=2))


def sigmoid_kernel(X, Y, a: float = 1.0, c: float = -1.0):
    """NOT positive definite in general; included to show a failing PSD check."""
    return np.tanh(a * linear_kernel(X, Y) + c)


def gram_matrix(k, X, Y=None, **kw):
    return k(X, X if Y is None else Y, **kw)


def is_psd(K: np.ndarray, tol: float = 1e-8) -> bool:
    K = 0.5 * (K + K.T)
    return bool(np.linalg.eigvalsh(K).min() >= -tol)


def poly2_feature_map(X: np.ndarray, c: float = 1.0) -> np.ndarray:
    """Explicit phi with <phi(x), phi(x')> = (<x,x'> + c)^2 for x in R^d:
    [c, sqrt(2c) x_i, x_i^2, sqrt(2) x_i x_j (i<j)]."""
    X = np.atleast_2d(X)
    n, d = X.shape
    cols = [np.full((n, 1), c), np.sqrt(2 * c) * X, X**2]
    cross = [np.sqrt(2) * X[:, [i]] * X[:, [j]] for i in range(d) for j in range(i + 1, d)]
    return np.hstack(cols + cross)


def feature_distance(k, x, y) -> float:
    """||phi(x) - phi(y)||^2 = k(x,x) - 2k(x,y) + k(y,y)."""
    return float(np.squeeze(k(x, x) - 2 * k(x, y) + k(y, y)))


def centre_gram(K: np.ndarray) -> np.ndarray:
    n = K.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    return J @ K @ J


def representer_demo(X: np.ndarray, y: np.ndarray, lam: float, c: float = 1.0):
    """Regularised least squares min_w (1/n)||Phi w - y||^2 + lam ||w||^2 in the explicit
    feature space of the quadratic kernel. Returns (w_primal, w_from_alpha, alpha, max_dev)
    where w_from_alpha = Phi^T alpha with alpha = (K + n lam I)^{-1} y: the representer theorem
    says w* lies in span{phi(x_i)}, and the two coincide."""
    Phi = poly2_feature_map(X, c)
    n, p = Phi.shape
    w_primal = np.linalg.solve(Phi.T @ Phi + n * lam * np.eye(p), Phi.T @ y)
    K = polynomial_kernel(X, X, 2, c)
    alpha = np.linalg.solve(K + n * lam * np.eye(n), y)
    w_dual = Phi.T @ alpha
    # component of w_primal orthogonal to span{phi(x_i)} must vanish
    Q, _ = np.linalg.qr(Phi.T)          # orthonormal basis of the span (p x n)
    orth = w_primal - Q @ (Q.T @ w_primal)
    return w_primal, w_dual, alpha, float(np.linalg.norm(orth))


def kernel_rademacher_mc(K: np.ndarray, B: float, n_sigma: int, rng: np.random.Generator) -> float:
    """R_S of the RKHS ball of radius B: (B/n) E_sigma sqrt(sigma^T K sigma), by Monte Carlo.

    sup_{||f|| <= B} sum_i sigma_i f(x_i) = sup <f, sum_i sigma_i k(x_i, .)> = B ||sum_i sigma_i k(x_i,.)||.
    """
    n = K.shape[0]
    sigma = rng.choice([-1.0, 1.0], size=(n_sigma, n))
    q = np.sum((sigma @ K) * sigma, axis=1)                 # sigma^T K sigma per draw (BLAS)
    return float(B * np.mean(np.sqrt(np.maximum(q, 0.0))) / n)


def kernel_rademacher_bound(K: np.ndarray, B: float) -> float:
    """Jensen: (B/n) sqrt(E sigma^T K sigma) = B sqrt(tr K) / n."""
    return float(B * np.sqrt(np.trace(K)) / K.shape[0])


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X = rng.normal(size=(6, 2))
    for name, k in (("linear", linear_kernel), ("poly2", polynomial_kernel),
                    ("rbf", rbf_kernel), ("laplacian", laplacian_kernel), ("sigmoid", sigmoid_kernel)):
        K = gram_matrix(k, X)
        print(f"{name:10s} min eigenvalue {np.linalg.eigvalsh(0.5*(K+K.T)).min():+.4f}  PSD: {is_psd(K)}")
    Phi = poly2_feature_map(X)
    print("explicit quadratic map reproduces the kernel:",
          np.allclose(Phi @ Phi.T, polynomial_kernel(X, X, 2, 1.0)))
    y = X[:, 0] ** 2 - X[:, 1] + 0.1 * rng.normal(size=6)
    wp, wd, alpha, dev = representer_demo(X, y, 0.1)
    print(f"representer theorem: ||w_primal - Phi^T alpha|| = {np.linalg.norm(wp - wd):.2e}, "
          f"orthogonal component {dev:.2e}")
    print("feature-space distance RBF, gamma=1:", feature_distance(lambda a, b: rbf_kernel(a, b, 1.0), X[0], X[1]))
    print("\nRKHS ball ||f|| <= 1, R_S = (1/n) E sqrt(sigma^T K sigma) vs B sqrt(tr K)/n, 5000 sigma draws:")
    for n in (10, 100, 1000):
        Xn = rng.normal(size=(n, 2))
        for name, K in (("rbf gamma=0.5", rbf_kernel(Xn, Xn, 0.5)), ("poly2", polynomial_kernel(Xn, Xn, 2, 1.0))):
            print(f"  n={n:5d} {name:14s} R_S {kernel_rademacher_mc(K, 1.0, 5000, rng):.4f}"
                  f"  bound {kernel_rademacher_bound(K, 1.0):.4f}")
