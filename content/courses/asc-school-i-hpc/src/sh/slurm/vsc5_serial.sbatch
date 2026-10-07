#!/bin/bash
#SBATCH --job-name=single
#SBATCH --ntasks=1                   # -n : one core; the node is SHARED with others
#SBATCH --mem=4G                     # per node; needed because the node is shared
#SBATCH --time=00:10:00
#SBATCH --partition=zen3_0512        # -p : which hardware   [S19]
#SBATCH --qos=zen3_0512              # -q : which limits     ALWAYS give both  [S9]
###SBATCH --account=p7XXXX           # optional; the default project is used if omitted
#
# vsc5_serial.sbatch - one core on VSC-5, shared node.
# Modelled on ASC's own examples/05_submitting_batch_jobs/job_single_core_vsc5.sh [S9].
#
# VSC-5 nodes: 2 x AMD EPYC 7713 (Zen3), 64 cores/CPU = 128 cores, 512 GB [S19].
set -euo pipefail

module purge
# module load <the EXACT line `module avail` printed when you built this>
module list

echo "host:      $HOSTNAME"
echo "nodes:     ${SLURM_JOB_NUM_NODES-}  (${SLURM_JOB_NODELIST-})"
echo "partition: ${SLURM_JOB_PARTITION-}  qos: ${SLURM_JOB_QOS-}"
date

# <do_my_work>
sleep 5

date
