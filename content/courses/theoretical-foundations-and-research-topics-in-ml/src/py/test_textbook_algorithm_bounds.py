"""Rademacher complexity and per-algorithm guarantees, verified against the books.

Covers notes 05-09: Massart's lemma and the Rademacher complexity of the
threshold and linear classes, the stability rate of regularised loss
minimisation, the ridge bias constant, the OLS in-sample excess risk, and the
SVM worked example with the support-vector leave-one-out bound.

Part of the textbook-verification suite (see ../README.md). Each test hard-codes
the expression as the source states it and compares it against an independently
computed quantity, so a *misremembered constant* in the notes -- a wrong sign, a
stray factor of two, a log that should be a log-log, an exponent inside a square
root instead of outside -- fails here rather than being read past.

Locators refer to ../../refs/SOURCES.md:

    S9  = Shalev-Shwartz & Ben-David, Understanding Machine Learning (2014)
    S10 = Mohri, Rostamizadeh & Talwalkar, Foundations of ML, 2nd ed. (2018)
"""
import math

import numpy as np
import pytest

import least_squares
import rademacher
import svm


# --- Rademacher: S10 Thm 3.7 (Massart), S10 Thm 5.10 (linear) ---------------

def test_massart_bound_dominates_exact_rademacher_complexity():
    """S10 Thm 3.7: R_S(F) <= (r/n) sqrt(2 log|F|), r = max_f ||f|_S||_2.

    Compared against R_S computed EXACTLY by enumerating all 2^n sign vectors,
    so any factor-of-two slip in either expression shows up.
    """
    rng = np.random.default_rng(2)
    for n in (4, 6, 8):
        signs = np.array(np.meshgrid(*[[-1.0, 1.0]] * n)).T.reshape(-1, n)
        for n_f in (2, 5, 20):
            F = rng.choice([-1.0, 1.0], size=(n_f, n))
            exact = float(np.mean(np.max(signs @ F.T, axis=1)) / n)
            r = float(np.max(np.linalg.norm(F, axis=1)))
            assert exact <= r * math.sqrt(2 * math.log(n_f)) / n + 1e-12
            assert exact <= rademacher.massart_bound(n_f, n) + 1e-12


def test_threshold_class_on_two_points_has_rademacher_complexity_three_quarters():
    """Note 05's worked example, computed exactly.

    Thresholds on x1 < x2 realise (-,-), (-,+), (+,+) but not (+,-), so
    R_S = (1/4)(1 + 1 + 1 + 0) = 3/4. Massart with |F|=3 gives ~1.05: vacuous
    at n=2, exactly as the note says.
    """
    F = np.array([[-1.0, -1.0], [-1.0, 1.0], [1.0, 1.0]])
    signs = np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]], float)
    exact = float(np.mean(np.max(signs @ F.T, axis=1)) / 2)
    assert exact == pytest.approx(0.75)

    r = math.sqrt(2)                       # every row has norm sqrt(2)
    assert r * math.sqrt(2 * math.log(3)) / 2 == pytest.approx(1.0481, abs=1e-3)

    rng = np.random.default_rng(3)
    assert rademacher.rademacher_threshold(np.array([0.2, 0.8]), 20000, rng) == \
        pytest.approx(0.75, abs=0.02)


def test_linear_class_rademacher_exact_bound_and_jensen_gap():
    """S10 Thm 5.10: R_S({<w,.> : ||w||<=L}) <= sqrt(r^2 L^2 / m) = r L / sqrt(m).

    The exact value is (B/n) E||sum sigma_i x_i||, and the note's two limiting
    cases are checked: near-orthogonal rows saturate the bound, while identical
    rows give sqrt(2/pi) ~ 0.798 of it.
    """
    rng = np.random.default_rng(4)
    n, B = 200, 1.0

    # Near-orthogonal high-dimensional rows: exact ~ bound.
    X = rng.normal(size=(n, 400))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    exact = rademacher.rademacher_linear_exact(X, B, 4000, rng)
    bound = rademacher.rademacher_linear_bound(X, B)
    assert exact <= bound + 1e-9
    assert bound == pytest.approx(B * 1.0 / math.sqrt(n), rel=1e-9)
    assert exact == pytest.approx(bound, rel=0.05)

    # All rows equal: ||sum sigma_i x_i|| = |sum sigma_i|, E|.| ~ sqrt(2n/pi).
    Xsame = np.ones((n, 3)) / math.sqrt(3)
    exact_same = rademacher.rademacher_linear_exact(Xsame, B, 20000, rng)
    assert exact_same == pytest.approx(B * math.sqrt(2 / (math.pi * n)), rel=0.05)
    assert exact_same == pytest.approx(0.798 * B / math.sqrt(n), rel=0.05)


# --- Stability: S9 Cor. 13.6 and Cor. 13.9 ----------------------------------

def test_rlm_stability_rate_and_its_optimal_lambda():
    """S9 Cor. 13.6: RLM with lambda||w||^2 is (2 rho^2 / (lambda m))-stable.
    S9 Cor. 13.9: minimising lambda B^2 + 2 rho^2/(lambda m) over lambda gives
    lambda* = sqrt(2 rho^2 / (B^2 m)) and value sqrt(8 rho^2 B^2 / m).

    Note 09 Thm 9.8 quotes exactly this with rho = R. Verified symbolically-by-
    numerics: the closed form must equal the numerical minimum.
    """
    def excess(lam, rho, B, m):
        return lam * B**2 + 2 * rho**2 / (lam * m)

    for rho, B, m in [(1.0, 1.0, 100), (2.0, 0.5, 1000), (0.3, 3.0, 50)]:
        lam_star = math.sqrt(2 * rho**2 / (B**2 * m))
        value = math.sqrt(8 * rho**2 * B**2 / m)
        assert excess(lam_star, rho, B, m) == pytest.approx(value)

        grid = np.geomspace(lam_star / 50, lam_star * 50, 20001)
        assert excess(lam_star, rho, B, m) == pytest.approx(
            float(np.min(excess(grid, rho, B, m))), rel=1e-6)


# --- Ridge: note 07 Thm 7.9(c) ----------------------------------------------

def test_ridge_bias_bound_lambda_over_four():
    """Note 07 Thm 7.9(c): ||(I - H_lam) X w*||^2 <= (lambda/4) ||w*||^2.

    (I - H_lam) X = lambda X (X'X + lambda I)^-1, so the squared norm is
    lambda^2 sum_j s_j (w*_j)^2 / (s_j + lambda)^2, and max over s >= 0 of
    lambda^2 s / (s + lambda)^2 is lambda/4, attained at s = lambda. The test
    checks the inequality on random designs AND that lambda/4 is attained, which
    a wrong constant (lambda/2, lambda) would not satisfy.
    """
    rng = np.random.default_rng(5)
    for _ in range(30):
        n, d = 40, 6
        X = rng.normal(size=(n, d))
        w = rng.normal(size=d)
        lam = float(rng.uniform(0.05, 20.0))
        H = X @ np.linalg.solve(X.T @ X + lam * np.eye(d), X.T)
        bias2 = float(np.sum(((np.eye(n) - H) @ X @ w) ** 2))
        assert bias2 <= lam / 4 * float(w @ w) + 1e-8

    # Tightness: one direction with singular value exactly sqrt(lambda).
    lam = 4.0
    X = np.diag([math.sqrt(lam)])
    w = np.array([1.0])
    H = X @ np.linalg.solve(X.T @ X + lam * np.eye(1), X.T)
    bias2 = float(np.sum(((np.eye(1) - H) @ X @ w) ** 2))
    assert bias2 == pytest.approx(lam / 4 * float(w @ w))


def test_ols_in_sample_excess_risk_is_sigma_squared_d():
    """Note 07 Thm 7.3(c): E||X w_hat - X w*||^2 = sigma^2 d, exactly, since
    X w_hat - X w* = H eps and E eps' H eps = sigma^2 tr H = sigma^2 d."""
    rng = np.random.default_rng(6)
    n, d, sigma = 120, 5, 0.7
    X = rng.normal(size=(n, d))
    H = least_squares.hat_matrix(X)
    assert float(np.trace(H)) == pytest.approx(d, abs=1e-8)

    w_star = rng.normal(size=d)
    vals = []
    for _ in range(4000):
        y = X @ w_star + sigma * rng.normal(size=n)
        vals.append(float(np.sum((X @ least_squares.ols(X, y) - X @ w_star) ** 2)))
    assert float(np.mean(vals)) == pytest.approx(sigma**2 * d, rel=0.06)


# --- SVM: note 09 worked example, S10 Thm 5.4 -------------------------------

def test_svm_worked_example_matches_the_hand_computation():
    """Note 09's four-point example, solved by hand:
    w* = (1/2, 1/2), b = 0, geometric margin sqrt(2), SVs {x1, x3},
    alpha_1 = alpha_3 = 1/4, sum alpha = ||w*||^2 = 1/2, dual value 1/4.
    """
    X = np.array([[1.0, 1.0], [2.0, 2.0], [-1.0, -1.0], [-2.0, -2.0]])
    y = np.array([1.0, 1.0, -1.0, -1.0])

    model = svm.SVM(C=None).fit(X, y)
    assert model.w() == pytest.approx(np.array([0.5, 0.5]), abs=1e-4)
    assert model.b_ == pytest.approx(0.0, abs=1e-4)
    assert model.margin() == pytest.approx(math.sqrt(2), rel=1e-3)
    assert sorted(model.support_.tolist()) == [0, 2]

    # alpha_ already holds only the support vectors, in index order.
    assert model.alpha_ == pytest.approx(np.array([0.25, 0.25]), abs=1e-4)
    assert float(model.alpha_.sum()) == pytest.approx(0.5, abs=1e-4)      # = ||w*||^2
    # Strong duality: dual value = (1/2)||w*||^2 = 1/4.
    w = model.w()
    assert float(model.alpha_.sum() - 0.5 * w @ w) == pytest.approx(0.25, abs=1e-4)


def test_leave_one_out_support_vector_bound_is_respected():
    """S10 Thm 5.4: E_{S~D^m}[R(h_S)] <= E_{S~D^{m+1}}[N_SV(S)] / (m+1).

    Checked by simulation on a separable 2-D problem: the measured leave-one-out
    error never exceeds the support-vector fraction, because every leave-one-out
    mistake must be a support vector.
    """
    rng = np.random.default_rng(7)
    for _ in range(12):
        X, y = svm.make_blobs(16, 1.0, rng)
        full = svm.SVM(C=None).fit(X, y)
        n_sv = len(full.support_)

        errors = 0
        for i in range(len(y)):
            keep = np.arange(len(y)) != i
            m = svm.SVM(C=None).fit(X[keep], y[keep])
            errors += int(m.predict(X[i:i + 1])[0] != y[i])
        assert errors <= n_sv
