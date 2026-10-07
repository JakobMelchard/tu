#!/bin/bash
#SBATCH --job-name=mpi
#SBATCH --nodes=2                    # -N
#SBATCH --tasks-per-node=48         # one rank per physical core on Zen3 [S19]
#SBATCH --time=01:00:00
#SBATCH --partition=skylake_0096
#SBATCH --qos=skylake_0096
#
# vsc4_mpi.sbatch - pure MPI, 2 x 48 = 96 ranks on VSC-4.
# Modelled on ASC's examples/05_submitting_batch_jobs/job_mpi_vsc4.sh [S9].
# VSC-5 version: --partition/--qos zen3_0512 and --tasks-per-node=128.
#
# Build on a login node first, with the SAME modules you load below:
#   module purge && module load <compiler> <mpi>
#   mpicc -O2 -march=skylake mpi_prog.c -o mpi_prog     # Intel: -O3 -xHost
set -euo pipefail

module purge
# module load gcc/<version>-<...>-<hash>
# module load openmpi/<version>-<...>-<hash>      # copy the whole line from `module avail`
module list

echo "job ${SLURM_JOB_ID-}: ${SLURM_JOB_NUM_NODES-} nodes, ${SLURM_NTASKS-} ranks"
echo "nodes: ${SLURM_JOB_NODELIST-}"

# ASC's own examples use mpirun with an explicit count; srun reads the
# allocation and needs no -np.  Either works; be consistent.
mpirun -np "${SLURM_NTASKS:-96}" ./mpi_prog
# srun ./mpi_prog

# Pinning, when memory bandwidth or NUMA placement matters [S9]:
#   srun --cpu-bind=map_cpu:0,64 ./mpi_prog          # one rank per socket
#   export I_MPI_PIN_PROCESSOR_LIST=0,64             # the Intel MPI equivalent
