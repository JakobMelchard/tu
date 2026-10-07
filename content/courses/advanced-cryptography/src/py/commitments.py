"""Commitments: Pedersen (perfectly hiding, computationally binding under DL),
its trapdoor equivocation, a hash commitment (ROM), vector Pedersen, and the
Bulletproofs inner-product argument (Protocols 1 and 2 of [S19 sec. 3]) made
non-interactive with Fiat-Shamir.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). The group is
the order-q subgroup of Z_p^* (groups.py), not an elliptic curve; generators
come from hash_to_group so nobody knows their mutual discrete logs. The
inner-product argument here is sound but NOT zero-knowledge (as in [S19]:
zero knowledge is added by the range-proof layer on top, not shown).
"""
from __future__ import annotations

import hashlib
import secrets

from groups import MEDIUM, SchnorrGroup


# --- Pedersen [S30], [S4 sec. 19.5 context] ---------------------------------

def pedersen_setup(G: SchnorrGroup, label: str = "pedersen-h") -> int:
    return G.hash_to_group(label)


def pedersen_commit(G: SchnorrGroup, h: int, m: int, r: int | None = None):
    """C = g^m h^r. Returns (C, r)."""
    r = G.rand_scalar() if r is None else r
    return G.mul(G.exp(G.g, m), G.exp(h, r)), r


def pedersen_open(G: SchnorrGroup, h: int, C: int, m: int, r: int) -> bool:
    return pedersen_commit(G, h, m, r)[0] == C


def pedersen_dlog_from_double_opening(G: SchnorrGroup, m1, r1, m2, r2) -> int:
    """Binding reduction: g^m1 h^r1 = g^m2 h^r2, m1 != m2  =>  log_g h
    = (m1 - m2)/(r2 - r1). So breaking binding solves DL."""
    return (m1 - m2) * pow(r2 - r1, -1, G.q) % G.q


def pedersen_equivocate(G: SchnorrGroup, tau: int, m: int, r: int, m_new: int) -> int:
    """With the trapdoor tau = log_g h anyone can open C to any m_new:
    m + tau r = m_new + tau r'  =>  r' = r + (m - m_new)/tau."""
    return (r + (m - m_new) * pow(tau, -1, G.q)) % G.q


def hash_commit(m: bytes, r: bytes | None = None):
    """C = SHA-256(r || m) with 32 random bytes r: hiding in the ROM,
    binding by collision resistance (the dual trade-off to Pedersen)."""
    r = secrets.token_bytes(32) if r is None else r
    return hashlib.sha256(r + m).digest(), r


# --- vector Pedersen and the inner-product argument [S19 sec. 3] ------------

def generators(G: SchnorrGroup, n: int, label: str) -> list[int]:
    return [G.hash_to_group(f"{label}-{i}") for i in range(n)]


def multiexp(G: SchnorrGroup, bases, exps) -> int:
    acc = 1
    for b, e in zip(bases, exps):
        acc = acc * G.exp(b, e) % G.p
    return acc


def ip(a, b, q) -> int:
    return sum(x * y for x, y in zip(a, b)) % q


def _challenge(G: SchnorrGroup, *parts) -> int:
    while True:
        x = G.hash_to_scalar("ipa", *parts)
        if x:
            return x
        parts = parts + ("again",)


def ipa_prove(G: SchnorrGroup, g, h, u, P, a, b):
    """Protocol 2: prove knowledge of a, b with P = g^a h^b u^<a,b>.
    Each round halves n and sends (L, R); the tail sends the scalars a, b.
    Proof size 2 log2(n) group elements + 2 scalars."""
    q, Ls, Rs = G.q, [], []
    g, h, a, b = list(g), list(h), list(a), list(b)
    while len(a) > 1:
        n2 = len(a) // 2
        cL = ip(a[:n2], b[n2:], q)
        cR = ip(a[n2:], b[:n2], q)
        L = multiexp(G, g[n2:] + h[:n2] + [u], a[:n2] + b[n2:] + [cL])
        R = multiexp(G, g[:n2] + h[n2:] + [u], a[n2:] + b[:n2] + [cR])
        x = _challenge(G, P, L, R)            # Fiat-Shamir for the verifier's x
        xi = pow(x, -1, q)
        g = [G.mul(G.exp(g[i], xi), G.exp(g[n2 + i], x)) for i in range(n2)]
        h = [G.mul(G.exp(h[i], x), G.exp(h[n2 + i], xi)) for i in range(n2)]
        P = G.mul(G.mul(G.exp(L, x * x), P), G.exp(R, xi * xi))
        a = [(a[i] * x + a[n2 + i] * xi) % q for i in range(n2)]
        b = [(b[i] * xi + b[n2 + i] * x) % q for i in range(n2)]
        Ls.append(L)
        Rs.append(R)
    return Ls, Rs, a[0], b[0]


def ipa_verify(G: SchnorrGroup, g, h, u, P, proof) -> bool:
    Ls, Rs, a, b = proof
    q, g, h = G.q, list(g), list(h)
    if len(g) != 2 ** len(Ls):
        return False
    for L, R in zip(Ls, Rs):
        n2 = len(g) // 2
        x = _challenge(G, P, L, R)
        xi = pow(x, -1, q)
        g = [G.mul(G.exp(g[i], xi), G.exp(g[n2 + i], x)) for i in range(n2)]
        h = [G.mul(G.exp(h[i], x), G.exp(h[n2 + i], xi)) for i in range(n2)]
        P = G.mul(G.mul(G.exp(L, x * x), P), G.exp(R, xi * xi))
    return P == multiexp(G, [g[0], h[0], u], [a, b, a * b % q])


def ipa_relation2_prove(G: SchnorrGroup, g, h, u, P, c, a, b):
    """Protocol 1: for P = g^a h^b and a claimed c = <a,b>, the verifier's
    x (here Fiat-Shamir) moves c into the commitment: P' = P u^{x c},
    then Protocol 2 runs with base u^x."""
    x = _challenge(G, "rel2", P, c)
    ux = G.exp(u, x)
    return ipa_prove(G, g, h, ux, G.mul(P, G.exp(ux, c)), a, b)


def ipa_relation2_verify(G: SchnorrGroup, g, h, u, P, c, proof) -> bool:
    x = _challenge(G, "rel2", P, c)
    ux = G.exp(u, x)
    return ipa_verify(G, g, h, ux, G.mul(P, G.exp(ux, c)), proof)


if __name__ == "__main__":
    G = MEDIUM
    h = pedersen_setup(G)
    C, r = pedersen_commit(G, h, 42)
    print("Pedersen opens:", pedersen_open(G, h, C, 42, r), "| wrong m:", pedersen_open(G, h, C, 43, r))
    C1, r1 = pedersen_commit(G, h, 10)
    C2, r2 = pedersen_commit(G, h, 32)
    print("homomorphic C1*C2 opens to 42:", pedersen_open(G, h, G.mul(C1, C2), 42, (r1 + r2) % G.q))
    tau = G.rand_scalar()
    ht = G.exp(G.g, tau)
    C, r = pedersen_commit(G, ht, 1)
    r_new = pedersen_equivocate(G, tau, 1, r, 999)
    print("with trapdoor, same C opens to 999:", pedersen_open(G, ht, C, 999, r_new))
    n = 16
    g, hh, u = generators(G, n, "g"), generators(G, n, "h"), G.hash_to_group("u")
    a = [G.rand_scalar() for _ in range(n)]
    b = [G.rand_scalar() for _ in range(n)]
    P = multiexp(G, g + hh, a + b)
    c = ip(a, b, G.q)
    pf = ipa_relation2_prove(G, g, hh, u, P, c, a, b)
    print(f"IPA n={n}: {len(pf[0]) + len(pf[1])} group elements + 2 scalars,"
          f" verifies: {ipa_relation2_verify(G, g, hh, u, P, c, pf)},"
          f" wrong c: {ipa_relation2_verify(G, g, hh, u, P, (c + 1) % G.q, pf)}")
