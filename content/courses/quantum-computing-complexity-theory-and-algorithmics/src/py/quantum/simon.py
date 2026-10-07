"""Simon's algorithm: find the hidden period s of a 2-to-1 f with f(x) = f(x xor s) (KLM 6.5, N&C problem 6.3).

Belongs to the Part C note on Simon's algorithm (C04).

Circuit on 2n qubits: H^n on the input register, XOR oracle |x>|0> -> |x>|f(x)>,
H^n again, measure the input register. Every outcome y satisfies y.s = 0 mod 2
(uniformly over that subspace). After O(n) samples the y's span the orthogonal
complement of s with high probability; s is the unique nonzero null vector.

Implements: random_two_to_one_function, simon_oracle_permutation, simon_sample,
simon, bits_to_int.
"""
import numpy as np

from gf2 import gf2_nullspace, gf2_rank
from sim import Register


def bits_to_int(bits):
    return int("".join(str(int(b)) for b in bits), 2)


def random_two_to_one_function(n, s, rng):
    """Truth table with f(x) = f(x ^ s), otherwise injective, values in 0..2^n-1 (s != 0)."""
    assert 0 < s < 2 ** n
    table = -np.ones(2 ** n, dtype=int)
    values = list(rng.permutation(2 ** n))
    for x in range(2 ** n):
        if table[x] < 0:
            table[x] = table[x ^ s] = values.pop()
    return table


def simon_oracle_permutation(table, n):
    """Permutation on 2n qubits: |x>|y> -> |x>|y xor f(x)>."""
    N = 2 ** n
    perm = np.empty(N * N, dtype=int)
    for x in range(N):
        fx = int(table[x])
        for y in range(N):
            perm[x * N + y] = x * N + (y ^ fx)
    return perm


def simon_sample(table, n, rng, perm=None):
    """One run of the circuit: returns a bit vector y with y.s = 0 mod 2."""
    perm = simon_oracle_permutation(table, n) if perm is None else perm
    reg = Register(2 * n)
    for q in range(n):
        reg.h(q)
    reg.apply_permutation(perm, list(range(2 * n)))
    for q in range(n):
        reg.h(q)
    return np.array(reg.measure(list(range(n)), rng))


def simon(table, n, rng, max_samples=None):
    """Recover s (as an int) from at most max_samples runs; returns None if the samples did not span."""
    max_samples = 3 * n if max_samples is None else max_samples
    perm = simon_oracle_permutation(table, n)
    rows = []
    for _ in range(max_samples):
        rows.append(simon_sample(table, n, rng, perm))
        if gf2_rank(np.array(rows)) == n - 1:       # y's span s^perp: unique nonzero null vector
            null = gf2_nullspace(np.array(rows))
            return bits_to_int(null[0])
    return None


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = 4
    s = 0b1011
    table = random_two_to_one_function(n, s, rng)
    print(f"n={n}, hidden s={s:0{n}b}, table={table.tolist()}")
    for _ in range(4):
        y = simon_sample(table, n, rng)
        print("  sample y =", y.tolist(), " y.s mod 2 =", int(np.dot(y, [int(b) for b in f'{s:0{n}b}'])) % 2)
    found = simon(table, n, rng)
    print(f"recovered s = {found:0{n}b}" if found is not None else "samples did not span s^perp")
