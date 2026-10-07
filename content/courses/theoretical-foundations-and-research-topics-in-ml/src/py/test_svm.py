import numpy as np

from kernels import rbf_kernel
from svm import (SVM, leave_one_out_error, make_blobs, make_margin_data, perceptron,
                 solve_dual)


def test_hard_margin_by_hand():
    X = np.array([[1.0, 1.0], [2.0, 2.0], [-1.0, -1.0], [-2.0, -2.0]])
    y = np.array([1, 1, -1, -1])
    m = SVM(C=None).fit(X, y)
    assert np.allclose(m.w(), [0.5, 0.5], atol=1e-4)
    assert abs(m.b_) < 1e-4
    assert abs(m.margin() - np.sqrt(2)) < 1e-3
    assert set(m.support_) == {0, 2}


def test_kkt_conditions_soft_margin():
    rng = np.random.default_rng(0)
    X, y = make_blobs(60, 0.5, rng)
    C = 1.0
    m = SVM(C=C).fit(X, y)
    K = X @ X.T
    alpha = solve_dual(K, y.astype(float), C)
    assert abs(alpha @ y) < 1e-6                     # sum alpha_i y_i = 0
    f = m.decision_function(X)
    marg = y * f
    free = (alpha > 1e-5) & (alpha < C - 1e-5)
    assert np.allclose(marg[free], 1.0, atol=1e-3)   # free SVs sit on the margin
    assert np.all(marg[alpha < 1e-5] >= 1 - 1e-3)    # alpha=0 -> outside margin
    assert np.all(marg[alpha > C - 1e-5] <= 1 + 1e-3)  # alpha=C -> margin violators


def test_matches_sklearn_linear_and_rbf():
    from sklearn.svm import SVC
    rng = np.random.default_rng(1)
    X, y = make_blobs(70, 0.8, rng)
    for C in (0.5, 5.0):
        m = SVM(C=C).fit(X, y)
        sk = SVC(C=C, kernel="linear").fit(X, y)
        assert np.allclose(m.w(), sk.coef_.ravel(), atol=2e-3)
        assert abs(m.b_ - sk.intercept_[0]) < 2e-3
        assert np.mean(m.predict(X) != sk.predict(X)) == 0
    gamma = 0.7
    m = SVM(C=2.0, kernel=lambda A, B: rbf_kernel(A, B, gamma)).fit(X, y)
    sk = SVC(C=2.0, kernel="rbf", gamma=gamma).fit(X, y)
    xt = rng.normal(size=(200, 2)) * 2
    assert np.allclose(m.decision_function(xt), sk.decision_function(xt), atol=5e-3)


def test_C_to_infinity_recovers_hard_margin():
    X = np.array([[1.0, 1.0], [2.0, 2.0], [-1.0, -1.0], [-2.0, -2.0]])
    y = np.array([1, 1, -1, -1])
    hard = SVM(C=None).fit(X, y)
    soft = SVM(C=1e4).fit(X, y)
    assert np.allclose(hard.w(), soft.w(), atol=1e-3)


def test_kernel_svm_separates_circles():
    rng = np.random.default_rng(2)
    t = rng.uniform(0, 2 * np.pi, 80); r = np.where(rng.uniform(size=80) < 0.5, 1.0, 2.5)
    X = np.stack([r * np.cos(t), r * np.sin(t)], 1)
    y = np.where(r > 2, 1, -1)
    m = SVM(C=10.0, kernel=lambda A, B: rbf_kernel(A, B, 1.0)).fit(X, y)
    assert np.mean(m.predict(X) != y) == 0


def test_leave_one_out_only_support_vectors_matter():
    # Theorem 9.6 via Lemma 5.3 of S10: refitting only the SVs gives the full LOO count,
    # and LOO mistakes <= N_SV.
    rng = np.random.default_rng(3)
    for _ in range(4):
        X, y = make_blobs(18, 0.05, rng)
        e_sv, nsv = leave_one_out_error(X, y, only_sv=True)
        e_all, _ = leave_one_out_error(X, y, only_sv=False)
        assert e_sv == e_all <= nsv


def test_perceptron_mistake_bound():
    # Theorem 9.9: at most (R/gamma)^2 mistakes for every ordering; the output separates.
    rng = np.random.default_rng(4)
    for g in (0.2, 0.05):
        X, y, w_star = make_margin_data(150, g, rng)
        gamma, R = np.min(y * (X @ w_star)), np.max(np.linalg.norm(X, axis=1))
        for _ in range(30):
            p = rng.permutation(len(y))
            w, mistakes = perceptron(X[p], y[p])
            assert mistakes <= (R / gamma) ** 2
            assert np.all(y * (X @ w) > 0)


def test_perceptron_closed_form_two_points():
    # x1 = (1,0), y=+1; x2 = (0,1), y=-1: first pass makes 2 mistakes, w = (1,-1), then clean.
    w, m = perceptron(np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([1.0, -1.0]))
    assert m == 2 and np.allclose(w, [1.0, -1.0])
