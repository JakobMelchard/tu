#!/bin/bash
#SBATCH --job-name=hybrid
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8          # one MPI rank per NUMA domain (8 per MUSICA node) [S14]
#SBATCH --cpus-per-task=22           # 22 cores each: NUMA 7 has only 22 free (WEKA reserve) [S14]
#SBATCH --threads-per-core=1         # physical cores only, no SMT siblings
#SBATCH --time=00:30:00
#SBATCH --partition=zen4_0768        # MUSICA CPU nodes, 2x EPYC 9654 [S13]
#SBATCH --qos=zen4_0768              # partition and QoS: always both, always matching [S13]
#SBATCH --output=%x_%j.out
#
# hybrid.sbatch - MPI + OpenMP on MUSICA CPU nodes (notes/01).
#
# 2 nodes x 8 ranks x 22 threads = 16 ranks, 352 cores.  8 x 22 = 176 of the
# 190 cores Slurm offers per node: the price of one layout that fits every
# NUMA domain.  Try 2 ranks x 88 threads and 190 x 1 too; measure, do not guess.
# For testing first: --qos=dev_zen4_0768 (2 nodes, 10 min) [S13].
set -euo pipefail

module purge
# module load <compiler> <mpi>       # names: `module avail` on the machine
module list 2>&1 || true

# Slurm reserves cores; it does NOT set the thread count.
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
export OMP_PLACES=cores              # one place = one physical core
export OMP_PROC_BIND=close           # threads fill the rank's cores in order

# Pass --cpus-per-task to srun explicitly: whether a step inherits it from the
# allocation has changed between Slurm releases, passing it is always right [S9].
# --cpu-bind=cores pins each rank to its block of cores; OMP_PROC_BIND then
# pins the threads inside that block.
srun --cpus-per-task="${SLURM_CPUS_PER_TASK:-1}" --cpu-bind=cores ./affinity_report
srun --cpus-per-task="${SLURM_CPUS_PER_TASK:-1}" --cpu-bind=cores ./hybrid_pi -n 2000000000
