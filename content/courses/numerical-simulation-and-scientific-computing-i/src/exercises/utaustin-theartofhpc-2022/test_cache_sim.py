"""Tests for the cache simulator, one per exercise plus the machinery.

Every assertion is either a hand-countable trace or a closed form derived in
cache_sim.py, so the simulator is checked against arithmetic, not against
itself. See README.md for provenance.
"""

import math
import random

import pytest

from cache_sim import (
    WORD,
    Cache,
    associativity_sweep,
    e1_index_bits,
    e3_locality,
    expected_occupancy_direct_mapped,
    linear_sum_trace,
    occupancy_trial,
    three_row_trace,
    tree_sum_trace,
)


# ------------------------------------------------------------- the simulator
def test_a_line_is_fetched_once_and_then_hits():
    """32-byte line, 8-byte words: one miss then three hits."""
    c = Cache(n_sets=8, assoc=1, line_bytes=32).run([0, 8, 16, 24])
    assert (c.misses, c.hits) == (1, 3)


def test_lru_evicts_the_least_recently_used_way():
    c = Cache(n_sets=1, assoc=2, line_bytes=1)
    c.run([10, 20, 10, 30])  # 30 evicts 20, not 10, because 10 was re-touched
    assert c.resident_lines() == {10, 30}
    assert c.evictions == 1


def test_a_fully_associative_cache_never_evicts_below_capacity():
    c = Cache(n_sets=1, assoc=16, line_bytes=1).run(range(16))
    assert c.evictions == 0 and len(c.resident_lines()) == 16


def test_non_power_of_two_geometry_is_rejected():
    with pytest.raises(ValueError):
        Cache(n_sets=3, assoc=1)


# --------------------------------------------------------------------- E1
def test_e1_low_bits_make_every_access_a_conflict_miss():
    """3 arrays x 512 iterations, rows 64 KB apart: no access ever hits."""
    r = e1_index_bits()["low"]
    assert r["conflict_misses"] == len(three_row_trace()) == 1536
    assert r["conflict_hits"] == 0


def test_e1_high_bits_remove_the_conflicts():
    """One miss per 32-byte line per row: 3 * 512/4 = 384, the minimum."""
    r = e1_index_bits()["high"]
    assert r["conflict_misses"] == 3 * (512 // 4) == 384
    assert r["conflict_hits"] == 1536 - 384


def test_e1_high_bits_are_a_bad_rule_in_general():
    """The other half of the exercise: a contiguous array smaller than the
    cache has identical high bits, so it collapses onto a single set."""
    res = e1_index_bits()
    assert res["high"]["stream_resident_lines"] == 1
    assert res["low"]["stream_resident_lines"] == 2048


# --------------------------------------------------------------------- E2
def test_e2_direct_mapped_occupancy_matches_the_closed_form():
    """n(1 - (1-1/n)^n) = 20.41 for n = 32; 100 trials land within 0.5."""
    sweep = associativity_sweep()
    assert sweep[1]["mean"] == pytest.approx(
        expected_occupancy_direct_mapped(32), abs=0.5)
    assert expected_occupancy_direct_mapped(32) / 32 == pytest.approx(
        1 - 1 / math.e, abs=0.01)


def test_e2_fully_associative_is_the_limit():
    sweep = associativity_sweep()
    assert sweep[32] == {"median": 32, "mean": 32.0, "stdev": 0.0,
                         "min": 32, "max": 32}


def test_e2_occupancy_increases_with_associativity():
    means = [s["mean"] for s in associativity_sweep().values()]
    assert means == sorted(means)
    assert means[0] < means[-1]


def test_e2_a_single_trial_is_bounded_by_the_cache_size():
    rng = random.Random(1)
    for k in (1, 2, 4, 8, 16, 32):
        assert 1 <= occupancy_trial(32, k, rng) <= 32


# --------------------------------------------------------------------- E3
def test_e3_the_linear_sum_attains_the_minimum_miss_count():
    """One compulsory miss per line, four doubles per line: 0.25 per element."""
    r = e3_locality()["linear"]
    assert r["misses"] == 1024 // 4
    assert r["misses_per_element"] == pytest.approx(0.25)


def test_e3_the_tree_sum_has_worse_spatial_locality():
    lin, tree = e3_locality()["linear"], e3_locality()["tree"]
    assert tree["misses_per_element"] > 3 * lin["misses_per_element"]


def test_e3_both_traces_touch_the_same_elements():
    n = 64
    assert set(linear_sum_trace(n)) == {WORD * i for i in range(n)}
    assert set(tree_sum_trace(n)) <= {WORD * i for i in range(n)}
    assert len(tree_sum_trace(n)) == 3 * (n - 1)  # 3 accesses per pairwise add
