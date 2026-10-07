"""Decoy-state BB84 with weak coherent pulses: channel model, vacuum+weak estimation of the
single-photon yield Y_1 and error e_1, the PNS attack, and the GLLP rate without decoys.

Note 06 (imperfections). Model and bounds from Ma, Qi, Zhao, Lo [S9]:
- eta = 10^{-alpha L/10} eta_Bob, eta_i = 1 - (1-eta)^i, Y_i = Y0 + eta_i - Y0 eta_i (Eqs. 5-7),
  Q_mu = Y0 + 1 - e^{-eta mu} (Eq. 10), E_mu Q_mu = e0 Y0 + e_d (1 - e^{-eta mu}) (Eq. 11),
  e_i = (e0 Y0 + e_d eta_i) / Y_i (Eq. 9), e0 = 1/2 (`Channel`).
- Vacuum+weak lower bound on Y_1 (Eq. 34) and upper bound on e_1 (Eq. 37)
  (`vacuum_weak_bounds`); general two-decoy bounds Eqs. 18, 21, 25 (`two_decoy_bounds`).
- Key rate R = q { -Q_mu f h(E_mu) + Q_1 [1 - h(e_1)] }, q = 1/2 (Eq. 1) with the true
  Q_1, e_1 (infinite decoys) or the vacuum+weak bounds (`rate_decoy`).
- GLLP without decoys: multi-photon fraction Delta <= (1 - (1+mu) e^{-mu}) / Q_mu,
  R = q Q_mu { -f h(E) + (1-Delta) [1 - h(E/(1-Delta))] } (`rate_gllp_no_decoy`) [S15, S9 Eq. 3].
- PNS attack that keeps Q_mu fixed: Eve blocks all single photons and forwards multi-photon
  pulses losslessly with the yield needed (`pns_attack_gains`); the weak decoy exposes it.

Parameters `GYS` are those of [S9 Table 1] (1550 nm, 0.21 dB/km, e_d = 3.3 %,
Y0 = 1.7e-6, eta_Bob = 0.045, f = 1.22). Run `python decoy.py`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, minimize_scalar

from entropies import h2


@dataclass(frozen=True)
class Channel:
    alpha: float = 0.21      # dB/km
    eta_bob: float = 0.045   # Bob's optics times detector efficiency
    y0: float = 1.7e-6       # background (dark count) yield
    e_d: float = 0.033       # misalignment error probability
    f: float = 1.22          # error-correction inefficiency
    q: float = 0.5           # basis-sift factor

    def eta(self, L: float) -> float:
        return 10 ** (-self.alpha * L / 10) * self.eta_bob

    def yield_i(self, i: int, L: float) -> float:
        eta_i = 1 - (1 - self.eta(L)) ** i
        return self.y0 + eta_i - self.y0 * eta_i

    def error_i(self, i: int, L: float) -> float:
        eta_i = 1 - (1 - self.eta(L)) ** i
        return (0.5 * self.y0 + self.e_d * eta_i) / self.yield_i(i, L)

    def gain(self, mu: float, L: float) -> float:
        return self.y0 + 1 - math.exp(-self.eta(L) * mu)

    def qber(self, mu: float, L: float) -> float:
        return (0.5 * self.y0 + self.e_d * (1 - math.exp(-self.eta(L) * mu))) / self.gain(mu, L)


GYS = Channel()


def vacuum_weak_bounds(q_mu, q_nu, e_nu, y0, mu, nu) -> tuple[float, float]:
    """(Y1^L, e1^U) from the signal gain, the weak decoy gain/QBER and the vacuum yield Y0."""
    y1 = mu / (mu * nu - nu**2) * (q_nu * math.exp(nu) - q_mu * math.exp(mu) * nu**2 / mu**2
                                   - (mu**2 - nu**2) / mu**2 * y0)
    e1 = (e_nu * q_nu * math.exp(nu) - 0.5 * y0) / (y1 * nu) if y1 > 0 else 0.5
    return y1, min(e1, 0.5)


def two_decoy_bounds(q_mu, q_n1, e_n1, q_n2, e_n2, mu, n1, n2) -> tuple[float, float, float]:
    """(Y0^L, Y1^L, e1^U) for decoys 0 <= n2 < n1, n1 + n2 < mu [S9 Eqs. 18, 21, 25]."""
    y0 = max((n1 * q_n2 * math.exp(n2) - n2 * q_n1 * math.exp(n1)) / (n1 - n2), 0.0)
    y1 = mu / (mu * n1 - mu * n2 - n1**2 + n2**2) * (
        q_n1 * math.exp(n1) - q_n2 * math.exp(n2) - (n1**2 - n2**2) / mu**2 * (q_mu * math.exp(mu) - y0))
    e1 = (e_n1 * q_n1 * math.exp(n1) - e_n2 * q_n2 * math.exp(n2)) / ((n1 - n2) * y1)
    return y0, y1, min(e1, 0.5)


def rate_decoy(L: float, mu: float = 0.48, ch: Channel = GYS, nu: float | None = None) -> float:
    """Key rate per pulse. nu=None: infinite decoys (true Y1, e1). Else vacuum+weak with that nu."""
    q_mu, e_mu = ch.gain(mu, L), ch.qber(mu, L)
    if nu is None:
        y1, e1 = ch.yield_i(1, L), ch.error_i(1, L)
    else:
        y1, e1 = vacuum_weak_bounds(q_mu, ch.gain(nu, L), ch.qber(nu, L), ch.y0, mu, nu)
    q1 = y1 * mu * math.exp(-mu)
    return ch.q * (-q_mu * ch.f * h2(e_mu) + q1 * (1 - h2(e1)))


def rate_gllp_no_decoy(L: float, mu: float, ch: Channel = GYS) -> float:
    """Worst case: every multi-photon pulse is detected and fully known to Eve."""
    q_mu, e_mu = ch.gain(mu, L), ch.qber(mu, L)
    delta = (1 - (1 + mu) * math.exp(-mu)) / q_mu
    if delta >= 1 or e_mu / (1 - delta) >= 0.5:
        return 0.0
    return ch.q * q_mu * (-ch.f * h2(e_mu) + (1 - delta) * (1 - h2(e_mu / (1 - delta))))


def best_mu(rate, L: float, lo: float = 1e-5, hi: float = 1.0) -> tuple[float, float]:
    """Maximise rate(L, mu) over mu: log grid (the rate can be 0 on most of [lo, hi]), then refine."""
    grid = np.geomspace(lo, hi, 60)
    vals = [rate(L, m) for m in grid]
    i = int(np.argmax(vals))
    a, b = grid[max(i - 1, 0)], grid[min(i + 1, len(grid) - 1)]
    r = minimize_scalar(lambda m: -rate(L, m), bounds=(a, b), method="bounded",
                        options={"xatol": 1e-7})
    if -r.fun >= vals[i]:
        return float(r.x), -float(r.fun)
    return float(grid[i]), float(vals[i])


def max_distance(rate_of_L, lo: float = 0.0, hi: float = 400.0, tol: float = 1e-3) -> float:
    """Largest L with positive rate, by bisection (rate assumed positive then non-positive)."""
    if rate_of_L(hi) > 0:
        return hi
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if rate_of_L(mid) > 0 else (lo, mid)
    return lo


def mu_optimal_small_eta(ch: Channel = GYS) -> float:
    """Solve (1 - mu) e^{-mu} = f h(e_d) / (1 - h(e_d)) [S9 Eq. 12]."""
    rhs = ch.f * h2(ch.e_d) / (1 - h2(ch.e_d))
    return brentq(lambda m: (1 - m) * math.exp(-m) - rhs, 1e-6, 1.0)


def relative_deviations(L: float, mu: float, nu: float, ch: Channel = GYS) -> tuple[float, float]:
    """beta_Y1 = (Y1 - Y1^L)/Y1 and beta_e1 = (e1^U - e1)/e1 [S9 Eqs. 29, 30]."""
    y1l, e1u = vacuum_weak_bounds(ch.gain(mu, L), ch.gain(nu, L), ch.qber(nu, L), ch.y0, mu, nu)
    y1, e1 = ch.yield_i(1, L), ch.error_i(1, L)
    return (y1 - y1l) / y1, (e1u - e1) / e1


def pns_attack_gains(L: float, mu: float, nu: float, ch: Channel = GYS) -> dict:
    """Eve blocks n=1, forwards n>=2 with yield y so that Q_mu matches the honest channel."""
    q_mu = ch.gain(mu, L)
    multi = lambda m: 1 - math.exp(-m) * (1 + m)          # P(n >= 2)
    y = (q_mu - ch.y0 * math.exp(-mu)) / multi(mu)        # yield Eve gives to multi-photon pulses
    q_nu_pns = ch.y0 * math.exp(-nu) + y * multi(nu)
    y1l, _ = vacuum_weak_bounds(q_mu, q_nu_pns, 0.0, ch.y0, mu, nu)
    return dict(y_multi=y, q_nu_honest=ch.gain(nu, L), q_nu_pns=q_nu_pns, y1_lower=y1l)


def demo() -> None:
    ch = GYS
    print(f"mu_opt from Eq. 12: {mu_optimal_small_eta(ch):.3f} (paper: 0.48)")
    d_inf = max_distance(lambda L: rate_decoy(L, 0.48, ch))
    d_vw = max_distance(lambda L: rate_decoy(L, 0.48, ch, nu=0.05))
    d_gl = max_distance(lambda L: best_mu(lambda LL, m: rate_gllp_no_decoy(LL, m, ch), L)[1])
    print(f"max distance: infinite decoys {d_inf:.2f} km (paper 142.05), vacuum+weak nu=0.05 "
          f"{d_vw:.2f} km (paper 140.55), no decoy (GLLP, best mu) {d_gl:.1f} km")
    print(f"{'L km':>5} {'eta':>9} {'Q_mu':>9} {'E_mu':>6} {'R inf':>9} {'R v+w':>9} {'R GLLP':>9}")
    for L in (0, 25, 50, 100, 130):
        r_gl = best_mu(lambda LL, m: rate_gllp_no_decoy(LL, m, ch), L)[1]
        print(f"{L:5d} {ch.eta(L):9.2e} {ch.gain(0.48, L):9.2e} {ch.qber(0.48, L):6.4f} "
              f"{rate_decoy(L, 0.48, ch):9.2e} {rate_decoy(L, 0.48, ch, 0.05):9.2e} {r_gl:9.2e}")
    for r in (0.1, 0.25):
        by, be = relative_deviations(40, 0.48, r * 0.48, ch)
        print(f"nu/mu={r:.2f}: beta_Y1 = {100 * by:.1f} %, beta_e1 = {100 * be:.1f} % "
              f"(paper at 25 %: 3.5 %, 16.8 %)")
    p = pns_attack_gains(40, 0.48, 0.05, ch)
    print(f"PNS at 40 km: Q_nu honest {p['q_nu_honest']:.3e} vs under attack {p['q_nu_pns']:.3e}; "
          f"Y1^L = {p['y1_lower']:.2e} (honest Y1 = {ch.yield_i(1, 40):.2e})")


if __name__ == "__main__":
    demo()
