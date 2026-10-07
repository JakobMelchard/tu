import numpy as np
import pytest
import scipy.linalg

from linsolve import (forward_substitution, back_substitution, gauss_elim, lu_decompose, lu_unpack, lu_solve, solve,
                      determinant, cholesky, cholesky_solve, jacobi, gauss_seidel,
                      sor, sor_optimal_omega, conjugate_gradient, power_iteration,
                      iteration_matrix, poisson_1d)


@pytest.fixture
def system():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((8, 8))
    b = rng.standard_normal(8)
    return A, b


def test_gauss_elim_matches_numpy(system):
    A, b = system
    np.testing.assert_allclose(gauss_elim(A, b), np.linalg.solve(A, b), rtol=1e-10)


def test_lu_reproduces_matrix_and_scipy(system):
    A, _ = system
    LU, piv = lu_decompose(A)
    P, L, U = lu_unpack(LU, piv)
    np.testing.assert_allclose(P @ A, L @ U, atol=1e-12)
    assert np.all(np.abs(L[np.tril_indices(8, -1)]) <= 1.0)       # partial pivoting
    Ps, Ls, Us = scipy.linalg.lu(A)
    np.testing.assert_allclose(np.abs(np.diag(U)), np.abs(np.diag(Us)), rtol=1e-10)


def test_lu_solve_and_det(system):
    A, b = system
    LU, piv = lu_decompose(A)
    np.testing.assert_allclose(lu_solve(LU, piv, b), np.linalg.solve(A, b), rtol=1e-10)
    np.testing.assert_allclose(determinant(A), np.linalg.det(A), rtol=1e-10)


def test_lu_needs_pivoting():
    A = np.array([[0.0, 1.0], [1.0, 0.0]])
    np.testing.assert_allclose(solve(A, [2.0, 3.0]), [3.0, 2.0])
    with pytest.raises(ValueError):
        lu_decompose(np.array([[1.0, 2.0], [2.0, 4.0]]))


def test_cholesky_matches_numpy():
    rng = np.random.default_rng(1)
    B = rng.standard_normal((6, 6))
    A = B @ B.T + 6 * np.eye(6)
    L = cholesky(A)
    np.testing.assert_allclose(L, np.linalg.cholesky(A), atol=1e-12)
    b = rng.standard_normal(6)
    np.testing.assert_allclose(cholesky_solve(L, b), np.linalg.solve(A, b), rtol=1e-10)
    with pytest.raises(ValueError):
        cholesky(np.array([[1.0, 2.0], [2.0, 1.0]]))       # indefinite


@pytest.mark.parametrize("method", [jacobi, gauss_seidel])
def test_stationary_iterations_converge(method):
    A = poisson_1d(10)
    b = np.ones(10)
    x, k, hist = method(A, b, tol=1e-10)
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-8)
    assert np.all(np.diff(hist[:50]) <= 1e-14)               # monotone residual


def test_spectral_radii_of_poisson():
    n = 10
    A = poisson_1d(n)
    rho_j = power_iteration(iteration_matrix(A, "jacobi"))
    assert abs(rho_j - np.cos(np.pi / (n + 1))) < 1e-8
    rho_gs = power_iteration(iteration_matrix(A, "gauss_seidel"))
    assert abs(rho_gs - rho_j ** 2) < 1e-6                  # GS = Jacobi^2 (Young)
    ev = np.max(np.abs(np.linalg.eigvals(iteration_matrix(A, "jacobi"))))
    assert abs(rho_j - ev) < 1e-8


def test_sor_faster_than_gauss_seidel():
    A = poisson_1d(30)
    b = np.ones(30)
    w = sor_optimal_omega(np.cos(np.pi / 31))
    _, k_gs, _ = gauss_seidel(A, b, tol=1e-8)
    x, k_sor, _ = sor(A, b, omega=w, tol=1e-8)
    assert k_sor < k_gs / 5
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-6)


def test_cg_exact_in_n_steps_and_matrix_free():
    n = 25
    A = poisson_1d(n)
    b = np.sin(np.arange(1, n + 1))
    x, k, hist = conjugate_gradient(A, b, tol=1e-12)
    assert k <= n
    np.testing.assert_allclose(x, np.linalg.solve(A, b), atol=1e-9)
    mv = lambda v: 2 * v - np.concatenate([v[1:], [0]]) - np.concatenate([[0], v[:-1]])
    x2, _, _ = conjugate_gradient(None, b, matvec=mv, tol=1e-12)
    np.testing.assert_allclose(x2, x, atol=1e-9)


def test_cg_convergence_bound():
    n = 40
    A = poisson_1d(n)
    b = np.ones(n)
    x_star = np.linalg.solve(A, b)
    ev = np.linalg.eigvalsh(A)
    kappa = ev[-1] / ev[0]
    rate = (np.sqrt(kappa) - 1) / (np.sqrt(kappa) + 1)
    e0 = np.sqrt(x_star @ A @ x_star)
    for k in (5, 10, 15):
        x, _, _ = conjugate_gradient(A, b, maxiter=k, tol=0)
        e = x - x_star
        assert np.sqrt(e @ A @ e) <= 2 * rate ** k * e0 * (1 + 1e-10)


# ============================ [S4] §8.1: CG directions =====================
def test_cg_search_directions_are_a_orthogonal():
    """[S4] Lem. 8.3: the CG directions are conjugate, (d_i, d_j)_A = 0."""
    A = poisson_1d(15)
    b = np.random.default_rng(0).standard_normal(15)
    x = np.zeros(15)
    r = b - A @ x
    d = r.copy()
    ds = []
    for _ in range(8):
        Ad = A @ d
        alpha = (r @ r) / (d @ Ad)
        x = x + alpha * d
        rn = r - alpha * Ad
        ds.append(d.copy())
        d = rn + ((rn @ rn) / (r @ r)) * d
        r = rn
    for i in range(len(ds)):
        for j in range(i + 1, len(ds)):
            denom = np.sqrt(ds[i] @ (A @ ds[i])) * np.sqrt(ds[j] @ (A @ ds[j]))
            assert abs(float(ds[i] @ (A @ ds[j]))) < 1e-8 * denom


def test_substitution_matches_scipy_solve_triangular():
    """[S4 §4.1]: O(n^2) forward and back substitution."""
    r = np.random.default_rng(3)
    n = 8
    L = np.tril(r.standard_normal((n, n))) + n * np.eye(n)
    U = np.triu(r.standard_normal((n, n))) + n * np.eye(n)
    b = r.standard_normal(n)
    np.testing.assert_allclose(forward_substitution(L, b),
                               scipy.linalg.solve_triangular(L, b, lower=True))
    np.testing.assert_allclose(back_substitution(U, b),
                               scipy.linalg.solve_triangular(U, b, lower=False))
    Lu = np.tril(L, -1) + np.eye(n)
    np.testing.assert_allclose(forward_substitution(L, b, unit_diag=True),
                               scipy.linalg.solve_triangular(Lu, b, lower=True,
                                                             unit_diagonal=True))
