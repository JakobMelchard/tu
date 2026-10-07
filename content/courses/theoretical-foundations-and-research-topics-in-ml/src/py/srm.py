"""Structural risk minimisation over nested finite classes, with exact risks.

Note 06 (regularisation and SRM), section Results:
- Definition 4 (SRM rule) with weights w_k = 6/(pi^2 k^2), sum_k w_k = 1.
- Theorem 6.1: with prob >= 1-delta, for all k and all h in H_k simultaneously,
  |L_D(h) - L_S(h)| <= eps_k(n, w_k delta).
- Theorem 6.2: with prob >= 1-delta, L_D(h_SRM) <= L_D(h*) + 2 eps_{k(h*)}(n, w_{k(h*)} delta)
  for every h*, i.e. L_D(h_SRM) <= min_k [min_{H_k} L_D + 2 eps_k].

Classes: H_k = thresholds on the dyadic grid {j / 2^k : j = 0..2^k}, nested,
|H_k| = 2^k + 1. eps_k is the finite-class uniform-convergence accuracy of
note 02, Theorem 2.6: eps_k(n, d) = sqrt(log(2|H_k| / d) / (2n)). The data are
note 01's noisy thresholds with theta off the grid, so the approximation error
(1-2eta) dist(theta, grid_k) decreases with k and SRM must trade it against eps_k.
All risks are closed-form (Proposition 1.5), so both theorems are checked
exactly on every resample. regularisation.py has the polynomial SRM demo, whose
penalty is only a heuristic; this module is the version with a proven bound.

Run `python srm.py`.
"""
from __future__ import annotations

import math

import numpy as np

from framework import ThresholdProblem, threshold_empirical_risks


def dyadic_class(k: int) -> np.ndarray:
    """H_k: thresholds j / 2^k, j = 0..2^k. H_1 subset H_2 subset ..."""
    return np.arange(2**k + 1) / 2**k


def srm_weight(k: int) -> float:
    """w_k = 6 / (pi^2 k^2), k >= 1; sum_{k>=1} w_k = 1 (Basel)."""
    return 6.0 / (math.pi**2 * k**2)


def uc_epsilon(size: int, n: int, delta: float) -> float:
    """Theorem 2.6 accuracy for a finite class: sqrt(log(2 |H| / delta) / (2n))."""
    return math.sqrt(math.log(2 * size / delta) / (2 * n))


def srm_penalties(n: int, K: int, delta: float) -> np.ndarray:
    """eps_k(n, w_k delta) for k = 1..K."""
    return np.array([uc_epsilon(2**k + 1, n, srm_weight(k) * delta) for k in range(1, K + 1)])


def srm_threshold_select(X: np.ndarray, y: np.ndarray, K: int, delta: float):
    """SRM over H_1..H_K: minimise L_S(h) + eps_{k(h)} (Definition 4).

    Since the classes are nested and eps_k increases with k, it suffices to run
    ERM in each H_k and pick k minimising L_S(h_k) + eps_k. Returns (k*, t*).
    """
    pen = srm_penalties(len(X), K, delta)
    best = (np.inf, None, None)
    for k in range(1, K + 1):
        H = dyadic_class(k)
        risks = threshold_empirical_risks(X, y, H)
        i = int(np.argmin(risks))
        score = risks[i] + pen[k - 1]
        if score < best[0]:
            best = (score, k, float(H[i]))
    return best[1], best[2]


def srm_experiment(problem: ThresholdProblem, n: int, K: int, delta: float, trials: int,
                   rng: np.random.Generator):
    """Checks Theorems 6.1 and 6.2 on `trials` resamples.

    Returns a dict with
      viol_61: fraction of samples where some h in some H_k has |L_D - L_S| > eps_k,
      viol_62: fraction where L_D(h_SRM) > min_k [min_{H_k} L_D + 2 eps_k],
      LD_srm, LD_erm_K: mean true risk of SRM and of plain ERM over H_K,
      k_mean: mean selected k, oracle: min_k [min_{H_k} L_D + 2 eps_k].
    """
    pen = srm_penalties(n, K, delta)
    classes = [dyadic_class(k) for k in range(1, K + 1)]
    LD = [problem.risk(H) for H in classes]
    oracle = min(float(LD[k].min()) + 2 * pen[k] for k in range(K))
    v61 = v62 = 0
    ld_srm, ld_erm, ks = [], [], []
    for _ in range(trials):
        X, y = problem.sample(n, rng)
        LS = [threshold_empirical_risks(X, y, H) for H in classes]
        v61 += any(np.max(np.abs(LS[k] - LD[k])) > pen[k] for k in range(K))
        k_star, t_star = srm_threshold_select(X, y, K, delta)
        r = float(problem.risk(t_star))
        v62 += r > oracle
        ld_srm.append(r); ks.append(k_star)
        ld_erm.append(float(LD[-1][int(np.argmin(LS[-1]))]))
    return {"viol_61": v61 / trials, "viol_62": v62 / trials, "LD_srm": float(np.mean(ld_srm)),
            "LD_erm_K": float(np.mean(ld_erm)), "k_mean": float(np.mean(ks)), "oracle": oracle}


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    K, delta = 12, 0.05
    prob = ThresholdProblem(theta=0.3, eta=0.1)   # 0.3 is not dyadic: every H_k is misspecified
    print(f"SRM over dyadic thresholds H_1..H_{K}, theta=0.3, eta=0.1, delta={delta}, 300 resamples")
    print("approximation error min_{H_k} L_D - L*: "
          + " ".join(f"{float(prob.risk(dyadic_class(k)).min()) - prob.eta:.4f}" for k in (1, 2, 4, 8)))
    print(f"{'n':>6} {'mean k*':>8} {'L_D(SRM)':>9} {'L_D(ERM H_K)':>13} {'Thm 6.2 bound':>14}"
          f" {'P(6.1 fails)':>13} {'P(6.2 fails)':>13}")
    for n in (30, 100, 300, 1000, 3000):
        r = srm_experiment(prob, n, K, delta, 300, rng)
        print(f"{n:6d} {r['k_mean']:8.2f} {r['LD_srm']:9.4f} {r['LD_erm_K']:13.4f} {r['oracle']:14.4f}"
              f" {r['viol_61']:13.4f} {r['viol_62']:13.4f}")
    print("ERM over H_K wins here: log|H_K| overstates the complexity of thresholds (VCdim 1);\n"
          "SRM pays the worst-case penalty of each H_k but still learns without knowing k.")
    print(f"sum of weights k=1..{K}: {sum(srm_weight(k) for k in range(1, K + 1)):.4f} (<= 1)")
