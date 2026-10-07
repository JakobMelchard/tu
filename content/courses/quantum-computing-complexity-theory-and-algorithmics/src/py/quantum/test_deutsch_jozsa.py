import itertools

import numpy as np

from deutsch_jozsa import (apply_phase_oracle, apply_xor_oracle, constant_function,
                           deutsch, deutsch_jozsa, is_balanced,
                           random_balanced_function, truth_table, xor_oracle_permutation)
from sim import Register, ket


def test_all_one_bit_functions():
    for a, b in itertools.product((0, 1), repeat=2):
        expect = "constant" if a == b else "balanced"
        assert deutsch(np.array([a, b])) == expect
        assert deutsch(np.array([a, b]), oracle="xor") == expect


def test_random_functions_n3_n4_single_query():
    rng = np.random.default_rng(0)
    for n in (3, 4):
        for _ in range(10):
            tbl = random_balanced_function(n, rng)
            assert is_balanced(tbl)
            assert deutsch_jozsa(tbl) == "balanced"
            assert deutsch_jozsa(tbl, oracle="xor") == "balanced"
        for v in (0, 1):
            assert deutsch_jozsa(constant_function(n, v)) == "constant"
            assert deutsch_jozsa(constant_function(n, v), oracle="xor") == "constant"


def test_oracles_act_as_defined():
    tbl = truth_table(lambda x: (x >> 1) & 1, 2)     # f(x) = MSB of x
    assert tbl.tolist() == [0, 0, 1, 1]
    perm = xor_oracle_permutation(tbl)
    for x in range(4):
        for y in (0, 1):
            assert perm[2 * x + y] == 2 * x + (y ^ tbl[x])
    r = apply_xor_oracle(Register(3, ket("100")), tbl, [0, 1], 2)
    assert np.allclose(r.state, ket("101"))
    r = apply_phase_oracle(Register(2, np.ones(4) / 2), tbl, [0, 1])
    assert np.allclose(r.state, [0.5, 0.5, -0.5, -0.5])
