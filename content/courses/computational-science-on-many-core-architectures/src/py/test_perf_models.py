"""Tests for perf_models.py: each reproduces a number stated by a source."""
import math

import pytest

from perf_models import (CC_86, CC_90, accumulation_ii, alpha_beta_time, amdahl, amdahl_f_from_gustafson_s,
                         effective_bandwidth, gustafson, karp_flatt, little_bytes_in_flight, n_half, occupancy,
                         offload_speedup, pipeline_cycles, pj_per_flop)


def test_amdahl_limits():
    assert amdahl(0.05, 1) == pytest.approx(1.0)
    assert amdahl(0.05, 1e12) == pytest.approx(20.0, rel=1e-9)
    assert amdahl(0.1, 16) == pytest.approx(6.4)


def test_gustafson_reproduces_the_1988_paper():
    # [S10]: s = 0.4 .. 0.8 % on 1024 processors -> speedups just over 1000
    assert gustafson(0.004, 1024) == pytest.approx(1019.9, abs=0.05)
    assert gustafson(0.008, 1024) == pytest.approx(1015.8, abs=0.05)


@pytest.mark.parametrize("s,p", [(0.004, 1024), (0.05, 12), (0.3, 7)])
def test_the_two_laws_are_one_law(s, p):
    # [S37]: converting the serial fraction makes the two formulas agree
    assert amdahl(amdahl_f_from_gustafson_s(s, p), p) == pytest.approx(gustafson(s, p), rel=1e-12)


def test_karp_flatt_inverts_amdahl():
    for f in (0.0, 0.02, 0.2):
        for p in (2, 8, 64):
            assert karp_flatt(amdahl(f, p), p) == pytest.approx(f, abs=1e-12)


def test_offload_is_amdahl():
    assert offload_speedup(0.9, 20) == pytest.approx(amdahl(0.1, 20))
    assert offload_speedup(0.9, 20, 0.1) < offload_speedup(0.9, 20)


def test_little_and_alpha_beta():
    assert little_bytes_in_flight(100e-9, 120e9) == pytest.approx(12_000)
    a, b = 10e-6, 16e9  # Rupp [S4]: PCIe 3, ~10 us, 16 GB/s
    assert n_half(a, b) == pytest.approx(160e3)
    assert effective_bandwidth(n_half(a, b), a, b) == pytest.approx(b / 2)
    assert alpha_beta_time(0, a, b) == a


def test_occupancy_against_table_27():
    # [S15] Table 27, cc 9.0: 64 warps, 32 blocks, 64 K regs, 228 KB smem per SM
    assert occupancy(CC_90, 256, 32) == (8, 1.0, "warps")
    assert occupancy(CC_90, 256, 64)[:2] == (4, 0.5)
    assert occupancy(CC_90, 256, 64)[2] == "registers"
    assert occupancy(CC_90, 256, 32, 48 * 1024)[:2] == (4, 0.5)
    assert occupancy(CC_90, 32, 16)[2] == "blocks"  # 32 blocks x 1 warp = 50 %
    assert occupancy(CC_90, 32, 16)[1] == 0.5
    assert occupancy(CC_86, 1024, 32)[:2] == (1, 32 / 48)  # 2 x 1024 would exceed 1536 threads


def test_energy():
    assert pj_per_flop(700, 34000) == pytest.approx(20.6, abs=0.05)
    assert math.isclose(pj_per_flop(1, 1), 1000.0)


def test_pipeline_model():
    # depth + (n-1) II; throughput -> one result per II cycles
    assert pipeline_cycles(1, 10, 1) == 10
    assert pipeline_cycles(1000, 10, 1) == 1009
    assert pipeline_cycles(1000, 10, 4) == 4006
    assert pipeline_cycles(0, 10, 1) == 0
    assert accumulation_ii(4, 1) == 4 and accumulation_ii(4, 4) == 1 and accumulation_ii(5, 2) == 3
