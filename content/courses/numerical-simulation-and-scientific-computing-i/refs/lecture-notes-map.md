# Topic map - what the course says it covers, and where we cover it

There is no lecture script for 360.242 (see [`SOURCES.md`](SOURCES.md)), so the
structural index is the **TISS "Subject of course" list** [S1], which is
character-for-character identical in 2024W, 2025W and 2026W [S1–S3]. Ten items,
one note each, in TISS's order. The notes are numbered to match.

## The ten topics

| # | TISS topic [S1] | our note | primary sources | our code |
|---|---|---|---|---|
| 1 | Computer Architectures | [01](../notes/01-computer-architectures.md) | [S8] *Caches*, *Pipelining*; [S16] roofline; [S17] STREAM; [S18]; [S34] the host | `cpp/cache_bench.cpp` |
| 2 | Serial Optimization | [02](../notes/02-serial-optimisation.md) | [S8] *Caches* §matmul; [S31]; [S37] clang flags; [S35] | `cpp/matmul_opt.cpp` |
| 3 | Numerical Derivatives and Integrals | [03](../notes/03-numerical-derivatives-and-integrals.md) | [S25] Fornberg; [S23] §1 | `py/fd_poisson.py`, `py/fdstencil.py` |
| 4 | Finite Difference Discretization | [04](../notes/04-finite-difference-discretisation.md) | [S23] LeVeque; [S24] Lax–Richtmyer, CFL | `cpp/fd_poisson1d.cpp`, `cpp/heat2d.cpp`, `py/heat2d.py` |
| 5 | Numerical Linear Algebra | [05](../notes/05-numerical-linear-algebra.md) | [S22] Saad; [S15] Hestenes & Stiefel | `cpp/csr.cpp`, `py/csr.py` |
| 6 | Random Number Generation and Monte Carlo Methods | [06](../notes/06-random-numbers-and-monte-carlo.md) | [S26] MT; [S27] Marsaglia; [S28] Park–Miller; [S29] Hull–Dobell; [S30] Box–Muller; [S14] C++ test vectors | `cpp/rng_mc.cpp`, `py/montecarlo.py`, `py/lattice.py`, `py/test_lattice.py` |
| 7 | Shared Memory Parallel Computing | [07](../notes/07-shared-memory-parallel-computing.md) | **[S11] the OpenMP spec**; [S8] *Parallelization*; [S19]/[S20]/[S21] | `cpp/omp_examples.cpp`, `cpp/threads_cpp.cpp`, `py/scaling.py` |
| 8 | Algorithmic Complexity and Data Structures | [08](../notes/08-algorithmic-complexity-and-data-structures.md) | [S14] container complexity requirements | `cpp/containers_bench.cpp` |
| 9 | Mesh Generation and Visualiziation *(sic)* | [09](../notes/09-mesh-generation-and-visualisation.md) | **[S12]/[S13] the VTK format**; [S32] Delaunay; [S33] Gmsh | `cpp/vtk_writer.cpp`, `py/delaunay.py`, `py/vtk_check.py` |
| 10 | Software Engineering Principles for Scientific Computing | [10](../notes/10-software-engineering-for-scientific-computing.md) | [S36] CMake; [S37]/[S38] sanitizers; [S39] pybind11; [S40] git; [S41] licences | `cpp/CMakeLists.txt`, `sh/*.sh` |

Plus [00-exam-focus.md](../notes/00-exam-focus.md), which is about the exam
rather than a topic, and
[11-practice-set.md](../notes/11-practice-set.md), which is 24 exam-shaped
problems drawn from **substitute** sources - [S8], [S43] and [S44] - because
this course sets none of its own. Its last table names the topics for which no
free practice material exists at all: **6, 9 and 10**.

## How the sources cover the ten topics

`●` = a source we treat as authoritative for that topic. `○` = supporting.

| topic | [S8] lecturer's book | [S11] OpenMP spec | [S12]/[S13] VTK | original papers | textbooks |
|---|---|---|---|---|---|
| 1 Architectures | ● | | | ● [S16] [S17] | ○ [S35] |
| 2 Serial optimisation | ● | | | ● [S31] | ○ [S35] [S18] |
| 3 Derivatives & integrals | | | | ● [S25] | ○ |
| 4 FD discretisation | | | | ● [S24] | ● [S23] |
| 5 Linear algebra | | | | ● [S15] | ● [S22] |
| 6 RNG & Monte Carlo | | | | ● [S26]–[S30] | ○ |
| 7 Shared memory | ● | ● | | ● [S19]–[S21] | ○ [S35] |
| 8 Complexity & structures | ○ | | | | ○ |
| 9 Mesh & visualisation | | | ● | ● [S32] [S33] | |
| 10 Software engineering | ● | | | ● [S38] | ○ |

Two things fall out of this table and they drive the whole note set:

- **Topics 7 and 9 have a normative document.** The OpenMP spec and the VTK
  format say exactly what a clause or a keyword means. Those two notes are the
  ones where a claim can simply be *checked*, and they are where the exam can
  ask a question with a single right answer. Both specs are in
  `vendor/`.
- **Topics 1, 2 and 8 have no fixed truth at all** - they are about *this*
  machine. Their numbers come from [S34] and from running the code. A number in
  those notes is only meaningful with the machine and the compiler beside it,
  which is why every table there now names both.

## Where the syllabus and the teaching team disagree

The topic list has been byte-identical since at least 2024W [S1–S3], but the
teaching team changed completely for 2025W and the slot grew from 2 h to 3 h
[S2 vs S3]:

| | 2024W [S3] | 2025W and 2026W [S2, S1] |
|---|---|---|
| lecturers | Manstetten, Etl, Filipovic, Salzmann | Manstetten, **Schöberl**, **Toth**, **Garcia Villalba Navaridas**, **Moriche Guerrero** |
| institutes | E360 Microelectronics only | E360 + **E101 ASC** + **E325 Mechanics/Mechatronics** + **E322 Fluid Mechanics** |
| slot | Thu 14:00–16:00 (2 h) | Thu 13:00–16:00 (3 h) |
| room | EI 11 HS - INF | Sem.R. DA grün 03 A |
| ECTS | 6.0 | 6.0 |
| topics | the ten below | **identical** |

So the same ten topics are now delivered by four institutes. Consequences the
notes act on:

1. **Note 07 no longer assumes OpenMP is the whole answer.** OpenMP is the
   institute's historical tool and remains the normative reference [S11], but
   Schöberl's own material teaches a hand-written C++ task manager over
   `std::thread` and explicitly lists OpenMP, TBB and Taskflow as
   alternatives [S8]. `src/cpp/threads_cpp.cpp` covers the C++ route; the note
   gives both and says which is which.
2. **Notes 03–05 should be read with a fluid-mechanics/mechanics eye.** Three of
   the five lecturers are from E322 and E325, whose own courses are CFD and
   structural mechanics [S10]. The manufactured-solution and convergence-table
   discipline in notes 03/04 is the part those groups examine hardest.
3. **Nothing in the topic list moved**, so the note order is safe.

## Claimed by TISS but thin in the sources

- **"Mesh Generation"** (topic 9). The notes describe Delaunay and advancing
  front, but nothing public says which the course implements. [S32] is the
  primary source for the Delaunay half; `src/py/delaunay.py` is a Bowyer–Watson
  implementation added so the note has code behind it. Advancing front and
  octree meshing remain description-only and are marked as such.
- **"Discussion of case studies"** (Teaching methods, [S1]). No case study is
  public. Nothing in the notes is written to it.
- **"Written and oral"** (Mode of examination, [S1]) while the Exams table lists
  only *written* sittings. See [00-exam-focus.md](../notes/00-exam-focus.md);
  this discrepancy is in TISS itself and is not resolved anywhere public.
