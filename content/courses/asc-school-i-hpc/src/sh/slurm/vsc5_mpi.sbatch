#!/bin/bash
#SBATCH --job-name=mpi
#SBATCH --nodes=2                    # -N
#SBATCH --tasks-per-node=128         # one rank per physical core on Zen3 [S19]
#SBATCH --time=01:00:00
#SBATCH --partition=zen3_0512
#SBATCH --qos=zen3_0512
#
# vsc5_mpi.sbatch - pure MPI, 2 x 128 = 256 ranks on VSC-5.
# Modelled on ASC's examples/05_submitting_batch_jobs/job_mpi_vsc5.sh [S9].
# VSC-4 version: --partition/--qos skylake_0096 and --tasks-per-node=48.
#
# Build on a login node first, with the SAME modules you load below:
#   module purge && module load <compiler> <mpi>
#   mpicc -O2 -march=znver3 mpi_prog.c -o mpi_prog     # znver2 on the A40 nodes!
set -euo pipefail

module purge
# module load gcc/<version>-<...>-<hash>
# module load openmpi/<version>-<...>-<hash>      # copy the whole line from `module avail`
module list

echo "job ${SLURM_JOB_ID-}: ${SLURM_JOB_NUM_NODES-} nodes, ${SLURM_NTASKS-} ranks"
echo "nodes: ${SLURM_JOB_NODELIST-}"

# ASC's own examples use mpirun with an explicit count; srun reads the
# allocation and needs no -np.  Either works; be consistent.
mpirun -np "${SLURM_NTASKS:-256}" ./mpi_prog
# srun ./mpi_prog

# Pinning, when memory bandwidth or NUMA placement matters [S9]:
#   srun --cpu-bind=map_cpu:0,64 ./mpi_prog          # one rank per socket
#   export I_MPI_PIN_PROCESSOR_LIST=0,64             # the Intel MPI equivalent
