"""Prime-order Schnorr groups shared by the Sigma-protocol, commitment, ROM and
OT modules.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). The groups are
the order-q subgroup of Z_p^* for a safe prime p = 2q + 1 [S4 sec. 10.5].
TINY and TOY are small enough to enumerate exhaustively, which is what the
tests exploit (perfect HVZK, perfect hiding). MEDIUM is 128 bits: too small for
real use (discrete log in it is a laptop computation), large enough that the
demos do not hit accidental collisions. Nothing here is constant-time.
"""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class SchnorrGroup:
    p: int  # safe prime p = 2q + 1
    q: int  # prime order of the subgroup
    g: int  # generator of the order-q subgroup (a quadratic residue != 1)

    def exp(self, base: int, e: int) -> int:
        return pow(base, e % self.q, self.p)

    def mul(self, a: int, b: int) -> int:
        return a * b % self.p

    def inv(self, a: int) -> int:
        return pow(a, -1, self.p)

    def rand_scalar(self) -> int:
        return secrets.randbelow(self.q)

    def is_member(self, a: int) -> bool:
        # QR test: a^q = 1 iff a lies in the order-q subgroup
        return 0 < a < self.p and pow(a, self.q, self.p) == 1

    def hash_to_scalar(self, *parts: object) -> int:
        """H: {0,1}* -> Z_q, the random oracle of the Fiat-Shamir transform."""
        h = hashlib.sha256()
        for x in parts:
            b = str(x).encode()
            h.update(len(b).to_bytes(4, "big") + b)  # length-prefixed: unambiguous
        return int.from_bytes(h.digest(), "big") % self.q

    def hash_to_group(self, label: str) -> int:
        """A group element whose discrete log nobody knows (square of a hash)."""
        ctr = 0
        while True:
            d = hashlib.sha256(f"{label}|{ctr}".encode()).digest()
            x = int.from_bytes(d, "big") % self.p
            if x > 1:
                h = x * x % self.p
                if h != 1:
                    return h
            ctr += 1

    def dlog_bruteforce(self, y: int) -> int:
        """Only for TINY/TOY: exhaustive search, used to check extractors."""
        acc = 1
        for x in range(self.q):
            if acc == y:
                return x
            acc = acc * self.g % self.p
        raise ValueError("not in subgroup")


TINY = SchnorrGroup(p=23, q=11, g=4)
TOY = SchnorrGroup(p=2039, q=1019, g=4)
MEDIUM = SchnorrGroup(
    p=170141183460469231731687303715884114527,
    q=85070591730234615865843651857942057263,
    g=4,
)


if __name__ == "__main__":
    for name, G in (("TINY", TINY), ("TOY", TOY), ("MEDIUM", MEDIUM)):
        print(f"{name}: p = {G.p} ({G.p.bit_length()} bits), q = {G.q}, g = {G.g},"
              f" g^q mod p = {pow(G.g, G.q, G.p)}")
    print("TOY: log_g of hash_to_group('h') by brute force =", TOY.dlog_bruteforce(TOY.hash_to_group("h")))
