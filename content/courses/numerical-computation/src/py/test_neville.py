"""Tests for neville.py, against the course script [S4] and the past papers."""
import numpy as np
import pytest

from interp import lagrange_eval
from neville import (aitken_neville, neville_tableau, extrapolate_derivative,
                     omega, omega_max, chebyshev_omega_max, lebesgue_constant,
                     lebesgue_function,
                     chebyshev_lebesgue_bound, hermite_divided_differences,
                     hermite_eval, hermite, _factorial)

XS = np.array([0.0, 1.0, 2.0, 4.0])
YS = np.array([1.0, 3.0, 2.0, 5.0])


def cheb(n, a=-1.0, b=1.0):
    """[S4] (1.19): n+1 Chebyshev points on [a, b]."""
    return (a + b) / 2 + (b - a) / 2 * np.cos((2 * np.arange(n + 1) + 1) * np.pi / (2 * n + 2))


# ------------------------------------------------------------ Neville
def test_neville_matches_lagrange():
    for t in np.linspace(-1, 5, 25):
        assert aitken_neville(XS, YS, t) == pytest.approx(lagrange_eval(XS, YS, t), rel=1e-12)


def test_neville_worked_example_from_note():
    assert aitken_neville(XS, YS, 3.0) == pytest.approx(1.5)


def test_neville_reproduces_the_data_and_polynomials():
    for x, y in zip(XS, YS):
        assert aitken_neville(XS, YS, x) == pytest.approx(y)
    p = lambda x: 2 * x ** 3 - x + 1
    assert aitken_neville(XS, p(XS), 3.7) == pytest.approx(p(3.7), rel=1e-12)


def test_neville_knots_need_not_be_sorted():
    """[S4] Rem. 1.6."""
    perm = [2, 0, 3, 1]
    assert aitken_neville(XS[perm], YS[perm], 3.0) == pytest.approx(1.5)


def test_neville_cost_is_quadratic_not_linear():
    """[S4] Rem. 1.6 -- the true/false item of F1 5a, S1a 1.5b, F3 2.5a."""
    counts = {}
    for n in (4, 8, 16, 32, 64):
        x = np.linspace(0, 1, n + 1)
        _, ops = aitken_neville(x, np.sin(x), 0.5, count_ops=True)
        counts[n] = ops
    # exactly 3 * n(n+1)/2 operations, i.e. Theta(n^2)
    for n, ops in counts.items():
        assert ops == 3 * n * (n + 1) // 2
    ratios = [counts[2 * n] / counts[n] for n in (4, 8, 16, 32) if 2 * n in counts]
    assert all(3.5 < r < 4.5 for r in ratios)          # quadruples, not doubles


def test_neville_tableau_column_m_holds_degree_m_polynomials():
    """[S4] Thm 1.4 / the F1 5a true item."""
    P = neville_tableau(XS, YS, 3.0)
    for m in range(4):
        for j in range(4 - m):
            sub_x, sub_y = XS[j:j + m + 1], YS[j:j + m + 1]
            assert P[j, m] == pytest.approx(lagrange_eval(sub_x, sub_y, 3.0), rel=1e-12)


# -------------------------------------------------------- extrapolation
def test_extrapolation_column_rate_is_h_to_the_m_plus_one():
    """[S4] Thm 1.17: column m converges like h^{m+1} for smooth f."""
    hs = 2.0 ** -np.arange(10)
    T = extrapolate_derivative(np.exp, 0.0, hs)         # f'(0) = 1
    for m in (0, 1, 2):
        err = np.array([abs(T[i, m] - 1.0) for i in range(4, 8)])
        rate = np.log2(err[:-1] / err[1:])
        assert rate.mean() == pytest.approx(m + 1, abs=0.3)


def test_extrapolation_stalls_for_non_smooth_data():
    """[S4] Ex. 1.18 / Fig. 1.2: u = |x|^{3/2} gives D(h) = sqrt(h)."""
    hs = 2.0 ** -np.arange(12)
    T = extrapolate_derivative(lambda x: abs(x) ** 1.5, 0.0, hs)   # exact value 0
    # the published first rows of [S4] Fig. 1.2
    assert abs(T[0, 0]) == pytest.approx(1.000, abs=5e-4)
    assert abs(T[0, 1]) == pytest.approx(0.414, abs=5e-4)
    assert abs(T[0, 2]) == pytest.approx(0.252, abs=5e-4)
    assert abs(T[1, 0]) == pytest.approx(0.707, abs=5e-4)
    assert abs(T[1, 1]) == pytest.approx(0.293, abs=5e-4)
    # every column stalls at O(sqrt h): halving h only gains a factor sqrt 2
    for m in (0, 2, 4):
        err = np.array([abs(T[i, m]) for i in range(2, 6)])
        rate = np.log2(err[:-1] / err[1:])
        assert rate.mean() == pytest.approx(0.5, abs=0.05)


# ------------------------------------------ node polynomial and Lebesgue
@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 12])
def test_chebyshev_node_polynomial_closed_form(n):
    """[S4] Thm 1.21: ||omega||_inf = 2 ((b-a)/4)^{n+1} for Chebyshev points."""
    assert omega_max(cheb(n)) == pytest.approx(chebyshev_omega_max(n), rel=1e-5)


@pytest.mark.parametrize("n", [3, 6, 10])
def test_chebyshev_minimises_the_node_polynomial(n):
    """[S4] Thm 1.21: no other node set does better."""
    best = chebyshev_omega_max(n)
    assert omega_max(np.linspace(-1, 1, n + 1)) > best
    rng = np.random.default_rng(n)
    for _ in range(5):
        xs = np.sort(rng.uniform(-1, 1, n + 1))
        assert omega_max(xs) >= best - 1e-9


def test_chebyshev_node_polynomial_on_a_general_interval():
    a, b, n = 0.0, 3.0, 5
    assert omega_max(cheb(n, a, b), a, b) == pytest.approx(chebyshev_omega_max(n, a, b), rel=1e-4)


@pytest.mark.parametrize("n", [5, 10, 15, 20])
def test_chebyshev_lebesgue_bound_holds(n):
    """[S4] Thm 1.24(ii): Lambda_n <= (2/pi) ln(n+1) + 1."""
    assert lebesgue_constant(cheb(n)) <= chebyshev_lebesgue_bound(n)


def test_uniform_lebesgue_constant_grows_exponentially():
    """[S4] Thm 1.24(ii) -- S1a 1.5a marks 'uniform grows like O(log n)' FALSE."""
    lam = {n: lebesgue_constant(np.linspace(-1, 1, n + 1)) for n in (10, 15, 20, 25)}
    assert lam[25] > 100 * lam[10]                       # nothing logarithmic does this
    asym = lambda n: 2.0 ** n / (np.e * n * np.log(n))
    for n in (15, 20, 25):
        assert 0.2 < lam[n] / asym(n) < 5.0              # right order of magnitude


def test_lebesgue_quasi_best_approximation_bound():
    """[S4] Thm 1.24(i): ||f - I_n f|| <= (1 + Lambda_n) min_q ||f - q||."""
    f = lambda x: 1.0 / (1 + 25 * x ** 2)                # Runge
    t = np.linspace(-1, 1, 2001)
    for n in (6, 10):
        xs = cheb(n)
        err = np.abs(f(t) - lagrange_eval(xs, f(xs), t)).max()
        best = np.abs(f(t) - np.polyval(np.polyfit(t, f(t), n), t)).max()  # ~ L2-best
        assert err <= (1 + lebesgue_constant(xs)) * best * 1.5


def test_best_approximation_numbers_of_s4_example_1_26():
    """[S4] Ex. 1.26: exp on [-1,1], degree 1."""
    t = np.linspace(-1, 1, 20001)
    taylor = np.abs(np.exp(t) - (1 + t)).max()
    assert taylor == pytest.approx(np.e - 2, rel=1e-6)
    assert taylor == pytest.approx(0.7183, abs=5e-4)
    xs = cheb(1)                                          # +- 1/sqrt 2
    assert np.sort(xs) == pytest.approx([-1 / np.sqrt(2), 1 / np.sqrt(2)])
    icheb = np.abs(np.exp(t) - lagrange_eval(xs, np.exp(xs), t)).max()
    assert icheb == pytest.approx(0.3723, abs=5e-4)
    remez = np.abs(np.exp(t) - (1.1752 * t + 1.2643)).max()
    assert remez == pytest.approx(0.2788, abs=5e-4)
    assert remez < icheb < taylor


# ---------------------------------------------------------- Hermite
def test_hermite_reproduces_values_and_derivatives():
    """[S4] (1.22)."""
    f = lambda x: np.sin(x)
    fp = lambda x: np.cos(x)
    xs = [0.0, 1.0, 2.0]
    derivs = [[f(x), fp(x)] for x in xs]
    zs, c = hermite_divided_differences(xs, derivs)
    assert len(c) == 6                                    # degree 5
    for x in xs:
        assert hermite_eval(zs, c, np.array([x]))[0] == pytest.approx(f(x), abs=1e-12)
        h = 1e-6
        num = (hermite_eval(zs, c, np.array([x + h]))[0]
               - hermite_eval(zs, c, np.array([x - h]))[0]) / (2 * h)
        assert num == pytest.approx(fp(x), abs=1e-7)


def test_hermite_exact_on_polynomials_of_the_right_degree():
    g = lambda x: 2 * x ** 3 - x + 1
    gp = lambda x: 6 * x ** 2 - 1
    zs, c = hermite_divided_differences([0.0, 1.0], [[g(0.), gp(0.)], [g(1.), gp(1.)]])
    t = np.linspace(-1, 2, 31)
    np.testing.assert_allclose(hermite_eval(zs, c, t), g(t), atol=1e-12)


def test_hermite_degenerate_cases():
    """[S4] Rem. 1.29: all d_i = 0 is ordinary interpolation; one knot is Taylor."""
    zs, c = hermite_divided_differences(list(XS), [[y] for y in YS])
    t = np.linspace(-1, 5, 21)
    np.testing.assert_allclose(hermite_eval(zs, c, t), lagrange_eval(XS, YS, t), rtol=1e-10)

    N = 5
    zs, c = hermite_divided_differences([0.0], [[1.0] * (N + 1)])      # exp at 0
    for k in range(N + 1):
        assert c[k] == pytest.approx(1.0 / _factorial(k))
    x = 0.3
    assert hermite_eval(zs, c, np.array([x]))[0] == pytest.approx(
        sum(x ** k / _factorial(k) for k in range(N + 1)))


def test_hermite_mixed_multiplicities():
    """Value at three knots plus the derivative at one -- the F3 2.1b shape."""
    f = lambda x: np.exp(x)
    xs = [0.5, 1.0, 2.0]
    derivs = [[f(0.5), f(0.5)], [f(1.0)], [f(2.0)]]        # d = (1, 0, 0)
    val = hermite(xs, derivs, np.array([0.5, 1.0, 2.0]))
    np.testing.assert_allclose(val, f(np.array([0.5, 1.0, 2.0])), atol=1e-12)
    zs, c = hermite_divided_differences(xs, derivs)
    assert len(c) == 4                                     # cubic


def test_lebesgue_function_is_one_at_the_knots_and_peaks_at_lambda_n():
    """[S4 §1.6]: sum_i |l_i(x_j)| = 1, and max_x of it is Lambda_n."""
    xs = np.linspace(-1, 1, 8)
    np.testing.assert_allclose(lebesgue_function(xs, xs), 1.0, atol=1e-13)
    t = np.linspace(-1, 1, 20001)
    assert lebesgue_function(xs, t).max() == pytest.approx(lebesgue_constant(xs), rel=1e-4)
