"""Tests for eig.py, against [S4] chapter 7."""
import numpy as np
import pytest
import scipy.linalg

from eig import (rayleigh_quotient, subspace_angle, inverse_iteration,
                 inverse_iteration_shift, rayleigh_quotient_iteration,
                 eigen_residual_bound, orthogonal_iteration, hessenberg,
                 shifted_qr, wilkinson_shift)
from qr_svd import power_method

A3 = np.array([[4.0, 1, 0], [1, 3, 1], [0, 1, 2]])       # eigenvalues 3 +- sqrt3, 3
EV3 = np.array([3 - np.sqrt(3), 3.0, 3 + np.sqrt(3)])
RNG = np.random.default_rng(11)


def sym(n, seed=0):
    r = np.random.default_rng(seed)
    M = r.standard_normal((n, n))
    return M + M.T


def test_the_reference_matrix_has_the_advertised_spectrum():
    np.testing.assert_allclose(np.sort(np.linalg.eigvalsh(A3)), EV3, atol=1e-12)


def test_rayleigh_quotient_and_angle():
    w, V = np.linalg.eigh(A3)
    for i in range(3):
        assert rayleigh_quotient(A3, V[:, i]) == pytest.approx(w[i])
    assert subspace_angle([1, 0, 0], [2, 0, 0]) == pytest.approx(0.0, abs=1e-12)
    assert subspace_angle([1, 0, 0], [-3, 0, 0]) == pytest.approx(0.0, abs=1e-12)
    assert subspace_angle([1, 0, 0], [0, 1, 0]) == pytest.approx(1.0)


# --------------------------------------------------------- the power method
def test_power_method_rate_is_lambda2_over_lambda1():
    """[S4] Thm 7.1 and Thm 7.5."""
    w = np.array([1.0, 0.85, 0.4, 0.05])
    Q = np.linalg.qr(RNG.standard_normal((4, 4)))[0]
    A = Q @ np.diag(w) @ Q.T
    x = RNG.standard_normal(4)
    errs, angles = [], []
    for _ in range(80):
        x = A @ x
        x /= np.linalg.norm(x)
        errs.append(abs(rayleigh_quotient(A, x) - w[0]))
        angles.append(subspace_angle(x, Q[:, 0]))
    errs, angles = np.array(errs), np.array(angles)
    keep = (angles > 1e-7) & (errs > 1e-13)
    errs, angles = errs[keep][5:], angles[keep][5:]
    ratio = w[1] / w[0]
    # the eigenvalue error of a symmetric matrix goes like the SQUARE of the
    # eigenvector angle, so it decays like (l2/l1)^{2l}; the angle like (l2/l1)^l
    assert (angles[1:] / angles[:-1]).mean() == pytest.approx(ratio, rel=0.05)
    assert (errs[1:] / errs[:-1]).mean() == pytest.approx(ratio ** 2, rel=0.1)


def test_power_method_fails_when_the_two_largest_have_equal_modulus():
    """[S4] Rem. 7.2(3)."""
    A = np.array([[0.0, -1.0], [1.0, 0.0]])              # eigenvalues +- i
    x = np.array([1.0, 0.3])
    seen = []
    for _ in range(60):
        x = A @ x
        x /= np.linalg.norm(x)
        seen.append(rayleigh_quotient(A, x))
    assert np.std(seen[-20:]) < 1e-12                     # it just cycles at 0
    assert not np.isclose(abs(seen[-1]), 1.0)             # never finds |lambda| = 1


# ----------------------------------------------------- inverse iteration
def test_inverse_iteration_finds_the_smallest_eigenvalue():
    """[S4] Alg. 18, Rem. 7.6."""
    lam, x = inverse_iteration(A3)
    assert lam == pytest.approx(EV3[0], abs=1e-10)
    np.testing.assert_allclose(A3 @ x, lam * x, atol=1e-9)


@pytest.mark.parametrize("mu", [0.0, 1.0, 2.9, 3.4, 4.5, 6.0])
def test_shifted_inverse_iteration_finds_the_closest_eigenvalue(mu):
    """[S4] Alg. 19, Thm 7.7."""
    lam, x = inverse_iteration_shift(A3, mu)
    expected = EV3[np.argmin(np.abs(EV3 - mu))]
    assert lam == pytest.approx(expected, abs=1e-9)


def test_shifted_inverse_iteration_rate():
    """[S4] Thm 7.7: rate |l_n - mu| / |l_{n-1} - mu|."""
    mu = 2.0
    lam, x, hist, _ = inverse_iteration_shift(A3, mu, x0=[1.0, 0.3, -0.2],
                                              iters=40, tol=0.0, history=True)
    target = EV3[np.argmin(np.abs(EV3 - mu))]
    d = np.sort(np.abs(EV3 - mu))
    rate = (d[0] / d[1]) ** 2       # eigenvalue error ~ (angle)^2 for symmetric A
    err = np.abs(hist - target)
    err = err[(err > 1e-13) & (err < 1e-2)]
    assert len(err) >= 4
    assert (err[1:] / err[:-1]).mean() == pytest.approx(rate, rel=0.3)


def test_rayleigh_quotient_iteration_is_cubic_for_symmetric_matrices():
    """[S4] Thm 7.8."""
    A = sym(6, seed=4)
    w, V = np.linalg.eigh(A)
    x0 = V[:, 3] + 0.15 * RNG.standard_normal(6)
    lam, x, hist, xs = rayleigh_quotient_iteration(A, x0, history=True)
    target = w[np.argmin(np.abs(w - lam))]
    ang = np.array([subspace_angle(xx, V[:, np.argmin(np.abs(w - target))]) for xx in xs])
    ang = ang[(ang > 1e-14) & (ang < 0.3)]
    assert len(ang) >= 2
    # cubic: log e_{k+1} ~ 3 log e_k
    slopes = np.log(ang[1:]) / np.log(ang[:-1])
    assert slopes.max() > 2.5


def test_rayleigh_quotient_iteration_is_quadratic_in_general():
    """[S4] Rem. 7.9: only quadratic for a general diagonalisable matrix."""
    A = RNG.standard_normal((5, 5))
    w, V = np.linalg.eig(A)
    i = int(np.argmax(w.real))
    x0 = V[:, i].real + 0.05 * RNG.standard_normal(5)
    lam, x = rayleigh_quotient_iteration(A, x0)
    assert np.min(np.abs(w - lam)) < 1e-8


# --------------------------------------------------------- stopping criteria
def test_residual_bounds_for_a_symmetric_matrix():
    """[S4] Thm 7.10(ii) and (iii)."""
    A = sym(5, seed=2)
    w, V = np.linalg.eigh(A)
    for eps in (1e-1, 1e-2, 1e-3):
        x = V[:, 2] + eps * RNG.standard_normal(5)
        d = eigen_residual_bound(A, x)
        assert d["distance"] <= d["bound_symmetric"] + 1e-14
        assert d["distance"] <= 100 * d["bound_rayleigh"] + 1e-14   # C ||r||^2


def test_residual_bound_needs_cond_T_for_a_nonsymmetric_matrix():
    """[S4] Thm 7.10(i): the symmetric bound ||r|| can fail badly."""
    A = np.array([[1.0, 1e4], [0.0, 1.0 + 1e-6]])        # nearly defective
    x = np.array([1.0, 1e-6])
    d = eigen_residual_bound(A, x, symmetric=False)
    assert d["cond_T"] > 1e3
    assert d["distance"] <= d["bound_general"] + 1e-12
    # and the symmetric bound is violated -- which is why (i) carries cond(T)
    assert d["distance"] > d["residual"]


# ---------------------------------------------------- orthogonal iteration
def test_orthogonal_iteration_converges_to_block_triangular_form():
    """[S4] Alg. 21, Thm 7.12, Rem. 7.13.

    Well-separated eigenvalues, so the |l_{k+1}/l_k| rates are all comfortably
    below 1; for a random matrix with a near-degenerate pair the same theorem
    predicts arbitrarily slow convergence.
    """
    Q0 = np.linalg.qr(RNG.standard_normal((6, 6)))[0]
    A = Q0 @ np.diag([32.0, 16.0, 8.0, 4.0, 2.0, 1.0]) @ Q0.T
    Q, offs = orthogonal_iteration(A, iters=300, history=True)
    assert offs[-1] < 1e-9
    assert offs[-1] < offs[10]
    assert np.all(np.diff(offs[5:]) <= 1e-12)              # monotone
    np.testing.assert_allclose(Q.T @ Q, np.eye(6), atol=1e-12)
    np.testing.assert_allclose(np.sort(np.diag(Q.T @ A @ Q)),
                               np.linalg.eigvalsh(A), atol=1e-8)


def test_orthogonal_iteration_on_a_subspace():
    A = sym(8, seed=6)
    w, V = np.linalg.eigh(A)
    Q = orthogonal_iteration(A, k=3, iters=800)
    assert Q.shape == (8, 3)
    dom = V[:, np.argsort(-np.abs(w))[:3]]
    # the two subspaces coincide: the projector onto them is the same
    np.testing.assert_allclose(Q @ Q.T, dom @ dom.T, atol=1e-5)


# ------------------------------------------------ Hessenberg and shifted QR
@pytest.mark.parametrize("n", [4, 6, 9])
def test_hessenberg_is_a_similarity_transformation(n):
    """[S4] sec. 7.6.1."""
    A = RNG.standard_normal((n, n))
    H, Q = hessenberg(A, return_q=True)
    np.testing.assert_allclose(np.tril(H, -2), 0.0, atol=1e-12)
    np.testing.assert_allclose(Q.T @ Q, np.eye(n), atol=1e-12)
    np.testing.assert_allclose(Q.T @ A @ Q, H, atol=1e-10)
    np.testing.assert_allclose(np.sort_complex(np.linalg.eigvals(H)),
                               np.sort_complex(np.linalg.eigvals(A)), atol=1e-9)


def test_hessenberg_matches_scipy():
    A = RNG.standard_normal((7, 7))
    H = hessenberg(A)
    np.testing.assert_allclose(np.abs(np.diag(H, -1)),
                               np.abs(np.diag(scipy.linalg.hessenberg(A), -1)), atol=1e-9)


def test_wilkinson_shift_is_an_eigenvalue_of_the_trailing_block():
    H = np.array([[1.0, 2.0, 3.0], [0.0, 4.0, 5.0], [0.0, 1.0, 6.0]])
    mu = wilkinson_shift(H)
    tb = H[-2:, -2:]
    assert np.min(np.abs(np.linalg.eigvals(tb) - mu)) < 1e-10


def test_shifted_qr_on_the_reference_matrix():
    """[S4] Alg. 24 with deflation."""
    ev, it = shifted_qr(A3, count=True)
    np.testing.assert_allclose(ev, EV3, atol=1e-10)
    assert it <= 12


@pytest.mark.parametrize("n", [5, 10, 20])
def test_shifted_qr_on_symmetric_matrices(n):
    A = sym(n, seed=n)
    ev, it = shifted_qr(A, count=True)
    np.testing.assert_allclose(ev, np.sort(np.linalg.eigvalsh(A)), atol=1e-9)
    assert it < 5 * n                                 # a few QR steps per eigenvalue


def test_shifted_qr_beats_the_unshifted_one():
    """The point of [S4] sec. 7.6.3: shifts make deflation happen quickly."""
    from qr_svd import qr_algorithm
    A = sym(8, seed=12)
    ev, it = shifted_qr(A, count=True)
    ref = np.sort(np.linalg.eigvalsh(A))
    unshifted = np.sort(qr_algorithm(A, iters=200))
    err_shifted = np.abs(ev - ref).max()
    err_unshifted = np.abs(unshifted - ref).max()
    assert it < 40                                    # ~2 QR steps per eigenvalue
    assert err_shifted < 1e-9
    # 200 unshifted steps on a matrix with close eigenvalues are still far off:
    # the unshifted rate is |l_{i+1}/l_i|, which shifts replace by quadratic
    # convergence of the last off-diagonal row ([S4] sec. 7.6.3)
    assert err_unshifted > 100 * err_shifted
