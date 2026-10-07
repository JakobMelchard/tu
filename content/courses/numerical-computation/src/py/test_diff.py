import pytest
import numpy as np
import scipy.differentiate

from diff import (forward_diff, backward_diff, central_diff, second_diff, fd_weights, optimal_h,
                  richardson, gradient_fd)


def order(err_h, err_h2):
    return np.log2(err_h / err_h2)


def test_orders_of_finite_differences():
    f, df, ddf, x = np.sin, np.cos, lambda t: -np.sin(t), 0.7
    h = 1e-2
    e1 = [abs(forward_diff(f, x, hh) - df(x)) for hh in (h, h / 2)]
    e2 = [abs(central_diff(f, x, hh) - df(x)) for hh in (h, h / 2)]
    e3 = [abs(second_diff(f, x, hh) - ddf(x)) for hh in (h, h / 2)]
    assert abs(order(*e1) - 1) < 0.05
    assert abs(order(*e2) - 2) < 0.05
    assert abs(order(*e3) - 2) < 0.05


def test_roundoff_dominates_for_tiny_h():
    err_opt = abs(forward_diff(np.exp, 1.0, optimal_h(1)) - np.e)
    err_tiny = abs(forward_diff(np.exp, 1.0, 1e-14) - np.e)
    assert err_opt < 1e-7 and err_tiny > 1e-3


def test_matches_scipy_derivative():
    res = scipy.differentiate.derivative(np.exp, 1.0)
    assert abs(central_diff(np.exp, 1.0, optimal_h(2)) - res.df) < 1e-9


def test_fd_weights_known_stencils():
    np.testing.assert_allclose(fd_weights([-1, 0, 1], 1), [-0.5, 0, 0.5], atol=1e-13)
    np.testing.assert_allclose(fd_weights([-1, 0, 1], 2), [1, -2, 1], atol=1e-13)
    np.testing.assert_allclose(fd_weights([-2, -1, 0, 1, 2], 1) * 12, [1, -8, 0, 8, -1], atol=1e-12)
    np.testing.assert_allclose(fd_weights([0, 1, 2], 1) * 2, [-3, 4, -1], atol=1e-13)


def test_richardson_gains_two_orders_per_column():
    T = richardson(lambda h: central_diff(np.exp, 1.0, h), 0.4, p=2, levels=4)
    err = np.abs(T - np.e)
    assert err[3, 3] < 1e-11 < err[3, 0]
    # column j is order 2(j+1): error ratio between consecutive rows ~ 4^(j+1)
    for j in range(2):
        ratio = err[2, j] / err[3, j]
        assert abs(np.log2(ratio) - 2 * (j + 1)) < 0.3


def test_gradient_fd():
    f = lambda v: v[0] ** 2 * v[1] + np.exp(v[1])
    x = np.array([1.5, -0.5])
    g = np.array([2 * x[0] * x[1], x[0] ** 2 + np.exp(x[1])])
    np.testing.assert_allclose(gradient_fd(f, x), g, atol=1e-8)


def test_leading_error_terms_and_signs():
    """Every row of the stencil table in note 12, derived symbolically.

    Convention: error = approximation - exact.  Two of these signs were wrong in
    an earlier draft of the note (the 5-point central and the one-sided
    second-order rule), so they are pinned here rather than trusted to a table.
    """
    import sympy as sp

    h = sp.symbols("h", positive=True)
    N = 9
    d = sp.symbols("d0:%d" % N)                       # d[k] is f^{(k)}(x)

    def T(k):                                         # Taylor series of f(x + k h)
        return sum(d[j] * (k * h) ** j / sp.factorial(j) for j in range(N))

    table = {
        "forward":             ((T(1) - T(0)) / h, 1, d[2] * h / 2),
        "backward":            ((T(0) - T(-1)) / h, 1, -d[2] * h / 2),
        "central":             ((T(1) - T(-1)) / (2 * h), 1, d[3] * h ** 2 / 6),
        "second derivative":   ((T(1) - 2 * T(0) + T(-1)) / h ** 2, 2, d[4] * h ** 2 / 12),
        "5-point central":     ((-T(2) + 8 * T(1) - 8 * T(-1) + T(-2)) / (12 * h), 1,
                                -d[5] * h ** 4 / 30),
        "one-sided 2nd order": ((-3 * T(0) + 4 * T(1) - T(2)) / (2 * h), 1,
                                -d[3] * h ** 2 / 3),
    }
    for name, (D, order, expected) in table.items():
        e = sp.expand(sp.simplify(D - d[order]))
        lead = min((t for t in sp.Add.make_args(e) if t != 0),
                   key=lambda t: sp.degree(t, h))
        assert sp.simplify(lead - expected) == 0, f"{name}: got {lead}, expected {expected}"


def test_five_point_error_sign_numerically():
    """The 5-point central rule UNDER-estimates f' when f^{(5)} > 0."""
    f = np.exp
    x = 1.0
    for h in (0.2, 0.1, 0.05):
        approx = (-f(x + 2 * h) + 8 * f(x + h) - 8 * f(x - h) + f(x - 2 * h)) / (12 * h)
        err = approx - f(x)                           # f' = f for exp
        assert err < 0                                # the sign the table now states
        assert err == pytest.approx(-h ** 4 * f(x) / 30, rel=2e-2)


def test_backward_diff_is_first_order_with_opposite_sign():
    """(f(x) - f(x-h))/h - f'(x) = -h/2 f''(x) + O(h^2): forward's error, mirrored."""
    x = 0.3
    for h in (1e-2, 5e-3, 2.5e-3):
        eb = backward_diff(np.exp, x, h) - np.exp(x)
        ef = forward_diff(np.exp, x, h) - np.exp(x)
        assert eb == pytest.approx(-h / 2 * np.exp(x), rel=0.02)
        assert eb == pytest.approx(-ef, rel=0.02)
