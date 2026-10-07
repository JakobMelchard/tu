#!/bin/bash
#SBATCH --job-name=snglcre
#SBATCH --nodes=1
#SBATCH --time=00:30:00
#SBATCH --partition=zen3_0512
#SBATCH --qos=zen3_0512
#
# vsc5_single_node_many_jobs.sbatch - fill one whole node with independent
# single-core work.  ASC's single_node_multiple_jobs_vsc5.sh [S9].
#
# You are charged for the whole node anyway, so use all of it.  Two details are
# load-bearing and are the point of the exercise:
#   `&`    puts each run in the background so the loop can continue;
#   `wait` stops the script exiting - and Slurm killing the children - early.
set -euo pipefail

module purge

ncores=128                            # VSC-5 zen3 node; 48 on VSC-4 skylake
for ((i = 1; i <= ncores; i++)); do
    # <do_my_work "$i"> &
    sleep "$((i % 5 + 1))" &
done
wait
echo "all $ncores background tasks finished"

# The two can be combined: an array whose every task fills a node.
#   #SBATCH --array=1-384:128
#   j=$SLURM_ARRAY_TASK_ID; ((j += 127))
#   for ((i = SLURM_ARRAY_TASK_ID; i <= j; i++)); do ... & done; wait
