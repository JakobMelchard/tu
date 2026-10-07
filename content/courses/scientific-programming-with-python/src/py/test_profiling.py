"""Tests for profiling.py (note 10): timers, cProfile, duplicate-check variants, tracemalloc, sizes."""
import numpy as np

import profiling as pf


def test_bench_returns_seconds_per_call():
    t = pf.bench("sum(range(100))", number=200, repeat=2)
    assert 0 < t < 1e-3


def test_profile_reports_the_hot_function():
    xs = list(range(400))
    result, report = pf.profile(pf.has_duplicates_quadratic, xs)
    assert result is False and "has_duplicates_quadratic" in report
    assert "function calls" in report


def test_duplicates_variants_agree():
    for xs in ([1, 2, 3], [1, 2, 2], [], [5]):
        assert pf.has_duplicates_quadratic(xs) == pf.has_duplicates_hash(xs)


def test_section_timer_accumulates():
    t = {}
    with pf.section("a", t):
        pass
    with pf.section("a", t):
        pass
    assert set(t) == {"a"} and t["a"] >= 0
    r = pf.simulate(3, 10, np.random.default_rng(0))
    assert set(r["times"]) == {"init", "integrate", "analyse"} and r["mean_distance"] > 0


def test_memory_of_sees_numpy_allocations():
    _, peak = pf.memory_of(lambda: np.ones(100_000))
    assert peak >= 100_000 * 8
    d = pf.temporaries_demo(200_000)
    assert d["in_place"] < d["array_bytes"] // 10 < d["array_bytes"] <= d["new_array"] < 2 * d["array_bytes"]


def test_sizes():
    s = pf.sizes()
    assert s["list_total"] > s["ndarray"] == 8000 and s["float_obj"] == 24
