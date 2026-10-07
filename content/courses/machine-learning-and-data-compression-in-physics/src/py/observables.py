"""Pattern recognition and prediction of observables from Ising configurations.

Note 07 (pattern recognition and prediction of observables).
- Regression of the energy per spin e and of m^2 from raw spins: linear ridge
  fails (e, m^2 are even under s -> -s, a linear function of s is odd), ridge on
  nearest-neighbour bond features is exact, kernel ridge with the degree-2
  polynomial kernel (1 + x.y/N)^2 recovers both (`ridge`, `kernel_ridge`, `r2`).
- Phase classification T < T_c vs T > T_c (Carrasquilla-Melko [S23]): logistic
  regression on raw spins fails for the same symmetry reason; logistic on m^2
  works; a small MLP on raw spins works once the training set is augmented with
  the flipped snapshots -s (the Z2 symmetry as data); the crossing of the mean
  P(ordered) with 1/2 estimates T_c (`logistic_newton`, `MLPClassifier`, `estimate_tc`).

All models are hand-written (numpy closed forms, Newton, a torch MLP); tests
cross-check ridge and kernel ridge against scikit-learn.

Run `python observables.py`.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from ising_snapshots import T_C, bond_features, energy_per_spin, magnetisation, sample_ising


def dataset(L: int = 10, n_per_T: int = 60, seed: int = 0):
    """Dict with raw spins X (n, N), bonds B, e, m, T, label (T < T_c), train/test index."""
    temps = np.linspace(1.5, 3.5, 16)
    s, T = sample_ising(L, temps, n_per_T, n_therm=400, rng=np.random.default_rng(seed))
    perm = np.random.default_rng(seed + 1).permutation(len(s))
    cut = int(0.7 * len(s))
    return {"X": s.reshape(len(s), -1).astype(np.float64), "B": bond_features(s),
            "e": energy_per_spin(s), "m": magnetisation(s), "T": T, "y": (T < T_C).astype(float),
            "tr": perm[:cut], "te": perm[cut:], "L": L}


def r2(y: np.ndarray, yhat: np.ndarray) -> float:
    """Coefficient of determination 1 - SS_res / SS_tot."""
    return float(1.0 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2))


def ridge(X: np.ndarray, y: np.ndarray, lam: float):
    """Ridge with unpenalised intercept: returns predict(Xnew)."""
    mx, my = X.mean(0), y.mean()
    Xc = X - mx
    w = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y - my))
    return lambda Z: (Z - mx) @ w + my


def poly2_kernel(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """(1 + a.b / N)^2: spans all s_i s_j products, hence e and m^2."""
    return (1.0 + A @ B.T / A.shape[1]) ** 2


def kernel_ridge(X: np.ndarray, y: np.ndarray, lam: float, kernel=poly2_kernel):
    """alpha = (K + lam I)^{-1} (y - mean y); predict(Z) = k(Z, X) alpha + mean y."""
    my = y.mean()
    alpha = np.linalg.solve(kernel(X, X) + lam * np.eye(len(X)), y - my)
    return lambda Z: kernel(Z, X) @ alpha + my


def logistic_newton(F: np.ndarray, y: np.ndarray, lam: float = 1e-3, iters: int = 50):
    """L2-regularised logistic regression by Newton's method; returns predict_proba."""
    mu, sd = F.mean(0), F.std(0) + 1e-12
    Z = np.hstack([np.ones((len(F), 1)), (F - mu) / sd])
    w = np.zeros(Z.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Z @ w))
        g = Z.T @ (p - y) + lam * w
        H = (Z.T * (p * (1 - p))) @ Z + lam * np.eye(len(w))
        w -= np.linalg.solve(H, g)
    return lambda G: 1 / (1 + np.exp(-np.hstack([np.ones((len(G), 1)), (G - mu) / sd]) @ w))


class MLPClassifier(nn.Module):
    """N -> h -> 1, tanh hidden layer, as in Carrasquilla-Melko [S23]."""

    def __init__(self, n: int, h: int = 16):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n, h), nn.Tanh(), nn.Linear(h, 1))

    def fit(self, X, y, steps: int = 600, lr: float = 1e-2, wd: float = 1e-3, seed: int = 0):
        torch.manual_seed(seed)
        for mod in self.net:
            if isinstance(mod, nn.Linear):
                mod.reset_parameters()
        Xt, yt = torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
        opt = torch.optim.AdamW(self.parameters(), lr=lr, weight_decay=wd)
        lossf = nn.BCEWithLogitsLoss()
        for _ in range(steps):
            loss = lossf(self.net(Xt)[:, 0], yt)
            opt.zero_grad()
            loss.backward()
            opt.step()
        return self

    @torch.no_grad()
    def predict_proba(self, X) -> np.ndarray:
        return torch.sigmoid(self.net(torch.tensor(X, dtype=torch.float32))[:, 0]).numpy()


def accuracy(y, p, mask=None) -> float:
    ok = (p > 0.5) == (y > 0.5)
    return float(np.mean(ok if mask is None else ok[mask]))


def estimate_tc(T: np.ndarray, p: np.ndarray) -> float:
    """Temperature where the per-T mean of P(ordered) crosses 1/2 (linear interpolation)."""
    ts = np.unique(T)
    mp = np.array([p[T == t].mean() for t in ts])
    i = int(np.nonzero((mp[:-1] >= 0.5) & (mp[1:] < 0.5))[0][0])
    return float(ts[i] + (mp[i] - 0.5) * (ts[i + 1] - ts[i]) / (mp[i] - mp[i + 1]))


def regression_table(d) -> dict:
    tr, te = d["tr"], d["te"]
    X, B = d["X"], d["B"]
    out = {}
    for name, y in (("e", d["e"]), ("m2", d["m"] ** 2)):
        out[(name, "ridge raw")] = r2(y[te], ridge(X[tr], y[tr], 1.0)(X[te]))
        out[(name, "ridge bonds")] = r2(y[te], ridge(B[tr], y[tr], 1e-6)(B[te]))
        out[(name, "KRR poly2 raw")] = r2(y[te], kernel_ridge(X[tr], y[tr], 1e-6)(X[te]))
    return out


def classification_table(d) -> dict:
    tr, te = d["tr"], d["te"]
    X, y, T = d["X"], d["y"], d["T"]
    far = np.abs(T[te] - T_C) > 0.3
    m2 = (d["m"] ** 2)[:, None]
    res = {}
    p = logistic_newton(X[tr], y[tr])(X[te])
    res["logistic raw"] = (accuracy(y[te], p), accuracy(y[te], p, far))
    p = logistic_newton(m2[tr], y[tr])(m2[te])
    res["logistic m^2"] = (accuracy(y[te], p), accuracy(y[te], p, far))
    mlp = MLPClassifier(X.shape[1]).fit(X[tr], y[tr])
    p = mlp.predict_proba(X[te])
    res["MLP raw"] = (accuracy(y[te], p), accuracy(y[te], p, far))
    # the symmetry s -> -s as data augmentation: same labels for flipped snapshots
    mlp = MLPClassifier(X.shape[1], h=32).fit(np.vstack([X[tr], -X[tr]]),
                                              np.concatenate([y[tr], y[tr]]), steps=1500)
    p = mlp.predict_proba(X[te])
    res["MLP raw + Z2"] = (accuracy(y[te], p), accuracy(y[te], p, far))
    res["Tc_MLP"] = estimate_tc(T, mlp.predict_proba(X))
    return res


def demo() -> None:
    torch.set_num_threads(1)
    d = dataset()
    print(f"Ising {d['L']}x{d['L']}, {len(d['X'])} configs, 16 temperatures in [1.5, 3.5], "
          f"{len(d['tr'])} train / {len(d['te'])} test")
    print("\ntest R^2")
    for (target, model), v in regression_table(d).items():
        print(f"  {target:>3}  {model:<14} {v:8.4f}")
    print("  linear in s cannot fit a Z2-even target. Bonds make e exactly linear. The poly-2 kernel\n"
          "  contains both e and m^2, but m^2 weights all N^2 products s_i s_j equally (small RKHS\n"
          "  norm) while e sits on 2N of them (large norm): e needs more than 672 samples.")
    res = classification_table(d)
    print("\nphase classification, test accuracy (all / |T - T_c| > 0.3)")
    for k in ("logistic raw", "logistic m^2", "MLP raw", "MLP raw + Z2"):
        print(f"  {k:<13} {res[k][0]:.3f} / {res[k][1]:.3f}")
    print(f"T_c from MLP crossing P = 1/2: {res['Tc_MLP']:.3f} (exact infinite lattice {T_C:.3f}; "
          f"L = {d['L']} shifts it)")


if __name__ == "__main__":
    demo()
