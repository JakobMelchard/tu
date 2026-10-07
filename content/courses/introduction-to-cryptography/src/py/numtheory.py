"""Number theory for cryptography: egcd, modular inverse, fast exponentiation,
CRT, Miller-Rabin, prime generation, group order / generators, baby-step
giant-step discrete log.

Primitive: the arithmetic of Z_N^* and of prime-order subgroups of Z_p^*,
on which RSA, Diffie-Hellman, ElGamal, Schnorr and DSA are built.
Note: notes/09-number-theory.md (lectures 10 and 11).
Standard: none implemented here; the algorithms are textbook (Katz-Lindell
sec. 9.1 [S10]).  The safe-prime group they are checked against is
RFC 3526 group 14 [S26] (`dh.MODP2048`, `test_standard_vectors.py`), and
every function is cross-checked against `sympy` or Python's `pow`.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
Parameters are tiny so that attacks run in milliseconds. Not constant-time,
not side-channel safe, never use for real keys.
"""
from __future__ import annotations

import math

import rng


# ---------------------------------------------------------------- basics
def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclid: returns (g, x, y) with a*x + b*y = g = gcd(a, b)."""
    x0, x1, y0, y1 = 1, 0, 0, 1
    while b:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1          # keep the invariant a = x0*a0 + y0*b0
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def modinv(a: int, n: int) -> int:
    """a^{-1} mod n, exists iff gcd(a, n) = 1."""
    g, x, _ = egcd(a % n, n)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {n} (gcd = {g})")
    return x % n


def modexp(base: int, exp: int, n: int) -> int:
    """Square-and-multiply: O(log exp) multiplications mod n."""
    if exp < 0:
        base, exp = modinv(base, n), -exp
    result, base = 1 % n, base % n             # 1 % n: everything is 0 mod 1
    while exp:
        if exp & 1:
            result = result * base % n
        base = base * base % n
        exp >>= 1
    return result


def crt(residues: list[int], moduli: list[int]) -> int:
    """Chinese remainder theorem for pairwise coprime moduli.
    Returns the unique x in [0, prod moduli) with x = r_i mod m_i."""
    n = math.prod(moduli)
    x = 0
    for r, m in zip(residues, moduli):
        n_i = n // m
        x += r * n_i * modinv(n_i, m)     # n_i * n_i^{-1} = 1 mod m, 0 mod others
    return x % n


# ---------------------------------------------------------------- primes
def miller_rabin(n: int, rounds: int = 32) -> bool:
    """Probabilistic primality test. A composite passes one round with
    probability <= 1/4, so `rounds` rounds give error <= 4^{-rounds}."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % p == 0:
            return n == p
    # write n-1 = 2^s * d with d odd
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = 2 + rng.randbelow(n - 3)
        x = modexp(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False              # a is a witness: n is composite
    return True


def gen_prime(bits: int) -> int:
    """Random prime with exactly `bits` bits (top bit set, odd)."""
    while True:
        candidate = rng.randbits(bits) | (1 << (bits - 1)) | 1
        if miller_rabin(candidate):
            return candidate


def gen_safe_prime(bits: int) -> int:
    """Safe prime p = 2q + 1 with q prime; then Z_p^* has a subgroup of
    prime order q, which is what DH / ElGamal / Schnorr want."""
    while True:
        q = gen_prime(bits - 1)
        p = 2 * q + 1
        if miller_rabin(p):
            return p


def factorize(n: int) -> dict[int, int]:
    """Trial division; only for the small numbers used in demos."""
    factors: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def euler_phi(n: int) -> int:
    return math.prod((p - 1) * p ** (k - 1) for p, k in factorize(n).items())


# ---------------------------------------------------------------- groups
def order(g: int, p: int) -> int:
    """Order of g in Z_p^* for prime p: smallest d | p-1 with g^d = 1."""
    d = p - 1
    for q in factorize(p - 1):
        while d % q == 0 and modexp(g, d // q, p) == 1:
            d //= q                       # strip q while g^(d/q) is still 1
    return d


def order_mod(a: int, n: int) -> int:
    """Order of a in Z_n^* for any n (a coprime to n): the smallest d dividing
    phi(n) with a^d = 1.  `order` above is the prime-modulus special case."""
    if math.gcd(a, n) != 1:
        raise ValueError(f"{a} is not a unit mod {n}")
    d = euler_phi(n)
    for q in factorize(d):
        while d % q == 0 and modexp(a, d // q, n) == 1:
            d //= q
    return d


def is_generator(g: int, p: int) -> bool:
    """g generates Z_p^* iff g^((p-1)/q) != 1 for every prime q | p-1."""
    return all(modexp(g, (p - 1) // q, p) != 1 for q in factorize(p - 1))


def find_generator(p: int) -> int:
    """Smallest generator of Z_p^* (p prime, p-1 must be small enough to factor)."""
    for g in range(2, p):
        if is_generator(g, p):
            return g
    raise ValueError("no generator found (is p prime?)")


def subgroup_generator(p: int, q: int) -> int:
    """Generator of the order-q subgroup of Z_p^* where q | p-1."""
    while True:
        h = 2 + rng.randbelow(p - 3)
        g = modexp(h, (p - 1) // q, p)
        if g != 1:
            return g


def bsgs(g: int, h: int, p: int, n: int | None = None) -> int:
    """Baby-step giant-step: find x with g^x = h mod p, 0 <= x < n.
    Time and memory O(sqrt(n)); n defaults to the group order p-1."""
    n = n or (p - 1)
    m = math.isqrt(n) + 1
    baby = {}
    cur = 1
    for j in range(m):                    # baby steps: g^j for j < m
        baby.setdefault(cur, j)
        cur = cur * g % p
    factor = modexp(g, -m, p)             # g^{-m}
    cur = h
    for i in range(m):                    # giant steps: h * g^{-im}
        if cur in baby:
            return i * m + baby[cur]
        cur = cur * factor % p
    raise ValueError("no discrete log found")


if __name__ == "__main__":
    rng.seed(2027)                        # reproducible output; see rng.py
    print("egcd(240, 46) =", egcd(240, 46))
    print("3^-1 mod 11 =", modinv(3, 11))
    print("CRT x=2 (mod 3), x=3 (mod 5), x=2 (mod 7):", crt([2, 3, 2], [3, 5, 7]))
    p = gen_safe_prime(40)
    print(f"safe prime p = {p}, q = {(p - 1) // 2}")
    print("Carmichael 561 prime?", miller_rabin(561), "| 2^1000+297 prime?", miller_rabin(2 ** 1000 + 297))
    print("Z_23^*: generator", find_generator(23), "order of 2 =", order(2, 23), "phi(23) =", euler_phi(23))
    # the two by-hand exam items of note 00: reduce by the ORDER, not by phi
    print("[3^1000000 mod 22] =", modexp(3, 10 ** 6, 22), "since ord(3) =", order_mod(3, 22),
          "| [2^63 mod 11] =", modexp(2, 63, 11), "since ord(2) =", order_mod(2, 11))
    g, x = find_generator(1000003), 123456
    print("bsgs recovers x =", bsgs(g, modexp(g, x, 1000003), 1000003))
