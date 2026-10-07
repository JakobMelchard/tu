import numpy as np
import pytest
import scipy.integrate

from ode import (euler, implicit_euler, heun, rk4, rk4_step, stability_function,
                 real_stability_interval, rk45)

F = lambda t, y: -2 * t * y
EXACT = lambda t: np.exp(-t * t)


@pytest.mark.parametrize("method, p", [(euler, 1), (implicit_euler, 1), (heun, 2), (rk4, 4)])
def test_global_order(method, p):
    errs = []
    for n in (40, 80):
        _, ys = method(F, 0.0, np.array([1.0]), 2.0 / n, n)
        errs.append(abs(ys[-1, 0] - EXACT(2.0)))
    assert abs(np.log2(errs[0] / errs[1]) - p) < 0.15


def test_rk4_matches_scipy_on_a_system():
    # harmonic oscillator y'' = -y as a system
    f = lambda t, y: np.array([y[1], -y[0]])
    ts, ys = rk4(f, 0.0, np.array([1.0, 0.0]), 0.01, 1000)
    np.testing.assert_allclose(ys[-1], [np.cos(10.0), -np.sin(10.0)], atol=1e-7)
    sol = scipy.integrate.solve_ivp(f, (0, 10), [1.0, 0.0], rtol=1e-10, atol=1e-12)
    np.testing.assert_allclose(ys[-1], sol.y[:, -1], atol=1e-7)


def test_stability_functions_and_intervals():
    z = np.array([-0.5, -1.0, -2.5], complex)
    np.testing.assert_allclose(stability_function("euler", z), 1 + z)
    np.testing.assert_allclose(stability_function("rk4", z),
                               np.array([np.polyval([1 / 24, 1 / 6, 1 / 2, 1, 1], v) for v in z]))
    assert abs(real_stability_interval("euler") + 2) < 1e-3
    assert abs(real_stability_interval("heun") + 2) < 1e-3
    assert abs(real_stability_interval("rk4") + 2.785) < 2e-3
    # A-stability: implicit Euler and trapezoid bounded on the whole left half-plane
    zz = -np.abs(np.random.default_rng(0).standard_normal(50)) * 100 + 1j * np.random.default_rng(1).standard_normal(50) * 100
    assert np.all(np.abs(stability_function("implicit_euler", zz)) <= 1)
    assert np.all(np.abs(stability_function("trapezoid", zz)) <= 1)


def test_stiff_problem():
    lam = -50.0
    f = lambda t, y: lam * y
    _, y_e = euler(f, 0.0, np.array([1.0]), 0.1, 10)             # z = -5: unstable
    _, y_ie = implicit_euler(f, 0.0, np.array([1.0]), 0.1, 10)   # R(z) = 1/6 per step
    assert abs(y_e[-1, 0]) > 1e5
    np.testing.assert_allclose(y_ie[-1, 0], 6.0 ** -10, rtol=1e-8)
    _, y_e2 = euler(f, 0.0, np.array([1.0]), 0.03, 100)           # z = -1.5: stable
    assert abs(y_e2[-1, 0]) < 1e-10


def test_implicit_euler_with_analytic_jacobian():
    f = lambda t, y: np.array([y[1], -y[0]])
    J = lambda t, y: np.array([[0.0, 1.0], [-1.0, 0.0]])
    _, ys = implicit_euler(f, 0.0, np.array([1.0, 0.0]), 0.001, 1000, jac=J)
    _, ys_fd = implicit_euler(f, 0.0, np.array([1.0, 0.0]), 0.001, 1000)
    np.testing.assert_allclose(ys[-1], ys_fd[-1], atol=1e-8)
    assert abs(ys[-1, 0] - np.cos(1.0)) < 2e-3


def test_rk45_accuracy_and_step_adaptation():
    ts, ys, rej = rk45(F, 0.0, [1.0], 2.0, rtol=1e-8, atol=1e-10)
    assert abs(ys[-1, 0] - EXACT(2.0)) < 1e-7
    assert ts[0] == 0.0 and ts[-1] == 2.0 and np.all(np.diff(ts) > 0)
    # tighter tolerance -> more steps; error reduces
    ts2, ys2, _ = rk45(F, 0.0, [1.0], 2.0, rtol=1e-11, atol=1e-13)
    assert len(ts2) > len(ts) and abs(ys2[-1, 0] - EXACT(2.0)) < 1e-9


def test_rk45_matches_scipy_dop853_on_van_der_pol():
    mu = 3.0
    vdp = lambda t, y: np.array([y[1], mu * (1 - y[0] ** 2) * y[1] - y[0]])
    ts, ys, rej = rk45(vdp, 0.0, [2.0, 0.0], 10.0, rtol=1e-9, atol=1e-11)
    sol = scipy.integrate.solve_ivp(vdp, (0, 10), [2.0, 0.0], method="DOP853", rtol=1e-12, atol=1e-13)
    np.testing.assert_allclose(ys[-1], sol.y[:, -1], atol=1e-6)
    hs = np.diff(ts)
    assert hs.max() / hs.min() > 5                               # step size really adapts


def test_rk4_step_local_error_is_order_five():
    """One step on y' = y from y = 1: y_1 = sum_{k<=4} h^k/k!, error ~ h^5/120."""
    f = lambda t, y: y
    for h in (0.1, 0.05):
        y1 = rk4_step(f, 0.0, np.array([1.0]), h)[0]
        assert y1 == pytest.approx(1 + h + h**2 / 2 + h**3 / 6 + h**4 / 24, rel=1e-15)
        assert np.exp(h) - y1 == pytest.approx(h**5 / 120, rel=0.1)
