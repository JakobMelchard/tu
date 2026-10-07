"""LCG structure: full-period conditions and the lattice of k-tuples (topic 06).

Two published results about linear congruential generators, implemented so they
can be checked rather than believed:

* Hull & Dobell (1962) [S29]: x <- (a x + c) mod m has full period m for every
  seed iff gcd(c, m) = 1, a = 1 (mod p) for every prime p | m, and a = 1 (mod 4)
  if 4 | m.
* Marsaglia (1968) [S27]: overlapping k-tuples of an LCG lie on a lattice, and
  therefore on at most (k! m)^(1/k) parallel hyperplanes. For RANDU
  (a = 65539 = 2^16 + 3, c = 0, m = 2^31) the lattice is visible in the
  recurrence itself: x_{k+2} = 6 x_{k+1} - 9 x_k (mod 2^31), so every triple
  lies on one of 15 planes.

Run `python3 lattice.py` for the demo. Tests: test_lattice.py.
"""
import math

import numpy as np

# RANDU, the generator Marsaglia used as the cautionary example [S27].
RANDU = (65539, 0, 2**31)
# "minstd" of Park & Miller (1988) [S28]; std::minstd_rand0 in C++ [S14].
MINSTD0 = (16807, 0, 2**31 - 1)
# std::minstd_rand in C++ [S14] (Lewis-Goodman-Miller multiplier).
MINSTD = (48271, 0, 2**31 - 1)


def lcg_sequence(seed, a, c, m, n):
    """n successive states of x <- (a x + c) mod m, starting after `seed`."""
    out = np.empty(n, dtype=np.int64)
    x = seed
    for i in range(n):
        x = (a * x + c) % m
        out[i] = x
    return out


def prime_factors(n):
    """The distinct prime factors of n > 1."""
    fs, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            fs.add(d)
            n //= d
        d += 1
    if n > 1:
        fs.add(n)
    return fs


def hull_dobell(a, c, m):
    """True iff the LCG (a, c, m) has full period m for every seed [S29].

    Conditions: gcd(c, m) = 1; a - 1 divisible by every prime factor of m;
    a - 1 divisible by 4 if m is.
    """
    if np.gcd(c, m) != 1:
        return False
    if any((a - 1) % p for p in prime_factors(m)):
        return False
    if m % 4 == 0 and (a - 1) % 4:
        return False
    return True


def period(seed, a, c, m, limit=None):
    """Measured period of the state sequence from `seed` (brute force)."""
    limit = limit or m + 1
    x, seen = seed, {}
    for i in range(limit):
        if x in seen:
            return i - seen[x]
        seen[x] = i
        x = (a * x + c) % m
    return None


def marsaglia_plane_bound(k, m):
    """Marsaglia's upper bound (k! m)^(1/k) on the number of hyperplanes that
    can hold every k-tuple of an LCG with modulus m [S27]."""
    return float(math.factorial(k)) ** (1.0 / k) * m ** (1.0 / k)


def randu_triple_residual(x0, n):
    """x_{k+2} - 6 x_{k+1} + 9 x_k mod 2^31 for RANDU, which is identically 0.

    Marsaglia's example [S27]: 65539 = 2^16 + 3, so
    a^2 = (2^16 + 3)^2 = 6(2^16 + 3) - 9 (mod 2^31), hence every RANDU triple
    satisfies a fixed integer relation with coefficients (9, -6, 1). Its
    L1 norm 1 + 6 + 9 = 16 bounds the number of planes by 15.
    """
    a, c, m = RANDU
    x = lcg_sequence(x0, a, c, m, n + 2)
    return (x[2:] - 6 * x[1:-1] + 9 * x[:-2]) % m


def randu_plane_count(x0, n):
    """How many distinct planes 9 x_k - 6 x_{k+1} + x_{k+2} = j * 2^31 the
    triples actually occupy. Marsaglia: at most 15 [S27]."""
    a, c, m = RANDU
    x = lcg_sequence(x0, a, c, m, n + 2).astype(object)
    j = (9 * x[:-2] - 6 * x[1:-1] + x[2:]) // m
    return len(set(int(v) for v in j))


def _main():
    print("Hull-Dobell [S29]: full period for m = 16")
    print(f"{'a':>4}{'c':>4}  predicted  measured")
    for a, c in [(5, 1), (5, 3), (3, 1), (4, 1), (5, 2), (9, 1), (13, 1)]:
        print(f"{a:>4}{c:>4}  {str(hull_dobell(a, c, 16)):>9}  {period(0, a, c, 16):>8}")

    print("\nMarsaglia plane bound (k! m)^(1/k) [S27]")
    for m, name in [(2**31, 'RANDU  m=2^31'), (2**31 - 1, 'minstd m=2^31-1')]:
        bounds = ', '.join(f'k={k}: {marsaglia_plane_bound(k, m):.0f}' for k in (2, 3, 4, 5))
        print(f"  {name}: {bounds}")

    print("\nRANDU lattice, 100000 triples from seed 1")
    r = randu_triple_residual(1, 100_000)
    print(f"  max |x_{{k+2}} - 6 x_{{k+1}} + 9 x_k| mod 2^31 = {int(r.max())}  (Marsaglia: 0)")
    print(f"  distinct planes occupied              = {randu_plane_count(1, 100_000)}  (Marsaglia: <= 15)")

    print("\nC++ standard [rand.predef] required 10000th values [S14]")
    for (a, c, m), name, want in [(MINSTD0, 'minstd_rand0', 1043618065),
                                  (MINSTD, 'minstd_rand', 399268537)]:
        got = int(lcg_sequence(1, a, c, m, 10_000)[-1])
        print(f"  {name:<13} a={a:<6} -> {got:>10}  required {want:>10}  {'ok' if got == want else 'MISMATCH'}")


if __name__ == "__main__":
    _main()
