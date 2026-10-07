"""Performance (note 10).

timeit for micro-benchmarks, cProfile/pstats for where-the-time-goes,
tracemalloc for memory, a section timer for line-level thinking, and the
usual ladder: better algorithm > vectorise > numba/cython/C.
"""
from __future__ import annotations

import cProfile
import io
import pstats
import sys
import time
import timeit
import tracemalloc
from contextlib import contextmanager

import numpy as np


# ---------------------------------------------------------------- micro-benchmarks
def bench(stmt, number: int | None = None, repeat: int = 5, **ns) -> float:
    """Best-of-repeat seconds per call.  timeit disables GC, uses
    perf_counter and repeats; take the MIN (noise only adds time).
    autorange picks `number` so that one repeat takes >= 0.2 s."""
    t = timeit.Timer(stmt, globals=ns)
    if number is None:
        number, _ = t.autorange()
    return min(t.repeat(repeat=repeat, number=number)) / number


def sum_of_squares_variants(n: int) -> dict[str, float]:
    x = np.arange(n, dtype=float)
    xl = x.tolist()
    return {
        "python loop": bench("s = 0.0\nfor v in xl: s += v*v", xl=xl),
        "python sum(gen)": bench("sum(v*v for v in xl)", xl=xl),
        "numpy (x*x).sum()": bench("(x*x).sum()", x=x),
        "numpy dot": bench("x @ x", x=x),
    }


# ---------------------------------------------------------------- profiling
def profile(fn, *args, top: int = 10, sort: str = "cumulative") -> tuple[object, str]:
    """Deterministic profiler: hooks every Python call, so it inflates the
    cost of many tiny calls and sees numpy internals only as one C call.
    tottime = own time, cumtime = including callees."""
    pr = cProfile.Profile()
    pr.enable()
    result = fn(*args)
    pr.disable()
    buf = io.StringIO()
    pstats.Stats(pr, stream=buf).sort_stats(sort).print_stats(top)
    return result, buf.getvalue()


@contextmanager
def section(name: str, store: dict):
    """Manual line-level profiling: wrap suspect blocks and compare.
    (line_profiler / %lprun does this automatically per line.)"""
    t0 = time.perf_counter()
    try:
        yield
    finally:
        store[name] = store.get(name, 0.0) + time.perf_counter() - t0


# ---------------------------------------------------------------- an example to profile
def has_duplicates_quadratic(xs: list[int]) -> bool:
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] == xs[j]:
                return True
    return False


def has_duplicates_hash(xs: list[int]) -> bool:
    """O(n) with a set: the profile shows the O(n^2) loop dominating, and
    the fix is the algorithm, not a faster loop."""
    return len(set(xs)) != len(xs)


def simulate(n_steps: int, n_particles: int, rng: np.random.Generator) -> dict:
    """A toy pipeline with distinct phases for `section` timing."""
    t = {}
    with section("init", t):
        pos = rng.random((n_particles, 3))
        vel = rng.standard_normal((n_particles, 3))
    with section("integrate", t):
        for _ in range(n_steps):
            pos += 1e-3 * vel
    with section("analyse", t):
        d = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=-1)
        mean_d = d[np.triu_indices(n_particles, 1)].mean()
    return {"times": t, "mean_distance": float(mean_d)}


# ---------------------------------------------------------------- memory
def memory_of(fn, *args) -> tuple[object, int]:
    """Peak bytes allocated by Python (numpy buffers included) during fn."""
    tracemalloc.start()
    try:
        result = fn(*args)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, peak


def temporaries_demo(n: int) -> dict[str, int]:
    """`x = 2*x + 1` allocates a new n-sized array (numpy >= 1.13 elides the
    second temporary: `2*x` is reused in place for `+ 1` because its
    refcount is 1, so ONE buffer, not two); `x *= 2; x += 1` allocates
    nothing.  Inside a time loop the difference is a full array per step."""
    x = np.ones(n)

    def new_array():
        return 2 * x + 1

    def in_place():                      # (x += 1 here would make x local!)
        np.multiply(x, 2, out=x)
        np.add(x, 1, out=x)
        return x
    return {"new_array": memory_of(new_array)[1], "in_place": memory_of(in_place)[1],
            "array_bytes": x.nbytes}


def sizes() -> dict[str, int]:
    """sys.getsizeof counts only the object header + pointers, not what the
    pointers refer to: a list of 1000 floats is 8 kB of pointers PLUS 1000
    separate 24-byte float objects; the numpy array is 8 kB total."""
    lst = [float(i) for i in range(1000)]
    return {"list_shell": sys.getsizeof(lst), "list_total": sys.getsizeof(lst) + sum(map(sys.getsizeof, lst)),
            "ndarray": np.arange(1000.0).nbytes, "float_obj": sys.getsizeof(1.0)}


NUMBA_CYTHON_IDEA = """
numba: `@numba.njit` compiles a numeric Python function (loops over numpy
arrays, scalars) to machine code with LLVM at first call; `parallel=True`
+ `prange` for multi-core.  No Python objects inside, or it falls back to
slow object mode.  Cython: annotate types in a .pyx (`cdef double x`), compile
to a C extension; more work, but handles arbitrary Python and C libraries.
Both remove the interpreter overhead in loops; neither speeds up code that
is already spending its time inside BLAS.
"""


if __name__ == "__main__":
    for k, v in sum_of_squares_variants(100_000).items():
        print(f"{k:22s} {v*1e6:9.1f} us")
    xs = list(range(3000))
    _, report = profile(has_duplicates_quadratic, xs, top=5)
    print(report.splitlines()[0], "...", [l for l in report.splitlines() if "has_duplicates" in l])
    print("hash version:", bench("has_duplicates_hash(xs)", xs=xs, has_duplicates_hash=has_duplicates_hash) * 1e6, "us")
    print("sections:", simulate(200, 300, np.random.default_rng(0))["times"])
    print("memory:", temporaries_demo(1_000_000))
    print("sizes:", sizes())
