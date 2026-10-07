"""PAC learning: sample complexities and an empirical check of the guarantee.

Note 03 (PAC learning), section Results:
- Theorem 3.1: finite classes are (agnostic) PAC learnable by ERM
  (`sample_complexity_finite`, same formulas as concentration.py).
- Note 04, Theorem 4.11 (fundamental theorem): VC-based sample sizes up to the
  unknown constant C (`sample_complexity_vc`).
- The textbook realisable-threshold argument behind Theorem 2.7 / 3.1: for the
  consistent learner that returns the largest negative point, the failure event
  L_D(h_S) > eps is exactly "no sample in [theta-eps, theta]", so
  P(fail) = (1-eps)^n <= e^{-eps n} (`threshold_failure_exact`).

Run `python pac.py`: failure probabilities over many resamples vs delta, and
Monte-Carlo vs exact (1-eps)^n.
"""
from __future__ import annotations

import math

import numpy as np

import concentration
from framework import ThresholdProblem


def sample_complexity_finite(size_H: int, eps: float, delta: float,
                             realisable: bool = True) -> int:
    """n_H(eps, delta) for a finite class; delegates to concentration.py (default: realisable)."""
    return concentration.sample_complexity_finite(size_H, eps, delta, realisable)


def sample_complexity_vc(d: int, eps: float, delta: float, realisable: bool = True,
                         C: float = 1.0) -> int:
    """Upper bound of the fundamental theorem, with an explicit constant C.

    realisable: C (d log(1/eps) + log(1/delta)) / eps
    agnostic:   C (d + log(1/delta)) / eps^2
    The true constants (UML Thm 6.8) are not tight; C=1 gives the order of magnitude.
    """
    if realisable:
        return math.ceil(C * (d * math.log(1 / eps) + math.log(1 / delta)) / eps)
    return math.ceil(C * (d + math.log(1 / delta)) / eps**2)


def consistent_threshold_learner(X: np.ndarray, y: np.ndarray) -> float:
    """Realisable thresholds: return the midpoint between the largest -1 and smallest +1."""
    lo = X[y == -1].max() if np.any(y == -1) else 0.0
    hi = X[y == 1].min() if np.any(y == 1) else 1.0
    return 0.5 * (lo + hi)


def max_negative_threshold_learner(X: np.ndarray, y: np.ndarray) -> float:
    """Realisable thresholds: t = largest x_i labelled -1 (0 if none). Consistent,
    and its error theta - t has the exact tail P(theta - t > eps) = (1-eps)^n."""
    return float(X[y == -1].max()) if np.any(y == -1) else 0.0


def threshold_failure_exact(eps: float, n: int, theta: float) -> float:
    """P_S(L_D(h_S) > eps) for `max_negative_threshold_learner`, x ~ U[0,1], no noise.

    Failure iff no x_i falls in [theta - eps, theta] (an interval of mass min(eps, theta)).
    """
    return (1.0 - min(eps, theta)) ** n if eps < theta else 0.0


def erm_threshold_learner(X: np.ndarray, y: np.ndarray) -> float:
    """Agnostic ERM over all thresholds: scan the sorted sample (O(n log n))."""
    order = np.argsort(X)
    Xs, ys = X[order], y[order]
    # threshold before position i: predict -1 for j < i, +1 for j >= i
    err_left = np.concatenate([[0], np.cumsum(ys == 1)])       # +1's predicted -1
    err_right = np.concatenate([np.cumsum((ys == -1)[::-1])[::-1], [0]])  # -1's predicted +1
    errs = err_left + err_right
    i = int(np.argmin(errs))
    if i == 0:
        return Xs[0] - 1e-9
    if i == len(Xs):
        return Xs[-1] + 1e-9
    return 0.5 * (Xs[i - 1] + Xs[i])


def estimate_failure_probability(problem: ThresholdProblem, learner, n: int, eps: float,
                                 trials: int, rng: np.random.Generator) -> float:
    """Fraction of runs with L_D(h_S) - min_h L_D(h) > eps (excess risk, agnostic form)."""
    fails = 0
    for _ in range(trials):
        X, y = problem.sample(n, rng)
        h = learner(X, y)
        fails += (problem.risk(h) - problem.bayes_risk) > eps
    return fails / trials


def pac_demo(eps=0.1, delta=0.05, trials=500, seed=0):
    rng = np.random.default_rng(seed)
    d = 1  # VC dimension of thresholds
    clean = ThresholdProblem(theta=0.3, eta=0.0)
    noisy = ThresholdProblem(theta=0.3, eta=0.1)
    n_real = sample_complexity_vc(d, eps, delta, realisable=True)
    n_agn = sample_complexity_vc(d, eps, delta, realisable=False)
    print(f"VC bound sample sizes (C=1): realisable n={n_real}, agnostic n={n_agn}")
    fr = estimate_failure_probability(clean, consistent_threshold_learner, n_real, eps, trials, rng)
    fa = estimate_failure_probability(noisy, erm_threshold_learner, n_agn, eps, trials, rng)
    print(f"P(excess risk > {eps}) realisable: {fr:.3f} (target <= {delta})")
    print(f"P(excess risk > {eps}) agnostic:   {fa:.3f} (target <= {delta})")
    return fr, fa


if __name__ == "__main__":
    print("Theorem 3.1, finite classes, eps = delta = 0.05:")
    for size in (10, 1000, 10**6):
        print(f"  |H|={size:>8}: realisable n={sample_complexity_finite(size, 0.05, 0.05):6d}"
              f"  agnostic n={sample_complexity_finite(size, 0.05, 0.05, False):7d}")
    pac_demo()
    rng = np.random.default_rng(1)
    eps, theta = 0.05, 0.3
    print(f"\nRealisable thresholds, largest-negative learner, eps={eps}, 20 000 resamples:")
    print(f"{'n':>5} {'MC P(fail)':>11} {'exact (1-eps)^n':>16} {'bound e^(-eps n)':>17}")
    for n in (10, 30, 60, 100):
        mc = estimate_failure_probability(ThresholdProblem(theta, 0.0), max_negative_threshold_learner,
                                          n, eps, 20_000, rng)
        print(f"{n:5d} {mc:11.4f} {threshold_failure_exact(eps, n, theta):16.4f} {math.exp(-eps * n):17.4f}")
