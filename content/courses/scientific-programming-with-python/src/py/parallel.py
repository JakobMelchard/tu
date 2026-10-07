"""Parallel processing in Python (note 08).

Monte Carlo estimate of pi run serially, with threads (GIL-bound: no
speedup for pure Python), with a process Pool (speedup ~ cores) and with
concurrent.futures.  Also: shared memory between processes, Amdahl's law,
and the case where numpy already vectorises so no Python parallelism is
needed.  Workers are top-level functions so they can be pickled for the
'spawn' start method that macOS uses.
"""
from __future__ import annotations

import multiprocessing as mp
import os
import random
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import shared_memory

import numpy as np


# ---------------------------------------------------------------- workers
def pi_hits_python(args: tuple[int, int]) -> int:
    """Pure-Python inner loop: (n, seed) -> number of points inside the
    quarter disc.  Each task gets its own seed so streams are independent."""
    n, seed = args
    rnd = random.Random(seed)
    hits = 0
    for _ in range(n):
        x, y = rnd.random(), rnd.random()
        hits += x * x + y * y <= 1.0
    return hits


def pi_hits_numpy(args: tuple[int, int]) -> int:
    """Vectorised inner loop: ~50x faster than the Python loop on one core,
    and numpy releases the GIL inside its C loops."""
    n, seed = args
    rng = np.random.default_rng(seed)
    x, y = rng.random(n), rng.random(n)
    return int(np.count_nonzero(x * x + y * y <= 1.0))


def chunks(n_total: int, n_chunks: int, seed: int) -> list[tuple[int, int]]:
    """Split work into equal chunks with child seeds from one SeedSequence."""
    seeds = np.random.SeedSequence(seed).spawn(n_chunks)
    sizes = [n_total // n_chunks + (i < n_total % n_chunks) for i in range(n_chunks)]
    return [(s, int(ss.generate_state(1)[0])) for s, ss in zip(sizes, seeds)]


# ---------------------------------------------------------------- drivers
def pi_serial(n: int, seed: int = 0, worker=pi_hits_python) -> float:
    return 4 * worker((n, seed)) / n


def pi_threads(n: int, workers: int, seed: int = 0, worker=pi_hits_python) -> float:
    """Threads share one interpreter; the GIL lets only one run Python
    bytecode at a time, so CPU-bound Python code gets NO speedup.  Threads
    do help for I/O waits and for C code that releases the GIL (numpy)."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        hits = sum(ex.map(worker, chunks(n, workers, seed)))
    return 4 * hits / n


def pi_pool(n: int, workers: int, seed: int = 0, worker=pi_hits_python) -> float:
    """multiprocessing.Pool: separate interpreters, arguments and results
    are pickled through pipes.  map() blocks and preserves order."""
    with mp.Pool(workers) as pool:
        hits = sum(pool.map(worker, chunks(n, workers, seed)))
    return 4 * hits / n


def pi_futures(n: int, workers: int, seed: int = 0, worker=pi_hits_python) -> float:
    """Same thing with the higher-level concurrent.futures API (submit ->
    Future, or map); swap ProcessPoolExecutor for ThreadPoolExecutor to
    switch the model without touching the rest."""
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(worker, c) for c in chunks(n, workers, seed)]
        hits = sum(f.result() for f in futures)
    return 4 * hits / n


# ---------------------------------------------------------------- shared memory
def _square_slice(args):
    """Worker attaches to the shared block by name: no pickling of the data."""
    name, shape, lo, hi = args
    shm = shared_memory.SharedMemory(name=name)
    arr = np.ndarray(shape, dtype=np.float64, buffer=shm.buf)
    arr[lo:hi] **= 2
    shm.close()
    return hi - lo


def square_in_shared_memory(x: np.ndarray, workers: int) -> np.ndarray:
    """Zero-copy parallel in-place update of a big array.  Compare: passing
    slices to Pool.map would pickle every slice there AND back."""
    shm = shared_memory.SharedMemory(create=True, size=x.nbytes)
    try:
        arr = np.ndarray(x.shape, dtype=x.dtype, buffer=shm.buf)
        arr[:] = x
        edges = np.linspace(0, x.size, workers + 1).astype(int)
        tasks = [(shm.name, x.shape, int(lo), int(hi)) for lo, hi in zip(edges[:-1], edges[1:])]
        with mp.Pool(workers) as pool:
            pool.map(_square_slice, tasks)
        return arr.copy()
    finally:
        shm.close()
        shm.unlink()


# ---------------------------------------------------------------- theory
def amdahl_speedup(parallel_fraction: float, n_workers: int) -> float:
    """S(n) = 1 / ((1 - p) + p / n); S(inf) = 1 / (1 - p)."""
    p = parallel_fraction
    return 1.0 / ((1 - p) + p / n_workers)


def gustafson_speedup(parallel_fraction: float, n_workers: int) -> float:
    """Scaled speedup when the problem grows with n: S = (1 - p) + p n."""
    p = parallel_fraction
    return (1 - p) + p * n_workers


def timed(fn, *args) -> tuple[float, float]:
    t0 = time.perf_counter()
    r = fn(*args)
    return r, time.perf_counter() - t0


if __name__ == "__main__":
    n, workers = 20_000_000, min(8, os.cpu_count() or 2)
    print(f"cores: {os.cpu_count()}, workers: {workers}, start method: {mp.get_start_method()}")
    r_s, t_s = timed(pi_serial, n)
    print(f"serial  python  pi={r_s:.5f}  {t_s:6.2f} s")
    r_t, t_t = timed(pi_threads, n, workers)
    print(f"threads python  pi={r_t:.5f}  {t_t:6.2f} s  speedup {t_s / t_t:.2f}  (GIL)")
    r_p, t_p = timed(pi_pool, n, workers)
    print(f"pool    python  pi={r_p:.5f}  {t_p:6.2f} s  speedup {t_s / t_p:.2f}")
    r_f, t_f = timed(pi_futures, n, workers)
    print(f"futures python  pi={r_f:.5f}  {t_f:6.2f} s  speedup {t_s / t_f:.2f}")
    r_n, t_n = timed(pi_serial, n, 0, pi_hits_numpy)
    print(f"serial  numpy   pi={r_n:.5f}  {t_n:6.3f} s  ({t_s / t_n:.0f}x vs python loop)")
    r_nt, t_nt = timed(pi_threads, n, workers, 0, pi_hits_numpy)
    print(f"threads numpy   pi={r_nt:.5f}  {t_nt:6.3f} s  (numpy releases the GIL)")
    print("Amdahl, p=0.9:", [round(amdahl_speedup(0.9, k), 2) for k in (1, 2, 4, 8, 1000)])
    x = np.arange(1e6)
    print("shared memory squares ok:", np.allclose(square_in_shared_memory(x, workers), x**2))
