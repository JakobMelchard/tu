"""ElGamal encryption over a prime-order subgroup, IND-CPA under DDH, its
re-randomisation / malleability, hybrid KEM/DEM encryption and its CCA
break, and DHIES as the fix.

Primitive: ElGamal public-key encryption (Katz-Lindell sec. 12 [S10]),
the KEM/DEM paradigm, DHIES/ECIES.
Note: notes/10-key-exchange-pke.md (lectures 11 and 12); the DDH assumption
is notes/09-number-theory.md, the reduction notes/13-proof-toolkit.md.
Standard: ElGamal itself is not standardised.  The group can be RFC 3526
group 14 [S26] (`ElGamalParams.from_values(dh.MODP2048, 2)`), where the
ElGamal mask h^y is cross-checked against the `cryptography` package's DH;
the KEM/DEM key derivation is HKDF, RFC 5869 [S34] (`mac.hkdf`).

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
Messages must be *group elements*: `encode` maps an integer into the
order-q subgroup (the quadratic residues), and encrypting anything outside
it leaks a bit (`test_elgamal.py`).  `ElGamalParams(bits)` makes toy groups.
"""
from __future__ import annotations

import rng
from dh import DHParams
from mac import encrypt_then_mac, etm_decrypt, hkdf
from numtheory import modexp, modinv


class ElGamalParams(DHParams):
    """(p, q, g): p = 2q + 1 a safe prime, g of order q.  The same object as a
    Diffie-Hellman group, which is the point: ElGamal is DH with the second
    message replaced by a masked plaintext."""


def keygen(params: ElGamalParams) -> tuple[int, int]:
    """Secret x in [1, q), public h = g^x. Public key is (g, h)."""
    x = 1 + rng.randbelow(params.q - 1)
    return x, modexp(params.g, x, params.p)


def is_group_element(params: ElGamalParams, m: int) -> bool:
    """Membership in the order-q subgroup, i.e. m is a quadratic residue
    mod p (Euler's criterion m^q = 1)."""
    return 0 < m < params.p and modexp(m, params.q, params.p) == 1


def encode(params: ElGamalParams, m: int) -> int:
    """Map m in [1, q] into the subgroup: m itself if it is a residue, else
    p - m.  Exactly one of the two is, because -1 is a non-residue when
    p = 3 mod 4, which every safe prime p > 7 satisfies."""
    if not 1 <= m <= params.q:
        raise ValueError("message must lie in [1, q]")
    return m if is_group_element(params, m) else params.p - m


def decode(params: ElGamalParams, e: int) -> int:
    return e if e <= params.q else params.p - e


def encrypt(params: ElGamalParams, h: int, m: int, y: int | None = None) -> tuple[int, int]:
    """c = (g^y, m * h^y). The pair (g^y, h^y) is a DH tuple; DDH says h^y
    looks random, so it masks m. Randomised via fresh y each time."""
    y = y if y is not None else 1 + rng.randbelow(params.q - 1)
    return modexp(params.g, y, params.p), m * modexp(h, y, params.p) % params.p


def decrypt(params: ElGamalParams, x: int, ct: tuple[int, int]) -> int:
    """m = c2 / c1^x, since c1^x = g^{xy} = h^y."""
    c1, c2 = ct
    return c2 * modinv(modexp(c1, x, params.p), params.p) % params.p


def rerandomize(params: ElGamalParams, h: int, ct: tuple[int, int]) -> tuple[int, int]:
    """Produce a fresh encryption of the SAME message without knowing it:
    multiply by an encryption of 1, (g^y', h^y'). Underlies mix-nets and
    shows ElGamal is not CCA-secure."""
    c1, c2 = ct
    y2 = 1 + rng.randbelow(params.q - 1)
    return c1 * modexp(params.g, y2, params.p) % params.p, c2 * modexp(h, y2, params.p) % params.p


def malleability_demo(params: ElGamalParams, ct: tuple[int, int], factor: int) -> tuple[int, int]:
    """Multiply the plaintext by `factor` on the ciphertext: (c1, c2*factor)
    decrypts to m*factor. ElGamal is homomorphic under multiplication."""
    c1, c2 = ct
    return c1, c2 * factor % params.p


# ------------------------------------------- hybrid encryption (KEM/DEM)
def _kdf(params: ElGamalParams, *group_elements: int) -> tuple[bytes, bytes]:
    """Derive independent DEM keys (encryption, MAC) from group elements with
    HKDF (RFC 5869).  The DEM key depends on *everything* hashed, which is
    the whole difference between the two schemes below."""
    size = (params.p.bit_length() + 7) // 8
    okm = hkdf(b"".join(g.to_bytes(size, "big") for g in group_elements), 48,
               info=b"192.125 KEM/DEM")
    return okm[:16], okm[16:]


def hybrid_encrypt(params: ElGamalParams, h: int, msg: bytes,
                   y: int | None = None) -> tuple[tuple[int, int], tuple[bytes, bytes]]:
    """The textbook KEM/DEM split, in the exact form the final exam of
    26 January 2024 question 5b puts it [S12]: encapsulate a random group
    element k with ElGamal, then encrypt the message under keys derived
    from k with a CCA-secure DEM (encrypt-then-MAC).

        c = ( Enc_pk(k) , Enc'_k(m) )

    It is CPA-secure, and it is NOT CCA-secure -- see `hybrid_cca_attack`.
    """
    k = modexp(params.g, 1 + rng.randbelow(params.q - 1), params.p)   # k in G
    kem = encrypt(params, h, k, y)
    return kem, encrypt_then_mac(*_kdf(params, k), msg)


def hybrid_decrypt(params: ElGamalParams, x: int, ct) -> bytes:
    kem, (body, tag) = ct
    return etm_decrypt(*_kdf(params, decrypt(params, x, kem)), body, tag)


def hybrid_cca_attack(params: ElGamalParams, h: int, ct, dec_oracle) -> bytes:
    """Break the scheme above in the CCA game with one oracle query.

    ElGamal is re-randomisable, so from the challenge ((c1,c2), dem) the
    adversary forms ((c1*g^s, c2*h^s), dem) -- a *different* ciphertext that
    encapsulates the *same* k, hence decrypts to the same m.  It is not the
    challenge ciphertext, so the decryption oracle answers it, and the
    adversary reads off the plaintext.  Advantage 1/2.

    The moral is note 10's: a CCA-secure DEM does not rescue a malleable
    KEM.  The composition theorem needs the KEM to be CCA-secure too.
    """
    kem, dem = ct
    return dec_oracle((rerandomize(params, h, kem), dem))


# ------------------------------------------------------------- DHIES/ECIES
def dhies_encrypt(params: ElGamalParams, h: int, msg: bytes,
                  y: int | None = None) -> tuple[int, tuple[bytes, bytes]]:
    """DHIES (lecture 12; ECIES when the group is an elliptic curve).  The
    fix for the scheme above: derive the DEM key from *both* c1 = g^y and
    the DH value h^y, rather than encapsulating an independent k.

        c = ( g^y , Enc'_{H(g^y, h^y)}(m) )

    Now mauling c1 changes the derived key, so the re-randomisation attack
    produces a ciphertext that fails the DEM's authentication check instead
    of decrypting to m.  CCA-secure in the random-oracle model under the
    gap/hashed-DH assumption.
    """
    y = y if y is not None else 1 + rng.randbelow(params.q - 1)
    c1 = modexp(params.g, y, params.p)
    return c1, encrypt_then_mac(*_kdf(params, c1, modexp(h, y, params.p)), msg)


def dhies_decrypt(params: ElGamalParams, x: int, ct) -> bytes:
    c1, (body, tag) = ct
    return etm_decrypt(*_kdf(params, c1, modexp(c1, x, params.p)), body, tag)


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    params = ElGamalParams(128)
    x, h = keygen(params)
    m = encode(params, 123456789)
    ct = encrypt(params, h, m)
    print("roundtrip:", decode(params, decrypt(params, x, ct)) == 123456789)
    print("randomised:", encrypt(params, h, m) != encrypt(params, h, m))

    # re-randomisation: different ciphertext, same plaintext
    ct2 = rerandomize(params, h, ct)
    print("re-randomised ciphertext differs:", ct2 != ct,
          "| same plaintext:", decrypt(params, x, ct2) == m)

    # malleability: multiply the (encoded) plaintext by 4 = 2^2, a residue
    ct3 = malleability_demo(params, ct, 4)
    print("malleability: decrypt(scaled) == 4*m:", decrypt(params, x, ct3) == 4 * m % params.p)

    # hybrid KEM/DEM: CPA-secure, but a re-randomised KEM breaks CCA
    msg = b"the bid is 4200 euro"
    hct = hybrid_encrypt(params, h, msg)
    print("hybrid roundtrip:", hybrid_decrypt(params, x, hct) == msg)
    oracle = lambda c: hybrid_decrypt(params, x, c)
    print("hybrid CCA attack recovers the plaintext:",
          hybrid_cca_attack(params, h, hct, oracle) == msg)

    # DHIES binds c1 into the key derivation, so the same attack fails
    dct = dhies_encrypt(params, h, msg)
    print("DHIES roundtrip:", dhies_decrypt(params, x, dct) == msg)
    mauled = (dct[0] * modexp(params.g, 7, params.p) % params.p, dct[1])
    try:
        dhies_decrypt(params, x, mauled)
        print("DHIES: mauled ciphertext NOT rejected (bug)")
    except ValueError:
        print("DHIES: mauled ciphertext rejected by the DEM tag")
