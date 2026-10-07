# 360.242 NSSC I - notes

One note per lecture topic, in the order of the TISS "Subject of course" list
[S1], which has been byte-identical since at least 2024W [S1] [S2] [S3]. Each
note: definitions and formulas, a worked example with numbers measured on the
reference code (Apple M3 Pro, Apple clang 21.0.0, `-O2`; hardware parameters in
[S34]; re-measured 2026-09-27), pitfalls, exam-style questions with answers, and pointers into
[`../src`](../src/README.md). Assumed background: physics master's level maths,
C++ and Python basics (the course prerequisite [S1], and the programme FAQ is
explicit that no introductory coding course is provided [S6]).

**Course logistics, as of 2026-09-27** (details and reasoning in
[00-exam-focus.md](00-exam-focus.md#logistics-and-status-2026-09-27)).
Course registration: cap 50, CSE first; closes 08.10.2026 15:00 [S1].
Lecture Thu 13:00-16:00, Sem.R. DA grün 03 A, from 01.10.2026 [S1].
Written exam 27.01.2027 10:00-13:00, GM 2 Radinger
(registration 19.10.2026-22.01.2027 14:00); substitute 05.03.2027 11:00-14:00,
FH HS 6 [S1]. TUWEL opens 05.10.2026 [S1].

Every claim carries an `[S<n>]` citation into
[`../refs/SOURCES.md`](../refs/SOURCES.md); claims that could not be sourced are
marked `(unsourced: …)` in place. Changes are recorded in
`CHANGELOG.md`.

**Literature.** TISS names **no** literature and states *"No lecture notes are
available."* [S1]. The books below are therefore **our** choice, not the
course's, and the notes cite them only where no primary source covers a claim:
Hager & Wellein, *Introduction to High Performance Computing for Scientists and
Engineers* [S35] (topics 1, 2, 7); LeVeque, *Finite Difference Methods for ODEs
and PDEs* [S23] (topics 3, 4); Saad, *Iterative Methods for Sparse Linear
Systems* [S22], free from the author (topic 5). Where a **specification**
exists - OpenMP [S11], the legacy VTK format [S12] [S13], ISO C++ [S14] - the
notes follow it and not a textbook. The one piece of writing by a lecturer of
this course is Schöberl's *Introduction to Scientific Computing* [S8]; read its
"Performance" part.

**Practice material.** There is none for this course: no past paper, no exercise
sheet [S1] [S4]. [Note 11](11-practice-set.md) closes the gap with **substitute
problems** built from three free, licence-clear outside sources - Schöberl's own
exercises [S8] (he is a 2026W lecturer of *this* course [S1]), Eijkhout's *The
Art of HPC* vol. 1 [S43], CC BY 4.0, and Bindel's Cornell CS 5220 HW3 [S44],
MIT - plus our own problems where those are silent. Every problem names its
source; none of them is or claims to be a 360.242 question. The runnable
solutions are in [`../src/exercises/`](../src/exercises/README.md).

| # | note | one line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | what TISS states, what no public source says, what the format implies, and the 2026-09-27 logistics (registration, slot, TUWEL) |
| 01 | [Computer architectures](01-computer-architectures.md) | memory hierarchy, cache lines, latency vs throughput, dependency chains, SIMD, roofline, how to measure FLOP/s and GB/s |
| 02 | [Serial optimisation](02-serial-optimisation.md) | loop order, blocking (and what a real BLAS does), aliasing, compiler flags, inlining, branch prediction, benchmarking protocol |
| 03 | [Numerical derivatives and integrals](03-numerical-derivatives-and-integrals.md) | FD stencils from the order conditions, Fornberg, round-off vs truncation, Richardson, composite quadrature rules |
| 04 | [Finite difference discretisation](04-finite-difference-discretisation.md) | 1D/2D Poisson systems, boundary conditions, heat equation explicit vs implicit, von Neumann/CFL, Lax equivalence, order checks |
| 05 | [Numerical linear algebra](05-numerical-linear-algebra.md) | dense vs CSR, Thomas, Jacobi/Gauss-Seidel/SOR/CG iteration counts on Poisson, preconditioning |
| 06 | [Random numbers and Monte Carlo](06-random-numbers-and-monte-carlo.md) | LCG full period, the Marsaglia lattice and RANDU, Mersenne Twister, seeding, inverse transform, Box-Muller, $1/\sqrt{N}$, variance reduction |
| 07 | [Shared-memory parallel computing](07-shared-memory-parallel-computing.md) | OpenMP from the specification, plain-C++ threads, races and fixes, false sharing, scheduling, Amdahl/Gustafson/Karp-Flatt, scaling |
| 08 | [Algorithmic complexity and data structures](08-algorithmic-complexity-and-data-structures.md) | big-O, STL containers and their standard-mandated cost, structures for meshes and sparse matrices |
| 09 | [Mesh generation and visualisation](09-mesh-generation-and-visualisation.md) | structured vs unstructured meshes, Delaunay and Bowyer-Watson, the legacy VTK format line by line, ParaView |
| 10 | [Software engineering for scientific computing](10-software-engineering-for-scientific-computing.md) | git workflow, Make/CMake (verified against a real CMake run), compiling and linking, lldb and sanitizers, testing, licences, ctypes/pybind11 |
| 11 | [Practice set](11-practice-set.md) | 24 exam-shaped problems with answers, one to four per TISS topic, each tagged with the outside source it is adapted from or marked as ours - **substitute material, not a past paper** |

Figures produced by `src/py/plot_helper.py` are in `img/`:
`fd_poisson_convergence.png` (order-2 line for note 04), `poisson2d.png`.
