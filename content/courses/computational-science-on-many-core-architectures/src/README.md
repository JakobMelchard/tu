# 360.252 - reference implementations

Three directories:

| dir | language | status on this Mac (Apple M3 Pro, no CUDA) |
|---|---|---|
| `cpp/` | C++17 + OpenMP (Homebrew libomp) | **built, tested, benchmarked** |
| `py/` | Python 3.12 (repo venv), numpy, matplotlib, pytest | **tested** |
| `cuda/` | CUDA C++ | **untested here: no nvcc, no NVIDIA GPU.** Syntax- and type-checked only (`make -C cuda syntax`) |

Every CUDA kernel's host-side logic is mirrored in a CPU program that runs the
same algorithm with the same checks:

| CUDA (untested) | CPU mirror (tested) | what is checked | note |
|---|---|---|---|
| `cuda/vector_add.cu` | `cpp/stream_triad.cpp` | $x = y + z$ exact; bandwidth vs $N$; alpha-beta fit | 02, 03 |
| `cuda/reduction.cu` | `cpp/reduction_scan.cpp` (`reduce_blocks`, `reduce_thread_tree`) | sums of integer-valued data exact; float tree vs running sum | 04 |
| `cuda/scan.cu` | `cpp/reduction_scan.cpp` (`scan_hillis_steele`, `scan_blelloch`, `scan_three_phase`) | Rupp's slide example [S4]; equals `std::*_scan`; add counts $n\log_2 n-(n-1)$ and $2(n-1)$ | 04 |
| `cuda/tiled_matmul.cu` | `cpp/matmul_tiling.cpp` | naive and tiled equal the triple loop exactly (integer entries) | 04 |
| `cuda/stencil.cu` | `cpp/stencil_halo.cpp` | blocked, halo-exchange and naive sweeps bitwise equal; $x^2-y^2$ fixed point; convergence | 03, 04 |
| - | `cpp/spmv_csr_ell.cpp` | CSR = ELL = SELL-C-$\sigma$ bitwise; Laplacian row sums; dense cross-check | 03, 04 |
| - | `cpp/atomics_histogram.cpp` | atomic, privatised and array-reduction histograms equal serial | 04 |

## Build, test, benchmark

From the course folder:

```sh
make -C src/cpp test        # 6 programs, --test each (~5 s)
make -C src/cpp bench       # timing tables (~1 min); prints the load average next to each table
make -C src/cuda            # prints SKIP here (no nvcc); builds bin/* where nvcc exists
make -C src/cuda test       # on a CUDA machine: build + run all five, each self-checking
make -C src/cuda syntax     # clang CUDA front end, host and device side, against cuda/syntax/cuda_runtime.h
python -m pytest src/py -q                    # 16 tests
python src/py/roofline.py --png notes/img/roofline.png
python src/py/perf_models.py                  # worked examples of notes 01, 03, 04, 06, 07
```

`python` is the repo venv (from the root `pyproject.toml`, Python 3.12). Run
this folder's tests by path as above.

Requirements: `clang++` (Apple clang 21.0.0 used), Homebrew `libomp`
(`-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include
-L/opt/homebrew/opt/libomp/lib -lomp`; without it `make -C cpp test` prints
SKIP and builds nothing). For CUDA: `nvcc` with C++17 support;
default `ARCH=-arch=sm_70` (change with `make ARCH=-arch=sm_90`); the double
`atomicAdd` in `reduction.cu` needs cc $\ge$ 6.0 [S15]. `stencil.cu` is built
with `-fmad=false` so its bitwise check against the host is meaningful. No
network access, no data files; everything is generated.

## Files

### `cpp/`
- `common.hpp` - `--test`/`--bench` parsing, best-of-$k$ timer, checks, splitmix64 RNG, `print_load`.
- `stream_triad.cpp` - STREAM copy/scale/add/triad over a thread sweep; roofline point of the triad; empty-parallel-region latency; $T(N)$ table and alpha-beta fit, $n_{1/2}$.
- `reduction_scan.cpp` - three reductions, three scans, work counts, float accuracy.
- `matmul_tiling.cpp` - naive vs tiled ($T$ = 8..64) with explicit "shared-memory" tile buffers.
- `stencil_halo.cpp` - Jacobi: naive, tile + halo staging, strip decomposition with halo exchange.
- `spmv_csr_ell.cpp` - CSR, ELL (column-major), SELL-C-$\sigma$; fill efficiency $\beta$; GB/s per format.
- `atomics_histogram.cpp` - `omp atomic` on shared bins vs private bins + merge vs array-section reduction.

### `py/`
- `perf_models.py` - Amdahl, Gustafson, Shi, Karp-Flatt, offload; Little; alpha-beta, $n_{1/2}$; CUDA occupancy (Table 27 limits [S15]); pipeline cycles and accumulation II (FPGA); pJ/flop.
- `roofline.py` - parses the vendored Rupp data [S5]; machines table; kernel intensities; `--png` plot.
- `test_perf_models.py` (11 cases), `test_roofline.py` (5; incl. the vendored-data parse and the plot), `conftest.py`.

### `cuda/`
- `common.cuh` - `CUDA_CHECK`, event timer, device print.
- `vector_add.cu` - grid-stride kernel, alpha-beta table, pageable vs pinned H2D, 1 vs 4 streams.
- `reduction.cu` - Harris kernels 1 and 3 [S16], shuffle + `atomicAdd`.
- `scan.cu` - Hillis-Steele block (Rupp's slide [S4]), Blelloch block with bank-conflict padding [S18], recursive multi-block scan.
- `tiled_matmul.cu` - naive and `mm_tiled<16|32>`.
- `stencil.cu` - naive and shared-memory tile with halo.
- `syntax/cuda_runtime.h` - **not CUDA**: declarations only, so clang can parse the `.cu` files without a toolkit.
