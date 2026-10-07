"""MDI-QKD: linear-optics Bell-state measurement (BSM), sifting, and key rate vs distance.

Note 06 (imperfections). Polarisation scheme of Lo, Curty, Qi [S10]: Alice's and Bob's pulses meet
at a 50:50 beam splitter (outputs c, d), each output hits a polarising beam splitter and two
threshold detectors cH, cV, dH, dV. Success = exactly one H detector AND exactly one V detector:
    Psi-: (cH, dV) or (cV, dH);   Psi+: (cH, cV) or (dH, dV).
Sifting (LCQ Table I): keep successful rounds with equal bases; Bob flips his bit, except
X basis with Psi+.

- `single_photon_bsm`: exact two-photon Fock calculation with loss eta_a, eta_b and dark count
  p_d per detector; `y11_e11` averages over the four bit pairs of a basis.
- `coherent_bsm`: phase-randomised weak coherent pulses. Coherent states stay product coherent
  states through linear optics, so each detector clicks independently with
  1 - (1-p_d) exp(-|amplitude|^2); the relative phase is averaged numerically.
- Closed forms of Ma and Razavi [S11]: Y11 (A9), e11 (A11), Q_rect = Q^C + Q^E (B29, B30),
  E_rect (B31), diagonal-basis gain and error (B12, B15, B16) (`mr_*`). The tests check the two
  first-principles models above against them.
- Key rate [S10 Eq. (1)]: R = Q11^Z [1 - h(e11^X)] - Q_rect f h(E_rect), Q11 = mu_a mu_b
  e^{-mu_a-mu_b} Y11 (infinite decoys), relay in the middle (`key_rate`, `rate_curve`).

Parameters `LCQ` follow [S10 Fig. 2] / [S11 Table I]: 0.2 dB/km, detector efficiency 14.5 %,
p_d = 3e-6 per detector, e_d = 1.5 %, f = 1.16. Run `python mdi_qkd.py`.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
from scipy.special import i0

from decoy import best_mu, max_distance
from entropies import h2

S2 = 1 / math.sqrt(2)
POL = {("Z", 0): np.array([1.0, 0.0]), ("Z", 1): np.array([0.0, 1.0]),
       ("X", 0): np.array([S2, S2]), ("X", 1): np.array([S2, -S2])}
DET = ("cH", "cV", "dH", "dV")
PSI_M = [{0, 3}, {1, 2}]
PSI_P = [{0, 1}, {2, 3}]


def output_modes(u: np.ndarray, v: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Mode functions over (cH, cV, dH, dV) of Alice's (u) and Bob's (v) photon after the BS."""
    a = np.array([u[0], u[1], u[0], u[1]]) * S2
    b = np.array([v[0], v[1], -v[0], -v[1]]) * S2
    return a, b


def _click_dist(occupied: dict[frozenset, float], pd: float) -> dict[frozenset, float]:
    """Occupation-set distribution -> click-set distribution with independent dark counts."""
    out: dict[frozenset, float] = {}
    for clicks in itertools.chain.from_iterable(itertools.combinations(range(4), r) for r in range(5)):
        c = frozenset(clicks)
        out[c] = sum(p * pd ** len(c - o) * (1 - pd) ** (4 - len(c))
                     for o, p in occupied.items() if o <= c)
    return out


def single_photon_bsm(u, v, eta_a: float, eta_b: float, pd: float = 0.0) -> dict:
    """Probabilities of Psi- and Psi+ announcements for single photons u (Alice), v (Bob)."""
    a, b = output_modes(u, v)
    occ: dict[frozenset, float] = {}

    def add(o, p):
        occ[frozenset(o)] = occ.get(frozenset(o), 0.0) + p

    for i in range(4):                              # both photons arrive: bosonic amplitudes
        for j in range(i, 4):
            amp = math.sqrt(2) * a[i] * b[i] if i == j else a[i] * b[j] + a[j] * b[i]
            add({i, j}, eta_a * eta_b * abs(amp) ** 2)
    for i in range(4):                              # only one photon arrives
        add({i}, eta_a * (1 - eta_b) * abs(a[i]) ** 2 + (1 - eta_a) * eta_b * abs(b[i]) ** 2)
    add(set(), (1 - eta_a) * (1 - eta_b))
    clicks = _click_dist(occ, pd)
    return dict(psi_minus=sum(clicks[frozenset(s)] for s in PSI_M),
                psi_plus=sum(clicks[frozenset(s)] for s in PSI_P),
                norm=sum(occ.values()))


def _sift_error(basis: str, xa: int, xb: int, which: str) -> bool:
    """After Bob's flip rule, is his bit different from Alice's?"""
    flip = not (basis == "X" and which == "psi_plus")
    return (xb ^ int(flip)) != xa


def y11_e11(basis: str, eta_a: float, eta_b: float, pd: float = 0.0) -> tuple[float, float]:
    """Single-photon yield (success prob. averaged over bit pairs) and error rate in a basis."""
    y = err = 0.0
    for xa, xb in itertools.product((0, 1), repeat=2):
        r = single_photon_bsm(POL[(basis, xa)], POL[(basis, xb)], eta_a, eta_b, pd)
        for which in ("psi_minus", "psi_plus"):
            y += r[which] / 4
            err += r[which] / 4 * _sift_error(basis, xa, xb, which)
    return y, err / y


def coherent_bsm(u, v, ma: float, mb: float, pd: float, n_phase: int = 512) -> dict:
    """Phase-averaged Psi-/Psi+ probabilities for coherent pulses with mean photon numbers
    ma = eta_a mu_a, mb = eta_b mu_b arriving at the relay."""
    phi = np.linspace(0, 2 * np.pi, n_phase, endpoint=False)
    a, b = output_modes(u, v)
    amp = math.sqrt(ma) * a[None, :] + math.sqrt(mb) * np.exp(1j * phi)[:, None] * b[None, :]
    noclick = (1 - pd) * np.exp(-np.abs(amp) ** 2)          # shape (phase, detector)
    click = 1 - noclick
    res = {}
    for name, pats in (("psi_minus", PSI_M), ("psi_plus", PSI_P)):
        p = np.zeros(n_phase)
        for s in pats:
            p += np.prod([click[:, k] if k in s else noclick[:, k] for k in range(4)], axis=0)
        res[name] = float(p.mean())
    return res


def gain_qber(basis: str, ma: float, mb: float, pd: float) -> tuple[float, float]:
    """Overall gain Q (success prob., averaged over bits) and QBER E in one basis, e_d = 0."""
    q = err = 0.0
    for xa, xb in itertools.product((0, 1), repeat=2):
        r = coherent_bsm(POL[(basis, xa)], POL[(basis, xb)], ma, mb, pd)
        for which in ("psi_minus", "psi_plus"):
            q += r[which] / 4
            err += r[which] / 4 * _sift_error(basis, xa, xb, which)
    return q, err / q


# ------------------------------------------------------------ Ma-Razavi closed forms [S11]
def mr_y11(eta_a, eta_b, pd):
    return (1 - pd) ** 2 * (eta_a * eta_b / 2 + (2 * eta_a + 2 * eta_b - 3 * eta_a * eta_b) * pd
                            + 4 * (1 - eta_a) * (1 - eta_b) * pd**2)


def mr_e11(eta_a, eta_b, pd, ed):
    y = mr_y11(eta_a, eta_b, pd)
    return (0.5 * y - (0.5 - ed) * (1 - pd) ** 2 * eta_a * eta_b / 2) / y


def mr_rect(ma, mb, pd, ed):
    """(Q_rect, E_rect) from Eqs. (B29)-(B31); ma = eta_a mu_a, mb = eta_b mu_b."""
    mup, x = ma + mb, math.sqrt(ma * mb) / 2
    qc = 2 * (1 - pd) ** 2 * math.exp(-mup / 2) * (1 - (1 - pd) * math.exp(-ma / 2)) \
        * (1 - (1 - pd) * math.exp(-mb / 2))
    qe = 2 * pd * (1 - pd) ** 2 * math.exp(-mup / 2) * (i0(2 * x) - (1 - pd) * math.exp(-mup / 2))
    q = qc + qe
    return float(q), float((ed * qc + (1 - ed) * qe) / q)


def mr_diag(ma, mb, pd, ed):
    """(Q, E) in the diagonal basis from Eqs. (B12), (B15), (B16)."""
    mup, x = ma + mb, math.sqrt(ma * mb) / 2
    y = (1 - pd) * math.exp(-mup / 4)
    q = 2 * y**2 * (1 + 2 * y**2 - 4 * y * i0(x) + i0(2 * x))
    return float(q), float((0.5 * q - 2 * (0.5 - ed) * y**2 * (i0(2 * x) - 1)) / q)


@dataclass(frozen=True)
class MDIChannel:
    alpha: float = 0.2
    eta_d: float = 0.145
    pd: float = 3e-6
    ed: float = 0.015
    f: float = 1.16

    def eta(self, L_half: float) -> float:
        return self.eta_d * 10 ** (-self.alpha * L_half / 10)


LCQ = MDIChannel()


def key_rate(L: float, mu: float, ch: MDIChannel = LCQ, q_sift: float = 1.0) -> float:
    """Asymptotic rate per pulse pair, relay at L/2, mu_a = mu_b = mu, infinite decoys."""
    eta = ch.eta(L / 2)
    q11 = mu * mu * math.exp(-2 * mu) * mr_y11(eta, eta, ch.pd)
    e11x = mr_e11(eta, eta, ch.pd, ch.ed)
    q, e = mr_rect(eta * mu, eta * mu, ch.pd, ch.ed)
    return q_sift * (q11 * (1 - h2(e11x)) - q * ch.f * h2(e))


def rate_curve(Ls, ch: MDIChannel = LCQ) -> list[tuple[float, float, float]]:
    out = []
    for L in Ls:
        mu, r = best_mu(lambda LL, m: key_rate(LL, m, ch), L, lo=1e-3, hi=2.0)
        out.append((float(L), mu, max(r, 0.0)))
    return out


def demo() -> None:
    for basis in ("Z", "X"):
        print(f"basis {basis}, ideal relay:")
        for xa, xb in itertools.product((0, 1), repeat=2):
            r = single_photon_bsm(POL[(basis, xa)], POL[(basis, xb)], 1.0, 1.0)
            print(f"  bits ({xa},{xb}): P(Psi-)={r['psi_minus']:.3f} P(Psi+)={r['psi_plus']:.3f}")
        y, e = y11_e11(basis, 1.0, 1.0)
        print(f"  Y11 = {y:.3f} (1/2 = BSM success), e11 = {e:.3f}")
    eta, pd = 0.01, 1e-4
    for basis in ("Z", "X"):
        y, e = y11_e11(basis, eta, eta, pd)
        print(f"{basis}: Fock Y11={y:.4e} e11={e:.4f} | Ma-Razavi Y11={mr_y11(eta, eta, pd):.4e} "
              f"e11={mr_e11(eta, eta, pd, 0.0):.4f}")
    ma = mb = 0.05
    qz, ez = gain_qber("Z", ma, mb, pd)
    qx, ex = gain_qber("X", ma, mb, pd)
    mz, mx = mr_rect(ma, mb, pd, 0.0), mr_diag(ma, mb, pd, 0.0)
    print(f"coherent Z: Q={qz:.4e} E={ez:.4f} | (B29-31) Q={mz[0]:.4e} E={mz[1]:.4f}")
    print(f"coherent X: Q={qx:.4e} E={ex:.4f} | (B12-16) Q={mx[0]:.4e} E={mx[1]:.4f}")
    print("\nLCQ parameters, relay in the middle, mu optimised")
    print(f"{'L km':>5} {'mu*':>6} {'R':>10}")
    for L, mu, r in rate_curve([0, 50, 100, 150, 200, 250]):
        print(f"{L:5.0f} {mu:6.3f} {r:10.3e}")
    d = max_distance(lambda L: rate_curve([L])[0][2], hi=500)
    print(f"cutoff: {d:.1f} km")


if __name__ == "__main__":
    demo()
