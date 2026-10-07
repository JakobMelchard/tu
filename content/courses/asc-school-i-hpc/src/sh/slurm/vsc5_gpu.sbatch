#!/bin/bash
#SBATCH --job-name=gpu
#SBATCH --nodes=1
#SBATCH --gres=gpu:2                 # 1 or 2 are the only allowed values [S19]
#SBATCH --time=01:00:00
#SBATCH --partition=zen3_0512_a100x2 # 2 x NVIDIA A100, "best for double precision"
#SBATCH --qos=zen3_0512_a100x2
#
# vsc5_gpu.sbatch - a GPU job on VSC-5.
#
# Choose the partition by the PRECISION your kernel needs [S9] [S19]:
#   zen3_0512_a100x2   61 nodes, 2 x A100, 40 GB,  1600 GB/s, 20 000/10 000 GFlop/s FP32/FP64
#   zen2_0256_a40x2    45 nodes, 2 x A40,  48 GB,   696 GB/s, 37 000/  578 GFlop/s FP32/FP64
# The A40 is ~1.9x faster in single precision and ~17x slower in double.
# The A40 nodes are the ONLY Zen2 CPUs on VSC-5, so build with -march=znver2
# for them and -march=znver3 for everything else [S10].
set -euo pipefail

module purge
# CUDA on the cuda-zen environment is loaded with spack, not a module [S9]:
#   spack unload && spack load cuda@<version>%gcc@<version>/<hash>
nvidia-smi || true

# <do_my_work>   # the program sees CUDA_VISIBLE_DEVICES

# Interactive alternative, for development [S9] [S19]:
#   salloc -N 1 -p zen3_0512_a100x2 --qos=zen3_0512_a100x2 --gres=gpu:2
#   squeue -u $USER          # find the node
#   ssh n3071-003            # ... and go there
# or ASC's wrapper, which does all of that for you:
#   interactivejobs -N 1 -p zen3_0512_a100x2 --qos zen3_0512_a100x2 --gres=gpu:2 -t 1:00:00
