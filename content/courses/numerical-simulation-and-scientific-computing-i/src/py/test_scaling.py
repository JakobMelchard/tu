"""Speedup laws, checked against the numbers the original papers report."""
import numpy as np

from scaling import (amdahl, amdahl_f_from_gustafson_s, efficiency, gustafson,
                     gustafson_s_from_amdahl_f, karp_flatt, strong_scaling_table)


def test_amdahl_limits():
    assert abs(amdahl(0.05, 1) - 1.0) < 1e-12
    assert abs(amdahl(0.05, 16) - 1 / (0.05 + 0.95 / 16)) < 1e-12
    assert abs(amdahl(0.05, 10**9) - 20.0) < 1e-4          # limit 1/f
    assert abs(amdahl(0.10, 16) - 6.4) < 0.01              # note 07, question 3
    assert abs(amdahl(0.05, 12) - 7.7) < 0.05              # note 07, "7.7x on 12 cores"


def test_gustafson_reproduces_the_1024_processor_result():
    """Gustafson (1988) [S20] reports speedups just above 1000 on a
    1024-processor nCUBE for applications whose serial fraction, measured on the
    parallel run, was 0.4-0.8 %. The scaled-speedup formula must land there."""
    assert abs(gustafson(0.004, 1024) - 1019.9) < 0.1
    assert abs(gustafson(0.008, 1024) - 1015.8) < 0.1
    # Amdahl with the SAME (misread) fraction would predict far less, which is
    # the contrast the paper is built on.
    assert amdahl(0.004, 1024) < 210


def test_the_two_laws_are_one_law(  ):
    """Shi (1996) [S21]: converting the serial fraction makes them identical."""
    for p in (2, 8, 64, 1024):
        for s in (0.001, 0.004, 0.05, 0.3):
            f = amdahl_f_from_gustafson_s(s, p)
            assert abs(amdahl(f, p) - gustafson(s, p)) < 1e-9 * gustafson(s, p)
            assert abs(gustafson_s_from_amdahl_f(f, p) - s) < 1e-12


def test_karp_flatt_recovers_a_synthetic_serial_fraction():
    """With a pure Amdahl machine the Karp-Flatt estimate returns f exactly."""
    p = np.array([2.0, 4, 8, 16, 64])
    for f in (0.01, 0.05, 0.2):
        assert np.allclose(karp_flatt(amdahl(f, p), p), f)


def test_karp_flatt_rises_when_overhead_grows():
    """The diagnostic use: on the measured table of note 07 (a 6+6 core M3 Pro,
    re-measured 2026-09-27) e stays near 0.02 while every thread has a P-core and
    jumps at p = 8, when two threads land on E-cores: a shared limit, not a
    serial section [S21] [S35]. A genuine serial fraction would keep e constant."""
    _, s, eff, e = strong_scaling_table([0.01460, 0.00743, 0.00384, 0.00326], [1, 2, 4, 8])
    assert abs(s[1] - 1.965) < 0.01 and abs(s[3] - 4.479) < 0.01
    assert eff[3] < 0.6
    assert abs(e[1] - e[2]) < 0.01 and e[3] > 5 * max(e[1], e[2])


def test_efficiency_definition():
    assert np.allclose(efficiency([1.0, 2.0, 3.3], [1, 2, 4]), [1.0, 1.0, 0.825])
