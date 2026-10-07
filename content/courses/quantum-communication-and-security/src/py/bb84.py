"""BB84 prepare-and-measure simulation: sifting, intercept-resend, depolarising noise, QBER.

TOY PROTOCOL SIMULATION, not a QKD implementation. Note 02 (BB84):
- States |0>,|1> (Z, basis 0) and |+>,|-> (X, basis 1); Born-rule measurement (`measure`).
- Eve intercepts a fraction `p_ir` of the qubits, measures in a random (or fixed Z) basis and
  re-sends her result (`simulate`). Then a depolarising channel rho -> (1-p) rho + p I/2.
- Analytic QBER per sifted bit (`qber_analytic`):
    e = (1 - p) * e_Eve + p / 2,   e_Eve = p_ir / 4 (random basis) [S3 Sec. I.B].
- Sifting keeps rounds with equal bases, a fraction 1/2 (`sift`).
- Parameter estimation on a random sample of k sifted bits (`estimate_qber`) and the
  sampling-without-replacement tail of Tomamichel-Leverrier Lemma 6 [S5]
  (`serfling_tail`).
- Eve's information for the intercept-resend attack: I(A:E) = p_ir/2 = 2e per sifted bit.

Run `python bb84.py`.
"""
from __future__ import annotations

import math

import numpy as np

S2 = 1 / math.sqrt(2)
# STATES[basis, bit] as real 2-vectors
STATES = np.array([[[1, 0], [0, 1]], [[S2, S2], [S2, -S2]]])


def measure(vecs: np.ndarray, bases: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Measure each state vector in its basis; outcome 0 with prob |<basis,0|psi>|^2."""
    p0 = np.einsum("ij,ij->i", STATES[bases, 0], vecs) ** 2
    return (rng.random(len(vecs)) >= p0).astype(np.int8)


def simulate(n: int, rng: np.random.Generator, p_ir: float = 0.0, p_depol: float = 0.0,
             eve_basis: str = "random") -> dict:
    """n rounds of BB84. Returns the raw strings and bases of Alice, Bob (and Eve's guesses)."""
    a_bits = rng.integers(0, 2, n).astype(np.int8)
    a_bases = rng.integers(0, 2, n)
    b_bases = rng.integers(0, 2, n)
    vecs = STATES[a_bases, a_bits].astype(float)

    # intercept-resend: Eve measures and re-prepares the eigenstate she found
    hit = rng.random(n) < p_ir
    e_bases = rng.integers(0, 2, n) if eve_basis == "random" else np.zeros(n, dtype=int)
    e_bits = np.full(n, -1, dtype=np.int8)
    if hit.any():
        e_bits[hit] = measure(vecs[hit], e_bases[hit], rng)
        vecs[hit] = STATES[e_bases[hit], e_bits[hit]]

    b_bits = measure(vecs, b_bases, rng)
    # depolarising channel: with probability p the state is replaced by I/2 -> random outcome
    dep = rng.random(n) < p_depol
    b_bits[dep] = rng.integers(0, 2, int(dep.sum())).astype(np.int8)
    return dict(a_bits=a_bits, a_bases=a_bases, b_bits=b_bits, b_bases=b_bases,
                e_bits=e_bits, e_bases=e_bases, hit=hit)


def sift(r: dict) -> dict:
    """Keep the rounds where Alice's and Bob's bases agree (announced publicly)."""
    keep = r["a_bases"] == r["b_bases"]
    return {k: v[keep] for k, v in r.items()}


def qber(s: dict, basis: int | None = None) -> float:
    m = np.ones(len(s["a_bits"]), bool) if basis is None else s["a_bases"] == basis
    return float(np.mean(s["a_bits"][m] != s["b_bits"][m]))


def qber_analytic(p_ir: float, p_depol: float, eve_basis: str = "random") -> dict:
    """Expected QBER overall and per basis."""
    if eve_basis == "random":
        ez = ex = p_ir / 4           # wrong basis half the time, then error half the time
    else:                            # Eve always measures Z: no Z errors, X errors 1/2
        ez, ex = 0.0, p_ir / 2
    ez = (1 - p_depol) * ez + p_depol / 2
    ex = (1 - p_depol) * ex + p_depol / 2
    return dict(total=(ez + ex) / 2, Z=ez, X=ex)


def eve_information(s: dict) -> float:
    """Fraction of sifted bits Eve knows with certainty (right basis): I(A:E) per sifted bit."""
    known = s["hit"] & (s["e_bases"] == s["a_bases"])
    return float(np.mean(known))


def estimate_qber(s: dict, k: int, rng: np.random.Generator) -> tuple[float, dict]:
    """Reveal k random sifted positions; return the sample QBER and the unrevealed remainder."""
    idx = rng.permutation(len(s["a_bits"]))
    test, rest = idx[:k], idx[k:]
    est = float(np.mean(s["a_bits"][test] != s["b_bits"][test]))
    return est, {key: v[rest] for key, v in s.items()}


def serfling_tail(n: int, k: int, nu: float) -> float:
    """Pr[error rate on n key bits >= sample rate on k test bits + nu] <= this [S5 Lemma 6]."""
    return math.exp(-2 * nu**2 * n * k**2 / ((n + k) * (k + 1)))


def sampling_deviation_mc(n: int, k: int, e: float, nu: float, trials: int,
                          rng: np.random.Generator) -> float:
    """Monte Carlo of the event in `serfling_tail` for a fixed string with error rate e."""
    m = n + k
    z = np.zeros(m, dtype=np.int8)
    z[: int(round(e * m))] = 1
    bad = 0
    for _ in range(trials):
        perm = rng.permutation(z)
        bad += perm[k:].mean() >= perm[:k].mean() + nu
    return bad / trials


def demo() -> None:
    rng = np.random.default_rng(1)
    n = 200_000
    print(f"{'p_ir':>5} {'p_dep':>6} {'sift':>6} {'QBER sim':>9} {'analytic':>9} {'I(A:E)':>7} {'p_ir/2':>6}")
    for p_ir, p_dep in [(0, 0), (1, 0), (0.4, 0), (0, 0.1), (0.4, 0.1)]:
        r = simulate(n, rng, p_ir, p_dep)
        s = sift(r)
        a = qber_analytic(p_ir, p_dep)
        print(f"{p_ir:5.2f} {p_dep:6.2f} {len(s['a_bits']) / n:6.3f} {qber(s):9.4f} "
              f"{a['total']:9.4f} {eve_information(s):7.4f} {p_ir / 2:6.3f}")
    r = sift(simulate(n, rng, 1.0, 0.0, eve_basis="Z"))
    print("Eve always in Z: e_Z =", round(qber(r, 0), 4), " e_X =", round(qber(r, 1), 4),
          "-> a basis-resolved check catches a biased Eve")
    s = sift(simulate(20_000, rng, 0.2, 0.02))
    est, rest = estimate_qber(s, 1000, rng)
    print(f"estimate from 1000 test bits: {est:.4f}; true on the rest: {qber(rest):.4f}; "
          f"analytic {qber_analytic(0.2, 0.02)['total']:.4f}")
    for nu in (0.02, 0.05):
        print(f"Serfling tail n=9000, k=1000, nu={nu}: {serfling_tail(9000, 1000, nu):.2e}")


if __name__ == "__main__":
    demo()
