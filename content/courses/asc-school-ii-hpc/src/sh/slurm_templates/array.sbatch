#!/bin/bash
#SBATCH --job-name=sweep
#SBATCH --array=0-99%10              # 100 tasks, at most 10 running at once
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G                     # per task; a shared node, not an exclusive one [S13]
#SBATCH --time=00:20:00
#SBATCH --partition=zen4_0768
#SBATCH --qos=zen4_0768
#SBATCH --output=logs/%x_%A_%a.out   # %A = array job id, %a = task index
#
# array.sbatch - parameter sweep as a job array (notes/07).
#
# Each task reads one line of params.txt and runs one serial/threaded case.
# Create logs/ BEFORE sbatch: Slurm does not create the output directory.
# Every task is a full job for the scheduler: bundle cases so that each task
# runs minutes, not seconds (our rule of thumb). %10 is the throttle [S9].
# After it ran: sacct -j <jobid> --format=JobID,State,Elapsed,TotalCPU,MaxRSS
set -euo pipefail

PARAMS=${PARAMS:-params.txt}
line=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "$PARAMS")
if [ -z "$line" ]; then
    echo "task ${SLURM_ARRAY_TASK_ID}: no line in $PARAMS" >&2
    exit 1
fi

export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-1}"
out="results/case_${SLURM_ARRAY_TASK_ID}.txt"
mkdir -p results
# $line is split into arguments on purpose (one case = one line of flags)
# shellcheck disable=SC2086
srun ./my_prog $line > "$out"
echo "task ${SLURM_ARRAY_TASK_ID} of job ${SLURM_ARRAY_JOB_ID}: done -> $out"
