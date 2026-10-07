"""Sigma protocols: Schnorr's proof of knowledge of a discrete log, its HVZK
simulator and special-soundness extractor, the Fiat-Shamir transform (strong,
and the weak variant that forgets the statement), Chaum-Pedersen for DH tuples,
and the Cramer-Damgard-Schoenmakers OR-proof.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Groups are
tiny (groups.TINY/TOY) or 128-bit (groups.MEDIUM); SHA-256 stands in for the
random oracle. Definitions follow [S4 sec. 19.1, 19.4-19.7, 20.3].
"""
from __future__ import annotations

from dataclasses import dataclass

from groups import MEDIUM, SchnorrGroup


@dataclass(frozen=True)
class Transcript:
    t: int  # commitment (first message)
    c: int  # challenge
    s: int  # response


# --- Schnorr: R = {(y, x) : y = g^x} ----------------------------------------

def schnorr_commit(G: SchnorrGroup, r: int | None = None):
    r = G.rand_scalar() if r is None else r
    return r, G.exp(G.g, r)


def schnorr_respond(G: SchnorrGroup, x: int, r: int, c: int) -> int:
    return (r + c * x) % G.q


def schnorr_check(G: SchnorrGroup, y: int, tr: Transcript) -> bool:
    """Accept iff g^s = t * y^c."""
    return G.exp(G.g, tr.s) == G.mul(tr.t, G.exp(y, tr.c))


def schnorr_run(G: SchnorrGroup, x: int, c: int | None = None) -> Transcript:
    """One honest execution (honest verifier samples c uniformly)."""
    r, t = schnorr_commit(G)
    c = G.rand_scalar() if c is None else c
    return Transcript(t, c, schnorr_respond(G, x, r, c))


def schnorr_simulate(G: SchnorrGroup, y: int, c: int | None = None,
                     s: int | None = None) -> Transcript:
    """Special HVZK simulator: pick (c, s), solve t = g^s y^{-c}. No witness."""
    c = G.rand_scalar() if c is None else c
    s = G.rand_scalar() if s is None else s
    return Transcript(G.mul(G.exp(G.g, s), G.inv(G.exp(y, c))), c, s)


def schnorr_extract(G: SchnorrGroup, tr1: Transcript, tr2: Transcript) -> int:
    """Special soundness: same t, c1 != c2 gives x = (s1 - s2)/(c1 - c2)."""
    if tr1.t != tr2.t or tr1.c == tr2.c:
        raise ValueError("need two accepting transcripts with equal t, distinct c")
    return (tr1.s - tr2.s) * pow(tr1.c - tr2.c, -1, G.q) % G.q


# --- Fiat-Shamir ------------------------------------------------------------

def fs_prove(G: SchnorrGroup, x: int, msg: str = "", strong: bool = True):
    """Non-interactive proof (or signature on msg): c = H(g, y, t, msg).
    strong=False hashes only (t, msg): the 'weak' Fiat-Shamir of [S33]."""
    y = G.exp(G.g, x)
    r, t = schnorr_commit(G)
    c = G.hash_to_scalar(G.g, y, t, msg) if strong else G.hash_to_scalar(t, msg)
    return t, schnorr_respond(G, x, r, c)


def fs_verify(G: SchnorrGroup, y: int, proof, msg: str = "", strong: bool = True) -> bool:
    t, s = proof
    c = G.hash_to_scalar(G.g, y, t, msg) if strong else G.hash_to_scalar(t, msg)
    return G.is_member(y) and schnorr_check(G, y, Transcript(t, c, s))


def weak_fs_forge(G: SchnorrGroup, msg: str = ""):
    """With weak FS the statement can be chosen *after* the challenge:
    fix t (no known log), c = H(t), pick s, solve y = (g^s / t)^{1/c}.
    The 'prover' never knows log_g y (it would need log_g t) [S33]."""
    t = G.hash_to_group("frozen-heart")
    c = G.hash_to_scalar(t, msg)
    s = G.rand_scalar()
    y = G.exp(G.mul(G.exp(G.g, s), G.inv(t)), pow(c, -1, G.q))
    return y, (t, s)


# --- Chaum-Pedersen: R = {((u, v, w), x) : v = g^x, w = u^x} ------------------

def cp_prove(G: SchnorrGroup, x: int, u: int, c: int | None = None):
    r = G.rand_scalar()
    t1, t2 = G.exp(G.g, r), G.exp(u, r)
    c = G.rand_scalar() if c is None else c
    return (t1, t2), c, (r + c * x) % G.q


def cp_check(G: SchnorrGroup, u: int, v: int, w: int, t, c: int, s: int) -> bool:
    t1, t2 = t
    return (G.exp(G.g, s) == G.mul(t1, G.exp(v, c))
            and G.exp(u, s) == G.mul(t2, G.exp(w, c)))


# --- OR-proof: know log_g y0 OR log_g y1 [S4 sec. 19.7.2], [S29] ------------

def or_prove(G: SchnorrGroup, ys: tuple[int, int], b: int, x: int,
             c: int | None = None, coins: tuple[int, int, int] | None = None):
    """Prover knows x = log y_b. It simulates branch 1-b with a self-chosen
    challenge c_{1-b}, runs branch b honestly with c_b = c - c_{1-b}.
    coins = (c_sim, s_sim, r) fixes the prover's randomness (for tests)."""
    c_sim, s_sim, r = coins if coins else (None, None, None)
    sim = schnorr_simulate(G, ys[1 - b], c_sim, s_sim)
    r, t_b = schnorr_commit(G, r)
    ts = [0, 0]
    ts[b], ts[1 - b] = t_b, sim.t
    c = G.rand_scalar() if c is None else c  # verifier's challenge
    cs, ss = [0, 0], [0, 0]
    cs[1 - b], ss[1 - b] = sim.c, sim.s
    cs[b] = (c - sim.c) % G.q
    ss[b] = schnorr_respond(G, x, r, cs[b])
    return tuple(ts), c, tuple(cs), tuple(ss)


def or_check(G: SchnorrGroup, ys, ts, c, cs, ss) -> bool:
    return ((cs[0] + cs[1]) % G.q == c % G.q and
            all(schnorr_check(G, ys[i], Transcript(ts[i], cs[i], ss[i])) for i in (0, 1)))


def or_extract(G: SchnorrGroup, ys, run1, run2):
    """Two accepting runs with equal (t0, t1), c != c': since c0+c1 != c0'+c1',
    some branch i has c_i != c_i'; special soundness of that branch gives x_i."""
    (ts, _, cs, ss), (ts2, _, cs2, ss2) = run1, run2
    assert ts == ts2
    for i in (0, 1):
        if cs[i] != cs2[i]:
            return i, schnorr_extract(G, Transcript(ts[i], cs[i], ss[i]),
                                      Transcript(ts[i], cs2[i], ss2[i]))
    raise ValueError("challenges equal")


def or_fs_prove(G: SchnorrGroup, ys, b: int, x: int, msg: str = ""):
    """Non-interactive OR-proof: c = H(ys, t0, t1, msg). Needs the commitments
    before c, so recompute with a hash-derived challenge."""
    sim = schnorr_simulate(G, ys[1 - b])
    r, t_b = schnorr_commit(G)
    ts = [0, 0]
    ts[b], ts[1 - b] = t_b, sim.t
    c = G.hash_to_scalar(G.g, ys[0], ys[1], ts[0], ts[1], msg)
    cs, ss = [0, 0], [0, 0]
    cs[1 - b], ss[1 - b] = sim.c, sim.s
    cs[b] = (c - sim.c) % G.q
    ss[b] = schnorr_respond(G, x, r, cs[b])
    return tuple(ts), tuple(cs), tuple(ss)


def or_fs_verify(G: SchnorrGroup, ys, proof, msg: str = "") -> bool:
    ts, cs, ss = proof
    c = G.hash_to_scalar(G.g, ys[0], ys[1], ts[0], ts[1], msg)
    return or_check(G, ys, ts, c, cs, ss)


if __name__ == "__main__":
    G = MEDIUM
    x = G.rand_scalar()
    y = G.exp(G.g, x)
    tr = schnorr_run(G, x)
    print("honest transcript accepted:", schnorr_check(G, y, tr))
    print("simulated transcript accepted (no witness):", schnorr_check(G, y, schnorr_simulate(G, y)))
    r, t = schnorr_commit(G)
    t1 = Transcript(t, 5, schnorr_respond(G, x, r, 5))
    t2 = Transcript(t, 9, schnorr_respond(G, x, r, 9))
    print("extractor recovers x from (t,5,s),(t,9,s'):", schnorr_extract(G, t1, t2) == x)
    print("Fiat-Shamir proof verifies:", fs_verify(G, y, fs_prove(G, x, "ctx"), "ctx"))
    yf, pf = weak_fs_forge(G)
    print("weak FS: proof for y with unknown log verifies:", fs_verify(G, yf, pf, strong=False),
          "| same proof under strong FS:", fs_verify(G, yf, pf))
    y1 = G.exp(G.g, G.rand_scalar())
    run = or_prove(G, (y, y1), 0, x)
    print("OR-proof (knows branch 0) accepted:", or_check(G, (y, y1), *run))
