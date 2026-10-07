import numpy as np
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.linear_model import Perceptron as SkPerceptron
from sklearn.datasets import make_moons, make_blobs
from sklearn.preprocessing import StandardScaler

import mlp

X, y = make_moons(400, noise=0.25, random_state=0)
X = StandardScaler().fit_transform(X)
Xtr, Xte, ytr, yte = X[:300], X[300:], y[:300], y[300:]


def test_perceptron_separable():
    Xb, yb = make_blobs(100, centers=[[-3, -3], [3, 3]], cluster_std=1.0, random_state=0)
    ours = mlp.Perceptron().fit(Xb, yb)
    assert ours.errors_[-1] == 0 and np.mean(ours.predict(Xb) == yb) == 1.0
    assert SkPerceptron(random_state=0).fit(Xb, yb).score(Xb, yb) == 1.0


def test_gradient_check():
    for act in ("relu", "tanh", "sigmoid"):
        m = mlp.MLP((5, 4), act, l2=0.1, rng=1)
        m.classes_ = np.array([0, 1, 2]); m._init(3, 3)
        Xs = np.random.default_rng(0).normal(size=(7, 3)); Y = np.eye(3)[[0, 1, 2, 0, 1, 2, 0]]
        _, cache = m._forward(Xs)
        gW, gb = m._backward(cache, Y)
        num = mlp.numerical_gradient(m, Xs, Y)
        for a, b in zip(gW + gb, num):
            assert np.abs(a - b).max() < 1e-6


def test_mlp_classifier_matches_sklearn_accuracy():
    ours = mlp.MLP((32, 16), "relu", lr=0.01, epochs=150, optimizer="adam").fit(Xtr, ytr)
    theirs = MLPClassifier((32, 16), max_iter=1000, random_state=0).fit(Xtr, ytr)
    acc_o, acc_t = np.mean(ours.predict(Xte) == yte), theirs.score(Xte, yte)
    assert acc_o > 0.9 and abs(acc_o - acc_t) < 0.08
    assert ours.history_[-1][0] < ours.history_[0][0]


def test_sgd_momentum_and_early_stopping():
    m = mlp.MLP((16,), "tanh", lr=0.05, epochs=300, optimizer="sgd", early_stopping=True, patience=5).fit(Xtr, ytr, Xte, yte)
    assert len(m.history_) < 300 and np.mean(m.predict(Xte) == yte) > 0.85


def test_mlp_regressor():
    xr = np.linspace(-3, 3, 150)[:, None]; yr = np.sin(2 * xr[:, 0])
    ours = mlp.MLP((32, 32), "tanh", task="regression", lr=0.01, epochs=300, batch_size=16).fit(xr, yr)
    theirs = MLPRegressor(hidden_layer_sizes=(32, 32), activation="tanh", max_iter=3000, random_state=0).fit(xr, yr)
    mse_o, mse_t = np.mean((ours.predict(xr) - yr) ** 2), np.mean((theirs.predict(xr) - yr) ** 2)
    assert mse_o < 0.05 and mse_t < 0.2
