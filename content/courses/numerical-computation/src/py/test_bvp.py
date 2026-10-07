"""Tests for bvp.py, against [S4] sec. 9.4."""
import numpy as np
import pytest
import scipy.integrate

from bvp import (solve_ivp_shot, shooting, shooting_sensitivity, variational_rhs)

# y'' = -y, the model problem of [S4] Ex. 9.17 and Ex. 9.18
F = lambda t, y, u: -y
FY = lambda t, y, u: -1.0
FU = lambda t, y, u: 0.0


def test_ivp_shot_solves_the_first_order_system():
    """[S4] (9.13): y(t; s0) = s0 sin t for y'' = -y, y(0) = 0."""
    for s0 in (0.5, 1.0, -2.0):
        ts, y, u = solve_ivp_shot(F, 0.0, s0, np.pi, N=800)
        np.testing.assert_allclose(y, s0 * np.sin(ts), atol=1e-9)
        np.testing.assert_allclose(u, s0 * np.cos(ts), atol=1e-9)


def test_s4_example_9_18_one_newton_step_is_exact():
    """[S4] Ex. 9.18: y'' = -y, y(0) = 0, y(pi/2) = 1, exact y = sin t.

    The variational problem is v'' = -v, v(0) = 0, v'(0) = 1, i.e. v = sin t,
    and y(T; s0) is linear in s0, so Newton lands on s0 = 1 in one step from 0.
    """
    s, ts, y, hist = shooting(F, 0.0, 1.0, np.pi / 2, s0=0.0, f_y=FY, f_u=FU,
                              N=800, history=True)
    assert hist[0] == 0.0
    assert hist[1] == pytest.approx(1.0, abs=1e-9)          # exact after ONE step
    assert s == pytest.approx(1.0, abs=1e-9)
    assert np.abs(y - np.sin(ts)).max() < 1e-9


def test_s4_example_9_18_from_any_start():
    """Linearity in s0 means any starting guess converges in one step."""
    for s0 in (-5.0, 0.3, 17.0):
        s, _, _, hist = shooting(F, 0.0, 1.0, np.pi / 2, s0=s0, f_y=FY, f_u=FU,
                                 N=800, history=True)
        assert hist[1] == pytest.approx(1.0, abs=1e-8)


def test_variational_solution_is_the_sensitivity():
    """[S4] (9.14): v = d y(t; s0) / d s0."""
    s0, eps = 0.7, 1e-6
    T = 1.3
    ts, y, u = solve_ivp_shot(F, 0.0, s0, T, N=800)
    _, y2, _ = solve_ivp_shot(F, 0.0, s0 + eps, T, N=800)
    numeric = (y2[-1] - y[-1]) / eps
    from ode import rk4
    ysol = lambda t: np.interp(t, ts, y)
    usol = lambda t: np.interp(t, ts, u)
    _, W = rk4(variational_rhs(FY, FU, ysol, usol, ts), 0.0, np.array([0.0, 1.0]),
               T / 800, 800)
    assert np.asarray(W)[-1, 0] == pytest.approx(numeric, rel=1e-5)
    assert np.asarray(W)[-1, 0] == pytest.approx(np.sin(T), abs=1e-8)   # v = sin t


# ------------------------------------ [S4] Ex. 9.17: the three boundary problems
def test_unique_case():
    s, ts, y = shooting(F, 0.0, 1.0, np.pi / 2, s0=0.0, f_y=FY, f_u=FU, N=800)
    assert s == pytest.approx(1.0, abs=1e-9)
    assert np.abs(y - np.sin(ts)).max() < 1e-9


def test_non_unique_case():
    """y(0) = y(pi) = 0 is solved by y = c sin t for every c."""
    for c in (-3.0, 0.0, 1.0, 7.5):
        ts, y, _ = solve_ivp_shot(F, 0.0, c, np.pi, N=1200)
        assert abs(y[-1]) < 1e-7                        # every slope satisfies it
        np.testing.assert_allclose(y, c * np.sin(ts), atol=1e-8)


def test_unsolvable_case_produces_a_meaningless_answer():
    """y(0) = 0, y(pi) = 1 has no solution: y(pi; s0) = s0 sin(pi) = 0 for every
    s0, so the sensitivity d y(pi)/d s0 = sin(pi) vanishes and Newton has no step.

    A discretisation does not see the exact zero -- with RK4, y(pi; s0) is
    s0 * O(h^4) -- so the *discrete* problem is solvable and the solver happily
    returns an s0 of the order 1/O(h^4).  The answer satisfies the boundary
    conditions to plotting accuracy and is physically nonsense: its amplitude is
    ten orders of magnitude larger than the data.  This is the failure mode to
    recognise, not a divergence.
    """
    s, ts, y = shooting(F, 0.0, 1.0, np.pi, s0=0.5, f_y=FY, f_u=FU, N=1200,
                        iters=20)
    assert abs(s) > 1e6                                 # slope of order 1/h^4
    assert np.abs(y).max() > 1e6                        # amplitude, data is O(1)
    assert abs(y[-1] - 1.0) < 1e-2                      # "satisfies" the condition
    # the continuous sensitivity really is zero
    eps = 1e-3
    _, y1, _ = solve_ivp_shot(F, 0.0, 1.0, np.pi, N=4000)
    _, y2, _ = solve_ivp_shot(F, 0.0, 1.0 + eps, np.pi, N=4000)
    assert abs(y2[-1] - y1[-1]) / eps < 1e-8            # d y(pi) / d s0 = sin(pi) = 0


# ------------------------------------------------------------- nonlinear BVP
def test_nonlinear_bvp_against_the_exact_solution():
    """y'' = 2 y^3 on [1, 2], y(1) = 1, y(2) = 1/2 has the solution y = 1/t."""
    g = lambda t, y, u: 2.0 * y ** 3
    gy = lambda t, y, u: 6.0 * y ** 2
    gu = lambda t, y, u: 0.0
    s, ts, y, hist = shooting(g, 1.0, 0.5, 2.0, s0=-0.9, f_y=gy, f_u=gu, t0=1.0,
                              N=800, history=True)
    assert s == pytest.approx(-1.0, abs=1e-7)           # y'(1) = -1/t^2 at t=1
    assert np.abs(y - 1.0 / ts).max() < 1e-8
    assert len(hist) - 1 <= 8                           # Newton, so a few steps


def test_nonlinear_bvp_against_scipy_solve_bvp():
    g = lambda t, y, u: 2.0 * y ** 3
    s, ts, y = shooting(g, 1.0, 0.5, 2.0, s0=-0.9, t0=1.0, N=800)

    def rhs(t, z):
        return np.vstack([z[1], 2.0 * z[0] ** 3])

    def bc(za, zb):
        return np.array([za[0] - 1.0, zb[0] - 0.5])

    tm = np.linspace(1.0, 2.0, 40)
    ref = scipy.integrate.solve_bvp(rhs, bc, tm, np.vstack([1.0 / tm, -1.0 / tm ** 2]))
    assert ref.success
    np.testing.assert_allclose(y, ref.sol(ts)[0], atol=1e-6)


def test_finite_difference_sensitivity_matches_the_variational_one():
    g = lambda t, y, u: 2.0 * y ** 3
    gy = lambda t, y, u: 6.0 * y ** 2
    gu = lambda t, y, u: 0.0
    a = shooting(g, 1.0, 0.5, 2.0, s0=-0.9, f_y=gy, f_u=gu, t0=1.0, N=400)[0]
    b = shooting(g, 1.0, 0.5, 2.0, s0=-0.9, t0=1.0, N=400)[0]
    assert a == pytest.approx(b, abs=1e-8)


def test_damped_problem_with_a_first_derivative_term():
    """y'' = -2 y' - y, y(0) = 1, y(1) = 2/e; exact y = (1 + t) e^{-t}."""
    g = lambda t, y, u: -2.0 * u - y
    gy = lambda t, y, u: -1.0
    gu = lambda t, y, u: -2.0
    s, ts, y = shooting(g, 1.0, 2.0 / np.e, 1.0, s0=0.0, f_y=gy, f_u=gu, N=800)
    assert s == pytest.approx(0.0, abs=1e-8)            # y'(0) = 0
    np.testing.assert_allclose(y, (1 + ts) * np.exp(-ts), atol=1e-8)


# ----------------------------------------------------------- the sensitivity
def test_sensitivity_bound():
    """[S4] sec. 9.4: e^{L T}; for L = T = 10 that is ~2.7e43."""
    assert shooting_sensitivity(1.0, 1.0) == pytest.approx(np.e)
    assert shooting_sensitivity(10.0, 10.0) == pytest.approx(np.exp(100))
    assert shooting_sensitivity(10.0, 10.0) > 2.6e43


def test_sensitivity_is_real_on_an_exponentially_growing_problem():
    """y'' = L^2 y really does amplify a change in s0 like e^{LT}."""
    L, T = 4.0, 2.0
    g = lambda t, y, u: L ** 2 * y
    eps = 1e-6
    _, y1, _ = solve_ivp_shot(g, 0.0, 1.0, T, N=4000)
    _, y2, _ = solve_ivp_shot(g, 0.0, 1.0 + eps, T, N=4000)
    amp = abs(y2[-1] - y1[-1]) / eps
    assert amp <= shooting_sensitivity(L, T)
    assert amp > 0.1 * np.exp(L * T) / (2 * L)          # and it is of that order
