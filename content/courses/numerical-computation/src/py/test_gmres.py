"""Tests for gmres.py, against [S4] §8 (basic methods) and §8.2 (GMRES)."""
import numpy as np
import pytest
import scipy.sparse.linalg

from gmres import (arnoldi, gmres, gmres_restarted, cg_polynomial_bound,
                   richardson, steepest_descent_linear)
from linsolve import conjugate_gradient, poisson_1d

RNG = np.random.default_rng(17)


def nonsym(n, seed=0):
    """A non-symmetric matrix with a well-spread spectrum, so the Krylov basis
    stays well conditioned (a matrix close to a multiple of I makes the Arnoldi
    vectors nearly dependent and no Gram-Schmidt variant survives that)."""
    r = np.random.default_rng(seed)
    return (np.diag(np.linspace(1.0, 4.0, n)) + np.diag(np.ones(n - 1), 1)
            + np.diag(-0.5 * np.ones(n - 1), -1) + 0.1 * r.standard_normal((n, n)))


# --------------------------------------------------------------- Arnoldi
@pytest.mark.parametrize("n,m", [(10, 5), (20, 8), (30, 12)])
def test_arnoldi_relation_and_orthonormality(n, m):
    """[S4] Alg. 28: A V_k = V_{k+1} Hbar_k with V orthonormal, Hbar Hessenberg."""
    A = nonsym(n, seed=n)
    b = RNG.standard_normal(n)
    V, H, k = arnoldi(A, b, m)
    assert k == m
    np.testing.assert_allclose(V.T @ V, np.eye(k + 1), atol=1e-10)
    np.testing.assert_allclose(A @ V[:, :k], V @ H, atol=1e-10)
    np.testing.assert_allclose(np.tril(H, -2), 0.0, atol=1e-14)
    np.testing.assert_allclose(V[:, 0], b / np.linalg.norm(b), atol=1e-12)


def test_arnoldi_lucky_breakdown():
    """[S4] Rem. 8.12: h_{j+1,j} = 0 means K_j is A-invariant."""
    D = np.diag([1.0, 2.0, 3.0, 4.0])
    b = np.array([1.0, 1.0, 0.0, 0.0])            # only two eigendirections excited
    V, H, k = arnoldi(D, b, 4)
    assert k == 2
    np.testing.assert_allclose(D @ V[:, :k], V @ H, atol=1e-12)


def test_modified_gram_schmidt_keeps_orthogonality_better():
    """note 06: [S4] Alg. 28 is the *standard* Gram-Schmidt variant."""
    n, m = 40, 25
    A = nonsym(n, seed=21)
    b = RNG.standard_normal(n)
    Vm, _, _ = arnoldi(A, b, m, modified=True)
    Vc, _, _ = arnoldi(A, b, m, modified=False)
    loss_m = np.abs(Vm.T @ Vm - np.eye(m + 1)).max()
    loss_c = np.abs(Vc.T @ Vc - np.eye(m + 1)).max()
    assert loss_m <= loss_c
    assert loss_m < 1e-10


def test_arnoldi_accepts_a_matvec():
    n = 12
    A = nonsym(n, seed=3)
    b = RNG.standard_normal(n)
    V1, H1, _ = arnoldi(A, b, 5)
    V2, H2, _ = arnoldi(lambda x: A @ x, b, 5)
    np.testing.assert_allclose(V1, V2, atol=1e-12)
    np.testing.assert_allclose(H1, H2, atol=1e-12)


# ----------------------------------------------------------------- GMRES
@pytest.mark.parametrize("n", [8, 20, 40])
def test_gmres_solves_and_terminates_at_n(n):
    """[S4] (8.7): full GMRES is exact after at most n steps."""
    A = nonsym(n, seed=n + 1)
    b = RNG.standard_normal(n)
    x, res = gmres(A, b, history=True)
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-8)
    assert res[-1] < 1e-9 * max(1.0, res[0])
    assert len(res) - 1 <= n


def test_gmres_residuals_are_monotone():
    """GMRES minimises the residual over a growing space, so it cannot increase."""
    A = nonsym(30, seed=5)
    b = RNG.standard_normal(30)
    _, res = gmres(A, b, history=True)
    assert np.all(np.diff(res) <= 1e-12)


def test_gmres_matches_scipy():
    A = nonsym(25, seed=8)
    b = RNG.standard_normal(25)
    x = gmres(A, b)
    ref, info = scipy.sparse.linalg.gmres(A, b, rtol=1e-12, restart=25, maxiter=200)
    np.testing.assert_allclose(x, ref, atol=1e-7)
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-8)


def test_gmres_on_a_matrix_where_cg_has_no_theory():
    """[S4] sec. 8.2: GMRES needs only invertibility, CG needs SPD."""
    A = np.array([[0.0, 1.0], [-1.0, 0.0]])       # skew-symmetric, indefinite
    b = np.array([1.0, 2.0])
    np.testing.assert_allclose(gmres(A, b), np.linalg.solve(A, b), atol=1e-12)
    assert not np.allclose(A, A.T)                # CG's inner product does not exist


def test_gmres_lucky_breakdown_is_exact():
    D = np.diag([1.0, 2.0, 3.0, 4.0])
    b = np.array([1.0, 1.0, 0.0, 0.0])
    x, res = gmres(D, b, history=True)
    np.testing.assert_allclose(x, np.linalg.solve(D, b), atol=1e-12)
    assert len(res) - 1 <= 2                      # converged inside the invariant space


def test_gmres_with_an_initial_guess():
    A = nonsym(15, seed=2)
    b = RNG.standard_normal(15)
    exact = np.linalg.solve(A, b)
    x0 = exact + 1e-3 * RNG.standard_normal(15)
    x, res = gmres(A, b, x0=x0, history=True)
    np.testing.assert_allclose(x, exact, atol=1e-9)
    assert res[0] < 1.0                           # starts from a small residual


def test_restarted_gmres_converges():
    """[S4] Ex. 8.14."""
    A = nonsym(60, seed=6)
    b = RNG.standard_normal(60)
    x, res = gmres_restarted(A, b, m=10, history=True)
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-8)
    assert res[-1] < 1e-9 * res[0]


# ------------------------------------------------------------- the CG bound
def test_cg_bound_is_an_upper_bound_on_the_poisson_problem():
    """[S4] Thm 8.7: ||e_l||_A <= 2 ((sqrt k -1)/(sqrt k +1))^l ||e_0||_A."""
    n = 60
    A = poisson_1d(n)
    kappa = np.linalg.cond(A)
    rng = np.random.default_rng(1)
    b = rng.standard_normal(n)
    xstar = np.linalg.solve(A, b)
    x = np.zeros(n)
    e0 = xstar - x
    norm_A = lambda v: np.sqrt(v @ (A @ v))
    r, d = b - A @ x, b - A @ x
    for ell in range(1, 30):
        alpha = (r @ r) / (d @ (A @ d))
        x = x + alpha * d
        rn = r - alpha * (A @ d)
        beta = (rn @ rn) / (r @ r)
        d, r = rn + beta * d, rn
        assert norm_A(xstar - x) <= cg_polynomial_bound(kappa, ell) * norm_A(e0) + 1e-12


def test_cg_bound_predicts_sqrt_kappa_iterations():
    """O(sqrt kappa log(1/tol)) against O(kappa) for a stationary method."""
    need = {}
    for kappa in (25, 100, 400, 1600):
        need[kappa] = next(l for l in range(1, 100000)
                           if cg_polynomial_bound(kappa, l) < 1e-8)
    for k in (25, 100, 400):
        assert 1.8 < need[4 * k] / need[k] < 2.2      # quadrupling kappa doubles l


def test_cg_beats_the_bound_on_a_clustered_spectrum():
    """The min-max form of [S4] Thm 8.6 is sharper than the Chebyshev estimate."""
    n = 40
    Q = np.linalg.qr(RNG.standard_normal((n, n)))[0]
    w = np.concatenate([np.full(20, 1.0), np.full(20, 100.0)])  # two clusters
    A = Q @ np.diag(w) @ Q.T
    b = RNG.standard_normal(n)
    x, iters, res = conjugate_gradient(A, b, tol=1e-10, maxiter=n)
    np.testing.assert_allclose(A @ x, b, atol=1e-6)
    # two distinct eigenvalues => CG is exact in (at most) two steps, while the
    # Chebyshev bound of Thm 8.7 for kappa = 100 is still ~0.5 after two steps
    assert iters <= 4
    assert cg_polynomial_bound(100.0, 2) > 1e-1


# ==================== [S4] §8: the basic iterative methods ====================


def test_richardson_converges_when_scaled_and_diverges_otherwise():
    """[S4] sec. 8: the basic methods "do not always converge"."""
    A = poisson_1d(20)
    b = np.ones(20)
    lmax = np.linalg.eigvalsh(A).max()
    x, k = richardson(A, b, omega=1.0 / lmax, maxiter=20000)
    np.testing.assert_allclose(A @ x, b, atol=1e-8)
    assert k > 100                                        # slow
    xbad, kbad = richardson(A, b, omega=2.0 / lmax * 1.5, maxiter=200)
    assert not np.all(np.isfinite(xbad)) or np.linalg.norm(A @ xbad - b) > 1.0


def test_steepest_descent_is_order_kappa_and_cg_is_order_sqrt_kappa():
    """[S4] Lem. 6.23 vs Thm 8.7 -- the argument for CG."""
    counts_sd, counts_cg = {}, {}
    for n in (10, 20, 40):
        A = poisson_1d(n)
        b = np.ones(n)
        _, counts_sd[n] = steepest_descent_linear(A, b, tol=1e-8, maxiter=200000)
        _, counts_cg[n], _ = conjugate_gradient(A, b, tol=1e-8)
    # kappa ~ n^2, so steepest descent ~ n^2 and CG ~ n
    assert counts_sd[40] / counts_sd[10] > 8              # ~16 if quadratic
    assert counts_cg[40] / counts_cg[10] < 6              # ~4 if linear
    assert counts_cg[40] < counts_sd[40] / 20


def test_steepest_descent_directions_are_euclidean_orthogonal():
    """[S4] sec. 8: consecutive gradient directions are (.,.)_2-orthogonal."""
    A = poisson_1d(12)
    b = np.ones(12)
    x = np.zeros(12)
    prev = None
    for _ in range(6):
        r = b - A @ x
        if prev is not None:
            assert abs(float(prev @ r)) < 1e-10 * np.linalg.norm(prev) * np.linalg.norm(r)
        x = x + (float(r @ r) / float(r @ (A @ r))) * r
        prev = r
