"""Logistic and softmax regression from scratch; kernel features; confusion metrics.

Note 04. Binary cross-entropy for y in {0, 1}, p = sigma(x^T w):
    E(w) = -sum_n [y_n log p_n + (1 - y_n) log(1 - p_n)] + (lam/2) ||w_{1:}||^2
    grad  = X^T (p - y) + lam w,     Hessian = X^T diag(p (1 - p)) X + lam 1  (PSD: convex)
Newton on E is iteratively reweighted least squares (IRLS) [S8 sec. 4.4.1].
Softmax: p_nc = exp(z_nc) / sum_c' exp(z_nc'), z = X W, grad = X^T (P - Y) + lam W [S6 sec. VII.D].
The bias is column 0 of X (`add_bias`) and is never penalised, matching sklearn.
"""
from __future__ import annotations

import numpy as np


def sigmoid(z):
    return 0.5 * (1.0 + np.tanh(0.5 * z))  # overflow-free form of 1/(1+e^{-z})


def add_bias(X):
    return np.hstack([np.ones((X.shape[0], 1)), X])


def bce(w, X, y, lam=0.0):
    z = X @ w
    # log(1 + e^z) - y z, computed stably
    return float(np.sum(np.logaddexp(0.0, z) - y * z) + 0.5 * lam * (w[1:] @ w[1:]))


def bce_grad(w, X, y, lam=0.0):
    g = X.T @ (sigmoid(X @ w) - y)
    g[1:] += lam * w[1:]
    return g


def logistic_newton(X, y, lam=0.0, max_iter=50, tol=1e-10):
    """IRLS with the bias in column 0 (unpenalised)."""
    w = np.zeros(X.shape[1])
    R = lam * np.eye(X.shape[1])
    R[0, 0] = 0.0
    for _ in range(max_iter):
        p = sigmoid(X @ w)
        H = X.T @ (X * (p * (1 - p))[:, None]) + R
        step = np.linalg.solve(H, bce_grad(w, X, y, lam))
        w -= step
        if np.max(np.abs(step)) < tol:
            break
    return w


def logistic_gd(X, y, lam=0.0, eta=0.1, epochs=2000):
    """Plain GD on the mean loss (step eta); slower than Newton but the course's first tool."""
    w = np.zeros(X.shape[1])
    N = X.shape[0]
    for _ in range(epochs):
        w -= eta * bce_grad(w, X, y, lam) / N
    return w


def softmax(Z):
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)


def one_hot(y, C):
    Y = np.zeros((y.size, C))
    Y[np.arange(y.size), y] = 1.0
    return Y


def softmax_loss_grad(W, X, Y, lam=0.0):
    P = softmax(X @ W)
    loss = -np.sum(Y * np.log(P + 1e-300)) + 0.5 * lam * np.sum(W[1:] ** 2)
    G = X.T @ (P - Y)
    G[1:] += lam * W[1:]
    return float(loss), G


def softmax_fit(X, y, C, lam=1e-3, eta=0.5, epochs=3000):
    """GD on the mean softmax cross-entropy."""
    W = np.zeros((X.shape[1], C))
    Y = one_hot(y, C)
    N = X.shape[0]
    for _ in range(epochs):
        _, G = softmax_loss_grad(W, X, Y, lam)
        W -= eta * G / N
    return W


def rbf_features(X, centres, gamma):
    """phi_j(x) = exp(-gamma ||x - c_j||^2): a finite kernel expansion (note 04, kernels)."""
    d2 = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(-1)
    return np.exp(-gamma * d2)


def confusion(y_true, y_pred):
    """[[TN, FP], [FN, TP]] and derived rates (label 1 = signal)."""
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    return dict(matrix=np.array([[tn, fp], [fn, tp]]), accuracy=(tp + tn) / y_true.size,
                sensitivity=tp / max(tp + fn, 1), specificity=tn / max(tn + fp, 1),
                precision=tp / max(tp + fp, 1))


def make_blobs2(n, rng, sep=2.0):
    """Two Gaussian classes in 2D, linearly separable up to overlap."""
    X0 = rng.normal(size=(n, 2)) + np.array([-sep / 2, 0])
    X1 = rng.normal(size=(n, 2)) + np.array([sep / 2, 0])
    return np.vstack([X0, X1]), np.r_[np.zeros(n), np.ones(n)]


def make_xor(n, rng, noise=0.3):
    """XOR / checkerboard: no linear boundary exists."""
    X = rng.uniform(-1, 1, size=(n, 2))
    y = ((X[:, 0] > 0) ^ (X[:, 1] > 0)).astype(float)
    return X + noise * 0.1 * rng.normal(size=X.shape), y


def _demo() -> None:
    rng = np.random.default_rng(4711)
    X, y = make_blobs2(500, rng)
    Xb = add_bias(X)
    w = logistic_newton(Xb, y)
    print(f"blobs: Newton w = {np.round(w, 4)}; boundary x1 = {-w[0] / w[1]:+.3f} "
          f"(Bayes boundary 0 for equal covariances)")
    print("  confusion:", confusion(y, (Xb @ w > 0).astype(int))["matrix"].tolist())
    Xx, yx = make_xor(1000, rng)
    wl = logistic_newton(add_bias(Xx), yx, lam=1e-3)
    acc_lin = np.mean((add_bias(Xx) @ wl > 0) == yx)
    C = rng.uniform(-1, 1, size=(40, 2))
    F = add_bias(rbf_features(Xx, C, gamma=4.0))
    wk = logistic_newton(F, yx, lam=1e-2)
    acc_k = np.mean((F @ wk > 0) == yx)
    print(f"XOR: linear logistic accuracy {acc_lin:.3f}, RBF-feature logistic {acc_k:.3f}")
    Xs = np.vstack([rng.normal(size=(200, 2)) + c for c in [(0, 3), (-3, -2), (3, -2)]])
    ys = np.repeat(np.arange(3), 200)
    W = softmax_fit(add_bias(Xs), ys, 3)
    print(f"3-class softmax training accuracy {np.mean(np.argmax(add_bias(Xs) @ W, 1) == ys):.3f}")


if __name__ == "__main__":
    _demo()
