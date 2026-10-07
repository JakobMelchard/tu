"""Elliptic curves: Weierstrass group law over a small prime field, scalar
multiplication (double-and-add and Montgomery ladder), brute-force point
counting, ECDH, EC-Schnorr, ECDSA and its nonce-reuse break; then the two real
curves of RFC 7748 / RFC 8032 written from the RFC text (X25519, Ed25519).

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Toy curves have
~10^3 points, so every discrete log is a table lookup. The Curve25519 code
follows RFC 7748 sec. 5 and RFC 8032 sec. 5.1 [S22, S23] and reproduces their
test vectors, but it is NOT constant-time (Python big ints, affine inversions,
data-dependent branches) and must never touch a real key.
Group law: [S4 sec. 15.2]; ladder: [S22 sec. 5], [S20].
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

INF = None  # the point at infinity O


@dataclass(frozen=True)
class Curve:
    """E: y^2 = x^3 + a x + b over F_p, p > 3 prime [S4 Def. 15.1]."""
    p: int
    a: int
    b: int

    def __post_init__(self):
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular curve: 4a^3 + 27b^2 = 0")

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        x, y = P
        return (y * y - x**3 - self.a * x - self.b) % self.p == 0

    def neg(self, P):
        return INF if P is INF else (P[0], -P[1] % self.p)

    def add(self, P, Q):
        """Chord-and-tangent rule, the three cases of [S4 sec. 15.2]."""
        if P is INF:
            return Q
        if Q is INF:
            return P
        p = self.p
        (x1, y1), (x2, y2) = P, Q
        if x1 == x2 and (y1 + y2) % p == 0:
            return INF  # P + (-P), including 2P for y1 = 0
        if x1 != x2:
            s = (y1 - y2) * pow(x1 - x2, -1, p) % p          # chord slope
        else:
            s = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p  # tangent slope
        x3 = (s * s - x1 - x2) % p
        return x3, (s * (x1 - x3) - y1) % p

    def mul(self, k: int, P):
        """Left-to-right double-and-add: the branch on each key bit leaks k."""
        R = INF
        for bit in bin(k)[2:] if k > 0 else "":
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R if k >= 0 else self.neg(self.mul(-k, P))

    def ladder(self, k: int, P):
        """Montgomery ladder: invariant R1 - R0 = P, one add + one double per
        bit whatever the bit is (uniform operation sequence)."""
        R0, R1 = INF, P
        for bit in bin(k)[2:] if k > 0 else "":
            if bit == "1":
                R0, R1 = self.add(R0, R1), self.add(R1, R1)
            else:
                R0, R1 = self.add(R0, R0), self.add(R0, R1)
        return R0

    def points(self) -> list:
        """All of E(F_p), by tabulating square roots: O(p) time."""
        p, roots = self.p, {}
        for y in range(p):
            roots.setdefault(y * y % p, []).append(y)
        pts = [INF]
        for x in range(p):
            pts += [(x, y) for y in roots.get((x**3 + self.a * x + self.b) % p, [])]
        return pts

    def order(self) -> int:
        return len(self.points())

    def point_order(self, P, group_order: int) -> int:
        """Smallest d | #E with dP = O (Lagrange)."""
        for d in sorted(d for d in range(1, group_order + 1) if group_order % d == 0):
            if self.mul(d, P) is INF:
                return d
        raise AssertionError("unreachable")


# A toy curve of prime order found by exhaustive search (see test_ec_toy.py):
# #E(F_1009) = N is prime, so every point != O generates the whole group.
TOY = Curve(p=1009, a=1, b=14)
TOY_N = 1013
TOY_G = (0, 425)


def _h(*parts, mod: int) -> int:
    d = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(d, "big") % mod


def keygen(E=TOY, G=TOY_G, n=TOY_N):
    d = 1 + secrets.randbelow(n - 1)
    return d, E.mul(d, G)


def ecdh(d: int, Q, E=TOY):  # both sides land on d_A d_B G
    return E.mul(d, Q)


def schnorr_sign(d, m, E=TOY, G=TOY_G, n=TOY_N):
    """EC-Schnorr in the (R, s) form that EdDSA uses: R = kG,
    e = H(R, P, m), s = k + e d mod n [S4 sec. 19.2]."""
    P = E.mul(d, G)
    k = 1 + secrets.randbelow(n - 1)
    R = E.mul(k, G)
    e = _h(R, P, m, mod=n)
    return R, (k + e * d) % n


def schnorr_verify(P, m, sig, E=TOY, G=TOY_G, n=TOY_N) -> bool:
    R, s = sig
    e = _h(R, P, m, mod=n)
    return E.mul(s, G) == E.add(R, E.mul(e, P))


def ecdsa_sign(d, m, E=TOY, G=TOY_G, n=TOY_N, k=None):
    """r = x(kG) mod n, s = k^{-1}(H(m) + r d) mod n [S4 sec. 19.3]."""
    while True:
        kk = k if k is not None else 1 + secrets.randbelow(n - 1)
        R = E.mul(kk, G)
        r = R[0] % n
        s = pow(kk, -1, n) * (_h(m, mod=n) + r * d) % n
        if r and s:
            return r, s
        if k is not None:
            raise ValueError("fixed nonce gives r = 0 or s = 0")


def ecdsa_verify(Q, m, sig, E=TOY, G=TOY_G, n=TOY_N) -> bool:
    r, s = sig
    if not (0 < r < n and 0 < s < n):
        return False
    w = pow(s, -1, n)
    X = E.add(E.mul(_h(m, mod=n) * w % n, G), E.mul(r * w % n, Q))
    return X is not INF and X[0] % n == r


def ecdsa_nonce_reuse(m1, sig1, m2, sig2, n=TOY_N) -> int:
    """Same k twice: k = (h1 - h2)/(s1 - s2), d = (s1 k - h1)/r."""
    (r, s1), (_, s2) = sig1, sig2
    h1, h2 = _h(m1, mod=n), _h(m2, mod=n)
    k = (h1 - h2) * pow(s1 - s2, -1, n) % n
    return (s1 * k - h1) * pow(r, -1, n) % n


# --- secp256k1, parameters from SEC 2 sec. 2.4.1 [S21] ---------------------
SECP256K1 = Curve(p=2**256 - 2**32 - 977, a=0, b=7)
SECP256K1_G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
               0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
SECP256K1_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# --- Curve25519 / X25519, RFC 7748 sec. 5 [S22] ----------------------------
P25519 = 2**255 - 19


def x25519(k: bytes, u: bytes) -> bytes:
    """X25519(k, u): clamp k, then the x-only Montgomery ladder of RFC 7748
    sec. 5 with a24 = 121665. The cswap is arithmetic here only in spirit."""
    kb = bytearray(k)
    kb[0] &= 248
    kb[31] &= 127
    kb[31] |= 64
    k_int = int.from_bytes(kb, "little")
    x1 = int.from_bytes(u, "little") & ((1 << 255) - 1)  # mask the top bit
    p = P25519
    x2, z2, x3, z3, swap = 1, 0, x1, 1, 0
    for t in reversed(range(255)):
        kt = (k_int >> t) & 1
        swap ^= kt
        if swap:
            x2, x3, z2, z3 = x3, x2, z3, z2
        swap = kt
        A, B = (x2 + z2) % p, (x2 - z2) % p
        AA, BB = A * A % p, B * B % p
        E = (AA - BB) % p
        C, D = (x3 + z3) % p, (x3 - z3) % p
        DA, CB = D * A % p, C * B % p
        x3, z3 = (DA + CB) ** 2 % p, x1 * (DA - CB) ** 2 % p
        x2, z2 = AA * BB % p, E * (AA + 121665 * E) % p
    if swap:
        x2, z2 = x3, z3
    return (x2 * pow(z2, p - 2, p) % p).to_bytes(32, "little")


# --- Ed25519, RFC 8032 sec. 5.1 [S23] --------------------------------------
ED_D = -121665 * pow(121666, -1, P25519) % P25519
ED_L = 2**252 + 27742317777372353535851937790883648493
_SQRT_M1 = pow(2, (P25519 - 1) // 4, P25519)


def _ed_add(P, Q):
    """Twisted Edwards -x^2 + y^2 = 1 + d x^2 y^2: one complete formula,
    no special cases [S4 sec. 15.2.1]."""
    p, (x1, y1), (x2, y2) = P25519, P, Q
    t = ED_D * x1 * x2 * y1 * y2 % p
    return ((x1 * y2 + x2 * y1) * pow(1 + t, -1, p) % p,
            (y1 * y2 + x1 * x2) * pow(1 - t, -1, p) % p)


def _ed_mul(k: int, P):
    R = (0, 1)
    while k:
        if k & 1:
            R = _ed_add(R, P)
        P, k = _ed_add(P, P), k >> 1
    return R


def _ed_recover_x(y: int, sign: int):
    p = P25519
    u = (y * y - 1) * pow(ED_D * y * y + 1, -1, p) % p
    x = pow(u, (p + 3) // 8, p)                   # p = 5 mod 8
    if (x * x - u) % p:
        x = x * _SQRT_M1 % p
    if (x * x - u) % p or (x == 0 and sign):
        return None
    return p - x if x & 1 != sign else x


ED_B = (_ed_recover_x(4 * pow(5, -1, P25519) % P25519, 0), 4 * pow(5, -1, P25519) % P25519)


def _ed_enc(P) -> bytes:
    return (P[1] | ((P[0] & 1) << 255)).to_bytes(32, "little")


def _ed_dec(b: bytes):
    v = int.from_bytes(b, "little")
    y, sign = v & ((1 << 255) - 1), v >> 255
    if y >= P25519:
        return None
    x = _ed_recover_x(y, sign)
    return None if x is None else (x, y)


def _h512(*bs) -> int:
    return int.from_bytes(hashlib.sha512(b"".join(bs)).digest(), "little")


def _ed_expand(sk: bytes):
    h = hashlib.sha512(sk).digest()
    a = int.from_bytes(h[:32], "little")
    a = (a & ((1 << 254) - 8)) | (1 << 254)     # clamp
    return a, h[32:]


def ed25519_public(sk: bytes) -> bytes:
    return _ed_enc(_ed_mul(_ed_expand(sk)[0], ED_B))


def ed25519_sign(sk: bytes, m: bytes) -> bytes:
    """Deterministic Schnorr: r = H(prefix || m), S = r + H(R || A || m) a."""
    a, prefix = _ed_expand(sk)
    A = _ed_enc(_ed_mul(a, ED_B))
    r = _h512(prefix, m) % ED_L
    R = _ed_enc(_ed_mul(r, ED_B))
    k = _h512(R, A, m) % ED_L
    return R + ((r + k * a) % ED_L).to_bytes(32, "little")


def ed25519_verify(pk: bytes, m: bytes, sig: bytes) -> bool:
    """Cofactored check [8][S]B = [8]R + [8][k]A (RFC 8032 sec. 5.1.7)."""
    A, R = _ed_dec(pk), _ed_dec(sig[:32])
    S = int.from_bytes(sig[32:], "little")
    if A is None or R is None or S >= ED_L:
        return False
    k = _h512(sig[:32], pk, m) % ED_L
    lhs = _ed_mul(8 * S, ED_B)
    return lhs == _ed_mul(8, _ed_add(R, _ed_mul(k, A)))


if __name__ == "__main__":
    E, G, n = TOY, TOY_G, TOY_N
    print(f"toy curve y^2 = x^3 + {E.a}x + {E.b} over F_{E.p}: #E = {E.order()}"
          f" (Hasse window {E.p + 1} +- {2 * E.p ** 0.5:.1f})")
    print("G =", G, " n G =", E.mul(n, G), " ladder == double-and-add:",
          E.ladder(777, G) == E.mul(777, G))
    da, Qa = keygen()
    db, Qb = keygen()
    print("ECDH agree:", ecdh(da, Qb) == ecdh(db, Qa))
    sig = schnorr_sign(da, "hello")
    print("Schnorr ok:", schnorr_verify(Qa, "hello", sig), " tampered:", schnorr_verify(Qa, "hellO", sig))
    s1, s2 = ecdsa_sign(da, "m1", k=42), ecdsa_sign(da, "m2", k=42)
    print("ECDSA nonce reuse recovers d:", ecdsa_nonce_reuse("m1", s1, "m2", s2) == da)
    base = (9).to_bytes(32, "little")
    a, b = secrets.token_bytes(32), secrets.token_bytes(32)
    print("X25519 DH agree:", x25519(a, x25519(b, base)) == x25519(b, x25519(a, base)))
    sk = secrets.token_bytes(32)
    print("Ed25519 sign/verify:", ed25519_verify(ed25519_public(sk), b"m", ed25519_sign(sk, b"m")))
