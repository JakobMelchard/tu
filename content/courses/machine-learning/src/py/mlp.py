"""Perceptron (Rosenblatt rule) and a multilayer perceptron from scratch:
forward pass, manual backpropagation, ReLU/tanh/sigmoid, softmax +
cross-entropy or linear + MSE output, SGD with momentum or Adam, L2 weight
decay, dropout, early stopping, He/Xavier initialisation.

Serves note 11 (neural networks) and the regularisation part of note 13.
Tests (test_mlp.py): numerical gradient check to 1e-6, accuracy against
sklearn.neural_network.  Run `python mlp.py` for the moons demo of note 11.
"""
import numpy as np
from model_selection import BaseEstimator


class Perceptron(BaseEstimator):
    """Rosenblatt rule: on a mistake w <- w + eta y x, b <- b + eta y. Converges iff linearly separable."""

    def __init__(self, eta=1.0, n_epochs=100):
        self.eta, self.n_epochs = eta, n_epochs

    def fit(self, X, y):
        X = np.asarray(X, float); self.classes_ = np.unique(y)
        y = np.where(np.asarray(y) == self.classes_[1], 1.0, -1.0)
        self.coef_, self.intercept_, self.errors_ = np.zeros(X.shape[1]), 0.0, []
        for _ in range(self.n_epochs):
            errs = 0
            for xi, yi in zip(X, y):
                if yi * (xi @ self.coef_ + self.intercept_) <= 0:
                    self.coef_ += self.eta * yi * xi; self.intercept_ += self.eta * yi; errs += 1
            self.errors_.append(errs)
            if errs == 0:
                break
        return self

    def predict(self, X):
        return np.where(np.asarray(X, float) @ self.coef_ + self.intercept_ > 0, self.classes_[1], self.classes_[0])


ACTS = {
    "relu": (lambda z: np.maximum(z, 0), lambda z, a: (z > 0).astype(float)),
    "tanh": (np.tanh, lambda z, a: 1 - a ** 2),
    "sigmoid": (lambda z: 1 / (1 + np.exp(-z)), lambda z, a: a * (1 - a)),
    "identity": (lambda z: z, lambda z, a: np.ones_like(z)),
}


def softmax(Z):
    Z = Z - Z.max(1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(1, keepdims=True)


class MLP(BaseEstimator):
    """hidden: tuple of layer widths. task: 'classification' (softmax/CE) or 'regression' (linear/MSE)."""

    def __init__(self, hidden=(32,), activation="relu", task="classification", lr=0.01, epochs=200,
                 batch_size=32, optimizer="adam", momentum=0.9, l2=0.0, dropout=0.0, early_stopping=False,
                 patience=10, rng=0):
        self.hidden, self.activation, self.task, self.lr, self.epochs = hidden, activation, task, lr, epochs
        self.batch_size, self.optimizer, self.momentum, self.l2, self.dropout = batch_size, optimizer, momentum, l2, dropout
        self.early_stopping, self.patience, self.rng = early_stopping, patience, rng

    # -------------------------------------------------------------- setup
    def _init(self, d_in, d_out):
        r = np.random.default_rng(self.rng)
        sizes = [d_in, *self.hidden, d_out]
        self.W_, self.b_ = [], []
        for a, b in zip(sizes[:-1], sizes[1:]):
            scale = np.sqrt(2 / a) if self.activation == "relu" else np.sqrt(1 / a)   # He / Xavier init
            self.W_.append(r.normal(0, scale, (a, b))); self.b_.append(np.zeros(b))
        self._m = [np.zeros_like(p) for p in self.W_ + self.b_]
        self._v = [np.zeros_like(p) for p in self.W_ + self.b_]
        self._t = 0

    # ------------------------------------------------------------ forward
    def _forward(self, X, train=False, rng=None):
        act, _ = ACTS[self.activation]
        A, cache = X, []
        for l, (W, b) in enumerate(zip(self.W_, self.b_)):
            Z = A @ W + b
            if l < len(self.W_) - 1:
                A_new = act(Z)
                mask = None
                if train and self.dropout > 0:                     # inverted dropout
                    mask = (rng.random(A_new.shape) >= self.dropout) / (1 - self.dropout)
                    A_new = A_new * mask
            else:
                A_new = softmax(Z) if self.task == "classification" else Z
                mask = None
            cache.append((A, Z, A_new, mask))
            A = A_new
        return A, cache

    # ----------------------------------------------------------- backward
    def _backward(self, cache, Y):
        """dL/dZ_out = (P - Y)/n for softmax+CE and (F - y)/n for linear+MSE (up to constant);
        then dZ_{l} = (dZ_{l+1} W_{l+1}^T) * act'(Z_l), dW_l = A_{l-1}^T dZ_l, db_l = sum dZ_l."""
        _, dact = ACTS[self.activation]
        n = len(Y)
        gW, gb = [None] * len(self.W_), [None] * len(self.W_)
        dZ = (cache[-1][2] - Y) / n
        for l in range(len(self.W_) - 1, -1, -1):
            A_prev, Z, A, mask = cache[l]
            gW[l] = A_prev.T @ dZ + self.l2 * self.W_[l] / n
            gb[l] = dZ.sum(0)
            if l > 0:
                dA = dZ @ self.W_[l].T
                if cache[l - 1][3] is not None:
                    dA = dA * cache[l - 1][3]
                dZ = dA * dact(cache[l - 1][1], cache[l - 1][2])
        return gW, gb

    def _step(self, grads):
        params = self.W_ + self.b_
        self._t += 1
        for i, (p, g) in enumerate(zip(params, grads)):
            if self.optimizer == "adam":
                b1, b2, eps = 0.9, 0.999, 1e-8
                self._m[i] = b1 * self._m[i] + (1 - b1) * g
                self._v[i] = b2 * self._v[i] + (1 - b2) * g ** 2
                mhat, vhat = self._m[i] / (1 - b1 ** self._t), self._v[i] / (1 - b2 ** self._t)
                p -= self.lr * mhat / (np.sqrt(vhat) + eps)
            else:                                                       # SGD with momentum
                self._m[i] = self.momentum * self._m[i] - self.lr * g
                p += self._m[i]

    def loss(self, X, Y):
        """Mean cross-entropy (or half MSE) plus the L2 penalty l2/(2n) sum ||W||^2 that _backward differentiates."""
        P, _ = self._forward(X)
        data = -np.mean(np.sum(Y * np.log(P + 1e-12), 1)) if self.task == "classification" else 0.5 * np.mean((P - Y) ** 2)
        return float(data + self.l2 / (2 * len(X)) * sum(np.sum(W ** 2) for W in self.W_))

    # ---------------------------------------------------------------- fit
    def fit(self, X, y, X_val=None, y_val=None):
        X, y = np.asarray(X, float), np.asarray(y)
        if self.task == "classification":
            self.classes_, yi = np.unique(y, return_inverse=True)
            Y = np.eye(len(self.classes_))[yi]
            Yv = np.eye(len(self.classes_))[np.searchsorted(self.classes_, y_val)] if y_val is not None else None
        else:
            Y = y.reshape(len(y), -1).astype(float)
            Yv = np.asarray(y_val, float).reshape(len(y_val), -1) if y_val is not None else None
        self._init(X.shape[1], Y.shape[1])
        r = np.random.default_rng(self.rng)
        self.history_, best, wait = [], (np.inf, None), 0
        for _ in range(self.epochs):
            for idx in np.array_split(r.permutation(len(X)), max(1, len(X) // self.batch_size)):
                _, cache = self._forward(X[idx], train=True, rng=r)
                gW, gb = self._backward(cache, Y[idx])
                self._step(gW + gb)
            tr = self.loss(X, Y)
            va = self.loss(X_val, Yv) if Yv is not None else None
            self.history_.append((tr, va))
            if self.early_stopping and va is not None:
                if va < best[0] - 1e-6:
                    best, wait = (va, ([W.copy() for W in self.W_], [b.copy() for b in self.b_])), 0
                else:
                    wait += 1
                    if wait >= self.patience:
                        self.W_, self.b_ = best[1]
                        break
        return self

    def predict_proba(self, X):
        return self._forward(np.asarray(X, float))[0]

    def predict(self, X):
        out = self.predict_proba(X)
        return self.classes_[np.argmax(out, 1)] if self.task == "classification" else out.squeeze()


def numerical_gradient(mlp, X, Y, eps=1e-5):
    """Finite-difference gradient of the loss for every parameter (gradient checking)."""
    grads = []
    for p in mlp.W_ + mlp.b_:
        g = np.zeros_like(p)
        for i in np.ndindex(p.shape):
            old = p[i]
            p[i] = old + eps; lp = mlp.loss(X, Y)
            p[i] = old - eps; lm = mlp.loss(X, Y)
            p[i] = old
            g[i] = (lp - lm) / (2 * eps)
        grads.append(g)
    return grads


if __name__ == "__main__":
    from sklearn.datasets import make_moons, make_blobs
    from preprocessing import StandardScaler
    from model_selection import train_test_split
    from metrics import accuracy

    Xb, yb = make_blobs(100, centers=[[-3, -3], [3, 3]], random_state=0)      # linearly separable
    p = Perceptron().fit(Xb, yb)
    print("perceptron: converged after %d epochs, acc %.3f" % (len(p.errors_), accuracy(yb, p.predict(Xb))))
    X, y = make_moons(600, noise=0.25, random_state=0)
    X = StandardScaler().fit_transform(X)
    Xtr, Xte, ytr, yte = train_test_split(X, y, 0.3, stratify=True, rng=0)
    for opt, act in [("sgd", "tanh"), ("adam", "relu")]:
        m = MLP((32, 16), act, lr=0.05 if opt == "sgd" else 0.01, epochs=100, optimizer=opt).fit(Xtr, ytr)
        print(f"MLP {act}/{opt}: train {accuracy(ytr, m.predict(Xtr)):.3f} test {accuracy(yte, m.predict(Xte)):.3f} final loss {m.history_[-1][0]:.3f}")
    # early stopping monitors a validation split carved from the training data, never the test set
    Xfit, Xval, yfit, yval = train_test_split(Xtr, ytr, 0.25, stratify=True, rng=1)
    m = MLP((64, 64), "relu", epochs=300, dropout=0.2, l2=1e-3, early_stopping=True, patience=15).fit(Xfit, yfit, Xval, yval)
    print("with dropout+L2+early stopping: stopped after %d epochs, test acc %.3f" % (len(m.history_), accuracy(yte, m.predict(Xte))))
    xr = np.linspace(-3, 3, 200)[:, None]; yr = np.sin(2 * xr[:, 0]) + 0.1 * np.random.default_rng(0).normal(size=200)
    reg = MLP((32, 32), "tanh", task="regression", lr=0.01, epochs=300).fit(xr, yr)
    print("regression MSE %.4f" % np.mean((reg.predict(xr) - yr) ** 2))
