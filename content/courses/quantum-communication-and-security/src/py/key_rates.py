"""Key rates: Shor-Preskill, Devetak-Winter for BB84, decoy-state rate vs distance, and the
Tomamichel-Leverrier finite-key length.

Note 05 (security proofs), note 06 (imperfections):
- Shor-Preskill r = 1 - 2 h(e), threshold e* = 11.00 % (`shor_preskill`, `sp_threshold`) [S7].
- Devetak-Winter r = I(A:B) - chi(A:E) = H(Z|E) - H(Z|B) [S14, S4 Cor. 6.5.2], evaluated on
  the Bell-diagonal state with Eve holding the purification (`devetak_winter_bell_diagonal`,
  `holevo_eve`). For e_Z = e_X = e the minimum over the unobserved weight lambda_Psi- is at
  lambda_Psi- = e^2 and equals 1 - 2h(e) (`devetak_winter_bb84_min`).
- Asymptotic decoy-state BB84 rate vs distance for a detector/channel `Channel`, with the
  signal intensity optimised per distance (`decoy_rate_curve`); single-photon source reference
  R = q eta (1 - 2h(e)) with QBER from the same detector model (`single_photon_rate`).
- Finite key [S5 Thms 2, 3]: with block m, k test rounds, tolerance delta, leak r = f n h(delta),
  hash t, c = 1/2 (BB84),
      eps_pe = 2 exp(-(m-k) k^2 nu^2 / (m (k+1))),   eps_ec = 2^-t,
      eps_pa = 1/2 sqrt(2^{-(m-k)(log 1/c - h(delta+nu)) + r + t + l}),
  and eps = eps_ec + eps_pe + eps_pa. `finite_key_length` maximises l over k, nu and the split.

Run `python key_rates.py`.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import brentq

from decoy import GYS, Channel, best_mu, max_distance, rate_decoy
from entropies import bb84_lams, h2, h_z_given_e


def shor_preskill(e):
    return 1 - 2 * h2(e)


def sp_threshold() -> float:
    return brentq(lambda e: 1 - 2 * h2(e), 0.05, 0.2, xtol=1e-12)


def devetak_winter_bell_diagonal(lams) -> float:
    """H(Z|E) - H(Z|B) for the Bell-diagonal state (one-way reconciliation from Alice)."""
    e_z = lams[2] + lams[3]
    return h_z_given_e(lams) - h2(e_z)


def holevo_eve(lams) -> float:
    """chi(Z:E) = H(Z) - H(Z|E) with H(Z) = 1 (Alice's key bit is uniform)."""
    return 1.0 - h_z_given_e(lams)


def devetak_winter_bb84_min(e: float, grid: int = 201) -> tuple[float, float]:
    """min over lambda_Psi- in [0, e] of the DW rate at e_Z = e_X = e; returns (rate, argmin)."""
    ls = np.linspace(0, e, grid)
    rates = [devetak_winter_bell_diagonal(bb84_lams(e, e, l)) for l in ls]
    i = int(np.argmin(rates))
    return float(rates[i]), float(ls[i])


def decoy_rate_curve(Ls, ch: Channel = GYS, nu: float | None = None) -> list[tuple[float, float, float]]:
    """[(L, mu*, R(L, mu*))] with mu optimised per distance (nu=None: infinite decoys)."""
    out = []
    for L in Ls:
        mu, r = best_mu(lambda LL, m: rate_decoy(LL, m, ch, nu), L, lo=1e-3, hi=1.0)
        out.append((float(L), mu, max(r, 0.0)))
    return out


def single_photon_rate(L: float, ch: Channel = GYS) -> float:
    """Ideal single-photon source with the same channel and detectors: q Y1 (1 - (1+f) h(e1))."""
    y1, e1 = ch.yield_i(1, L), ch.error_i(1, L)
    return ch.q * y1 * max(0.0, 1 - h2(e1) - ch.f * h2(e1))


def finite_key_length(m: int, delta: float, eps: float = 1e-10, f_ec: float = 1.1,
                      log_inv_c: float = 1.0) -> tuple[int, dict]:
    """Largest l for an eps-secure BB84 block of m rounds [S5 Eq. (58)]. Returns (l, parameters)."""
    best = (0, {})
    for frac_k in np.geomspace(1e-5, 0.5, 70):
        k = max(1, int(frac_k * m))
        n = m - k
        for s_ec, s_pe in [(0.1, 0.45), (0.2, 0.4), (0.05, 0.5), (0.1, 0.6), (0.3, 0.35), (0.1, 0.3)]:
            e_ec, e_pe = s_ec * eps, s_pe * eps
            e_pa = eps - e_ec - e_pe
            t = math.ceil(math.log2(1 / e_ec))
            nu = math.sqrt(m * (k + 1) * math.log(2 / e_pe) / (n * k**2))
            if delta + nu >= 0.5:
                continue
            r = f_ec * n * h2(delta)
            l = math.floor(n * (log_inv_c - h2(delta + nu)) - r - t - 2 * math.log2(1 / (2 * e_pa)))
            if l > best[0]:
                best = (l, dict(k=k, n=n, nu=nu, t=t, r=r, eps_ec=e_ec, eps_pe=e_pe, eps_pa=e_pa))
    return best


def finite_key_errors(m: int, k: int, delta: float, nu: float, r: float, t: int, l: int,
                      log_inv_c: float = 1.0) -> dict:
    """Evaluate the three error terms of [S5 Thms 2, 3] for given parameters."""
    n = m - k
    e_pe = 2 * math.exp(-n * k**2 * nu**2 / (m * (k + 1)))
    expo = -n * (log_inv_c - h2(delta + nu)) + r + t + l
    e_pa = 0.5 * math.sqrt(2.0**expo) if expo < 1000 else float("inf")
    return dict(eps_ec=2.0**-t, eps_pe=e_pe, eps_pa=e_pa, total=2.0**-t + e_pe + e_pa)


def demo() -> None:
    print(f"Shor-Preskill threshold e* = {100 * sp_threshold():.4f} %")
    for e in (0.01, 0.03, 0.05, 0.08):
        r, arg = devetak_winter_bb84_min(e)
        print(f"e={e:.2f}: 1-2h(e)={shor_preskill(e):.4f}  min DW={r:.4f} at lambda_Psi-={arg:.5f} "
              f"(e^2={e * e:.5f})  chi(Z:E)={holevo_eve(bb84_lams(e, e)):.4f} = h(e)={h2(e):.4f}")
    print("\nDecoy BB84, GYS parameters, mu optimised per distance")
    print(f"{'L km':>5} {'mu*':>6} {'R inf decoy':>12} {'R single photon':>16}")
    for L, mu, r in decoy_rate_curve([0, 50, 100, 140]):
        print(f"{L:5.0f} {mu:6.3f} {r:12.3e} {single_photon_rate(L):16.3e}")
    d = max_distance(lambda L: decoy_rate_curve([L])[0][2])
    print(f"cutoff with optimised mu: {d:.1f} km")
    print("\nFinite key (Tomamichel-Leverrier), eps = 1e-10, r = 1.1 n h(delta), c = 1/2")
    print(f"{'m':>9} " + " ".join(f"{'d=' + str(dl):>9}" for dl in (0.01, 0.025, 0.05)))
    for m in (10**4, 10**5, 10**6, 10**7, 10**8):
        row = [finite_key_length(m, dl)[0] / m for dl in (0.01, 0.025, 0.05)]
        print(f"{m:9d} " + " ".join(f"{x:9.4f}" for x in row))
    print("asym.     " + " ".join(f"{1 - 2.1 * h2(dl):9.4f}" for dl in (0.01, 0.025, 0.05))
          + "   (1 - (1+f) h(delta))")


if __name__ == "__main__":
    demo()
