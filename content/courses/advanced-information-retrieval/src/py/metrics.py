"""Ranking metrics and significance tests.

Note 04. Definitions as in the lecture [S7 sl. 14-30]: MRR on the first
relevant rank, AP normalised by the number of relevant documents of the query
(not by the number retrieved), nDCG with linear gain $rel/\\log_2(i+1)$ and the
ideal DCG from all judged grades of the query [S25]. `exp_gain=True` gives the
$2^{rel}-1$ gain popularised by Burges et al. [S49]; tools differ in their default.

Significance: paired t-test by hand (cross-checked with scipy), paired
randomisation (permutation) test, Bonferroni correction [S7 sl. 29-30, S26].
Kendall's tau for comparing two system orderings (note 13).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence

import numpy as np
from scipy import stats


def precision_at_k(ranking: Sequence[str], relevant: set[str], k: int) -> float:
    return sum(d in relevant for d in ranking[:k]) / k


def recall_at_k(ranking: Sequence[str], relevant: set[str], k: int) -> float:
    return sum(d in relevant for d in ranking[:k]) / len(relevant) if relevant else 0.0


def reciprocal_rank(ranking: Sequence[str], relevant: set[str], k: int | None = None) -> float:
    for i, d in enumerate(ranking[:k] if k else ranking, 1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def average_precision(ranking: Sequence[str], relevant: set[str], k: int | None = None) -> float:
    """(1/|rel(q)|) sum_i P@i rel_i; relevant documents never retrieved contribute 0."""
    if not relevant:
        return 0.0
    hits, s = 0, 0.0
    for i, d in enumerate(ranking[:k] if k else ranking, 1):
        if d in relevant:
            hits += 1
            s += hits / i
    return s / len(relevant)


def dcg(gains: Iterable[float], k: int | None = None, exp_gain: bool = False) -> float:
    g = list(gains)[:k] if k else list(gains)
    return sum(((2**x - 1) if exp_gain else x) / math.log2(i + 1) for i, x in enumerate(g, 1))


def ndcg_at_k(ranking: Sequence[str], grades: dict[str, int], k: int = 10, exp_gain: bool = False) -> float:
    """Unjudged documents get grade 0. Ideal ranking = all judged grades sorted descending."""
    ideal = dcg(sorted(grades.values(), reverse=True), k, exp_gain)
    return dcg([grades.get(d, 0) for d in ranking], k, exp_gain) / ideal if ideal > 0 else 0.0


def mean_metric(fn: Callable[[str], float], qids: Iterable[str]) -> float:
    vals = [fn(q) for q in qids]
    return float(np.mean(vals)) if vals else 0.0


def per_query(fn: Callable[[str], float], qids: Sequence[str]) -> np.ndarray:
    return np.array([fn(q) for q in qids], dtype=float)


def paired_t_test(a: Sequence[float], b: Sequence[float]) -> tuple[float, float]:
    """H0: mean per-query difference is 0. t = mean(d) / (sd(d)/sqrt(n)), df = n-1, two-sided p."""
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d)
    sd = d.std(ddof=1)
    if sd == 0:
        return (math.inf if d.mean() else 0.0), (0.0 if d.mean() else 1.0)
    t = d.mean() / (sd / math.sqrt(n))
    return float(t), float(2 * stats.t.sf(abs(t), n - 1))


def randomisation_test(a: Sequence[float], b: Sequence[float], n_perm: int = 20000,
                       rng: np.random.Generator | None = None) -> float:
    """Paired permutation test: under H0 the labels A/B are exchangeable per query,
    so flip the sign of each difference at random; p = P(|mean| >= observed)."""
    rng = rng or np.random.default_rng(0)
    d = np.asarray(a, float) - np.asarray(b, float)
    obs = abs(d.mean())
    signs = rng.choice([-1.0, 1.0], size=(n_perm, len(d)))
    null = np.abs((signs * d).mean(1))
    return float((np.sum(null >= obs - 1e-12) + 1) / (n_perm + 1))


def bonferroni(pvals: Sequence[float]) -> list[float]:
    """Adjusted p-values min(1, m p): equivalent to testing each at alpha/m [S7 sl. 30]."""
    m = len(pvals)
    return [min(1.0, m * p) for p in pvals]


def kendall_tau(x: Sequence[float], y: Sequence[float]) -> float:
    """Tau-a over all pairs: (concordant - discordant) / (n choose 2)."""
    n, s = len(x), 0
    for i in range(n):
        for j in range(i + 1, n):
            s += np.sign(x[i] - x[j]) * np.sign(y[i] - y[j])
    return float(s / (n * (n - 1) / 2))


if __name__ == "__main__":
    # the three systems of [S7 sl. 18, 20, 27]: two relevant docs x (grade 3) and y (grade 1)
    rel, grades = {"x", "y"}, {"x": 3, "y": 1}
    runs = {"A": ["y", "n1", "x"], "B": ["n1", "n2", "y"], "C": ["n1", "x", "y"]}
    for s, r in runs.items():
        print(f"system {s}: RR {reciprocal_rank(r, rel):.3f}  AP {average_precision(r, rel):.3f}  "
              f"nDCG {ndcg_at_k(r, grades, 10):.3f}  P@3 {precision_at_k(r, rel, 3):.3f}")
    a, b = [0.5, 0.6, 0.7, 0.4], [0.4, 0.5, 0.5, 0.4]
    t, p = paired_t_test(a, b)
    print(f"paired t-test on 4 queries: t = {t:.3f}, p = {p:.4f}; randomisation p = {randomisation_test(a, b):.4f}")
    rng = np.random.default_rng(1)
    base = rng.beta(2, 3, 50)
    better = np.clip(base + rng.normal(0.03, 0.08, 50), 0, 1)
    t, p = paired_t_test(better, base)
    print(f"50 queries, +{np.mean(better - base):.3f} mean AP: t = {t:.2f}, p = {p:.4f}; "
          f"x10 comparisons, Bonferroni p = {bonferroni([p] * 10)[0]:.4f}")
