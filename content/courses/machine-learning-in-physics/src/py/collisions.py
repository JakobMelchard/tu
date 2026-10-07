"""Signal vs background for synthetic collision events: logistic, MLP, ROC and AUC.

Note 10 (exercise domain "classification of proton collisions in the LHC"). The course
used the simulated SUSY dataset of Baldi et al. [S17] (18 kinematic variables, 5e6
events; 2021S exercises 08-09 [S5]). No download here: the features are a TOY with the
same structure, not physics:
  pT1, pT2   lepton transverse momenta, harder for signal
  MET        missing transverse energy, larger for signal (invisible neutralinos)
  dphi       azimuthal angle between the leptons
  eta1, eta2 pseudorapidities; individually identical for both classes, but signal
             leptons are correlated (|eta1 - eta2| small): invisible to a linear model
  phi1       pure noise
ROC: sweep the threshold on a score, TPR = TP/P against FPR = FP/N.
AUC = P(score_signal > score_background) + P(=)/2 (Mann-Whitney U / (P N)).
"""
from __future__ import annotations

import numpy as np

import classification as cl

NAMES = ["pT1", "pT2", "MET", "dphi", "eta1", "eta2", "phi1"]


def make_events(n, signal_fraction=0.3, seed=0):
    rng = np.random.default_rng(seed)
    y = (rng.random(n) < signal_fraction).astype(int)
    s = y == 1
    pt1 = np.where(s, rng.gamma(2.0, 30.0, n), rng.gamma(2.0, 22.0, n))
    pt2 = np.where(s, rng.gamma(2.0, 20.0, n), rng.gamma(2.0, 16.0, n))
    met = np.where(s, rng.gamma(3.0, 22.0, n), rng.gamma(2.0, 20.0, n))
    dphi = np.where(s, np.pi * rng.beta(2.0, 1.5, n), np.pi * rng.random(n))
    eta1 = rng.normal(0.0, 1.2, n)
    eta2_b = rng.normal(0.0, 1.2, n)
    # signal: eta2 = rho eta1 + sqrt(1 - rho^2) noise keeps the marginal N(0, 1.2)
    rho = 0.9
    eta2_s = rho * eta1 + np.sqrt(1 - rho**2) * rng.normal(0.0, 1.2, n)
    eta2 = np.where(s, eta2_s, eta2_b)
    phi1 = rng.uniform(-np.pi, np.pi, n)
    return np.c_[pt1, pt2, met, dphi, eta1, eta2, phi1], y


def engineered(X):
    """Physicist's features: logs of the momenta, |eta1 - eta2|, MET / (pT1 + pT2)."""
    return np.c_[np.log(X[:, :3]), X[:, 3], np.abs(X[:, 4] - X[:, 5]),
                 X[:, 2] / (X[:, 0] + X[:, 1])]


def standardise(Xtr, Xte):
    mu, sd = Xtr.mean(0), Xtr.std(0)
    return (Xtr - mu) / sd, (Xte - mu) / sd


def roc_curve(y, score):
    """FPR, TPR at every distinct threshold (descending), starting at (0, 0)."""
    order = np.argsort(-score, kind="mergesort")
    s, yy = score[order], y[order]
    distinct = np.r_[np.flatnonzero(np.diff(s)), yy.size - 1]  # last index of each tie block
    tp = np.cumsum(yy)[distinct]
    fp = (distinct + 1) - tp
    return np.r_[0.0, fp / (yy.size - yy.sum())], np.r_[0.0, tp / yy.sum()]


def auc(y, score) -> float:
    fpr, tpr = roc_curve(y, score)
    return float(np.trapezoid(tpr, fpr))


def auc_mann_whitney(y, score) -> float:
    """Rank form: (sum of signal ranks - P(P+1)/2) / (P N), average ranks for ties."""
    from scipy.stats import rankdata
    r = rankdata(score)
    P = int(y.sum())
    N = y.size - P
    return float((r[y == 1].sum() - P * (P + 1) / 2) / (P * N))


def tpr_at_fpr(y, score, fpr_target=0.01) -> float:
    fpr, tpr = roc_curve(y, score)
    return float(np.interp(fpr_target, fpr, tpr))


def fit_all(n_train=20000, n_test=20000, seed=0):
    from sklearn.neural_network import MLPClassifier

    Xtr, ytr = make_events(n_train, seed=seed)
    Xte, yte = make_events(n_test, seed=seed + 1)
    out = {}
    A, B = standardise(Xtr, Xte)
    w = cl.logistic_newton(cl.add_bias(A), ytr, lam=1e-3)
    out["logistic, raw"] = cl.sigmoid(cl.add_bias(B) @ w)
    out["_w_raw"] = w
    A2, B2 = standardise(engineered(Xtr), engineered(Xte))
    w2 = cl.logistic_newton(cl.add_bias(A2), ytr, lam=1e-3)
    out["logistic, engineered"] = cl.sigmoid(cl.add_bias(B2) @ w2)
    mlp = MLPClassifier((32, 32), early_stopping=True, max_iter=300, random_state=seed)
    mlp.fit(A, ytr)
    out["MLP 32-32, raw"] = mlp.predict_proba(B)[:, 1]
    return yte, out


def _demo() -> None:
    yte, scores = fit_all()
    print(f"test events {yte.size}, signal fraction {yte.mean():.3f} "
          f"(always 'background' scores accuracy {1 - yte.mean():.3f})")
    print("raw logistic weights (standardised):",
          dict(zip(["bias"] + NAMES, np.round(scores.pop("_w_raw"), 2).tolist())))
    for name, sc in scores.items():
        c = cl.confusion(yte, (sc > 0.5).astype(int))
        print(f"{name:22s} AUC {auc(yte, sc):.4f}  acc {c['accuracy']:.3f}  "
              f"sens {c['sensitivity']:.3f}  spec {c['specificity']:.3f}  "
              f"TPR@FPR=1% {tpr_at_fpr(yte, sc):.3f}")


if __name__ == "__main__":
    _demo()
