"""Shannon and von Neumann entropy, relative entropy, conditional entropy, mutual information.

Note 03 (entropy). All logarithms base 2 (bits). Implements
- H(p), S(rho) = -tr rho log rho via eigenvalues (0 log 0 = 0),
- D(rho||sigma) = tr rho (log rho - log sigma), +inf if supp rho not in supp sigma,
- S(A|B) = S(AB) - S(B), I(A:B) = S(A) + S(B) - S(AB) = D(rho_AB || rho_A x rho_B),
- numerical checks of Klein (D >= 0), subadditivity, Araki-Lieb, concavity,
  strong subadditivity (Lieb-Ruskai) on seeded random states.
Run `python entropies.py`.
"""
from __future__ import annotations

import numpy as np

from states import partial_trace, random_state

EPS = 1e-12


def shannon(p) -> float:
    p = np.asarray(p, dtype=float)
    p = p[p > EPS]
    return float(-(p * np.log2(p)).sum())


def von_neumann(rho: np.ndarray) -> float:
    return shannon(np.clip(np.linalg.eigvalsh(rho), 0, None))


def _logm_psd(A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """log2 of a PSD matrix on its support, plus the projector onto the kernel."""
    w, V = np.linalg.eigh(A)
    supp = w > EPS
    L = (V[:, supp] * np.log2(w[supp])) @ V[:, supp].conj().T
    K = V[:, ~supp] @ V[:, ~supp].conj().T
    return L, K


def relative_entropy(rho: np.ndarray, sigma: np.ndarray) -> float:
    """D(rho||sigma); +inf if rho has weight on the kernel of sigma."""
    Lr, _ = _logm_psd(rho)
    Ls, Ks = _logm_psd(sigma)
    if np.real(np.trace(rho @ Ks)) > 1e-9:
        return float("inf")
    return float(np.real(np.trace(rho @ (Lr - Ls))))


def conditional_entropy(rho_ab: np.ndarray, dims) -> float:
    """S(A|B) = S(AB) - S(B); can be negative (-log d_A for a maximally entangled state)."""
    return von_neumann(rho_ab) - von_neumann(partial_trace(rho_ab, dims, [1]))


def mutual_information(rho_ab: np.ndarray, dims) -> float:
    ra = partial_trace(rho_ab, dims, [0])
    rb = partial_trace(rho_ab, dims, [1])
    return von_neumann(ra) + von_neumann(rb) - von_neumann(rho_ab)


def conditional_mutual_information(rho_abc: np.ndarray, dims) -> float:
    """I(A:C|B) = S(AB) + S(BC) - S(B) - S(ABC) >= 0 is strong subadditivity."""
    s = lambda keep: von_neumann(partial_trace(rho_abc, dims, keep))
    return s([0, 1]) + s([1, 2]) - s([1]) - von_neumann(rho_abc)


def check_inequalities(rng: np.random.Generator, trials: int = 200, dims=(2, 3)) -> dict:
    """Worst-case slack of each inequality over random states (all should be >= 0)."""
    da, db = dims
    worst = dict(klein=np.inf, subadditivity=np.inf, araki_lieb=np.inf,
                 concavity=np.inf, mi_equals_relative_entropy=0.0)
    for _ in range(trials):
        rank = int(rng.integers(1, da * db + 1))
        r = random_state(da * db, rng, rank=rank)
        s = random_state(da * db, rng)
        ra, rb = partial_trace(r, dims, [0]), partial_trace(r, dims, [1])
        S, Sa, Sb = von_neumann(r), von_neumann(ra), von_neumann(rb)
        worst["klein"] = min(worst["klein"], relative_entropy(r, s))
        worst["subadditivity"] = min(worst["subadditivity"], Sa + Sb - S)
        worst["araki_lieb"] = min(worst["araki_lieb"], S - abs(Sa - Sb))
        lam = rng.uniform()
        mix = lam * r + (1 - lam) * s
        worst["concavity"] = min(worst["concavity"],
                                 von_neumann(mix) - lam * S - (1 - lam) * von_neumann(s))
        mi_gap = abs(mutual_information(r, dims) - relative_entropy(r, np.kron(ra, rb)))
        worst["mi_equals_relative_entropy"] = max(worst["mi_equals_relative_entropy"], mi_gap)
    return worst


def check_ssa(rng: np.random.Generator, trials: int = 100, dims=(2, 2, 2)) -> float:
    """Minimum of I(A:C|B) over random tripartite states, including low-rank ones."""
    d = int(np.prod(dims))
    return min(conditional_mutual_information(
        random_state(d, rng, rank=int(rng.integers(1, d + 1))), dims) for _ in range(trials))


def demo() -> None:
    from states import BELL, dm
    rng = np.random.default_rng(3)
    phi = dm(BELL["phi+"])
    print("Bell state: S(AB) =", round(von_neumann(phi), 6),
          " S(A) =", round(von_neumann(partial_trace(phi, [2, 2], [0])), 6),
          " S(A|B) =", round(conditional_entropy(phi, [2, 2]), 6),
          " I(A:B) =", round(mutual_information(phi, [2, 2]), 6))
    cc = 0.5 * (dm(np.array([1, 0, 0, 0])) + dm(np.array([0, 0, 0, 1])))
    print("classically correlated (|00><00|+|11><11|)/2: I(A:B) =",
          round(mutual_information(cc, [2, 2]), 6))
    w = check_inequalities(rng)
    print("worst slack over 200 random 2x3 states (>= 0 means the inequality held):")
    for k, v in w.items():
        print(f"  {k:28s} {v: .3e}")
    print("strong subadditivity, min I(A:C|B) over 100 random 2x2x2 states:",
          f"{check_ssa(rng): .3e}")


if __name__ == "__main__":
    demo()
