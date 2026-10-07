"""Multilayer perceptron with hand-written backpropagation, gradient-checked.

Note 05. Layer l: z^l = a^{l-1} W^l + b^l, a^l = g(z^l) (row-vector convention, batch first).
Backward pass for the mean loss E [S6 sec. IX.C]:
    delta^L = dE/dz^L                     (softmax + CE: (P - Y)/N; identity + MSE: 2(A - Y)/N)
    dE/dW^l = a^{l-1 T} delta^l,  dE/db^l = sum_n delta^l_n
    delta^{l-1} = (delta^l W^{l T}) * g'(z^{l-1})
Initialisation: He (ReLU) or Glorot (tanh) scaled Gaussians. Optimisers: SGD, Adam [S26].
"""
from __future__ import annotations

import numpy as np

ACT = {
    "relu": (lambda z: np.maximum(z, 0.0), lambda z: (z > 0).astype(float)),
    "tanh": (np.tanh, lambda z: 1.0 - np.tanh(z) ** 2),
    "sigmoid": (lambda z: 0.5 * (1 + np.tanh(0.5 * z)),
                lambda z: 0.25 * (1 - np.tanh(0.5 * z) ** 2)),
    "identity": (lambda z: z, lambda z: np.ones_like(z)),
}


class MLP:
    def __init__(self, sizes, hidden="tanh", out="identity", seed=0):
        """sizes = [n_in, h_1, ..., n_out]; out in {'identity' (MSE), 'softmax' (CE)}."""
        rng = np.random.default_rng(seed)
        self.hidden, self.out = hidden, out
        gain = 2.0 if hidden == "relu" else 1.0
        self.W = [rng.normal(0, np.sqrt(gain / m), size=(m, n)) for m, n in zip(sizes, sizes[1:])]
        self.b = [np.zeros(n) for n in sizes[1:]]

    # parameters as one flat vector, for gradient checks
    def params(self):
        return [p for pair in zip(self.W, self.b) for p in pair]

    def forward(self, X):
        """Returns output and the cache (a^0..a^{L-1}, z^1..z^L)."""
        g = ACT[self.hidden][0]
        a, acts, zs = X, [X], []
        for l, (W, b) in enumerate(zip(self.W, self.b)):
            z = a @ W + b
            zs.append(z)
            if l < len(self.W) - 1:
                a = g(z)
                acts.append(a)
        zL = zs[-1]
        if self.out == "softmax":
            e = np.exp(zL - zL.max(axis=1, keepdims=True))
            return e / e.sum(axis=1, keepdims=True), (acts, zs)
        return zL, (acts, zs)

    def loss(self, X, Y):
        P, _ = self.forward(X)
        if self.out == "softmax":
            return float(-np.mean(np.sum(Y * np.log(P + 1e-300), axis=1)))
        return float(np.mean(np.sum((P - Y) ** 2, axis=1)))

    def backward(self, X, Y):
        """Gradients of the mean loss, same order as params()."""
        P, (acts, zs) = self.forward(X)
        N = X.shape[0]
        delta = (P - Y) / N if self.out == "softmax" else 2.0 * (P - Y) / N
        dg = ACT[self.hidden][1]
        grads = []
        for l in range(len(self.W) - 1, -1, -1):
            grads.append((acts[l].T @ delta, delta.sum(axis=0)))
            if l > 0:
                delta = (delta @ self.W[l].T) * dg(zs[l - 1])
        grads.reverse()
        return [g for pair in grads for g in pair]

    def predict(self, X):
        return self.forward(X)[0]


def numerical_grad(net: MLP, X, Y, h=1e-6):
    """Central differences over every parameter (float64)."""
    out = []
    for p in net.params():
        g = np.zeros_like(p)
        it = np.nditer(p, flags=["multi_index"])
        for _ in it:
            i = it.multi_index
            old = p[i]
            p[i] = old + h
            fp = net.loss(X, Y)
            p[i] = old - h
            fm = net.loss(X, Y)
            p[i] = old
            g[i] = (fp - fm) / (2 * h)
        out.append(g)
    return out


def grad_check(net, X, Y) -> float:
    """max over parameter arrays of ||g_bp - g_fd|| / (||g_bp|| + ||g_fd||).

    Norm-based: an element-wise ratio blows up on entries whose true gradient is ~0."""
    ga, gn = net.backward(X, Y), numerical_grad(net, X, Y)
    return max(float(np.linalg.norm(a - n) / max(np.linalg.norm(a) + np.linalg.norm(n), 1e-300))
               for a, n in zip(ga, gn))


def train(net: MLP, X, Y, epochs=200, batch=32, eta=1e-2, opt="adam", seed=0,
          X_val=None, Y_val=None, patience=None):
    """Minibatch training; optional early stopping on a validation set (restores best)."""
    rng = np.random.default_rng(seed)
    ps = net.params()
    m = [np.zeros_like(p) for p in ps]
    v = [np.zeros_like(p) for p in ps]
    t, hist, best, best_state, wait = 0, [], np.inf, None, 0
    for _ in range(epochs):
        perm = rng.permutation(X.shape[0])
        for j in range(0, X.shape[0], batch):
            idx = perm[j:j + batch]
            gs = net.backward(X[idx], Y[idx])
            t += 1
            for p, g, mi, vi in zip(ps, gs, m, v):
                if opt == "sgd":
                    p -= eta * g
                else:
                    mi *= 0.9
                    mi += 0.1 * g
                    vi *= 0.999
                    vi += 0.001 * g * g
                    p -= eta * (mi / (1 - 0.9**t)) / (np.sqrt(vi / (1 - 0.999**t)) + 1e-8)
        if X_val is not None:
            lv = net.loss(X_val, Y_val)
            hist.append(lv)
            if lv < best:
                best, wait = lv, 0
                best_state = [p.copy() for p in ps]
            else:
                wait += 1
                if patience is not None and wait >= patience:
                    break
    if best_state is not None:
        for p, q in zip(ps, best_state):
            p[...] = q
    return hist


def _demo() -> None:
    rng = np.random.default_rng(4711)
    X = rng.normal(size=(8, 3))
    Y = np.eye(2)[rng.integers(0, 2, 8)]
    for act in ["tanh", "sigmoid", "relu"]:
        net = MLP([3, 5, 4, 2], hidden=act, out="softmax", seed=1)
        print(f"gradient check ({act:7s}, softmax-CE): max rel err {grad_check(net, X, Y):.2e}")
    # XOR needs a hidden layer
    Xx = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
    yx = np.eye(2)[[0, 1, 1, 0]]
    net = MLP([2, 4, 2], hidden="tanh", out="softmax", seed=3)
    train(net, Xx, yx, epochs=2000, batch=4, eta=0.05)
    print("XOR predictions:", np.argmax(net.predict(Xx), 1).tolist(), "(target [0, 1, 1, 0])")
    # universal approximation in action: 1D regression with one hidden layer
    x = np.linspace(-np.pi, np.pi, 200)[:, None]
    y = np.sin(2 * x) + 0.3 * x
    for h in [2, 8, 32]:
        net = MLP([1, h, 1], hidden="tanh", seed=0)
        train(net, x, y, epochs=1500, batch=50, eta=1e-2)
        print(f"1-hidden-layer width {h:2d}: MSE on sin(2x)+0.3x = {net.loss(x, y):.2e}")


if __name__ == "__main__":
    _demo()
