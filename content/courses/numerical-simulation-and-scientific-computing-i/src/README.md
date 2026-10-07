# 360.242 NSSC I - reference implementations

C++17 is the primary language (the course assumes C++ and Python basics [S1] [S6]); Python versions exist where the comparison with scipy is instructive; bash scripts cover the software-engineering topic.

**Where a source states a reference result, a test reproduces it.** Those are the tests worth trusting:

| test | reproduces | source |
|---|---|---|
| `test_lattice.py::test_randu_triples_lie_on_15_planes` | Marsaglia's RANDU example: `x_{k+2} - 6x_{k+1} + 9x_k = 0 (mod 2^31)` identically, and exactly **15** occupied planes | [S27] |
| `test_lattice.py::test_hull_dobell_exhaustive_m16` | the Hull-Dobell full-period theorem, over **all** 256 `(a,c)` pairs and all 16 seeds at `m = 16` - a complete check of an iff at that modulus | [S29] |
| `test_lattice.py::test_cpp_standard_required_10000th_values` | the three 10000th values ISO C++ **requires**: 1043618065, 399268537, 4123659995 | [S14] |
| `test_scaling.py::test_gustafson_reproduces_the_1024_processor_result` | Gustafson's 1024-processor speedups for serial fractions 0.4-0.8 %: 1019.9 and 1015.8 | [S20] |
| `test_scaling.py::test_the_two_laws_are_one_law` | Shi's identity: converting the serial fraction makes Amdahl and Gustafson give the same number to 9 digits | [S21] |
| `test_fdstencil.py` | note 03's stencil weights and signed error constants, in exact rational arithmetic | [S25] |
| `test_vtk_check.py` | the legacy VTK format clause by clause, and the eight cell type ids read out of VTK's own header | [S12] [S13] |
| `test_delaunay.py` | the empty-circumcircle property, the Euler count `2n-2-h`, max-min-angle optimality, and agreement with Qhull | [S32] |
| `test_montecarlo.py`, `rng_mc.cpp --test` | the same C++ standard RNG vectors, plus KS tests on the samplers | [S14] |

Sources are registered in [`../refs/SOURCES.md`](../refs/SOURCES.md).

## Build, test, benchmark (everything)

```sh
make -C cpp test                      # build bin/ and run every program with --test (~10 s from clean, ~5 s once built)
make -C cpp bench                     # timing tables (a few minutes)
make -C cpp cmake                     # the same build through CMake + ctest (note 10)
uv run pytest py -q     # 64 tests, cross-checked against scipy and against sources
uv run pytest . -q      # 101 tests: the above plus exercises/ (builds one C++ file)
make -C exercises/tuwien-introsc-2025 test    # the C++ solution's own assertions
sh/build_and_bench.sh [--quick]       # builds, runs benchmarks, prints a one-screen summary
sh/git_workflow.sh                    # annotated feature-branch workflow on a temp repo
sh/sanitizers.sh                      # ASan/UBSan reports for buggy_sample.cpp
```

Run from this `src/` folder. `uv run` uses the repo venv (Python 3.12, created with `uv sync` at the repo root); all three commands were re-run on 2026-09-27. Build output (`cpp/bin/`, `cpp/build/`, `exercises/*/bin/`) is git-ignored by the `.gitignore` next to it.

Requirements: `clang++` (Xcode command line tools), Homebrew `libomp` (`brew install libomp`; the Makefile uses `-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp`); without it `make test` skips `omp_examples`, the repo venv with numpy/scipy/matplotlib/pytest. For `make cmake`, CMake >= 3.20 (`brew install cmake`; verified with 4.4.3, again on 2026-09-27). No network, no data downloads.

Two build systems on purpose: the Makefile is note 10's Make example, `CMakeLists.txt` is its CMake example, and both build the same nine-plus-one programs. `ctest` runs 10/10.

## exercises/ - substitute practice material from other courses

**Not 360.242 material.** This course publishes no exercise sheet and no past
paper [S1] [S4]. Each directory is another course's or another author's
material, restated in our words with our own solution, and each states its
institution, course, year, licence, URL and retrieval date in its own
`README.md` and in the header of its solution file. **Nothing is vendored.**

| directory | source | licence | TISS topics | solution | tests |
|---|---|---|---|---|---|
| `tuwien-introsc-2025/` | J. Schöberl, *Introduction to Scientific Computing*, TU Wien E101 [S8] [S9] - **a 2026W lecturer of this course** | LGPL-2.1 / MIT | 1, 2, 7 | `taskmanager_matmul.cpp` - a CAS lock and `lock_guard`, a `std::thread` task manager, matmul over row bands, scaling table. **No OpenMP**, because that lecturer teaches a hand-written task manager instead [S8] | `make test`, and `test_taskmanager_matmul.py` (2) |
| [`utaustin-theartofhpc-2022/`](exercises/utaustin-theartofhpc-2022/README.md) | V. Eijkhout, *The Art of HPC* vol. 1, UT Austin / TACC [S43] | CC BY 4.0 | 1, 2, 8 | `cache_sim.py` - set-associative cache simulator; the direct-mapped conflict example, the k-way occupancy sweep, tree vs linear summation locality | `test_cache_sim.py` (14) |
| [`cornell-cs5220-2015/`](exercises/cornell-cs5220-2015/README.md) | D. Bindel, Cornell CS 5220 *Applications of Parallel Computers*, Fall 2015, HW3 [S44] | MIT | 2, 7, 8 | `minplus_path.py` - all-pairs shortest paths in the $(\min,+)$ semiring: Floyd–Warshall vs repeated squaring, blocked kernel, cost model | `test_minplus_path.py` (21) |

Results these reproduce, in the same spirit as the table above:

| test | reproduces |
|---|---|
| `test_cache_sim.py::test_e2_direct_mapped_occupancy_matches_the_closed_form` | $n\bigl(1-(1-1/n)^n\bigr) = 20.41$ for $n=32$, against a measured mean of 20.44 over 100 trials |
| `test_cache_sim.py::test_e1_high_bits_remove_the_conflicts` | 1536 conflict misses become 384 - the compulsory minimum, one per 32-byte line per row |
| `test_minplus_path.py::test_squaring_and_floyd_warshall_agree` | two independent APSP routes, both against `scipy.sparse.csgraph.shortest_path` |
| `test_taskmanager_matmul.py::test_cpp_assertions_pass` | a CAS lock that does not lose any of 80 000 non-atomic increments, and a task-parallel matmul bit-identical to the naive triple loop |

The problems built on top of these are in
[`../notes/11-practice-set.md`](../notes/11-practice-set.md), which also names
the TISS topics for which **no** free practice material exists.

## cpp/ (C++17, `clang++ -std=c++17 -O2 -Wall -Wextra`)

Every program runs as a demo (`./bin/x`), as a test with assertions on known results (`./bin/x --test`, exit code 1 on failure) and, where timing matters, as a benchmark (`./bin/x --bench`). `common.hpp` holds the timer, the `CHECK` macro and the mode parser.

| file | note | what it shows |
|---|---|---|
| `cache_bench.cpp` | 01 | pointer-chasing latency per working-set size, stride sweep, loop order, triad bandwidth, scalar FLOP/s, roofline classification |
| `matmul_opt.cpp` | 02 | naive vs `ikj` vs transposed vs blocked matmul, best-of-3 GFLOP/s, results cross-checked; `--bench` adds a block-size sweep at n = 2048 (one level of tiling loses to `ikj` here; note 02 derives why) |
| `fd_poisson1d.cpp` | 03, 04, 05 | `-u'' = f` with Thomas and matrix-free CG, convergence table (order 2), CG iterations ~ N |
| `heat2d.cpp` | 04 | explicit Euler at r = 0.24 / 0.30 and implicit Euler (CG) with CFL check against the exact solution |
| `csr.cpp` | 05 | CSR storage and SpMV, Jacobi / Gauss-Seidel / SOR / CG / Jacobi-PCG on the 2D Poisson system |
| `rng_mc.cpp` | 06 | LCG vs `std::minstd_rand0` and `std::mt19937` (standard 10000th values), inverse transform, Box-Muller, MC pi and integral, 1/sqrt(N) fit, antithetic and control variates |
| `omp_examples.cpp` | 07 | race condition and its fixes, false sharing (counters are `volatile` so the measurement is not optimised away), schedules, strong scaling vs threads (needs libomp) |
| `threads_cpp.cpp` | 07 | the same topic without OpenMP: a `TaskManager` worker pool over `std::thread`, the four accumulation strategies and their cost, false sharing with atomics (20-50x), strong scaling, thread-pool startup cost |
| `containers_bench.cpp` | 08 | vector / list / deque / map / unordered_map / sorted vector timings |
| `vtk_writer.cpp` | 09 | legacy VTK STRUCTURED_POINTS (scalar + vector) and UNSTRUCTURED_GRID (triangles) writers; demo writes `field.vtk`, `mesh.vtk`, both validated against the specification by `py/vtk_check.py` |
| `CMakeLists.txt` | 10 | the worked CMake example, executed: `CMAKE_CXX_STANDARD_REQUIRED`, the `OpenMP_ROOT` workaround for AppleClang, `enable_testing` + `add_test` |

## py/ (Python 3.12, numpy/scipy)

| file | note | what it shows | test |
|---|---|---|---|
| `fd_poisson.py` | 03, 04 | FD derivatives and composite quadrature with orders, Thomas, 1D Poisson, 2D Poisson via `scipy.sparse` Kronecker sum | `test_fd_poisson.py` (orders, Euler-Maclaurin error constants, scipy `spsolve`, `quad`) |
| `heat2d.py` | 04 | explicit vs implicit Euler (`splu` factorised once), CFL limit | `test_heat2d.py` (stable, blow-up, first order in dt) |
| `montecarlo.py` | 06 | LCG, inverse transform, Box-Muller, MC pi/integral, error scaling, variance reduction | `test_montecarlo.py` (known LCG values, KS tests, slope -0.5) |
| `csr.py` | 05 | pure-numpy CSR with Jacobi / SOR / (P)CG | `test_csr.py` (against `scipy.sparse`, iteration ordering) |
| `plot_helper.py` | 04, 09 | log-log convergence plot and 2D field plot into `notes/img/` | `test_plot_helper.py` (slope 2 of the plotted errors, valid PNGs written to a temp dir) |
| `fdstencil.py` | 03 | FD weights from the order conditions (exact rationals) and by Fornberg's recurrence; signed leading error terms; regenerates note 03's table | `test_fdstencil.py` (exact weights, measured orders, non-uniform nodes) |
| `lattice.py` | 06 | Hull-Dobell full-period predicate, brute-force period, Marsaglia's plane bound, the RANDU lattice | `test_lattice.py` (exhaustive at m=16, exact RANDU identity, C++ standard vectors) |
| `scaling.py` | 07 | Amdahl, Gustafson, the conversion between their serial fractions, Karp-Flatt, scaling tables | `test_scaling.py` (Gustafson's 1024-processor numbers, the two-laws identity) |
| `delaunay.py` | 09 | Bowyer-Watson triangulation, circumcircle predicate, Delaunay check, minimum angle | `test_delaunay.py` (vs scipy/Qhull, Euler count, max-min-angle) |
| `vtk_check.py` | 09 | a validating reader for the legacy VTK format; cell type ids read from the vendored `vtkCellType.h`; also a conforming writer | `test_vtk_check.py` (every note-09 pitfall rejected; the C++ writer's own output parsed back) |

## sh/ (bash, `set -euo pipefail`)

| file | note | what it does |
|---|---|---|
| `build_and_bench.sh` | 01, 02, 07 | `make all`, runs the `--bench` modes, extracts a summary table (bandwidth, peak, latency, matmul, CG, OpenMP speedup, MC slope); `--quick` uses demo sizes |
| `git_workflow.sh` | 10 | init, branch, commit, rebase, `--no-ff` merge, tag, stash on a temporary repository, every command echoed |
| `sanitizers.sh` + `buggy_sample.cpp` | 10 | heap overflow, use-after-free, signed overflow, stack overflow: silent at `-O1`, reported with `-fsanitize=address,undefined` |
