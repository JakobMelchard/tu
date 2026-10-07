"""Concentration inequalities and finite-class uniform convergence.

Note 02 (finite classes and concentration), section Results:
- Theorems 2.1, 2.2: Markov, Chebyshev (`markov_bound`, `chebyshev_bound`).
- Theorem 2.4: Hoeffding, P(|mean - p| >= eps) <= 2 exp(-2 n eps^2) (`hoeffding_bound`),
  checked against the exact binomial tail (`binomial_tail_exact`).
- Theorem 2.6: finite classes have uniform convergence with
  eps(n) = sqrt(log(2|H|/delta) / (2n)) (`epsilon_from_n`); reproduced over many
  resamples by `uniform_deviation_finite`.
- Theorem 2.7: realisable case, n >= log(|H|/delta) / eps (`sample_complexity_finite`).

Run `python concentration.py [--png]`.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.stats import binom

from framework import ThresholdProblem, finite_threshold_class, threshold_empirical_risks


def hoeffding_bound(n: int, eps: float, a: float = 0.0, b: float = 1.0) -> float:
    """Two-sided Hoeffding: P(|mean - E| >= eps) <= 2 exp(-2 n eps^2 / (b-a)^2)."""
    return 2.0 * math.exp(-2.0 * n * eps**2 / (b - a) ** 2)


def binomial_tail_exact(p: float, n: int, eps: float) -> float:
    """Exact P(|Bin(n,p)/n - p| >= eps), the quantity Hoeffding bounds."""
    k = np.arange(n + 1)
    return float(binom.pmf(k, n, p)[np.abs(k / n - p) >= eps - 1e-12].sum())


def hoeffding_empirical(p: float, n: int, eps: float, trials: int,
                        rng: np.random.Generator) -> float:
    """Fraction of trials in which the mean of n Bernoulli(p) deviates by >= eps."""
    means = rng.binomial(n, p, size=trials) / n
    return float(np.mean(np.abs(means - p) >= eps - 1e-12))


def union_bound_experiment(n_hyps: int, n: int, eps: float, trials: int,
                           rng: np.random.Generator, p: float = 0.5):
    """Probability that SOME of n_hyps independent empirical means deviates by >= eps.

    Compares the observed frequency with the union bound n_hyps * hoeffding_bound.
    Returns (observed, union_bound, single_hoeffding).
    """
    means = rng.binomial(n, p, size=(trials, n_hyps)) / n
    some_bad = np.any(np.abs(means - p) >= eps - 1e-12, axis=1)
    single = hoeffding_bound(n, eps)
    return float(np.mean(some_bad)), min(1.0, n_hyps * single), single


def sample_complexity_finite(size_H: int, eps: float, delta: float,
                             realisable: bool = False) -> int:
    """Smallest n guaranteeing (eps, delta)-success of ERM over a finite class.

    realisable (Thm 2.7): n >= log(|H|/delta) / eps
    agnostic   (Thm 2.6): n >= log(2|H|/delta) / (2 eps^2)
    """
    if realisable:
        return math.ceil(math.log(size_H / delta) / eps)
    return math.ceil(math.log(2 * size_H / delta) / (2 * eps**2))


def epsilon_from_n(n: int, size_H: int, delta: float, realisable: bool = False) -> float:
    """Invert sample_complexity_finite: the accuracy guaranteed by n samples."""
    if realisable:
        return math.log(size_H / delta) / n
    return math.sqrt(math.log(2 * size_H / delta) / (2 * n))


def uniform_deviation_finite(problem: ThresholdProblem, k: int, n: int, trials: int,
                             rng: np.random.Generator) -> np.ndarray:
    """sup_{h in H_k} |L_S(h) - L_D(h)| for `trials` independent samples.

    H_k = `finite_threshold_class(k)`; L_D is the closed form of Proposition 1.5,
    so the supremum is exact. Theorem 2.6 says its (1-delta)-quantile is
    <= epsilon_from_n(n, k, delta).
    """
    hyps = finite_threshold_class(k)
    LD = problem.risk(hyps)
    out = np.empty(trials)
    for j in range(trials):
        X, y = problem.sample(n, rng)
        out[j] = np.max(np.abs(threshold_empirical_risks(X, y, hyps) - LD))
    return out


def markov_bound(mean: float, a: float) -> float:
    return mean / a


def chebyshev_bound(var: float, eps: float) -> float:
    return var / eps**2


if __name__ == "__main__":
    import sys
    rng = np.random.default_rng(0)
    print("Theorem 2.4, fair coin, eps = 0.1 (100 000 resamples per n):")
    ns = (10, 20, 50, 100, 200, 500)
    obs_all = []
    for n in ns:
        obs = hoeffding_empirical(0.5, n, 0.1, 100_000, rng)
        obs_all.append(obs)
        print(f"  n={n:4d}  observed {obs:.4f}  exact {binomial_tail_exact(0.5, n, 0.1):.4f}"
              f"  Hoeffding {hoeffding_bound(n, 0.1):.4f}"
              f"  Chebyshev {min(1, chebyshev_bound(0.25 / n, 0.1)):.4f}")
    if "--png" in sys.argv:
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        plt.semilogy(ns, [max(o, 1e-5) for o in obs_all], "o-", label="observed")
        plt.semilogy(ns, [hoeffding_bound(n, 0.1) for n in ns], "s--", label="Hoeffding")
        plt.semilogy(ns, [min(1, chebyshev_bound(0.25 / n, 0.1)) for n in ns], "^:", label="Chebyshev")
        plt.xlabel("n"); plt.ylabel("P(|mean-1/2| >= 0.1)"); plt.legend()
        plt.savefig("hoeffding.png", dpi=120); print("saved hoeffding.png")
    print("\nUnion bound over m independent means, n=100, eps=0.1:")
    for m in (1, 10, 100, 1000):
        obs, ub, single = union_bound_experiment(m, 100, 0.1, 20_000, rng)
        print(f"  m={m:5d}  observed {obs:.4f}  union bound {ub:.4f}")
    delta, k = 0.05, 50
    print(f"\nTheorem 2.6, |H|={k} thresholds, eta=0.1, delta={delta}, 2000 resamples:")
    print(f"{'n':>6} {'95% quantile of sup gap':>24} {'eps(n) bound':>13} {'P(sup gap > eps)':>17}")
    for n in (50, 200, 1000):
        gaps = uniform_deviation_finite(ThresholdProblem(0.3, 0.1), k, n, 2000, rng)
        eps = epsilon_from_n(n, k, delta)
        print(f"{n:6d} {np.quantile(gaps, 1 - delta):24.4f} {eps:13.4f} {np.mean(gaps > eps):17.4f}")
    print("\nSample complexity, |H|=1000, delta=0.05:")
    for eps in (0.1, 0.05, 0.01):
        print(f"  eps={eps}: realisable n={sample_complexity_finite(1000, eps, 0.05, True):7d}"
              f"  agnostic n={sample_complexity_finite(1000, eps, 0.05, False):8d}")
