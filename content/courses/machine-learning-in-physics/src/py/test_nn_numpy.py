"""Tests for nn_numpy.py (note 05): gradient checks, XOR, approximation, early stopping."""
import numpy as np
import pytest

import nn_numpy as nn


@pytest.mark.parametrize("act", ["tanh", "sigmoid", "relu"])
@pytest.mark.parametrize("out", ["softmax", "identity"])
def test_backprop_matches_finite_differences(act, out):
    rng = np.random.default_rng(7)
    X = rng.normal(size=(6, 3))
    Y = np.eye(2)[rng.integers(0, 2, 6)] if out == "softmax" else rng.normal(size=(6, 2))
    net = nn.MLP([3, 5, 4, 2], hidden=act, out=out, seed=2)
    assert nn.grad_check(net, X, Y) < 1e-7


def test_xor_needs_and_gets_a_hidden_layer():
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
    Y = np.eye(2)[[0, 1, 1, 0]]
    net = nn.MLP([2, 4, 2], hidden="tanh", out="softmax", seed=3)
    nn.train(net, X, Y, epochs=2000, batch=4, eta=0.05)
    assert np.argmax(net.predict(X), 1).tolist() == [0, 1, 1, 0]
    lin = nn.MLP([2, 2], out="softmax", seed=3)             # no hidden layer
    nn.train(lin, X, Y, epochs=2000, batch=4, eta=0.05)
    assert np.mean(np.argmax(lin.predict(X), 1) == [0, 1, 1, 0]) <= 0.75


def test_wider_hidden_layer_approximates_better():
    x = np.linspace(-np.pi, np.pi, 200)[:, None]
    y = np.sin(2 * x) + 0.3 * x
    losses = []
    for h in [2, 32]:
        net = nn.MLP([1, h, 1], hidden="tanh", seed=0)
        nn.train(net, x, y, epochs=1500, batch=50, eta=1e-2)
        losses.append(net.loss(x, y))
    assert losses[1] < 0.05 * losses[0] and losses[1] < 2e-3


def test_early_stopping_restores_best_validation_loss():
    rng = np.random.default_rng(0)
    x = rng.uniform(-1, 1, (30, 1))
    y = np.sin(3 * x) + 0.3 * rng.normal(size=x.shape)
    xv = rng.uniform(-1, 1, (200, 1))
    yv = np.sin(3 * xv) + 0.3 * rng.normal(size=xv.shape)
    net = nn.MLP([1, 64, 64, 1], hidden="tanh", seed=1)
    hist = nn.train(net, x, y, epochs=400, batch=30, eta=1e-2, X_val=xv, Y_val=yv)
    assert net.loss(xv, yv) == pytest.approx(min(hist))
    assert hist[-1] > min(hist)          # the validation curve turned up: overfitting
