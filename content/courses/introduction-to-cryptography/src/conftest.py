"""Shared pytest setup for src/py.

Puts src/py on sys.path and seeds `rng` before every test, so each test
draws the same keys, nonces and messages on every run and in any order or
selection.  The seed is fixed, not per-test, on purpose: a failure then
reproduces with `pytest path::test_name` alone.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "py"))

import rng                                                   # noqa: E402

SEED = 192125


@pytest.fixture(autouse=True)
def _seeded_rng():
    rng.seed(SEED)
    yield
    rng.seed(None)
