import numpy as np

from bernstein_vazirani import bernstein_vazirani, bits_to_int, inner_product_table, int_to_bits


def test_random_hidden_strings_n1_to_6():
    rng = np.random.default_rng(0)
    for n in range(1, 7):
        for _ in range(4):
            s = [int(b) for b in rng.integers(0, 2, n)]
            tbl = inner_product_table(s)
            assert bernstein_vazirani(tbl) == s
            assert bernstein_vazirani(tbl, oracle="xor") == s


def test_table_and_bit_helpers():
    assert inner_product_table([1, 0]).tolist() == [0, 0, 1, 1]
    assert inner_product_table([1, 1]).tolist() == [0, 1, 1, 0]
    assert bits_to_int(int_to_bits(37, 6)) == 37
