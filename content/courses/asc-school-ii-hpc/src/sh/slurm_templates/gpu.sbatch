#!/bin/bash
#ASC --vanilla
#SBATCH --job-name=gpu
#SBATCH --nodes=1
#SBATCH --gres=gpu:4                 # all 4 H100 of the node; 1, 2 or 3 give a share [S13]
#SBATCH --ntasks-per-node=4          # one rank per GPU
#SBATCH --cpus-per-task=22           # the physical cores of that GPU's NUMA domain [S14]
#SBATCH --threads-per-core=1
#SBATCH --time=00:30:00
#SBATCH --partition=zen4_0768_h100x4
#SBATCH --qos=zen4_0768_h100x4
#SBATCH --output=%x_%j.out
#
# gpu.sbatch - one MPI rank per GPU on a MUSICA H100 node (notes/04).
#
# `#ASC --vanilla` switches off ASC's job-script rewriting so that the
# explicit task layout above is used as written; it is the form of ASC's own
# 4-tasks x 22-cores example [S13].  Drop it to get the site defaults.
# The GPUs hang off NUMA domains 2, 3, 4 and 6; srun pins each task to the
# domain of its GPU [S14].  Check with `nvidia-smi topo -m` below.
# VSC-5 instead: --partition/--qos=zen3_0512_a100x2, --gres=gpu:1|2 [S12].
# For testing first: --qos=dev_zen4_0768_h100x4 (2 nodes, 10 min) [S13].
set -euo pipefail

module purge
# module load <cuda> <compiler> <mpi>
nvidia-smi --query-gpu=index,name,memory.total --format=csv || true
nvidia-smi topo -m || true

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
# Each rank sees all 4 GPUs unless bound; pick one per local rank:
#   int dev = local_rank % ndev; cudaSetDevice(dev);   (in the program)
srun --cpus-per-task="${SLURM_CPUS_PER_TASK:-1}" ./my_gpu_prog

# Profile one run with Nsight Systems (writes report_<rank>.nsys-rep):
#   srun nsys profile -o report_%q{SLURM_PROCID} ./my_gpu_prog
