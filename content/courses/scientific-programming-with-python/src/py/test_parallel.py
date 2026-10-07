"""Tests for parallel.py (note 08): Monte Carlo pi on threads/processes, shared memory, Amdahl."""
import math

import numpy as np
import pytest

import parallel as par

N = 40_000


def test_chunks_cover_total_with_distinct_seeds():
    c = par.chunks(10, 3, seed=1)
    assert [s for s, _ in c] == [4, 3, 3]
    assert len({seed for _, seed in c}) == 3
    assert par.chunks(10, 3, seed=1) == c          # deterministic


def test_serial_estimate_is_reasonable():
    assert abs(par.pi_serial(N) - math.pi) < 0.05
    assert abs(par.pi_serial(N, worker=par.pi_hits_numpy) - math.pi) < 0.05


@pytest.mark.parametrize("driver", [par.pi_threads, par.pi_pool, par.pi_futures])
def test_parallel_drivers_agree_with_serial_on_same_seeds(driver):
    """Same chunking and seeds -> bit-identical hit counts regardless of
    the execution model."""
    expected = 4 * sum(par.pi_hits_python(c) for c in par.chunks(N, 2, 0)) / N
    assert driver(N, 2, seed=0) == expected


def test_shared_memory_in_place_update():
    x = np.arange(10_000, dtype=float)
    np.testing.assert_array_equal(par.square_in_shared_memory(x, 2), x**2)


def test_amdahl_and_gustafson():
    assert par.amdahl_speedup(1.0, 8) == 8
    assert par.amdahl_speedup(0.5, 10**9) == pytest.approx(2.0)
    assert par.amdahl_speedup(0.9, 4) == pytest.approx(1 / (0.1 + 0.9 / 4))
    assert par.gustafson_speedup(0.9, 4) == pytest.approx(3.7)
    assert par.amdahl_speedup(0.9, 4) < par.gustafson_speedup(0.9, 4)
