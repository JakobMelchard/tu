# 04 Cluster anatomy — and the ASC systems in particular

Block 2, first session ("ASC intro & login", 09:05–09:50 [S8]), plus the opening
lecture of block 1 [S1]. No code; the pieces named here reappear as Slurm flags
in [06](06-slurm.md) and as MPI cost models in
[16](16-best-practice-and-debugging.md).

The learning outcome is literally *"describe in word and sketch how a typical
high-performance computing cluster is structured"* [S1] — so the drawing below
matters more than any single number.

> **Every figure on this page comes from a public page or slide, not from the
> machine.** No ASC system was logged into for these notes. Where the lecturer's
> March-2026 slides [S9] [S10] and the live user documentation [S19] disagree,
> the documentation wins and the disagreement is shown. `sinfo -o %P`, `sqos`
> and `mmlsquota` on the machine beat both.

## The sketch you should be able to draw

```
 you (laptop) --ssh + SMS OTP--> [login nodes l50..l56]  ----+
   only from a partner-uni IP     edit, compile (<=4 threads),|  Slurm controller
   or VPN/WireGuard [S19]         submit, transfer            |  decides who runs
                                  24 GB / 4 cores per user    v  where and when
        +-------------------------------------------------------------------+
        | node interconnect: 2-level fat tree (leaf / edge)              [S9]|
        +---+-----------+-----------+-----------+-------------+-------------+
            |           |           |           |             |
        [zen3_0512] [zen3_0512] ... [zen3_1024] [zen3_0512_   [zen3_2048]
         2x64 cores   638 nodes      136 nodes    a100x2]        20 nodes
         512 GB                      1 TB         +2x A100       2 TB
            |           |           |           |             |
        +---+-----------+-----------+-----------+-------------+-------------+
        | IBM Storage Scale (GPFS), shared by VSC-4 and VSC-5:              |
        |   $HOME  /home/fs7XXXX/<user>     100 GB, 10^6 inodes, backed up  |
        |   $DATA  /gpfs/data/fs7XXXX/<user>  10 TB (to 100 TB), tiered     |
        +-------------------------------------------------------------------+
        per compute node only:  /local  NVMe, ~1.8 TB (VSC-5)   /tmp in RAM
                                both wiped when the job ends
```

A cluster is many ordinary servers ("nodes"), each with its own memory and
operating system, glued together by a fast network and a shared filesystem, with
a batch system that hands nodes to jobs. Nothing is "one big computer": a
program only sees one node unless it explicitly sends messages (MPI, block 3).

## The ASC systems, by generation

ASC — **Austrian Scientific Computing** — is the joint HPC facility of TU Wien,
Univ. Wien, BOKU, Univ. Innsbruck, TU Graz, Univ. Graz and JKU, plus ACA, AIT and
INiTS [S4] [S9]. Until 2025 it was called **VSC**, the Vienna Scientific
Cluster, and the machines are still named `vsc4`, `vsc5` [S3] [S19]. The course
number 057.020 was called *VSC-School I* up to and including 2024W [S3].

| system | year | peak / Rmax | TOP500 at launch → 11/2025 | nodes | CPU | memory |
|---|---|---|---|---|---|---|
| VSC-1 | 2009 | 35 TFlop/s | #156 (11/2009) | | | |
| VSC-2 | 2011 | 135 TFlop/s | #56 (06/2011) | | | |
| VSC-3 | 2014 | 596 TFlop/s | #85 (11/2014) | | | |
| **VSC-4** | 2019 | 2.7 PFlop/s | #82 (06/2019) → **#465** | **790** | 2× Intel Xeon Platinum 8174 (Skylake), 24 c/CPU | 96 GB (some 384 / 768) |
| — | 2022 | | | 48 | 2× Intel Cascadelake, 48 c/CPU | 384 GB |
| **VSC-5** | 2022 | 2.3 PFlop/s | #301 (06/2022) → #499 (11/2024), now out | **770** | 2× AMD EPYC 7713 (Milan, Zen3), 64 c/CPU | 512 GB (some 1 / 2 TB) |
| VSC-5 GPU | 2022 | | | 61 + 45 | Zen3 + 2× A100 / Zen2 + 2× A40 | 512 / 256 GB |
| LEONARDO | 2022 | 241.2 PFlop/s | #4 (11/2022) → **#10** | EuroHPC, Italy — ASC is a partner [S9] [S19] | | |
| **MUSICA** | 2024 | 31.84 PFlop/s (11/2025) | #50 (11/2024) → **#60** | Vienna 112 GPU + 72 CPU; Innsbruck and Linz 80 + 48 each | GPU 4× H100 94 GB + NVLink; CPU 2× EPYC 9654, 96 c/CPU, 768 GB | |

Generation list, node counts and CPU/memory from [S9]; the TOP500 columns were
re-read independently on the November 2025 list and agree exactly, including
VSC-4 at **#465, Rmax 2.73 PFlop/s, 37 920 cores** (= 790 × 48, confirming the
node count) and MUSICA Phase 1 at **#60, 31.84 PFlop/s, 161 280 cores** [S22].
VSC-5 has fallen out of the list, consistent with the slide's #499 in 11/2024
[S9] [S22]. The 24.2 PFlop/s the slide gives for MUSICA is its 11/2024 figure;
the machine has grown since.

**Interconnect.** TOP500 names VSC-4's fabric: **Intel Omni-Path** [S22]. The
lecturer's slides draw a **2-level fat tree** (leaf and edge switches, compute
nodes on the lowest level) for VSC-5 and a 3-level one with blocking factors
2:1 and 4:1 for the retired VSC-3 [S9] [S14]. *(unsourced: the actual fabric
technology and speed of VSC-5 — no public ASC page read here names it, and
guessing "InfiniBand HDR" from the vendor would be exactly the kind of stale
spec this pass is meant to remove.)*

## Login vs compute nodes

- **Login nodes** (`l40 … l47` on VSC-4, `l50 … l56` on VSC-5 [S19]; the
  March-2026 slide says `l40 … l49` [S9]): edit, submit, transfer, compile —
  the documentation explicitly allows compiling with **at most 4 threads** and
  enforces **24 GB and 4 cores per user** with cgroups, with all users limited
  to 80 % of the node. Processes that hurt others are killed and you get an
  e-mail [S19]. There are also GUI login nodes (`rackws5`) [S19].
- **Compute nodes** (`n4901-001`-style on VSC-4, `n3501-001` on VSC-5 [S9]):
  reachable only through Slurm (`sbatch`, `salloc`, ASC's `interactivejobs`
  wrapper [S19]). Once a job is yours you may `ssh` onto its nodes to watch with
  `htop` [S19].
- Neither is a "GPU node" unless you asked for one: the GPUs live in two
  dedicated partitions ([06](06-slurm.md)).

## Inside a node

A node here has **2 sockets**, each a CPU with 24 (Skylake), 48 (Cascadelake),
64 (Zen3) or 96 (MUSICA, EPYC 9654) physical cores, two hardware threads each
[S9] [S19]. Each socket has its own memory controller and attached RAM, so
memory access is **non-uniform**: within a socket it is uniform (UMA/SMP), across
sockets in one node it is cache-coherent but slower (**ccNUMA** — the lecturer's
slide marks the Zen3 die as the *smallest possible ccNUMA domain*), and across
nodes there is no shared memory at all [S9]. The consequences the slide draws:
**first touch and pinning matter** inside a node, and only message passing
crosses a node boundary.

The latency/bandwidth ladder the course actually teaches [S9] [S14]:

| | latency | bandwidth |
|---|---|---|
| L1 cache | 1–2 ns | 100 GB/s |
| L2/L3 cache | 3–10 ns | 50 GB/s |
| memory | 100 ns | 10 GB/s |
| HPC network | 1–10 µs | 1–8 GB/s |
| Gigabit Ethernet | 50 µs | 100 MB/s |
| solid-state disk | 500 µs | 100 MB/s |
| local hard disk | 10 ms | 50 MB/s |
| internet | 50 ms | 10 MB/s |

These are the lecturer's order-of-magnitude figures, reproduced as *her* claim,
and the slide's own conclusion is the thing to remember: **"avoiding slow data
paths is the key to most performance optimizations"** [S9]. Measured numbers for
the first three rows, on real hardware, are in the sibling course's note 01
[S23]; this course does not measure them.

Reading the node yourself: `numactl --hardware`, `lscpu`, `cpuinfo -A` (Intel),
`likwid-topology -c -g` [S9] [S14].

## Shared vs distributed memory

| | Shared memory (one node) | Distributed memory (many nodes) |
|---|---|---|
| Address space | one; all threads see all variables | one per process; nothing is shared |
| Communication | read/write the same memory (needs synchronisation) | explicit messages over the network |
| Programming model | OpenMP, pthreads | MPI |
| Limit | the cores and RAM of one node | the whole machine |
| Cost of moving data | cache line, 1–100 ns | message, ~1 µs + size/bandwidth |

A cluster is both, and the slide says so in one line: *"MPI works everywhere"*
[S9]. Consequences, which are a stated learning outcome [S1]: a pure OpenMP
program can never use more than one node; a pure MPI program can use everything
and also works inside one node (messages through shared memory, and by MPI-3
even through a genuinely shared window — [14](14-shared-memory-one-sided.md));
**hybrid** MPI+OpenMP uses one MPI process per socket or NUMA domain with threads
inside ([07](07-mpi-concepts.md)). ASC teaches OpenMP itself as a separate
training event, not as part of 057.020 [S5]; the write-up is in the sibling
course [S23].

## Storage

Four tiers, all from [S19] unless marked:

| tier | path | size / quota | backed up | survives the job |
|---|---|---|---|---|
| `$HOME` | `/home/fs7XXXX/<user>` | **100 GB**, 10⁶ inodes, *cannot* be extended (inode count can) | yes | yes |
| `$DATA` | `/gpfs/data/fs7XXXX/<user>` | **10 TB**, 10⁶ inodes, extendable to 100 TB | yes | yes |
| `/local` | node-local NVMe | ~450 GB (VSC-4), ~1.8 TB (VSC-5) | no | **no** |
| `/tmp`, `/dev/shm` | node-local, in RAM | up to half the node's memory | no | **no** |

`$HOME` and `$DATA` are one IBM Storage Scale (GPFS) filesystem shared by VSC-4
and VSC-5, so a project sees the same data on both. `$DATA` is tiered: ~500 TB
of flash in front of ~5 PB of spinning disk, with all metadata and the hottest
~10 % of data on NVMe and a Spectrum Scale policy migrating the rest back and
forth [S19] [S10]. Files on `$DATA` are normally group-readable so project
members can share. Backup exists for disaster recovery only, on a best-effort
basis, and the project manager can exclude `$DATA` [S10].

What goes where [S19]: **`$HOME`** — settings, caches, code, scripts, conda
environments, and *no research data at all*; **`$DATA`** — every input, every
intermediate, every result; **`/local` and `/tmp`** — heavy I/O *during* a job,
then copy out or lose it. Check quotas with
`mmlsquota --block-size auto -j home_fs7XXXX home` (and `-j data_fs7XXXX data`);
plain `quota` does not work on Spectrum Scale.

> **A stale-figure warning that is itself a finding.** The March-2026
> `file_storage` deck states `$DATA` = 100 GB "can be extended on request" and
> `/local` = 480 GB / 2 TB [S10]. The current documentation says 10 TB and
> ~450 GB / ~1.8 TB [S19]. The table above follows the documentation. A slide
> deck is a snapshot; run `mmlsquota` before you plan a campaign.

## GPUs

Two partitions on VSC-5 only [S9] [S19]:

| partition | nodes | GPU | cores/CPU | RAM | GPU memory | GPU bandwidth | FP32 / FP64 |
|---|---|---|---|---|---|---|---|
| `zen2_0256_a40x2` | 45 | 2× NVIDIA A40 | 8 (EPYC 7252) | 256 GB | 48 GB | 696 GB/s | 37 000 / 578 GFlop/s |
| `zen3_0512_a100x2` | 61 | 2× NVIDIA A100 | 64 (EPYC 7713) | 512 GB | 40 GB | 1600 GB/s | 20 000 / 10 000 GFlop/s |

Node counts from [S19]; the GPU columns from the lecturer's GPU deck [S9],
which also lists 19 private `gpu_rtx2080ti` nodes usable only when idle. The
two decks round differently ("40 GPU nodes"/"60 GPU nodes" on the intro deck vs
45/61 in the GPU deck and the documentation) — use the documentation.

The ratio in the last column is the whole point: the **A40 is ~64× faster in
single than in double precision**, the A100 only 2×. ASC says so in the
partition description: A40 "best for single precision GPU code", A100 "best for
double precision GPU code" [S19]. Pick by the precision your code needs, not by
the newer name.

You request them with `--gres=gpu:1` or `:2` (those are the only allowed values
[S19]) on the matching partition **and** QoS; `nvcc -arch=native`, `nvidia-smi`,
and `spack load cuda@...` rather than a module on the `cuda-zen` environment
[S9]. A job that reserves a GPU and does not use it wastes the most expensive
resource in the building.

## The batch system and fair share

Users submit **jobs** (a script plus a resource request). The scheduler starts
them in priority order; priority weighs queue age, fair share (recent use by
your project against its allocation), job size and QoS [S16]. **Backfill** lets
a short job jump into a gap before a large reserved job starts — the lecturer's
slide puts it plainly: the `--time` you give *"is an estimate of your required
computing time; if this is shorter than the default runtime limit (mostly 24 h),
SLURM may squeeze it in on idle nodes waiting for a larger job"* [S9]. Core-hours
are charged against the project for the whole allocation, used or not, and for
the entire period of a reservation [S9].

Details, flags and the ASC-specific partition/QoS pairing: [06](06-slurm.md).

## Pitfalls

- Running the "quick test" on the login node: cgroups cap you at 4 cores and
  24 GB and ASC kills what remains disruptive [S19]; everybody else's editor
  stalls in the meantime.
- Assuming memory is shared across nodes: a 2-node job with 512 GB per node does
  not give one process 1 TB.
- Putting research data in `$HOME`: 100 GB, strict, not extendable, and a full
  `$HOME` breaks your logins [S19].
- Leaving results on `/local` or `/tmp`: gone the moment the job ends [S19].
- Choosing the A100 partition for a single-precision code: the A40 partition is
  nearly twice as fast for FP32 and much less contended [S9] [S19].
- Compiling with `-march=znver3` on a login node and running on `zen2_0256_a40x2`:
  the A40 nodes are the **only** Zen2 CPUs on VSC-5, so the binary faults [S10].
- Quoting a 2019 node count in 2026. Every figure here has a retrieval date; the
  machines get retired (VSC-1, -2, -3 are gone) and the queues get renamed.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)).

1. **Sketch a cluster and label where you compile, where your job runs, where
   results should be written, and how the pieces are connected.** Login nodes
   (edit, compile ≤4 threads, submit), Slurm, compute nodes on the fat-tree
   interconnect (run), GPFS shared by all nodes: `$DATA` for results, `$HOME`
   for code, `/local` for scratch during the job. This is the stated learning
   outcome [S1]; the diagram at the top is the answer.
2. **A colleague's OpenMP code "scales to 64 cores". Can it use 4 nodes?**
   No. OpenMP threads share one address space, which exists only within one
   node's operating system. Four nodes need MPI (or hybrid) [S1] [S9].
3. **You have a single-precision GPU kernel. Which VSC-5 partition, and why?**
   `zen2_0256_a40x2`. 37 TFlop/s FP32 on an A40 against 20 on an A100, and ASC
   labels the partitions exactly that way [S9] [S19]. Watch out: those nodes are
   Zen2 with only 8 cores per CPU, so the host side is weak.
4. **Where do 2 TB of trajectory frames written during a job go, and where do
   the 20 GB you keep go?** During the job: `/local` (~1.8 TB on VSC-5) or
   `/tmp` if it fits in half the node's RAM. Afterwards: `$DATA` — and only
   `$DATA`, `$HOME` is 100 GB and is not for research data [S19].
5. **Why does an accurate, short `--time` get you started sooner?** Backfill:
   Slurm can slot a job into a gap ahead of a large reserved job if it provably
   finishes before the gap closes [S9] [S16].
6. **Name one number on this page you should not trust, and how to check it.**
   Any of them — but concretely `$DATA` = 10 TB, because a March-2026 ASC slide
   still says 100 GB [S10]. Check with `mmlsquota --block-size auto -j
   data_fs7XXXX data` on the machine [S19].
