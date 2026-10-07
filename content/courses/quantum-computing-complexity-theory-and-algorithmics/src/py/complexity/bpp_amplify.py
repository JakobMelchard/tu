"""Error amplification for BPP (majority vote) and RP (repeat, accept if any accepts).

Belongs to the complexity note B05 (probabilistic classes).

Implements: majority_vote (k independent runs of a base algorithm with success
probability p > 1/2), chernoff_bound exp(-2k(p-1/2)^2) (Hoeffding form),
exact_majority_error via the binomial tail, empirical_error (numpy RNG simulation),
repetitions_needed(p, target) from the Chernoff bound, rp_amplify (one-sided:
k repetitions push the false-negative rate from 1-p to (1-p)^k).
"""
import math

import numpy as np
from scipy.stats import binom


def chernoff_bound(k, p):
    """Pr[majority of k Bernoulli(p) trials is wrong] <= exp(-2 k (p - 1/2)^2).

    Hoeffding: for X = sum of k indicators with mean kp, Pr[X <= k/2] =
    Pr[X - kp <= -k(p-1/2)] <= exp(-2 (k(p-1/2))^2 / k)."""
    return math.exp(-2 * k * (p - 0.5) ** 2)


def exact_majority_error(k, p):
    """Pr[at most floor(k/2) successes] -- a tie counts as an error (k odd avoids it)."""
    return float(binom.cdf(k // 2, k, p))


def majority_vote(base, k, rng):
    """Run base(rng) k times (each returns True on the correct answer); return the majority."""
    votes = sum(bool(base(rng)) for _ in range(k))
    return votes > k / 2


def empirical_error(p, k, trials, rng):
    """Vectorised: trials majority votes of k Bernoulli(p) coins; fraction of wrong votes."""
    correct = rng.random((trials, k)) < p
    return float(np.mean(correct.sum(axis=1) <= k / 2))


def repetitions_needed(p, target_error):
    """Smallest odd k with exp(-2k(p-1/2)^2) <= target_error.

    From 2/3 to 1 - 2^-s: k >= s ln 2 / (2 (1/6)^2) = 18 s ln 2 ~ 12.5 s."""
    k = math.ceil(math.log(1 / target_error) / (2 * (p - 0.5) ** 2))
    return k + 1 if k % 2 == 0 else k


def rp_amplify(base, k, rng):
    """RP: base never accepts a no-instance, accepts a yes-instance w.p. >= p.
    Accept iff any of k runs accepts: error on yes-instances drops to (1-p)^k."""
    return any(base(rng) for _ in range(k))


def rp_error(k, p):
    return (1 - p) ** k


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    p = 2 / 3
    print(f"base success p = {p:.3f}; majority vote of k runs")
    print(f"{'k':>4} {'empirical':>10} {'exact tail':>11} {'Chernoff':>10}")
    for k in (1, 3, 5, 11, 21, 51, 101):
        print(f"{k:>4} {empirical_error(p, k, 20000, rng):>10.4f} "
              f"{exact_majority_error(k, p):>11.2e} {chernoff_bound(k, p):>10.2e}")
    for s in (10, 20, 50):
        print(f"error 2^-{s} needs k = {repetitions_needed(p, 2 ** -s)} (Chernoff), "
              f"exact tail then {exact_majority_error(repetitions_needed(p, 2 ** -s), p):.2e}")
    print("RP: p=1/2, k=20 ->", rp_error(20, 0.5))
