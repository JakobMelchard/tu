"""Reference results reproduced from the original papers, not from a textbook.

Every assertion here is a number or a statement that a named, resolvable source
prints. See ../../refs/SOURCES.md.
"""
import itertools

import numpy as np

from lattice import (MINSTD, MINSTD0, RANDU, hull_dobell, lcg_sequence, marsaglia_plane_bound,
                     period, randu_plane_count, randu_triple_residual)


def test_hull_dobell_exhaustive_m16():
    """Hull & Dobell (1962) [S29], checked for every (a, c) with m = 16.

    The theorem is an iff, so brute force over all 256 parameter pairs is a
    complete verification of it at this modulus: the predicate must agree with
    the measured period for every pair, from every seed.
    """
    m = 16
    for a, c in itertools.product(range(m), repeat=2):
        full = all(period(s, a, c, m) == m for s in range(m))
        assert hull_dobell(a, c, m) == full, (a, c)


def test_randu_triples_lie_on_15_planes():
    """Marsaglia (1968) [S27], the paper's own example.

    RANDU has a = 65539 = 2^16 + 3 and m = 2^31, so a^2 - 6a + 9 = (a - 3)^2
    = 2^32 = 0 (mod 2^31). Hence x_{k+2} - 6 x_{k+1} + 9 x_k = 0 (mod 2^31)
    identically, and since 9 x_k - 6 x_{k+1} + x_{k+2} lies in (-6 m, 10 m)
    the triples occupy at most 15 planes. Both are exact statements, so the
    test is exact.
    """
    for seed in (1, 12345, 2**20 + 7):
        assert np.all(randu_triple_residual(seed, 50_000) == 0)
    assert randu_plane_count(1, 200_000) == 15


def test_marsaglia_generic_bound_is_far_weaker_than_randu():
    """The point of [S27]: RANDU is much worse than a generic LCG has to be."""
    generic = marsaglia_plane_bound(3, 2**31)
    assert 2300 < generic < 2400          # (3! * 2^31)^(1/3) ~ 2344
    assert randu_plane_count(1, 100_000) == 15 < generic


def test_cpp_standard_required_10000th_values():
    """ISO C++ [rand.predef] [S14] fixes these three values exactly."""
    assert int(lcg_sequence(1, *MINSTD0, 10_000)[-1]) == 1043618065   # minstd_rand0
    assert int(lcg_sequence(1, *MINSTD, 10_000)[-1]) == 399268537     # minstd_rand


def test_randu_period_is_an_eighth_of_the_modulus():
    """RANDU has c = 0, so Hull-Dobell cannot apply (gcd(0, 2^31) != 1) and the
    period is the multiplicative order of a = 65539 mod 2^31, which is 2^29 --
    an eighth of the modulus [S27] [S28]. Checked by exponentiation rather than
    by iterating 5*10^8 states."""
    a, c, m = RANDU
    assert not hull_dobell(a, c, m)
    assert pow(a, 2**29, m) == 1
    assert pow(a, 2**28, m) != 1
    # and the first 2^29 states really are distinct modulo a short prefix check
    assert period(1, a, c, m, limit=10_000) is None
