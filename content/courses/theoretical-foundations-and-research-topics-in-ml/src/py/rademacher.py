"""Empirical Rademacher complexity for finite, threshold and linear classes.

Note 05 (Rademacher complexity), section Results:
- Definition: R_S(F) = E_sigma sup_f (1/n) sum_i sigma_i f(z_i); Monte Carlo
  (`empirical_rademacher_finite`) and exact by enumerating all 2^n sign vectors
  (`empirical_rademacher_exact`, worked example: 3/4 for thresholds on 2 points).
- Theorem 5.3: with prob >= 1-delta, L_D(h) <= L_S(h) + 2 R_S(l o H) + 3 sqrt(log(2/delta)/(2n)),
  and R_S(l_01 o H) = R_S(H)/2 (Remark after 5.3). `rademacher_bound_experiment`
  checks it over many resamples with the exact one-sided sup from vc.py.
- Theorem 5.6: Massart, R_S <= r sqrt(2 log|F|) / n (`massart_bound`).
- Theorem 5.7: linear class ||w|| <= B: R_S = (B/n) E||sum sigma_i x_i|| <= BR/sqrt(n).
- Theorem 5.9: R_S(H) <= sqrt(2 d log(en/d) / n) (`rademacher_vc_bound`).

Run `python rademacher.py`.
"""
from __future__ import annotations

import itertools
import math

import numpy as np

from framework import ThresholdProblem
from vc import threshold_sup_deviation


def empirical_rademacher_finite(predictions: np.ndarray, n_sigma: int,
                                rng: np.random.Generator) -> float:
    """R_S(F) for a finite class given as a (|F|, n) matrix of values f(z_i).

    Monte-Carlo over n_sigma draws of sigma in {-1,+1}^n:
    R_S = E_sigma max_f (1/n) sum_i sigma_i f(z_i).
    """
    F = np.asarray(predictions, float)
    n = F.shape[1]
    sigma = rng.choice([-1.0, 1.0], size=(n_sigma, n))
    return float(np.mean(np.max(sigma @ F.T, axis=1)) / n)


def empirical_rademacher_exact(predictions: np.ndarray) -> float:
    """R_S(F) by enumerating all 2^n sign vectors (n <= ~20)."""
    F = np.asarray(predictions, float)
    n = F.shape[1]
    sigma = np.array(list(itertools.product([-1.0, 1.0], repeat=n)))
    return float(np.mean(np.max(sigma @ F.T, axis=1)) / n)


def massart_bound(n_hyps: int, n: int, max_norm: float | None = None) -> float:
    """Massart: R_S(F) <= max_f ||f||_2 sqrt(2 log |F|) / n; with |f_i|<=1, ||f||_2 <= sqrt(n)."""
    if max_norm is None:
        max_norm = math.sqrt(n)
    return max_norm * math.sqrt(2 * math.log(n_hyps)) / n


def threshold_predictions(X: np.ndarray) -> np.ndarray:
    """All distinct labelings of a 1-D sample by thresholds (n+1 of them)."""
    x = np.asarray(X, float).ravel()
    cuts = np.concatenate([[-np.inf], np.sort(x)])
    return np.array([np.where(x > t, 1.0, -1.0) for t in cuts])


def rademacher_threshold(X: np.ndarray, n_sigma: int, rng: np.random.Generator) -> float:
    """R_S of thresholds in O(n_sigma n): with sigma in sorted-x order and prefix sums
    P_k, the labeling (-1)^k (+1)^{n-k} scores T - 2 P_k, so the sup is T - 2 min_k P_k."""
    n = len(np.asarray(X).ravel())
    sigma = rng.choice([-1.0, 1.0], size=(n_sigma, n))
    P = np.concatenate([np.zeros((n_sigma, 1)), np.cumsum(sigma, axis=1)], axis=1)
    return float(np.mean(P[:, -1] - 2 * P.min(axis=1)) / n)


def rademacher_linear_exact(X: np.ndarray, B: float, n_sigma: int,
                            rng: np.random.Generator) -> float:
    """R_S of {x -> <w,x> : ||w||<=B}: sup is attained at w = B u/||u||, u = sum sigma_i x_i,
    so R_S = (B/n) E_sigma ||sum_i sigma_i x_i||."""
    X = np.asarray(X, float)
    n = X.shape[0]
    sigma = rng.choice([-1.0, 1.0], size=(n_sigma, n))
    return float(B * np.mean(np.linalg.norm(sigma @ X, axis=1)) / n)


def rademacher_linear_bound(X: np.ndarray, B: float) -> float:
    """B * sqrt(sum ||x_i||^2) / n <= B R / sqrt(n) with R = max ||x_i||."""
    X = np.asarray(X, float)
    return float(B * math.sqrt(np.sum(X**2)) / X.shape[0])


def rademacher_vc_bound(d: int, n: int) -> float:
    """From Massart + Sauer: R_n(H) <= sqrt(2 d log(e n / d) / n)."""
    return math.sqrt(2 * d * math.log(math.e * n / d) / n)


def generalisation_bound(emp_risk: float, rad: float, n: int, delta: float) -> float:
    """L_D(h) <= L_S(h) + 2 R_S + 3 sqrt(log(2/delta) / (2n)) for losses in [0,1]."""
    return emp_risk + 2 * rad + 3 * math.sqrt(math.log(2 / delta) / (2 * n))


def rademacher_bound_experiment(problem: ThresholdProblem, n: int, delta: float, trials: int,
                                n_sigma: int, rng: np.random.Generator):
    """Theorem 5.3 for all thresholds with 0-1 loss, over `trials` resamples.

    Returns (gaps, slacks): gaps = sup_t (L_D - L_S) (exact), slacks = the
    data-dependent bound 2 R_S(l o H) + 3 sqrt(log(2/delta)/(2n)) with
    R_S(l o H) = R_S(H) / 2. The theorem says P(gap > slack) <= delta.
    """
    gaps, slacks = np.empty(trials), np.empty(trials)
    for j in range(trials):
        X, y = problem.sample(n, rng)
        gaps[j] = threshold_sup_deviation(problem, X, y)[1]
        slacks[j] = generalisation_bound(0.0, rademacher_threshold(X, n_sigma, rng) / 2, n, delta)
    return gaps, slacks


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    print("Worked example, thresholds on 2 points: exact R_S =",
          empirical_rademacher_exact(threshold_predictions(np.array([0.2, 0.8]))))
    print("\nThresholds on n uniform points (VC dim 1):")
    for n in (2, 10, 100, 1000):
        X = rng.uniform(size=n)
        r = rademacher_threshold(X, 4000, rng)
        print(f"  n={n:5d}  R_S = {r:.4f}  Massart {massart_bound(n + 1, n):.4f}"
              f"  VC bound {rademacher_vc_bound(1, n):.4f}")
    print("\nTheorem 5.7, linear class ||w||<=1 on unit-norm points in R^d, n=100:")
    for d in (2, 20, 200):
        X = rng.normal(size=(100, d))
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        r = rademacher_linear_exact(X, 1.0, 4000, rng)
        print(f"  d={d:4d}  R_S = {r:.4f}  bound BR/sqrt(n) = {rademacher_linear_bound(X, 1.0):.4f}"
              f"  (dimension-free)")
    delta = 0.05
    print(f"\nTheorem 5.3, all thresholds, eta=0.1, delta={delta}, 500 resamples:")
    print(f"{'n':>6} {'95% quantile sup(L_D-L_S)':>26} {'mean bound':>11} {'P(gap > bound)':>15}")
    for n in (50, 200, 1000):
        gaps, slacks = rademacher_bound_experiment(ThresholdProblem(0.3, 0.1), n, delta, 500, 200, rng)
        print(f"{n:6d} {np.quantile(gaps, 1 - delta):26.4f} {slacks.mean():11.4f}"
              f" {np.mean(gaps > slacks):15.4f}")
