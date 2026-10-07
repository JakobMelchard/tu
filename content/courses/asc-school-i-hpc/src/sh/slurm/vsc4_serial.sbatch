#!/bin/bash
#SBATCH --job-name=single
#SBATCH --ntasks=1                   # -n : one core; the node is SHARED with others
#SBATCH --mem=2G                     # per node; needed because the node is shared
#SBATCH --time=00:10:00
#SBATCH --partition=skylake_0096     # -p : which hardware   [S19]
#SBATCH --qos=skylake_0096           # -q : which limits     ALWAYS give both  [S9]
###SBATCH --account=p7XXXX           # optional; the default project is used if omitted
#
# vsc4_serial.sbatch - one core on VSC-4, shared node.
# Modelled on ASC's own examples/05_submitting_batch_jobs/job_single_core_vsc4.sh [S9].
#
#   sbatch vsc4_serial.sbatch          output: slurm-<jobid>.out
#   squeue --me                        scancel <jobid>
#
# VSC-4 nodes: 2 x Intel Xeon Platinum 8174, 24 cores/CPU = 48 cores, 96 GB [S19].
set -euo pipefail

module purge                         # recommended in every ASC job [S9] [S19]
# module load <the EXACT line `module avail` printed when you built this>
#   e.g. module load openmpi/4.1.4-gcc-12.2.0-xt53foa
#   There is no unversioned default on the ASC systems: the whole name,
#   including the Spack hash, or nothing. [S10] [S19]
module list                          # goes into the .out file: your build record

echo "host:      $HOSTNAME"
echo "nodes:     ${SLURM_JOB_NUM_NODES-}  (${SLURM_JOB_NODELIST-})"
echo "partition: ${SLURM_JOB_PARTITION-}  qos: ${SLURM_JOB_QOS-}"
date

# <do_my_work>
sleep 5

date
