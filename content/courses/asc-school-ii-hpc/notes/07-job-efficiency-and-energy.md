# 07 Job efficiency, accounting, scaling studies, energy

No catalogue event is devoted to this [S4]; it is the part of *Slurm
(advanced)* in the ASC intro that every ASC-School II hand-in needs: a program
example is only convincing with a scaling table and evidence that the job used
what it asked for. Slurm basics, partitions and QoS are in ASC-School I note 06
[S11]; Amdahl's law with the sequential-fraction convention in its note 16.

## Definitions

- **Charged resources**: allocated cores (whole nodes for exclusive jobs) x
  elapsed wall time, in core-hours. On ASC a job ending before its limit is
  charged only for the time used; project totals are on the project service
  page under "view statistics" [S12].
- **CPU efficiency** $\eta_\text{cpu} = \text{TotalCPU} / (\text{AllocCPUS}
  \times \text{Elapsed})$: fraction of the allocated core-time spent computing.
- **Memory efficiency**: MaxRSS / requested memory (per task or node).
- **Strong scaling** (fixed total problem): $S(p) = T(1)/T(p)$,
  $E(p) = S(p)/p$. **Weak scaling** (work $\propto p$): $E_w(p) = T(1)/T(p)$.
- **Karp-Flatt metric**, the experimentally determined serial fraction:
  $$e(p) = \frac{1/S(p) - 1/p}{1 - 1/p}.$$
  Constant $e$ means an Amdahl-type serial part; $e$ growing with $p$ means
  overhead that grows with $p$ (communication, imbalance).
- **Energy to solution** $E_\text{sol} = \int P(t)\,dt$ over the job.
  Slurm reports `ConsumedEnergy` (joules) if the site configured an energy
  plugin, and it is meaningful **only for exclusive allocations** [S9].

## Why efficiency is energy

With node power roughly constant while a job runs (static power dominates),
$E_\text{sol} \approx p\,P_\text{core}\,T(p) = P_\text{core}\,T(1)/E(p)$. The
energy relative to one core is $1/E(p)$: running at 50 % parallel efficiency
doubles the energy bill for the same answer. The fastest configuration and the
cheapest are different points; a scaling study shows both.

## Worked example 1: what did my job use?

```bash
sacct -j 1234567 --format=JobID,JobName,Partition,AllocCPUS,Elapsed,TotalCPU,MaxRSS,State,ExitCode
sacct -j 1234567 -o JobID,Elapsed,ConsumedEnergy      # empty if no energy plugin
sacct -u $USER -S 2028-03-01 -o JobID,JobName,Elapsed,AllocCPUS,State   # a month
lastjobs                                              # ASC wrapper: last 10 jobs [S12]
seff 1234567                                          # Slurm contrib script, if installed
ssh <node>; htop                                      # live, during the job [S12]
```

`MaxRSS` is reported per step and task (the largest task), so look at the
`.0` step line for `srun` jobs. Formats, the `-l` long form and `-b` brief form
are listed in ASC's accounting page [S12] and `sacct(1)` [S9].

Reading a hypothetical result: `AllocCPUS=190 Elapsed=01:00:00
TotalCPU=47:30:00`. $\eta_\text{cpu} = 47.5/190 = 0.25$: three quarters of
the node idled. Typical causes: `OMP_NUM_THREADS` unset in a serial program on
an exclusive node, a hybrid job with threads pinned to one core (note 01), or
a code waiting on I/O.

## Worked example 2: a strong-scaling table

`hybrid_pi`, $N = 4 \cdot 10^8$, laptop [S10], best combination of $P \times
T$ for each worker count $p = PT$ (medians of 3, the sweep of note 01):

| $p$ | $T(p)$ [s] | $S(p)$ | $E(p)$ | $e(p)$ |
|---|---|---|---|---|
| 1 | 0.351 | 1.00 | 1.00 | - |
| 2 | 0.158 | 2.22 | 1.11 | $-0.10$ |
| 4 | 0.083 | 4.22 | 1.06 | $-0.018$ |
| 8 | 0.048 | 7.28 | 0.91 | 0.014 |
| 12 | 0.050 | 7.02 | 0.58 | 0.065 |

Three lessons, none about the code:

1. $E > 1$ at $p = 2, 4$ appeared in both measurement sessions. The kernel
   cannot be superlinear (no cache effect: it touches no arrays), so the
   baseline is suspect: an unpinned single worker that the OS may move between
   core types (a guess; macOS allows no pinning to test it). A scaling table is
   only as good as its $p = 1$ run.
2. The kernel has no communication, yet $e$ grows with $p$: past 6 workers
   the efficiency cores join, the workers are no longer identical and the
   static split leaves fast cores waiting; at 12 background load adds noise
   (note 01). On a cluster the same symptom means imbalance, mixed node types
   or shared nodes.
3. On a real node, pin (note 01), use exclusive nodes, and report the median
   of $\ge 3$ runs with the spread.

For a **weak-scaling** study scale $N \propto p$ (`-n` flag) and plot $T(p)$,
which should stay flat.

## Worked example 3: many small cases as an array job

[`../src/sh/slurm_templates/array.sbatch`](../src/sh/slurm_templates/array.sbatch):
100 cases from `params.txt`, at most 10 running (`--array=0-99%10`), each a
4-core, 8 GB slice of a shared MUSICA node rather than an exclusive one [S9]
[S13]. Charging then follows the slice, not 190 cores per case. The throttle
`%10` is Slurm's [S9]; the "minutes, not seconds per task" rule is ours.

## Choosing the request

- **Walltime**: realistic plus margin, not the 72 h maximum [S13]. Shorter
  jobs fit into backfill gaps and start sooner [S12].
- **Nodes**: the count where $E(p)$ drops below your threshold (0.7 is a
  common choice; ours, not ASC's). Beyond it every extra node costs more
  energy and core-hours than it saves in time.
- **Memory**: from MaxRSS of a test run plus margin; on shared nodes it is what
  you are charged for and what blocks others.
- **Test first** on the devel QoS: 2 nodes, 10 minutes on MUSICA [S13].

## Pitfalls

- Scaling measured on shared (non-exclusive) nodes or unpinned: noise larger
  than the effect.
- The 1-core baseline run with a different code path (no MPI), making $S(p)$
  look better or worse; use the parallel code with $p = 1$.
- Strong scaling far past the point where each rank has little work: the table
  becomes a latency measurement.
- Reading `ConsumedEnergy` on a shared node: it includes the neighbours [S9].
- `sacct` right after the job: accounting fields fill with a delay (common
  experience; unsourced).

## Questions (ours)

1. *$T(1) = 1000$ s, $T(64) = 25$ s. Speed-up, efficiency, Karp-Flatt?*
   $S = 40$, $E = 0.625$, $e = (1/40 - 1/64)/(1 - 1/64) = 0.0095$.
2. *Same code, $T(128) = 15$ s. Is the extra node worth it?* $S = 66.7$,
   $E = 0.52$; time drops by 40 % but core-hours rise from 0.44 to 0.53
   ($p\,T/3600$), and energy by the same ratio.
3. *Weak scaling: $T(1) = 100$ s on one node, $T(64) = 125$ s on 64 nodes with
   64x the work. Efficiency?* $E_w = 100/125 = 0.8$; the 25 s are overhead that
   grows with $p$ (communication, I/O), not serial work.
4. *Why is `ConsumedEnergy` only meaningful for exclusive jobs?* The counters
   measure the node (or socket); on a shared node other jobs' consumption is
   included [S9].
5. *A 100-case sweep of 20 s per case: array job of 100 tasks or one job?*
   One job (or 10 tasks of 10 cases): 20 s tasks spend a comparable time in
   scheduling and start-up; bundle to minutes per task.

## Code

- [`../src/sh/slurm_templates/array.sbatch`](../src/sh/slurm_templates/array.sbatch),
  [`hybrid.sbatch`](../src/sh/slurm_templates/hybrid.sbatch),
  checked by [`../src/sh/test_slurm_templates.sh`](../src/sh/test_slurm_templates.sh).
- [`../src/c/hybrid_pi.c`](../src/c/hybrid_pi.c) `-n N` for strong and weak
  scaling runs; prints the max-over-ranks time.
