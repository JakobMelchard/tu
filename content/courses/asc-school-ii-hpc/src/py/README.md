# src/py: mpi4py demo (not present)

`mpi4py` is **not installed** in the repo venv (root `pyproject.toml`), checked
2026-09-28 with `python -c "import mpi4py"`; neither are `numba`,
`dask` or `h5py`. This pass did not install anything, so there is no
`mpi4py_demo.py` and no untested code.

The program that would go here is printed in full in
[`../../notes/05-python-for-hpc.md`](../../notes/05-python-for-hpc.md)
(worked example 2, the midpoint-rule $\pi$ with `comm.Allreduce`). To run it
once mpi4py is available, build it against the same Open MPI the C code uses:

```bash
MPICC=mpicc ../../../../.venv/bin/python -m pip install --no-binary=mpi4py mpi4py
mpirun --oversubscribe -np 4 ../../../../.venv/bin/python pi_mpi.py
```

(Adding a dependency to the venv changes `pyproject.toml` for the whole repo;
decide that deliberately.) On the cluster use the Python environment from the
*Python for HPC* course [S7] and `srun python pi_mpi.py` inside a job.
