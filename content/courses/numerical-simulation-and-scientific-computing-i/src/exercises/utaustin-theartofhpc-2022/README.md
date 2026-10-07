# UT Austin / TACC - Eijkhout, *The Art of HPC* vol. 1 (2022), exercises

> **This is not 360.242 material.** 360.242 publishes no exercise sheet and no
> past paper [S1] [S4]. The exercises below belong to **another author's book**,
> are restated in our words, and the code is ours.

| | |
|---|---|
| Institution | The University of Texas at Austin / Texas Advanced Computing Center |
| Work | *The Art of High Performance Computing*, **volume 1: Introduction to High-Performance Scientific Computing** |
| Author | Victor Eijkhout |
| Edition used | the 2022 source repository (book © 2012–2022) |
| Source | [S43] <https://theartofhpc.com/>, <https://github.com/VictorEijkhout/TheArtOfHPC_vol1_scientificcomputing> |
| Licence | **CC BY 4.0** (`booksources/copyright.tex`; the repository's `LICENSE` is MIT and covers the sources/code) |
| Retrieved | 2026-09-22 |
| Vendored here | **nothing** - exercises are restated, not copied |

## Why it is comparable to this syllabus

Not because it is called HPC - because the *first* chapter of the book is the
*first* two topics of this course, in the same order and at the same level.
Eijkhout's chapter 1, "Single-processor Computing", is caches, cache lines,
associativity, TLB, prefetch, memory banks, multicore, false sharing, NUMA,
locality, arithmetic intensity and the **roofline model**: that is 360.242's
"Computer Architectures" and "Serial Optimization" [S1]. Chapter 4, "Numerical
treatment of differential equations", is the 1D/2D Poisson and heat-equation
material of topic 4. Chapter 5, "Numerical linear algebra", is sparse storage,
stationary iterations and CG - topic 5. Chapter 2 is parallelism, of which the
shared-memory half is topic 7.

It also has what almost nothing else free has: **exercises with a checkable
answer** rather than programming projects. That is the format a written exam
uses, and it is why this is the source the practice note leans on hardest.

## What it covers that 360.242's TISS topic list also covers

| TISS topic [S1] | chapter / section in [S43] |
|---|---|
| 1 Computer Architectures | ch. "Single-processor Computing" - Memory Hierarchies, Caches, Multicore architectures, Locality and data reuse, The roofline model |
| 2 Serial Optimization | same chapter's locality sections, and ch. "Programming for performance" |
| 4 Finite Difference Discretization | ch. "Numerical treatment of differential equations" - IVPs, BVPs, 1D/2D Poisson, heat equation, stability |
| 5 Numerical Linear Algebra | ch. "Numerical linear algebra" - sparse storage, stationary iteration, CG |
| 7 Shared Memory Parallel Computing | ch. "Parallel Computing" - shared memory, threads, Amdahl, efficiency |
| 8 Algorithmic Complexity and Data Structures | ch. "Numerical linear algebra" - sparse matrix storage; appendix on complexity |

## What it covers that 360.242 does not, and the reverse

**In [S43] but outside this syllabus.** Distributed memory and MPI, network
topologies and bisection bandwidth, GPUs, the Top500 and power, cloud and
MapReduce, computer arithmetic in IEEE detail, molecular dynamics, graph
analytics, N-body, machine learning. Roughly half the book is about clusters;
360.242's topic 7 is *shared memory* only [S1].

**In this syllabus but absent from [S43].** Two topics outright:

- **Topic 9, Mesh Generation and Visualisation.** Grepping the whole book for
  "mesh generation", "unstructured grid" and "visualization" returns **nothing**.
  The book discusses graph partitioning, not mesh generation, and no file
  format at all. This is a real gap and the practice note says so.
- **Topic 10, Software Engineering Principles.** Volume 1 has none; it lives in
  a different volume of the series (the tutorials volume), which is out of scope
  here.

Topic 6 (random numbers and Monte Carlo) has a chapter in [S43] but **no
exercises** in it, so nothing was drawn from there.

## What is copied, and what is ours

**Nothing is vendored.** CC BY 4.0 would permit copying the exercise text with
attribution; the exercises are nevertheless **restated in our words** at the top
of [`cache_sim.py`](cache_sim.py), each cited to its chapter and section, so
that the file can be read without ambiguity about what is Eijkhout's and what is
ours. All code, all numbers and all tests are ours.

## The solution

[`cache_sim.py`](cache_sim.py) - a set-associative cache simulator (`n_sets ×
assoc` lines, LRU per set, configurable line size and index-bit rule) and the
three experiments the exercises ask for.

| exercise | what it asks | what the code answers |
|---|---|---|
| **E1** *Caches → Direct mapped caches* | his `double A[3][8192]` loop conflicts because the rows are exactly 64 KB apart; show the conflicts go away if the *most significant* address bits index the cache, and why that is a bad rule in general | low bits: **1536 misses, 0 hits** - every one of the 3×512 accesses is a conflict miss. High bits: **384 misses** = one per 32-byte line per row, the compulsory minimum. And the counter-argument, measured: a contiguous 64 KB stream leaves **2048** lines resident under low-bit indexing and **1** under high-bit indexing, because a small contiguous array has identical high bits |
| **E2** *Caches → Associative caches* | simulate a k-way cache of 32 entries with 16-bit addresses; store 32 random addresses, count survivors, 100 trials, report median/mean/stdev, find the limit in k | measured mean at k=1 is **20.44**, against the closed form $n(1-(1-1/n)^n) = 20.41 \to n(1-1/e)$ derived in the module; k=32 gives exactly 32 every time. The occupancy is monotone in k. This is what turns a plotting exercise into a testable one |
| **E3** *Locality → Spatial locality* | contrast the locality of the pairwise (tree) summation with the linear sum | linear: **0.25 misses per element**, i.e. one per four-double line, the compulsory minimum. Tree: **0.995**, four times worse, on the same cache |

```sh
uv run python cache_sim.py          # the three experiments
uv run pytest .           # 14 tests
```

Sources: [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
