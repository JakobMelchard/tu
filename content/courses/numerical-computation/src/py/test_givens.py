"""Tests for givens.py, against [S4] sec. 4.7.4-4.7.5."""
import numpy as np
import pytest
import scipy.linalg

from givens import (givens_rotation, apply_givens_left, apply_givens_right, givens_qr,
                    hessenberg_qr, rq_product, is_hessenberg, qr_column_pivoting)

RNG = np.random.default_rng(3)


def hessenberg_matrix(n, seed=0):
    r = np.random.default_rng(seed)
    return np.triu(r.standard_normal((n, n)), -1)


# ------------------------------------------------------- rotation itself
def test_rotation_zeroes_the_second_entry():
    for a, b in [(3.0, 4.0), (-1.0, 2.0), (5.0, 0.0), (0.0, 7.0)]:
        c, s = givens_rotation(a, b)
        assert c ** 2 + s ** 2 == pytest.approx(1.0)
        out = np.array([[c, s], [-s, c]]) @ np.array([a, b])
        assert out[1] == pytest.approx(0.0, abs=1e-14)
        assert abs(out[0]) == pytest.approx(np.hypot(a, b))


def test_rotation_touches_only_two_rows_or_columns():
    """[S4] Lem. 4.53(ii)-(iii)."""
    A = RNG.standard_normal((5, 5))
    c, s = givens_rotation(A[1, 0], A[3, 0])
    L = apply_givens_left(A, 1, 3, c, s)
    R = apply_givens_right(A, 1, 3, c, s)
    for k in (0, 2, 4):
        np.testing.assert_allclose(L[k], A[k])
        np.testing.assert_allclose(R[:, k], A[:, k])


# ------------------------------------------------------------ dense QR
@pytest.mark.parametrize("n", [3, 5, 8])
def test_givens_qr_matches_numpy(n):
    A = RNG.standard_normal((n, n))
    Q, R = givens_qr(A)
    np.testing.assert_allclose(Q @ R, A, atol=1e-10)
    np.testing.assert_allclose(Q.T @ Q, np.eye(n), atol=1e-12)
    assert np.allclose(np.tril(R, -1), 0.0, atol=1e-12)
    np.testing.assert_allclose(np.abs(np.diag(R)), np.abs(np.diag(np.linalg.qr(A)[1])),
                               atol=1e-10)


def test_dense_givens_qr_needs_quadratically_many_rotations():
    """[S4] sec. 4.7.5: O(n^2) rotations, more expensive than Householder."""
    for n in (4, 8, 16):
        A = RNG.standard_normal((n, n))
        assert givens_qr(A, count_rotations=True)[2] == n * (n - 1) // 2


# ------------------------------------------------------- Hessenberg QR
def test_s4_example_4_54():
    """[S4] Ex. 4.54: A = [[1,1,1],[1,0,1],[0,1,1]] needs two rotations."""
    A = np.array([[1.0, 1, 1], [1, 0, 1], [0, 1, 1]])
    Q, R, rot = hessenberg_qr(A, count_rotations=True)
    assert rot == 2
    np.testing.assert_allclose(Q @ R, A, atol=1e-12)
    np.testing.assert_allclose(Q.T @ Q, np.eye(3), atol=1e-14)
    # the diagonal printed in [S4]: sqrt2, sqrt3/sqrt2, -1/sqrt3
    np.testing.assert_allclose(np.diag(R),
                               [np.sqrt(2), np.sqrt(3) / np.sqrt(2), -1 / np.sqrt(3)],
                               atol=1e-12)
    # the first row, recomputed by hand: (sqrt2, 1/sqrt2, sqrt2)
    np.testing.assert_allclose(R[0], [np.sqrt(2), 1 / np.sqrt(2), np.sqrt(2)], atol=1e-12)
    np.testing.assert_allclose(R[1, 2], np.sqrt(2 / 3), atol=1e-12)


@pytest.mark.parametrize("n", [4, 7, 12])
def test_hessenberg_qr_needs_exactly_n_minus_one_rotations(n):
    """[S4] Ex. 4.55: hence O(n^2) instead of O(n^3)."""
    H = hessenberg_matrix(n, seed=n)
    Q, R, rot = hessenberg_qr(H, count_rotations=True)
    assert rot == n - 1
    np.testing.assert_allclose(Q @ R, H, atol=1e-10)
    assert np.allclose(np.tril(R, -1), 0.0, atol=1e-10)


@pytest.mark.parametrize("n", [4, 7, 12])
def test_rq_is_hessenberg_again(n):
    """[S4] sec. 4.7.5 -- the fact that makes the QR algorithm O(n^3)."""
    H = hessenberg_matrix(n, seed=n + 1)
    for _ in range(5):
        H = rq_product(H)
        assert is_hessenberg(H, tol=1e-10)


def test_rq_preserves_the_eigenvalues_and_converges():
    """R Q = Q^T H Q is a similarity transformation (note 09)."""
    H = hessenberg_matrix(5, seed=2)
    ref = np.sort_complex(np.linalg.eigvals(H))
    A = H.copy()
    for _ in range(300):
        A = rq_product(A)
        assert is_hessenberg(A, tol=1e-9)
    np.testing.assert_allclose(np.sort_complex(np.linalg.eigvals(A)), ref, atol=1e-8)


def test_tridiagonal_case_is_linear():
    """A symmetric Hessenberg matrix is tridiagonal: O(n) rotations."""
    n = 20
    T = (np.diag(2.0 * np.ones(n)) + np.diag(-np.ones(n - 1), 1)
         + np.diag(-np.ones(n - 1), -1))
    assert hessenberg_qr(T, count_rotations=True)[2] == n - 1


# ------------------------------------------------- QR with column pivoting
def test_column_pivoting_orders_the_diagonal_and_reveals_the_rank():
    """[S4] sec. 4.7.4."""
    B = RNG.standard_normal((10, 4))
    B = np.column_stack([B[:, :3], B[:, 0] + 2 * B[:, 1]])      # rank 3
    Q, R, piv, rank = qr_column_pivoting(B)
    np.testing.assert_allclose(B[:, piv], Q @ R, atol=1e-10)
    np.testing.assert_allclose(Q.T @ Q, np.eye(10), atol=1e-10)
    d = np.abs(np.diag(R))
    assert np.all(d[:-1] >= d[1:] - 1e-12)                      # non-increasing
    assert rank == np.linalg.matrix_rank(B) == 3
    assert d[3] < 1e-10


def test_column_pivoting_agrees_with_scipy():
    A = RNG.standard_normal((9, 5))
    Q, R, piv, rank = qr_column_pivoting(A)
    _, Rs, ps = scipy.linalg.qr(A, pivoting=True)
    np.testing.assert_allclose(np.abs(np.diag(R)), np.abs(np.diag(Rs)), atol=1e-9)
    np.testing.assert_array_equal(piv, ps)
    assert rank == 5


def test_column_pivoting_on_a_full_rank_square_matrix():
    A = RNG.standard_normal((6, 6))
    Q, R, piv, rank = qr_column_pivoting(A)
    assert rank == 6
    np.testing.assert_allclose(np.abs(np.linalg.det(A)),
                               np.abs(np.prod(np.diag(R))), rtol=1e-9)
