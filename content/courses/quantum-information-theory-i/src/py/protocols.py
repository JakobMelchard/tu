"""Teleportation, entanglement swapping, dense coding, BB84 and E91 (toy simulations).

Notes 08 (teleportation family) and 09 (QKD). TOY CRYPTO: the QKD functions are
textbook simulations for checking statistics, not secure implementations.
- Teleportation [S27]: projector-based, every Bell outcome m = (m0, m1) has
  probability 1/4 and Bob's corrected state equals the input (fidelity 1); with
  the noisy resource p|Phi+><Phi+| + (1-p) I/4 the fidelity is (1+p)/2 for every
  input, above the classical 2/3 iff p > 1/3.
- Entanglement swapping [S28]: a Bell measurement on qubits 1,2 of
  |Phi+>_01 |Phi+>_23 leaves 0,3 in the corresponding Bell state.
- Dense coding [S29]: Alice's I, X, Z, XZ map |Phi+> to the four orthogonal Bell
  states; Bob's Bell measurement decodes 2 bits.
- BB84 [S30]: sifting keeps ~1/2, QBER 0 without Eve, 1/4 with intercept-resend.
- E91 [S31]: singlet; spin observables cos(t) Z + sin(t) X in the xz-plane with
  Ekert's angles, Alice {0, pi/4, pi/2}, Bob {pi/4, pi/2, 3pi/4}, so that
  E(a, b) = -cos(a - b). The pairs (a2, b1) and (a3, b2) coincide and give
  perfectly anticorrelated key bits; S = E(a1,b1) - E(a1,b3) + E(a3,b1) + E(a3,b3)
  = -2 sqrt 2 exactly; after an intercept-resend in Z, |S| = sqrt 2 < 2.
Run `python protocols.py`.
"""
from __future__ import annotations

import itertools

import numpy as np

from states import BELL, I2, X, Z, dm, kron, partial_trace, random_pure

BELL_BY_BITS = {(0, 0): BELL["phi+"], (0, 1): BELL["psi+"],
                (1, 0): BELL["phi-"], (1, 1): BELL["psi-"]}  # |B_{m0 m1}> = (Z^m0 X^m1 x I)|Phi+>


def teleport(psi: np.ndarray):
    """Return {m: (prob, Bob's corrected state as a density matrix)} for all 4 outcomes."""
    state = np.kron(psi, BELL["phi+"])  # qubit 0 = input, 1 = Alice's half, 2 = Bob's
    out = {}
    for m, b in BELL_BY_BITS.items():
        proj = np.kron(np.outer(b, b.conj()), I2)
        post = proj @ state
        p = float(np.vdot(post, post).real)
        bob = partial_trace(dm(post / np.sqrt(p)), [2, 2, 2], [2])
        C = np.linalg.matrix_power(Z, m[0]) @ np.linalg.matrix_power(X, m[1])  # undo X first, then Z
        out[m] = (p, C @ bob @ C.conj().T)
    return out


def teleport_with_resource(psi: np.ndarray, resource: np.ndarray) -> float:
    """Average fidelity <psi|rho_out|psi> when |Phi+> is replaced by a mixed resource (qubits 1, 2)."""
    rho = np.kron(dm(psi), resource)
    fid = 0.0
    for m, b in BELL_BY_BITS.items():
        proj = np.kron(np.outer(b, b.conj()), I2)
        post = proj @ rho @ proj
        bob = partial_trace(post, [2, 2, 2], [2])  # unnormalised, weight = probability
        C = np.linalg.matrix_power(Z, m[0]) @ np.linalg.matrix_power(X, m[1])
        fid += float(np.real(psi.conj() @ C @ bob @ C.conj().T @ psi))
    return fid


def entanglement_swapping():
    """Bell measurement on qubits (1, 2) of |Phi+>_01|Phi+>_23: {m: (prob, overlap of 0,3 with B_m)}."""
    state = np.kron(BELL["phi+"], BELL["phi+"])
    out = {}
    for m, b in BELL_BY_BITS.items():
        proj = kron(I2, np.outer(b, b.conj()), I2)
        post = proj @ state
        p = float(np.vdot(post, post).real)
        rho03 = partial_trace(dm(post / np.sqrt(p)), [2, 2, 2, 2], [0, 3])
        out[m] = (p, float(np.real(BELL_BY_BITS[m].conj() @ rho03 @ BELL_BY_BITS[m])))
    return out


def dense_coding():
    """Probability that Bob decodes (b0, b1) when Alice sent each of the 4 messages."""
    table = {}
    for m in itertools.product((0, 1), repeat=2):
        U = np.linalg.matrix_power(Z, m[0]) @ np.linalg.matrix_power(X, m[1])
        sent = np.kron(U, I2) @ BELL["phi+"]
        table[m] = {k: float(abs(np.vdot(b, sent)) ** 2) for k, b in BELL_BY_BITS.items()}
    return table


def _measure(rng, rho_bit_basis, basis):
    """Measure a single qubit prepared as (bit, basis) in `basis` (0 = Z, 1 = X)."""
    bit, prep = rho_bit_basis
    return bit if basis == prep else int(rng.integers(2))


def bb84(n: int, rng: np.random.Generator, eve: bool = False):
    """Return (sifted fraction, QBER). Eve does intercept-resend in a random basis."""
    a_bits, a_bases = rng.integers(2, size=n), rng.integers(2, size=n)
    b_bases = rng.integers(2, size=n)
    b_bits = np.empty(n, dtype=int)
    for i in range(n):
        q = (a_bits[i], a_bases[i])
        if eve:
            e_basis = int(rng.integers(2))
            q = (_measure(rng, q, e_basis), e_basis)
        b_bits[i] = _measure(rng, q, b_bases[i])
    keep = a_bases == b_bases
    return keep.mean(), float((a_bits[keep] != b_bits[keep]).mean())


def spin_xz(theta: float) -> np.ndarray:
    return np.cos(theta) * Z + np.sin(theta) * X


E91_ALICE = (0.0, np.pi / 4, np.pi / 2)
E91_BOB = (np.pi / 4, np.pi / 2, 3 * np.pi / 4)
KEY_PAIRS = ((1, 0), (2, 1))  # (Alice index, Bob index) with equal angles


def correlation(rho: np.ndarray, ta: float, tb: float) -> float:
    return float(np.real(np.trace(rho @ np.kron(spin_xz(ta), spin_xz(tb)))))


def e91_exact(rho: np.ndarray):
    """(S, [E on the two key pairs]) with Ekert's CHSH combination."""
    a, b = E91_ALICE, E91_BOB
    S = (correlation(rho, a[0], b[0]) - correlation(rho, a[0], b[2])
         + correlation(rho, a[2], b[0]) + correlation(rho, a[2], b[2]))
    return S, [correlation(rho, a[i], b[j]) for i, j in KEY_PAIRS]


def e91_sampled(rho: np.ndarray, n: int, rng: np.random.Generator):
    """n rounds with uniformly random settings: (S estimate, key error rate, key length).

    A key bit is an error when the outcomes on a key pair are equal (ideal singlet
    outcomes are opposite; Bob flips his bit).
    """
    outcomes = {}
    for _ in range(n):
        i, j = int(rng.integers(3)), int(rng.integers(3))
        pa = [(np.eye(2) + s * spin_xz(E91_ALICE[i])) / 2 for s in (1, -1)]
        pb = [(np.eye(2) + s * spin_xz(E91_BOB[j])) / 2 for s in (1, -1)]
        probs = np.clip([np.real(np.trace(rho @ np.kron(P, Q))) for P in pa for Q in pb], 0, None)
        k = rng.choice(4, p=probs / probs.sum())
        outcomes.setdefault((i, j), []).append((1 - 2 * (k // 2)) * (1 - 2 * (k % 2)))
    E = {k: np.mean(v) for k, v in outcomes.items()}
    S = E[(0, 0)] - E[(0, 2)] + E[(2, 0)] + E[(2, 2)]
    key = [x for pair in KEY_PAIRS for x in outcomes.get(pair, [])]
    return S, float(np.mean([x == 1 for x in key])), len(key)


def intercept_resend_z(rho: np.ndarray) -> np.ndarray:
    """Eve measures both halves' source in Z (dephasing each qubit): a separable state."""
    P = [np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)]
    return sum(np.kron(P[i], P[j]) @ rho @ np.kron(P[i], P[j]) for i in range(2) for j in range(2))


def demo() -> None:
    rng = np.random.default_rng(7)
    psi = random_pure(2, rng)
    res = teleport(psi)
    print("teleportation: probs", [round(v[0], 6) for v in res.values()],
          " fidelities", [round(float(np.real(psi.conj() @ v[1] @ psi)), 6) for v in res.values()])
    iso = lambda p: p * dm(BELL["phi+"]) + (1 - p) * np.eye(4) / 4
    print("teleportation with p|Phi+><Phi+| + (1-p)I/4, p=0.5: fidelity",
          round(teleport_with_resource(psi, iso(0.5)), 6), "= (1+p)/2; classical limit 2/3")
    print("swapping: (prob, overlap with B_m)", {k: tuple(round(x, 6) for x in v)
                                               for k, v in entanglement_swapping().items()})
    dc = dense_coding()
    print("dense coding decoded correctly:", all(abs(dc[m][m] - 1) < 1e-12 for m in dc))
    print("BB84 no Eve: sifted %.3f QBER %.4f" % bb84(20000, rng))
    print("BB84 intercept-resend: sifted %.3f QBER %.4f (theory 0.25)" % bb84(20000, rng, eve=True))
    s = dm(BELL["psi-"])
    S, Ekey = e91_exact(s)
    print("E91 exact singlet: S = %.6f (-2 sqrt2 = %.6f), key-pair correlations %s"
          % (S, -2 * np.sqrt(2), np.round(Ekey, 6)))
    print("E91 exact after Z intercept: S = %.6f" % e91_exact(intercept_resend_z(s))[0])
    print("E91 sampled (9000 rounds): S = %.3f, key error rate = %.3f, key bits = %d"
          % e91_sampled(s, 9000, rng))


if __name__ == "__main__":
    demo()
