"""Tests for pseudoinverse.py, against [S4] sec. 5.1-5.3 and the past papers."""
import numpy as np
import pytest
import scipy.linalg

from pseudoinverse import (reduced_svd, numerical_rank, pinv, lstsq_svd,
                           min_norm_solution, project_range, project_kernel,
                           svd_via_symmetric, normal_equations_solve, s4_example_5_6)
from qr_svd import qr_solve

RNG = np.random.default_rng(5)


def rank_deficient(m, n, r, seed=0):
    rr = np.random.default_rng(seed)
    return rr.standard_normal((m, r)) @ rr.standard_normal((r, n))


# ---------------------------------------------- [S4] Ex. 5.6, the headline
def test_s4_example_5_6_normal_equations_lose_digits():
    """[S4] Ex. 5.6.  MATLAB prints 1.011235955056180 / 0.988764044943820 for
    the normal equations and (1, 1) to 16 digits for the QR route."""
    A, b, x = s4_example_5_6(1e-7)
    assert np.linalg.cond(A.T @ A) == pytest.approx(2 / 1e-7 ** 2 + 1, rel=0.02)
    ne = normal_equations_solve(A, b)
    assert ne[0] == pytest.approx(1.011235955056180, abs=1e-12)
    assert ne[1] == pytest.approx(0.988764044943820, abs=1e-12)
    assert abs(ne[0] - 1.0) > 1e-3                       # only ~2 correct digits
    np.testing.assert_allclose(qr_solve(A, b), x, atol=1e-14)
    np.testing.assert_allclose(lstsq_svd(A, b), x, atol=1e-12)


def test_kappa_of_the_gram_matrix_is_kappa_squared():
    """[S4] sec. 5.2 and Ex. 5.6: kappa(A^T A) = 2/eps^2 + 1 = kappa(A)^2.

    A^T A = [[1+e^2, 1], [1, 1+e^2]] has eigenvalues 2+e^2 and e^2, so the exact
    value is (2+e^2)/e^2.  Only moderate eps are checked numerically: for
    eps = 1e-7 the Gram matrix itself is formed inaccurately, which is the point.
    """
    for eps in (1e-2, 1e-3, 1e-4):
        A, _, _ = s4_example_5_6(eps)
        exact = 2 / eps ** 2 + 1
        assert np.linalg.cond(A.T @ A) == pytest.approx(exact, rel=1e-4)
        assert np.linalg.cond(A) ** 2 == pytest.approx(exact, rel=1e-4)


# ------------------------------------------------------------ reduced SVD
def test_reduced_svd_reconstructs_and_is_orthonormal():
    for (m, n, r) in [(6, 4, 3), (8, 3, 3), (5, 5, 2)]:
        A = rank_deficient(m, n, r, seed=m + n)
        U, s, V, rk = reduced_svd(A)
        assert rk == r
        np.testing.assert_allclose(U @ np.diag(s) @ V.T, A, atol=1e-10)
        np.testing.assert_allclose(U.T @ U, np.eye(r), atol=1e-12)
        np.testing.assert_allclose(V.T @ V, np.eye(r), atol=1e-12)
        np.testing.assert_allclose(s, np.linalg.svd(A, compute_uv=False)[:r], atol=1e-10)


def test_numerical_rank_needs_a_cut_off():
    """[S4] Rem. 5.16: in floating point every sigma_i is non-zero."""
    A = rank_deficient(7, 5, 3, seed=1)
    assert numerical_rank(A) == 3 == np.linalg.matrix_rank(A)
    s = np.linalg.svd(A, compute_uv=False)
    assert s[3] > 0.0 and s[4] > 0.0                     # not exactly zero
    assert numerical_rank(A, tol=s[0] * 0.5) == 1        # a coarse cut-off sees rank 1


# ------------------------------------------------------------ pseudoinverse
def test_penrose_identities():
    """[S4] sec. 5.3.6: A A^+ A = A, (A^+)^+ = A, plus the two symmetry ones."""
    for (m, n, r) in [(6, 4, 3), (4, 6, 3), (5, 5, 5), (7, 2, 2)]:
        A = rank_deficient(m, n, r, seed=m * n)
        P = pinv(A)
        np.testing.assert_allclose(A @ P @ A, A, atol=1e-9)
        np.testing.assert_allclose(P @ A @ P, P, atol=1e-9)
        np.testing.assert_allclose((A @ P).T, A @ P, atol=1e-9)
        np.testing.assert_allclose((P @ A).T, P @ A, atol=1e-9)
        np.testing.assert_allclose(pinv(P), A, atol=1e-9)
        np.testing.assert_allclose(P, np.linalg.pinv(A), atol=1e-9)
        np.testing.assert_allclose(P, scipy.linalg.pinv(A), atol=1e-9)


def test_pinv_is_the_inverse_for_an_invertible_matrix():
    A = RNG.standard_normal((5, 5))
    np.testing.assert_allclose(pinv(A), np.linalg.inv(A), atol=1e-9)


def test_norm_of_the_pseudoinverse():
    """[S4] Exercise 5.19: ||A^+||_2 = 1/sigma_r."""
    A = rank_deficient(8, 5, 4, seed=9)
    s = np.linalg.svd(A, compute_uv=False)
    assert np.linalg.norm(pinv(A), 2) == pytest.approx(1.0 / s[3], rel=1e-8)


# ------------------------------------------------- minimum-norm solutions
def test_min_norm_solution_is_a_solution_and_is_minimal():
    """[S4] sec. 5.3.2."""
    A = RNG.standard_normal((3, 7))
    b = RNG.standard_normal(3)
    x = min_norm_solution(A, b)
    np.testing.assert_allclose(A @ x, b, atol=1e-10)
    for _ in range(20):
        y = RNG.standard_normal(7)
        other = x + project_kernel(A, y)
        np.testing.assert_allclose(A @ other, b, atol=1e-9)
        assert np.linalg.norm(other) >= np.linalg.norm(x) - 1e-12
    np.testing.assert_allclose(x, np.linalg.lstsq(A, b, rcond=None)[0], atol=1e-9)


def test_min_norm_solution_is_orthogonal_to_the_kernel():
    A = RNG.standard_normal((3, 7))
    b = RNG.standard_normal(3)
    x = min_norm_solution(A, b)
    np.testing.assert_allclose(project_kernel(A, x), 0.0, atol=1e-10)


def test_projections():
    """[S4] Exercise 5.12."""
    A = rank_deficient(6, 5, 3, seed=4)
    x = RNG.standard_normal(6)
    Pr = project_range(A, x)
    np.testing.assert_allclose(project_range(A, Pr), Pr, atol=1e-10)      # idempotent
    assert abs((x - Pr) @ Pr) < 1e-10                                     # orthogonal
    z = RNG.standard_normal(5)
    Pk = project_kernel(A, z)
    np.testing.assert_allclose(A @ Pk, 0.0, atol=1e-9)


def test_lstsq_svd_handles_rank_deficiency():
    """[S4] Thm 5.17: minimum norm among the minimisers of ||Ax - b||."""
    A = rank_deficient(9, 5, 3, seed=6)
    b = RNG.standard_normal(9)
    x = lstsq_svd(A, b)
    ref = np.linalg.lstsq(A, b, rcond=None)[0]
    np.testing.assert_allclose(x, ref, atol=1e-8)
    r = np.linalg.norm(A @ x - b)
    for _ in range(20):
        y = RNG.standard_normal(5)
        cand = x + project_kernel(A, y)
        assert np.linalg.norm(A @ cand - b) >= r - 1e-9
        assert np.linalg.norm(cand) >= np.linalg.norm(x) - 1e-9


# ----------------------------------------- the symmetric embedding of 5.3.6
def test_svd_via_symmetric_embedding():
    """[S4] sec. 5.3.6: [[0, A^T], [A, 0]] has eigenvalues +- sigma_i."""
    for (m, n) in [(6, 4), (4, 6), (5, 5)]:
        A = RNG.standard_normal((m, n))
        np.testing.assert_allclose(svd_via_symmetric(A),
                                   np.linalg.svd(A, compute_uv=False), atol=1e-10)


def test_symmetric_embedding_spectrum_is_plus_minus_sigma():
    A = RNG.standard_normal((4, 3))
    m, n = A.shape
    S = np.zeros((m + n, m + n))
    S[:n, n:] = A.T
    S[n:, :n] = A
    ev = np.sort(np.linalg.eigvalsh(S))
    s = np.linalg.svd(A, compute_uv=False)
    np.testing.assert_allclose(ev[-3:], np.sort(s), atol=1e-10)
    np.testing.assert_allclose(ev[:3], -np.sort(s)[::-1], atol=1e-10)


# ------------------------------------------------------------- exam items
def test_s2a_rectangle_least_squares():
    """S2a 2.3b, 2024W: a ~ 15, b ~ 21, a + b ~ 39."""
    A = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    y = np.array([15.0, 21.0, 39.0])
    np.testing.assert_allclose(lstsq_svd(A, y), [16.0, 22.0], atol=1e-10)
    np.testing.assert_allclose(qr_solve(A, y), [16.0, 22.0], atol=1e-10)
    np.testing.assert_allclose(A.T @ A, [[2, 1], [1, 2]])
    np.testing.assert_allclose(A.T @ y, [54.0, 60.0])
    assert np.linalg.norm(y - A @ np.array([16.0, 22.0])) == pytest.approx(np.sqrt(3))


def test_f2_least_squares_exam_item():
    """F2 2.4, 2022W."""
    A = np.array([[1.0, 1.0], [2.0, 0.0], [0.0, 2.0]])
    b = np.array([1.0, 1.0, -5.0])
    np.testing.assert_allclose(A.T @ A, [[5, 1], [1, 5]])
    np.testing.assert_allclose(A.T @ b, [3.0, -9.0])
    np.testing.assert_allclose(lstsq_svd(A, b), [1.0, -2.0], atol=1e-10)
