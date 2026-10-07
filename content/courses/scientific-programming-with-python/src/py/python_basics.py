"""Python for scientists (note 01).

Data model, mutability, comprehensions, generators, iterators, closures,
decorators, classes and dataclasses, typing, exceptions, context managers.
Every function is small and self-contained so the tests double as examples.
"""
from __future__ import annotations

import contextlib
import functools
import math
import time
from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator


# ---------------------------------------------------------------- data model
def append_bad(x, acc=[]):           # noqa: B006 - deliberate pitfall
    """Mutable default: `acc` is created ONCE at def time and shared between
    calls, so the list grows across calls."""
    acc.append(x)
    return acc


def append_good(x, acc=None):
    """The idiom: default None, create the list inside the body."""
    if acc is None:
        acc = []
    acc.append(x)
    return acc


def rebinding_vs_mutation():
    """`a = a + [4]` rebinds the name a to a NEW list; `b += [4]` calls
    list.__iadd__ and mutates in place, so an alias sees the change."""
    a = [1, 2, 3]
    alias_a = a
    a = a + [4]                      # new object
    b = [1, 2, 3]
    alias_b = b
    b += [4]                         # in place
    return alias_a, alias_b          # [1,2,3], [1,2,3,4]


# ---------------------------------------------------------------- comprehensions
def primes_below(n: int) -> list[int]:
    """Sieve written with comprehensions; set for O(1) membership."""
    composite = {m for p in range(2, int(n**0.5) + 1) for m in range(p * p, n, p)}
    return [k for k in range(2, n) if k not in composite]


def transpose(rows: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*rows)]


# ---------------------------------------------------------------- iterators & generators
class Countdown:
    """The iterator protocol by hand: __iter__ returns an object with __next__
    that raises StopIteration when exhausted.  A for loop does exactly this."""

    def __init__(self, start: int):
        self.n = start

    def __iter__(self) -> Iterator[int]:
        return self

    def __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1


def fibonacci() -> Iterator[int]:
    """Infinite generator: state lives in the paused frame, O(1) memory."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(n: int, it: Iterable):
    """First n items of any iterable (works on infinite generators)."""
    out = []
    for i, x in enumerate(it):
        if i >= n:
            break
        out.append(x)
    return out


def running_mean(xs: Iterable[float]) -> Iterator[float]:
    """Generator pipeline stage: consumes lazily, yields lazily."""
    total, count = 0.0, 0
    for x in xs:
        total += x
        count += 1
        yield total / count


# ---------------------------------------------------------------- closures
def make_counter() -> Callable[[], int]:
    """Closure over `count`; `nonlocal` is needed to rebind, not to read."""
    count = 0

    def counter() -> int:
        nonlocal count
        count += 1
        return count

    return counter


def late_binding_bad() -> list[int]:
    """Classic pitfall: all lambdas see the final value of i (i is looked up
    at CALL time in the enclosing scope, not captured at definition)."""
    fs = [lambda: i for i in range(3)]
    return [f() for f in fs]          # [2, 2, 2]


def late_binding_good() -> list[int]:
    """Fix: bind i as a default argument, evaluated at definition time."""
    fs = [lambda i=i: i for i in range(3)]
    return [f() for f in fs]          # [0, 1, 2]


# ---------------------------------------------------------------- decorators
def timed(fn):
    """Decorator = function taking a function and returning a wrapper.
    functools.wraps copies __name__/__doc__ so introspection still works."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = fn(*args, **kwargs)
        wrapper.last_seconds = time.perf_counter() - t0
        return result
    wrapper.last_seconds = None
    return wrapper


def memoize(fn):
    """Hand-rolled functools.lru_cache: cache keyed by the positional args.
    Only valid for pure functions with hashable arguments."""
    cache = {}

    @functools.wraps(fn)
    def wrapper(*args):
        if args not in cache:
            cache[args] = fn(*args)
        return cache[args]
    wrapper.cache = cache
    return wrapper


@memoize
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def repeat(times: int):
    """Decorator WITH arguments = a function returning a decorator."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            result = None
            for _ in range(times):
                result = fn(*a, **kw)
            return result
        return wrapper
    return deco


# ---------------------------------------------------------------- classes
class Vector:
    """Minimal numeric class: dunder methods hook into operators; __slots__
    removes the per-instance __dict__ (less memory, no new attributes)."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float):
        self.x, self.y = float(x), float(y)

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Vector) and (self.x, self.y) == (other.x, other.y)

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, k: float) -> "Vector":
        return Vector(k * self.x, k * self.y)

    __rmul__ = __mul__                 # so 2 * v works too

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    @property
    def angle(self) -> float:
        return math.atan2(self.y, self.x)

    @classmethod
    def polar(cls, r: float, phi: float) -> "Vector":
        return cls(r * math.cos(phi), r * math.sin(phi))


@dataclass(frozen=True, order=True)
class Measurement:
    """dataclass generates __init__, __repr__, __eq__ (and __lt__... with
    order=True, comparing fields in order).  frozen=True makes it hashable
    and raises on attribute assignment.  Mutable defaults need field()."""
    time: float
    value: float
    tags: tuple[str, ...] = field(default=(), compare=False)


# ---------------------------------------------------------------- exceptions
class ConvergenceError(RuntimeError):
    def __init__(self, iterations: int, residual: float):
        super().__init__(f"no convergence after {iterations} iterations, residual {residual:.3g}")
        self.iterations, self.residual = iterations, residual


def newton_sqrt(a: float, tol: float = 1e-12, max_iter: int = 50) -> float:
    """Raise a domain-specific exception instead of returning NaN/None."""
    if a < 0:
        raise ValueError("a must be non-negative")
    x = max(a, 1.0)
    for k in range(max_iter):
        x_new = 0.5 * (x + a / x)
        if abs(x_new - x) < tol * max(1.0, x_new):
            return x_new
        x = x_new
    raise ConvergenceError(max_iter, abs(x_new - x))


def parse_float_or_default(s: str, default: float) -> float:
    """EAFP (try/except) instead of LBYL (checking first): idiomatic and
    faster when failures are rare."""
    try:
        return float(s)
    except ValueError:
        return default


# ---------------------------------------------------------------- context managers
class Timer:
    """__enter__/__exit__: __exit__ always runs, even on exceptions; returning
    False (None) re-raises the exception, True would swallow it."""

    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.seconds = time.perf_counter() - self.t0
        return False


@contextlib.contextmanager
def temporarily(obj, attr: str, value):
    """Generator-based context manager: code before yield is __enter__,
    after yield is __exit__ (in a finally so it restores on errors)."""
    old = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield obj
    finally:
        setattr(obj, attr, old)


if __name__ == "__main__":
    print("mutable default:", append_bad(1), append_bad(2))
    print("rebind vs mutate:", rebinding_vs_mutation())
    print("primes:", primes_below(30))
    print("countdown:", list(Countdown(3)), " fib:", take(10, fibonacci()))
    print("running mean:", list(running_mean([1, 2, 3, 4])))
    c = make_counter(); c(); print("counter:", c())
    print("late binding:", late_binding_bad(), late_binding_good())
    print("fib(80) memoized:", fib(80))
    v = Vector.polar(2, math.pi / 2); print("vector:", v, abs(v), 2 * v)
    m = Measurement(0.5, 3.2, ("lab",)); print("dataclass:", m, m < Measurement(1.0, 0.0))
    try:
        newton_sqrt(-1)
    except ValueError as e:
        print("caught:", e)
    with Timer() as t:
        sum(range(10**6))
    print(f"timer: {t.seconds*1e3:.2f} ms")
