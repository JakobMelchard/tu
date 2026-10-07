"""Deep learning theory: universal approximation, implicit bias of GD, double descent.

Note 10 (deep learning theory), section Results:
- Theorem 10.1 (universal approximation): 1-hidden-layer MLP with hand-written
  backprop and Adam (`MLP`, `universal_approximation_demo`); the explicit
  3-ReLU hat function of the constructive proof (`hat_network`).
- Theorem 10.6: GD from 0 on least squares converges to the min-norm
  interpolator Phi^+ y (`gd_least_squares`, `min_norm_least_squares`).
- Theorem 10.8 (Hastie et al. 2022, Thm 1): asymptotic risk of min-norm least
  squares, sigma^2 gamma/(1-gamma) for gamma < 1 and r^2(1-1/gamma) + sigma^2/(gamma-1)
  for gamma > 1 (`ridgeless_risk`), reproduced by `min_norm_risk_simulation`;
  finite-n check below the threshold: sigma^2 p/(n-p-1) exactly (Gaussian design).
- Double descent on random ReLU features (`double_descent_curve`).

Run `python deep_theory.py [--png]`.
"""
from __future__ import annotations

import numpy as np


class MLP:
    """One hidden layer, f(x) = sum_j v_j act(w_j x + b_j) + c, trained with Adam on MSE."""

    def __init__(self, hidden: int, act: str = "relu", rng=None):
        rng = np.random.default_rng(0) if rng is None else rng
        self.act = act
        self.W = rng.normal(size=hidden) * 3.0
        self.b = rng.uniform(-3.0, 3.0, size=hidden)
        self.V = rng.normal(size=hidden) / np.sqrt(hidden)
        self.c = 0.0

    def _act(self, z):
        return np.maximum(z, 0.0) if self.act == "relu" else np.tanh(z)

    def _dact(self, z):
        return (z > 0).astype(float) if self.act == "relu" else 1 - np.tanh(z) ** 2

    def forward(self, x):
        z = np.outer(x, self.W) + self.b            # (n, hidden)
        return self._act(z) @ self.V + self.c

    def gradients(self, x, y):
        z = np.outer(x, self.W) + self.b
        h = self._act(z)
        r = (h @ self.V + self.c - y) * 2 / len(x)  # dL/df
        gV = h.T @ r
        gc = r.sum()
        back = (r[:, None] * self.V[None, :]) * self._dact(z)
        gW = (back * x[:, None]).sum(0)
        gb = back.sum(0)
        return gW, gb, gV, gc

    def fit(self, x, y, steps=3000, lr=1e-2):
        params = [self.W, self.b, self.V, np.array([self.c])]
        m = [np.zeros_like(p) for p in params]; v = [np.zeros_like(p) for p in params]
        b1, b2, eps = 0.9, 0.999, 1e-8
        for t in range(1, steps + 1):
            grads = list(self.gradients(x, y))
            grads[3] = np.array([grads[3]])
            for i, (p, g) in enumerate(zip(params, grads)):
                m[i] = b1 * m[i] + (1 - b1) * g
                v[i] = b2 * v[i] + (1 - b2) * g * g
                p -= lr * (m[i] / (1 - b1**t)) / (np.sqrt(v[i] / (1 - b2**t)) + eps)
            self.c = float(params[3][0])
        return self

    def mse(self, x, y):
        return float(np.mean((self.forward(x) - y) ** 2))


def target(x):
    return np.sin(2 * np.pi * x) + np.exp(-100 * (x - 0.7) ** 2)


def hat_network(a: float, b: float, c: float):
    """Explicit 3-ReLU net computing the hat function rising from a to b and falling to c."""
    s1, s2 = 1 / (b - a), 1 / (c - b)
    W = np.array([1.0, 1.0, 1.0]); bias = np.array([-a, -b, -c])
    V = np.array([s1, -(s1 + s2), s2])
    return lambda x: np.maximum(np.outer(x, W) + bias, 0) @ V


def universal_approximation_demo(widths=(2, 4, 8, 32, 128), steps=3000, seed=0):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, 200); y = target(x)
    out = {}
    for h in widths:
        net = MLP(h, "relu", rng).fit(x, y, steps=steps, lr=1e-2)
        out[h] = net.mse(x, y)
    return out


def random_relu_features(X: np.ndarray, W: np.ndarray) -> np.ndarray:
    """phi(x) = relu(W x) / sqrt(m): random-features model with m = W.shape[0]."""
    return np.maximum(X @ W.T, 0.0) / np.sqrt(W.shape[0])


def min_norm_least_squares(Phi: np.ndarray, y: np.ndarray, lam: float = 0.0) -> np.ndarray:
    if lam > 0:
        return np.linalg.solve(Phi.T @ Phi + lam * np.eye(Phi.shape[1]), Phi.T @ y)
    return np.linalg.pinv(Phi) @ y


def gd_least_squares(Phi: np.ndarray, y: np.ndarray, steps: int, lr: float | None = None) -> np.ndarray:
    """Theorem 10.6: w_{t+1} = w_t - lr Phi^T (Phi w_t - y) from w_0 = 0, lr < 2/||Phi||_2^2."""
    lr = 1.0 / np.linalg.norm(Phi, 2) ** 2 if lr is None else lr
    w = np.zeros(Phi.shape[1])
    for _ in range(steps):
        w -= lr * Phi.T @ (Phi @ w - y)
    return w


def ridgeless_risk(gamma: float, r2: float, sigma2: float) -> float:
    """Theorem 10.8, isotropic well-specified model, gamma = p/n != 1."""
    if gamma < 1:
        return sigma2 * gamma / (1 - gamma)
    return r2 * (1 - 1 / gamma) + sigma2 / (gamma - 1)


def min_norm_risk_simulation(n: int, p: int, r2: float, sigma2: float, trials: int,
                             rng: np.random.Generator) -> float:
    """E||beta_hat - beta||^2 of pinv(X) y, x ~ N(0, I_p), ||beta||^2 = r2 (= excess risk)."""
    beta = rng.normal(size=p)
    beta *= np.sqrt(r2) / np.linalg.norm(beta)
    out = []
    for _ in range(trials):
        X = rng.normal(size=(n, p))
        y = X @ beta + np.sqrt(sigma2) * rng.normal(size=n)
        out.append(np.sum((np.linalg.pinv(X) @ y - beta) ** 2))
    return float(np.mean(out))


def double_descent_curve(n_train=40, d=5, widths=(5, 10, 20, 30, 38, 40, 42, 50, 80, 200, 800),
                         noise=0.1, n_test=1000, trials=5, seed=0, lam=0.0):
    """Test MSE of ridgeless least squares on m random ReLU features vs m.
    The teacher is a smooth function of a random projection; the curve peaks at m ~ n_train.
    With larger `noise` the second descent stays above the first minimum (interpolating
    noisy labels is only benign when the noise is small relative to the signal)."""
    rng = np.random.default_rng(seed)
    beta = rng.normal(size=d)
    f = lambda X: np.tanh(X @ beta)
    res = {}
    for m in widths:
        errs = []
        for _ in range(trials):
            Xtr = rng.normal(size=(n_train, d)); ytr = f(Xtr) + noise * rng.normal(size=n_train)
            Xte = rng.normal(size=(n_test, d)); yte = f(Xte)
            W = rng.normal(size=(m, d))
            w = min_norm_least_squares(random_relu_features(Xtr, W), ytr, lam)
            errs.append(np.mean((random_relu_features(Xte, W) @ w - yte) ** 2))
        res[m] = float(np.mean(errs))
    return res


if __name__ == "__main__":
    import sys
    hat = hat_network(0.2, 0.5, 0.8)
    print("hat network at x=0.2,0.35,0.5,0.65,0.8:", np.round(hat(np.array([0.2, 0.35, 0.5, 0.65, 0.8])), 3))
    print("\nUniversal approximation (train MSE after 3000 Adam steps):")
    for h, e in universal_approximation_demo().items():
        print(f"  width {h:4d}: MSE {e:.5f}")
    print("\nDouble descent (n_train=40, ridgeless random ReLU features):")
    curve = double_descent_curve()
    for m, e in curve.items():
        print(f"  m={m:4d}: test MSE {e:.3f}" + ("  <- interpolation threshold" if m == 40 else ""))
    rng = np.random.default_rng(1)
    n, r2, s2 = 100, 4.0, 1.0
    print(f"\nTheorem 10.8, min-norm least squares, n={n}, r^2={r2}, sigma^2={s2}, 40 resamples:")
    for gamma in (0.25, 0.5, 0.8, 1.25, 2.0, 4.0):
        p = int(gamma * n)
        extra = f"  finite-n sigma^2 p/(n-p-1) = {s2 * p / (n - p - 1):.3f}" if gamma < 1 else ""
        print(f"  gamma={gamma:4.2f}: MC {min_norm_risk_simulation(n, p, r2, s2, 40, rng):6.3f}"
              f"  asymptotic {ridgeless_risk(gamma, r2, s2):6.3f}{extra}")
    if "--png" in sys.argv:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.semilogx(list(curve), list(curve.values()), "o-"); plt.axvline(40, ls="--")
        plt.xlabel("number of random features m"); plt.ylabel("test MSE"); plt.title("double descent")
        plt.savefig("double_descent.png", dpi=120); print("saved double_descent.png")
