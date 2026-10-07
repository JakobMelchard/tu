import numpy as np
import pytest

from lowrank import (compression_ratio, noise_threshold_rank, eckart_young_error, error_curve, pca, pca_reconstruct,
                     randomized_svd, range_finder, rank_for_tolerance, reconstruct, smooth_kernel_matrix,
                     truncate)


@pytest.mark.parametrize("k", [1, 3, 10])
def test_truncation_error_is_eckart_young(k):
    rng = np.random.default_rng(0)
    A = rng.standard_normal((40, 30))
    s = np.linalg.svd(A, compute_uv=False)
    Ak = reconstruct(*truncate(A, k))
    assert np.isclose(np.linalg.norm(A - Ak), eckart_young_error(s, k))
    assert np.isclose(np.linalg.norm(A - Ak, 2), eckart_young_error(s, k, "2"))


def test_truncated_svd_beats_random_rank_k_matrices():
    rng = np.random.default_rng(1)
    A = rng.standard_normal((20, 15))
    best = np.linalg.norm(A - reconstruct(*truncate(A, 4)))
    for _ in range(50):
        B = rng.standard_normal((20, 4)) @ rng.standard_normal((4, 15))
        # best rank-4 approximation in the column space of B: still no better
        P = B @ np.linalg.pinv(B)
        assert np.linalg.norm(A - P @ A) >= best - 1e-12


def test_smooth_kernel_decays_exponentially_and_rank_for_tolerance():
    A = smooth_kernel_matrix()
    err = error_curve(A, [4, 8, 16, 32])
    assert np.all(np.diff(np.log(err)) < -1.0)          # each doubling gains > e
    s = np.linalg.svd(A, compute_uv=False)
    k = rank_for_tolerance(s, 1e-6)
    assert eckart_young_error(s, k) <= 1e-6 * np.linalg.norm(A)
    assert eckart_young_error(s, k - 1) > 1e-6 * np.linalg.norm(A)
    assert k < 60                       # 47 of 200


def test_pca_matches_sklearn_and_reconstruction_is_projection():
    from sklearn.decomposition import PCA
    rng = np.random.default_rng(2)
    X = rng.standard_normal((200, 3)) @ rng.standard_normal((3, 10)) + 0.01 * rng.standard_normal((200, 10))
    mu, comps, var, ratio = pca(X, 3)
    sk = PCA(3).fit(X)
    assert np.allclose(var, sk.explained_variance_)
    assert np.allclose(np.abs(np.sum(comps * sk.components_, axis=1)), 1.0)
    assert ratio.sum() > 0.999
    R = pca_reconstruct(X, mu, comps)
    assert np.allclose(pca_reconstruct(R, mu, comps), R)   # idempotent


def test_randomized_svd_is_near_optimal():
    rng = np.random.default_rng(3)
    A = smooth_kernel_matrix() + 1e-6 * rng.standard_normal((300, 200))
    s = np.linalg.svd(A, compute_uv=False)
    for k in (5, 10, 20):
        U, sr, Vt = randomized_svd(A, k, oversample=10, power_iter=2, rng=rng)
        err = np.linalg.norm(A - reconstruct(U, sr, Vt))
        assert err <= 1.5 * eckart_young_error(s, k)
        assert np.allclose(sr[:3], s[:3], rtol=1e-8)

@pytest.mark.parametrize("k,p", [(5, 2), (10, 5), (10, 10)])
def test_range_finder_obeys_halko_martinsson_tropp_thm_10_5(k, p):
    """E||A - Q Q^T A||_F <= sqrt(1 + k/(p-1)) * sqrt(sum_{j>k} s_j^2), q = 0."""
    rng = np.random.default_rng(4)
    A = rng.standard_normal((120, 3 * k)) @ np.diag(0.7 ** np.arange(3 * k)) @ rng.standard_normal((3 * k, 90))
    A += 1e-3 * rng.standard_normal(A.shape)
    s = np.linalg.svd(A, compute_uv=False)
    errs = []
    for _ in range(200):
        Q = range_finder(A, k + p, 0, rng)
        errs.append(np.linalg.norm(A - Q @ (Q.T @ A)))
    assert np.mean(errs) <= np.sqrt(1 + k / (p - 1)) * eckart_young_error(s, k)
    assert min(errs) >= eckart_young_error(s, k + p) - 1e-12   # rank k+p: Eckart-Young floor


def test_compression_ratio():
    assert compression_ratio(100, 100, 10) == pytest.approx(10 * 201 / 1e4)
    assert compression_ratio(1000, 1000, 1) < 0.01


def test_noise_edge_threshold_is_near_optimal_denoiser():
    rng = np.random.default_rng(5)
    A = smooth_kernel_matrix()
    sigma = 1e-3
    N = sigma * rng.standard_normal(A.shape)
    assert np.linalg.svd(N, compute_uv=False)[0] == pytest.approx(sigma * (np.sqrt(300) + np.sqrt(200)), rel=0.1)
    U, s, Vt = np.linalg.svd(A + N, full_matrices=False)
    errs = {k: np.linalg.norm(A - reconstruct(U[:, :k], s[:k], Vt[:k])) for k in range(5, 80)}
    k_star = noise_threshold_rank(s, sigma, *A.shape)
    assert errs[k_star] <= 1.1 * min(errs.values())
    assert errs[79] > errs[k_star]                          # keeping noise directions hurts
