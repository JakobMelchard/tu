"""Tests for optimize.py, against [S4] sec. 6.5-6.8."""
import numpy as np
import pytest
import scipy.optimize

from optimize import (armijo, steepest_descent, gradient_descent_quadratic,
                      globalized_newton, gauss_newton, sherman_morrison,
                      broyden_update, broyden, s4_example_6_20)

RNG = np.random.default_rng(13)


# -------------------------------------------------------------- Armijo
def test_armijo_returns_a_step_with_sufficient_descent():
    """[S4] (6.13)."""
    g = lambda x: float(x @ x)
    gg = lambda x: 2.0 * x
    for x0 in ([1.0, 2.0], [10.0, -3.0], [0.1, 0.1]):
        x = np.array(x0)
        d = -gg(x)
        lam, trials = armijo(g, gg, x, d)
        assert 0 < lam <= 1.0
        assert g(x + lam * d) < g(x) + 1e-4 * (gg(x) @ d) * lam
        assert trials >= 1


def test_armijo_rejects_an_ascent_direction():
    g = lambda x: float(x @ x)
    gg = lambda x: 2.0 * x
    with pytest.raises(ValueError):
        armijo(g, gg, np.array([1.0, 1.0]), np.array([1.0, 1.0]))


def test_steepest_descent_finds_a_minimum():
    f = lambda x: float((x[0] - 1) ** 2 + 3 * (x[1] + 2) ** 2)
    df = lambda x: np.array([2 * (x[0] - 1), 6 * (x[1] + 2)])
    x = steepest_descent(f, df, [5.0, 5.0], iters=2000)
    np.testing.assert_allclose(x, [1.0, -2.0], atol=1e-5)


# -------------------------------------- gradient method on a quadratic
def test_gradient_descent_on_a_quadratic_has_the_predicted_rate():
    """[S4] sec. 6.8.1, Lem. 6.23: the error contracts by (kappa-1)/(kappa+1)."""
    for kappa in (10.0, 100.0):
        Q = np.diag(np.linspace(1.0, kappa, 5))
        V = np.linalg.qr(RNG.standard_normal((5, 5)))[0]
        Q = V @ Q @ V.T
        x0 = RNG.standard_normal(5)
        _, hist = gradient_descent_quadratic(Q, np.zeros(5), 0.0, x0,
                                             iters=5000, history=True)
        err = np.linalg.norm(hist, axis=1)
        err = err[err > 1e-9]
        half = len(err) // 2
        rate = (err[-1] / err[half]) ** (1.0 / (len(err) - 1 - half))
        assert rate == pytest.approx((kappa - 1) / (kappa + 1), rel=0.05)


def test_gradient_descent_reaches_the_exact_minimiser():
    """[S4] Rem. 6.24: the minimiser of the quadratic solves Q x = -c."""
    Q = np.array([[4.0, 1.0], [1.0, 3.0]])
    c = np.array([-1.0, 2.0])
    x = gradient_descent_quadratic(Q, c, 0.0, [0.0, 0.0], iters=5000)
    np.testing.assert_allclose(x, np.linalg.solve(Q, -c), atol=1e-8)


# --------------------------------------------------- globalised Newton
def test_globalized_newton_where_plain_newton_diverges():
    """[S4] Alg. 15 on arctan from x0 = 3."""
    f = lambda x: np.arctan(x)
    j = lambda x: np.array([[1.0 / (1.0 + float(x[0]) ** 2)]])
    x, hist, lams = globalized_newton(f, j, [3.0], history=True)
    assert abs(x[0]) < 1e-10
    assert len(hist) - 1 <= 12
    assert lams[0] < 1.0                               # damped at first
    assert lams[-1] == pytest.approx(1.0)              # full Newton steps at the end
    # plain Newton from the same start blows up
    xn = np.array([3.0])
    for _ in range(6):
        xn = xn - np.arctan(xn) * (1.0 + xn ** 2)
    assert abs(xn[0]) > 1e10


def test_globalized_newton_on_a_system():
    F, J, x0, xstar = s4_example_6_20()
    x = globalized_newton(F, J, [2.0, 3.0])
    np.testing.assert_allclose(F(x), 0.0, atol=1e-9)


def test_globalized_newton_keeps_quadratic_convergence_near_the_root():
    F, J, x0, xstar = s4_example_6_20()
    x, hist, lams = globalized_newton(F, J, x0, history=True)
    np.testing.assert_allclose(x, xstar, atol=1e-10)
    err = np.linalg.norm(hist - xstar, axis=1)
    err = err[err > 1e-14]
    assert np.all(lams[-2:] == pytest.approx(1.0))
    assert err[-1] < err[-2] ** 1.8                    # quadratic at the end


# ------------------------------------------------------- Gauss-Newton
def _expfit():
    t = np.linspace(0, 2, 11)
    model = lambda p: p[0] * np.exp(p[1] * t)
    J = lambda p: np.column_stack([np.exp(p[1] * t), p[0] * t * np.exp(p[1] * t)])
    return t, model, J


def test_gauss_newton_is_quadratic_for_a_zero_residual_problem():
    """[S4] Thm 6.17, first half."""
    t, model, J = _expfit()
    truth = np.array([2.0, -1.0])
    data = model(truth)
    F = lambda p: model(p) - data
    x, hist = gauss_newton(F, J, [1.0, -0.5], history=True)
    np.testing.assert_allclose(x, truth, atol=1e-10)
    err = np.linalg.norm(hist - truth, axis=1)
    err = err[err > 1e-13]
    assert len(err) >= 3
    assert err[-1] < err[-2] ** 1.7                    # order ~ 2


def test_gauss_newton_is_only_linear_for_a_large_residual_problem():
    """[S4] Thm 6.17, second half."""
    t, model, J = _expfit()
    data = model([2.0, -1.0]) + 0.5 * np.sin(6 * t)
    F = lambda p: model(p) - data
    x, hist = gauss_newton(F, J, [1.0, -0.5], iters=200, history=True)
    err = np.linalg.norm(hist[:-1] - x, axis=1)
    err = err[err > 1e-12]
    ratios = err[1:] / err[:-1]
    assert np.all(F(x) != 0.0)                         # residual really is non-zero
    assert 0.0 < np.median(ratios) < 0.9               # linear, not quadratic
    assert err[-1] > err[-2] ** 1.5                    # NOT quadratic


def test_gauss_newton_matches_scipy_least_squares():
    t, model, J = _expfit()
    data = model([2.0, -1.0]) + 0.05 * np.cos(4 * t)
    F = lambda p: model(p) - data
    x = gauss_newton(F, J, [1.0, -0.5], iters=200)
    ref = scipy.optimize.least_squares(F, [1.0, -0.5]).x
    np.testing.assert_allclose(x, ref, atol=1e-6)


def test_gauss_newton_reduces_to_newton_in_1d():
    """[S4] Exercise 6.18."""
    f = lambda x: np.array([x[0] ** 2 - 2.0])
    J = lambda x: np.array([[2 * x[0]]])
    x, hist = gauss_newton(f, J, [2.0], history=True)
    assert x[0] == pytest.approx(np.sqrt(2), abs=1e-12)
    np.testing.assert_allclose(hist[1:4, 0],
                               [1.5, 1.4166666666666667, 1.4142156862745097], atol=1e-12)


# ------------------------------------------------------------- Broyden
def test_sherman_morrison():
    """[S4] (6.23)."""
    A = RNG.standard_normal((5, 5)) + 5 * np.eye(5)
    u, v = RNG.standard_normal(5), RNG.standard_normal(5)
    np.testing.assert_allclose(sherman_morrison(np.linalg.inv(A), u, v),
                               np.linalg.inv(A + np.outer(u, v)), atol=1e-9)


def test_broyden_update_satisfies_the_secant_condition():
    """[S4] (6.20), (6.22)."""
    H = RNG.standard_normal((4, 4))
    s, y = RNG.standard_normal(4), RNG.standard_normal(4)
    Hp = broyden_update(H, s, y)
    np.testing.assert_allclose(Hp @ s, y, atol=1e-12)


def test_broyden_update_is_the_frobenius_closest_such_matrix():
    """[S4] Lem. 6.19: unique minimiser of ||A - H||_F subject to A s = y."""
    H = RNG.standard_normal((4, 4))
    s, y = RNG.standard_normal(4), RNG.standard_normal(4)
    Hp = broyden_update(H, s, y)
    best = np.linalg.norm(Hp - H, "fro")
    for _ in range(200):
        Z = RNG.standard_normal((4, 4))
        Z = Z - np.outer(Z @ s - (Hp @ s), s) / (s @ s)   # project onto A s = y
        np.testing.assert_allclose(Z @ s, y, atol=1e-9)
        assert np.linalg.norm(Z - H, "fro") >= best - 1e-9


def test_broyden_converges_superlinearly_on_s4_example_6_20():
    """[S4] Ex. 6.20: x* = (0, 1), x0 = (-0.5, 1.4), H0 = F'(x0)."""
    F, J, x0, xstar = s4_example_6_20()
    np.testing.assert_allclose(F(xstar), 0.0, atol=1e-14)
    x, hist = broyden(F, x0, H0=J(x0), history=True)
    np.testing.assert_allclose(x, xstar, atol=1e-10)
    err = np.linalg.norm(hist - xstar, axis=1)
    err = err[err > 1e-14]
    ratios = err[1:] / err[:-1]
    assert ratios[-1] < ratios[0]                      # superlinear: the ratio -> 0
    assert ratios[-1] < 1e-2


def test_broyden_is_slower_than_newton_and_faster_than_steepest_descent():
    """The ordering [S4] Fig. 6.3 shows."""
    F, J, x0, xstar = s4_example_6_20()
    _, hb = broyden(F, x0, H0=J(x0), history=True)
    xn = x0.copy()
    en = []
    for _ in range(8):
        xn = xn - np.linalg.solve(J(xn), F(xn))
        en.append(np.linalg.norm(xn - xstar))
    eb = np.linalg.norm(hb - xstar, axis=1)
    _, hs = steepest_descent(lambda p: float(F(p) @ F(p)),
                             lambda p: 2.0 * J(p).T @ F(p), x0, iters=8,
                             sigma=0.9, q=0.5, history=True)
    es = np.linalg.norm(hs - xstar, axis=1)
    assert en[3] < eb[4]                               # Newton ahead at step 4
    assert eb[-1] < es[-1]                             # Broyden far ahead of descent
    assert es[-1] > 1e-3                               # descent has barely moved


def test_broyden_with_and_without_sherman_morrison_agree():
    F, J, x0, _ = s4_example_6_20()
    a = broyden(F, x0, H0=J(x0), use_sm=True)
    b = broyden(F, x0, H0=J(x0), use_sm=False)
    np.testing.assert_allclose(a, b, atol=1e-10)
