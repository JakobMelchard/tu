"""Diffie-Hellman key exchange over a safe-prime group, plus a
man-in-the-middle demonstration (DH gives no authentication on its own).

Primitive: unauthenticated Diffie-Hellman key agreement, g^(xy) in the
order-q subgroup of Z_p^* with p = 2q + 1.
Note: notes/10-key-exchange-pke.md (lecture 11); the group theory is
notes/09-number-theory.md, the missing authentication is note 12.
Standard: the group `MODP2048` is RFC 3526 sec. 3, group 14 [S26], checked
against the vendored RFC text in test_standard_vectors.py.  The exchange is
the textbook one [S51]; `shared_secret` is cross-checked against the
`cryptography` package's DH (OpenSSL) in test_dh.py.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
`DHParams(bits)` generates tiny groups so the demo is instant; only the RFC
group has a realistic size.  The key derivation is a bare SHA-256 of the
shared value; real protocols use HKDF (`mac.hkdf`, RFC 5869) over the whole
transcript, and real DH must authenticate the exchange (note 12).
"""
from __future__ import annotations

import hashlib

import rng
from numtheory import gen_safe_prime, modexp, subgroup_generator

# RFC 3526 sec. 3: p = 2^2048 - 2^1984 - 1 + 2^64 * (floor(2^1918 pi) + 124476),
# generator 2.  p and (p-1)/2 are both prime, and 2 generates the order-q
# subgroup (it is a quadratic residue because p = 7 mod 8).
MODP2048 = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74"
    "020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F1437"
    "4FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF05"
    "98DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB"
    "9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF695581718"
    "3995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)


class DHParams:
    """Group (p, q, g) where p = 2q+1 is a safe prime and g generates the
    order-q subgroup. Security rests on the DDH assumption in that subgroup."""

    def __init__(self, bits: int = 256):
        self.p = gen_safe_prime(bits)
        self.q = (self.p - 1) // 2
        self.g = subgroup_generator(self.p, self.q)

    @classmethod
    def from_values(cls, p: int, g: int) -> "DHParams":
        """A fixed, published group, e.g. `DHParams.from_values(MODP2048, 2)`."""
        obj = cls.__new__(cls)
        obj.p, obj.q, obj.g = p, (p - 1) // 2, g
        return obj


def rfc3526_group14() -> DHParams:
    return DHParams.from_values(MODP2048, 2)


def keypair(params: DHParams, x: int | None = None) -> tuple[int, int]:
    """Secret x in [1, q), public X = g^x mod p.  Pass `x` only to replay a
    known exchange."""
    x = x if x is not None else 1 + rng.randbelow(params.q - 1)
    return x, modexp(params.g, x, params.p)


def shared_value(params: DHParams, my_secret: int, their_public: int) -> bytes:
    """g^{xy} = (g^y)^x = (g^x)^y as a big-endian string of |p| bytes, the
    form in which OpenSSL (and TLS) hand it on.  Rejects public values
    outside [2, p-2], the minimal check every implementation must make."""
    if not 1 < their_public < params.p - 1:
        raise ValueError("public value out of range")
    s = modexp(their_public, my_secret, params.p)
    return s.to_bytes((params.p.bit_length() + 7) // 8, "big")


def shared_secret(params: DHParams, my_secret: int, their_public: int) -> bytes:
    """Both sides hash the shared value to a 32-byte key."""
    return hashlib.sha256(shared_value(params, my_secret, their_public)).digest()


def mitm_demo(params: DHParams):
    """Unauthenticated DH: an active attacker sitting between Alice and Bob
    runs a separate exchange with each, so both derive keys shared with the
    attacker, not with each other. Returns the four keys involved."""
    a, A = keypair(params)
    b, B = keypair(params)
    e, E = keypair(params)                       # attacker's ephemeral key

    # Attacker replaces A->Bob and B->Alice with E.
    alice_key = shared_secret(params, a, E)      # Alice thinks she talks to Bob
    bob_key = shared_secret(params, b, E)        # Bob thinks he talks to Alice
    attacker_key_with_alice = shared_secret(params, e, A)
    attacker_key_with_bob = shared_secret(params, e, B)
    return {
        "alice": alice_key,
        "bob": bob_key,
        "attacker_alice": attacker_key_with_alice,
        "attacker_bob": attacker_key_with_bob,
    }


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    params = rfc3526_group14()
    print(f"RFC 3526 group 14: |p| = {params.p.bit_length()} bits, g = {params.g}")

    a, A = keypair(params)
    b, B = keypair(params)
    ka = shared_secret(params, a, B)
    kb = shared_secret(params, b, A)
    print("\nhonest exchange, keys match:", ka == kb)
    print("shared key:", ka.hex())

    keys = mitm_demo(params)
    print("\nMITM: Alice's key equals attacker's key with Alice:",
          keys["alice"] == keys["attacker_alice"])
    print("MITM: Bob's key equals attacker's key with Bob:",
          keys["bob"] == keys["attacker_bob"])
    print("MITM: Alice and Bob DON'T share a key:", keys["alice"] != keys["bob"])
