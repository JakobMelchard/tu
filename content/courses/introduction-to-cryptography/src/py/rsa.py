"""RSA: key generation, textbook encrypt/decrypt, CRT decryption, and the
standard classroom attacks on textbook RSA (small-e / Hastad, common
modulus, shared prime factor, homomorphic malleability).

Primitive: the RSA trapdoor permutation and textbook ("plain") RSA
encryption, with its classic attacks.
Note: notes/10-key-exchange-pke.md (lecture 12); CRT and the RSA assumption
are notes/09-number-theory.md; signatures are `signatures.py` (note 11).
Standard: the key format (n, e, d, p, q, dP, dQ, qInv) and the primitives
RSAEP / RSADP are RFC 8017 sec. 3.1-3.2 and 5.1 [S20]; the CRT exponents are
cross-checked against the `cryptography` package, which also has to accept
every generated key as a valid RSA key.  The attacks are textbook
(Katz-Lindell sec. 12.5 [S10]) plus the shared-prime scan of [S47].

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
Textbook RSA ("plain RSA", lecture 12) is deterministic and malleable and
must NEVER be used to encrypt real data; the attacks below are exactly why
RSA-OAEP exists.  The padding itself lives in `oaep.py`, implemented
against RFC 8017 sec. 7.1 rather than sketched here.
"""
from __future__ import annotations

import math

import rng
from numtheory import crt, egcd, gen_prime, modexp, modinv


# ------------------------------------------------------------- key gen
def keygen(bits: int = 512, e: int = 65537) -> dict:
    """Pick primes p, q; n = pq; phi = (p-1)(q-1); d = e^{-1} mod phi.
    Requires gcd(e, phi) = 1."""
    while True:
        p = gen_prime(bits // 2)
        q = gen_prime(bits // 2)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if egcd(e, phi)[0] == 1:
            n = p * q
            d = modinv(e, phi)
            return {"n": n, "e": e, "d": d, "p": p, "q": q,
                    "dp": d % (p - 1), "dq": d % (q - 1), "qinv": modinv(q, p)}


def encrypt(pub: dict, m: int) -> int:
    """c = m^e mod n. Deterministic -> not even EAV-secure."""
    return modexp(m, pub["e"], pub["n"])


def decrypt(priv: dict, c: int) -> int:
    return modexp(c, priv["d"], priv["n"])


def decrypt_crt(priv: dict, c: int) -> int:
    """~4x faster: decrypt mod p and mod q, recombine.  Garner's form of the
    CRT, RFC 8017 sec. 5.1.2 step 2.b: h = qInv (m1 - m2) mod p,
    m = m2 + q h.  `numtheory.crt` gives the same number the general way."""
    mp = modexp(c, priv["dp"], priv["p"])
    mq = modexp(c, priv["dq"], priv["q"])
    h = priv["qinv"] * (mp - mq) % priv["p"]
    return mq + priv["q"] * h


# ------------------------------------------------------- malleability
def malleability_demo(pub: dict, c: int, factor: int) -> int:
    """RSA is homomorphic: (m*factor)^e = m^e * factor^e, so multiplying the
    ciphertext by factor^e multiplies the plaintext by factor, all without
    the private key. Breaks CCA / non-malleability."""
    return c * modexp(factor, pub["e"], pub["n"]) % pub["n"]


# --------------------------------------------------------- small-e attack
def small_e_attack(ciphertexts: list[int], moduli: list[int], e: int) -> int:
    """Hastad broadcast: the same m sent to e recipients with exponent e.
    CRT gives m^e mod (prod n_i); since m^e < prod n_i, an integer e-th root
    recovers m exactly. Returns m."""
    combined = crt(ciphertexts, moduli)
    return _iroot(combined, e)


def small_message_attack(pub: dict, c: int, e: int) -> int:
    """If m is small enough that m^e < n, then c = m^e over the integers and
    no modular reduction happened: just take the integer e-th root."""
    return _iroot(c, e)


def _iroot(x: int, k: int) -> int:
    """Integer k-th root via binary search (exact when x is a perfect power)."""
    if x < 2:
        return x
    lo, hi = 1, 1 << ((x.bit_length() // k) + 1)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** k <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo


# ---------------------------------------------------- common modulus
def common_modulus_attack(n: int, e1: int, e2: int, c1: int, c2: int) -> int:
    """Same n, same m, two coprime exponents e1, e2. Bezout gives a, b with
    a*e1 + b*e2 = 1, then c1^a * c2^b = m^{a e1 + b e2} = m mod n."""
    g, a, b = egcd(e1, e2)
    if g != 1:
        raise ValueError("exponents must be coprime")
    # negative exponents use the modular inverse of the ciphertext
    r1 = modexp(c1, a, n) if a >= 0 else modexp(modinv(c1, n), -a, n)
    r2 = modexp(c2, b, n) if b >= 0 else modexp(modinv(c2, n), -b, n)
    return r1 * r2 % n


# ------------------------------------------------ shared prime factor
def shared_prime_attack(n1: int, n2: int, e1: int, e2: int) -> tuple[dict, dict]:
    """Two moduli generated with a faulty RNG share one prime.  gcd(N1, N2)
    is that prime -- a single Euclid run, no factoring -- and both private
    keys fall out.  This is the exam question of 26 Jan 2024, and it is not
    hypothetical: large-scale scans of TLS/SSH keys have repeatedly found
    colliding primes from low-entropy embedded RNGs.

    Note how much weaker this is than the common-*modulus* attack: there the
    modulus is shared deliberately, here only one prime leaks by accident,
    and yet the consequence is total.
    """
    p = math.gcd(n1, n2)
    if p == 1 or p in (n1, n2):
        raise ValueError("moduli share no non-trivial factor")
    q1, q2 = n1 // p, n2 // p
    return (_priv_from_factors(p, q1, e1), _priv_from_factors(p, q2, e2))


def _priv_from_factors(p: int, q: int, e: int) -> dict:
    phi = (p - 1) * (q - 1)
    d = modinv(e, phi)
    return {"n": p * q, "e": e, "d": d, "p": p, "q": q,
            "dp": d % (p - 1), "dq": d % (q - 1), "qinv": modinv(q, p)}


if __name__ == "__main__":
    rng.seed(2027)                               # reproducible output; see rng.py
    key = keygen(512)
    m = 42
    c = encrypt(key, m)
    print("decrypt == m:", decrypt(key, c) == m, "| CRT decrypt == m:", decrypt_crt(key, c) == m)

    # deterministic
    print("textbook RSA deterministic:", encrypt(key, m) == encrypt(key, m))

    # malleability: turn Enc(42) into Enc(42*3) without the key
    c3 = malleability_demo(key, c, 3)
    print("malleability: decrypt(c * 3^e) =", decrypt(key, c3), "(expected 126)")

    # small message / small-e cube-root attack (e=3, tiny m)
    k3 = keygen(512, e=3)
    small = 1234567
    cs = encrypt(k3, small)
    print("small-message cube-root attack recovers:", small_message_attack(k3, cs, 3) == small)

    # Hastad broadcast with e=3 across 3 moduli
    msg = 987654321
    keys = [keygen(512, e=3) for _ in range(3)]
    cts = [encrypt(k, msg) for k in keys]
    rec = small_e_attack(cts, [k["n"] for k in keys], 3)
    print("Hastad broadcast attack recovers:", rec == msg)

    # common modulus
    p, q = gen_prime(256), gen_prime(256)
    n = p * q
    e1, e2 = 3, 65537
    m2 = 555
    print("common-modulus attack recovers:",
          common_modulus_attack(n, e1, e2, modexp(m2, e1, n), modexp(m2, e2, n)) == m2)

    # shared prime factor between two moduli
    shared = gen_prime(256)
    k1 = _priv_from_factors(shared, gen_prime(256), 65537)
    k2 = _priv_from_factors(shared, gen_prime(256), 65537)
    r1, r2 = shared_prime_attack(k1["n"], k2["n"], 65537, 65537)
    print("shared-prime attack recovers both keys:",
          r1["d"] == k1["d"] and r2["d"] == k2["d"])

    # the fix for all of the above: RSAES-OAEP, in oaep.py (RFC 8017 7.1)
    print("padding: see oaep.py for RSAES-OAEP per RFC 8017 section 7.1")
