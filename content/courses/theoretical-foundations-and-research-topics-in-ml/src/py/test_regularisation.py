import numpy as np

from regularisation import (bias_complexity_curve, fit_least_squares, logistic_loss, mse,
                            poly_features, rlm_logistic, sample_ball_classification,
                            srm_select, stability_experiment, target, tikhonov,
                            validation_bound, validation_experiment, validation_select)


def test_nested_classes_train_error_monotone():
    rng = np.random.default_rng(0)
    curve = bias_complexity_curve(30, range(0, 12), 0.3, rng)
    train = [curve[d][0] for d in range(0, 12)]
    assert all(a >= b - 1e-12 for a, b in zip(train, train[1:]))


def test_u_shaped_test_error():
    rng = np.random.default_rng(1)
    curve = bias_complexity_curve(30, range(0, 16), 0.3, rng)
    test = {d: curve[d][1] for d in curve}
    best = min(test, key=test.get)
    assert 2 <= best <= 9            # sine needs a few degrees
    assert test[0] > test[best] and test[15] > test[best]


def test_srm_and_validation_pick_moderate_degree():
    rng = np.random.default_rng(2)
    n = 40
    x = rng.uniform(-1, 1, n); y = target(x) + 0.3 * rng.normal(size=n)
    xv = rng.uniform(-1, 1, n); yv = target(xv) + 0.3 * rng.normal(size=n)
    d_srm, _, _ = srm_select(x, y, range(0, 16), scale=0.5)
    d_val, _, _ = validation_select(x, y, xv, yv, range(0, 16))
    assert 2 <= d_srm <= 9 and 2 <= d_val <= 9


def test_tikhonov_shrinks_and_reduces_to_ols():
    rng = np.random.default_rng(3)
    x = rng.uniform(-1, 1, 30); y = target(x) + 0.3 * rng.normal(size=30)
    Phi = poly_features(x, 6)
    w0 = fit_least_squares(Phi, y)
    assert np.allclose(tikhonov(Phi, y, 1e-14), w0, atol=1e-6)
    norms = [np.linalg.norm(tikhonov(Phi, y, lam)) for lam in (1e-4, 1e-2, 1, 100)]
    assert all(a > b for a, b in zip(norms, norms[1:]))


def test_validation_bound_holds_empirically():
    # A single fixed predictor: |L_D - L_V| exceeds the Hoeffding bound with prob <= delta.
    rng = np.random.default_rng(4)
    n_val, delta = 50, 0.1
    w = np.array([0.0, 1.0])
    # true risk under clipped loss in [0,1]: estimate with a huge sample
    xb = rng.uniform(-1, 1, 200_000); yb = target(xb) + 0.3 * rng.normal(size=200_000)
    loss = lambda x, y: np.minimum(1.0, (poly_features(x, 1) @ w - y) ** 2)
    L = loss(xb, yb).mean()
    viol = 0
    for _ in range(500):
        xv = rng.uniform(-1, 1, n_val); yv = target(xv) + 0.3 * rng.normal(size=n_val)
        viol += abs(loss(xv, yv).mean() - L) > validation_bound(1, n_val, delta)
    assert viol / 500 <= delta


def test_tikhonov_matches_sklearn_ridge():
    # (1/n)||Phi w - y||^2 + lam ||w||^2  <=>  sklearn ||Phi w - y||^2 + alpha ||w||^2, alpha = n lam.
    from sklearn.linear_model import Ridge
    rng = np.random.default_rng(5)
    x = rng.uniform(-1, 1, 40); y = target(x) + 0.3 * rng.normal(size=40)
    Phi = poly_features(x, 5)
    sk = Ridge(alpha=40 * 0.01, fit_intercept=False).fit(Phi, y)
    assert np.allclose(tikhonov(Phi, y, 0.01), sk.coef_, atol=1e-8)


def test_logistic_rlm_is_stationary_and_matches_sklearn():
    # (1/n) sum l + lam ||w||^2  <=>  sklearn 0.5||w||^2 + C sum l with C = 1/(2 n lam).
    from sklearn.linear_model import LogisticRegression
    rng = np.random.default_rng(6)
    n, lam = 80, 0.02
    X, y = sample_ball_classification(n, 4, rng)
    w = rlm_logistic(X, y, lam)
    p = 1 / (1 + np.exp(-X @ w))
    assert np.linalg.norm(X.T @ (p - (y + 1) / 2) / n + 2 * lam * w) < 1e-12
    sk = LogisticRegression(C=1 / (2 * n * lam), fit_intercept=False, tol=1e-12, max_iter=10_000).fit(X, y)
    assert np.allclose(w, sk.coef_.ravel(), atol=1e-6)


def test_rlm_stability_theorems_6_6_and_6_7():
    rng = np.random.default_rng(7)
    n, lam, T = 40, 0.05, 300
    r = stability_experiment(n, 3, lam, T, rng)
    assert np.all(r["dw"] <= r["bound_w"]) and np.all(r["replace"] <= r["bound_loss"])
    se = np.sqrt(r["gap"].var() / T + r["replace"].var() / T)
    assert abs(r["gap"].mean() - r["replace"].mean()) < 4 * se   # Theorem 6.6 is an identity
    assert r["gap"].mean() <= r["bound_loss"]


def test_validation_experiment_theorem_6_9():
    rng = np.random.default_rng(8)
    freq, bound = validation_experiment(40, 0.05, 4000, rng)
    assert freq <= 0.05 and abs(bound - np.sqrt(np.log(2 / 0.05) / 80)) < 1e-12
