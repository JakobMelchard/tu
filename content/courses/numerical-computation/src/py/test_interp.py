import numpy as np
import scipy.interpolate

from interp import (lagrange_basis, barycentric_weights, lagrange_eval, barycentric_eval, divided_differences, newton_eval,
                    chebyshev_nodes, runge, thomas, cubic_spline, spline_eval,
                    vandermonde, lstsq_normal, lstsq_qr, polyfit, polyval,
                    orthogonal_polys, orthogonal_lstsq)

XS = np.array([0.0, 1.0, 2.0, 4.0])
YS = np.array([1.0, 3.0, 2.0, 5.0])
T = np.linspace(-1, 5, 41)


def test_three_forms_agree_and_match_scipy():
    ref = scipy.interpolate.BarycentricInterpolator(XS, YS)(T)
    np.testing.assert_allclose(lagrange_eval(XS, YS, T), ref, rtol=1e-10)
    np.testing.assert_allclose(barycentric_eval(XS, YS, T), ref, rtol=1e-10)
    c = divided_differences(XS, YS)
    np.testing.assert_allclose(newton_eval(XS, c, T), ref, rtol=1e-10)
    np.testing.assert_allclose(barycentric_eval(XS, YS, XS), YS)     # hits the nodes


def test_divided_differences_known_table():
    np.testing.assert_allclose(divided_differences(XS, YS), [1, 2, -1.5, 7 / 12])


def test_interpolation_reproduces_polynomials():
    p = lambda x: 2 * x ** 3 - x + 1
    xs = np.array([-1.0, 0.5, 2.0, 3.0])
    np.testing.assert_allclose(lagrange_eval(xs, p(xs), T), p(T), rtol=1e-12)


def test_chebyshev_nodes_and_lebesgue_effect():
    x = chebyshev_nodes(4)
    np.testing.assert_allclose(x, np.sort(np.cos((2 * np.arange(4) + 1) * np.pi / 8)))
    x = chebyshev_nodes(5, 0, 2)
    assert x.min() > 0 and x.max() < 2
    tt = np.linspace(-1, 1, 1001)
    n = 21
    xe, xc = np.linspace(-1, 1, n), chebyshev_nodes(n)
    err_e = np.max(np.abs(barycentric_eval(xe, runge(xe), tt) - runge(tt)))
    err_c = np.max(np.abs(barycentric_eval(xc, runge(xc), tt) - runge(tt)))
    assert err_e > 10 and err_c < 0.05                          # Runge phenomenon


def test_thomas_matches_numpy():
    n = 7
    lower, diag, upper = -np.ones(n - 1), 4 * np.ones(n), -np.ones(n - 1)
    A = np.diag(diag) + np.diag(lower, -1) + np.diag(upper, 1)
    b = np.arange(1.0, n + 1)
    np.testing.assert_allclose(thomas(lower, diag, upper, b), np.linalg.solve(A, b), rtol=1e-12)


def test_natural_spline_matches_scipy():
    xs = np.linspace(0, 3, 8)
    ys = np.sin(xs) * np.exp(-xs)
    t = np.linspace(0, 3, 101)
    ref = scipy.interpolate.CubicSpline(xs, ys, bc_type="natural")(t)
    np.testing.assert_allclose(spline_eval(cubic_spline(xs, ys), t), ref, atol=1e-12)


def test_clamped_spline_matches_scipy_and_is_fourth_order():
    f, df = np.sin, np.cos
    for n in (8, 16):
        xs = np.linspace(0, 2, n + 1)
        t = np.linspace(0, 2, 401)
        spl = cubic_spline(xs, f(xs), "clamped", df(0), df(2))
        ref = scipy.interpolate.CubicSpline(xs, f(xs), bc_type=((1, df(0)), (1, df(2))))(t)
        np.testing.assert_allclose(spline_eval(spl, t), ref, atol=1e-12)
    e8 = np.max(np.abs(spline_eval(cubic_spline(np.linspace(0, 2, 9), f(np.linspace(0, 2, 9)),
                                                "clamped", df(0), df(2)), t) - f(t)))
    e16 = np.max(np.abs(spline_eval(cubic_spline(np.linspace(0, 2, 17), f(np.linspace(0, 2, 17)),
                                                 "clamped", df(0), df(2)), t) - f(t)))
    assert abs(np.log2(e8 / e16) - 4) < 0.3


def test_least_squares_matches_numpy():
    rng = np.random.default_rng(2)
    x = np.linspace(0, 1, 40)
    y = 1 + 2 * x - 3 * x ** 2 + 0.01 * rng.standard_normal(40)
    ref = np.polyfit(x, y, 2)[::-1]
    np.testing.assert_allclose(polyfit(x, y, 2, "qr"), ref, rtol=1e-9)
    np.testing.assert_allclose(polyfit(x, y, 2, "normal"), ref, rtol=1e-9)
    A = vandermonde(x, 2)
    np.testing.assert_allclose(lstsq_qr(A, y), np.linalg.lstsq(A, y, rcond=None)[0], rtol=1e-9)
    np.testing.assert_allclose(lstsq_normal(A, y), np.linalg.lstsq(A, y, rcond=None)[0], rtol=1e-9)


def test_qr_more_accurate_than_normal_equations_when_ill_conditioned():
    x = np.linspace(0, 1, 60)
    y = np.exp(x)
    deg = 14
    A = vandermonde(x, deg)
    c_qr = lstsq_qr(A, y)
    res_qr = np.max(np.abs(A @ c_qr - y))
    try:
        c_ne = lstsq_normal(A, y)
        res_ne = np.max(np.abs(A @ c_ne - y))
    except ValueError:                                          # Cholesky breaks down
        res_ne = np.inf
    assert res_qr < 1e-10 and res_ne > res_qr


def test_orthogonal_polynomials():
    x = np.linspace(-1, 1, 30)
    P, _ = orthogonal_polys(x, 5)
    G = P.T @ P
    assert np.max(np.abs(G - np.diag(np.diag(G)))) < 1e-10 * np.max(G)
    y = np.cos(2 * x)
    fit, c = orthogonal_lstsq(x, y, 5)
    np.testing.assert_allclose(fit, polyval(polyfit(x, y, 5), x), atol=1e-10)


def test_lagrange_basis_is_cardinal_and_a_partition_of_unity():
    """[S4 §1.1]: l_j(x_i) = delta_ij, and sum_j l_j = 1 (interpolate f = 1)."""
    xs = np.array([-1.0, -0.2, 0.5, 1.0])
    L = np.array([lagrange_basis(xs, j, xs) for j in range(len(xs))])
    np.testing.assert_allclose(L, np.eye(len(xs)), atol=1e-14)
    t = np.linspace(-1, 1, 7)
    np.testing.assert_allclose(sum(lagrange_basis(xs, j, t) for j in range(len(xs))), 1.0)


def test_barycentric_weights_match_scipy_up_to_scale():
    xs = chebyshev_nodes(9, -1.0, 1.0)
    w = barycentric_weights(xs)
    ref = scipy.interpolate.BarycentricInterpolator(xs, np.zeros_like(xs)).wi
    np.testing.assert_allclose(w / w[0], ref / ref[0], rtol=1e-10)
