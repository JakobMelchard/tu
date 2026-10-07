"""Low-rank compression: truncated SVD, PCA, randomised SVD, error vs rank.

Note 02 (data compression as low-rank approximation):
- Eckart-Young-Mirsky [S19]: the rank-k truncated SVD is optimal in every
  unitarily invariant norm; ||A - A_k||_2 = s_{k+1}, ||A - A_k||_F^2 = sum_{j>k} s_j^2
  (`truncate`, `eckart_young_error`).
- PCA = SVD of the centred data matrix (`pca`, `pca_reconstruct`).
- Randomised range finder with power iterations, Halko-Martinsson-Tropp [S18]
  Algorithms 4.1/4.4 + 5.1, error bound Thm 10.5 (`range_finder`, `randomized_svd`).
- Storage: k (m + n + 1) numbers instead of m n (`compression_ratio`).

Run `python lowrank.py` for error-vs-rank tables on a smooth kernel matrix and on
a noisy one.
"""
from __future__ import annotations

import numpy as np


def truncate(A: np.ndarray, k: int):
    """Rank-k truncated SVD: (U_k, s_k, Vt_k) with A_k = U_k diag(s_k) Vt_k."""
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    return U[:, :k], s[:k], Vt[:k]


def reconstruct(U: np.ndarray, s: np.ndarray, Vt: np.ndarray) -> np.ndarray:
    return (U * s) @ Vt


def eckart_young_error(s: np.ndarray, k: int, norm: str = "fro") -> float:
    """Optimal rank-k error from the singular values alone."""
    tail = s[k:]
    if norm == "fro":
        return float(np.sqrt(np.sum(tail ** 2)))
    if norm == "2":
        return float(tail[0]) if tail.size else 0.0
    raise ValueError(norm)


def rank_for_tolerance(s: np.ndarray, rel_tol: float) -> int:
    """Smallest k with ||A - A_k||_F <= rel_tol ||A||_F."""
    tail = np.sqrt(np.cumsum((s ** 2)[::-1])[::-1])   # tail[k] = ||A - A_k||_F
    tail = np.append(tail, 0.0)
    return int(np.argmax(tail <= rel_tol * tail[0]))


def error_curve(A: np.ndarray, ranks) -> np.ndarray:
    """Relative Frobenius error ||A - A_k||_F / ||A||_F for each k."""
    s = np.linalg.svd(A, compute_uv=False)
    nrm = np.sqrt(np.sum(s ** 2))
    return np.array([eckart_young_error(s, k) / nrm for k in ranks])


def noise_threshold_rank(s: np.ndarray, sigma: float, m: int, n: int) -> int:
    """Keep singular values above the i.i.d. noise edge sigma (sqrt m + sqrt n).

    The largest singular value of an m x n matrix of N(0, sigma^2) entries is
    ~ sigma (sqrt m + sqrt n) (random-matrix edge); below it, directions are noise.
    """
    return int(np.sum(s > sigma * (np.sqrt(m) + np.sqrt(n))))


def compression_ratio(m: int, n: int, k: int) -> float:
    """Numbers stored by (U_k, s_k, V_k) over numbers in A."""
    return k * (m + n + 1) / (m * n)


def pca(X: np.ndarray, k: int):
    """PCA of rows of X (samples x features).

    Returns (mean, components (k, d), explained_variance (k,), ratio (k,)).
    The sample covariance C = Xc^T Xc / (n - 1) has eigenvalues s_j^2 / (n - 1).
    """
    mu = X.mean(axis=0)
    Xc = X - mu
    _, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    var = s ** 2 / (X.shape[0] - 1)
    return mu, Vt[:k], var[:k], var[:k] / var.sum()


def pca_encode(X, mu, comps):
    return (X - mu) @ comps.T


def pca_reconstruct(X, mu, comps):
    return mu + pca_encode(X, mu, comps) @ comps


def range_finder(A: np.ndarray, l: int, power_iter: int = 0,
                 rng: np.random.Generator | None = None) -> np.ndarray:
    """Orthonormal Q (m x l) with A ~ Q Q^T A [S18 Alg. 4.1 (q = 0), 4.4 (q > 0)].

    1. Omega ~ N(0,1)^{n x l}, Y = A Omega samples the range of A.
    2. q power iterations Y <- A (A^T Y), re-orthonormalised by QR each time;
       they replace s_j by s_j^{2q+1} and sharpen the spectral gap.
    For q = 0, l = k + p, p >= 2 [S18 Thm 10.5]:
        E ||A - Q Q^T A||_F <= (1 + k/(p-1))^{1/2} (sum_{j>k} s_j^2)^{1/2}.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    Q, _ = np.linalg.qr(A @ rng.standard_normal((A.shape[1], l)))
    for _ in range(power_iter):
        Q, _ = np.linalg.qr(A.T @ Q)
        Q, _ = np.linalg.qr(A @ Q)
    return Q


def randomized_svd(A: np.ndarray, k: int, oversample: int = 10, power_iter: int = 2,
                   rng: np.random.Generator | None = None):
    """Halko-Martinsson-Tropp randomised SVD [S18 Alg. 5.1]: Q from `range_finder`,
    B = Q^T A (small, (k+p) x n), SVD of B, U = Q U_B, truncated to rank k."""
    Q = range_finder(A, k + oversample, power_iter, rng)
    Ub, s, Vt = np.linalg.svd(Q.T @ A, full_matrices=False)
    return (Q @ Ub)[:, :k], s[:k], Vt[:k]


def smooth_kernel_matrix(m: int = 300, n: int = 200) -> np.ndarray:
    """A_ij = 1 / (1 + 25 (x_i - y_j)^2): analytic kernel, singular values decay
    exponentially (the same mechanism as the IR basis, note 03)."""
    x = np.linspace(-1, 1, m)
    y = np.linspace(-1, 1, n)
    return 1.0 / (1.0 + 25.0 * (x[:, None] - y[None, :]) ** 2)


def demo() -> None:
    rng = np.random.default_rng(1)
    A = smooth_kernel_matrix()
    noisy = A + 1e-3 * rng.standard_normal(A.shape)
    ranks = [1, 2, 4, 8, 16, 24, 32, 48]
    print("relative Frobenius error ||A - A_k||_F / ||A||_F")
    print(f"{'k':>4} {'smooth':>10} {'noisy':>10} {'rSVD(q=2)':>10} {'storage':>8}")
    e_s, e_n = error_curve(A, ranks), error_curve(noisy, ranks)
    nrm = np.linalg.norm(A)
    for k, a, b in zip(ranks, e_s, e_n):
        U, s, Vt = randomized_svd(A, k, rng=rng)
        r = np.linalg.norm(A - reconstruct(U, s, Vt)) / nrm
        print(f"{k:4d} {a:10.2e} {b:10.2e} {r:10.2e} {compression_ratio(*A.shape, k):8.3f}")
    print("smooth: exponential decay; noisy: floor of order ||noise||_F/||A||_F "
          f"= {1e-3 * np.sqrt(A.size) / nrm:.1e} (noise is full rank).")
    print(f"rank for 1e-6 relative error: {rank_for_tolerance(np.linalg.svd(A, compute_uv=False), 1e-6)}")
    s_noisy = np.linalg.svd(noisy, compute_uv=False)
    k_star = noise_threshold_rank(s_noisy, 1e-3, *A.shape)
    print("\ndenoising: error of the rank-k truncation of the NOISY matrix against the CLEAN one")
    for k in (10, 16, 20, 24, k_star, 36, 48):
        e = np.linalg.norm(A - reconstruct(*truncate(noisy, k))) / nrm
        print(f"  k = {k:2d} {e:.2e}" + ("   <- noise-edge threshold" if k == k_star else ""))
    print("  too small k: bias; too large k: the kept directions are fitted noise.")


if __name__ == "__main__":
    demo()
