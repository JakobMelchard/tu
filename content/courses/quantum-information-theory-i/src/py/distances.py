"""Hilbert-space geometry: fidelity, Uhlmann's theorem, Bures and trace distance.

Note 05. Convention (Jozsa 1994, Wilde, [S39, S11]): the *fidelity* is the squared
quantity F(rho, sigma) = (tr |sqrt(rho) sqrt(sigma)|)^2 = ||sqrt(rho) sqrt(sigma)||_1^2,
so F(psi, phi) = |<psi|phi>|^2 for pure states. `root_fidelity` is sqrt(F), which
Nielsen & Chuang call F. Implements
- trace distance T = ||rho - sigma||_1 / 2 and its measurement form,
- Bures distance D_B = sqrt(2 (1 - sqrt F)) and Bures angle arccos sqrt F,
- Uhlmann: F = max_U |<psi_rho|(I x U)|psi_sigma>|^2 over canonical purifications,
  with the maximising U built from the SVD of sqrt(rho) sqrt(sigma),
- Fuchs-van de Graaf 1 - sqrt F <= T <= sqrt(1 - F), and quantum Pinsker
  D(rho||sigma) >= (2 / ln 2) T^2, checked on seeded random pairs.
Run `python distances.py`.
"""
from __future__ import annotations

import numpy as np

from entropies import relative_entropy
from schmidt import canonical_purification
from states import dm, random_pure, random_state, random_unitary


def sqrtm_psd(A: np.ndarray) -> np.ndarray:
    w, V = np.linalg.eigh(A)
    return (V * np.sqrt(np.clip(w, 0, None))) @ V.conj().T


def trace_norm(A: np.ndarray) -> float:
    return float(np.linalg.svd(A, compute_uv=False).sum())


def trace_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    return 0.5 * trace_norm(rho - sigma)


def trace_distance_by_projector(rho: np.ndarray, sigma: np.ndarray) -> float:
    """max_P tr P(rho - sigma), attained by the projector onto the positive part."""
    w, V = np.linalg.eigh(rho - sigma)
    P = V[:, w > 0] @ V[:, w > 0].conj().T
    return float(np.real(np.trace(P @ (rho - sigma))))


def root_fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    return trace_norm(sqrtm_psd(rho) @ sqrtm_psd(sigma))


def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    return root_fidelity(rho, sigma) ** 2


def bures_distance(rho: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.sqrt(max(0.0, 2 * (1 - root_fidelity(rho, sigma)))))


def bures_angle(rho: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.arccos(min(1.0, root_fidelity(rho, sigma))))


def uhlmann_optimal_unitary(rho: np.ndarray, sigma: np.ndarray) -> np.ndarray:
    """U on R maximising |<psi_rho|(I x U)|psi_sigma>| for canonical purifications.

    With |psi_X> = (sqrt X x I)|Omega> the overlap is tr(sqrt(rho) sqrt(sigma) U^T).
    For A = sqrt(rho) sqrt(sigma) = W S V^dag (SVD), |tr(A M)| <= tr S = ||A||_1 with
    equality at M = V W^dag, so U = (V W^dag)^T.
    """
    A = sqrtm_psd(rho) @ sqrtm_psd(sigma)
    W, _, Vh = np.linalg.svd(A)
    return (Vh.conj().T @ W.conj().T).T


def uhlmann_overlap(rho: np.ndarray, sigma: np.ndarray, U: np.ndarray) -> float:
    d = rho.shape[0]
    a = canonical_purification(rho)
    b = np.kron(np.eye(d), U) @ canonical_purification(sigma)
    return float(abs(np.vdot(a, b)) ** 2)


def check_fuchs_van_de_graaf(rng: np.random.Generator, trials: int = 300, d: int = 3) -> dict:
    """Worst slack of both FvdG inequalities and of Pinsker; pure-state equality gap."""
    lo = hi = pinsker = np.inf
    pure_gap = 0.0
    for _ in range(trials):
        r = random_state(d, rng, rank=int(rng.integers(1, d + 1)))
        s = random_state(d, rng)
        F, T = fidelity(r, s), trace_distance(r, s)
        lo = min(lo, T - (1 - np.sqrt(F)))
        hi = min(hi, np.sqrt(max(0.0, 1 - F)) - T)
        pinsker = min(pinsker, relative_entropy(r, s) - 2 / np.log(2) * T ** 2)
        p, q = dm(random_pure(d, rng)), dm(random_pure(d, rng))
        pure_gap = max(pure_gap, abs(trace_distance(p, q) - np.sqrt(1 - fidelity(p, q))))
    return dict(lower=lo, upper=hi, pinsker=pinsker, pure_equality_gap=pure_gap)


def demo() -> None:
    rng = np.random.default_rng(5)
    r, s = random_state(2, rng), random_state(2, rng)
    F = fidelity(r, s)
    Uopt = uhlmann_optimal_unitary(r, s)
    best_random = max(uhlmann_overlap(r, s, random_unitary(2, rng)) for _ in range(2000))
    print(f"qubit pair: F = {F:.6f}; Uhlmann overlap at optimal U = {uhlmann_overlap(r, s, Uopt):.6f};"
          f" best of 2000 random U = {best_random:.6f}")
    print(f"T = {trace_distance(r, s):.6f} = max_P tr P(r-s) = {trace_distance_by_projector(r, s):.6f};"
          f" D_B = {bures_distance(r, s):.6f}; Bures angle = {bures_angle(r, s):.6f}")
    rb, sb = np.array([0.1, 0.2, 0.3]), np.array([-0.4, 0.0, 0.5])
    from states import from_bloch
    print("qubits: T = |r - s|/2 =", round(np.linalg.norm(rb - sb) / 2, 6), "numerical:",
          round(trace_distance(from_bloch(rb), from_bloch(sb)), 6))
    print("FvdG / Pinsker worst slack over 300 random qutrit pairs:",
          {k: f"{v:.2e}" for k, v in check_fuchs_van_de_graaf(rng).items()})


if __name__ == "__main__":
    demo()
