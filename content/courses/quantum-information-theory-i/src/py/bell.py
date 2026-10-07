"""Bell/CHSH non-locality, Tsirelson's bound, and contextuality proofs.

Notes 06 (non-locality) and 07 (contextuality). Implements
- CHSH operator B = A0(B0+B1) + A1(B0-B1) for spin observables a.sigma,
- the local bound 2 by enumerating all 16 deterministic strategies,
- Tsirelson: B^2 = 4 I - [A0,A1] x [B0,B1], hence ||B|| <= 2 sqrt 2, reached by
  the singlet with orthogonal settings; numerical optimisation over settings,
- Horodecki criterion max CHSH = 2 sqrt(m1 + m2) (two largest eigenvalues of T^T T),
  Werner state violates iff p > 1/sqrt 2,
- Peres-Mermin square and Mermin pentagram: operator products that no
  noncontextual +-1 assignment can reproduce, checked by exhaustive search,
- Cabello-Estebaranz-Garcia-Alcaine 18 vectors in C^4 (9 bases): KS by brute force,
- d = 2 has a noncontextual deterministic model (hemisphere assignment).
Run `python bell.py`.
"""
from __future__ import annotations

import itertools

import numpy as np
from scipy.optimize import minimize

from states import BELL, I2, PAULI, X, Y, Z, dm, kron, two_qubit_decomposition


def spin(n) -> np.ndarray:
    n = np.asarray(n, dtype=float)
    return sum(c * s for c, s in zip(n / np.linalg.norm(n), PAULI))


def chsh_operator(a0, a1, b0, b1) -> np.ndarray:
    A0, A1, B0, B1 = map(spin, (a0, a1, b0, b1))
    return np.kron(A0, B0 + B1) + np.kron(A1, B0 - B1)


def chsh_value(rho, a0, a1, b0, b1) -> float:
    return float(np.real(np.trace(rho @ chsh_operator(a0, a1, b0, b1))))


def local_bound() -> int:
    """max over deterministic a0,a1,b0,b1 in {+-1} of a0(b0+b1) + a1(b0-b1)."""
    return max(a0 * (b0 + b1) + a1 * (b0 - b1)
               for a0, a1, b0, b1 in itertools.product((1, -1), repeat=4))


def tsirelson_identity_error(rng: np.random.Generator) -> float:
    """|| B^2 - (4 I - [A0,A1] x [B0,B1]) || for random settings (should be ~0)."""
    v = [rng.normal(size=3) for _ in range(4)]
    A0, A1, B0, B1 = map(spin, v)
    B = np.kron(A0, B0 + B1) + np.kron(A1, B0 - B1)
    rhs = 4 * np.eye(4) - np.kron(A0 @ A1 - A1 @ A0, B0 @ B1 - B1 @ B0)
    return float(np.abs(B @ B - rhs).max())


def _angles_to_vec(t, p):
    return np.array([np.sin(t) * np.cos(p), np.sin(t) * np.sin(p), np.cos(t)])


def max_chsh_numeric(rho: np.ndarray, rng: np.random.Generator, restarts: int = 20) -> float:
    """max |<B>| over all four measurement directions, by multistart BFGS."""
    def neg(x):
        vs = [_angles_to_vec(x[2 * i], x[2 * i + 1]) for i in range(4)]
        return -abs(chsh_value(rho, *vs))
    best = 0.0
    for _ in range(restarts):
        res = minimize(neg, rng.uniform(0, 2 * np.pi, size=8), method="BFGS")
        best = max(best, -res.fun)
    return best


def horodecki_max_chsh(rho: np.ndarray) -> float:
    """2 sqrt(m1 + m2), m_i the two largest eigenvalues of T^T T [S19]."""
    _, _, T = two_qubit_decomposition(rho)
    m = np.sort(np.linalg.eigvalsh(T.T @ T))[::-1]
    return float(2 * np.sqrt(m[0] + m[1]))


def werner(p: float) -> np.ndarray:
    """p |psi-><psi-| + (1 - p) I/4."""
    return p * dm(BELL["psi-"]) + (1 - p) * np.eye(4) / 4


# Contextuality -------------------------------------------------------------

PERES_MERMIN = [[kron(X, I2), kron(I2, X), kron(X, X)],
                [kron(I2, Y), kron(Y, I2), kron(Y, Y)],
                [kron(X, Y), kron(Y, X), kron(Z, Z)]]


def square_contexts():
    """Rows and columns of the square with the sign of their operator product."""
    ctx = []
    for i in range(3):
        row = [(i, j) for j in range(3)]
        col = [(j, i) for j in range(3)]
        for c in (row, col):
            P = np.eye(4)
            for (a, b) in c:
                P = P @ PERES_MERMIN[a][b]
            sign = 1 if np.allclose(P, np.eye(4)) else (-1 if np.allclose(P, -np.eye(4)) else 0)
            ctx.append((c, sign))
    return ctx


def pentagram():
    """Mermin's star: 10 three-qubit observables on 5 lines of 4 commuting ones."""
    ops = {"X1": kron(X, I2, I2), "X2": kron(I2, X, I2), "X3": kron(I2, I2, X),
           "Y1": kron(Y, I2, I2), "Y2": kron(I2, Y, I2), "Y3": kron(I2, I2, Y),
           "XXX": kron(X, X, X), "XYY": kron(X, Y, Y), "YXY": kron(Y, X, Y), "YYX": kron(Y, Y, X)}
    lines = [["XXX", "XYY", "YXY", "YYX"], ["X1", "X2", "X3", "XXX"],
             ["X1", "Y2", "Y3", "XYY"], ["Y1", "X2", "Y3", "YXY"], ["Y1", "Y2", "X3", "YYX"]]
    out = []
    for line in lines:
        P = np.eye(8)
        for k in line:
            P = P @ ops[k]
        sign = 1 if np.allclose(P, np.eye(8)) else (-1 if np.allclose(P, -np.eye(8)) else 0)
        commute = all(np.allclose(ops[a] @ ops[b], ops[b] @ ops[a]) for a in line for b in line)
        out.append((line, sign, commute))
    return ops, out


def noncontextual_assignments(names, contexts) -> int:
    """Number of +-1 value assignments satisfying every context's product sign."""
    count = 0
    for vals in itertools.product((1, -1), repeat=len(names)):
        v = dict(zip(names, vals))
        if all(np.prod([v[k] for k in c]) == s for c, s in contexts):
            count += 1
    return count


CABELLO_BASES = [
    [(0, 0, 0, 1), (0, 0, 1, 0), (1, 1, 0, 0), (1, -1, 0, 0)],
    [(0, 0, 0, 1), (0, 1, 0, 0), (1, 0, 1, 0), (1, 0, -1, 0)],
    [(1, -1, 1, -1), (1, -1, -1, 1), (1, 1, 0, 0), (0, 0, 1, 1)],
    [(1, -1, 1, -1), (1, 1, 1, 1), (1, 0, -1, 0), (0, 1, 0, -1)],
    [(0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 1), (1, 0, 0, -1)],
    [(1, -1, -1, 1), (1, 1, 1, 1), (1, 0, 0, -1), (0, 1, -1, 0)],
    [(1, 1, -1, 1), (1, 1, 1, -1), (1, -1, 0, 0), (0, 0, 1, 1)],
    [(1, 1, -1, 1), (-1, 1, 1, 1), (1, 0, 1, 0), (0, 1, 0, -1)],
    [(1, 1, 1, -1), (-1, 1, 1, 1), (1, 0, 0, 1), (0, 1, -1, 0)],
]


def cabello_check():
    """(all bases orthogonal, every vector in exactly two bases, #KS colourings).

    A KS colouring assigns 1 to exactly one vector of each basis, consistently
    across bases. Each vector lies in two bases, so a colouring would mark an even
    number of (basis, vector) incidences, but there must be exactly 9: odd.
    """
    vecs = sorted({v for b in CABELLO_BASES for v in b})
    orth = all(abs(np.dot(u, w)) == 0 for b in CABELLO_BASES
               for u, w in itertools.combinations(b, 2))
    counts = {v: sum(v in b for b in CABELLO_BASES) for v in vecs}
    ok = 0
    for choice in itertools.product(range(4), repeat=9):
        ones = {CABELLO_BASES[i][c] for i, c in enumerate(choice)}
        if all(sum(v in ones for v in b) == 1 for b in CABELLO_BASES):
            ok += 1
    return orth, len(vecs), set(counts.values()), ok


def hemisphere_value(n) -> int:
    """Deterministic noncontextual value for the projector onto the Bloch direction n (d=2)."""
    n = np.asarray(n, dtype=float)
    for c in (n[2], n[1], n[0]):
        if abs(c) > 1e-12:
            return 1 if c > 0 else 0
    raise ValueError("zero vector")


def demo() -> None:
    rng = np.random.default_rng(6)
    s = dm(BELL["psi-"])
    x, z = np.array([1, 0, 0]), np.array([0, 0, 1])
    b0, b1 = -(z + x) / np.sqrt(2), -(z - x) / np.sqrt(2)
    print("local bound:", local_bound(), "| singlet, a0=z a1=x b0,b1=-(z+-x)/sqrt2:",
          round(chsh_value(s, z, x, b0, b1), 6), " 2 sqrt 2 =", round(2 * np.sqrt(2), 6))
    print("||B||_op over random settings <= 2 sqrt2:",
          max(np.abs(np.linalg.eigvalsh(chsh_operator(*[rng.normal(size=3) for _ in range(4)]))).max()
              for _ in range(500)).round(6), "| B^2 identity error", tsirelson_identity_error(rng))
    for p in (0.5, 1 / np.sqrt(2), 0.9):
        print(f"Werner p={p:.4f}: Horodecki max CHSH {horodecki_max_chsh(werner(p)):.6f},"
              f" numeric {max_chsh_numeric(werner(p), rng, 5):.6f}")
    ctx = square_contexts()
    print("Peres-Mermin product signs (r1 c1 r2 c2 r3 c3):", [c[1] for c in ctx],
          "| noncontextual assignments:", noncontextual_assignments(
              [(i, j) for i in range(3) for j in range(3)], ctx))
    ops, lines = pentagram()
    print("pentagram line signs:", [l[1] for l in lines], "commuting:", all(l[2] for l in lines),
          "| noncontextual assignments:", noncontextual_assignments(list(ops), [(l[0], l[1]) for l in lines]))
    print("Cabello 18 vectors (orthogonal bases, #vectors, incidences, #colourings):", cabello_check())


if __name__ == "__main__":
    demo()
