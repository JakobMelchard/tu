"""Tests for banded.py, against [S4] §4.3-4.4 and the past papers.

The §4.6 ordering and fill-in tests are in test_ordering.py.
"""
import numpy as np
import pytest
import scipy.linalg

from banded import (crout_lu, crout_lu_inplace, bandwidths, banded_lu, banded_solve,
                    banded_cholesky, skyline_profile, is_skyline_preserved)
from linsolve import lu_decompose, cholesky

RNG = np.random.default_rng(7)


def spd(n, seed=0, band=None):
    r = np.random.default_rng(seed)
    M = r.standard_normal((n, n))
    A = M @ M.T + n * np.eye(n)
    if band is not None:
        A = np.triu(np.tril(A, band), -band)
        A += np.diag(2 * n * np.ones(n))
    return A


# ------------------------------------------------------------------ Crout
def test_crout_matches_sweeping_lu():
    """[S4] Alg. 9 computes the same factors as [S4] Alg. 8, in a different order."""
    for n in (3, 5, 9):
        A = spd(n, seed=n)                       # SPD => no pivoting needed
        L, U = crout_lu(A)
        np.testing.assert_allclose(L @ U, A, atol=1e-10)
        assert np.allclose(np.diag(L), 1.0)      # normalised
        assert np.allclose(np.tril(U, -1), 0.0)
        Lr, Ur = scipy.linalg.lu(A, permute_l=False)[1:]
        np.testing.assert_allclose(L, Lr, atol=1e-10)
        np.testing.assert_allclose(U, Ur, atol=1e-10)


def test_crout_inplace_packs_both_factors():
    """[S4] Alg. 10."""
    A = spd(6, seed=3)
    L, U = crout_lu(A)
    np.testing.assert_allclose(crout_lu_inplace(A), np.tril(L, -1) + U, atol=1e-10)


def test_crout_refuses_a_matrix_without_an_lu_factorisation():
    """S2a 2.2a / F3 2.3a: [[0,2],[4,1]] has no LU with normalised L."""
    with pytest.raises(ZeroDivisionError):
        crout_lu(np.array([[0.0, 2.0], [4.0, 1.0]]))
    # after a row swap it factors trivially
    L, U = crout_lu(np.array([[4.0, 1.0], [0.0, 2.0]]))
    np.testing.assert_allclose(L @ U, [[4.0, 1.0], [0.0, 2.0]])


def test_s2a_exam_lower_triangular_lu():
    """S2a 2.1a: A = [[2,0,0],[4,3,0],[6,6,6]]."""
    A = np.array([[2.0, 0, 0], [4, 3, 0], [6, 6, 6]])
    L, U = crout_lu(A)
    np.testing.assert_allclose(L, [[1, 0, 0], [2, 1, 0], [3, 2, 1]])
    np.testing.assert_allclose(U, np.diag([2.0, 3.0, 6.0]))


# ----------------------------------------------------------------- banded
def test_bandwidths():
    A = np.diag(np.ones(6)) + np.diag(np.ones(5), 1) + np.diag(np.ones(4), -2)
    assert bandwidths(A) == (2, 1)


@pytest.mark.parametrize("p,q", [(1, 1), (2, 1), (3, 3)])
def test_banded_lu_factors_keep_the_bandwidth(p, q):
    """[S4] Thm 4.12(i)."""
    n = 30
    A = np.diag(10.0 * np.ones(n))
    for k in range(1, p + 1):
        A += np.diag(RNG.standard_normal(n - k), -k)
    for k in range(1, q + 1):
        A += np.diag(RNG.standard_normal(n - k), k)
    L, U = banded_lu(A, p, q)
    np.testing.assert_allclose(L @ U, A, atol=1e-9)
    assert bandwidths(L)[0] <= p
    assert bandwidths(U)[1] <= q


def test_banded_lu_cost_is_order_n_p_q():
    """[S4] Thm 4.12(ii)(a): the operation count scales like n p q."""
    n = 240
    prev = None
    for p in (2, 4, 8, 16):
        A = np.diag(40.0 * np.ones(n))
        for k in range(1, p + 1):
            A += np.diag(RNG.standard_normal(n - k), k) + np.diag(RNG.standard_normal(n - k), -k)
        _, _, ops = banded_lu(A, p, p, count_ops=True)
        c = ops / (n * p * p)
        assert 1.5 < c < 3.5                         # constant, i.e. ops ~ n p q
        if prev is not None:
            assert 3.0 < ops / prev < 5.0            # doubling p quadruples the work
        prev = ops


def test_banded_solve_matches_numpy():
    n, p = 40, 2
    A = np.diag(20.0 * np.ones(n))
    for k in range(1, p + 1):
        A += np.diag(RNG.standard_normal(n - k), k) + np.diag(RNG.standard_normal(n - k), -k)
    b = RNG.standard_normal(n)
    L, U = banded_lu(A, p, p)
    np.testing.assert_allclose(banded_solve(L, U, b, p, p), np.linalg.solve(A, b), atol=1e-9)


def test_tridiagonal_is_linear_in_n():
    """p = q = 1 makes every stage O(n) -- the Thomas algorithm."""
    counts = {}
    for n in (50, 100, 200, 400):
        A = (np.diag(4.0 * np.ones(n)) + np.diag(-np.ones(n - 1), 1)
             + np.diag(-np.ones(n - 1), -1))
        counts[n] = banded_lu(A, 1, 1, count_ops=True)[2]
    for n in (50, 100, 200):
        assert 1.9 < counts[2 * n] / counts[n] < 2.1


# --------------------------------------------------------------- Cholesky
def test_banded_cholesky_keeps_bandwidth_and_matches_dense():
    """[S4] (4.10) and Rem. 4.15."""
    for p in (1, 3, 5):
        A = spd(40, seed=p, band=p)
        C = banded_cholesky(A, p)
        np.testing.assert_allclose(C @ C.T, A, atol=1e-9)
        assert bandwidths(C)[0] <= p
        np.testing.assert_allclose(C, cholesky(A), atol=1e-9)
        np.testing.assert_allclose(C, np.linalg.cholesky(A), atol=1e-9)


def test_cholesky_costs_about_half_of_lu():
    """[S4] Rem. 4.16 -- S2a 2.5a asks the reverse as a FALSE statement.

    Counting the multiplications and divisions of the loops actually written in
    banded_lu and banded_cholesky: LU does ~n^3/3, Cholesky ~n^3/6.
    """
    def chol_mults(n):                      # diagonal dot of length j, then n-1-j rows
        return sum(j + (n - 1 - j) * (j + 1) for j in range(n))

    def lu_mults(n):                        # one division plus n-1-k products per row
        return sum((n - 1 - k) * (1 + (n - 1 - k)) for k in range(n - 1))

    for n in (50, 100, 200):
        assert 0.45 < chol_mults(n) / lu_mults(n) < 0.55
    assert lu_mults(300) / (300 ** 3 / 3) == pytest.approx(1.0, abs=0.02)
    assert chol_mults(300) / (300 ** 3 / 6) == pytest.approx(1.0, abs=0.02)


def test_banded_cholesky_detects_indefiniteness():
    A = np.array([[1.0, 2.0], [2.0, 1.0]])            # eigenvalues 3, -1
    with pytest.raises(np.linalg.LinAlgError):
        banded_cholesky(A, 1)


def test_s2a_exam_cholesky():
    """S2a 2.2c: B = [[4,2],[2,4]]."""
    C = banded_cholesky(np.array([[4.0, 2.0], [2.0, 4.0]]), 1)
    np.testing.assert_allclose(C, [[2.0, 0.0], [1.0, np.sqrt(3.0)]])


# ---------------------------------------------------------------- skyline
def s4_figure_45():
    """The SPD matrix of [S4] Fig. 4.5, rebuilt from its printed Cholesky factor."""
    L = np.array([[1., 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0],
                  [1, 2, 3, 1, 0, 0, 0],
                  [0, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 1, 0],
                  [1, 2, 3, 4, 5, 6, 1]])
    return L @ L.T, L


def test_skyline_factor_matches_the_printed_one():
    """[S4] Thm 4.18 / Fig. 4.5: the factor has the same sparsity pattern as A."""
    A, L = s4_figure_45()
    assert A[6, 6] == 92 and A[3, 6] == 18            # the two entries [S4] prints
    np.testing.assert_allclose(banded_cholesky(A, p=6), L, atol=1e-12)
    assert is_skyline_preserved(A)
    p, _ = skyline_profile(A)
    pl, _ = skyline_profile(L)
    np.testing.assert_array_equal(pl, p)


def test_reversing_the_ordering_creates_fill_in():
    """[S4] sec. 4.6: relabelling backwards destroys the structure."""
    A, L = s4_figure_45()
    good = int((np.abs(L) > 1e-12).sum())
    rev = A[::-1, ::-1]
    bad = int((np.abs(banded_cholesky(rev, p=6)) > 1e-12).sum())
    assert bad > good
