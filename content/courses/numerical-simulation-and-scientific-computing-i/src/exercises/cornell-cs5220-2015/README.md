# Cornell CS 5220 *Applications of Parallel Computers*, Fall 2015 - HW3

> **This is not 360.242 material.** 360.242 publishes no exercise sheet and no
> past paper [S1] [S4]. This is **another university's homework**, restated in
> our words, with our own solution to the parts that fit this syllabus.

| | |
|---|---|
| Institution | Cornell University, Department of Computer Science |
| Course | **CS 5220**, *Applications of Parallel Computers* |
| Instructor | David Bindel |
| Year | **Fall 2015** |
| Source | [S44] course site <https://github.com/cornell-cs5220-f15/cornell-cs5220-f15.github.io>, assignment <https://github.com/cornell-cs5220-f15/path> |
| Licence | **MIT** (`LICENSE.md` in both repositories, © 2015 David Bindel) |
| Retrieved | 2026-09-22 |
| Vendored here | **nothing** - the assignment is restated, the code is ours |

## Why it is comparable to this syllabus

CS 5220 is a one-semester graduate course whose first half is exactly 360.242's
performance half: single-core architecture and tuning, shared-memory
parallelism, and *"how fast should this go and why doesn't it"*. Its assignments
are the standard ones of that genre - tune a matrix multiply, tune a stencil
solver, tune an all-pairs shortest path - and each comes with a required report
of profiling, speedup plots and a **performance model that predicts the
speedup**. That last requirement is the same verb as 360.242's learning
outcomes: *judge the challenges regarding computing time* [S1].

HW3 was picked over HW1 (matrix multiply) on purpose: this repository already
has a blocked-matmul study in [`../../cpp/matmul_opt.cpp`](../../cpp/matmul_opt.cpp)
and a task-parallel one in
`../tuwien-introsc-2025/`. HW3 adds
something neither has - an algorithm whose **complexity** and whose **memory
access pattern** are both on the table at once, which is TISS topic 8 meeting
topics 2 and 7.

## What it covers that 360.242's TISS topic list also covers

| TISS topic [S1] | how HW3 touches it |
|---|---|
| 2 Serial Optimization | the kernel is a matrix product; profiling, blocking and vectorisation are the assignment's "tuning" task |
| 7 Shared Memory Parallel Computing | the reference implementation is an OpenMP `parallel for` with a `reduction(&& : done)`; strong and weak scaling studies are required deliverables |
| 8 Algorithmic Complexity and Data Structures | $O(n^3)$ Floyd–Warshall against $O(n^3 \log n)$ repeated squaring - the same answer at different cost, chosen for its parallel shape rather than its operation count |

## What it covers that 360.242 does not, and the reverse

**In CS 5220 but outside this syllabus.** MPI and distributed memory (HW3's
second task is explicitly "parallelize your code using MPI"); the Xeon Phi
accelerator the 2015 class ran on; cluster job submission; peer review of other
groups' reports. 360.242's topic 7 is *shared memory* [S1] and its topic list has
no distributed-memory or accelerator entry - the Institute for Microelectronics
teaches those in separate courses [S7].

**In this syllabus but absent from CS 5220.** Random numbers and Monte Carlo
(topic 6) and mesh generation and visualisation (topic 9) are not in the 2015
assignment set. Finite differences appear only as the shallow-water HW2, which
is a solver to be tuned rather than a discretisation to be derived.

**Assessment shape.** CS 5220 is graded on project reports; 360.242 is graded on
a **3-hour written exam** gated by group hand-ins [S1]. So the deliverable of
this assignment - a tuning report - is *not* the shape of a 360.242 answer. What
transfers is the analysis behind it, which is what the module below extracts.

## What is copied, and what is ours

**Nothing is vendored.** The MIT licence would permit it, but nothing here needs
the C reference: the assignment is **restated in our words** at the top of
[`minplus_path.py`](minplus_path.py), and the implementation, the cost model and
the tests are ours. The reference `path.c` was read to confirm that the
algorithm really is repeated `square()` until a fixed point, so that the
restatement is accurate.

## The solution

[`minplus_path.py`](minplus_path.py) - all-pairs shortest paths as a matrix
product in the $(\min, +)$ semiring.

| task | what it answers |
|---|---|
| **A** cost model | `floyd_warshall` in $O(n^3)$ against `shortest_paths_squaring`; after $s$ squarings the entries are shortest walks of at most $2^s$ edges, so $\lceil \log_2 (n-1)\rceil$ squarings suffice. `flop_counts` states the ratio: the squaring route costs a factor $\log n$ more, bought in exchange for a kernel that blocks and parallelises like GEMM |
| **B** blocking | `minplus_product_blocked` tiles i/j/k. The GEMM blocking argument survives unchanged because `min` is associative and commutative and `+` distributes over it, so partial results over disjoint k-blocks combine exactly as partial sums do. `largest_block_for_cache` picks the tile from a cache size (three tiles resident, not two) |
| **C** correctness | both routes agree with each other and with `scipy.sparse.csgraph.shortest_path`, on random graphs and on a hand-computed three-node example |

**One finding worth the exam.** The obvious stopping test - squaring until the
matrix is bitwise unchanged - is wrong. $\min_k(d_{ik} + d_{kj})$ re-adds the two
halves of an already-optimal path, and in floating point that sum can land one
ulp below the stored value, so the loop chases last bits and runs well past the
$\log n$ bound (8 squarings instead of 4 at $n = 32$, measured). The test needs a
tolerance. That is a convergence test failing for numerical rather than
algorithmic reasons, which is exactly the kind of thing topics 3–5 are about.

```sh
uv run python minplus_path.py       # cost table
uv run pytest .           # 21 tests
```

Sources: [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
