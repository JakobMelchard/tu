# 10 Performance: measuring, profiling and speeding up

Code: [`../src/py/profiling.py`](../src/py/profiling.py), tests in `test_profiling.py`.

Sources: CPython's `timeit`, `profile`/`cProfile` and `tracemalloc` docs [S11],
NumPy [S12], Numba [S31], Cython [S32]; cross-checked against the *Optimizing
code* chapter of the *Scientific Python Lectures* (CC BY 4.0) [S39].
**Verified against CPython 3.12.13 and NumPy 2.5.3** [S40], last re-run 2026-09-27.

**This topic is not in the TISS subject list** [S1]. It is here because notes 08
and 09 need it — you cannot justify parallelising or dropping to C without
measuring first. Read it; do not memorise it for the exam.

## 1. Method

Make it work, make it right, then measure before making it fast. The workflow: (1) a correct version with tests (note 05); (2) a *benchmark* that represents the real workload; (3) profile to find the hot spot (it is almost never where you guessed; typically 90 % of time in 10 % of code); (4) attack in this order: **algorithm and complexity** ($O(n^2) \to O(n \log n)$ beats any constant-factor trick: `has_duplicates_quadratic` vs `has_duplicates_hash`), **avoid work** (caching, early exit, lower precision if acceptable), **vectorise** with numpy, **reduce memory traffic** (in-place, fewer temporaries, contiguous access), **compile** the hot loop (numba, Cython, C), **parallelise** (note 08); (5) re-run tests and the benchmark after every change.

## 2. Timing with `timeit`

`time.perf_counter()` is the high-resolution wall clock (use for manual timing; `time.time()` has low resolution and jumps); `time.process_time()` counts CPU time. The `timeit` module does micro-benchmarks properly [S11]: it disables garbage collection, runs the statement `number` times in a loop to amortise timer overhead, and `repeat`s that; report the **minimum** (system noise only ever adds time) or the median, not the mean. `timeit.Timer(stmt, setup, globals=...)`, `.autorange()` picks `number` so one repeat takes at least 0.2 s (`bench`). In IPython, `%timeit` does all this (`-n`, `-r`). Beware: the first call may include JIT/import/cache warm-up; tiny statements are dominated by loop overhead (~30 ns per iteration); results depend on CPU frequency scaling, thermal state and other processes; benchmark with realistic sizes since cache effects change the picture at 1 kB vs 100 MB. `sum_of_squares_variants` shows the spread: Python loop ~1 ms, `sum(v*v for v in xl)` slower (generator overhead), `(x*x).sum()` 30 µs, `x @ x` 4 µs for $n = 10^5$.

## 3. Profiling with cProfile

`cProfile` is a **deterministic** profiler [S11]: it hooks every Python function call and return, recording the count, `tottime` (time inside the function excluding callees) and `cumtime` (including callees). Run `python -m cProfile -s cumulative script.py`, or `cProfile.Profile()` around a call and `pstats.Stats(pr).sort_stats("cumulative").print_stats(10)` (`profile`), or `%prun` in IPython. Save with `-o prof.out` and visualise with `snakeviz` or `tuna`. Reading the table: sort by `tottime` to find hot *functions*, by `cumtime` to find hot *call paths*; `ncalls` shows recursion as `a/b` (total/primitive). Limits: it inflates the cost of many tiny function calls (the hook overhead is per call), it sees a numpy operation as one C call with no detail, and it cannot see inside C. **Sampling** profilers (`py-spy top --pid`, `py-spy record -o prof.svg`, `scalene`, `austin`) interrupt the process periodically, have negligible overhead, work on running production code and can show native frames; they are the better first tool for long jobs.

## 4. Line-level thinking

A function-level profile says "`simulate` is slow", not which line. Options: `line_profiler` (`@profile` decorator, `kernprof -l -v script.py`, or `%lprun -f simulate simulate(...)`) prints time per line; or instrument manually with a section timer (`section` context manager accumulating per phase: `simulate` splits into init/integrate/analyse). Rules of thumb for what a line costs in CPython: a function call ~50-100 ns, an attribute lookup ~20 ns, a global lookup slower than a local (bind `local_sqrt = math.sqrt` in hot loops), list append ~30 ns, a numpy ufunc call ~1 µs fixed overhead plus ~1 ns per element (so numpy on 10-element arrays is *slower* than plain Python), `np.array(list)` and `arr.tolist()` are $O(n)$ conversions, a `pandas` row iteration ~10 µs. Avoid: repeated `len()` or `.shape` in loops (cheap but adds up), dictionary lookups with string formatting keys, `try/except` in the hot path when exceptions are common, `global` mutable state, `list.insert(0, x)` ($O(n)$; use `collections.deque`).

## 5. Memory

`tracemalloc.start()` / `get_traced_memory()` gives current and peak bytes allocated through Python's allocator, including numpy data buffers (`memory_of`) [S11]; `snapshot.statistics("lineno")` attributes them to lines. `sys.getsizeof` counts only the object's own header (a list of $10^3$ floats is 8 kB of pointers plus $10^3 \times 24$ B float objects; the numpy array is 8 kB total; `sizes`). Process-level: `resource.getrusage(...).ru_maxrss`, `psutil.Process().memory_info().rss`, `memory_profiler`'s `%memit` / `@profile`.

Memory is often the real bottleneck: a modern core does ~10 GFLOP/s per thread but memory delivers ~10-20 GB/s, so elementwise operations over large arrays are **memory-bound** (arithmetic intensity < 1 flop/byte), and each numpy temporary costs a full write and read of the array. `2 * x + 1` allocates a new array (numpy reuses the `2 * x` temporary for `+ 1`: *temporary elision*, introduced in numpy 1.13 and applied above a size threshold of a few hundred kB, so one allocation instead of two) [S12]; `np.multiply(x, 2, out=x); np.add(x, 1, out=x)` (or `x *= 2; x += 1`) allocates nothing (`temporaries_demo`: 8 MB vs ~0). Other levers: `float32` halves traffic when precision allows; process in chunks that fit in L2/L3 cache; use `numexpr` for long elementwise expressions (fused, multithreaded); prefer contiguous access along the last axis; `np.memmap` or HDF5/zarr for out-of-core data; delete large intermediates (`del`) in long notebooks; watch for hidden copies (`astype`, fancy indexing, `np.concatenate` in loops).

## 6. numba and Cython in concept

**numba** [S31] (**not installed in the repo venv** [S40] — nothing below is demonstrated in `src/`): `@numba.njit` compiles a function to machine code with LLVM on first call, specialised to the argument types; loops over numpy arrays, scalars, tuples, simple classes are supported; Python objects, pandas, arbitrary libraries are not (with `nopython=True`, the default of `njit`, unsupported code is a compile error rather than a silent fallback). `fastmath=True` relaxes IEEE, `parallel=True` with `numba.prange` uses threads, `cache=True` stores the compiled code, `@vectorize` makes ufuncs, `@guvectorize` generalised ufuncs, `cuda.jit` for GPUs. Typical gains: 10-1000x over Python loops, similar to C; zero gain on code already in BLAS. Costs: compile latency (~0.1-1 s per function per type signature), debugging inside compiled code is harder, the whole call graph must be numba-compatible.

**Cython** [S32] (also not installed): write `.pyx` with optional static types (`cdef double x`, `double[:, ::1] A` typed memoryviews, `cdef` functions, `cimport`), compile to a C extension (`cythonize`, a `setup.py` or `pyproject` build step). Untyped code runs as Python (slightly faster); typed loops run at C speed; `with nogil:` and `prange` for threading; `cdef extern` to call C/C++ libraries directly; `cython -a` produces an annotated HTML showing which lines still touch Python objects (yellow). Costs: a build step, a compiler, and a second language dialect. Choose numba for numeric kernels you own, Cython for wrapping C or shipping extensions, and none of them before profiling proves a Python-level loop is the bottleneck.

Other accelerators: `PyPy` (JIT for pure Python, poor numpy support), `jax` (XLA compilation and autodiff, GPU), `torch`, `cupy` (numpy on GPU), `pythran`, `mypyc`.

## 7. Checklist

1. Benchmark the real workload; time with `timeit`/`perf_counter`, report min or median and the size.
2. Profile (`cProfile` / `py-spy`), sort by `tottime` and `cumtime`; then line-profile the hottest function.
3. Fix complexity first (sets/dicts for membership, sorting once, caching pure functions with `lru_cache`, avoiding repeated work in loops).
4. Vectorise; avoid Python loops over array elements; batch small numpy calls into big ones.
5. Cut memory traffic: in-place ops, `out=`, fewer temporaries, right dtype, contiguous layouts, chunking.
6. Compile the residual hot loop (numba), or call C (note 09).
7. Parallelise the outer embarrassingly parallel loop (note 08); mind BLAS thread oversubscription.
8. Re-run the tests. Keep the slow reference implementation around as the oracle.

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md). Since
this topic is not on the TISS subject list, treat them as comprehension checks
rather than exam preparation.

1. `timeit` reports the minimum over repeats by default in `%timeit`'s "best of" style because
   (a) the minimum is the most pessimistic estimate (b) noise from other processes can only make a run slower, so the minimum is closest to the intrinsic cost (c) the mean is undefined (d) Python's timers are unreliable
   **b.**

2. In a cProfile table, a function with small `tottime` but large `cumtime`
   (a) is itself slow (b) spends its time in the functions it calls (c) was called only once (d) is a C extension
   **b.** `tottime` excludes callees, `cumtime` includes them.

3. For `n = 10` elements, `np.sin(x)` versus a Python loop with `math.sin` is
   (a) much faster (b) about the same or slower, because the ufunc has ~1 µs fixed overhead (c) impossible to compare (d) faster only with numba
   **b.** Vectorisation pays off for large arrays.

4. Which change removes all array allocations from `y = 2 * x + 1` inside a loop over time steps?
   (a) `y = (2 * x) + 1` (b) `np.multiply(x, 2, out=y); np.add(y, 1, out=y)` with `y` preallocated (c) `y = x * 2.0 + 1.0` (d) `y = np.array(2 * x + 1)`
   **b.**

5. `@numba.njit` speeds up
   (a) any Python function, including ones using pandas and requests (b) numeric loops over numpy arrays and scalars, by compiling them with LLVM (c) BLAS matrix products (d) I/O
   **b.** Unsupported Python objects are a compile error in nopython mode; BLAS calls are already compiled.
