# 00 Exam focus - what is known, what is guessed

Read this before deciding how much time to give a topic. Written 2026-09-22 from
the sources in [`../refs/SOURCES.md`](../refs/SOURCES.md); logistics updated
2026-09-27 after a logged-in re-read of TISS, in which no field of the course page
had changed [S1].

## The honest headline: there is no past paper

Unlike most TU Wien courses, 360.242 leaves no public trail.

- **TISS** says *"No lecture notes are available."* in every offering from 2019W
  to 2026W [S1] [S2] [S3].
- **VoWi** has a page for the course and **it is empty** - Inhalt, Ablauf,
  Vortrag, Übungen, *Prüfung/Benotung*, Zeitaufwand, Unterlagen, Tipps all read
  `noch offen`, and the attachment count is **0 Materialien** [S4]. The same is
  true of the sibling NSSC II page [S5].
- The course does **not** run under a second course number, so there is no
  "other LVA" page holding the papers: the only similarly-named LVAs are
  NSSC II (tiss:360243) under two lecturers, both also empty [S4] [S5].
- Neither the **Institute for Microelectronics** [S7] nor any of the five
  lecturers publishes slides, sheets or papers for this course [S8] [S10].
- **TUWEL** has the material and needs a login. Not fetched, not ours to copy.
  The course opens there on 05.10.2026 [S1].

So nothing below is a reconstruction of a real paper. What follows is what TISS
states, what the structure of the course implies, and - clearly marked - what is
a guess.

## What TISS actually states [S1]

| field | value | stable since |
|---|---|---|
| Type | **VU** (Lecture *and* Exercise), 3.0 h, 6.0 ECTS | ≥ 2024W |
| Mode of examination | **"Written and oral"** | ≥ 2024W |
| Examination modalities | *"Exercises hand-in, a minimum threshold is required to be eligible for the final examination at the end of the term"* | ≥ 2024W, verbatim |
| Teaching methods | *"Lectures, assignments (group homework) and discussion of case studies"* | ≥ 2024W, verbatim |
| Exam | Wed **27.01.2027, 10:00-13:00**, GM 2 Radinger, **written**, 3 hours; registration 19.10.2026 00:00 - 22.01.2027 14:00 | |
| Substitute exam | Fri **05.03.2027, 11:00-14:00**, FH HS 6, **written**, 3 hours; registration 11.02.2027 00:00 - 25.02.2027 23:59 | |
| Literature | *"No lecture notes are available."* | ≥ 2024W |
| Previous knowledge | C++ and Python (basics) | ≥ 2024W |

Four things follow directly, and they are the only things that follow directly:

1. **The exercises are a gate, not a grade component you can skip.** "A minimum
   threshold is required to be eligible for the final examination" - miss it and
   you do not sit the exam at all. Whether the hand-ins also carry marks is
   **not stated anywhere public**.
2. **Group homework.** "assignments (group homework)" [S1]. Expect to be
   assigned to a group and to hand in code plus a report.
3. **The written exam is three hours.** That is long for a paper of small hand
   calculations; it is the length of a paper that asks you to *design*, *analyse*
   and *justify*. See "the shape a 3-hour paper implies" below.
4. **"Written and oral" vs two written sittings.** The "Mode of examination"
   field says written *and* oral, but both entries in the Exams table say
   *written*. This discrepancy is in TISS itself, in all three years [S1–S3], and
   is **not resolved anywhere public.** The safe reading: the written exam is
   scheduled; an oral component (most likely a defence of the group hand-in) may
   be arranged separately. **Ask in the first lecture.**

## Logistics and status, 2026-09-27

| what | state | source |
|---|---|---|
| Course registration | Cap 50, CSE prioritised, then 066 393, then other masters. Closes **08.10.2026 15:00** | [S1] |
| Lecture | Thu 13:00-16:00, Sem.R. DA grün 03 A, 01.10.2026-28.01.2027 | [S1] |
| Exams | written 27.01.2027 10:00-13:00 GM 2 Radinger (register 19.10.2026-22.01.2027 14:00); substitute 05.03.2027 11:00-14:00 FH HS 6 | [S1] |
| TUWEL | course available from 05.10.2026 | [S1] |


TISS points to TUWEL from 05.10.2026 [S1] and publishes no material of its
own ("No lecture notes are available." [S1]); where the gated exercise hand-ins
are issued and submitted is not stated publicly.

## What the syllabus tells you about weighting

The "Subject of course" list is ten items and has been byte-identical since at
least 2024W [S1] [S2] [S3]. Ten topics over a 13-week, 3-hour lecture is roughly
**one topic per lecture with a little slack** - that is the only defensible
weighting model, and it means *no topic is a minor one*. There is no "if time"
chapter to skip.

The five lecturers come from four institutes [S1] [S10]: E360 Microelectronics
(Manstetten), E101 Analysis and Scientific Computing (Schöberl), E325 Mechanics
and Mechatronics (Toth), E322 Fluid Mechanics and Heat Transfer (García-Villalba,
Moriche). That composition is new in 2025W - 2024W was E360 only [S3]. It is
reasonable to expect each institute's lecturer to examine their own block; it is
**not established** which block that is.

## The shape a 3-hour written paper implies

*(This section is inference, not evidence. Marked as such.)*

Three hours and a ten-topic syllabus whose learning outcomes [S1] are *"select
and apply fundamental methods … and to judge the challenges regarding computing
time and implementation effort"* points at a paper made of:

- **Estimation questions.** "This kernel does X flops and moves Y bytes. On a
  machine with peak P and bandwidth B, what can it achieve and why?" The
  learning outcome says *judge the challenges regarding computing time* - that
  is the roofline question (note 01), and it is the single most characteristic
  question this course can ask.
- **Cost and scaling.** Complexity of an algorithm, memory of a data structure,
  iteration count of a solver against grid size, Amdahl/Gustafson on a measured
  table (notes 05, 07, 08).
- **Stability and accuracy conditions.** The explicit time-step limit, the order
  of a scheme, a convergence table read correctly (notes 03, 04).
- **"Choose and justify."** Direct vs iterative solver, structured vs
  unstructured mesh, MC vs quadrature, OpenMP vs threads - with the *reason*,
  not the name. The learning outcomes are written almost entirely in these
  verbs: *select*, *judge*, *evaluate*, *analyze*.
- **Short code reading or writing.** The prerequisite is C++ and Python [S1]
  [S6], so a data race, a wrong loop order or a missing `reduction` is fair game.

What a 3-hour paper is unlikely to be, given the syllabus: long hand
computations. There is no chapter of this course whose content is "do Gaussian
elimination on a 3×3 by hand" - that is 101.973 Numerical Computation, the CSE
module next door.

## The five questions most worth being able to answer cold

Written from the learning outcomes [S1] and the topic list, one per cluster.
They are **ours**, not reconstructions.

1. **Given a kernel, decide whether it is memory or compute bound, and say what
   the machine can achieve.** Compute the arithmetic intensity, compare it to
   the ridge point `P_peak / B`, quote the attainable
   `min(P_peak, AI × B)` [S16]. Do it for a triad, a 5-point stencil and a
   CSR SpMV without looking anything up (note 01).
2. **Given a PDE, a grid and a time integrator, state the stability limit and
   the order, and say what each costs.** Von Neumann analysis to `r ≤ 1/(2d)`,
   explicit vs implicit cost per step, why `Δt ~ h²` makes explicit schemes
   expensive in 2D and 3D [S23] (note 04).
3. **Given a sparse system, choose a solver and defend the choice with numbers.**
   Direct vs stationary vs CG, `κ ~ N²` for Poisson, `k ~ √κ ~ N` CG iterations,
   memory of a sparse Cholesky in 3D [S22] (note 05).
4. **Given a parallel loop, find the bug and the bottleneck.** Data race →
   `reduction` / `atomic` / `critical` and what each costs; false sharing; a
   memory-bound kernel that saturates before the cores do; read a measured
   scaling table with Amdahl and Karp–Flatt [S11] [S19] [S21] (note 07).
5. **Given a simulation result, get it on screen correctly.** Write a legacy VTK
   file whose `DIMENSIONS` counts points, whose values are in x-fastest order,
   whose `CELLS` size field includes the per-cell counts and whose cell type ids
   are real [S12] [S13] (note 09).

## How to prepare

1. **Do the hand-ins properly and early.** They are the eligibility gate [S1],
   and they are group work, so a late partner is your problem too.
2. **Learn the numbers of your own machine.** This course's first three topics
   are about a real computer. `sysctl -a | grep cache`, `lscpu`, a STREAM run
   [S17], `clang -Rpass=loop-vectorize`. Note 01 records the host's figures
   [S34]; get your own.
3. **Read [S8].** <https://jschoeberl.github.io/IntroSC/intro.html>, the
   "Performance" part. It is by one of the lecturers, it is four chapters, and
   it is the only public writing that overlaps this syllabus.
4. **Be able to run every algorithm as code, not as a formula.** This is a VU
   with a coding prerequisite; `src/` exists for that.
5. **Learn the OpenMP clauses from the specification, not from memory** [S11].
   `reduction`, `schedule`, `private`/`firstprivate`/`default(none)`,
   `atomic` vs `critical`. It is in
   [`../refs/vendor/openmp-api-specification-5.2.pdf`](../refs/vendor/openmp-api-specification-5.2.pdf).
6. **Ask about the oral part in the first lecture**, and about whether the
   hand-ins carry marks. Both are unresolved above.

## Our exam-style questions

Every note ends with five exam-style questions. **All of them are ours.** No
public past paper for this course exists, so none of them is modelled on a real
question, and none claims to be. They are written to the learning outcomes [S1]
and to the topic they follow. Where a question has a single objectively correct
answer because a specification fixes it - the OpenMP clauses, the VTK format,
the C++ RNG test vectors - the note says which source fixes it.
