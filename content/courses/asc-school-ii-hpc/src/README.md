# Reference implementations: ASC-School II

## Run everything

```bash
make -C c test                        # builds and runs every C program, self-checking
bash sh/test_slurm_templates.sh       # offline syntax/consistency check of the job scripts
make -C c vecreport                   # clang's vectorisation remarks for simd_dot.c
```

Requirements: Open MPI (`mpicc`, `mpirun`), a C compiler, OpenMP (Homebrew
`libomp` on macOS; the Makefile picks flags by `uname`). Without MPI or libomp
`make test` prints SKIP for the programs that need them and runs `simd_dot` only. On a cluster: build
after `module load` of compiler and MPI, and run inside a job with
`make test MPIRUN=srun MPIRUN_FLAGS=`. Every program checks its result and
exits non-zero on failure; `make test` ends with `ALL TESTS PASSED`.

## c/

| program | what | checks | note |
|---|---|---|---|
| `hybrid_pi.c` | MPI + OpenMP midpoint rule for $\pi$, `MPI_Init_thread(FUNNELED)`, compute vs allreduce time (max over ranks) | error bound $h^2/3 + 4N\varepsilon$; equals serial sum within $2N\varepsilon$; thread count $= P \cdot$ `OMP_NUM_THREADS` | [01](../notes/01-hybrid-mpi-openmp.md), [07](../notes/07-job-efficiency-and-energy.md) |
| `affinity_report.c` | host, rank, thread, CPU, allowed-CPU mask, OpenMP place for every thread (Linux; -1 on macOS) | one row per (rank, thread) | [01](../notes/01-hybrid-mpi-openmp.md) |
| `simd_dot.c` | scalar vs 4 accumulators vs `omp simd` vs NEON/AVX2 intrinsics, in L1 and from memory | exact on integer data; rounding-only differences on random data | [03](../notes/03-vectorisation-node-level.md) |
| `mpi_io_write_read.c` | 2-D block decomposition, subarray file view, `MPI_File_write_all`; read back by rows with `read_at_all`; hints queried | every element in the parallel and a serial `fread` re-read; file size | [06](../notes/06-parallel-io.md) |

`make test` runs `hybrid_pi` as 4x2, 2x1 and 3x3, `affinity_report` as 4x2
with `OMP_PROC_BIND=close OMP_PLACES=cores`, `simd_dot --quick`, and
`mpi_io_write_read` with 4 and 3 ranks, all with `--oversubscribe`.

## sh/

| file | what |
|---|---|
| `slurm_templates/hybrid.sbatch` | MUSICA CPU nodes, 8 ranks x 22 threads per node, pinning, runs `affinity_report` then `hybrid_pi` |
| `slurm_templates/gpu.sbatch` | MUSICA H100 node, 4 ranks x 1 GPU, `#ASC --vanilla`, `nvidia-smi topo -m` |
| `slurm_templates/array.sbatch` | 100-case sweep, throttle `%10`, shared-node slices, `sacct` follow-up |
| `test_slurm_templates.sh` | `bash -n`, directive placement and form, partition = QoS (or `dev_` QoS), `--time`, `shellcheck -S error` if installed |

The templates were **not submitted** (no ASC account); partition, QoS and
layout come from the ASC documentation [S13] [S14]. Check `sinfo -o %P` and
`sqos`/`sacctmgr` on the machine before the first real run.

## py/

[`py/README.md`](py/README.md): mpi4py is not installed, so no Python demo;
the program is in note 05.
