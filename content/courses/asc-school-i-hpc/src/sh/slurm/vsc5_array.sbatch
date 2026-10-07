#!/bin/bash
#SBATCH --job-name=array
#SBATCH --nodes=1
#SBATCH --array=1-20:5%2             # IDs 1,6,11,16; at most 2 running at once [S9]
#SBATCH --time=00:20:00
#SBATCH --partition=zen3_0512
#SBATCH --qos=zen3_0512
#
# vsc5_array.sbatch - a parameter sweep as ONE submission.
# This is exactly the ASC exercise: take job_array_vsc5.sh (--array=1-10) and
# change it to run 1..20 in steps of 5 [S9].
#
#   --array=1-10        ids 1..10
#   --array=1-20:5      ids 1, 6, 11, 16          (step)
#   --array=1-20:5%2    ... at most 2 at a time   (licences, or politeness)
#
# Output: slurm-<arrayjobid>_<taskid>.out.  scancel <arrayjobid> kills them all;
# scancel <arrayjobid>_11 kills one.
#
# Do NOT replace this with a shell loop of sbatch calls, and do not submit
# thousands of one-minute tasks: package short work into longer jobs [S9] [S19].
set -euo pipefail

module purge

id="${SLURM_ARRAY_TASK_ID:?this script must be submitted as an array}"
echo "array task $id of ${SLURM_ARRAY_TASK_COUNT-} " \
     "(range ${SLURM_ARRAY_TASK_MIN-}..${SLURM_ARRAY_TASK_MAX-})"

# map the index to a parameter, e.g. line $id of a file:
#   param=$(sed -n "${id}p" params.txt)
# <do_my_work "$param">
sleep "$id"
