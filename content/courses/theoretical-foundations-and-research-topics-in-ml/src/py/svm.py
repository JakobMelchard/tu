"""Support vector machines: hard/soft margin dual via scipy SLSQP, kernelised.

Note 09 (SVM), section Results:
- Theorems 9.1, 9.4: hard- and soft-margin duals (`solve_dual`), Corollary 9.2
  (support vectors, b, margin 1/||w||), Corollary 9.5 (the three KKT regimes).
- Theorem 9.6: leave-one-out bound, LOO error <= N_SV / (n+1); only support
  vectors can be LOO mistakes, so `leave_one_out_error` refits only for them
  (and `only_sv=False` refits for every point, to check that claim).
- Theorem 9.9: perceptron makes at most (R/gamma)^2 mistakes (`perceptron`).

Cross-checked against sklearn.svm.SVC in test_svm.py. Small problems only
(n <= ~200): the dual has n variables. Run `python svm.py`.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

from kernels import linear_kernel, rbf_kernel


def solve_dual(K: np.ndarray, y: np.ndarray, C: float | None) -> np.ndarray:
    """max_alpha sum alpha_i - 1/2 sum_ij alpha_i alpha_j y_i y_j K_ij
    s.t. sum alpha_i y_i = 0, 0 <= alpha_i <= C (C=None: hard margin).
    Solved as a minimisation of the negative objective with SLSQP."""
    n = len(y)
    Q = (y[:, None] * y[None, :]) * K
    Q = 0.5 * (Q + Q.T) + 1e-10 * np.eye(n)   # tiny ridge keeps SLSQP stable

    def obj(a):
        return 0.5 * a @ Q @ a - a.sum()

    def grad(a):
        return Q @ a - 1.0

    cons = [{"type": "eq", "fun": lambda a: a @ y, "jac": lambda a: y}]
    bounds = [(0.0, C)] * n
    res = minimize(obj, np.zeros(n), jac=grad, bounds=bounds, constraints=cons,
                   method="SLSQP", options={"maxiter": 2000, "ftol": 1e-12})
    return np.clip(res.x, 0.0, np.inf if C is None else C)


class SVM:
    """Kernel SVM. kernel: callable (X, Y) -> Gram matrix. C=None gives the hard-margin machine."""

    def __init__(self, C: float | None = 1.0, kernel=linear_kernel, tol: float = 1e-6):
        self.C, self.kernel, self.tol = C, kernel, tol

    def fit(self, X: np.ndarray, y: np.ndarray):
        X = np.asarray(X, float); y = np.asarray(y, float)
        K = self.kernel(X, X)
        alpha = solve_dual(K, y, self.C)
        sv = alpha > self.tol
        self.X_, self.y_, self.alpha_ = X[sv], y[sv], alpha[sv]
        self.support_ = np.flatnonzero(sv)
        # b from support vectors strictly inside the box (on the margin): y_i (w.x_i + b) = 1
        free = self.alpha_ < (np.inf if self.C is None else self.C - self.tol)
        idx = free if free.any() else np.ones_like(free)
        Ks = self.kernel(self.X_[idx], self.X_)
        self.b_ = float(np.mean(self.y_[idx] - Ks @ (self.alpha_ * self.y_)))
        return self

    def decision_function(self, X: np.ndarray) -> np.ndarray:
        return self.kernel(np.asarray(X, float), self.X_) @ (self.alpha_ * self.y_) + self.b_

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.where(self.decision_function(X) >= 0, 1, -1)

    def w(self) -> np.ndarray:
        """Primal weight vector (linear kernel only): w = sum alpha_i y_i x_i."""
        return self.X_.T @ (self.alpha_ * self.y_)

    def margin(self) -> float:
        """Geometric margin 1/||w||, with ||w||^2 = sum_ij alpha_i alpha_j y_i y_j k(x_i,x_j)."""
        K = self.kernel(self.X_, self.X_)
        v = self.alpha_ * self.y_
        return float(1.0 / np.sqrt(v @ K @ v))


def make_blobs(n: int, sep: float, rng: np.random.Generator):
    X = rng.normal(size=(n, 2))
    y = np.where(X[:, 0] + X[:, 1] > 0, 1, -1)
    X += sep * y[:, None] / np.sqrt(2)      # push classes apart along the normal
    return X, y


def leave_one_out_error(X: np.ndarray, y: np.ndarray, C: float | None = None,
                        only_sv: bool = True):
    """(number of leave-one-out mistakes, N_SV of the full fit).

    Removing a non-support vector leaves the solution unchanged (its alpha is 0),
    so it is classified correctly; with only_sv=True only the SVs are refitted.
    """
    full = SVM(C=C).fit(X, y)
    idx = full.support_ if only_sv else range(len(y))
    errors = 0
    for i in idx:
        keep = np.arange(len(y)) != i
        m = SVM(C=C).fit(X[keep], y[keep])
        errors += int(m.predict(X[i:i + 1])[0] != y[i])
    return errors, len(full.support_)


def perceptron(X: np.ndarray, y: np.ndarray, max_epochs: int = 1000):
    """Homogeneous perceptron w <- w + y_i x_i on each mistake, from w = 0 (Theorem 9.9).

    Cycles through the data until an epoch has no mistakes. Returns (w, mistakes).
    """
    w = np.zeros(X.shape[1])
    mistakes = 0
    for _ in range(max_epochs):
        clean = True
        for xi, yi in zip(X, y):
            if yi * (w @ xi) <= 0:
                w += yi * xi
                mistakes += 1
                clean = False
        if clean:
            break
    return w, mistakes


def make_margin_data(n: int, gamma: float, rng: np.random.Generator):
    """Points in the unit disk with |<w*, x>| >= gamma, w* = (1,1)/sqrt(2), y = sign(<w*,x>)."""
    w_star = np.array([1.0, 1.0]) / np.sqrt(2)
    pts = []
    while len(pts) < n:
        x = rng.uniform(-1, 1, 2)
        if x @ x <= 1 and abs(x @ w_star) >= gamma:
            pts.append(x)
    X = np.array(pts)
    return X, np.where(X @ w_star > 0, 1.0, -1.0), w_star


def hard_margin_demo():
    X = np.array([[1.0, 1.0], [2.0, 2.0], [-1.0, -1.0], [-2.0, -2.0]])
    y = np.array([1, 1, -1, -1])
    m = SVM(C=None).fit(X, y)
    print("hard margin on 4 points: w =", np.round(m.w(), 4), " b =", round(m.b_, 4),
          " margin =", round(m.margin(), 4), " SVs =", m.support_.tolist())
    print("  (expected w = (1/2, 1/2), b = 0, margin = sqrt(2), SVs = the two inner points)")
    return m


if __name__ == "__main__":
    hard_margin_demo()
    rng = np.random.default_rng(0)
    X, y = make_blobs(80, 1.0, rng)
    for C in (0.1, 1.0, 100.0):
        m = SVM(C=C).fit(X, y)
        print(f"soft margin C={C:6.1f}: #SV={len(m.support_):3d}  train err={np.mean(m.predict(X) != y):.3f}"
              f"  margin={m.margin():.3f}")
    t = rng.uniform(0, 2 * np.pi, 100); r = np.where(rng.uniform(size=100) < 0.5, 1.0, 2.5)
    Xc = np.stack([r * np.cos(t), r * np.sin(t)], 1) + 0.1 * rng.normal(size=(100, 2))
    yc = np.where(r > 2, 1, -1)
    m = SVM(C=10.0, kernel=lambda A, B: rbf_kernel(A, B, 1.0)).fit(Xc, yc)
    print(f"RBF SVM on concentric circles: train err={np.mean(m.predict(Xc) != yc):.3f}, #SV={len(m.support_)}")
    print("\nTheorem 9.6, hard margin, blobs with separation 0.05, n+1 = 31 points, 40 resamples:")
    loo, nsv = zip(*(leave_one_out_error(*make_blobs(31, 0.05, rng)) for _ in range(40)))
    print(f"  mean LOO error {np.mean(loo) / 31:.4f} <= mean N_SV/(n+1) {np.mean(nsv) / 31:.4f};"
          f" per sample LOO <= N_SV in {sum(a <= b for a, b in zip(loo, nsv))}/40")
    print("\nTheorem 9.9, perceptron on the unit disk, 200 shuffles per gamma:")
    for g in (0.2, 0.1, 0.05):
        X, y, w_star = make_margin_data(200, g, rng)
        gam, R = np.min(y * (X @ w_star)), np.max(np.linalg.norm(X, axis=1))
        ms = [perceptron(X[p], y[p])[1] for p in (rng.permutation(200) for _ in range(200))]
        print(f"  gamma>={g:4.2f}: max mistakes {max(ms):4d}  mean {np.mean(ms):6.1f}  bound (R/gamma)^2 = {(R / gam) ** 2:7.1f}")
