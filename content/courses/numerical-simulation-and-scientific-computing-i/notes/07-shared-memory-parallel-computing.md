# 07 Shared-memory parallel computing

Several threads in one process, one address space, one memory.

TISS calls this topic **"Shared Memory Parallel Computing"**, not "OpenMP" [S1], and that distinction matters in 2026W: the course is now co-taught by an ASC lecturer whose own public material builds a hand-written C++ task manager over `std::thread` and lists OpenMP, Intel TBB and Taskflow as the alternatives [S8]. So this note covers **both** - OpenMP first, because it is the standard and because the specification [S11] is normative and free, then the plain-C++ route.

Every OpenMP statement below is from the **OpenMP API Specification 5.2** [S11], vendored at [`../refs/vendor/openmp-api-specification-5.2.pdf`](../refs/vendor/openmp-api-specification-5.2.pdf) (the ARB explicitly permits copying). The toolchain here implements **OpenMP 5.1** via LLVM `libomp`, as CMake reports [S34]. Reference code: `src/cpp/omp_examples.cpp` and `src/cpp/threads_cpp.cpp`; measured on a 12-core M3 Pro (6 performance + 6 efficiency cores) [S34], Homebrew libomp.

## Model and vocabulary

- **Fork-join** [S11 §1.3]: the initial thread runs serially; at `#pragma omp parallel` it becomes the *primary* thread of a new *team*, every member executes the block, and the team joins at the implicit barrier at its end. Threads are reused between regions (thread pool) - the spec does not require this but every implementation does it, because creating and joining a pool costs about 8-12 us per thread (measured, `threads_cpp --bench`: 15 / 31 / 100 us for 2 / 4 / 8 threads).
- **Data-sharing attributes** [S11 §5.1]: variables declared *outside* the region default to **shared**; variables declared inside it, the iteration variables of an `omp for`, and anything in `private(...)` are **private**. `firstprivate` initialises each private copy from the original; `lastprivate` copies the sequentially-last iteration's value back. `default(none)` removes the default and forces you to classify every variable - the single most useful clause in the language.
- **Race condition**: two threads access the same location without synchronisation and at least one writes. The result depends on timing; in C++ it is undefined behaviour (the compiler may hoist the load out of the loop and "lose" all other threads' updates).
- **Cache coherence**: hardware keeps all cores' cached copies of a line consistent (MESI protocol): a write invalidates the line in every other core. Correct but slow when lines bounce.

Build on macOS: `clang++ -Xpreprocessor -fopenmp -I$(brew --prefix libomp)/include ... -L$(brew --prefix libomp)/lib -lomp`; Linux: `g++ -fopenmp`. Threads: `OMP_NUM_THREADS=4 ./a.out` or `omp_set_num_threads(4)`. Time with `omp_get_wtime()` (wall clock), never `clock()` (sums CPU time of all threads).

## Directives

```cpp
#pragma omp parallel                     // team of threads, block executed by all
#pragma omp for schedule(static)         // split the following loop among the team
#pragma omp parallel for reduction(+:s)  // both; s gets a private copy per thread, combined at the end
#pragma omp parallel for collapse(2)     // treat a 2D loop nest as one iteration space
#pragma omp critical                     // one thread at a time in this block (a lock)
#pragma omp atomic                       // single memory update done atomically (x += v, x++)
#pragma omp barrier                      // all threads wait here
#pragma omp single / master              // one thread executes, others skip (single has a barrier)
#pragma omp simd                         // vectorise this loop (no threads)
#pragma omp parallel for default(none) shared(a,b) private(tmp) firstprivate(n)
```

`reduction` [S11 §5.5.8] supports `+ * - & | ^ && || min max` and user-defined reduction identifiers (`declare reduction`). Each thread gets a private copy initialised to the operator's identity element, and the copies are combined at the end **in an unspecified order** - so a floating-point reduction is not bit-reproducible between runs or thread counts. If you need reproducibility you must reduce deterministically yourself.

**Schedules** `schedule(kind[, chunk])` [S11 §11.5.3]:

| kind | what the spec guarantees | use when |
|---|---|---|
| `static` | iterations are divided into chunks of the given size and assigned to threads **round-robin in order**; with no chunk size, into approximately equal contiguous blocks. The assignment is deterministic, so two `static` loops with the same bounds and chunk give each thread the same iterations - the only schedule for which that is guaranteed | uniform cost; also when a later loop must touch the same data as an earlier one (NUMA first touch) |
| `dynamic[,c]` | threads request a chunk of `c` (default 1) as they finish; assignment is **not** deterministic | cost varies per iteration |
| `guided[,c]` | chunk size decreases roughly exponentially to a minimum of `c` | cost varies and you want fewer queue hits than `dynamic,1` |
| `auto` | the implementation decides | rarely |
| `runtime` | taken from the `OMP_SCHEDULE` environment variable / `omp_set_schedule` | tuning without recompiling |

Rule: `static` unless the iteration cost varies; then `dynamic` with a chunk large enough that the queue is not the bottleneck. Measured on the unbalanced (triangular) loop in `omp_examples`: static 1.9 ms, `dynamic,16` 1.3 ms, `guided` 1.3 ms.

## Fixing a race, and what it costs

```
counter with none (race)  =   189599 (expected 999996)       0.3 ns/increment   <- 81% of the updates lost
counter with atomic       =  1000000                        26.2 ns/increment
counter with critical     =    20000                       339.6 ns/increment   <- 270 ns to 43 us over six runs
counter with reduction    =  1000000                         0.1 ns/increment
```
(`./bin/omp_examples`, 12 threads, 2026-09-27; the racy counter lost 81-90 % over six runs.)
`atomic` [S11 §15.8.4] applies to a **single** update of a scalar (`x++`, `x += v`, `x = x op expr`) and nothing else - it is a hardware read-modify-write, correct but serialising through the cache-coherence protocol, ~100x slower than a private increment. `critical` [S11 §15.2] is a named mutex around an arbitrary block: hundreds of ns to microseconds under contention. `reduction` gives each thread a private counter and combines 12 numbers at the end: as fast as serial code. **General rule: accumulate privately, synchronise once.**

The same four in plain C++ (`./bin/threads_cpp`, 12 threads, five runs): racy `long` 0.24-0.51 ns and 60-87 % of the updates lost; `std::atomic<long>` relaxed 20-28 ns; `std::mutex` 14-23 ns per lock; private + `std::accumulate` 0.05-0.07 ns. The ordering is identical to OpenMP's, which is the point - the directives are not magic, they are these four mechanisms.

## False sharing

Threads write to *different* variables that share one cache line. `hw.cachelinesize = 128` on this machine [S34], so **16** `long` counters fit one line and every write invalidates the other 15 cores' copies.

**Measuring it is harder than it looks, and the trap is instructive.** With a plain `long counts[nt]` the compiler is entitled to keep `counts[tid]` in a register for the whole loop - a data race is undefined behaviour, so it may assume no other thread writes - and then the line never bounces and you measure nothing. The note used to quote "12 ms vs 5.7 ms, ~2x"; that was that mistake. Forcing a real load-modify-store per iteration (`volatile`, or an atomic) gives, on this machine:

| counter type | packed (one line) | `alignas(128)` (one line each) | penalty |
|---|---|---|---|
| `volatile long` (`omp_examples`, 12 threads x 10^7) | 0.163 ns/update | 0.113 ns/update | **1.4x** (1.2-1.5x over six runs, once 0.9x) |
| `std::atomic<long>` relaxed (`threads_cpp`, 12 threads x 4x10^5) | 13.2 ns/update | 0.32 ns/update | **41x** (20-50x over five runs) |

(2026-09-27. The 2026-09-22 run of the same code had 0.20 vs 0.14 and 21.4 vs 0.24 ns, i.e. 1.4x and 89x: the atomic ratio is dominated by the denominator, which is sub-nanosecond and noisy.) So on Apple silicon a *plain* store to a falsely-shared line costs little and is hard to even see above the noise, while an *atomic* read-modify-write on one costs one to two orders of magnitude. On x86 with more cores and a 64-byte line the plain-store penalty is larger. The symptom is the same either way: a loop with no shared data that does not scale. Fix: pad to a line, or accumulate in a local variable and write once.

## Amdahl and Gustafson

$$S_{\text{Amdahl}}(p) = \frac{1}{f + (1 - f)/p} \;\xrightarrow{p \to \infty}\; \frac{1}{f}, \qquad S_{\text{Gustafson}}(p) = s + (1 - s)\,p.$$

**The two serial fractions are different quantities, and this is the trap** [S21]:

- Amdahl's $f = t_s / (t_s + t_p(1))$ is measured against the **1-processor** time and does not depend on $p$ [S19]. Fixed problem size; the serial part caps the speedup ($f = 5\%$: at most 20x, and 7.7x on 12 cores).
- Gustafson's $s = t_s / (t_s + t_p(1)/p)$ is measured against the **$p$-processor** time and therefore *does* depend on $p$ [S20]. Grow the problem with $p$ so the parallel part dominates; the speedup is nearly linear.

They are **the same law in two normalisations**. Substituting $f = s / (s + (1-s)p)$ turns one formula into the other exactly - `src/py/scaling.py` does the conversion and `test_scaling.py` asserts the two speedups agree to 9 digits. Gustafson's celebrated 1024-processor result - speedups just over 1000 for applications with $s$ between 0.4 % and 0.8 % [S20] - is reproduced by the formula: $s = 0.004 \Rightarrow 1019.9$, $s = 0.008 \Rightarrow 1015.8$. Shi's point [S21] is that the paper's claim to have *broken* Amdahl's law rests on reading $s$ as if it were $f$; with $f = 0.004$ Amdahl gives 204, but $f$ is not 0.004, it is $3.9\cdot10^{-6}$.

**Karp-Flatt.** Given a measured speedup, invert Amdahl for the experimental serial fraction
$$e(p) = \frac{1/S(p) - 1/p}{1 - 1/p}.$$
A *constant* $e$ means a genuine serial section; a *rising* $e$ means overhead or a shared resource. That is the right way to read a scaling table, and on the one below $e$ is flat at about 0.02 for 2 and 4 threads and jumps to 0.11 at 8: this machine's threads 7-12 are efficiency cores, not a serial bottleneck (`src/py/scaling.py` prints the column).

**Strong scaling**: fixed problem, increase $p$; report speedup $S = T_1 / T_p$ and efficiency $E = S/p$. **Weak scaling**: problem size $\propto p$; ideal is constant time. Measured strong scaling for the compute-bound sum in `omp_examples`:

```
threads  time[ms]  speedup  efficiency
      1     14.60     1.00     1.00
      2      7.43     1.96     0.98
      4      3.84     3.81     0.95
      8      3.26     4.47     0.56     <- threads 7-8 land on efficiency cores; the machine is not 12 equal cores
```
Fit $S(p)$ with Amdahl (or compute Karp-Flatt $e$) to estimate $f$; a memory-bound kernel (triad) saturates the shared bandwidth after 2-4 threads and its "serial fraction" is really a bandwidth limit [S35]. The `std::thread` version of the same compute-bound kernel (`threads_cpp --bench`) reaches 6.5x on 8 threads. The OpenMP loop reaches 4.5x on the 15 ms demo problem and 5.8x on the 5x larger `--bench` problem, so most of the gap is fixed per-region cost on a short run, not the threading library.

## Other things to know

- **Loop-carried dependencies** (`a[i] = a[i-1] + b[i]`) cannot be parallelised with `omp for`; recurrences need a scan algorithm.
- **Thread safety**: `rand()`, `strtok`, static local variables and most legacy C APIs are not thread safe; give each thread its own `std::mt19937` (note 06).
- **Nested parallelism** is off by default; calling a parallel BLAS from a parallel loop oversubscribes.
- **NUMA / first touch** (multi-socket Linux): memory is placed near the thread that first writes it; initialise arrays in the same parallel pattern as the compute loop.
- **Tasks** (`#pragma omp task`, `taskwait`) [S11 §12] for recursive or irregular work (tree traversal, quicksort). [S8]'s `RunParallel` is the same idea written out by hand, including nested tasks; `src/cpp/threads_cpp.cpp` implements it.
- Alternatives at the same level: `std::thread` + `std::atomic` + `std::mutex` (C++11), TBB, C++17 parallel algorithms (`std::for_each(std::execution::par, ...)`), and for Python `multiprocessing`, numba `prange` (the GIL blocks thread-level parallelism of pure Python).

## Worked example: parallel SpMV and CG

SpMV `y[i] = sum over row i` is embarrassingly parallel over rows: `#pragma omp parallel for schedule(dynamic, 256)` when row lengths vary, `static` for stencil matrices. Dot products need `reduction(+:s)`; axpys are plain parallel loops. CG is then a sequence of parallel regions with barriers; on 8 cores of a memory-bound problem expect 3-4x, not 8x, because SpMV is bandwidth bound (note 01). Gauss-Seidel needs red-black colouring to parallelise; Jacobi parallelises directly (two vectors).

## Pitfalls

- Declaring a temporary before the region and using it inside: shared by default, silent race. Declare inside, or `default(none)` to be forced to decide for every variable.
- `#pragma omp parallel for` with a `break`/`return` inside: not allowed (the loop must have a canonical form).
- Race-free but wrong: reading `counter` from a different thread before the barrier.
- Measuring speedup against the parallel code with `OMP_NUM_THREADS=1` instead of the best serial code.
- Expecting 12x on a chip with 6 fast and 6 slow cores, or on a memory-bound loop.
- Creating a parallel region inside the innermost loop: fork/join costs ~microseconds; put the region outside and use `omp for` inside.
- `omp_get_num_threads()` outside a parallel region returns 1; use `omp_get_max_threads()`.

## Exam-style questions

1. **What is a data race? Show a three-line OpenMP example and three ways to fix it, ranked by cost.** Concurrent unsynchronised access with a write: `#pragma omp parallel for  for(i) counter++;`. Fixes: `reduction(+:counter)` (private copies, cheapest), `#pragma omp atomic` (hardware RMW, ~25 ns each here), `#pragma omp critical` (lock, slowest).
2. **A loop is parallelised over 8 threads with no shared writes and shows no speedup. Name two likely causes and how to test each.** False sharing: per-thread results adjacent in one array; pad to a cache line and re-measure. Memory-bound kernel: compute the arithmetic intensity; if below the ridge point the shared bandwidth is saturated; test by measuring 1, 2, 4 threads (saturation appears early) or by running two independent copies at once.
3. **Amdahl: a code spends 10% in an unparallelised I/O phase. Maximum speedup on 16 cores? On infinitely many?** $S = 1/(0.1 + 0.9/16) = 6.4$; limit $1/0.1 = 10$.
4. **Static vs dynamic scheduling: when is each right, and what does the chunk size trade off?** Static for uniform iteration cost (no overhead, best locality, deterministic); dynamic for varying cost (triangular loops, adaptive work). Larger chunks: less scheduling overhead, worse balance at the end; smaller chunks: the opposite. Guided starts large and shrinks to balance both.
5. **Explain strong and weak scaling and what efficiency each reports.** Strong: fixed problem, $E = T_1/(p\,T_p)$, limited by Amdahl and synchronisation. Weak: problem size grows with $p$, $E = T_1/T_p$ for the scaled problem, limited by communication growth and shared resources; it is the relevant measure for "can I run a $p$ times bigger simulation on $p$ times the cores".

Code: `src/cpp/omp_examples.cpp` (`race_counter`, `false_sharing`, `unbalanced`, `heavy_sum`, scaling table), `src/cpp/threads_cpp.cpp` (`TaskManager`, `counters`, `false_sharing_ns`, `heavy_sum` - the same material in plain C++17), `src/py/scaling.py` (`amdahl`, `gustafson`, `karp_flatt`, `strong_scaling_table`); tests `src/py/test_scaling.py`. Sources: [S8] [S11] [S19] [S20] [S21] [S34] [S35].
