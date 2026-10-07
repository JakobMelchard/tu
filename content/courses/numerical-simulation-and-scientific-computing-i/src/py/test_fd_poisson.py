"""FD derivatives, quadrature and Poisson solvers of fd_poisson.py.

Observed orders against the theory [S23]; solutions against scipy.sparse.linalg.spsolve
and integrals against scipy.integrate.quad.
"""
import numpy as np
import scipy.integrate as si
import scipy.sparse.linalg as spla

from fd_poisson import (convergence_order, fd_derivative, fd_second_derivative, poisson1d,
                        poisson1d_matrix, poisson2d, poisson2d_matrix, quad_composite, thomas)


def test_derivative_orders():
    f = np.sin
    x = 0.7
    hs = np.array([1e-1, 5e-2, 2.5e-2, 1.25e-2])
    for scheme, order in [("forward", 1), ("central", 2)]:
        err = np.array([abs(fd_derivative(f, x, h, scheme) - np.cos(x)) for h in hs])
        assert np.allclose(convergence_order(err), order, atol=0.1)
    err2 = np.array([abs(fd_second_derivative(f, x, h) + np.sin(x)) for h in hs])
    assert np.allclose(convergence_order(err2), 2, atol=0.1)


def test_quadrature_orders_and_scipy():
    f = lambda x: np.exp(x) * np.cos(3 * x)
    exact = si.quad(f, 0, 1)[0]
    ns = [8, 16, 32, 64]
    for rule, order in [("midpoint", 2), ("trapezoid", 2), ("simpson", 4)]:
        err = np.array([abs(quad_composite(f, 0, 1, n, rule) - exact) for n in ns])
        assert np.allclose(convergence_order(err), order, atol=0.15), rule


def test_quadrature_error_constants_euler_maclaurin():
    """Note 03's worked-example table, checked against the leading Euler-Maclaurin
    terms: T_h - I = h^2/12 (f'(b) - f'(a)) + O(h^4), M_h - I = -h^2/24 (f'(b) - f'(a))."""
    f = lambda x: np.exp(x) * np.cos(3 * x)
    fp = lambda x: np.exp(x) * (np.cos(3 * x) - 3 * np.sin(3 * x))
    F = lambda x: np.exp(x) * (np.cos(3 * x) + 3 * np.sin(3 * x)) / 10   # antiderivative
    exact = F(1.0) - F(0.0)
    for n in (16, 32, 64):
        h, d = 1.0 / n, fp(1.0) - fp(0.0)
        assert abs((quad_composite(f, 0, 1, n, "trapezoid") - exact) / (h**2 / 12 * d) - 1) < 0.01
        assert abs((quad_composite(f, 0, 1, n, "midpoint") - exact) / (-(h**2) / 24 * d) - 1) < 0.01
    # the table rows themselves (n = 8: midpoint 3.2e-3, trapezoid 6.3e-3, Simpson 1.4e-4)
    errs = [abs(quad_composite(f, 0, 1, 8, r) - exact) for r in ("midpoint", "trapezoid", "simpson")]
    assert np.allclose(errs, [3.18e-3, 6.34e-3, 1.42e-4], rtol=0.01)


def test_thomas_matches_dense_solve():
    rng = np.random.default_rng(0)
    n = 50
    sub, diag, sup = rng.random(n), 4 + rng.random(n), rng.random(n)
    A = np.diag(diag) + np.diag(sub[1:], -1) + np.diag(sup[:-1], 1)
    b = rng.random(n)
    assert np.allclose(thomas(sub, diag, sup, b), np.linalg.solve(A, b))


def test_poisson1d_second_order_and_scipy():
    u_ex = lambda x: np.sin(np.pi * x) + x
    f = lambda x: np.pi**2 * np.sin(np.pi * x)
    errs = []
    for N in [16, 32, 64, 128]:
        x, u = poisson1d(f, N, 0.0, 1.0)
        errs.append(np.max(np.abs(u - u_ex(x))))
        # same linear system solved by scipy's sparse direct solver
        rhs = f(x[1:-1]).copy()
        rhs[-1] += 1.0 * N**2
        assert np.allclose(u[1:-1], spla.spsolve(poisson1d_matrix(N), rhs))
    assert np.allclose(convergence_order(errs), 2, atol=0.05)


def test_poisson2d_second_order():
    f = lambda X, Y: 2 * np.pi**2 * np.sin(np.pi * X) * np.sin(np.pi * Y)
    errs = []
    for N in [8, 16, 32, 64]:
        X, Y, U = poisson2d(f, N)
        errs.append(np.max(np.abs(U - np.sin(np.pi * X) * np.sin(np.pi * Y))))
    assert np.allclose(convergence_order(errs), 2, atol=0.05)
    A = poisson2d_matrix(8)
    assert (A != A.T).nnz == 0 and np.all(spla.eigsh(A, k=1, which="SA")[0] > 0)  # SPD
