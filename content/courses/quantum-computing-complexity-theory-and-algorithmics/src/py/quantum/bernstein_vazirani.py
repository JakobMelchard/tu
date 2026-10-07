"""Bernstein-Vazirani: recover the hidden string s of f(x) = s.x mod 2 with one query (KLM 6.5, N&C ex. 6.1).

Belongs to the Part C note on the Deutsch-Jozsa / Bernstein-Vazirani algorithms (C02).

Implements: inner_product_table, bernstein_vazirani, bits_to_int, int_to_bits.
Uses the phase oracle (or the XOR oracle with an ancilla in |->) from deutsch_jozsa.
"""
import numpy as np

from deutsch_jozsa import apply_phase_oracle, apply_xor_oracle
from sim import Register


def int_to_bits(x, n):
    return [(x >> (n - 1 - i)) & 1 for i in range(n)]


def bits_to_int(bits):
    return int("".join(str(int(b)) for b in bits), 2)


def inner_product_table(s_bits):
    """Truth table of f(x) = s.x mod 2 (bitwise AND then parity)."""
    n = len(s_bits)
    s = bits_to_int(s_bits)
    return np.array([bin(x & s).count("1") & 1 for x in range(2 ** n)])


def bernstein_vazirani(table, oracle="phase"):
    """H^n, one query, H^n: the state is exactly |s>, so the measurement is deterministic.

    (-1)^{s.x} summed against H^n gives amplitude 1 on |s> and 0 elsewhere. Returns s as a bit list.
    """
    n = int(np.log2(len(table)))
    if oracle == "phase":
        reg = Register(n)
        for q in range(n):
            reg.h(q)
        apply_phase_oracle(reg, table, range(n))
        for q in range(n):
            reg.h(q)
        probs = reg.probabilities()
    else:
        reg = Register(n + 1).x(n)
        for q in range(n + 1):
            reg.h(q)
        apply_xor_oracle(reg, table, range(n), n)
        for q in range(n):
            reg.h(q)
        probs = np.real(np.diag(reg.partial_trace(list(range(n)))))
    return int_to_bits(int(np.argmax(probs)), n)


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    for n in (3, 5):
        s = [int(b) for b in rng.integers(0, 2, n)]
        tbl = inner_product_table(s)
        print(f"n={n} hidden s={s} -> recovered {bernstein_vazirani(tbl)} (xor oracle: {bernstein_vazirani(tbl, 'xor')})")
