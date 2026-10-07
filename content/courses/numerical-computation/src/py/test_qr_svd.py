import numpy as np

from qr_svd import (gram_schmidt_classical, gram_schmidt_modified, householder_vector,
                    householder_qr,
                    qr_solve, power_method, qr_algorithm, jacobi_svd, low_rank, cond2)


def ill_conditioned(m, n, kappa, seed=0):
    rng = np.random.default_rng(seed)
    U, _ = np.linalg.qr(rng.standard_normal((m, m)))
    V, _ = np.linalg.qr(rng.standard_normal((n, n)))
    return U[:, :n] * np.logspace(0, -np.log10(kappa), n) @ V.T


def orth_loss(Q):
    return np.max(np.abs(Q.T @ Q - np.eye(Q.shape[1])))


def test_all_qr_variants_factor_a_well_conditioned_matrix():
    rng = np.random.default_rng(1)
    A = rng.standard_normal((7, 4))
    for fn in (gram_schmidt_classical, gram_schmidt_modified, householder_qr):
        Q, R = fn(A)
        np.testing.assert_allclose(Q @ R, A, atol=1e-13)
        assert orth_loss(Q) < 1e-13
        assert np.max(np.abs(np.tril(R[:4, :4], -1))) < 1e-13


def test_householder_matches_numpy_up_to_signs():
    A = np.random.default_rng(2).standard_normal((6, 4))
    Q, R = householder_qr(A)
    Qn, Rn = np.linalg.qr(A)
    s = np.sign(np.diag(R[:4]) * np.diag(Rn))
    np.testing.assert_allclose(R[:4] * s[:, None], Rn, atol=1e-12)
    np.testing.assert_allclose(Q[:, :4] * s, Qn, atol=1e-12)


def test_orthogonality_loss_hierarchy():
    A = ill_conditioned(50, 10, 1e8)
    l_cgs = orth_loss(gram_schmidt_classical(A)[0])
    l_mgs = orth_loss(gram_schmidt_modified(A)[0])
    l_hh = orth_loss(householder_qr(A)[0])
    assert l_hh < 1e-13 < l_mgs < 1e-5 < l_cgs      # CGS ~ kappa^2 u, MGS ~ kappa u


def test_qr_least_squares_matches_lstsq():
    rng = np.random.default_rng(3)
    A = rng.standard_normal((20, 5))
    b = rng.standard_normal(20)
    x = qr_solve(A, b)
    np.testing.assert_allclose(x, np.linalg.lstsq(A, b, rcond=None)[0], rtol=1e-10)
    assert np.max(np.abs(A.T @ (A @ x - b))) < 1e-10        # normal equations hold


def test_power_method_and_qr_algorithm():
    A = np.array([[4., 1., 0.], [1., 3., 1.], [0., 1., 2.]])
    ev = np.sort(np.linalg.eigvalsh(A))[::-1]
    lam, v = power_method(A)
    assert abs(lam - ev[0]) < 1e-10
    np.testing.assert_allclose(A @ v, lam * v, atol=1e-8)
    np.testing.assert_allclose(qr_algorithm(A), ev, atol=1e-10)


def test_jacobi_svd_matches_numpy():
    rng = np.random.default_rng(4)
    A = rng.standard_normal((9, 5))
    U, s, V = jacobi_svd(A)
    np.testing.assert_allclose(s, np.linalg.svd(A, compute_uv=False), rtol=1e-12)
    np.testing.assert_allclose((U * s) @ V.T, A, atol=1e-12)
    assert orth_loss(U) < 1e-12 and orth_loss(V) < 1e-12
    A2 = ill_conditioned(30, 6, 1e10, seed=5)
    # tiny sigma are only determined to ~u sigma_max absolutely (the matrix itself is rounded)
    np.testing.assert_allclose(jacobi_svd(A2)[1], np.linalg.svd(A2, compute_uv=False), rtol=1e-8, atol=1e-15)
    assert abs(cond2(A2) - np.linalg.cond(A2)) / 1e10 < 1e-6


def test_eckart_young():
    A = np.random.default_rng(6).standard_normal((10, 6))
    for k in (1, 2, 4):
        Ak, s = low_rank(A, k)
        assert np.linalg.matrix_rank(Ak) == k
        assert abs(np.linalg.norm(A - Ak, 2) - s[k]) < 1e-10
        assert abs(np.linalg.norm(A - Ak, "fro") - np.sqrt(np.sum(s[k:] ** 2))) < 1e-10
        rng = np.random.default_rng(k)
        B = rng.standard_normal((10, k)) @ rng.standard_normal((k, 6))    # any other rank-k
        assert np.linalg.norm(A - B, "fro") >= np.linalg.norm(A - Ak, "fro")


def test_householder_vector_maps_x_to_alpha_e1():
    """[S4 §4.7.3]: H x = alpha e_1 with alpha = -sign(x_0) ||x||, no cancellation."""
    for x in (np.array([3.0, 4.0, 0.0]), np.array([-1.0, 2.0, 2.0]), np.array([0.0, 1.0])):
        v, alpha = householder_vector(x)
        H = np.eye(len(x)) - 2 * np.outer(v, v) / (v @ v)
        np.testing.assert_allclose(H @ x, alpha * np.eye(len(x))[0], atol=1e-14)
        assert abs(alpha) == np.linalg.norm(x)
        np.testing.assert_allclose(H @ H, np.eye(len(x)), atol=1e-14)
