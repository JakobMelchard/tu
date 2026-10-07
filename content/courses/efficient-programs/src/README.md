# 185.190 Efficient Programs: reference implementations

C11 only: the course's example programs are C [S8] [S9], the exercises are
done with `gcc`, `perf`, `gprof` and `gcov` on the Linux course machine
`g0.complang.tuwien.ac.at` (Rocket Lake) [S5]–[S7]. Every program here is our
own code (see [`../refs/README.md`](../refs/README.md) for why nothing of the
lecturer's is copied), runs as a demo, has a `--test` mode with a self-check
that exits non-zero on failure, and a `--bench` mode that prints the numbers
the notes quote.

## Build, test, benchmark (everything)

```sh
make -C c            # cc -O2 -std=c11 -Wall -Wextra, no dependencies, builds warning-free
make -C c test       # all six self-checks, ~2 s
make -C c bench      # the timing tables in the notes, ~10 s on the M3 Pro
make -C c gcov       # line execution counts for profile_demo (macOS clang and Linux gcc)
make -C c clean
```

Portable on purpose: no `-march=native`, no intrinsics, so the same source
builds on Apple Silicon and on g0. On g0 build with
`make -C c CC=gcc CFLAGS='-O3 -march=native -std=c11 -Wall -Wextra'` for the
vectorised numbers; the tests still have to pass.

## c/

| file | note | what it shows | self-check |
|---|---|---|---|
| `matmul_steps.c` | [09](../notes/09-matmul-worked-example.md), 06 | `ijk` → `ikj` (interchange) → `dotT` (transposed B, 4 accumulators) → `blocked` (64×64 tiles) → `ikj4` (k unrolled by 4); ms, ns/iteration, GFLOP/s | `ijk` equal to an independent recomputation, all versions bit-identical to it (integer-valued inputs, non-degenerate A and B) for n = 1, 5, 33, 64, 100 |
| `pointer_chase.c` | [04](../notes/04-memory-hierarchy.md), 11 | our `memory1`: cyclic list, `random`/`linear`, `<elements> <stride>`, ns per dependent load; `--sweep` walks 2 KB … 128 MB | list is one cycle of exactly `elements` nodes for 6 sizes × 4 strides × 2 modes |
| `tsp_greedy.c` | [08](../notes/08-tsp-worked-example.md), 07 | greedy nearest-neighbour TSP: baseline → no `sqrt` + hoisting → compaction instead of `visited[]` → lazy y-distance; ms, ns per candidate, speedup | identical tour from all four versions for 6 sizes × 3 seeds; greedy property verified independently |
| `branch_predict.c` | [03](../notes/03-hardware-latency-and-throughput.md), 07 | filter with an `if` on sorted vs unsorted data, and the branchless `out[k]=v; k+=cond` form; estimates the cost of one misprediction | branch and branchless keep the same elements in the same order; sorted and unsorted runs keep the same multiset (histogram); count equals the number of inputs ≥ 128 |
| `recurrence.c` | [03](../notes/03-hardware-latency-and-throughput.md) | double sum with 1/2/4/8 accumulators, int64 sums, linked-list sum, `a[i]+=f`; ns and estimated cycles per element | every kernel returns the exact sum |
| `profile_demo.c` | [02](../notes/02-measurement-and-profiling.md), 11 | one hot function (`is_prime_trial`, ~92 % of the time) next to cheap ones; header lists the gprof/gcov/perf command lines | π(200 000) = 17 984 by trial division and by sieve |
| `util.h` | none | monotonic timer, xorshift64\* RNG, `CHECK`, flag parsing | none |

Timings are wall-clock (`clock_gettime(CLOCK_MONOTONIC)`), best-of or single
pass as stated by each program; the timers bracket the kernel, never the
input generation (work a version needs for itself, such as `tsp_greedy`'s
`visited[]`/`rest[]` arrays or `dotT`'s transpose, is inside). Run to run the
M3 Pro varies by about ±10 % (clock), so the notes quote ranges over four
`make bench` runs. "cycles" columns are ns × 4.05 GHz, an **assumed** P-core
clock, and are estimates: macOS gives user code no cycle counter [S19]. On g0 use `perf stat
-e cycles:u` instead and ignore the estimate.

## What only works on Linux (g0), and the exact commands

macOS has `/usr/bin/time -l` and `gcov` but **no `perf` and no `gprof`**
(`cc -pg` compiles and writes no `gmon.out`) [S19]. So notes 02, 04 and 11
show these as *described*, with the command lines to run on g0:

```sh
# slide 9: time, gprof, gcov                                    [S3 p.9]
/usr/bin/time ./profile_demo                       # user, system, elapsed, maxresident
gcc -pg -O2 profile_demo.c -o profile_demo_pg && ./profile_demo_pg >/dev/null && gprof -b profile_demo_pg | head -40
gcc -O2 --coverage -c profile_demo.c && gcc --coverage profile_demo.o -o profile_demo_cov \
    && rm -f *.gcda && ./profile_demo_cov >/dev/null && gcov profile_demo.c \
    && sort -rn profile_demo.c.gcov | head       # = make gcov; two steps so .gcno/.gcda carry the source's name

# slide 22: counters and perf profiling                          [S3 p.22]
perf list | less
perf stat -e cycles:u -e instructions:u -e branch-misses:u -e L1-dcache-load-misses:u -e dTLB-load-misses:u ./profile_demo
perf record -e cycles:u ./profile_demo >/dev/null && perf report --stdio | head -30 && perf annotate --stdio is_prime_trial | less
perf stat -M TopdownL1 ./profile_demo              # slide 23

# exercise 3 style, with our pointer_chase instead of memory1     [S7]
LC_NUMERIC=prog perf stat -e cycles:u -e L1-dcache-load-misses:u -e dtlb_load_misses.stlb_hit:u -e dTLB-load-misses:u \
    ./pointer_chase random 5000 8
for e in 256 512 1024 2048 4096 8192; do perf stat -e L1-dcache-load-misses:u ./pointer_chase random $e 64 2>&1 | grep -E 'size|L1'; done

# exercise 2 style: instructions vs cycles                        [S6]
perf stat -e cycles:u -e instructions:u ./recurrence --bench
```

`make -C c gprof` runs the gprof line and `make -C c perf` the `perf stat` and
`perf record`/`report` lines of the first two blocks (not `annotate` or
TopDown); both fail on macOS by design. Build outputs are listed in
`c/.gitignore`.

Every `[S<n>]` resolves to [`../refs/SOURCES.md`](../refs/SOURCES.md).
