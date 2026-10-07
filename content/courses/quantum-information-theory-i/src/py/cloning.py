"""No-cloning, optimal approximate cloning, broadcasting, and state discrimination.

Note 13. Implements
- the linearity/unitarity obstruction: a machine that clones |0>, |1> (CNOT) maps
  |+>|0> to a Bell state, not |+>|+> (fidelity 1/2) [S48, S49],
- the Buzek-Hillery universal 1->2 qubit cloner as an isometry on input x blank x
  machine [S50]: single-copy fidelity 5/6 for every input, reduced state
  (2/3) psi + (1/3) I/2, and equality with the symmetric-projector form
  (2/(d+1)) P_sym (rho x I) P_sym,
- the 1->M symmetric cloner for qubits, fidelity (2M+1)/(3M) [S51, S52]: 5/6, 7/9, 3/4,
  tending to 2/3, the optimal measure-and-prepare fidelity,
- broadcasting: CNOT broadcasts commuting (diagonal) states exactly, not |+> [S53],
- Helstrom: P_succ = (1 + ||p0 rho0 - p1 rho1||_1)/2, attained by the projector onto
  the positive part [S55]; unambiguous discrimination of two pure states,
  P_succ = 1 - |<a|b>| (Ivanovic-Dieks-Peres) [S56-S58].
Run `python cloning.py`.
"""
from __future__ import annotations

import itertools

import numpy as np

from states import I2, dm, ket, kron, partial_trace, random_pure

CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def cnot_clone_fidelity(psi: np.ndarray) -> float:
    """|<psi psi| CNOT |psi 0>|^2."""
    out = CNOT @ np.kron(psi, [1, 0])
    return float(abs(np.vdot(np.kron(psi, psi), out)) ** 2)


def buzek_hillery() -> np.ndarray:
    """Isometry C^2 -> C^2(A) x C^2(B) x C^2(M) (8 x 2).

    |0> -> sqrt(2/3)|00>|0> + sqrt(1/6)(|01> + |10>)|1>
    |1> -> sqrt(2/3)|11>|1> + sqrt(1/6)(|01> + |10>)|0>
    """
    b = lambda *bits: kron(*[np.eye(2)[x] for x in bits])
    v0 = np.sqrt(2 / 3) * b(0, 0, 0) + np.sqrt(1 / 6) * (b(0, 1, 1) + b(1, 0, 1))
    v1 = np.sqrt(2 / 3) * b(1, 1, 1) + np.sqrt(1 / 6) * (b(0, 1, 0) + b(1, 0, 0))
    return np.column_stack([v0, v1]).astype(complex)


def bh_output(rho: np.ndarray) -> np.ndarray:
    """Two-copy output rho_AB of the Buzek-Hillery machine."""
    V = buzek_hillery()
    return partial_trace(V @ rho @ V.conj().T, [2, 2, 2], [0, 1])


def sym_projector(M: int, d: int = 2) -> np.ndarray:
    """Projector onto the symmetric subspace of (C^d)^{x M}: average of permutation operators."""
    D = d ** M
    P = np.zeros((D, D))
    perms = list(itertools.permutations(range(M)))
    for perm in perms:
        for idx in itertools.product(range(d), repeat=M):
            src = np.ravel_multi_index(idx, [d] * M)
            dst = np.ravel_multi_index([idx[perm[k]] for k in range(M)], [d] * M)
            P[dst, src] += 1
    return P / len(perms)


def symmetric_cloner(rho: np.ndarray, M: int) -> np.ndarray:
    """Werner's optimal 1 -> M cloner for qubits: (2/(M+1)) P_M (rho x I^{M-1}) P_M."""
    P = sym_projector(M)
    return 2 / (M + 1) * P @ kron(rho, *([I2] * (M - 1))) @ P


def single_copy_fidelity(out: np.ndarray, psi: np.ndarray, M: int, k: int = 0) -> float:
    red = partial_trace(out, [2] * M, [k])
    return float(np.real(psi.conj() @ red @ psi))


def cnot_broadcast_marginals(rho: np.ndarray):
    out = CNOT @ np.kron(rho, dm(np.array([1, 0]))) @ CNOT.conj().T
    return partial_trace(out, [2, 2], [0]), partial_trace(out, [2, 2], [1])


def helstrom(rho0: np.ndarray, rho1: np.ndarray, p0: float = 0.5):
    """(P_succ, projector onto 'guess 0') for the optimal two-outcome measurement."""
    G = p0 * rho0 - (1 - p0) * rho1
    w, V = np.linalg.eigh(G)
    P = V[:, w > 0] @ V[:, w > 0].conj().T
    return 0.5 * (1 + np.abs(w).sum()), P


def helstrom_pure(overlap: float, p0: float = 0.5) -> float:
    return 0.5 * (1 + np.sqrt(1 - 4 * p0 * (1 - p0) * abs(overlap) ** 2))


def usd_povm(a: np.ndarray, b: np.ndarray):
    """IDP POVM for equal priors: E_a ~ |b_perp><b_perp|, E_b ~ |a_perp><a_perp|, E_? = rest."""
    c = abs(np.vdot(a, b))
    perp = lambda v: np.array([-np.conj(v[1]), np.conj(v[0])])
    Ea = dm(perp(b)) / (1 + c)
    Eb = dm(perp(a)) / (1 + c)
    return Ea, Eb, np.eye(2) - Ea - Eb


def usd_success(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """(success probability, error probability) with equal priors."""
    Ea, Eb, _ = usd_povm(a, b)
    succ = 0.5 * (np.real(a.conj() @ Ea @ a) + np.real(b.conj() @ Eb @ b))
    err = 0.5 * (np.real(a.conj() @ Eb @ a) + np.real(b.conj() @ Ea @ b))
    return float(succ), float(err)


def demo() -> None:
    rng = np.random.default_rng(10)
    plus = ket(1, 1)
    print("CNOT 'cloner': fidelity on |0> =", cnot_clone_fidelity(ket(1, 0)),
          " on |+> =", round(cnot_clone_fidelity(plus), 6))
    V = buzek_hillery()
    print("Buzek-Hillery V^dag V = I:", np.allclose(V.conj().T @ V, np.eye(2)))
    fids = []
    for _ in range(200):
        psi = random_pure(2, rng)
        out = bh_output(dm(psi))
        fids += [single_copy_fidelity(out, psi, 2, 0), single_copy_fidelity(out, psi, 2, 1)]
    print("BH single-copy fidelity over 200 random inputs: min %.6f max %.6f (5/6 = %.6f)"
          % (min(fids), max(fids), 5 / 6))
    psi = random_pure(2, rng)
    print("BH output = (2/3) P_sym (psi x I) P_sym:",
          np.allclose(bh_output(dm(psi)), symmetric_cloner(dm(psi), 2)))
    for M in (2, 3, 4):
        out = symmetric_cloner(dm(psi), M)
        print(f"1->{M} cloner: tr = {np.trace(out).real:.6f}, F = {single_copy_fidelity(out, psi, M):.6f},"
              f" (2M+1)/(3M) = {(2 * M + 1) / (3 * M):.6f}")
    d0 = np.diag([0.7, 0.3]).astype(complex)
    ma, mb = cnot_broadcast_marginals(d0)
    print("CNOT broadcasts diag(0.7,0.3):", np.allclose(ma, d0) and np.allclose(mb, d0),
          "| broadcasts |+><+|:", np.allclose(cnot_broadcast_marginals(dm(plus))[0], dm(plus)))
    a, b = ket(1, 0), ket(np.cos(0.4), np.sin(0.4))
    c = abs(np.vdot(a, b))
    P, _ = helstrom(dm(a), dm(b))
    print(f"|<a|b>| = {c:.4f}: Helstrom {P:.6f} (formula {helstrom_pure(c):.6f});"
          f" USD (succ, err) = {tuple(round(x, 6) for x in usd_success(a, b))}, 1 - |<a|b>| = {1 - c:.6f}")


if __name__ == "__main__":
    demo()
