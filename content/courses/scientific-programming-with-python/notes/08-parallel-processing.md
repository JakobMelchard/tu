# 08 Parallel processing in Python

Code: [`../src/py/parallel.py`](../src/py/parallel.py) (run it for the speedup table), tests in `test_parallel.py`.

Sources: the CPython 3.12 `multiprocessing` / `concurrent.futures` docs [S11],
PEP 703 and PEP 734 [S26], NumPy's parallel-RNG guide [S12], and the two primary
papers behind §7 — Amdahl 1967 [S35] and Gustafson 1988 [S36].
**Verified against CPython 3.12.13 on macOS** [S40], last re-run 2026-09-27, where the default start
method is `spawn`.

**Weight this note above what a generic Python syllabus would give it.** The
lecturer is an associate professor in TU Wien's Research Unit of Parallel
Computing, and MPI, collective communication and shared-memory programming are
his research area [S10].

## 1. The GIL

CPython has a **Global Interpreter Lock**: only one thread executes Python bytecode at a time. It exists because CPython's memory management (reference counting) is not thread-safe without it, and it makes single-threaded code and C extensions simple. Consequences:

- **CPU-bound pure-Python code gets no speedup from threads** (`pi_threads` with the Python worker: speedup about 1.0 on 8 threads; the switching overhead can even make it slower).
- Threads still help for **I/O-bound** work (network, disk, `time.sleep`): a thread waiting on I/O releases the GIL.
- **C extensions can release the GIL** around long computations. NumPy does this in most ufuncs, BLAS calls and `np.random` generation, so `pi_threads` with the numpy worker *does* scale; the same holds for scipy, pandas (partly), numba `nogil=True`, and I/O libraries.
- Python 3.13+ has an experimental *free-threaded* build (`python3.13t`, PEP 703 [S26]) without a GIL; it is opt-in and most extensions are still being adapted. Per-interpreter GILs with sub-interpreters (PEP 734 [S26]) are another route. The repo venv is CPython **3.12.13**, a normal GIL build [S40]. Assume the GIL for the exam.

## 2. The models

| Model | Module | Memory | Startup/communication | Best for |
|---|---|---|---|---|
| Threads | `threading`, `concurrent.futures.ThreadPoolExecutor` | shared (same process) | cheap; data shared without copies but needs locks | I/O, GIL-releasing C code |
| Processes | `multiprocessing`, `ProcessPoolExecutor` | separate interpreters; arguments and results **pickled** through pipes | fork/spawn cost (~10-100 ms per process), copies of data | CPU-bound Python |
| Async | `asyncio` | single thread, cooperative | very cheap tasks | many concurrent I/O waits, not CPU |
| Vectorised C | numpy/BLAS threads (OpenBLAS, MKL, Accelerate) | shared | none | linear algebra: already parallel |
| Compiled | numba `prange`, Cython `prange`, OpenMP in C | shared | none | tight numeric loops |
| Distributed | `mpi4py`, dask, ray | separate nodes | network | clusters |

Start methods for processes [S11]: `fork` (Linux default until 3.14, which switches to `forkserver`: the child is a copy of the parent, fast, but unsafe with threads/BLAS pools), `spawn` (macOS and Windows default: a fresh interpreter that **imports the main module**, so workers must be importable top-level functions, the main script must be guarded by `if __name__ == "__main__":`, and closures/lambdas/functions defined in a notebook cell cannot be sent), `forkserver`. `mp.get_start_method()`, `mp.set_start_method("spawn")`. Checked in this venv: `mp.get_start_method()` is `spawn`.

## 3. `multiprocessing.Pool` and `concurrent.futures`

```python
with mp.Pool(processes=8) as pool:
    results = pool.map(worker, tasks)            # blocks, keeps order, chunks automatically
    pool.imap_unordered(worker, tasks, chunksize=10)   # lazy, first-finished-first
    pool.starmap(f, [(a, b), ...]); pool.apply_async(f, args).get()
```

`concurrent.futures` is the modern uniform API: `ex.submit(f, *args)` returns a `Future` (`.result()`, `.done()`, `.exception()`, `add_done_callback`), `ex.map(f, it)` yields results in order, `as_completed(futures)` in completion order, `wait`. Switching `ProcessPoolExecutor` for `ThreadPoolExecutor` changes only one line (`pi_futures`, `pi_threads`). Exceptions in workers are re-raised in the parent when `.result()` is called. `max_workers` defaults to `os.cpu_count()` (processes) or `min(32, cpu_count + 4)` (threads) [S11].

Pickling cost is the hidden tax: every argument and result crosses a pipe. Pass small descriptions of work (seeds, index ranges, file names), not big arrays; let the worker generate or load its own data. `pi_pool` passes `(n, seed)` and returns an integer.

## 4. Chunking and load balancing

Task overhead is per call (pickling, pipe, scheduling), so batch small tasks into chunks: one chunk per worker for uniform work (`chunks(n_total, n_workers, seed)`), several chunks per worker (`chunksize` in `map`, or `4 * n_workers` chunks) when task durations vary, so a slow chunk does not leave others idle. Too many tiny chunks: overhead dominates; too few: load imbalance and the last worker determines the wall time. Each chunk gets its own seed from one `SeedSequence.spawn` — NumPy's documented way to get independent streams in parallel workers [S12] — giving statistically independent streams and deterministic results regardless of scheduling (the test checks that threads, Pool and futures give bit-identical hit counts).

## 5. Shared memory

Processes do not share memory by default. Options when the data is large:

- `multiprocessing.shared_memory.SharedMemory(create=True, size=...)` [S11]: a named block; workers attach by *name* and wrap it in `np.ndarray(shape, dtype, buffer=shm.buf)`; zero copies, in-place updates visible to all (`square_in_shared_memory`). The creator must `close()` **and** `unlink()`; workers only `close()`.
- `mp.Array` / `mp.Value` (ctypes-backed, with an optional lock), `mp.Manager` (proxy objects, slow).
- `np.memmap` of a file, read by every process (OS page cache shares it).
- On Linux, `fork` inherits read-only copies of parent arrays for free (copy-on-write) until written.
- Threads share everything; guard mutable shared state with `threading.Lock` (numpy in-place ops on disjoint slices are safe, `x += 1` on the same array from two threads is a race).

## 6. When numpy already parallelises

Matrix products, `solve`, `eigh`, `svd`, FFTs (`scipy.fft(workers=)`) use multithreaded BLAS/LAPACK: adding a process pool on top *oversubscribes* the cores (8 processes x 8 BLAS threads = 64 threads) and slows down. Control with `OMP_NUM_THREADS=1` / `OPENBLAS_NUM_THREADS` / `MKL_NUM_THREADS` in workers or `threadpoolctl.threadpool_limits(1)`. On this Mac none of that is demonstrable: NumPy 2.5.3 and SciPy 1.18.1 report Apple Accelerate as BLAS and LAPACK (`np.show_config()`), and `threadpoolctl.threadpool_info()` (3.7.0, installed as a scikit-learn dependency) finds no pool to limit (checked 2026-09-27 [S40]). Elementwise ufuncs (`np.sin`, `a * b`) are single-threaded (memory-bound anyway); numexpr and numba can multithread those. Rule: first vectorise (`pi_hits_numpy` alone is 6-50x faster than the Python loop; more than an 8-process pool gives), then parallelise the *outer* loop of independent tasks (parameter sweeps, seeds, files: "embarrassingly parallel"), and use MPI for tightly coupled work.

## 7. Amdahl and Gustafson

If a fraction $p$ of the (serial) runtime can be parallelised perfectly on $n$ workers, **Amdahl's law** [S35] gives

$$S(n) = \frac{1}{(1 - p) + p / n}, \qquad S(\infty) = \frac{1}{1 - p}.$$

With $p = 0.9$: $S(4) = 3.08$, $S(8) = 4.71$, $S(\infty) = 10$ (`amdahl_speedup`). The serial part (setup, pickling, reduction, I/O) bounds the speedup regardless of cores. **Gustafson** [S36] looks at a problem that grows with $n$ at fixed wall time: scaled speedup $S = (1 - p) + p n$, linear in $n$; this is the *weak scaling* view, Amdahl the *strong scaling* view. The two are not in conflict — they hold the problem size and the wall time fixed respectively. Parallel **efficiency** $E = S/n$. Measure: time serial, time parallel, report speedup and efficiency versus $n$ (the `__main__` demo: pool speedup 4-5 on 8 workers for 20 M samples, because process startup and result collection are serial).

Other overheads: process start (spawn imports numpy in every child: ~0.1 s each), pickling, memory bandwidth (several processes streaming arrays saturate RAM bandwidth before they saturate cores), hyperthreading (logical cores are not real cores for FPU-bound work), turbo frequencies dropping under all-core load.

## Pitfalls

- Missing `if __name__ == "__main__":` with `spawn`: infinite recursive process creation / `RuntimeError`.
- Workers defined as lambdas, nested functions or in notebook cells: `PicklingError`.
- Passing big arrays to `Pool.map` (pickled twice); returning big arrays (pickled back).
- Same seed in every worker: identical "random" samples, variance estimates wrong by a factor of the worker count. Use `SeedSequence.spawn`.
- Using threads for CPU-bound Python and reporting "Python cannot parallelise".
- BLAS oversubscription; `fork` after importing a threaded BLAS or after starting threads (deadlocks).
- Measuring speedup on tiny problems where startup dominates; forgetting to `close()`/`join()` pools (use `with`); zombie processes on exceptions.
- Shared memory leaks: forgetting `unlink()` leaves `/dev/shm` segments (Linux) behind.

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md). Given
the lecturer's field [S10], this is the note to over-prepare.

1. A pure-Python Monte Carlo loop is run in 4 threads with `ThreadPoolExecutor`. The expected speedup is about
   (a) 4 (b) 2 (c) 1 (d) it depends on the number of cores
   **c.** The GIL serialises bytecode execution; use processes.

2. Why must the worker function of a `multiprocessing.Pool` be a top-level function in an importable module on macOS?
   (a) Pool cannot call methods. (b) The `spawn` start method pickles a reference to the function and the child re-imports the module to find it. (c) Closures are slower. (d) It is only a style rule.
   **b.**

3. A program spends 20 % of its time in a serial setup. The maximum speedup on unlimited cores is
   (a) 5 (b) 20 (c) 80 (d) unbounded
   **a.** Amdahl: $1 / (1 - 0.8) = 5$.

4. `multiprocessing.shared_memory` is useful because
   (a) it makes Python threads run in parallel (b) worker processes can read and write one array without pickling copies of it (c) it replaces the GIL (d) it compresses arrays
   **b.**

5. Running an 8-process pool where each worker computes large `np.linalg.solve` calls is slower than expected because
   (a) numpy cannot run in subprocesses (b) each process starts its own multithreaded BLAS and the cores are oversubscribed (c) `solve` holds the GIL (d) pickling of the solution is impossible
   **b.** Limit BLAS threads per worker (`OMP_NUM_THREADS=1`) or use fewer processes.
