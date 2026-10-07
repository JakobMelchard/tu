import numpy as np

from deep_theory import (MLP, double_descent_curve, gd_least_squares, hat_network,
                         min_norm_least_squares, min_norm_risk_simulation,
                         random_relu_features, ridgeless_risk, target,
                         universal_approximation_demo)


def test_hat_network_is_exact():
    hat = hat_network(0.2, 0.5, 0.8)
    x = np.array([0.0, 0.2, 0.35, 0.5, 0.65, 0.8, 1.0])
    assert np.allclose(hat(x), [0, 0, 0.5, 1, 0.5, 0, 0])


def test_gradients_match_finite_differences():
    rng = np.random.default_rng(0)
    net = MLP(5, "tanh", rng)
    x = rng.uniform(size=7); y = rng.normal(size=7)
    gW, gb, gV, gc = net.gradients(x, y)
    eps = 1e-6
    for arr, g in ((net.W, gW), (net.b, gb), (net.V, gV)):
        for i in range(len(arr)):
            arr[i] += eps; lp = net.mse(x, y); arr[i] -= 2 * eps; lm = net.mse(x, y); arr[i] += eps
            assert abs((lp - lm) / (2 * eps) - g[i]) < 1e-5
    net.c += eps; lp = net.mse(x, y); net.c -= 2 * eps; lm = net.mse(x, y); net.c += eps
    assert abs((lp - lm) / (2 * eps) - gc) < 1e-5


def test_wider_networks_approximate_better():
    res = universal_approximation_demo(widths=(2, 16, 128), steps=1500)
    assert res[2] > res[16] > res[128]
    assert res[128] < 0.01


def test_min_norm_solution_interpolates_and_has_min_norm():
    rng = np.random.default_rng(1)
    Phi = rng.normal(size=(10, 30)); y = rng.normal(size=10)
    w = min_norm_least_squares(Phi, y)
    assert np.allclose(Phi @ w, y)
    # any other interpolator w + z with Phi z = 0 has larger norm
    z = rng.normal(size=30); z -= np.linalg.pinv(Phi) @ (Phi @ z)
    assert np.linalg.norm(w + z) > np.linalg.norm(w)


def test_gd_from_zero_converges_to_min_norm():
    rng = np.random.default_rng(2)
    Phi = rng.normal(size=(8, 20)); y = rng.normal(size=8)
    w = gd_least_squares(Phi, y, 20000)
    assert np.allclose(w, min_norm_least_squares(Phi, y), atol=1e-6)


def test_double_descent_peak_at_interpolation_threshold():
    res = double_descent_curve(n_train=40, widths=(20, 40, 800), trials=6, noise=0.1)
    assert res[40] > 5 * res[20] and res[40] > 5 * res[800]   # sharp peak at m = n
    assert res[800] < res[20]   # low noise: second descent beats the classical minimum
    noisy = double_descent_curve(n_train=40, widths=(20, 800), trials=6, noise=0.3)
    assert noisy[800] > noisy[20]   # high noise: interpolation is not benign


def test_ridge_removes_the_peak():
    ridgeless = double_descent_curve(n_train=40, widths=(40,), trials=4)[40]
    ridged = double_descent_curve(n_train=40, widths=(40,), trials=4, lam=1e-1)[40]
    assert ridged < ridgeless


def test_min_norm_matches_sklearn_linear_regression():
    # scipy lstsq inside sklearn also returns the minimum-norm solution when p > n.
    from sklearn.linear_model import LinearRegression
    rng = np.random.default_rng(3)
    Phi = rng.normal(size=(12, 40)); y = rng.normal(size=12)
    sk = LinearRegression(fit_intercept=False).fit(Phi, y)
    assert np.allclose(min_norm_least_squares(Phi, y), sk.coef_, atol=1e-10)


def test_underparameterised_risk_matches_finite_n_closed_form():
    # gamma < 1: E||beta_hat - beta||^2 = sigma^2 p/(n-p-1) exactly, -> sigma^2 gamma/(1-gamma).
    rng = np.random.default_rng(4)
    n, p, s2 = 60, 20, 1.0
    mc = min_norm_risk_simulation(n, p, 4.0, s2, 3000, rng)
    assert abs(mc - s2 * p / (n - p - 1)) < 0.03
    assert abs(ridgeless_risk(p / n, 4.0, s2) - 0.5) < 1e-12
    assert ridgeless_risk(2.0, 4.0, 1.0) == 3.0
