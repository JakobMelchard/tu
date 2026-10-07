import numpy as np
import pytest
import scipy.optimize

from nonlinear import (bisection, fixed_point, newton, secant, newton_system,
                       jacobian_fd, convergence_order, simplified_newton)

F_CUBIC = lambda x: x ** 3 - 2 * x - 5
DF_CUBIC = lambda x: 3 * x ** 2 - 2
ROOT = scipy.optimize.brentq(F_CUBIC, 2, 3, xtol=1e-15)


def test_bisection_error_bound():
    x, k, hist = bisection(F_CUBIC, 2.0, 3.0, tol=1e-10)
    assert abs(x - ROOT) < 1e-10
    for i, m in enumerate(hist):
        assert abs(m - ROOT) <= 1.0 / 2 ** (i + 1) + 1e-15
    with pytest.raises(ValueError):
        bisection(F_CUBIC, 3.0, 4.0)


def test_newton_quadratic():
    x, k, hist = newton(F_CUBIC, DF_CUBIC, 2.0)
    assert abs(x - ROOT) < 1e-14 and k <= 6
    p = convergence_order(hist, ROOT)
    assert np.any(np.abs(p - 2) < 0.2)                # before rounding limits it


def test_newton_linear_on_double_root():
    x, k, hist = newton(lambda x: (x - 1) ** 2, lambda x: 2 * (x - 1), 2.0, tol=1e-8)
    e = np.abs(hist - 1)
    np.testing.assert_allclose(e[1:6] / e[:5], 0.5, rtol=1e-10)


def test_secant_golden_ratio_order():
    x, k, hist = secant(F_CUBIC, 2.0, 3.0, tol=1e-15)
    assert abs(x - ROOT) < 1e-13
    p = convergence_order(hist, ROOT)
    phi = (1 + np.sqrt(5)) / 2
    assert np.any(np.abs(p - phi) < 0.25)


def test_fixed_point_rate_is_g_prime():
    g = lambda x: np.cos(x)
    x, k, hist = fixed_point(g, 1.0, tol=1e-13)
    assert abs(x - scipy.optimize.fixed_point(g, 1.0)) < 1e-10
    ratios = np.abs(hist[1:] - x)[5:20] / np.abs(hist[:-1] - x)[5:20]
    assert np.allclose(ratios, abs(np.sin(x)), atol=0.05)    # |g'(x*)| = sin(x*)


def test_fixed_point_diverges_when_g_prime_large():
    with np.errstate(all="ignore"):
        x, k, hist = fixed_point(lambda x: x ** 2 - 2, 2.5, maxiter=20)
    assert not np.isfinite(hist[-1]) or abs(hist[-1]) > 1e6


def test_newton_system_matches_scipy():
    F = lambda v: np.array([v[0] ** 2 + v[1] ** 2 - 4, np.exp(v[0]) + v[1] - 1])
    J = lambda v: np.array([[2 * v[0], 2 * v[1]], [np.exp(v[0]), 1.0]])
    x, k, hist = newton_system(F, J, [1.0, 1.0])
    ref = scipy.optimize.fsolve(F, [1.0, 1.0], xtol=1e-14)
    np.testing.assert_allclose(x, ref, atol=1e-10)
    assert hist[-1] < 1e-12
    x_fd, _, _ = newton_system(F, None, [1.0, 1.0])
    np.testing.assert_allclose(x_fd, ref, atol=1e-8)


def test_jacobian_fd():
    F = lambda v: np.array([v[0] * v[1], np.sin(v[0]) + v[1] ** 3])
    x = np.array([0.3, 0.7])
    J = np.array([[x[1], x[0]], [np.cos(x[0]), 3 * x[1] ** 2]])
    np.testing.assert_allclose(jacobian_fd(F, x), J, atol=1e-6)


def test_damping_widens_basin():
    F = lambda v: np.arctan(v)
    J = lambda v: np.array([[1 / (1 + v[0] ** 2)]])
    diverged = False
    try:
        with np.errstate(all="ignore"):
            x_plain, _, hist = newton_system(F, J, [3.0], maxiter=15)
        diverged = not np.isfinite(hist[-1]) or abs(x_plain[0]) > 1
    except ValueError:                                           # Jacobian underflows to 0
        diverged = True
    assert diverged
    x_damp, k, _ = newton_system(F, J, [3.0], damped=True)
    assert abs(x_damp[0]) < 1e-12


# ================= [S4] chapter 6: the script's own examples =================


def test_s4_example_6_2_newton_for_sqrt_two():
    """[S4] Ex. 6.2 / S2a 2.4a: x_{n+1} = x_n - (x_n^2 - 2)/(2 x_n) from x_0 = 2."""
    f, fp = (lambda x: x ** 2 - 2), (lambda x: 2 * x)
    x = 2.0
    iterates = []
    for _ in range(4):
        x = x - f(x) / fp(x)
        iterates.append(x)
    expect = [1.5, 1.416666666666667, 1.414215686274510, 1.414213562374690]
    for got, want in zip(iterates, expect):
        assert got == pytest.approx(want, abs=1e-14)
    errs = [abs(v - np.sqrt(2)) for v in iterates]
    for want in (8.578643762690485e-2, 2.453104293571595e-3,
                 2.1239014147411694e-6, 1.5947243525715749e-12):
        assert any(abs(e - want) < 1e-14 * max(1.0, want) for e in errs)
    for i in range(len(errs) - 1):                        # quadratic
        assert errs[i + 1] < 1.5 * errs[i] ** 2


def test_s4_example_6_7_the_rewriting_decides():
    """[S4] Ex. 6.7: 2 - x^2 - e^x = 0, x* = 0.5372744491738...

    Phi_1 = sqrt(2 - e^x) has |Phi_1'(x*)| ~ 1.59 and diverges;
    Phi_2 = ln(2 - x^2) has |Phi_2'(x*)| < 1 and converges.

    [S4] prints 0.31 for |Phi_2'(x*)|; recomputing gives 0.6279, and the ratio
    of successive errors in [S4]'s own printed iterate table is -0.628, so 0.31
    is a slip in the script.  The conclusion is unaffected.
    """
    xstar = 0.5372744491738201
    assert abs(2 - xstar ** 2 - np.exp(xstar)) < 1e-12

    d1 = abs(-np.exp(xstar) / (2 * np.sqrt(2 - np.exp(xstar))))
    d2 = abs(-2 * xstar / (2 - xstar ** 2))
    assert d1 == pytest.approx(1.5926, abs=1e-3)             # [S4]: 1.59
    assert d2 == pytest.approx(0.6279, abs=1e-3)             # [S4] prints 0.31
    assert d1 > 1.0 > d2

    # [S4]'s printed table for Phi_2 started at x0 = 0.5, reproduced exactly
    x, seen = 0.5, []
    for _ in range(10):
        x = np.log(2 - x ** 2)
        seen.append(x)
    expect = [0.559615787935423, 0.522851128605001, 0.546169619063046,
              0.531627015197373, 0.540795632739194, 0.535053787215218,
              0.538664955236433, 0.536399837485597, 0.537823020842571,
              0.536929765486145]
    for got, want in zip(seen, expect):
        assert got == pytest.approx(want, abs=1e-14)
    errs = np.array(seen) - xstar
    ratios = errs[1:] / errs[:-1]
    np.testing.assert_allclose(ratios, -d2, atol=0.02)    # rate is Phi_2'(x*)

    x, diverged = 0.5, False
    for _ in range(6):
        inner = 2 - np.exp(x)
        if inner < 0:                                     # [S4]: "stop: 2 - e^0.87 < 0"
            diverged = True
            break
        x = np.sqrt(inner)
    assert diverged


def test_s4_exercise_6_10_double_root_is_only_linear():
    """[S4] Exercise 6.10 / S2a 2.4c: Newton on f = x^2 gives x_{n+1} = x_n / 2."""
    f, fp = (lambda x: x ** 2), (lambda x: 2 * x)
    x = 1.0
    errs = []
    for _ in range(10):
        x = x - f(x) / fp(x)
        errs.append(abs(x))
    np.testing.assert_allclose(errs, [2.0 ** -(k + 1) for k in range(10)], rtol=1e-12)
    ratios = np.array(errs[1:]) / np.array(errs[:-1])
    np.testing.assert_allclose(ratios, 0.5, rtol=1e-12)   # linear, rate 1/2


def test_simplified_newton_is_linear_not_quadratic():
    """[S4] sec. 6.4: freezing f'(x_0) costs the quadratic convergence."""
    f, fp = (lambda x: x ** 2 - 2), (lambda x: 2 * x)
    xs, hs = simplified_newton(f, fp, 2.0, history=True)
    assert xs == pytest.approx(np.sqrt(2), abs=1e-10)
    errs = np.abs(hs - np.sqrt(2))
    errs = errs[errs > 1e-12]
    ratios = errs[1:] / errs[:-1]
    assert 0.2 < np.median(ratios) < 0.95                 # linear
    assert len(hs) - 1 > 10                               # Newton needs ~5


def test_f2_exam_newton_item():
    """F2 2.2b, 2022W: f = x^2 + 3x - 4 from x0 = 0."""
    f, fp = (lambda x: x ** 2 + 3 * x - 4), (lambda x: 2 * x + 3)
    x = 0.0
    x1 = x - f(x) / fp(x)
    x2 = x1 - f(x1) / fp(x1)
    assert x1 == pytest.approx(4 / 3)
    assert x2 == pytest.approx(52 / 51)
