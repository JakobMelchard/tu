#!/bin/bash
#SBATCH --job-name=devel
#SBATCH --nodes=1
#SBATCH --time=00:10:00              # the devel QoS hard limit IS 10 minutes [S19]
#SBATCH --partition=zen3_0512        # the partition is the normal one ...
#SBATCH --qos=zen3_0512_devel        # ... only the QoS changes              [S19]
#
# vsc5_devel.sbatch - the queue to use while you are still debugging.
#
# The devel QoS gives up to 5 nodes for 10 minutes at priority 5000000 against
# the normal 1000, so it starts in seconds rather than hours [S9] [S19].  ASC
# recommends running here before sending anything to a compute queue.
# VSC-4 equivalent: --partition=skylake_0096 --qos=skylake_0096_devel
# GPU equivalent:   --partition=zen3_0512_a100x2 --qos=zen3_0512_a100x2_devel (2 nodes)
#
# NOTE: --time is REQUIRED here.  Without it the default 24 h exceeds the QoS
# limit and the job is rejected with reason QOSMaxWallDurationPerJobLimit /
# PartitionTimeLimit [S9] [S19].
set -euo pipefail

module purge
hostname
free -g
nproc
echo "partition ${SLURM_JOB_PARTITION-} qos ${SLURM_JOB_QOS-}"
