import numpy as np

from least_squares import (bias_variance_simulation, effective_dof, hat_matrix,
                           in_sample_excess_risk, kernel_ridge, krr_predict, ols,
                           poly_design, random_design_excess_risk, ridge, ridge_dual,
                           ridge_risk_bound, ridge_risk_exact, ridge_risk_mc)


def test_ols_matches_lstsq_and_normal_equations():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(50, 4)); y = rng.normal(size=50)
    w = ols(X, y)
    assert np.allclose(w, np.linalg.lstsq(X, y, rcond=None)[0])
    assert np.allclose(X.T @ (y - X @ w), 0, atol=1e-10)   # residual orthogonal to col(X)


def test_hat_matrix_is_orthogonal_projector():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(20, 3))
    H = hat_matrix(X)
    assert np.allclose(H @ H, H) and np.allclose(H, H.T)
    assert abs(np.trace(H) - 3) < 1e-10


def test_ridge_primal_equals_dual_and_shrinks():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(30, 5)); y = rng.normal(size=30)
    for lam in (0.1, 1.0, 10.0):
        assert np.allclose(ridge(X, y, lam), ridge_dual(X, y, lam))
    assert np.linalg.norm(ridge(X, y, 10.0)) < np.linalg.norm(ridge(X, y, 0.1)) < np.linalg.norm(ols(X, y))
    assert effective_dof(X, 1e-12) > effective_dof(X, 1.0) > effective_dof(X, 100.0)


def test_ridge_matches_sklearn():
    from sklearn.linear_model import Ridge
    rng = np.random.default_rng(3)
    X = rng.normal(size=(40, 6)); y = rng.normal(size=40)
    sk = Ridge(alpha=2.0, fit_intercept=False).fit(X, y)
    assert np.allclose(ridge(X, y, 2.0), sk.coef_, atol=1e-8)


def test_bias_variance_decomposition_adds_up_and_trades_off():
    rng = np.random.default_rng(4)
    f = lambda x: np.sin(2 * np.pi * x)
    res = bias_variance_simulation(f, 40, 0.3, [1, 5, 12], 150, rng)
    for b, v, s, tot in res.values():
        assert abs(tot - (b + v + s)) < 1e-12
    assert res[1][0] > res[5][0]   # bias^2 drops with degree
    assert res[12][1] > res[5][1]  # variance rises with degree


def test_fixed_design_excess_risk_is_sigma2_d():
    rng = np.random.default_rng(5)
    X = rng.normal(size=(60, 5))
    mc = in_sample_excess_risk(X, np.arange(5.0), 1.5, 3000, rng)
    assert abs(mc - 1.5**2 * 5) < 0.8


def test_kernel_ridge_matches_sklearn_and_linear_kernel_equals_ridge():
    from sklearn.kernel_ridge import KernelRidge
    rng = np.random.default_rng(6)
    X = rng.normal(size=(30, 3)); y = rng.normal(size=30)
    K = X @ X.T
    alpha = kernel_ridge(K, y, 0.5)
    assert np.allclose(krr_predict(alpha, K), X @ ridge(X, y, 0.5))
    sk = KernelRidge(alpha=0.5, kernel="linear").fit(X, y)
    assert np.allclose(sk.dual_coef_, alpha, atol=1e-8)


def test_ols_matches_sklearn_linear_regression():
    from sklearn.linear_model import LinearRegression
    rng = np.random.default_rng(7)
    X = rng.normal(size=(30, 4)); y = rng.normal(size=30)
    assert np.allclose(ols(X, y), LinearRegression(fit_intercept=False).fit(X, y).coef_)


def test_random_design_excess_risk_closed_form():
    # E||w_hat - w*||^2 = sigma^2 d / (n - d - 1) for Gaussian rows.
    rng = np.random.default_rng(8)
    n, d, sigma = 20, 3, 1.0
    mc = random_design_excess_risk(n, d, sigma, 20_000, rng)
    assert abs(mc - sigma**2 * d / (n - d - 1)) < 0.01


def test_ridge_risk_exact_matches_simulation_and_bound():
    # Theorem 7.9(c): the exact decomposition, reproduced by simulation, and <= the bound.
    rng = np.random.default_rng(9)
    X = rng.normal(size=(25, 3)); w = np.array([1.0, -2.0, 0.5])
    for lam in (0.5, 5.0, 50.0):
        exact = ridge_risk_exact(X, w, 0.7, lam)
        assert exact <= ridge_risk_bound(X, w, 0.7, lam) + 1e-12
        assert abs(ridge_risk_mc(X, w, 0.7, lam, 20_000, rng) - exact) < 0.02 * exact + 1e-3
    assert abs(ridge_risk_exact(X, w, 0.7, 1e-12) - 0.7**2 * 3 / 25) < 1e-9   # lam -> 0: sigma^2 d / n
