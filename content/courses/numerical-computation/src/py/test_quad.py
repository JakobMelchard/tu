import math

import numpy as np
import pytest
import scipy.integrate
import scipy.special

from quad import (newton_cotes_weights, newton_cotes, midpoint, trapezoid, simpson,
                  legendre, gauss_legendre, gauss_quad, romberg, adaptive_simpson,
                  adaptive_trapezoid, graded_mesh, composite_trapezoid_mesh,
                  gauss_jacobi, gauss_chebyshev)

EXACT = np.e - 1


def test_newton_cotes_weights():
    np.testing.assert_allclose(newton_cotes_weights(1), [0.5, 0.5], atol=1e-14)
    np.testing.assert_allclose(newton_cotes_weights(2) * 6, [1, 4, 1], atol=1e-13)
    np.testing.assert_allclose(newton_cotes_weights(3) * 8, [1, 3, 3, 1], atol=1e-13)
    assert newton_cotes_weights(8).min() < 0                  # weights turn negative
    assert abs(newton_cotes(np.exp, 0, 1, 4) - EXACT) < 1e-6


@pytest.mark.parametrize("rule, p", [(midpoint, 2), (trapezoid, 2), (simpson, 4)])
def test_composite_orders(rule, p):
    e1 = abs(rule(np.exp, 0, 1, 8) - EXACT)
    e2 = abs(rule(np.exp, 0, 1, 16) - EXACT)
    assert abs(np.log2(e1 / e2) - p) < 0.1


def test_composite_matches_scipy():
    x = np.linspace(0, 1, 17)
    np.testing.assert_allclose(trapezoid(np.exp, 0, 1, 16),
                               scipy.integrate.trapezoid(np.exp(x), x), rtol=1e-14)
    np.testing.assert_allclose(simpson(np.exp, 0, 1, 16),
                               scipy.integrate.simpson(np.exp(x), x=x), rtol=1e-14)


def test_simpson_exact_for_cubics():
    assert abs(simpson(lambda x: x ** 3 - 2 * x, 0, 2, 2) - 0.0) < 1e-14
    with pytest.raises(ValueError):
        simpson(np.exp, 0, 1, 3)


def test_legendre_recurrence_against_scipy():
    x = np.linspace(-0.9, 0.9, 7)
    for n in (2, 5, 8):
        p, dp = legendre(n, x)
        np.testing.assert_allclose(p, scipy.special.eval_legendre(n, x), atol=1e-14)
        P = np.polynomial.legendre.Legendre.basis(n)
        np.testing.assert_allclose(dp, P.deriv()(x), atol=1e-12)


@pytest.mark.parametrize("n", [1, 2, 3, 5, 10, 20])
def test_gauss_legendre_nodes_weights(n):
    x, w = gauss_legendre(n)
    xr, wr = np.polynomial.legendre.leggauss(n)
    np.testing.assert_allclose(x, xr, atol=1e-14)
    np.testing.assert_allclose(w, wr, atol=1e-14)
    # exact for degree 2n-1, not for 2n
    for k in range(2 * n):
        assert abs(w @ x ** k - (2 / (k + 1) if k % 2 == 0 else 0)) < 1e-12
    # for f = x^(2n): error = 2^(2n+1) (n!)^4 / ((2n+1) ((2n)!)^2)  (f^(2n) = (2n)!)
    E = 2.0 ** (2 * n + 1) * math.factorial(n) ** 4 / ((2 * n + 1) * math.factorial(2 * n) ** 2)
    err = abs(w @ x ** (2 * n) - 2 / (2 * n + 1))
    assert abs(err - E) < 1e-3 * E + 1e-14


def test_gauss_quad_spectral():
    assert abs(gauss_quad(np.exp, 0, 1, 6) - EXACT) < 1e-12
    ref, _ = scipy.integrate.quad(lambda x: np.cos(x ** 2), 0, 3)
    assert abs(gauss_quad(lambda x: np.cos(x ** 2), 0, 3, 30) - ref) < 1e-10


def test_romberg_tableau():
    T = romberg(np.exp, 0, 1, 5)
    assert abs(T[1, 1] - simpson(np.exp, 0, 1, 2)) < 1e-14      # T[1,1] is Simpson
    assert abs(T[4, 4] - EXACT) < 1e-12
    assert np.all(np.diff(np.abs(np.diag(T) - EXACT)) < 0)


def test_adaptive_simpson_cusp():
    f = lambda x: np.sqrt(np.abs(x))
    exact = 2 / 3 + 2 / 3 * 2 ** 1.5
    I, nev = adaptive_simpson(f, -1, 2, tol=1e-9)
    assert abs(I - exact) < 1e-8
    ref, _ = scipy.integrate.quad(f, -1, 2, points=[0])
    assert abs(I - ref) < 1e-8
    I2, nev2 = adaptive_simpson(np.exp, 0, 1, tol=1e-9)
    assert nev2 < nev / 10 and abs(I2 - EXACT) < 1e-9        # smooth needs far fewer


# ============ [S4] sec. 2.3, 2.5, 2.7: adaptivity, grading, weights ==========


def test_s4_algorithm_5_adaptive_trapezoid():
    """[S4] Alg. 5: trapezoid checked against Simpson, bisect on failure."""
    val, nev = adaptive_trapezoid(np.exp, 0.0, 1.0, 1e-4)
    assert val == pytest.approx(np.e - 1, abs=1e-6)
    assert nev > 3
    val2, nev2 = adaptive_trapezoid(np.exp, 0.0, 1.0, 1e-6)
    assert abs(val2 - (np.e - 1)) <= abs(val - (np.e - 1)) + 1e-12
    assert nev2 > nev                                    # tighter tau costs more


def test_adaptive_trapezoid_concentrates_on_the_hard_part():
    f = lambda x: np.sqrt(abs(x))
    val, nev = adaptive_trapezoid(f, -1.0, 2.0, 1e-5)
    exact = 2.0 / 3.0 * (1.0 + 2.0 ** 1.5)
    assert val == pytest.approx(exact, abs=1e-4)


def test_graded_mesh_restores_the_order_for_a_singular_integrand():
    """[S4] Ex. 2.12: int_0^1 x^0.1 is O(N^-1.1) uniform, O(N^-2) graded."""
    exact = 1.0 / 1.1
    f = lambda x: x ** 0.1
    Ns = np.array([50, 100, 200, 400, 800])
    eu = np.array([abs(composite_trapezoid_mesh(f, np.linspace(0, 1, N + 1)) - exact)
                   for N in Ns])
    eg = np.array([abs(composite_trapezoid_mesh(f, graded_mesh(N, 2.0)) - exact)
                   for N in Ns])
    ru = np.log2(eu[:-1] / eu[1:]).mean()
    rg = np.log2(eg[:-1] / eg[1:]).mean()
    assert ru == pytest.approx(1.1, abs=0.15)
    assert rg == pytest.approx(2.0, abs=0.15)
    assert eg[-1] < eu[-1] / 100


def test_trapezoid_is_exceptional_for_periodic_integrands():
    """[S4] sec. 2.5, Ex. 2.20: f1 = sin(pi x), f2 = cos(pi x)^10, f3 = exp(sin(8 pi x))
    on [-1, 1].  All Euler-Maclaurin boundary terms cancel over a full period."""
    T = lambda f, N: composite_trapezoid_mesh(f, np.linspace(-1.0, 1.0, N + 1))

    # f1 is a trigonometric polynomial of degree 1: exact from N = 4 on
    for N in (4, 8, 16, 64):
        assert abs(T(lambda x: np.sin(np.pi * x), N)) < 1e-13

    # f2 = cos^10 is a trigonometric polynomial of degree 10: exact once N > 20
    ref = scipy.integrate.quad(lambda x: np.cos(np.pi * x) ** 10, -1, 1)[0]
    for N in (32, 64):
        assert T(lambda x: np.cos(np.pi * x) ** 10, N) == pytest.approx(ref, abs=1e-12)
    assert abs(T(lambda x: np.cos(np.pi * x) ** 10, 8) - ref) > 1e-6     # too coarse

    # f3 is analytic and periodic: convergence is faster than any power of h
    f3 = lambda x: np.exp(np.sin(8 * np.pi * x))
    ref3 = scipy.integrate.quad(f3, -1, 1, limit=400)[0]
    e = [abs(T(f3, N) - ref3) for N in (64, 128, 256)]
    assert e[2] < 1e-12
    assert e[0] / e[1] > 50                              # not an O(h^2) factor of 4
    # and Simpson, which is better for smooth non-periodic integrands, is not here
    assert abs(simpson(f3, -1.0, 1.0, 128) - ref3) > e[1]


def test_gauss_jacobi_reduces_to_legendre():
    """[S4] sec. 2.7.1: alpha = beta = 0 is Legendre."""
    for n in (2, 4, 7):
        x, w = gauss_jacobi(n, 0.0, 0.0)
        xr, wr = gauss_legendre(n)
        np.testing.assert_allclose(x, xr, atol=1e-10)
        np.testing.assert_allclose(w, wr, atol=1e-10)


def test_gauss_chebyshev_closed_form_and_exactness():
    """[S4] sec. 2.7.1: alpha = beta = -1/2, x_i = cos((2i+1)pi/2n), w_i = pi/n."""
    for n in (2, 4, 8):
        x, w = gauss_chebyshev(n)
        np.testing.assert_allclose(x, np.sort(np.cos((2 * np.arange(n) + 1) * np.pi / (2 * n))))
        np.testing.assert_allclose(w, np.pi / n)
        np.testing.assert_allclose(gauss_jacobi(n, -0.5, -0.5)[0], x, atol=1e-12)
        # exact on P_{2n-1} for the weighted integral
        for k in range(2 * n):
            got = float(w @ (x ** k))
            ref = 0.0 if k % 2 else np.pi * np.prod([(2 * j - 1) / (2 * j)
                                                     for j in range(1, k // 2 + 1)])
            assert got == pytest.approx(ref, abs=1e-10)


def test_gauss_jacobi_weighted_exactness():
    """[S4] Thm 2.26: exact on P_{2n-1} for int omega(x) f(x) dx."""
    from math import gamma
    n, alpha, beta = 4, 1.0, 0.5
    x, w = gauss_jacobi(n, alpha, beta)
    assert np.all(w > 0)                                  # positive weights
    for k in range(2 * n):
        got = float(w @ (x ** k))
        ref = scipy.integrate.quad(
            lambda t: (1 - t) ** alpha * (1 + t) ** beta * t ** k, -1, 1)[0]
        assert got == pytest.approx(ref, abs=1e-8)
