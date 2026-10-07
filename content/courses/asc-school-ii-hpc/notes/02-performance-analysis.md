# 02 Performance analysis and profiling on a cluster

Prepares for *Debugging and Optimizing Parallel Codes with Linaro Forge*
(1 day), *Extrae and Paraver* (1 day), the *POP/VI-HPS Tuning Workshop*
(3 days) and the profiling parts of *Python for HPC* [S4] [S7]. Serial
measurement method (timers, variance, `perf` on one core) is in Efficient
Programs note 02 [S11]; this note is about **parallel** programs on a
**batch system**.

## Definitions

- **Profile**: aggregated statistics per function / call path / rank
  (how much time, how many calls). **Trace**: time-stamped event record per
  rank and thread (enter/leave, send/receive), viewed as a timeline.
- **Sampling**: interrupt every $\Delta t$ or every $k$ events, record the
  program counter and call stack. Overhead set by the rate, independent of
  call frequency. **Instrumentation**: code inserted at function entry/exit and
  around MPI/OpenMP calls; exact counts, overhead proportional to the number of
  calls.
- **Inclusive / exclusive time**: with / without the time spent in callees.
- **Hardware performance counters**: registers in the CPU's performance
  monitoring unit that count events (cycles, instructions, cache misses,
  floating-point operations, memory traffic). Read with `perf`, PAPI or
  LIKWID [S19]. Few counters exist per core, so many events need several runs
  or multiplexing (which extrapolates).
- **Derived metrics**: IPC = instructions/cycles; GFlop/s; memory bandwidth
  = (bytes read + written)/time; arithmetic intensity = flops/byte (note 03).

## The POP efficiency model

The POP Centre of Excellence reduces a parallel run to a few multiplicative
factors [S19]. With useful (non-MPI) compute time $u_r$ on rank $r$ and total
runtime $T$:

$$
\text{LB} = \frac{\overline{u}}{\max_r u_r},\qquad
\text{CommE} = \frac{\max_r u_r}{T},\qquad
\text{PE} = \text{LB}\cdot\text{CommE} = \frac{\overline{u}}{T}.
$$

Load balance (LB) says how much time ranks wait for the slowest; communication
efficiency (CommE) says how much of the critical path is MPI. Across a scaling
series, **computation scaling** $\sum_r u_r(P_0)/\sum_r u_r(P)$ exposes code
that does more total work at more ranks (replicated setup, larger halos).

Worked numbers: 4 ranks with $u = (9, 10, 10, 12)$ s and $T = 14$ s:
$\overline u = 10.25$, LB $= 10.25/12 = 0.854$, CommE $= 12/14 = 0.857$,
PE $= 0.732$. Balancing the fourth rank gains more than faster MPI.

## The tools and what they answer

| question | tool | mode |
|---|---|---|
| where does time go, per function, one node | `perf record` / `perf report` [S19] | sampling |
| is the core busy or waiting (IPC, misses) | `perf stat -e cycles,instructions,cache-misses` [S19] | counting |
| memory bandwidth, flops, per core group | `likwid-perfctr -C 0-21 -g MEM_DP ./prog` [S19] | counting, needs MSR/perf access |
| counters from inside the code | PAPI `PAPI_start`/`PAPI_stop`, `papi_avail` [S19] | counting |
| MPI vs compute vs I/O share, whole job | Linaro `perf-report srun ...` [S12] | sampling, summary `.txt`/`.html` |
| which line is hot, per rank | Linaro MAP: `map --profile srun ...`, open the `.map` file in the GUI [S12] | sampling |
| call-path profile with MPI wait states | Score-P + Cube, Scalasca [S19] | instrumentation |
| timeline of messages and waits | Score-P traces (OTF2) in Vampir; Extrae + Paraver [S19] | tracing |

ASC documents only the Linaro (formerly Arm/Allinea) Forge tools, with licences
for up to 512 parallel tasks [S12]. Whether `perf`, LIKWID or Score-P are
installed on MUSICA was not checked (no login): `module avail` on the machine.

## Worked example: a profiling session in a job

```bash
# 1. build with symbols, KEEP the optimisation you will run with
mpicc -g -O2 -fno-omit-frame-pointer prog.c -o prog

# 2. one-page summary (ASC recipe, module name from `module avail`) [S12]
perf-report srun --jobid $SLURM_JOB_ID -n 32 ./prog     # -> prog_32p_*.txt/.html

# 3. line-level profile, analysed later on the login node [S12]
map --profile srun --jobid $SLURM_JOB_ID -n 32 ./prog   # -> prog_32p_2n_<date>.map
map ./prog_32p_2n_<date>.map                            # GUI, needs ssh -X

# 4. Score-P call-path profile, then Scalasca wait-state analysis [S19]
scorep mpicc -O2 prog.c -o prog                         # instrumenting wrapper
export SCOREP_EXPERIMENT_DIRECTORY=scorep_32 SCOREP_ENABLE_TRACING=false
srun -n 32 ./prog && cube_stat -t 10 scorep_32/profile.cubex
scalasca -analyze srun -n 32 ./prog && scalasca -examine scorep_prog_32_sum

# 5. node level, one rank, Linux perf
srun -n 1 perf stat -e cycles,instructions,cache-misses ./simd_dot --quick
```

On the laptop [S10] none of steps 2-5 exists (`perf` and LIKWID are Linux
tools, Forge and Score-P are cluster modules). What does run is the timer
discipline the tools rest on: `simd_dot` takes the best of 5 samples, each
$\ge 20$ ms, and prints ns/element; `hybrid_pi` reports the **maximum** over
ranks, because the slowest rank is the runtime.

## Reading the output

- `perf-report`: if "MPI" is above ~20-30 % (our threshold), look at load
  balance before tuning messages: waiting inside `MPI_Allreduce` usually means
  imbalance upstream, not a slow network.
- Scalasca "late sender" time at a receive = the sender arrived late; the
  cause is the computation before the send, on the other rank.
- IPC well below the core's issue width with high cache-miss counts:
  memory-bound, go to note 03 (blocking, roofline). High IPC but low GFlop/s:
  scalar code, check vectorisation.

## Pitfalls

- Profiling a `-O0` build: the profile describes a different program.
- Instrumenting tiny, hot functions: overhead dominates; Score-P needs a
  filter file (`SCOREP_FILTERING_FILE`) excluding them [S19].
- Traces of many ranks x long runs reach tens of GB: trace a few iterations.
- Too few samples: a 2 s run at 1 kHz gives 2000 samples per rank; a
  function at 1 % has about 20, i.e. $\pm 22$ % relative error ($1/\sqrt{20}$).
- Counters need kernel permission (`perf_event_paranoid`); on shared clusters
  they may be restricted or reserved for the site's own monitoring
  (unsourced for ASC: ask support).
- Comparing runs with different pinning, node types, or turbo states.

## Questions (ours)

1. *Sampling or instrumentation for a code with $10^8$ calls of a 20 ns
   function?* Sampling: instrumentation adds ~tens of ns per call, i.e. more
   than the function itself.
2. *LB = 0.95, CommE = 0.60 at 256 ranks. Where to look?* Communication on the
   critical path: message count and size, collectives, missing overlap,
   synchronising barriers. Load balance is fine.
3. *Total useful time grows from 1000 core-s at 32 ranks to 1400 at 256. What
   is that?* Computation scaling 0.71: extra work at scale (halo
   recomputation, replicated serial parts, worse cache behaviour).
4. *`MPI_Wait` is 40 % of the profile on rank 0 only. Cause?* Rank 0 waits for
   others that compute longer (imbalance), or rank 0 is the root of gather-like
   patterns; check per-rank useful time before touching MPI.
5. *Why build the profiled binary with `-g -O2` rather than `-g`?* Without an
   `-O` flag GCC and clang default to `-O0`; `-g` only adds symbols and leaves
   the optimised code unchanged, so `-g -O2` profiles what you run.

## Code

- [`../src/c/simd_dot.c`](../src/c/simd_dot.c): `time_fn` (best-of-5,
  adaptive repetitions) as a model timer; a good first target for `perf stat`
  on a Linux node.
- [`../src/c/hybrid_pi.c`](../src/c/hybrid_pi.c): compute vs
  compute+allreduce time, max over ranks.
