# 05 Python for HPC: numpy, Numba, mpi4py, Dask

Prepares for *Python for HPC* (3 days, Basic; the only catalogue event that
alone reaches three training days) and *MPI for Python* [S4] [S6]. Its
notebooks are public under CC BY-SA 4.0 [S7]; `../refs/fetch-sources.sh`
clones them. Python itself, numpy idioms and `multiprocessing` are in
Scientific Programming with Python notes 07-10 [S11].

## What the course covers, in its own order [S7]

Day 1: HPC and VSC intro, modules and Spack, venv, conda, Apptainer, Slurm and
Python, debugging, benchmarking and profiling. Day 2: built-in and other
profilers, single-node performance, native code, Cython, Numba on the CPU,
Dask. Day 3: multi-node, mpi4py, Slurm and MPI, Dask distributed, Numba on the
GPU, cuDF and CuPy. Hands-on on the ASC JupyterHub with a temporary account, or
locally with Python 3 and the listed packages [S6].

## Definitions

- **GIL** (global interpreter lock): one thread executes Python bytecode at a
  time in CPython. Threads help only when the work runs in C that releases the
  GIL (numpy kernels, I/O).
- **Vectorisation (numpy sense)**: replace the Python loop by whole-array
  operations executed by compiled loops.
- **Numba**: JIT compiler for a numeric subset of Python via LLVM. `@njit`
  compiles on first call; `@njit(parallel=True)` with `prange` parallelises a
  loop with threads; `fastmath=True` allows reassociation (note 03) [S21].
- **Cython**: Python-like source translated to C, compiled ahead of time.
- **mpi4py**: MPI bindings. Lower-case methods (`comm.send`, `comm.bcast`,
  `comm.allreduce`) pickle arbitrary objects; upper-case methods
  (`comm.Send`, `comm.Allreduce`) take buffers such as numpy arrays and move
  raw bytes at near-C speed [S21].
- **Dask**: builds a task graph from chunked arrays/dataframes or
  `dask.delayed` calls and executes it with a scheduler (threads, processes,
  or `dask.distributed` across nodes) [S21].

## Worked example 1: the same integral, three speeds

Midpoint rule for $\pi$, $N = 10^7$, one core of the laptop [S10] (numpy
2.5.3, best of 3):

| implementation | time | ns/element | $\lvert\pi_N - \pi\rvert$ |
|---|---|---|---|
| pure Python loop | 0.427 s | 43 | $6.2\cdot10^{-14}$ |
| numpy, one array | 0.0141 s | 1.4 | $8.9\cdot10^{-16}$ |
| numpy, chunks of $2^{16}$ | 0.0134 s | 1.3 | $4.4\cdot10^{-16}$ |
| C, `-O2`, `hybrid_pi` P=T=1 (from $N=4\cdot10^8$) | - | 0.88 | - |

numpy is 30x faster than the loop and within 1.6x of scalar C; the chunked
version avoids a 80 MB temporary and is slightly faster (cache). numpy's sum
is also more accurate: it uses **pairwise summation**, error $O(\log N\,
\varepsilon)$ instead of $O(N\varepsilon)$ for the running sum.

## Worked example 2: mpi4py (not run: mpi4py is not installed here)

```python
# pi_mpi.py - run: mpirun -n 4 python pi_mpi.py   or, in a job: srun python pi_mpi.py
from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
rank, size = comm.Get_rank(), comm.Get_size()
N = 10_000_000
lo, hi = rank * N // size, (rank + 1) * N // size      # block distribution
x = (np.arange(lo, hi) + 0.5) / N
local = np.array(np.sum(4.0 / (1.0 + x * x)) / N)
pi = np.zeros(1)
comm.Allreduce(local, pi, op=MPI.SUM)                  # buffer API: no pickling
if rank == 0:
    print(pi[0], abs(pi[0] - np.pi))
```

`comm.allreduce(float(local), op=MPI.SUM)` (lower case) gives the same number
via pickling: fine for scalars, slow for large arrays. On the cluster, the
Python environment has to be visible on every node and mpi4py must be built
against the **same MPI** that `srun` launches (`MPICC=mpicc pip install
--no-binary mpi4py mpi4py` inside the loaded modules) [S21].

## Worked example 3: Numba and Dask in two lines each

```python
from numba import njit, prange
@njit(parallel=True, fastmath=True)
def pi_numba(n):
    s = 0.0
    for i in prange(n):                   # threads; reduction recognised by Numba
        x = (i + 0.5) / n
        s += 4.0 / (1.0 + x * x)
    return s / n

import dask.array as da
x = (da.arange(N, chunks=1_000_000) + 0.5) / N
pi = (4.0 / (1.0 + x * x)).sum().compute() / N   # graph of 10 chunks, then run
```

Numba's first call includes compilation (typically 0.1-1 s; unsourced
estimate): time the second call, or use `cache=True`. Numba's threads obey
`NUMBA_NUM_THREADS`, not `OMP_NUM_THREADS`.

## Environments on the cluster

- `$HOME` quota on MUSICA is 50 GB and 10 million files; ASC warns that conda
  environments "might get too big" for it [S13]. Put them in `$DATA` or use a
  container (Apptainer, day 1 of the course [S7]).
- Build environments on a node of the type you run on (note 03, `-march`).
- One BLAS thread pool per rank: with 8 ranks per node set
  `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS` or `MKL_NUM_THREADS` to the cores
  per rank, or numpy's BLAS spawns one thread per core in every rank.

## Pitfalls

- Lower-case mpi4py calls on large numpy arrays: pickling copies and
  serialises; use the upper-case buffer methods.
- Every rank importing a large package from a parallel file system at start-up
  stresses metadata servers at scale (common experience; unsourced for ASC).
- Dask's default scheduler on the login node: the work runs on the login node,
  which has per-user CPU and memory limits (sibling course, note 03).
- `multiprocessing` inside an MPI rank: forks under the MPI library, often
  unsupported.
- Comparing Numba timings that include the JIT compile.

## Questions (ours)

1. *Why can a threaded pure-Python loop not use 8 cores, but a threaded numpy
   loop can?* The GIL serialises bytecode; numpy kernels release it while they
   run.
2. *`comm.bcast(big_array)` vs `comm.Bcast(big_array)`?* The first pickles and
   sends a byte string (extra copies, receiver needs no buffer); the second
   sends the raw buffer into a pre-allocated array of the same shape and dtype.
3. *8 ranks per node, each numpy `@` product runs slower than with 1 rank.*
   Each rank's BLAS starts one thread per core: 8x oversubscription. Set
   `OMP_NUM_THREADS` (and the BLAS-specific variable) to cores per rank.
4. *Why is the numpy sum of $10^7$ terms more accurate than the loop?* Pairwise
   summation: rounding error grows like $\log_2 N$ instead of $N$.
5. *When is Dask the right tool rather than mpi4py?* Task-parallel or
   out-of-core workflows on chunked data with a dynamic graph (pipelines,
   parameter studies, larger-than-memory arrays); mpi4py for SPMD codes with
   regular communication (halo exchange, collectives).

## Code

- [`../src/py/README.md`](../src/py/README.md): why there is no
  `mpi4py_demo.py` (mpi4py is not installed in the repo venv; not installed by
  this pass), and how to run the snippet above once it is.
