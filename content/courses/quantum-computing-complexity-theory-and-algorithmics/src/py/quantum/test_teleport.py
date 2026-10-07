import itertools

import numpy as np

from teleport import random_qubit_state, superdense_coding, teleport


def test_teleportation_fidelity_one_for_all_measurement_outcomes():
    rng = np.random.default_rng(0)
    seen = set()
    for _ in range(40):
        psi = random_qubit_state(rng)
        F, bits = teleport(psi, rng)
        assert np.isclose(F, 1.0, atol=1e-12)
        seen.add(bits)
    assert seen == {(0, 0), (0, 1), (1, 0), (1, 1)}   # every correction branch exercised


def test_superdense_coding_all_bit_pairs():
    rng = np.random.default_rng(1)
    for b in itertools.product((0, 1), repeat=2):
        for _ in range(3):
            assert superdense_coding(*b, rng) == b
