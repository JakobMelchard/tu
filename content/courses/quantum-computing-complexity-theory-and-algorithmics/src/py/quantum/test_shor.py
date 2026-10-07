import time

import numpy as np

from order_finding import order_classical
from shor import shor, shor_classical_order, shor_trial


def test_fixed_base_reduction():
    order = lambda a, N: order_classical(a, N)
    assert shor_trial(15, 7, order) == (3, 5)
    assert shor_trial(15, 2, order) == (3, 5)
    assert shor_trial(15, 14, order) is None          # r=2, a^{r/2} = -1 mod 15
    assert shor_trial(15, 5, order) == (3, 5)              # gcd shortcut
    assert shor_trial(21, 2, order) == (3, 7)


def test_factors_15_in_at_least_80_percent_of_seeded_runs():
    rng = np.random.default_rng(0)
    t0 = time.time()
    ok = sum(shor(15, rng, max_trials=3) == (3, 5) for _ in range(20))
    assert ok >= 16
    assert time.time() - t0 < 15


def test_quantum_path_only_with_coprime_base():
    rng = np.random.default_rng(1)
    from order_finding import order_finding
    hits = sum(shor_trial(15, 7, lambda a, N: order_finding(a, N, rng)[0]) == (3, 5) for _ in range(10))
    assert hits >= 3


def test_factors_21_at_least_once():
    rng = np.random.default_rng(2)
    t0 = time.time()
    results = [shor(21, rng, max_trials=3, check_multiples=True) for _ in range(3)]
    assert (3, 7) in results
    assert time.time() - t0 < 10


def test_classical_order_variant_on_larger_numbers():
    rng = np.random.default_rng(3)
    assert shor_classical_order(91, rng) == (7, 13)
    assert shor_classical_order(221, rng) == (13, 17)
    assert shor_classical_order(1001, rng) in {(7, 143), (11, 91), (13, 77)}
