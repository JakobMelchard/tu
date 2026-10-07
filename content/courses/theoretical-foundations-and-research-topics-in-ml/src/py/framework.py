"""Statistical learning framework: risk, empirical risk, ERM, optimism of L_S.

Note 01 (statistical learning framework), section Results:
- Proposition 1.5: risk of a threshold under label noise, eta + (1-2eta)|t-theta|.
- Theorem 1.3: E_S L_S(h) = L_D(h) for fixed h; E_S L_S(h_S) <= min_H L_D <= E_S L_D(h_S).
- Theorem 1.4: the memorising classifier has L_S = 0 and L_D = P(y = +1).
- Definition 11: ERM over a finite class (`erm_finite`).

`threshold_empirical_risks` evaluates L_S for many thresholds at once and is
reused by concentration.py, vc.py, rademacher.py and srm.py.

Run `python framework.py`: closed-form vs Monte-Carlo risk, the Theorem 1.3(b)
chain over 200 resamples per n, and the memoriser.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def zero_one_loss(pred: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Pointwise 0-1 loss for labels in {-1, +1}."""
    return (pred != y).astype(float)


def squared_loss(pred: np.ndarray, y: np.ndarray) -> np.ndarray:
    return (pred - y) ** 2


def empirical_risk(pred: np.ndarray, y: np.ndarray, loss=zero_one_loss) -> float:
    """L_S(h) = (1/n) sum_i loss(h(x_i), y_i)."""
    return float(np.mean(loss(pred, y)))


def threshold_predict(t: float, X: np.ndarray) -> np.ndarray:
    """h_t(x) = +1 if x > t else -1."""
    return np.where(X > t, 1, -1)


def threshold_empirical_risks(X: np.ndarray, y: np.ndarray, ts: np.ndarray) -> np.ndarray:
    """L_S(h_t) for every t in ts in O((n + |ts|) log n).

    Errors of h_t = #{x_i <= t, y_i = +1} + #{x_i > t, y_i = -1}; with the sample
    sorted, both counts are prefix sums evaluated at c(t) = #{x_i <= t}.
    """
    order = np.argsort(X)
    xs, ys = X[order], y[order]
    pos = np.concatenate([[0], np.cumsum(ys == 1)])
    neg = np.concatenate([[0], np.cumsum(ys == -1)])
    c = np.searchsorted(xs, np.asarray(ts, float), side="right")
    return (pos[c] + (neg[-1] - neg[c])) / len(X)


@dataclass
class ThresholdProblem:
    """x ~ U[0,1], y = sign(x - theta) with each label flipped w.p. eta.

    Proposition 1.5: the Bayes predictor is h_theta, the Bayes risk is eta, and
    for t in [0,1] the risk is eta + (1-2eta)|t-theta| (h_t disagrees with the
    clean label exactly on the interval between t and theta).
    """

    theta: float = 0.3
    eta: float = 0.1

    def sample(self, n: int, rng: np.random.Generator):
        X = rng.uniform(0.0, 1.0, size=n)
        y = np.where(X > self.theta, 1, -1)
        flip = rng.uniform(size=n) < self.eta
        return X, np.where(flip, -y, y)

    def risk(self, t):
        """Closed form; vectorised over t, and t outside [0,1] acts like its clip."""
        t = np.clip(t, 0.0, 1.0)
        return self.eta + (1 - 2 * self.eta) * np.abs(t - self.theta)

    @property
    def bayes_risk(self) -> float:
        return self.eta

    def risk_mc(self, t: float, rng: np.random.Generator, n: int = 200_000) -> float:
        """Monte-Carlo estimate of the true risk, used to check `risk`."""
        X, y = self.sample(n, rng)
        return empirical_risk(threshold_predict(t, X), y)


def finite_threshold_class(k: int) -> np.ndarray:
    """k equally spaced thresholds in (0,1): the finite class H_k."""
    return (np.arange(k) + 0.5) / k


def erm_finite(hyps: np.ndarray, X: np.ndarray, y: np.ndarray, predict=threshold_predict):
    """ERM over a finite class given as an array of parameters (Definition 11).

    Returns (best parameter, its empirical risk). Ties broken by first index.
    """
    risks = np.array([empirical_risk(predict(h, X), y) for h in hyps])
    i = int(np.argmin(risks))
    return hyps[i], float(risks[i])


def generalisation_gap_experiment(problem: ThresholdProblem, k: int, n: int,
                                  trials: int, rng: np.random.Generator):
    """Theorem 1.3(b) over `trials` resamples: (E L_S(h_S), E L_D(h_S), min_H L_D).

    The theorem predicts E L_S(h_S) <= min_H L_D <= E L_D(h_S).
    """
    hyps = finite_threshold_class(k)
    best_in_class = float(np.min(problem.risk(hyps)))
    train, true = [], []
    for _ in range(trials):
        X, y = problem.sample(n, rng)
        risks = threshold_empirical_risks(X, y, hyps)
        i = int(np.argmin(risks))
        train.append(risks[i])
        true.append(problem.risk(hyps[i]))
    return float(np.mean(train)), float(np.mean(true)), best_in_class


def memoriser_predict(X_train: np.ndarray, y_train: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Theorem 1.4's h_S: y_i if x = x_i for some i, else -1."""
    lookup = dict(zip(X_train.tolist(), y_train.tolist()))
    return np.array([lookup.get(x, -1) for x in X.tolist()])


def memoriser_risk(problem: ThresholdProblem):
    """Closed form of Theorem 1.4: (L_S, L_D) = (0, P(y = +1)).

    x is continuous, so a fresh point is never in the sample and h_S predicts -1:
    L_D = P(y=+1) = (1-theta)(1-eta) + theta eta.
    """
    p_plus = (1 - problem.theta) * (1 - problem.eta) + problem.theta * problem.eta
    return 0.0, p_plus


def memoriser_experiment(problem: ThresholdProblem, n: int, n_test: int,
                         rng: np.random.Generator):
    """Monte-Carlo (L_S, L_D) of the memoriser, to compare with `memoriser_risk`."""
    X, y = problem.sample(n, rng)
    Xt, yt = problem.sample(n_test, rng)
    return (empirical_risk(memoriser_predict(X, y, X), y),
            empirical_risk(memoriser_predict(X, y, Xt), yt))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    prob = ThresholdProblem(theta=0.3, eta=0.1)
    print(f"Proposition 1.5, Bayes risk = {prob.bayes_risk}")
    for t in (0.3, 0.4, 0.6):
        print(f"  L_D(h_{t}) closed form {prob.risk(t):.4f}  MC {prob.risk_mc(t, rng):.4f}")
    print("\nTheorem 1.3(b): ERM over k=50 thresholds, 200 resamples per n")
    print(f"{'n':>6} {'E L_S(h_S)':>12} {'min_H L_D':>10} {'E L_D(h_S)':>12}  chain holds")
    for n in (10, 30, 100, 300, 1000):
        tr, te, best = generalisation_gap_experiment(prob, 50, n, 200, rng)
        print(f"{n:6d} {tr:12.4f} {best:10.4f} {te:12.4f}  {tr <= best <= te}")
    ls, ld = memoriser_experiment(prob, 100, 100_000, rng)
    print(f"\nTheorem 1.4, memoriser: MC L_S = {ls}, L_D = {ld:.3f}; "
          f"closed form (0, {memoriser_risk(prob)[1]:.3f})")
