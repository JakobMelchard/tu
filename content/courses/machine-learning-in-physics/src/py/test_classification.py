"""Tests for classification.py (note 04), cross-checked against scikit-learn."""
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression

import classification as cl


@pytest.fixture
def blobs():
    return cl.make_blobs2(300, np.random.default_rng(0))


def test_sigmoid_is_stable():
    z = np.array([-800.0, -1.0, 0.0, 1.0, 800.0])
    p = cl.sigmoid(z)
    assert np.all(np.isfinite(p)) and p[2] == 0.5 and p[0] == 0.0 and p[-1] == 1.0
    assert np.allclose(p[1] + p[3], 1)


def test_gradient_matches_finite_differences(blobs):
    X, y = blobs
    Xb = cl.add_bias(X)
    w = np.array([0.1, -0.3, 0.7])
    g = cl.bce_grad(w, Xb, y, lam=0.5)
    h = 1e-6
    fd = [(cl.bce(w + h * e, Xb, y, 0.5) - cl.bce(w - h * e, Xb, y, 0.5)) / (2 * h)
          for e in np.eye(3)]
    assert np.allclose(g, fd, rtol=1e-6)


def test_newton_matches_sklearn(blobs):
    X, y = blobs
    lam = 2.0
    w = cl.logistic_newton(cl.add_bias(X), y, lam=lam)
    sk = LogisticRegression(C=1 / lam, tol=1e-12, max_iter=10000).fit(X, y)
    assert np.allclose(w, np.r_[sk.intercept_, sk.coef_[0]], atol=1e-6)


def test_gd_approaches_newton(blobs):
    X, y = blobs
    Xb = cl.add_bias(X)
    assert np.allclose(cl.logistic_gd(Xb, y, lam=1.0, eta=1.0, epochs=5000),
                       cl.logistic_newton(Xb, y, lam=1.0), atol=1e-4)


def test_separable_data_weights_diverge_without_regularisation():
    X = np.array([[-2.0], [-1.0], [1.0], [2.0]])
    y = np.array([0, 0, 1, 1])
    w_small = cl.logistic_gd(cl.add_bias(X), y, eta=1.0, epochs=100)
    w_large = cl.logistic_gd(cl.add_bias(X), y, eta=1.0, epochs=10000)
    assert abs(w_large[1]) > 2 * abs(w_small[1])          # no finite minimiser
    w_reg = cl.logistic_newton(cl.add_bias(X), y, lam=1.0)
    assert np.isfinite(w_reg).all() and abs(w_reg[1]) < 5


def test_softmax_two_classes_reduces_to_logistic(blobs):
    X, y = blobs
    Xb = cl.add_bias(X)
    W = cl.softmax_fit(Xb, y.astype(int), 2, lam=0.0, eta=1.0, epochs=4000)
    w = cl.logistic_newton(Xb, y)
    assert np.allclose(W[:, 1] - W[:, 0], w, atol=1e-2)   # only differences are identifiable


def test_softmax_gradient_and_accuracy():
    rng = np.random.default_rng(1)
    X = cl.add_bias(rng.normal(size=(20, 3)))
    Y = cl.one_hot(rng.integers(0, 4, 20), 4)
    W = rng.normal(size=(4, 4))
    _, G = cl.softmax_loss_grad(W, X, Y, lam=0.3)
    h = 1e-6
    for i, j in [(0, 0), (2, 3), (3, 1)]:
        E = np.zeros_like(W)
        E[i, j] = h
        fd = (cl.softmax_loss_grad(W + E, X, Y, 0.3)[0] - cl.softmax_loss_grad(W - E, X, Y, 0.3)[0]) / (2 * h)
        assert G[i, j] == pytest.approx(fd, rel=1e-6)


def test_kernel_features_solve_xor():
    rng = np.random.default_rng(4711)
    X, y = cl.make_xor(1000, rng)
    lin = cl.logistic_newton(cl.add_bias(X), y, lam=1e-3)
    assert np.mean((cl.add_bias(X) @ lin > 0) == y) < 0.65
    C = rng.uniform(-1, 1, size=(40, 2))
    F = cl.add_bias(cl.rbf_features(X, C, 4.0))
    wk = cl.logistic_newton(F, y, lam=1e-2)
    Xt, yt = cl.make_xor(1000, rng)
    Ft = cl.add_bias(cl.rbf_features(Xt, C, 4.0))
    assert np.mean((Ft @ wk > 0) == yt) > 0.95


def test_confusion_rates():
    y = np.array([1, 1, 1, 0, 0, 0, 0, 0])
    p = np.array([1, 0, 1, 0, 0, 1, 0, 0])
    c = cl.confusion(y, p)
    assert c["matrix"].tolist() == [[4, 1], [1, 2]]
    assert c["sensitivity"] == pytest.approx(2 / 3) and c["specificity"] == pytest.approx(0.8)
    assert c["accuracy"] == pytest.approx(6 / 8)
