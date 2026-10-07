"""The one source of randomness for every module in src/py.

Primitive: uniform sampling, the "x <- S" in every Gen and Enc of the notes.
Note: notes/04-computational-security.md (randomness is part of the security
definition) and notes/05-pseudorandomness.md (why a seeded generator is not
a PRG); the notation is in notes/README.md.
Standard: none implemented.  A real system draws keys from an approved DRBG
(NIST SP 800-90A, not vendored) via the operating system, which is what the
default branch below does through `secrets`.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
`seed(s)` swaps `secrets` for a Mersenne Twister `random.Random(s)` so that
the demos and the tests print and check the same numbers on every run.  A
seeded Mersenne Twister is *predictable* (624 outputs determine its state),
so a seeded run has no secrets at all: that is the point of seeding it, and
the reason nothing here may ever protect real data.
"""
from __future__ import annotations

import random
import secrets

_rng: random.Random | None = None


def seed(s: int | None) -> None:
    """Make every later draw reproducible (`s` an int), or go back to the
    operating-system CSPRNG (`s` None)."""
    global _rng
    _rng = None if s is None else random.Random(s)


def is_seeded() -> bool:
    return _rng is not None


def randbelow(n: int) -> int:
    """Uniform integer in [0, n)."""
    return secrets.randbelow(n) if _rng is None else _rng.randrange(n)


def randbits(k: int) -> int:
    """Uniform k-bit integer."""
    return secrets.randbits(k) if _rng is None else _rng.getrandbits(k)


def token_bytes(n: int) -> bytes:
    """n uniform bytes."""
    return secrets.token_bytes(n) if _rng is None else _rng.randbytes(n)


if __name__ == "__main__":
    seed(2027)
    a = token_bytes(8).hex()
    seed(2027)
    print("seeded draws repeat:", a == token_bytes(8).hex(), "|", a)
    seed(None)
    print("unseeded draws differ:", token_bytes(8) != token_bytes(8))
