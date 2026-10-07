"""Deutsch and Deutsch-Jozsa: one query decides constant vs balanced (N&C 1.4.3-1.4.4, KLM 6.3-6.4).

Belongs to the Part C note on the Deutsch-Jozsa / Bernstein-Vazirani algorithms (C02).

Boolean functions f: {0,1}^n -> {0,1} are passed as truth tables: an int array
`table` of length 2^n with table[x] = f(x), x read big-endian like the register.
Two oracle forms are provided:
  phase oracle  |x> -> (-1)^f(x) |x>                   (apply_phase_oracle)
  XOR oracle    |x>|y> -> |x>|y xor f(x)>  with ancilla (apply_xor_oracle, xor_oracle_permutation)
The XOR oracle turns into the phase oracle when the ancilla is prepared in |->
(phase kickback), which is exactly what deutsch_jozsa(..., oracle="xor") does.

Implements: truth_table, constant_function, random_balanced_function, is_balanced,
xor_oracle_permutation, apply_xor_oracle, apply_phase_oracle, deutsch, deutsch_jozsa.
"""
import numpy as np

from sim import Register


def truth_table(f, n):
    return np.array([int(f(x)) & 1 for x in range(2 ** n)])


def constant_function(n, value):
    return np.full(2 ** n, int(value))


def random_balanced_function(n, rng):
    """Random f with exactly half of the inputs mapped to 1."""
    table = np.zeros(2 ** n, dtype=int)
    table[rng.permutation(2 ** n)[: 2 ** (n - 1)]] = 1
    return table


def is_balanced(table):
    return int(table.sum()) * 2 == len(table)


def xor_oracle_permutation(table):
    """Permutation of the (n+1)-qubit basis realising |x>|y> -> |x>|y xor f(x)> (ancilla = last qubit)."""
    n_in = len(table)
    perm = np.empty(2 * n_in, dtype=int)
    for x in range(n_in):
        for y in (0, 1):
            perm[2 * x + y] = 2 * x + (y ^ int(table[x]))
    return perm


def apply_xor_oracle(reg, table, inputs, ancilla):
    """One query of U_f in XOR form on register qubits `inputs` (MSB first) and `ancilla`."""
    return reg.apply_permutation(xor_oracle_permutation(table), list(inputs) + [ancilla])


def apply_phase_oracle(reg, table, inputs):
    """One query of the phase oracle |x> -> (-1)^f(x)|x>."""
    return reg.apply_diagonal((-1.0) ** np.asarray(table), list(inputs))


def deutsch_jozsa(table, oracle="phase"):
    """Decide 'constant' or 'balanced' for a promised f with a single oracle query.

    H^n |0> -> uniform superposition; query; H^n; measure. The amplitude of |0...0>
    is (1/N) sum_x (-1)^f(x): +-1 if constant, 0 if balanced, so the outcome
    0...0 appears with certainty iff f is constant (no randomness involved).
    """
    n = int(np.log2(len(table)))
    if oracle == "phase":
        reg = Register(n)
        for q in range(n):
            reg.h(q)
        apply_phase_oracle(reg, table, range(n))
        for q in range(n):
            reg.h(q)
        p0 = reg.probabilities()[0]
    else:
        reg = Register(n + 1).x(n)          # ancilla |1> -> H -> |-> gives the phase kickback
        for q in range(n + 1):
            reg.h(q)
        apply_xor_oracle(reg, table, range(n), n)
        for q in range(n):
            reg.h(q)
        p0 = reg.partial_trace(list(range(n)))[0, 0].real
    return "constant" if p0 > 0.5 else "balanced"


def deutsch(table, oracle="phase"):
    """n = 1 special case: is f(0) == f(1)? (constant) or f(0) != f(1)? (balanced)."""
    assert len(table) == 2
    return deutsch_jozsa(table, oracle)


if __name__ == "__main__":
    for name, tbl in (("f=0", [0, 0]), ("f=1", [1, 1]), ("f=x", [0, 1]), ("f=not x", [1, 0])):
        print(f"Deutsch {name:8s}: {deutsch(np.array(tbl))}")
    rng = np.random.default_rng(0)
    n = 4
    tbl = random_balanced_function(n, rng)
    print(f"n={n} random balanced table {tbl.tolist()} -> phase oracle: {deutsch_jozsa(tbl)},"
          f" xor oracle: {deutsch_jozsa(tbl, 'xor')}")
    print(f"n={n} constant 1 -> {deutsch_jozsa(constant_function(n, 1))}")
