"""Exercises in the style of Aalto's *Python for Scientific Computing* [S41].

Serves note 11 (practice set) §3; topics: NumPy views, reductions and ``out=``
(note 02), pandas ``agg``/``transform`` (04), ``quad`` and sparse (03), seeded
parallel Monte Carlo (08).

**Not this course's material.**  Source: Aalto Scientific Computing, *Python for
Scientific Computing*, https://aaltoscicomp.github.io/python-for-scicomp/,
licence "Creative Commons Attribution 4.0" (repository ``LICENSE``) — see
``README.md`` in this directory and ``../../../refs/SOURCES.md`` [S41].  The
tasks are **restated in our own words and reimplemented**; no text or code is
copied, and the two exercises that need a downloaded dataset are replaced by
generated data because the course test suite does no network I/O.

Covers TISS items: "The SciPy and NumPy ecosystem", "Data processing and
plotting (Matplotlib)" and "Parallel processing in Python".

Workers are module-level functions so they survive the ``spawn`` start method.

Run:  ../../../../../.venv/bin/python aalto_exercises.py
"""
from __future__ import annotations

import multiprocessing as mp
import os

import numpy as np

# ------------------------------------------------------------------- NumPy
# Task 1 (after Aalto "NumPy, Exercises 3"): a slice is a view, so writing
# through it changes the original.


def views_and_copies() -> dict[str, bool]:
    """Which of the four ways to take the first two rows aliases the original."""
    a = np.arange(12).reshape(3, 4)
    return {
        "basic slice": np.shares_memory(a, a[:2]),
        "fancy index": np.shares_memory(a, a[[0, 1]]),
        "boolean mask": np.shares_memory(a, a[np.array([True, True, False])]),
        "explicit copy": np.shares_memory(a, a[:2].copy()),
    }


# Task 2 (after Aalto "NumPy, Exercises 2"): `*` is elementwise, `@` is the
# matrix product, and a reduction needs to be told which axis to collapse.


def elementwise_vs_matrix(a: np.ndarray, b: np.ndarray) -> dict[str, np.ndarray]:
    """`a * b` multiplies entry by entry; `a @ b` contracts a's last axis with
    b's second-to-last.  For square a, b both are defined and they differ."""
    return {"elementwise": a * b, "matrix": a @ b, "dot_is_matmul_in_2d": np.dot(a, b)}


def reduce_along_axis(a: np.ndarray) -> dict[str, tuple]:
    """`axis` names the axis that *disappears*: for a (3, 4) array, axis=0 leaves
    4 column results and axis=1 leaves 3 row results.  `keepdims=True` keeps the
    collapsed axis at length 1 so the result still broadcasts against `a`."""
    return {
        "axis=None": np.shape(a.sum()),
        "axis=0": a.sum(axis=0).shape,
        "axis=1": a.sum(axis=1).shape,
        "axis=1, keepdims": a.sum(axis=1, keepdims=True).shape,
    }


# Task 3 (after Aalto "NumPy, Exercises 4"): in-place work and `out=`.


def without_temporaries(x: np.ndarray) -> dict[str, bool]:
    """`y = x * 2` allocates; `np.multiply(x, 2, out=x)` and `x *= 2` do not.

    The check is identity of the buffer, not speed: in a tight loop over large
    arrays the allocation is the cost, and `out=` is how you remove it.
    """
    base = x.copy()
    allocated = base * 2
    in_place = base.copy()
    in_place *= 2
    out_arg = base.copy()
    np.multiply(out_arg, 2, out=out_arg)
    return {
        "product is a new array": not np.shares_memory(base, allocated),
        "*= writes in place": np.array_equal(in_place, allocated),
        "out= writes in place": np.array_equal(out_arg, allocated),
    }


# ------------------------------------------------------- pandas / data
# Task 4 (after Aalto's pandas exercises, which use the Titanic and Nobel CSVs;
# generated data is used instead so the suite stays offline).


def sample_measurements(seed: int = 2026, n: int = 240):
    """A tidy frame: one row per measurement, three columns."""
    import pandas as pd

    rng = np.random.default_rng(seed)
    station = rng.choice(["north", "south", "east"], size=n)
    offset = {"north": -2.0, "south": 4.0, "east": 1.0}
    value = np.array([offset[s] for s in station]) + rng.normal(0.0, 1.0, n)
    return pd.DataFrame({"station": station, "value": value,
                         "flag": rng.random(n) < 0.1})


def group_statistics(df) -> dict[str, object]:
    """`agg` gives one row per group; `transform` gives one row per input row.

    Choosing between them is the pandas question most likely to appear as
    multiple choice, because the two differ only in the shape of the result.
    """
    per_group = df.groupby("station")["value"].agg(["count", "mean", "std"])
    centred = df["value"] - df.groupby("station")["value"].transform("mean")
    return {
        "groups": list(per_group.index),
        "rows_in_agg": len(per_group),
        "rows_in_transform": len(centred),
        "centred_group_means_are_zero": bool(
            np.allclose(centred.groupby(df["station"]).mean().to_numpy(), 0.0)
        ),
        "std_uses_ddof_1": bool(
            np.isclose(per_group["std"].iloc[0],
                       df[df.station == per_group.index[0]]["value"].std(ddof=1))
        ),
    }


# -------------------------------------------------------------------- SciPy
# Task 5 (after Aalto "SciPy": one integration exercise and one sparse exercise).


def quad_against_the_closed_form() -> tuple[float, float, float]:
    r"""$\int_0^\infty e^{-x}\,\mathrm{d}x = 1$: value, reported error, true error.

    `quad` returns a *pair*; the second element is an error estimate, and
    ignoring it is how a wrong answer gets believed.
    """
    from scipy.integrate import quad

    value, abserr = quad(lambda x: np.exp(-x), 0.0, np.inf)
    return value, abserr, abs(value - 1.0)


def sparse_tridiagonal(n: int = 500) -> dict[str, object]:
    """The 1-D Laplacian as a sparse matrix: O(n) stored entries, not O(n^2)."""
    from scipy import sparse

    a = sparse.diags_array([-np.ones(n - 1), 2 * np.ones(n), -np.ones(n - 1)],
                           offsets=[-1, 0, 1], format="csr")
    dense_entries = n * n
    return {
        "shape": a.shape,
        "stored": int(a.nnz),
        "density": a.nnz / dense_entries,
        "matvec_matches_dense": bool(
            np.allclose(a @ np.ones(n), a.toarray() @ np.ones(n))
        ),
    }


# --------------------------------------------------------- parallel processing
# Task 6 (after Aalto "Parallel-1" and "Parallel-2"): Monte Carlo pi on a Pool,
# and where the worker count comes from.


def pi_chunk(args: tuple[int, int]) -> int:
    """Worker: (n, seed) -> points inside the quarter disc.  Each chunk gets its
    own seed, so the streams are independent and the result is reproducible."""
    n, seed = args
    rng = np.random.default_rng(seed)
    x, y = rng.random(n), rng.random(n)
    return int(np.count_nonzero(x * x + y * y <= 1.0))


def pi_parallel(n: int = 400_000, workers: int = 2, seed: int = 7) -> float:
    """Split n samples over `workers` processes and combine the hit counts."""
    seeds = np.random.SeedSequence(seed).spawn(workers)
    sizes = [n // workers + (i < n % workers) for i in range(workers)]
    tasks = [(s, int(ss.generate_state(1)[0])) for s, ss in zip(sizes, seeds)]
    with mp.Pool(workers) as pool:
        hits = sum(pool.map(pi_chunk, tasks))
    return 4.0 * hits / n


def available_cpus() -> dict[str, int | None]:
    """Where `Pool()` gets its default worker count — and why that is wrong on a
    shared machine.

    `mp.cpu_count()` reports the *hardware*, not your allocation.  On a cluster
    the scheduler gives you a subset; read it from the affinity mask or the
    batch system's variable and pass it to `Pool(...)` explicitly.
    """
    affinity = getattr(os, "sched_getaffinity", None)
    return {
        "mp.cpu_count": mp.cpu_count(),
        "os.cpu_count": os.cpu_count(),
        "sched_getaffinity": len(affinity(0)) if affinity else None,
        "SLURM_CPUS_PER_TASK": (int(os.environ["SLURM_CPUS_PER_TASK"])
                                if "SLURM_CPUS_PER_TASK" in os.environ else None),
    }


def main() -> None:
    print("1. shares memory with the original:", views_and_copies())
    a = np.arange(12).reshape(3, 4)
    sq = np.array([[1.0, 2.0], [3.0, 4.0]])
    print("2. a*a vs a@a:", elementwise_vs_matrix(sq, sq)["elementwise"].tolist(),
          elementwise_vs_matrix(sq, sq)["matrix"].tolist())
    print("   reductions:", reduce_along_axis(a))
    print("3. temporaries:", without_temporaries(np.arange(6.0)))
    print("4. groups:", group_statistics(sample_measurements()))
    value, abserr, true_err = quad_against_the_closed_form()
    print(f"5. quad: {value:.12f} (reported {abserr:.2e}, true {true_err:.2e})")
    print("   sparse:", sparse_tridiagonal())
    print(f"6. pi on 2 processes: {pi_parallel():.4f}")
    print("   cpus:", available_cpus())


if __name__ == "__main__":
    main()
