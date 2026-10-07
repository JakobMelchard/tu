"""The random-oracle model as code: a lazily sampled oracle that logs every
query (observability) and can be programmed (programmability); the
Bellare-Rogaway encryption E(m) = (f(r), G(r) xor m) with the one-wayness
reduction that reads the query log; Schnorr signing simulated without the key
by programming H; and forking-lemma rewinding that extracts the Schnorr key.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). The 'hash' is
a Python dict of random values, RSA has 40-bit primes, the group is
groups.TOY/MEDIUM. Sources: ROM paradigm [S8]; ETDF, Schnorr bound [S4 Thm
11.2, eq. (19.5)-(19.6)]; general forking lemma [S27 Lemma 1], [S26].
"""
from __future__ import annotations

import random
import secrets

from groups import MEDIUM, SchnorrGroup


class ProgrammingFailure(Exception):
    """The reduction wanted to program H at a point already defined."""


class RandomOracle:
    """H: X -> Z_mod, sampled lazily. Every query is logged."""

    def __init__(self, mod: int, rng: random.Random | None = None):
        self.mod, self.table, self.log = mod, {}, []
        self.rng = rng or random.Random(secrets.randbits(64))

    def __call__(self, x):
        self.log.append(x)
        if x not in self.table:
            self.table[x] = self.rng.randrange(self.mod)
        return self.table[x]

    def program(self, x, y):
        if x in self.table:
            raise ProgrammingFailure(x)
        self.table[x] = y % self.mod


# --- Bellare-Rogaway 1993 sec. 3: E(m) = f(r) || G(r) xor m [S8] ------------

TOY_RSA_P, TOY_RSA_Q, TOY_RSA_E = 1000003, 1000033, 65537
TOY_RSA_N = TOY_RSA_P * TOY_RSA_Q
TOY_RSA_D = pow(TOY_RSA_E, -1, (TOY_RSA_P - 1) * (TOY_RSA_Q - 1))


def f(x: int) -> int:           # the trapdoor permutation (textbook RSA)
    return pow(x, TOY_RSA_E, TOY_RSA_N)


def f_inv(y: int) -> int:
    return pow(y, TOY_RSA_D, TOY_RSA_N)


def br_encrypt(Gro: RandomOracle, m: int):
    r = secrets.randbelow(TOY_RSA_N)
    return f(r), Gro(r) ^ m


def br_decrypt(Gro: RandomOracle, ct) -> int:
    y, c = ct
    return Gro(f_inv(y)) ^ c


def ow_inverter_from_log(y_star: int, log) -> int | None:
    """The reduction B: it cannot decrypt, but it SEES the adversary's
    queries. If A ever asked G(r*), B finds r* by testing f(x) = y*."""
    for x in log:
        if isinstance(x, int) and f(x) == y_star:
            return x
    return None


# --- Schnorr signatures in the ROM ------------------------------------------

def sign(G: SchnorrGroup, H: RandomOracle, x: int, m: str):
    y = G.exp(G.g, x)
    r = G.rand_scalar()
    t = G.exp(G.g, r)
    c = H((y, t, m))
    return t, (r + c * x) % G.q


def verify(G: SchnorrGroup, H: RandomOracle, y: int, m: str, sig) -> bool:
    t, s = sig
    return G.exp(G.g, s) == G.mul(t, G.exp(y, H((y, t, m))))


def simulated_sign(G: SchnorrGroup, H: RandomOracle, y: int, m: str):
    """Signing oracle WITHOUT x: HVZK simulator + programming H(y, t, m) := c.
    Fails iff (y, t, m) was already queried; t is uniform in G, so each
    signing query fails w.p. <= (#queries so far)/q [S4 eq. (19.5)]."""
    c, s = G.rand_scalar(), G.rand_scalar()
    t = G.mul(G.exp(G.g, s), G.inv(G.exp(y, c)))
    H.program((y, t, m), c)
    return t, s


# --- general forking lemma [S27 Lemma 1] -------------------------------------

def toy_forger(G: SchnorrGroup, x_secret: int, acc: float, q: int):
    """A black-box 'forger' A(pk, h_1..h_q; rho) in the format of [S27]:
    it gets the answers to its q oracle queries as a list, and returns
    (J, sigma) with J in {0..q}, J = 0 meaning failure. It uses x internally
    (a real forger would not need to) but the reduction only runs it."""
    def A(pk: int, hs: list[int], rho: int):
        rng = random.Random(rho)                     # all of A's coins
        rs = [rng.randrange(G.q) for _ in range(q)]
        ts = [G.exp(G.g, r) for r in rs]             # the i-th query is H(pk, t_i, m_i)
        # which forgery to output (and whether to succeed) may depend on ALL
        # oracle answers: this is what makes J' = J after a rewind a 1/q event
        late = random.Random(f"{rho}|{hs}")
        J = late.randrange(1, q + 1)
        if late.random() >= acc:
            return 0, None
        c = hs[J - 1]
        return J, (ts[J - 1], c, (rs[J - 1] + c * x_secret) % G.q)
    return A


def fork(A, pk: int, q: int, h_space: int, rng: random.Random):
    """F_A: run A, rewind to its J-th query, resample h_J..h_q, rerun with the
    SAME coins. Success iff J' = J >= 1 and h_J != h'_J."""
    rho = rng.getrandbits(64)
    hs = [rng.randrange(h_space) for _ in range(q)]
    J, sig = A(pk, hs, rho)
    if J == 0:
        return None
    hs2 = hs[:J - 1] + [rng.randrange(h_space) for _ in range(q - J + 1)]
    J2, sig2 = A(pk, hs2, rho)
    if J2 != J or hs[J - 1] == hs2[J - 1]:
        return None
    return sig, sig2


def extract_from_fork(G: SchnorrGroup, sig, sig2) -> int:
    """Two forgeries with the same t and different c: special soundness."""
    (t1, c1, s1), (t2, c2, s2) = sig, sig2
    assert t1 == t2 and c1 != c2
    return (s1 - s2) * pow(c1 - c2, -1, G.q) % G.q


def forking_bound(acc: float, q: int, h: int) -> float:
    """frk >= acc (acc/q - 1/h)."""
    return acc * (acc / q - 1 / h)


if __name__ == "__main__":
    Gro = RandomOracle(2**32)
    ct = br_encrypt(Gro, 0xC0FFEE)
    print("BR93 decrypts:", hex(br_decrypt(Gro, ct)))
    # an 'adversary' that can factor the toy modulus queries G at r* ...
    Gro.log.clear()
    r_star = f_inv(ct[0])
    Gro(r_star)
    print("reduction finds r* in the query log:", ow_inverter_from_log(ct[0], Gro.log) == r_star)

    G = MEDIUM
    x = G.rand_scalar()
    y = G.exp(G.g, x)
    H = RandomOracle(G.q)
    sig = simulated_sign(G, H, y, "hello")
    print("simulated (keyless) signature verifies:", verify(G, H, y, "hello", sig))

    q, acc, trials = 8, 0.5, 10000
    A = toy_forger(G, x, acc, q)
    rng = random.Random(1)
    wins = 0
    for _ in range(trials):
        out = fork(A, y, q, G.q, rng)
        if out:
            wins += 1
            assert extract_from_fork(G, *out) == x
    print(f"forking: q={q}, acc={acc}: empirical frk = {wins / trials:.4f}"
          f" +- {(wins / trials * (1 - wins / trials) / trials) ** 0.5:.4f}, bound "
          f"acc(acc/q - 1/h) = {forking_bound(acc, q, G.q):.4f} (this forger meets it"
          f" with equality in expectation); every success extracted x")
