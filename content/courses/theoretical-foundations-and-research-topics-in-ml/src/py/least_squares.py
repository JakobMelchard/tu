"""Least squares regression: closed form, geometry, ridge, bias-variance, KRR.

Note 07 (least-squares regression), section Results:
- Theorems 7.1, 7.2: normal equations, hat matrix H is the projector onto col(X), tr H = d.
- Theorem 7.3(c): fixed design, E||X w_hat - X w*||^2 = sigma^2 d (`in_sample_excess_risk`);
  random Gaussian design, E||w_hat - w*||^2 = sigma^2 d / (n - d - 1) (`random_design_excess_risk`).
- Theorem 7.5: ridge, SVD shrinkage, effective degrees of freedom df(lambda).
- Theorem 7.6: bias-variance decomposition (`bias_variance_simulation`).
- Theorems 7.7, 7.8: push-through identity, kernel ridge regression (`ridge_dual`, `kernel_ridge`).
- Theorem 7.9(c): ridge fixed-design risk, exact value and the bound
  lambda ||w*||^2 / (4n) + sigma^2 df(lambda) / n (`ridge_risk_exact`, `ridge_risk_bound`).

Run `python least_squares.py [--png]`.
"""
from __future__ import annotations

import numpy as np


def ols(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Normal equations (X^T X) w = X^T y; pseudo-inverse gives the min-norm solution when singular."""
    return np.linalg.pinv(X.T @ X) @ X.T @ y


def hat_matrix(X: np.ndarray) -> np.ndarray:
    """H = X (X^T X)^+ X^T, the orthogonal projector onto col(X)."""
    return X @ np.linalg.pinv(X.T @ X) @ X.T


def ridge(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """argmin ||Xw - y||^2 + lam ||w||^2 = (X^T X + lam I)^{-1} X^T y."""
    p = X.shape[1]
    return np.linalg.solve(X.T @ X + lam * np.eye(p), X.T @ y)


def ridge_dual(X: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """Same solution via X^T (X X^T + lam I)^{-1} y (n x n system): the kernel form."""
    n = X.shape[0]
    return X.T @ np.linalg.solve(X @ X.T + lam * np.eye(n), y)


def effective_dof(X: np.ndarray, lam: float) -> float:
    """tr(X (X^T X + lam I)^{-1} X^T) = sum_j s_j^2 / (s_j^2 + lam)."""
    s = np.linalg.svd(X, compute_uv=False)
    return float(np.sum(s**2 / (s**2 + lam)))


def kernel_ridge(K: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """alpha = (K + lam I)^{-1} y; predictor f(x) = sum_i alpha_i k(x_i, x)."""
    return np.linalg.solve(K + lam * np.eye(K.shape[0]), y)


def krr_predict(alpha: np.ndarray, K_test_train: np.ndarray) -> np.ndarray:
    return K_test_train @ alpha


def poly_design(x: np.ndarray, d: int) -> np.ndarray:
    return np.vander(np.asarray(x, float).ravel(), d + 1, increasing=True)


def bias_variance_simulation(f, n: int, sigma: float, degrees, trials: int,
                             rng: np.random.Generator, x_grid: np.ndarray | None = None,
                             lam: float = 0.0):
    """Monte-Carlo bias-variance decomposition of polynomial (ridge) regression.

    For each degree returns (bias^2, variance, noise, total) averaged over x_grid,
    where total = E_S,eps (f_S(x) - y)^2 = sigma^2 + bias^2 + variance.
    """
    if x_grid is None:
        x_grid = np.linspace(-1, 1, 101)
    out = {}
    for d in degrees:
        preds = np.empty((trials, len(x_grid)))
        Pg = poly_design(x_grid, d)
        for t in range(trials):
            x = rng.uniform(-1, 1, n)
            y = f(x) + sigma * rng.normal(size=n)
            P = poly_design(x, d)
            w = ridge(P, y, lam) if lam > 0 else ols(P, y)
            preds[t] = Pg @ w
        mean_pred = preds.mean(axis=0)
        bias2 = float(np.mean((mean_pred - f(x_grid)) ** 2))
        var = float(np.mean(preds.var(axis=0)))
        out[d] = (bias2, var, sigma**2, bias2 + var + sigma**2)
    return out


def in_sample_excess_risk(X: np.ndarray, w_star: np.ndarray, sigma: float, trials: int,
                          rng: np.random.Generator) -> float:
    """E ||X w_hat - X w*||^2 for fixed design; theory says sigma^2 * rank(X)."""
    vals = []
    for _ in range(trials):
        y = X @ w_star + sigma * rng.normal(size=X.shape[0])
        vals.append(np.sum((X @ ols(X, y) - X @ w_star) ** 2))
    return float(np.mean(vals))


def random_design_excess_risk(n: int, d: int, sigma: float, trials: int,
                              rng: np.random.Generator) -> float:
    """E||w_hat - w*||^2 with rows x_i ~ N(0, I_d): the out-of-sample excess risk.

    Closed form sigma^2 E tr (X^T X)^{-1} = sigma^2 d / (n - d - 1) (inverse-Wishart mean).
    """
    w_star = np.ones(d)
    vals = []
    for _ in range(trials):
        X = rng.normal(size=(n, d))
        y = X @ w_star + sigma * rng.normal(size=n)
        vals.append(np.sum((ols(X, y) - w_star) ** 2))
    return float(np.mean(vals))


def ridge_risk_exact(X: np.ndarray, w_star: np.ndarray, sigma: float, lam: float) -> float:
    """Theorem 7.9(c): (1/n)[||(I - H_lam) X w*||^2 + sigma^2 tr(H_lam^2)]."""
    n, d = X.shape
    H = X @ np.linalg.solve(X.T @ X + lam * np.eye(d), X.T)
    return float((np.sum(((np.eye(n) - H) @ X @ w_star) ** 2) + sigma**2 * np.trace(H @ H)) / n)


def ridge_risk_bound(X: np.ndarray, w_star: np.ndarray, sigma: float, lam: float) -> float:
    """Theorem 7.9(c) upper bound: lambda ||w*||^2 / (4n) + sigma^2 df(lambda) / n."""
    n = X.shape[0]
    return float(lam * np.sum(w_star**2) / (4 * n) + sigma**2 * effective_dof(X, lam) / n)


def ridge_risk_mc(X: np.ndarray, w_star: np.ndarray, sigma: float, lam: float, trials: int,
                  rng: np.random.Generator) -> float:
    """Monte-Carlo (1/n) E||X w_hat_lam - X w*||^2 over fresh noise."""
    vals = [np.mean((X @ ridge(X, X @ w_star + sigma * rng.normal(size=X.shape[0]), lam)
                     - X @ w_star) ** 2) for _ in range(trials)]
    return float(np.mean(vals))


if __name__ == "__main__":
    import sys
    rng = np.random.default_rng(0)
    X = np.array([[1, 0.0], [1, 1.0], [1, 2.0]])
    y = np.array([1.0, 2.0, 2.0])
    w = ols(X, y)
    print("3-point OLS w =", w, " residual orth. to columns:", np.abs(X.T @ (y - X @ w)).max() < 1e-12)
    for lam in (0.0, 1.0, 10.0):
        wl = ridge(X, y, lam) if lam > 0 else w
        print(f"  ridge lambda={lam:4.1f}: w={wl}, dof={effective_dof(X, lam):.3f}")
    f = lambda x: np.sin(2 * np.pi * x)
    print("\nBias-variance, n=30, sigma=0.3 (bias^2, var, noise, total):")
    bv = bias_variance_simulation(f, 30, 0.3, [1, 3, 5, 7, 9], 300, rng)
    for d, (b, v, s, tot) in bv.items():
        print(f"  degree {d:2d}: {b:.4f} {v:.4f} {s:.4f} {tot:.4f}")
    if "--png" in sys.argv:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ds = list(bv)
        plt.plot(ds, [bv[d][0] for d in ds], "o-", label="bias$^2$")
        plt.plot(ds, [bv[d][1] for d in ds], "s-", label="variance")
        plt.plot(ds, [bv[d][3] for d in ds], "k--", label="total")
        plt.yscale("log"); plt.xlabel("degree"); plt.legend(); plt.title("bias-variance, n=30")
        plt.savefig("bias_variance.png", dpi=120); print("saved bias_variance.png")
    Xf = rng.normal(size=(50, 4))
    print(f"\nTheorem 7.3(c), fixed design excess risk: MC {in_sample_excess_risk(Xf, np.ones(4), 1.0, 2000, rng):.3f}"
          f"  theory sigma^2 d = {4.0}")
    print(f"Random Gaussian design n=50, d=4: MC {random_design_excess_risk(50, 4, 1.0, 4000, rng):.4f}"
          f"  closed form sigma^2 d/(n-d-1) = {4 / 45:.4f}")
    print("\nTheorem 7.9(c), ridge, fixed design n=50, d=4, sigma=1, 2000 noise draws:")
    ws = np.array([2.0, -1.0, 0.5, 0.0])
    for lam in (0.1, 5.0, 50.0):
        print(f"  lambda={lam:5.1f}: MC {ridge_risk_mc(Xf, ws, 1.0, lam, 2000, rng):.4f}"
              f"  exact {ridge_risk_exact(Xf, ws, 1.0, lam):.4f}  bound {ridge_risk_bound(Xf, ws, 1.0, lam):.4f}")
    x = rng.uniform(-1, 1, 40); yk = f(x) + 0.2 * rng.normal(size=40)
    K = np.exp(-10 * (x[:, None] - x[None, :]) ** 2)
    alpha = kernel_ridge(K, yk, 1e-2)
    xt = np.linspace(-1, 1, 200)
    Kt = np.exp(-10 * (xt[:, None] - x[None, :]) ** 2)
    print(f"KRR (RBF gamma=10, lambda=0.01) test MSE {np.mean((krr_predict(alpha, Kt) - f(xt))**2):.4f}")
