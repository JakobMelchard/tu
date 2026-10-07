# Slurm on the ASC systems — cheatsheet

Site specifics come from the ASC user documentation [S19] and the lecturer's
March-2026 decks [S9]; everything else is standard Slurm [S16]. Full write-up in
[`../../../notes/06-slurm.md`](../../../notes/06-slurm.md); job templates next to
this file.

## The ASC rule the Slurm manual does not have

> **Always give both `--qos` and `--partition`, and make them match.** [S9]

They are usually spelled the same. Omit them and you get the defaults —
`skylake_0096` for both on VSC-4, `zen3_0512` for both on VSC-5 [S19] — which is
fine for a first test and wrong the moment you want memory, a GPU or the devel
queue. A wrong pair shows up in `squeue` as `InvalidQoS`, `QoSNotAllowed` or
`PartitionConfig` [S19].

### Partitions and QoS [S19]

| cluster | partition | nodes | cores/node | RAM | matching QoS |
|---|---|---|---|---|---|
| VSC-4 | `skylake_0096` *(default)* | 698 | 48 | 96 GB | `skylake_0096`, `skylake_0096_devel` |
| VSC-4 | `skylake_0384` | 78 | 48 | 384 GB | `skylake_0384` |
| VSC-4 | `skylake_0768` | 12 | 48 | 768 GB | `skylake_0768` |
| VSC-5 | `zen3_0512` *(default)* | 638 | 128 | 512 GB | `zen3_0512`, `zen3_0512_devel` |
| VSC-5 | `zen3_1024` | 136 | 128 | 1 TB | `zen3_1024` |
| VSC-5 | `zen3_2048` | 20 | 128 | 2 TB | `zen3_2048` |
| VSC-5 | `zen2_0256_a40x2` | 45 | 16 | 256 GB | `zen2_0256_a40x2` |
| VSC-5 | `zen3_0512_a100x2` | 61 | 128 | 512 GB | `zen3_0512_a100x2`, `…_devel` |

Default run time **24 h**, hard limit **72 h** on every normal QoS; `*_devel`
10 minutes and 5 nodes (2 on the A100 partition); `idle_*` for projects out of
compute time; private-project QoS up to 240 h [S19].

### ASC-local commands you will not find in `man slurm` [S9] [S19]

```bash
sqos                      # your QoS with walltimes and priorities
cat /etc/motd             # the partition -> QoS mapping
lastjobs                  # wrapper around sacct: the last 10 jobs of the last month
interactivejobs -N 1 -p zen3_0512 --qos zen3_0512 --exclusive -t 1:00:00
sacctmgr show user `id -u` withassoc format=user,defaultaccount,account,qos%40s,defaultqos%20s
alias sq='squeue -u $USER'
```

## Submit and run

| Command | What |
|---|---|
| `sbatch job.sbatch` | queue a batch script, returns the job id |
| `sbatch --time=2:00:00 --ntasks=8 job.sbatch` | command-line flags override `#SBATCH` lines |
| `sbatch --dependency=afterok:12345 next.sbatch` | start only after 12345 finished successfully (`afterany`, `afternotok`, `singleton`) |
| `sbatch --array=0-99%10 sweep.sbatch` | 100 tasks, at most 10 at once |
| `interactivejobs -N1 -p zen3_0512 --qos zen3_0512 -t 1:00:00` | **ASC wrapper**: allocate and log you in [S19] |
| `salloc -N1 -n4 -t 1:00:00` | raw Slurm: reserve, then `ssh` to the node yourself and `scancel` when done |
| `srun -N1 -n1 -t 30 --pty bash` | interactive shell on a compute node (never compute on the login node) |
| `srun ./prog` (inside a job) | launch `$SLURM_NTASKS` copies, binds them to cores |

## Watch and manage

| Command | What |
|---|---|
| `squeue --me` | my jobs: `PD` pending, `R` running, `CG` completing |
| `squeue -j 12345 --start` | estimated start time |
| `scontrol show job 12345` | every detail of a queued/running job (reason it waits, nodes, script path) |
| `sacct -j 12345 --format=JobID,State,Elapsed,MaxRSS,ExitCode` | accounting after the fact: did it finish, how long, how much memory |
| `sacct -X -S today` | my jobs since midnight, one line each |
| `seff 12345` | CPU and memory efficiency summary (if installed) |
| `scancel 12345` / `scancel --me` / `scancel -n name` | kill |
| `sinfo -s` | partitions and node states (`idle`, `alloc`, `mix`, `drain`) |
| `sinfo -p skylake_0096 -o "%n %c %m %G"` | nodes, cores, memory, GPUs of a partition |
| `sinfo -o %P` | just the partition names [S19] |
| `sqos` | **ASC**: the QoS available to you, with limits [S9] |
| `lastjobs -h` | **ASC**: recent jobs [S19] |
| `ssh <node from SLURM_JOB_NODELIST>` then `htop` | watch a running job [S19] |
| `sprio -j 12345` | why is my priority what it is (age, fair-share, size) |
| `sshare -u $USER` | my fair-share usage |

## Resource flags

| Flag | Meaning |
|---|---|
| `-N, --nodes=2` | number of nodes |
| `-n, --ntasks=96` | number of MPI processes in total |
| `--ntasks-per-node=48` | processes per node (with `-N` fixes `-n`) |
| `-c, --cpus-per-task=4` | cores per process (OpenMP threads); export `OMP_NUM_THREADS` yourself |
| `--mem=8G` / `--mem-per-cpu=2G` / `--mem=0` | memory per node / per core / all of the node |
| `-t, --time=1-12:00:00` | walltime `d-hh:mm:ss`; too short = killed, too long = waits longer |
| `-p, --partition=…` `--qos=…` | which pool of nodes and which rules |
| `--gres=gpu:2` / `--gpus-per-node=2` | GPUs |
| `--exclusive` | whole node even if you use fewer cores |
| `-J, --job-name=…` `-o, --output=%x-%j.out` `-e` | naming; `%j` id, `%x` name, `%A_%a` array |
| `--mail-type=END,FAIL --mail-user=…` | notification |

## Environment inside a job

`SLURM_JOB_ID`, `SLURM_JOB_NAME`, `SLURM_SUBMIT_DIR`, `SLURM_JOB_NODELIST`, `SLURM_JOB_NUM_NODES`, `SLURM_NTASKS`, `SLURM_NTASKS_PER_NODE`, `SLURM_CPUS_PER_TASK`, `SLURM_PROCID` (rank of this task under srun), `SLURM_ARRAY_JOB_ID`, `SLURM_ARRAY_TASK_ID`, `SLURM_MEM_PER_NODE`.

## Reading the result

1. exit status: `sacct -j ID --format=JobID,State,ExitCode` (`COMPLETED 0:0`; `FAILED 1:0` your program; `TIMEOUT`, `OUT_OF_MEMORY`, `CANCELLED`)
2. `MaxRSS` vs `--mem`: request ~1.3x of what was used next time
3. `Elapsed` vs `--time`; `seff` for CPU efficiency (<50% with MPI = load imbalance or too much communication)
4. the `.out` file: your prints, plus Slurm messages at the end (`slurmstepd: error: ... oom-kill`, `DUE TO TIME LIMIT`)

## Common mistakes

- `#SBATCH` after the first command: silently ignored.
- Running `mpirun`/`python` on the login node "just to test" with a full-size problem.
- Forgetting `OMP_NUM_THREADS`: OpenMP takes all cores of the node, not your `-c`.
- `--ntasks=48` for an OpenMP program: 48 copies of the same serial-with-threads program.
- `--mem` too small: `oom-kill`; `--time` too small: `TIMEOUT`; both mean rerun from scratch unless you checkpoint.
- Giving `--partition` without `--qos`, or a mismatched pair: the job never starts [S9] [S19].
- `--tasks-per-node=48` on VSC-5 or `=128` on VSC-4: 48 is Skylake, 128 is Zen3 [S19].
- Writing thousands of small files, or any research data, into `$HOME`: 100 GB, strict, and a full `$HOME` breaks logins. Use `$DATA`, and `/local` or `/tmp` during the job [S19].
- A `for` loop of `sbatch` calls, or thousands of one-minute jobs — package them [S9] [S19].
- `&` without `wait` when filling a node with background tasks: the script exits and Slurm kills the children [S9].
- `--time=72:00:00` when 2 h will do: no backfill, long wait, same core-hours charged [S9].
- Loading different modules than the ones the binary was built with (`module list` in the job output helps).
- `$SLURM_SUBMIT_DIR` not `cd`'d into: relative paths break, `sbatch` starts the script in the submit dir but only by default.

## Job reason codes worth recognising [S19]

`Priority`, `Resources` — normal queueing. `PartitionTimeLimit` — your `--time`
exceeds the QoS limit. `InvalidQoS`, `QoSNotAllowed`, `PartitionConfig` — the
`--qos`/`--partition` pair is wrong. `QoSGrpCpuLimit`, `QoSGrpNodeLimit`,
`QoSMaxNodePerUserLimit` — you or your project have hit a cap.
`JpbArrayTaskLimit` *(sic, ASC's spelling)* — the array's `%n` throttle.
`Dependency` — waiting for another job. `None` — so many jobs are waiting that
yours has not been given a priority yet.

`squeue --start` gives an estimated start time that the documentation itself
calls *"extremely unreliable"* [S19].

Source entries `S9`, `S16` and `S19` are in
[`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
