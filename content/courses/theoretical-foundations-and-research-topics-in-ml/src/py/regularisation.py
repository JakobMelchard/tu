"""Regularisation, stability, validation; heuristic SRM over polynomial degrees.

Note 06 (regularisation and SRM), section Results:
- Definition 1 / bias-complexity trade-off: train/test U-curve over nested
  polynomial classes (`bias_complexity_curve`).
- Definition 4 (SRM rule) with a VC-style penalty whose constant is a free
  `scale`: a heuristic illustration only. The version with a proven bound
  (Theorems 6.1, 6.2) is srm.py.
- Definition 7: Tikhonov / RLM with squared loss (`tikhonov`) and with the
  logistic loss (`rlm_logistic`, Newton's method).
- Theorem 6.6: E[L_D(A(S)) - L_S(A(S))] = E[l(A(S^(i)), z_i) - l(A(S), z_i)].
- Theorem 6.7: RLM with a convex rho-Lipschitz loss has ||A(S^(i)) - A(S)|| <= 2rho/(lambda n)
  and replace-one loss change <= 2rho^2/(lambda n), for every S, z', i.
  `stability_experiment` measures both sides over many resamples.
- Theorem 6.9: validation bound sqrt(log(2k/delta)/(2 n_v)) (`validation_bound`,
  `validation_experiment`).

Run `python regularisation.py [--png]`.
"""
from __future__ import annotations

import math

import numpy as np


def poly_features(x: np.ndarray, d: int) -> np.ndarray:
    """Vandermonde matrix [1, x, ..., x^d] (Legendre-free; fine for x in [-1,1], d <= 15)."""
    x = np.asarray(x, float).ravel()
    return np.vander(x, d + 1, increasing=True)


def fit_least_squares(Phi: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(Phi, y, rcond=None)[0]


def tikhonov(Phi: np.ndarray, y: np.ndarray, lam: float) -> np.ndarray:
    """argmin_w (1/n)||Phi w - y||^2 + lam ||w||^2  =  (Phi^T Phi / n + lam I)^{-1} Phi^T y / n."""
    n, p = Phi.shape
    return np.linalg.solve(Phi.T @ Phi / n + lam * np.eye(p), Phi.T @ y / n)


def mse(Phi: np.ndarray, w: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((Phi @ w - y) ** 2))


def nested_poly_erm(x: np.ndarray, y: np.ndarray, degrees):
    """ERM in each class H_d = polynomials of degree <= d. Returns {d: (w, L_S)}."""
    return {d: (w := fit_least_squares(poly_features(x, d), y), mse(poly_features(x, d), w, y))
            for d in degrees}


def srm_penalty(d: int, n: int, delta: float, weight: float, scale: float = 1.0) -> float:
    """Complexity term of the SRM bound for class index d with weight w_d:

    eps_d(n, delta w_d) = scale * sqrt((d + 1 + log(1 / (delta w_d))) / n),
    the VC/pseudo-dimension form with VCdim(H_d) ~ d + 1 (constants absorbed in `scale`).
    """
    return scale * math.sqrt((d + 1 + math.log(1.0 / (delta * weight))) / n)


def srm_select(x: np.ndarray, y: np.ndarray, degrees, n: int | None = None,
               delta: float = 0.05, scale: float = 1.0):
    """SRM: minimise L_S(h_d) + eps_d over degrees with weights w_d = 6/(pi^2 (d+1)^2), sum <= 1."""
    n = len(x) if n is None else n
    fits = nested_poly_erm(x, y, degrees)
    scores = {}
    for d, (w, ls) in fits.items():
        wd = 6.0 / (math.pi**2 * (d + 1) ** 2)
        scores[d] = ls + srm_penalty(d, n, delta, wd, scale)
    d_star = min(scores, key=scores.get)
    return d_star, fits[d_star][0], scores


def validation_select(x_tr, y_tr, x_val, y_val, degrees):
    """Pick the degree with the smallest held-out MSE. Returns (d*, w, {d: val_mse})."""
    fits = nested_poly_erm(x_tr, y_tr, degrees)
    val = {d: mse(poly_features(x_val, d), w, y_val) for d, (w, _) in fits.items()}
    d_star = min(val, key=val.get)
    return d_star, fits[d_star][0], val


def validation_bound(k: int, n_val: int, delta: float, span: float = 1.0) -> float:
    """Hoeffding + union bound over k candidates: |L_D - L_V| <= span sqrt(log(2k/delta)/(2 n_val))."""
    return span * math.sqrt(math.log(2 * k / delta) / (2 * n_val))


def validation_experiment(n_val: int, delta: float, trials: int, rng: np.random.Generator):
    """Theorem 6.9(a) for the fixed predictor x -> x on the noisy sine, loss min(1, sq. error).

    Returns (fraction of validation sets with |L_V - L_D| > bound, bound).
    L_D is estimated once on 200 000 fresh points.
    """
    loss = lambda x, y: np.minimum(1.0, (x - y) ** 2)
    xb = rng.uniform(-1, 1, 200_000)
    L = loss(xb, target(xb) + 0.3 * rng.normal(size=xb.size)).mean()
    bound = validation_bound(1, n_val, delta)
    xv = rng.uniform(-1, 1, (trials, n_val))
    LV = loss(xv, target(xv) + 0.3 * rng.normal(size=xv.shape)).mean(axis=1)
    return float(np.mean(np.abs(LV - L) > bound)), bound


def target(x):
    return np.sin(2 * np.pi * x)


# RLM with the logistic loss and replace-one stability (Theorems 6.6, 6.7) ----

def logistic_loss(w: np.ndarray, X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """l(w,(x,y)) = log(1 + exp(-y <w,x>)): convex, ||x||-Lipschitz in w."""
    return np.logaddexp(0.0, -y * (X @ w))


def rlm_logistic(X: np.ndarray, y: np.ndarray, lam: float, iters: int = 50) -> np.ndarray:
    """argmin_w (1/n) sum_i l(w, z_i) + lam ||w||^2 by Newton's method (2lam-strongly convex)."""
    n, d = X.shape
    w = np.zeros(d)
    for _ in range(iters):
        p = 0.5 * (1 + np.tanh(0.5 * X @ w))               # sigmoid(<w,x>)
        g = X.T @ (p - (y + 1) / 2) / n + 2 * lam * w
        H = (X.T * (p * (1 - p))) @ X / n + 2 * lam * np.eye(d)
        step = np.linalg.solve(H, g)
        w -= step
        if np.linalg.norm(step) < 1e-13:
            break
    return w


def sample_ball_classification(n: int, d: int, rng: np.random.Generator, flip: float = 0.1):
    """x uniform in the unit ball of R^d (so R = rho = 1), y = sign(x_1) flipped w.p. `flip`."""
    X = rng.normal(size=(n, d))
    X *= (rng.uniform(size=(n, 1)) ** (1 / d)) / np.linalg.norm(X, axis=1, keepdims=True)
    y = np.where(X[:, 0] > 0, 1.0, -1.0)
    return X, np.where(rng.uniform(size=n) < flip, -y, y)


def stability_experiment(n: int, d: int, lam: float, trials: int, rng: np.random.Generator,
                         n_test: int = 20_000):
    """Theorems 6.6 and 6.7 for logistic RLM on `trials` draws of (S, z', i).

    Returns a dict of per-trial arrays: gap = L_D(A(S)) - L_S(A(S)) (L_D on n_test
    fresh points), replace = l(A(S^(i)), z_i) - l(A(S), z_i), dw = ||A(S^(i)) - A(S)||,
    and the bounds 2rho/(lam n), 2rho^2/(lam n) with rho = R = 1.
    """
    Xt, yt = sample_ball_classification(n_test, d, rng)
    gap, rep, dw = np.empty(trials), np.empty(trials), np.empty(trials)
    for j in range(trials):
        X, y = sample_ball_classification(n + 1, d, rng)
        Xs, ys, xz, yz = X[:n], y[:n], X[n:], y[n:]
        w = rlm_logistic(Xs, ys, lam)
        gap[j] = logistic_loss(w, Xt, yt).mean() - logistic_loss(w, Xs, ys).mean()
        i = int(rng.integers(n))
        Xi, yi = Xs.copy(), ys.copy()
        Xi[i], yi[i] = xz[0], yz[0]
        wi = rlm_logistic(Xi, yi, lam)
        rep[j] = (logistic_loss(wi, Xs[i:i + 1], ys[i:i + 1]) - logistic_loss(w, Xs[i:i + 1], ys[i:i + 1]))[0]
        dw[j] = np.linalg.norm(wi - w)
    return {"gap": gap, "replace": rep, "dw": dw,
            "bound_w": 2 / (lam * n), "bound_loss": 2 / (lam * n)}


def bias_complexity_curve(n: int, degrees, sigma: float, rng: np.random.Generator,
                          n_test: int = 2000):
    """Train and test MSE of nested polynomial ERM on a noisy sine: the U-shaped curve."""
    x = rng.uniform(-1, 1, n)
    y = target(x) + sigma * rng.normal(size=n)
    xt = rng.uniform(-1, 1, n_test)
    yt = target(xt) + sigma * rng.normal(size=n_test)
    fits = nested_poly_erm(x, y, degrees)
    return {d: (ls, mse(poly_features(xt, d), w, yt)) for d, (w, ls) in fits.items()}


if __name__ == "__main__":
    import sys
    rng = np.random.default_rng(0)
    degrees = list(range(0, 16))
    n, sigma = 30, 0.3
    curve = bias_complexity_curve(n, degrees, sigma, rng)
    print(f"{'deg':>4} {'train':>8} {'test':>8}")
    for d, (tr, te) in curve.items():
        print(f"{d:4d} {tr:8.4f} {te:8.4f}")
    if "--png" in sys.argv:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.plot(degrees, [curve[d][0] for d in degrees], "o-", label="train")
        plt.plot(degrees, [curve[d][1] for d in degrees], "s-", label="test")
        plt.xlabel("polynomial degree"); plt.ylabel("MSE"); plt.legend(); plt.title("bias-complexity trade-off")
        plt.savefig("bias_complexity.png", dpi=120); print("saved bias_complexity.png")
    x = rng.uniform(-1, 1, n)
    y = target(x) + sigma * rng.normal(size=n)
    d_srm, _, _ = srm_select(x, y, degrees, scale=0.5)
    xv = rng.uniform(-1, 1, n)
    yv = target(xv) + sigma * rng.normal(size=n)
    d_val, _, _ = validation_select(x, y, xv, yv, degrees)
    print(f"\nSRM picks degree {d_srm}, validation picks degree {d_val} (noise var {sigma**2:.2f})")
    print(f"Validation bound, k=16 candidates, n_val=30, delta=0.05: "
          f"{validation_bound(16, 30, 0.05):.3f} (times loss range)")
    freq, b = validation_experiment(50, 0.1, 5000, rng)
    print(f"Theorem 6.9(a), n_v=50, delta=0.1, 5000 validation sets: P(|L_V - L_D| > {b:.3f}) = {freq:.4f}")
    for lam in (0.0, 1e-3, 1e-1):
        w = tikhonov(poly_features(x, 15), y, lam) if lam > 0 else fit_least_squares(poly_features(x, 15), y)
        print(f"Tikhonov degree 15, lambda={lam:g}: ||w||={np.linalg.norm(w):9.2f}  "
              f"test MSE={mse(poly_features(xv, 15), w, yv):.4f}")
    print("\nTheorems 6.6/6.7, logistic RLM, unit ball in R^5 (rho = 1), 400 draws of (S, z', i):")
    print(f"{'n':>5} {'lambda':>7} {'E gap':>8} {'E replace-one':>14} {'max dw':>8} {'2rho/(lam n)':>13}"
          f" {'max replace':>12} {'2rho^2/(lam n)':>15}")
    for n, lam in ((50, 0.05), (200, 0.05), (200, 0.01)):
        r = stability_experiment(n, 5, lam, 400, rng)
        print(f"{n:5d} {lam:7.2f} {r['gap'].mean():8.4f} {r['replace'].mean():14.4f} {r['dw'].max():8.4f}"
              f" {r['bound_w']:13.4f} {r['replace'].max():12.4f} {r['bound_loss']:15.4f}")
