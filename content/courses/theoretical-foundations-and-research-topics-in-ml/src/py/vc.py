"""VC dimension: shattering, growth functions, Sauer-Shelah, VC bounds.

Note 04 (VC dimension), section Results:
- Theorems 4.1-4.3, 4.5: VCdim of thresholds 1, intervals 2, rectangles 4,
  halfspaces in R^k k+1 (homogeneous: k), by brute-force shattering.
- Theorem 4.8 / Lemma 4.9: Sauer-Shelah, tau_H(n) <= sum_{i<=d} C(n,i) <= (en/d)^d.
- Theorem 4.10: E sup_h |L_D(h) - L_S(h)| <= (4 + sqrt(log tau_H(2n))) / sqrt(2n),
  plus the McDiarmid high-probability form; Theorem 4.12: the Vapnik-style form.
  `vc_bound_experiment` computes the exact sup over ALL thresholds on many
  resamples (`threshold_sup_deviation`) and compares with these bounds.

A hypothesis class is represented by a function `labelings(points) -> set of
tuples in {-1,+1}^n`: all dichotomies of the given point set that the class
can realise. This is enough to test shattering and to compute the growth
function on concrete point sets.

Run `python vc.py`.
"""
from __future__ import annotations

import itertools
import math

import numpy as np
from scipy.optimize import linprog

from framework import ThresholdProblem, threshold_empirical_risks


def _labels(mask):
    return tuple(1 if m else -1 for m in mask)


def threshold_labelings(points: np.ndarray) -> set:
    """Thresholds on R: h_t(x) = sign(x - t). Realisable dichotomies = prefixes in sorted order."""
    x = np.asarray(points, dtype=float).ravel()
    out = set()
    cuts = np.concatenate([[-np.inf], np.sort(x)])
    for t in cuts:
        out.add(_labels(x > t))
    return out


def interval_labelings(points: np.ndarray) -> set:
    """Intervals on R: +1 inside [a,b], -1 outside (including the empty interval)."""
    x = np.asarray(points, dtype=float).ravel()
    xs = np.sort(x)
    out = {_labels(np.zeros(len(x), bool))}
    for i in range(len(xs)):
        for j in range(i, len(xs)):
            out.add(_labels((x >= xs[i]) & (x <= xs[j])))
    return out


def rectangle_labelings(points: np.ndarray) -> set:
    """Axis-aligned rectangles in R^2: +1 inside. Corners can be chosen among the coordinates."""
    P = np.asarray(points, dtype=float)
    xs, ys = np.unique(P[:, 0]), np.unique(P[:, 1])
    out = {_labels(np.zeros(len(P), bool))}
    for x0, x1 in itertools.combinations_with_replacement(xs, 2):
        for y0, y1 in itertools.combinations_with_replacement(ys, 2):
            inside = (P[:, 0] >= x0) & (P[:, 0] <= x1) & (P[:, 1] >= y0) & (P[:, 1] <= y1)
            out.add(_labels(inside))
    return out


def _halfspace_realisable(P: np.ndarray, y: np.ndarray, homogeneous: bool) -> bool:
    """LP feasibility: exists w (and b) with y_i (w.x_i + b) >= 1 for all i."""
    n, d = P.shape
    A = -(y[:, None] * P)
    if not homogeneous:
        A = np.hstack([A, -y[:, None]])
    m = A.shape[1]
    res = linprog(np.zeros(m), A_ub=A, b_ub=-np.ones(n), bounds=[(None, None)] * m,
                  method="highs")
    return res.status == 0


def halfspace_labelings(points: np.ndarray, homogeneous: bool = False) -> set:
    """Halfspaces in R^d, decided by an LP for each of the 2^n candidate dichotomies."""
    P = np.asarray(points, dtype=float)
    out = set()
    for signs in itertools.product([-1, 1], repeat=len(P)):
        y = np.array(signs, dtype=float)
        if _halfspace_realisable(P, y, homogeneous):
            out.add(tuple(signs))
    return out


def is_shattered(labelings, points) -> bool:
    return len(labelings(points)) == 2 ** len(points)


def growth_function(labelings, sampler, n: int, trials: int, rng: np.random.Generator) -> int:
    """Lower bound on tau_H(n): max over random point sets of |H restricted to C|."""
    return max(len(labelings(sampler(n, rng))) for _ in range(trials))


def vc_dimension_estimate(labelings, sampler, max_d: int, trials: int,
                          rng: np.random.Generator) -> int:
    """Largest n <= max_d for which some sampled set of n points is shattered."""
    d = 0
    for n in range(1, max_d + 1):
        if any(is_shattered(labelings, sampler(n, rng)) for _ in range(trials)):
            d = n
        else:
            break
    return d


def sauer_bound(d: int, n: int) -> int:
    """sum_{i=0}^{d} C(n, i)."""
    return sum(math.comb(n, i) for i in range(min(d, n) + 1))


def sauer_upper_estimate(d: int, n: int) -> float:
    """(e n / d)^d, valid for n >= d >= 1."""
    return (math.e * n / d) ** d


def verify_sauer(labelings, sampler, d: int, n_max: int, trials: int,
                 rng: np.random.Generator) -> bool:
    return all(growth_function(labelings, sampler, n, trials, rng) <= sauer_bound(d, n)
               for n in range(1, n_max + 1))


# Uniform convergence for thresholds (Theorems 4.10, 4.12) --------------------

def threshold_sup_deviation(problem: ThresholdProblem, X: np.ndarray, y: np.ndarray):
    """Exact (sup_t |L_D(h_t) - L_S(h_t)|, sup_t (L_D(h_t) - L_S(h_t))) over all t in [0,1].

    L_S is constant on each [x_(i), x_(i+1)); L_D = eta + (1-2eta)|t-theta| is
    convex there, so both suprema are attained at an endpoint or at t = theta.
    """
    edges = np.concatenate([[0.0], np.sort(X), [1.0]])
    lo, hi = edges[:-1], edges[1:]
    LS = threshold_empirical_risks(X, y, lo)
    inside = (lo <= problem.theta) & (problem.theta <= hi)
    mid = np.where(inside, problem.risk(problem.theta), problem.risk(lo))
    D = np.stack([problem.risk(lo), problem.risk(hi), mid]) - LS
    return float(np.max(np.abs(D))), float(np.max(D))


def uc_bound_expectation(tau_2n: int, n: int) -> float:
    """Theorem 4.10: (4 + sqrt(log tau_H(2n))) / sqrt(2n) bounds E sup_h |L_D - L_S|."""
    return (4 + math.sqrt(math.log(tau_2n))) / math.sqrt(2 * n)


def uc_bound_mcdiarmid(tau_2n: int, n: int, delta: float) -> float:
    """Theorem 4.10 + McDiarmid (c_i = 1/n): holds with probability >= 1 - delta."""
    return uc_bound_expectation(tau_2n, n) + math.sqrt(math.log(1 / delta) / (2 * n))


def vc_bound_vapnik(d: int, n: int, delta: float) -> float:
    """Theorem 4.12: sqrt((8 d log(2en/d) + 8 log(4/delta)) / n), n >= d."""
    return math.sqrt((8 * d * math.log(2 * math.e * n / d) + 8 * math.log(4 / delta)) / n)


def vc_bound_experiment(problem: ThresholdProblem, n: int, trials: int,
                        rng: np.random.Generator) -> np.ndarray:
    """sup_t |L_D(h_t) - L_S(h_t)| on `trials` independent samples of size n."""
    return np.array([threshold_sup_deviation(problem, *problem.sample(n, rng))[0]
                     for _ in range(trials)])


# Point samplers --------------------------------------------------------------

def sample_line(n, rng):
    return rng.uniform(size=n)


def sample_plane(n, rng):
    return rng.uniform(size=(n, 2))


def sample_plane_circle(n, rng):
    """Points in convex position: the hardest configuration for halfspaces/rectangles."""
    a = np.sort(rng.uniform(0, 2 * np.pi, size=n))
    return np.stack([np.cos(a), np.sin(a)], axis=1)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    classes = {
        "thresholds": (threshold_labelings, sample_line),
        "intervals": (interval_labelings, sample_line),
        "rectangles": (rectangle_labelings, sample_plane),
        "halfspaces R^2": (halfspace_labelings, sample_plane),
    }
    for name, (lab, samp) in classes.items():
        d = vc_dimension_estimate(lab, samp, 6, 60, rng)
        tau = [growth_function(lab, samp, n, 30, rng) for n in range(1, 7)]
        sauer = [sauer_bound(d, n) for n in range(1, 7)]
        print(f"{name:16s} VC dim estimate {d}  tau(1..6) = {tau}  Sauer = {sauer}")
    diamond = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
    print("rectangles shatter the diamond:", is_shattered(rectangle_labelings, diamond))
    print("halfspaces shatter 4 points on a circle:",
          is_shattered(halfspace_labelings, sample_plane_circle(4, rng)))
    delta, prob = 0.05, ThresholdProblem(0.3, 0.1)
    print(f"\nTheorems 4.10/4.12, all thresholds (d=1, tau(2n)=2n+1), eta=0.1, delta={delta}, "
          "1000 resamples:")
    print(f"{'n':>6} {'E sup gap':>10} {'Thm 4.10 E':>11} {'95% quantile':>13}"
          f" {'4.10+McDiarmid':>15} {'Thm 4.12':>9}")
    for n in (50, 200, 1000):
        gaps = vc_bound_experiment(prob, n, 1000, rng)
        print(f"{n:6d} {gaps.mean():10.4f} {uc_bound_expectation(2 * n + 1, n):11.4f}"
              f" {np.quantile(gaps, 1 - delta):13.4f} {uc_bound_mcdiarmid(2 * n + 1, n, delta):15.4f}"
              f" {vc_bound_vapnik(1, n, delta):9.4f}")
