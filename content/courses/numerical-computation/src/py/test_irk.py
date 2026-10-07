"""Tests for irk.py, against [S4] sec. 9.3."""
import numpy as np
import pytest
from math import factorial

from irk import (butcher_explicit_euler, butcher_heun, butcher_rk4,
                 butcher_implicit_euler, butcher_theta, theta_scheme, implicit_rk,
                 stability_function_rational, is_a_stable, lambert_system)
from ode import euler, heun, rk4, stability_function

ZS = [-0.7 + 0.3j, -2.0 + 0.0j, 0.4 - 1.1j, 1e-3 + 0j]


# ------------------------------------------------------ stability functions
def test_stability_functions_match_s4_exercise_9_13():
    """[S4] Exercise 9.13."""
    for z in ZS:
        A, b, _ = butcher_explicit_euler()
        assert stability_function_rational(A, b, z) == pytest.approx(1 + z)
        A, b, _ = butcher_implicit_euler()
        assert stability_function_rational(A, b, z) == pytest.approx(1 / (1 - z))
        A, b, _ = butcher_theta(0.5)
        assert stability_function_rational(A, b, z) == pytest.approx(
            (1 + z / 2) / (1 - z / 2))
        A, b, _ = butcher_rk4()
        assert stability_function_rational(A, b, z) == pytest.approx(
            sum(z ** k / factorial(k) for k in range(5)))
        A, b, _ = butcher_heun()
        assert stability_function_rational(A, b, z) == pytest.approx(1 + z + z ** 2 / 2)


def test_stability_function_agrees_with_the_ode_module():
    for z in ZS:
        A, b, _ = butcher_explicit_euler()
        assert stability_function_rational(A, b, z) == pytest.approx(
            complex(stability_function("euler", z)))
        A, b, _ = butcher_rk4()
        assert stability_function_rational(A, b, z) == pytest.approx(
            complex(stability_function("rk4", z)))


def test_every_convergent_method_has_r_of_z_equal_one_plus_z_plus_o_z_squared():
    """[S4] sec. 9.3.4."""
    for A, b, _ in (butcher_explicit_euler(), butcher_heun(), butcher_rk4(),
                    butcher_implicit_euler(), butcher_theta(0.5)):
        z = 1e-6
        R = stability_function_rational(A, b, z)
        assert abs(R - (1 + z)) < 1e-11


# ------------------------------------------------------------- A-stability
def test_explicit_methods_are_not_a_stable():
    """[S4] Exercise 9.15: R is a polynomial, hence unbounded as z -> -inf."""
    for A, b, _ in (butcher_explicit_euler(), butcher_heun(), butcher_rk4(),
                    butcher_theta(0.0)):
        assert is_a_stable(A, b) is False
        assert abs(stability_function_rational(A, b, -1000.0 + 0j)) > 1.0


def test_implicit_euler_and_the_midpoint_rule_are_a_stable():
    """[S4] Def. 9.14."""
    for A, b, _ in (butcher_implicit_euler(), butcher_theta(0.5),
                    butcher_theta(0.75), butcher_theta(1.0)):
        assert is_a_stable(A, b) is True


def test_theta_below_one_half_is_not_a_stable():
    assert is_a_stable(*butcher_theta(0.25)[:2]) is False


def test_implicit_euler_is_l_stable_the_midpoint_rule_is_not():
    """Background [S19]: R(z) -> 0 damps the fast modes; R -> -1 does not."""
    A, b, _ = butcher_implicit_euler()
    assert abs(stability_function_rational(A, b, -1e8 + 0j)) < 1e-7
    A, b, _ = butcher_theta(0.5)
    assert abs(stability_function_rational(A, b, -1e8 + 0j)) == pytest.approx(1.0, abs=1e-6)


# --------------------------------------------------------- the theta scheme
@pytest.mark.parametrize("theta,order", [(0.0, 1), (1.0, 1), (0.25, 1), (0.75, 1),
                                         (0.5, 2)])
def test_theta_scheme_order(theta, order):
    """[S4] Ex. 9.11: order 1 for theta != 1/2, order 2 for theta = 1/2."""
    f = lambda t, y: -2 * t * y
    fp = lambda t, y: np.array([[-2 * t]])
    exact = np.exp(-4.0)
    errs = []
    for N in (40, 80, 160, 320):
        _, ys = theta_scheme(f, [1.0], 0.0, 2.0, N, theta, fprime=fp)
        errs.append(abs(float(np.ravel(ys)[-1]) - exact))
    rate = np.log2(np.array(errs[:-1]) / np.array(errs[1:])).mean()
    assert rate == pytest.approx(order, abs=0.15)


def test_theta_zero_and_one_reproduce_the_euler_methods():
    f = lambda t, y: -2 * t * y
    fp = lambda t, y: np.array([[-2 * t]])
    _, ye = theta_scheme(f, [1.0], 0.0, 1.0, 50, 0.0, fprime=fp)
    ts, ref = euler(f, 0.0, np.array([1.0]), 1.0 / 50, 50)
    np.testing.assert_allclose(np.ravel(ye), np.ravel(ref), atol=1e-10)


# ------------------------------------------------------------- implicit RK
def test_implicit_rk_with_the_implicit_euler_tableau():
    """[S4] Exercise 9.10."""
    f = lambda t, y: -2 * t * y
    A, b, c = butcher_implicit_euler()
    _, y1 = implicit_rk(f, [1.0], 0.0, 1.0, 40, A, b, c)
    _, y2 = theta_scheme(f, [1.0], 0.0, 1.0, 40, 1.0)
    np.testing.assert_allclose(np.ravel(y1), np.ravel(y2), atol=1e-8)


def test_implicit_rk_reproduces_explicit_tableaux():
    f = lambda t, y: -2 * t * y
    for tab, ref in ((butcher_rk4(), rk4), (butcher_heun(), heun),
                     (butcher_explicit_euler(), euler)):
        A, b, c = tab
        _, y1 = implicit_rk(f, [1.0], 0.0, 1.0, 20, A, b, c)
        _, y2 = ref(f, 0.0, np.array([1.0]), 1.0 / 20, 20)
        np.testing.assert_allclose(np.ravel(y1), np.ravel(y2), atol=1e-9)


def test_implicit_midpoint_is_second_order_and_a_stable_in_practice():
    """y' = -50 y with h = 0.1: z = -5, outside every explicit stability region."""
    f = lambda t, y: -50.0 * y
    A, b, c = butcher_theta(0.5)
    _, y = implicit_rk(f, [1.0], 0.0, 1.0, 10, A, b, c)
    assert abs(float(np.ravel(y)[-1])) < 1.0            # bounded
    _, ye = implicit_rk(f, [1.0], 0.0, 1.0, 10, *butcher_explicit_euler())
    assert abs(float(np.ravel(ye)[-1])) > 1e5           # explicit Euler blows up


def test_rk4_reduces_to_simpsons_rule():
    """[S4] Exercise 9.8: for f(t, y) = f(t) an RK method is a quadrature rule."""
    f = lambda t, y: np.array([np.cos(t)])
    h = 0.7
    ts, ys = rk4(lambda t, y: f(t, y), 0.0, np.array([0.0]), h, 1)
    simpson = h / 6 * (np.cos(0.0) + 4 * np.cos(h / 2) + np.cos(h))
    assert float(np.ravel(ys)[-1]) == pytest.approx(simpson, abs=1e-14)


# -------------------------------------------------- the stiff example 9.12
def test_lambert_exact_solution_solves_the_ode():
    """[S4] Ex. 9.12: the printed solution really is the solution."""
    A, y0, exact = lambert_system()
    np.testing.assert_allclose(exact(0.0)[0], y0, atol=1e-14)
    ev = np.sort_complex(np.linalg.eigvals(A))
    np.testing.assert_allclose(np.sort(ev.real), [-40.0, -40.0, -2.0], atol=1e-10)
    np.testing.assert_allclose(np.sort(np.abs(ev.imag)), [0.0, 40.0, 40.0], atol=1e-10)
    h = 1e-6
    for t in (0.01, 0.1, 0.5):
        num = (exact(t + h)[0] - exact(t - h)[0]) / (2 * h)
        np.testing.assert_allclose(num, A @ exact(t)[0], rtol=1e-5, atol=1e-6)


def test_explicit_euler_needs_the_stability_step_and_implicit_does_not():
    """[S4] Ex. 9.12: |1 + h lambda| <= 1 forces h <= 2/|lambda| ~ 0.0354."""
    A, y0, exact = lambert_system()
    f = lambda t, y: A @ y
    fp = lambda t, y: A
    limit = 2.0 / abs(-40 * (1 + 1j))
    assert limit == pytest.approx(0.035355, abs=1e-5)

    _, ybad = theta_scheme(f, y0, 0.0, 1.0, 20, 0.0, fprime=fp)       # h = 0.05 > limit
    assert np.abs(ybad[-1]).max() > 1e5

    _, yok = theta_scheme(f, y0, 0.0, 1.0, 50, 0.0, fprime=fp)        # h = 0.02 < limit
    assert np.abs(yok[-1] - exact(1.0)[0]).max() < 1e-1

    for N in (20, 50):
        _, yi = theta_scheme(f, y0, 0.0, 1.0, N, 1.0, fprime=fp)      # implicit Euler
        assert np.abs(yi[-1] - exact(1.0)[0]).max() < 1e-1            # stable at both
