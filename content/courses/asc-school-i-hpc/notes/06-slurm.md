# 06 Slurm on the ASC systems

Block 2, the two longest sessions of the day: *Slurm (basics)* 11:35–12:55 and
*Slurm (advanced)* 14:00–15:00 [S8]. Code:
`src/sh/slurm/` — job templates that mirror ASC's own
examples, plus [`slurm_cheatsheet.md`](../src/sh/slurm/slurm_cheatsheet.md).

Everything ASC-specific here comes from the lecturer's March-2026 decks [S9] and
the user documentation [S19]; everything that is plain Slurm behaviour comes
from SchedMD's manual [S16]. No job was submitted to produce this note.

## The one ASC rule that is not in the Slurm manual

> **Always give both `--qos` and `--partition`, and make them match.** [S9]

A **partition** is a set of nodes with the same hardware; a **QoS** is a set of
limits (run time, priority, node count) attached to your project. On most sites
you pick a partition and get a QoS implicitly. On ASC the slide says, in the
margin of three different slides, *"always provide: qos & partition"*, and they
are usually spelled the same:

```bash
#SBATCH --partition=zen3_0512    # -p : which hardware
#SBATCH --qos=zen3_0512          # -q : which limits
```

If you omit them you get the defaults — `skylake_0096` for both on VSC-4,
`zen3_0512` for both on VSC-5 [S19] — which is fine for a first test and wrong
the moment you want memory, a GPU, or the development queue. Mismatched pairs
are rejected with `InvalidQoS`, `QoSNotAllowed` or `PartitionConfig` in
`squeue`'s reason column [S19].

### The partitions and QoS you can actually use

VSC-4 [S19]:

| partition | nodes | RAM/node | matching QoS | default / hard run time |
|---|---|---|---|---|
| `skylake_0096` (default) | 698 | 96 GB | `skylake_0096`, `skylake_0096_devel` | 24 h / 72 h; devel 10 min, 5 nodes |
| `skylake_0384` | 78 | 384 GB | `skylake_0384` | 24 h / 72 h |
| `skylake_0768` | 12 | 768 GB | `skylake_0768` | 24 h / 72 h |

VSC-5 [S19]:

| partition | nodes | cores/node | RAM/node | matching QoS | notes |
|---|---|---|---|---|---|
| `zen3_0512` (default) | 638 | 128 | 512 GB | `zen3_0512`, `zen3_0512_devel` | devel: 5 nodes, 10 min |
| `zen3_1024` | 136 | 128 | 1 TB | `zen3_1024` | |
| `zen3_2048` | 20 | 128 | 2 TB | `zen3_2048` | |
| `zen2_0256_a40x2` | 45 | 16 | 256 GB | `zen2_0256_a40x2` | 2× A40, best for FP32 |
| `zen3_0512_a100x2` | 61 | 128 | 512 GB | `zen3_0512_a100x2`, `…_devel` | 2× A100, best for FP64 |

Plus `idle_*` QoS (low priority, 24 h) for projects that have used up their
compute time, `*_jupyter` QoS reserved for the JupyterHub, and private-project
QoS `p7XXXX_YYYY` with up to 240 h [S19].

The March-2026 slide also lists `cascadelake_0384` among the VSC-5 QoS [S9];
the current documentation does not list it as a selectable partition and
mentions it only to say it has no idle QoS [S19]. *(unsourced: whether the
Cascadelake nodes are still open to normal projects — the two sources disagree
and nothing public settles it. `sqos` and `sinfo -o %P` on the machine do.)*

Finding out for yourself, on the machine [S9] [S19]:

```bash
sinfo                                   # partitions and node states
sinfo -o %P                             # just the partition names
sqos                                    # ASC-local: your QoS with walltimes and priorities
cat /etc/motd                           # ASC-local: the partition -> QoS mapping
scontrol show partition zen3_0512
scontrol show node n3501-001
sacctmgr show user `id -u` withassoc \
    format=user,defaultaccount,account,qos%40s,defaultqos%20s
```

## Vocabulary

**Job**: a resource request plus a script. **Step**: one `srun` inside a job
(the batch script itself is step `.batch`). **Task**: one process of a step —
one MPI rank. **CPU** in Slurm speak: a core, or a hardware thread, depending on
site configuration. **Account**: the project charged, `p7XXXX` on ASC; omit
`--account` and the default project is used [S9] [S19].

## Three ways to get resources

```bash
sbatch job.sh                              # queue it, read slurm-<jobid>.out later
sbatch -t 10 job.sh arg1                   # command line overrides the #SBATCH lines
interactivejobs -N 1 -p zen3_0512 --qos zen3_0512 --exclusive -t 1:00:00   # ASC wrapper
salloc -N 2 --qos=skylake_0096_devel --partition=skylake_0096              # raw Slurm
```

`interactivejobs` is an ASC wrapper around `salloc` that also logs you into the
allocated node; with plain `salloc` you have to `ssh` to the node yourself and
`scancel` the job when done. Both take `sbatch`'s options. End an interactive
session with `exit` so the nodes go back [S19]. For a five-minute check, use a
`*_devel` QoS: 5 nodes, 10 minutes, priority 5 000 000 against the normal 1 000
[S9] [S19].

## The batch script, ASC style

This is ASC's own quickstart script, reformatted [S9]:

```bash
#!/bin/bash
#SBATCH -J test                     # --job-name
#SBATCH -N 1                        # --nodes            -> SLURM_JOB_NUM_NODES
#SBATCH --qos=zen3_0512             # limits             (VSC-4: skylake_0096)
#SBATCH --partition=zen3_0512       # hardware           (VSC-4: skylake_0096)
#SBATCH --tasks-per-node=128        # ranks per node     (VSC-4 skylake: 48)
###SBATCH --account=p70824          # optional; default project if omitted
#SBATCH --time=01:00:00             # DD-HH[:MM[:SS]]; shorter -> backfilled sooner

module purge                        # recommended in all jobs
# module load <the exact module lines you built with>

echo 'Hello from node: '$HOSTNAME
echo 'Number of nodes: '$SLURM_JOB_NUM_NODES
echo 'Tasks per node:  '$SLURM_TASKS_PER_NODE
echo 'Partition used:  '$SLURM_JOB_PARTITION
echo 'QOS used:        '$SLURM_JOB_QOS
echo 'Using the nodes: '$SLURM_JOB_NODELIST
# <do_my_work>
```

`#SBATCH` lines are comments to bash and options to `sbatch`; they must precede
the first command, and a typo is silently ignored (check with `scontrol show
job`). Output goes to `slurm-<job_id>.out` — both streams — unless you set
`--output` / `--error`. The script runs on the **first** allocated node only;
`srun` or `mpirun` is what spreads work over the rest [S9] [S16].

ASC's own advice on the script itself: it is an ordinary shell script,
independent of the queueing system; keep it simple, **max ~50 lines**, and put
complicated logic elsewhere; load modules from scratch, purge then load [S9].

### Per program type

| program | flags | then in the script | ASC's example |
|---|---|---|---|
| serial / few cores, **shared node** | `-n 1 --mem=2G` (VSC-4) or `--mem=4G` (VSC-5) | `./prog` | `job_single_core_vsc[45].sh` [S9] |
| OpenMP, one node | `-N 1 -n 1 -c 128` | `export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK; ./prog` | — |
| MPI | `-N 2 --tasks-per-node=128` | `mpirun -np 256 ./prog` or `srun ./prog` | `job_mpi_vsc[45].sh` [S9] |
| hybrid | `-N 2 --ntasks-per-node=2 -c 64` | `export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK; srun --cpus-per-task=$SLURM_CPUS_PER_TASK ./prog` | — |
| GPU | `-N 1 -p zen3_0512_a100x2 --qos=zen3_0512_a100x2 --gres=gpu:2` | `./prog` | `salloc … --gres=gpu:2` [S9] |
| many independent runs | `--array=1-20:5%2` | `$SLURM_ARRAY_TASK_ID` | `job_array_vsc[45].sh` [S9] |

`--mem` is per node, `--mem-per-cpu` per core; `--gres=gpu:` takes only 1 or 2
on ASC [S19]. Slurm reserves cores but does **not** set `OMP_NUM_THREADS` — that
is yours. Note that ASC's MPI examples use `mpirun -np <total>` rather than
`srun`; both work, `srun` reads the allocation without `-np`.

## Advanced: the four patterns the afternoon session teaches

All from [S9], cross-checked against [S16] and [S19].

**1. Job arrays** — one script, many independent runs.

```bash
#SBATCH --array=1-10          # SLURM_ARRAY_TASK_ID = 1..10
#SBATCH --array=1-20:5        # ... = 1, 6, 11, 16   (step)
#SBATCH --array=1-20:5%2      # ... and at most 2 running at once (licences)
```

Output files are `slurm-<arrayjobid>_<taskid>.out`; `scancel <arrayjobid>`
kills them all; `SLURM_ARRAY_JOB_ID`, `_TASK_MIN`, `_TASK_MAX`, `_TASK_COUNT`
are set as well [S9] [S19].

**2. Filling one node with many single-core jobs** — because a whole node is
allocated to you anyway:

```bash
#SBATCH -N 1
#SBATCH -p zen3_0512
#SBATCH --qos=zen3_0512
for ((i=1; i<=128; i++)); do
    ./my_prog $i &          # & is essential: background, so the loop continues
done
wait                        # wait is essential: do not exit before they finish
```

and the combination of the two, an array whose tasks each fill a node:
`#SBATCH --array=1-384:128` with the inner loop running IDs `j … j+127` [S9].

**3. What not to do.** The slide's two "bad job practices" are a `for` loop of
`sbatch` calls (slow, and it hammers the scheduler) and a `for` loop of
`mpirun` calls inside one job (serialised, no overlap) [S9]. The documentation
adds: do not submit thousands of short jobs; package thirty 1-minute jobs into
one 30-minute job [S19].

**4. Dependencies and pinning.**

```bash
jid=$(sbatch --parsable stage1.sh)
sbatch --dependency=afterok:"$jid" stage2.sh      # afterany, afternotok, singleton, aftercorr
```

```bash
#SBATCH -N 2
#SBATCH --tasks-per-node=2
srun --cpu-bind=map_cpu:0,64 ./my_mpi_program     # one rank per socket
export I_MPI_PIN_PROCESSOR_LIST=0,64              # the Intel MPI equivalent
mpirun -np 4 ./my_mpi_program
```

Pinning matters when memory demand is high (few ranks per node, one per NUMA
domain) and to stop the OS migrating ranks between sockets [S9]. The lecturer's
own STREAM plot on the intro deck shows the size of the effect, and adds that
*"MPI will give the very same picture"* [S9].

## Time, backfilling and reservations

- `--time=DD-HH[:MM[:SS]]`. Default limit 24 h, **hard limit 72 h** on every
  normal QoS; `*_devel` 10 minutes; private projects up to 240 h [S9] [S19].
- A shorter `--time` is an *estimate* that lets the backfiller squeeze your job
  into a gap ahead of a queued large job. Too short and you get `TIMEOUT` and
  lose the run [S9] [S16].
- Reservations: `#SBATCH --reservation=<name>`, named after the project id,
  arranged through `support@asc.ac.at`. **Core-hours are charged for the entire
  reservation period**, used or not [S9]. During the training courses you are
  told to `alias sbatch="sbatch --reservation=training"` and to `unalias sbatch`
  for the exercise that must go to the development queue [S9].
- `#SBATCH --mail-user=… --mail-type=BEGIN,END` for notifications [S9].

## Watching and checking success

```bash
squeue --me                       # or squeue -u $USER ; ASC suggests alias sq='squeue -u $USER'
squeue -u $USER -o "%A %Z"        # job id and the directory it was submitted from
scontrol show job <id>            # everything, incl. StdOut path and Reason
sacct -j <id> --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS,NNodes,NTasks
lastjobs                          # ASC-local wrapper: last 10 jobs of the last month
scancel <id> | scancel <name> | scancel -u $USER | scancel <arrayid>_<task>
```

**Checking the success of a job** is a stated learning outcome of block 2 [S1],
in two parts — *correct execution* and *runtime*:

1. `sacct` `State` + `ExitCode`. `COMPLETED 0:0` is good. `FAILED 1:0` means
   your program returned 1. `TIMEOUT` means `--time` was too short.
   `OUT_OF_MEMORY` (or `0:9` with `oom-kill` in the output) means `--mem` was.
   `CANCELLED`, `NODE_FAIL` are the environment's fault.
2. The tail of `slurm-<id>.out`: your own success message, and whether the
   physics is right.
3. `Elapsed` against `--time` and `MaxRSS` against `--mem`, to right-size the
   next submission — this is the "runtime" half of the outcome.
4. Whether it was *waiting*, not running: `squeue`'s reason column. ASC
   documents the codes [S19] — `Priority` and `Resources` are normal queueing;
   `QoSGrpCpuLimit`, `QoSMaxNodePerUserLimit` mean your project or you have hit
   a cap; `PartitionTimeLimit` means your `--time` exceeds the QoS hard limit;
   `InvalidQoS` / `QoSNotAllowed` / `PartitionConfig` mean the `--qos` /
   `--partition` pair is wrong. `squeue --start` gives an estimated start time
   that the documentation itself calls *"extremely unreliable"*.
5. Watch a running job: `ssh` to a node in `SLURM_JOB_NODELIST` and run `htop`
   [S19].

## Environment inside a job

`SLURM_JOB_ID`, `SLURM_JOB_NAME`, `SLURM_SUBMIT_DIR`, `SLURM_JOB_NODELIST`
(compressed, expand with `scontrol show hostnames`), `SLURM_JOB_NUM_NODES`,
`SLURM_JOB_PARTITION`, `SLURM_JOB_QOS`, `SLURM_NTASKS`, `SLURM_NTASKS_PER_NODE`,
`SLURM_TASKS_PER_NODE`, `SLURM_NTASKS_PER_CORE`, `SLURM_CPUS_PER_TASK`,
`SLURM_ARRAY_*`, and per task under `srun`: `SLURM_PROCID` (the MPI rank in
practice), `SLURM_LOCALID`, `SLURM_NODEID` [S9] [S16] [S19]. Use them instead of
hard-coding numbers, so that changing a `#SBATCH` line is enough — that is
exactly what ASC's sample script demonstrates by echoing six of them [S9].

## Pitfalls

- Giving `--partition` without `--qos` (or a mismatched pair): `InvalidQoS` /
  `QoSNotAllowed` and the job never starts [S9] [S19].
- `#SBATCH` after the first real command: silently ignored.
- `--tasks-per-node=48` on VSC-5 or `=128` on VSC-4: the wrong core count for
  the hardware. 48 is Skylake, 128 is Zen3 [S9] [S19].
- Running `mpirun` on a login node: the cgroup gives you 4 cores, and ASC kills
  what disturbs others [S19].
- OpenMP without `OMP_NUM_THREADS`: the runtime grabs every core Slurm gave the
  node, including a co-tenant's.
- Background `&` without `wait` in the fill-a-node pattern: the script exits and
  Slurm kills the children [S9].
- A `for` loop of `sbatch`es, or thousands of one-minute jobs [S9] [S19].
- Asking for `--time=72:00:00` when 2 h will do: no backfill, long wait, and the
  same core-hours charged.
- Writing job output into `$HOME`: 100 GB, and a full `$HOME` breaks logins
  ([04](04-cluster-anatomy.md)).
- Array tasks all writing the same file name: use `%A_%a`.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1, Q2 and Q5 restate what the ASC Slurm exercises
actually ask you to do [S9].

1. **Write the four `#SBATCH` lines for one whole VSC-5 CPU node with one MPI
   rank per core, and the launch line.**
   `-N 1`, `--partition=zen3_0512`, `--qos=zen3_0512`, `--tasks-per-node=128`;
   then `mpirun -np 128 ./prog` (or `srun ./prog`). On VSC-4 the same job is
   `skylake_0096` twice and `--tasks-per-node=48` [S9] [S19].
2. **Submit a 30-second test and get the answer in minutes rather than hours.**
   Use the development QoS: `--partition=zen3_0512 --qos=zen3_0512_devel
   --time=00:10:00`. Five nodes, ten minutes, priority 5 000 000 [S9] [S19].
3. **A job sits in `PD` with reason `PartitionTimeLimit`. What did you do?**
   Asked for more walltime than the QoS allows — more than 72 h on a normal QoS,
   or more than 10 minutes on `*_devel` [S19].
4. **You want 4 MPI ranks per node on 3 VSC-5 nodes, 32 OpenMP threads each.
   Lines?** `--nodes=3 --ntasks-per-node=4 --cpus-per-task=32` (= 128 cores per
   node), `export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK`, then
   `srun --cpus-per-task=$SLURM_CPUS_PER_TASK ./prog` [S16].
5. **Run 20 parameter values, in steps of 5, at most 2 at a time.**
   `#SBATCH --array=1-20:5%2`, and read `$SLURM_ARRAY_TASK_ID` in the script.
   That is ASC's own exercise, modified from `--array=1-10` [S9].
6. **`State FAILED, ExitCode 0:9` and `oom-kill` in the output. Diagnosis and
   two fixes.** The kernel killed a process for exceeding the requested memory.
   Either raise `--mem` (or move to `zen3_1024` / `skylake_0384`), or use fewer
   ranks per node so each gets more.
7. **Why does ASC tell you to keep job scripts under about 50 lines?** Because a
   job script is a shell script that is hard to debug through the queue: put the
   logic in a script you can run and test on the login node, and keep the job
   script to resources, modules and one call [S9].
