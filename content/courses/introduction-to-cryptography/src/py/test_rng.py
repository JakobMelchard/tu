"""Tests for rng.py: seeding makes every draw reproducible and equal to
Python's `random.Random` with the same seed (the library cross-check);
unseeding returns to `secrets`.  The conftest seeds before every test."""
import random

import rng


def test_seeded_draws_match_random_random():
    rng.seed(42)
    got = (rng.randbelow(1000), rng.randbits(64), rng.token_bytes(8))
    ref = random.Random(42)
    assert got == (ref.randrange(1000), ref.getrandbits(64), ref.randbytes(8))


def test_reseeding_repeats_the_stream():
    rng.seed(7)
    a = rng.token_bytes(32)
    rng.seed(7)
    assert rng.token_bytes(32) == a and rng.is_seeded()


def test_unseeded_uses_the_os_csprng():
    rng.seed(None)
    assert not rng.is_seeded()
    assert rng.token_bytes(32) != rng.token_bytes(32)
    assert all(0 <= rng.randbelow(5) < 5 for _ in range(100))


def test_conftest_seeds_every_test():
    assert rng.is_seeded()
