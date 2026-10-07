#!/bin/bash
#SBATCH --job-name=hybrid
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2          # 2 MPI ranks per node ...
#SBATCH --cpus-per-task=64           # ... x 64 threads = 128 cores/node
#SBATCH --time=01:00:00
#SBATCH --partition=zen3_0512
#SBATCH --qos=zen3_0512
#
# vsc5_hybrid.sbatch - MPI + OpenMP, one rank per socket on VSC-5.
# 2 nodes x 2 ranks x 64 threads = 4 ranks, 256 cores.
#
# One rank per socket is the usual starting point: each rank then owns one
# ccNUMA domain, so first-touch initialisation and thread pinning stay inside
# it [S9].  Compare against pure MPI (vsc5_mpi.sbatch) on YOUR code before
# believing either is faster.
set -euo pipefail

module purge
# module load <compiler> <mpi>
module list

# Slurm reserves the cores but does NOT set this for you.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_PROC_BIND=close
export OMP_PLACES=cores

echo "${SLURM_NTASKS-} ranks x ${OMP_NUM_THREADS} threads"
srun --cpus-per-task="${SLURM_CPUS_PER_TASK:-1}" ./hybrid_prog
