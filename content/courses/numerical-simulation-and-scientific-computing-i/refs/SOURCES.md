# Sources - 360.242 Numerical Simulation and Scientific Computing I

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). Notes cite these as `[S<n>]`. Retrieval dates
are the day the page or file was fetched; TISS and VoWi pages change, so
re-check before an exam.

**Vendoring policy.** Three sources are redistributable and are committed under
`vendor/`; everything else is cited only. See
[`README.md`](README.md) for the licence of each vendored file and
[`fetch-sources.sh`](fetch-sources.sh) for the cite-only downloads. No TUWEL
material was fetched: TUWEL needs a login and is not ours to copy.

**The headline finding.** TISS says outright *"No lecture notes are available."*
in every offering from 2019W to 2026W [S1–S3], VoWi has the course page but it
is empty [S4], and neither the Institute for Microelectronics [S7] nor any of
the five lecturers publishes slides for **this** course. There is **no public
course script and no public past paper for 360.242.** What does exist, and what
this register is built on, is:

1. **[S8]**, the online book of one of the 2026W lecturers (Schöberl), which
   covers the architecture / optimisation / parallelisation third of the
   syllabus in his own words - the closest thing to course material that exists.
2. The **primary sources** (specifications, original papers) behind every
   algorithm and constant the notes state.
3. The **host machine itself** [S34], which is where the notes' measured numbers
   come from and the only way to check them.

Read [`lecture-notes-map.md`](lecture-notes-map.md) for how the ten TISS topics
map onto these.

---

## Course-authoritative

### S1 - TISS course page, 2026W (the semester being studied)

- Title: 360.242 Numerical Simulation and Scientific Computing I, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=360242&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript). **Re-read
  2026-09-27** in a logged-in browser: no field changed (header of
  [`../docs/tiss.md`](../docs/tiss.md)).
- Access: public, no login; the registration status is shown only when logged in
- Registration: cap 50, CSE first; registration closes **08.10.2026 15:00**.
- Used for: the ten-item "Subject of course" list that fixes the note order,
  the learning outcomes, VU 3.0 h / 6.0 ECTS, mode of examination
  ("Written and oral"), examination modalities (exercise hand-ins with a minimum
  threshold), teaching methods ("Lectures, assignments (group homework) and
  discussion of case studies"), the five lecturers, the 50-student cap and its
  priority order, the exam and registration dates, and the literature line
  **"No lecture notes are available."**, the lecture slot (Thu 13:00-16:00,
  Sem.R. DA grün 03 A, 01.10.2026-28.01.2027), the exam sittings (written
  27.01.2027 10:00-13:00, GM 2 Radinger, registration 19.10.2026-22.01.2027
  14:00; substitute 05.03.2027 11:00-14:00, FH HS 6) and "TUWEL course
  available from 05.10.2026". Diffed against
  [`../docs/tiss.md`](../docs/tiss.md) on 2026-09-22 and again on 2026-09-27:
  **no change**, the transcription of 2026-09-21 is still exact.

### S2 - TISS course page, 2025W (previous offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=360242&semester=2025W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the year-on-year diff. Same 6.0 ECTS, same 3.0 h, **same five
  lecturers as 2026W** (Manstetten, Schöberl, Toth, Garcia Villalba Navaridas,
  Moriche Guerrero), same ten topics, same room and slot (Thu 13:00–16:00,
  Sem.R. DA grün 03 A, 02.10.2025 – 29.01.2026), same examination modalities.
  Registration 31.07.2025 12:00 – 02.10.2025 12:00.

### S3 - TISS course page, 2024W (two offerings back)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=360242&semester=2024W&locale=en>
- Retrieved: 2026-09-22
- Access: public
- Used for: the diff. Same 6.0 ECTS and the **same ten topics**, but a
  completely different teaching team - Manstetten, **Etl, Filipovic, Salzmann**,
  all Institute for Microelectronics - and a two-hour slot (Thu 14:00–16:00,
  EI 11 HS - INF, 03.10.2024 – 30.01.2025). Registration 01.08.2024 12:00 –
  03.10.2024 12:00. The exam table on the archived page shows the *2026W* exams,
  i.e. TISS renders current exams on old course pages; historical exam dates are
  therefore **not** recoverable from TISS.
  The offering selector lists 2019W…2026W, so the course has run every winter
  term since 2019W.

### S4 - VoWi: Numerical Simulation and Scientific Computing I VU (Weinbub)

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Numerical_Simulation_and_Scientific_Computing_I_VU_(Weinbub)>
- Retrieved: 2026-09-22 (browser; VoWi runs an Anubis proof-of-work gate that
  refuses plain HTTP clients)
- Access: public
- Used for: **a negative result that matters.** The page exists, is categorised
  `LVAs-aktuell`, and every content section - Inhalt, Ablauf, Vortrag, Übungen,
  *Prüfung/Benotung*, Zeitaufwand, Unterlagen, Tipps - reads `noch offen`
  ("still open"). **0 Materialien**: no past papers, no exercise sheets, no
  grading report. It does give: lecturers Clemens Etl · Paul Manstetten · Josef
  Weinbub, 6.0 ECTS, "Letzte Abhaltung 2023W", English, the Mattermost channel
  `numerical-simulation-and-scientific-computing-i`, and the curriculum slot
  **CSE → Modul Scientific Computing (Pflichtfach)**. Checked the "ähnlich
  benannte LVAs" list as the conventions require: the only siblings are NSSC II
  (Weinbub) and NSSC II (Manstetten), both also 0 Materialien - the course does
  **not** run under a second course number.

### S5 - VoWi: Numerical Simulation and Scientific Computing II VU (Manstetten)

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Numerical_Simulation_and_Scientific_Computing_II_VU_(Manstetten)>
- Retrieved: 2026-09-22
- Access: public
- Used for: identifying the sibling course as **tiss:360243**, last held 2024S,
  also 6.0 ECTS and also in "Modul Scientific Computing (Pflichtfach)". Its
  lecturer list (Asur Vijaya Kumar, Heid, Manstetten, Pettermann, Sturm,
  Weinbub, Zonta) shows the same pattern as S2/S1: NSSC is co-taught by one
  lecturer per participating institute. Also 0 Materialien.

### S6 - TU Wien, CSE master's programme FAQ ("Will I learn to code?")

- URL: <https://www.tuwien.at/en/studies/studies/master-programmes/computational-science-and-engineering/faqs>
- Retrieved: 2026-09-22. Access: public.
- This is the **only external link on the TISS page** [S1] and it is followed
  from the "Previous knowledge" field.
- Used for: the prerequisite claim in [`../notes/README.md`](../notes/README.md).
  "Programming skills are part of the admission requirements for the master's
  programme CSE", so there is no introductory coding course; "The main
  programming languages you will need are C++ and Python"; the modules in which
  programming is actually taught are named as **Programming, Parallel Computing
  and Scientific Computing** - 360.242 sits in the last of those [S4].

### S7 - Institute for Microelectronics (E360), teaching page

- URL: <https://www.iue.tuwien.ac.at/teaching/>
- Retrieved: 2026-09-22. Access: public.
- Used for: confirming that the institute that owns this course publishes **no
  material** for it - the page is a list of links into TISS. It does establish
  the CSE course family at E360: 360.242 NSSC I, 360.251 *Advanced Programming
  with C++*, 360.252 *Computational Science on Many-Core Architectures*. The
  last two are where the C++ and the GPU/many-core material live, which is
  evidence for what 360.242 does **not** have to cover.

### S8 - J. Schöberl, *Introduction to Scientific Computing* ★

- Author: Joachim Schöberl, Institute of Analysis and Scientific Computing
  (E101), TU Wien. Online book (Jupyter Book), "given in this form the first
  time in winter term 23/24", © 2023–2025.
- URLs: <https://jschoeberl.github.io/IntroSC/intro.html> (book),
  <https://github.com/JSchoeberl/IntroSC> (source),
  <https://www.tuwien.at/en/mg/asc/schoeberl/teaching> (the lecturer's own
  teaching page, which lists it under "Online teaching material")
- Retrieved: 2026-09-22
- Access: public, no login. **Licence: LGPL-2.1** (`LICENSE` in the repository),
  which does permit redistribution - not vendored only because it is a live
  multi-hundred-file Jupyter Book that is more useful online than pinned.
- Used for: **the single most valuable source for this course.** Schöberl is one
  of the five 2026W lecturers [S1] and this is his own public teaching material.
  Its "Performance" part - *Vectorization*, *Pipelining*, *Caches*,
  *Parallelization* - is the same ground as TISS topics 1, 2 and 7, in the words
  of a person who will be in the room. Specifically used for:
  - the **latency vs reciprocal-throughput** framing and the ski-lift analogy,
    the statement that an FMA with latency 4 and CPI 0.5 lets a dependent
    accumulation chain use only `CPI/latency` of peak, and that "with eight
    accumulators the full latency bottleneck could be overcome"
    (`performance/pipelining.md`) - this is the source of the number of
    accumulators in note 01 and `cache_bench.cpp`;
  - the **memory-transfer-to-arithmetic ratio** argument (2:1 for an inner
    product, 1:1 for multiple simultaneous inner products), which is arithmetic
    intensity stated operationally (`performance/pipelining.md`);
  - the **cache-blocked matmul** structure, two levels, ~96×96 L2 blocks and a
    4×12 register micro-kernel (`performance/caches1.md`), behind note 02;
  - the **shared vs distributed memory vs accelerator** taxonomy, and the
    scoping line "In this lecture we discuss only shared memory programming"
    (`performance/parallelization.md`), behind note 07;
  - the observation that shared-memory systems get expensive beyond ~20 CPUs,
    and the pointers to OpenMP, Intel TBB and Taskflow - plus the fact that
    **Schöberl teaches a hand-written C++ task manager, not OpenMP**, which is
    why note 07 and `src/cpp/threads_cpp.cpp` now cover both;
  - the measured-bandwidth methodology (sum a long vector with enough
    accumulators, read the cache sizes off the bandwidth-vs-size curve,
    re-run 4 copies in parallel to see the shared limit) - note 01's worked
    example follows it.
  It also names S20, S31 and S42 as its own references.

### S9 - TUWien-ASC / ASC-HPC

- URL: <https://github.com/TUWien-ASC/ASC-HPC>, GitHub organisation
  <https://github.com/TUWien-ASC>
- Retrieved: 2026-09-22. Access: public.
- Used for: the code companion to S8 (`src/taskmanager.{h,cc}`,
  `demos/simd_timings.cpp`, `demos/demo_tasks.cc`, `timing_mem.cc`). Cited as
  evidence of the *style* of exercise an ASC lecturer sets - measure, plot,
  read the machine off the curve - and as the origin of the
  `StartWorkers`/`RunParallel`/`StopWorkers` pattern mirrored in
  `src/cpp/threads_cpp.cpp`.

### S10 - Lecturer identities

- Manstetten (E360 Microelectronics, the constant across every offering):
  <https://www.iue.tuwien.ac.at/>
- Schöberl (E101 ASC, Scientific Computing and Modelling; NGSolve):
  <https://www.tuwien.at/en/mg/asc/schoeberl/>
- Toth (E325 Mechanics and Mechatronics)
- García-Villalba and Moriche (E322 Fluid Mechanics and Heat Transfer)
- Retrieved: 2026-09-22. Access: public.
- Used for: reading the 2025W team change [S2 vs S3]. From 2025W the course
  stopped being a single-institute (E360) lecture and became a four-institute
  one, and the slot grew from 2 h to 3 h. The topic list did not change, so the
  most likely reading is that the same ten topics are now taught by specialists;
  **which lecturer takes which topic is not established anywhere public.**

---

## Standards and specifications

### S11 - OpenMP Application Programming Interface, Version 5.2 (November 2021) ★

- Publisher: OpenMP Architecture Review Board.
- URL: <https://www.openmp.org/wp-content/uploads/OpenMP-API-Specification-5-2.pdf>;
  version list at <https://www.openmp.org/specifications/> (6.0 is also public).
- Retrieved: 2026-09-22. 2,068,230 bytes,
  `sha256 3a176ab131d7f83ff525aa5449f0e0880138ab444a69d19b4365f7f318381946`.
- Access: public. **Licence: explicit permission to copy** - the title page
  reads *"Permission to copy without fee all or part of this material is
  granted, provided the OpenMP Architecture Review Board copyright notice and
  the title of this document appear."* **Vendored**:
  [`vendor/openmp-api-specification-5.2.pdf`](vendor/openmp-api-specification-5.2.pdf).
- Used for: everything normative in note 07 - the fork-join execution model,
  data-sharing attribute clauses (`shared`, `private`, `firstprivate`,
  `default(none)`), `reduction` and its permitted operators, the `schedule`
  kinds (`static`, `dynamic`, `guided`, `auto`, `runtime`) and what each
  guarantees, `critical` / `atomic` / `barrier` / `single` / `master`,
  `collapse`, `simd`, the canonical loop form (which is why `break` is not
  allowed), `omp_get_wtime`, `omp_get_num_threads` vs `omp_get_max_threads`,
  and the statement that the order of combination in a reduction is
  unspecified. The version the toolchain implements is reported by CMake as
  **OpenMP 5.1** (LLVM `libomp`), measured on the host; 5.2 is a superset for
  everything used here.

### S12 - VTK file formats (legacy), Kitware ★

- URL: <https://docs.vtk.org/en/latest/vtk_file_formats/vtk_legacy_file_format.html>
  (also <https://docs.vtk.org/en/v9.3.0/design_documents/VTKFileFormats.html>)
- Retrieved: 2026-09-22. Access: public. Documentation of a BSD-3-Clause
  project; **not vendored** (a live page, and the normative part is S13).
- Used for: **every line of note 09's legacy-VTK section.** The five sections of
  a legacy file (version+identifier, header ≤256 chars, `ASCII`/`BINARY`,
  `DATASET`, attributes); the `STRUCTURED_POINTS` triple
  `DIMENSIONS`/`ORIGIN`/`SPACING` with `nx,ny,nz ≥ 1` and `sx,sy,sz > 0`; the
  `UNSTRUCTURED_GRID` sequence `POINTS n dataType`, `CELLS n size`,
  `CELL_TYPES n`, with `size` the **total number of integers including each
  cell's leading count**; `POINT_DATA`/`CELL_DATA` + `SCALARS name type numComp`
  + `LOOKUP_TABLE`; and the ordering rule quoted verbatim in the note:
  *"Data with implicit topology … are ordered with x increasing fastest, then y,
  then z."* Also the correction that the first line is
  `# vtk DataFile Version x.x` - the version number is **not** fixed at 3.0.

### S13 - `vtkCellType.h`, VTK source

- URL: <https://raw.githubusercontent.com/Kitware/VTK/master/Common/DataModel/vtkCellType.h>
- Retrieved: 2026-09-22. 4,423 bytes,
  `sha256 0dbf5812d4691a877104e78a4035021e0f42e939bb298cedaaa16d8f98e73e93`.
- Access: public. **Licence: BSD-3-Clause** (`SPDX-License-Identifier` on
  line 2), which permits redistribution with the notice. **Vendored**:
  [`vendor/vtkCellType.h`](vendor/vtkCellType.h).
- Used for: the normative cell-type ids in note 09 and in
  `src/cpp/vtk_writer.cpp` / `src/py/vtk_check.py`. Verified against the header:
  `VTK_VERTEX = 1`, `VTK_LINE = 3`, `VTK_TRIANGLE = 5`, `VTK_QUAD = 9`,
  `VTK_TETRA = 10`, `VTK_HEXAHEDRON = 12`, `VTK_WEDGE = 13`, `VTK_PYRAMID = 14`;
  all eight ids in the note are correct. The header also warns that the type
  array is `unsigned char`, capping ids at 255.

### S14 - ISO/IEC 14882 (C++), [rand.predef] ★

- Working draft, freely readable: <https://eel.is/c++draft/rand.predef>
  (mirror of the WG21 draft; the published standard is
  <https://www.iso.org/standard/83626.html>, paid).
- Retrieved: 2026-09-22. Access: draft public, standard paywalled.
  **Not vendored.**
- Used for: the **test vectors that make `src/*/rng*` verifiable.** The standard
  *requires* that the 10000th consecutive invocation of a default-constructed
  `std::minstd_rand0` produce **1043618065** and of `std::mt19937` produce
  **4123659995**. Both are asserted in `src/cpp/rng_mc.cpp` and
  `src/py/test_montecarlo.py`. The same clause fixes `minstd_rand`
  (a = 48271) at **399268537** - a third vector now used as well. It also fixes
  the parameters: `minstd_rand0 = linear_congruential_engine<uint_fast32_t,
  16807, 0, 2147483647>`, `mt19937 = mersenne_twister_engine<…,19937,…>` with
  default seed 5489.

---

## Primary literature - original papers

### S15 - M. R. Hestenes and E. Stiefel, "Methods of Conjugate Gradients for Solving Linear Systems", *J. Res. Natl. Bur. Stand.* **49**(6), 409–436, 1952 ★

- URL: <https://nvlpubs.nist.gov/nistpubs/jres/049/6/v49.n06.a08.pdf>
- Retrieved: 2026-09-22. 1,346,607 bytes,
  `sha256 63ac54f568a782821d51eeed8fe786e40a335413527a3a527c3c0fdf9d4b07b5`.
- Access: public. **Licence: a work of the U.S. Government published in the
  Journal of Research of the NBS/NIST - not subject to copyright in the United
  States.** **Vendored**:
  [`vendor/hestenes-stiefel-1952-conjugate-gradients.pdf`](vendor/hestenes-stiefel-1952-conjugate-gradients.pdf).
- Used for: note 05's CG section - the original algorithm, the A-orthogonality
  of the search directions, termination in at most n steps in exact arithmetic,
  and the authors' own §19 warning that "the results in the (n+1)st and (n+2)nd
  iterations are normally far superior to those obtained in the nth" (i.e. that
  finite termination is a theorem about exact arithmetic, not a stopping rule).
  The scan has no usable text layer for the tables, so **no numerical result of
  the paper is reproduced in a test**; the $\sqrt\kappa$ error bound in the note
  is taken from S22 instead, which states it in modern notation.

### S16 - S. Williams, A. Waterman, D. Patterson, "Roofline: An Insightful Visual Performance Model for Multicore Architectures", *CACM* **52**(4), 65–76, 2009

- URLs: <https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf>
  (free copy), tech-report version
  <https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf>,
  DOI <https://doi.org/10.1145/1498765.1498785> (ACM, paywalled)
- Retrieved: 2026-09-22. Access: free copies as above; **not vendored** (no
  redistribution notice).
- Used for: note 01's roofline section - the definition of **operational /
  arithmetic intensity** as flops per byte of DRAM traffic, the model
  `attainable = min(peak flops, AI × peak bandwidth)`, the log-log plot with a
  sloped bandwidth roof and a flat compute roof, the **ridge point** and its
  reading (kernels left of it are memory bound), and the ceilings that lower
  each roof when SIMD or ILP is not used.

### S17 - J. D. McCalpin, STREAM benchmark

- URL: <https://www.cs.virginia.edu/stream/ref.html>
- Retrieved: 2026-09-22. Access: public; **not vendored.**
- Used for: the definition of the **Triad** kernel `a[i] = b[i] + s*c[i]` and
  its byte count (24 B per iteration, 2 flops), the rule that arrays must be
  ≥4× the last-level cache, and the convention that reported bandwidth counts
  bytes the program asked for - which is why note 01 has a pitfall about
  write-allocate traffic. `src/cpp/cache_bench.cpp::triad_gbs` implements this
  kernel.

### S18 - A. Fog, optimization manuals (esp. manual 3, *The microarchitecture of Intel, AMD and VIA CPUs*)

- URL: <https://www.agner.org/optimize/> (PDFs, e.g.
  <https://www.agner.org/optimize/optimizing_cpp.pdf>)
- Retrieved: 2026-09-22. Access: free download. **Licence: none stated on the
  manual (title page carries only "Copyright © 2004 - 2026"), so all rights
  reserved. Not vendored.** (The GPL notice on `agner.org/optimize/` applies to
  the *asmlib* software package, not to the manuals - checked.)
- Used for: instruction latency and reciprocal throughput, cache sizes for a
  named microarchitecture, and branch-prediction misprediction costs. This is
  the reference **S8 itself uses** ("A great source of information are the
  optimization manuals by Agner Fog … manual 3 … Chapter 11: Intel Skylake
  pipeline"), which is why note 01's x86 column cites it rather than a vendor
  datasheet.

### S19 - G. M. Amdahl, "Validity of the single processor approach to achieving large scale computing capabilities", *AFIPS Spring Joint Computer Conference*, 483–485, 1967

- DOI: <https://doi.org/10.1145/1465482.1465560> (ACM, paywalled). Access: not
  free; **not vendored.**
- Used for: note 07's fixed-size speedup law `S(p) = 1/(f + (1-f)/p)` and its
  limit `1/f`.

### S20 - J. L. Gustafson, "Reevaluating Amdahl's Law", *CACM* **31**(5), 532–533, 1988

- DOI: <https://doi.org/10.1145/42411.42415> (ACM, paywalled). Access: not free;
  **not vendored.**
- Used for: note 07's scaled speedup `S(p) = f + (1-f)p` (in Gustafson's own
  letters, `s + p·N` with `s + p = 1` measured **on the parallel run**), and the
  1024-processor nCUBE result that motivated it.
- **Caveat recorded in the note**: the serial fraction in S19 and the serial
  fraction in S20 are *different quantities* - see S21.

### S21 - Y. Shi, "Reevaluating Amdahl's Law and Gustafson's Law", Temple University, 1996

- URL: <https://cgvr.cs.uni-bremen.de/teaching/mpar_literatur/Reevaluating%20Amdahl's%20Law%20and%20Gustafson's%20Law.pdf>
  (also <https://cis.temple.edu/~shi/wwwroot/shi/public_html/docs/amdahl/amdahl.html>)
- Retrieved: 2026-09-22. Access: public; **not vendored.**
- Used for: the correction in note 07 that the two laws are **algebraically the
  same law in two normalisations** - Amdahl's serial percentage is measured
  against the 1-processor time and is independent of `p`, Gustafson's is
  measured against the `p`-processor time and depends on `p`; substituting one
  into the other gives the same formula. Shi states directly that Gustafson's
  original paper claims an exception to Amdahl's law and that this claim rests
  on conflating the two percentages. `src/py/scaling.py` implements the
  conversion and tests it.

### S22 - Y. Saad, *Iterative Methods for Sparse Linear Systems*, 2nd ed., SIAM 2003

- URL: <https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf>
- Retrieved: 2026-09-22. Access: free download from the author's page.
  Licence: front matter reads "Copyright © 2003 by the Society for Industrial
  and Applied Mathematics"; **not vendored.**
- Used for: note 05 - the CSR/CSC/COO/ELL storage definitions and the SpMV loop;
  the splitting `A = M - K` and the convergence criterion `ρ(M⁻¹K) < 1`;
  Jacobi / Gauss–Seidel / SOR and the SOR optimum for consistently ordered
  matrices; the CG energy-norm bound
  `‖e_k‖_A ≤ 2((√κ-1)/(√κ+1))^k ‖e_0‖_A`; preconditioned CG and IC(0);
  GMRES/BiCGSTAB for the non-symmetric case; fill-in and reordering.

### S23 - R. J. LeVeque, *Finite Difference Methods for Ordinary and Partial Differential Equations*, SIAM 2007

- Book page: <https://faculty.washington.edu/rjl/fdmbook/>, notes page
  <https://faculty.washington.edu/rjl/booksnotes.html>. DOI
  <https://doi.org/10.1137/1.9780898717839> (SIAM, paywalled).
- Retrieved: 2026-09-22. Access: the book is not free; the author's page and the
  associated MATLAB/Python code are. **Not vendored.**
- Used for: note 04 - the 1D/2D Poisson stencils and the tridiagonal/
  block-tridiagonal matrices; the eigenpairs
  `λ_k = (4/h²)sin²(kπh/2)`, `v_k = (sin kπx_i)` and hence `κ ~ N²`;
  the truncation error `(h²/12)u''''`, the bound `‖A⁻¹‖_∞ ≤ 1/8` and the
  resulting `O(h²)` global error; ghost-point Neumann conditions;
  von Neumann analysis and the diffusion limit `r ≤ 1/(2d)`; the θ-schemes and
  Crank–Nicolson's oscillatory behaviour for stiff modes; the method of lines;
  and the **Lax equivalence theorem** (S24).

### S24 - P. D. Lax and R. D. Richtmyer, "Survey of the stability of linear finite difference equations", *Comm. Pure Appl. Math.* **9**(2), 267–293, 1956; and R. Courant, K. Friedrichs, H. Lewy, "Über die partiellen Differenzengleichungen der mathematischen Physik", *Math. Ann.* **100**, 32–74, 1928

- DOIs: <https://doi.org/10.1002/cpa.3160090206> (Wiley, paywalled),
  <https://link.springer.com/article/10.1007/BF01448839> (Springer, paywalled)
- Access: not free; **not vendored.**
- Used for: the Lax equivalence theorem and the CFL condition as named in
  note 04, cited to their originals rather than to a textbook restatement.

### S25 - B. Fornberg, "Generation of Finite Difference Formulas on Arbitrarily Spaced Grids", *Math. Comp.* **51**(184), 699–706, 1988

- DOI: <https://doi.org/10.1090/S0025-5718-1988-0935077-0>; AMS page
  <https://www.ams.org/journals/mcom/1988-51-184/S0025-5718-1988-0935077-0/>
  (the AMS blocks scripted clients; open in a browser). Access: AMS makes
  *Mathematics of Computation* back issues free after five years.
  **Not vendored.**
- Used for: note 03's "general recipe" for stencil weights - the algorithm that
  produces the weights of any order on any node set, which is what
  `src/py/fdstencil.py` now implements and tests against the table in note 03.

### S26 - M. Matsumoto and T. Nishimura, "Mersenne Twister: A 623-dimensionally equidistributed uniform pseudo-random number generator", *ACM TOMACS* **8**(1), 3–30, 1998

- URL: <http://www.math.sci.hiroshima-u.ac.jp/m-mat/MT/ARTICLES/mt.pdf>
  (author-hosted)
- Retrieved: 2026-09-22. Access: free from the author. ACM copyright;
  **not vendored.**
- Used for: note 06's MT19937 facts - period `2^19937 − 1`, 624 words of state,
  **623-dimensional equidistribution to 32-bit accuracy** (the title itself),
  and the tempering step. Also the basis for the note's warning that MT is not
  cryptographic.

### S27 - G. Marsaglia, "Random numbers fall mainly in the planes", *PNAS* **61**(1), 25–28, 1968 ★

- URL: <https://pmc.ncbi.nlm.nih.gov/articles/PMC285899/> (free full text)
- Retrieved: 2026-09-22. Access: public; **not vendored.**
- Used for: note 06's lattice statement - k-tuples from an LCG lie on at most
  `(k! m)^{1/k}` hyperplanes - and the RANDU example. RANDU's multiplier
  `a = 65539 = 2^16 + 3` satisfies `x_{k+2} = 6x_{k+1} − 9x_k (mod 2^31)`
  exactly, which puts every triple on 15 planes. **This identity is now a
  test** (`src/py/test_lattice.py`): it is an exact, published, reproducible
  result, which is the strongest verification in the whole course folder.

### S28 - S. K. Park and K. W. Miller, "Random number generators: good ones are hard to find", *CACM* **31**(10), 1192–1201, 1988

- DOI: <https://doi.org/10.1145/63039.63042> (ACM, paywalled). Access: not free;
  **not vendored.**
- Used for: the provenance of `a = 16807, m = 2^31 − 1` ("minstd") quoted in
  note 06, and the argument that 16807 is a primitive root mod `2^31 − 1` so the
  period is `m − 1`.

### S29 - T. E. Hull and A. R. Dobell, "Random Number Generators", *SIAM Review* **4**(3), 230–254, 1962

- DOI: <https://doi.org/10.1137/1004061> (SIAM, paywalled). Access: not free;
  **not vendored.**
- Used for: the full-period theorem quoted in note 06 - an LCG
  `x ← (ax + c) mod m` has period `m` for every seed iff `gcd(c, m) = 1`,
  `a ≡ 1 (mod p)` for every prime `p | m`, and `a ≡ 1 (mod 4)` if `4 | m`.
  **Now tested exhaustively** for all `(a, c)` with `m = 16` in
  `src/py/test_lattice.py`, which is a complete check of the theorem on a
  small modulus.

### S30 - G. E. P. Box and M. E. Muller, "A Note on the Generation of Random Normal Deviates", *Ann. Math. Statist.* **29**(2), 610–611, 1958

- URL: <https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-29/issue-2/A-Note-on-the-Generation-of-Random-Normal-Deviates/10.1214/aoms/1177706645.full>
- Retrieved: 2026-09-22. Access: free on Project Euclid. **Not vendored.**
- Used for: the transform and its derivation in note 06, cited to the two-page
  original.

### S31 - K. Goto and R. A. van de Geijn, "Anatomy of High-Performance Matrix Multiplication", *ACM TOMS* **34**(3), 2008

- URL: <https://www.cs.utexas.edu/users/flame/pubs/GotoTOMS_final.pdf>
- Retrieved: 2026-09-22. Access: free from the authors. **Not vendored.**
- Used for: note 02's blocking section - the two-level structure (a cache block
  copied into contiguous scratch memory, then a register micro-kernel), which is
  what real BLAS does and what S8 follows.

### S32 - J. R. Shewchuk, "Delaunay Refinement Algorithms for Triangular Mesh Generation", *Comput. Geom.* **22**(1–3), 21–74, 2002; and *Triangle*

- URLs: <https://people.eecs.berkeley.edu/~jrs/papers/2dj.pdf>,
  <https://www.cs.cmu.edu/~quake/triangle.html>
- Retrieved: 2026-09-22. Access: free from the author. **Not vendored.**
- Used for: note 09 - the empty-circumcircle (Delaunay) property, the
  max-min-angle optimality, constrained Delaunay, and Ruppert-style refinement
  with its guaranteed minimum angle (Shewchuk's variant reaches 20.7° with a
  proof and ~33° in practice).

### S33 - C. Geuzaine and J.-F. Remacle, "Gmsh: a three-dimensional finite element mesh generator with built-in pre- and post-processing facilities", *IJNME* **79**(11), 1309–1331, 2009

- URL: <https://gmsh.info/doc/preprints/gmsh_paper_preprint.pdf>
- Retrieved: 2026-09-22. Access: free preprint. **Not vendored.**
- Used for: note 09's list of generators and the mesh-size-field idea.

### S34 - The host machine (measured, not read)

- `sysctl`, `clang++ --version`, `cmake --version` on the machine the notes were
  written on, 2026-09-22.
- Used for: every machine-specific number in notes 01, 02 and 07. Recorded so
  they can be re-derived:
  - `machdep.cpu.brand_string = Apple M3 Pro`, `hw.model = Mac15,7`
  - `hw.ncpu = 12`; `hw.perflevel0.physicalcpu = 6` (performance),
    `hw.perflevel1.physicalcpu = 6` (efficiency)
  - **`hw.cachelinesize = 128`**
  - `hw.perflevel0.l1dcachesize = 131072` (128 KB, P-core),
    `hw.perflevel1.l1dcachesize = 65536` (64 KB, E-core)
  - `hw.perflevel0.l2cachesize = 16777216` (16 MB, P-cluster),
    `hw.perflevel1.l2cachesize = 4194304` (4 MB, E-cluster)
  - `hw.memsize = 38654705664` (36 GiB)
  - `Apple clang version 21.0.0 (clang-2100.1.1.101)`, target
    `arm64-apple-darwin25.6.0`
  - `cmake version 4.4.3`, which reports the toolchain's OpenMP as **5.1**
  and, via `cmake --system-information`, the default flags per build type
  (`Debug` = `-g`, `Release` = `-O3 -DNDEBUG`, `RelWithDebInfo` = `-O2 -g -DNDEBUG`,
  `MinSizeRel` = `-Os -DNDEBUG`), used in note 10.
- Access: run the commands yourself; no licence applies to a measurement.
  Reproduce with `sysctl -a | grep -E 'hw\.(cachelinesize|l1dcachesize|l2cachesize|memsize|ncpu|perflevel)'`,
  `clang++ --version`, `cmake --version`, `cmake --system-information`.
- This source **corrects note 01**: the DRAM row said "18 GB" and the L3 row
  claimed a 12 MB "L3 / system cache" that `sysctl` does not report at all.
- **Re-checked 2026-09-27**: every `sysctl` key above, `clang++ --version` and
  `cmake --version` return the same values (macOS 26.7, build 25G229), so the
  host is unchanged. What changed is the Python side: the repo moved on
  2026-09-26 and its venv was recreated on 2026-09-27 with `uv sync`: Python 3.12.13,
  numpy 2.5.3, scipy 1.18.1, pytest 9.1.1. The C++ tables in notes 01, 02, 05,
  07 and 08 were re-measured the same day; see
  `../notes/CHANGELOG.md`.

---

## Textbooks and documentation (cited where a primary source is silent)

### S35 - G. Hager and G. Wellein, *Introduction to High Performance Computing for Scientists and Engineers*, CRC Press 2010

- URL: <https://www.routledge.com/Introduction-to-High-Performance-Computing-for-Scientists-and-Engineers/Hager-Wellein/p/book/9781439811924>,
  DOI <https://doi.org/10.1201/EBK1439811924>; the authors' group page with
  related teaching material is <https://hpc.fau.de/>.
- ISBN 978-1-4398-1192-4. Retrieved (publisher page): 2026-09-22.
  Access: **not free**; **not vendored.**
- Used for: the benchmarking protocol in note 02 (minimum of repeated runs, warm
  up, consume the result, compare against a bound), the false-sharing and
  ccNUMA/first-touch material in note 07, and the "balance" view of memory-bound
  kernels. Named in [`../notes/README.md`](../notes/README.md) as the standard
  companion for topics 1, 2 and 7 - with the caveat that **TISS names no
  literature at all** [S1], so this is our choice, not the course's.

### S36 - CMake documentation, Kitware ★

- URL: <https://cmake.org/cmake/help/latest/>; specifically
  `cmake_minimum_required`, `project`, `CMAKE_CXX_STANDARD`,
  `CMAKE_CXX_STANDARD_REQUIRED`, `find_package`, `FindOpenMP`, `add_test`,
  `CMAKE_BUILD_TYPE`, and the `<PackageName>_ROOT` search rule.
- Retrieved: 2026-09-22. Access: public. CMake is BSD-3-Clause;
  **not vendored** (a live, versioned site).
- Used for: rewriting note 10's CMake section. The previous text was written
  with **no CMake installed** (it said so). CMake 4.4.3 was installed and the
  snippet was run: see `../notes/CHANGELOG.md` for the two defects it exposed,
  and `../src/cpp/CMakeLists.txt` for the corrected, executed version.

### S37 - Clang / LLVM documentation

- URLs: <https://clang.llvm.org/docs/UsersManual.html>,
  <https://clang.llvm.org/docs/DiagnosticsReference.html>,
  <https://clang.llvm.org/docs/AddressSanitizer.html>,
  <https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html>,
  <https://clang.llvm.org/docs/ThreadSanitizer.html>
- Retrieved: 2026-09-22. Access: public. Apache-2.0-with-LLVM-exception;
  **not vendored.**
- Used for: note 02's flag table (`-O0…-O3`, `-march=native`/`-mcpu=native`,
  `-ffast-math` and what it actually licenses, `-funroll-loops`, `-flto`,
  `-Rpass=loop-vectorize`) and note 10's sanitizer list and slowdown figures.

### S38 - K. Serebryany, D. Bruening, A. Potapenko, D. Vyukov, "AddressSanitizer: A Fast Address Sanity Checker", *USENIX ATC*, 2012

- URL: <https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf>
- Retrieved: 2026-09-22. Access: public. **Not vendored.**
- Used for: the bug classes ASan detects and its ~2× slowdown, quoted in
  note 10, and the explicit list of what it does **not** find.

### S39 - pybind11 documentation

- URL: <https://pybind11.readthedocs.io/en/stable/>
- Retrieved: 2026-09-22. Access: public. BSD-3-Clause; **not vendored.**
- Used for: the `PYBIND11_MODULE` / `py::array_t` example in note 10, the build
  line, and the GIL note.

### S40 - *Pro Git*, S. Chacon and B. Straub, 2nd ed.

- URL: <https://git-scm.com/book/en/v2>
- Retrieved: 2026-09-22. Access: public. Licence: CC BY-NC-SA 3.0 - commercial
  redistribution is excluded, so **not vendored** (the study-repo licence is
  not established).
- Used for: note 10's git section - branch/merge/rebase semantics and the rule
  not to rebase published history.

### S41 - SPDX License List and the OSI licence texts

- URLs: <https://spdx.org/licenses/>, <https://opensource.org/licenses>
- Retrieved: 2026-09-22. Access: public. **Not vendored.**
- Used for: note 10's licence table, checked term by term against the actual
  texts (MIT, BSD-2/3, Apache-2.0's patent grant and change-statement
  requirement, GPL-2.0/3.0 copyleft-on-distribution, LGPL's linking exception,
  MPL-2.0's file-level scope) and for the SPDX identifiers used in this
  register.

### S42 - Wikipedia, Apple silicon

- URL: <https://en.wikipedia.org/wiki/Apple_silicon>
- Retrieved: 2026-09-22. Access: public, CC BY-SA 4.0 (redistributable with
  attribution and share-alike; **not vendored** because nothing here depends on
  it).
- Used for **one thing only**, and it is a remark about source quality rather
  than a fact: [S8] takes its Apple-silicon cache figures "From Wikipedia", and
  note 01 points that out as the reason its own table is read from `sysctl`
  [S34] instead. Cited in [`../notes/01-computer-architectures.md`](../notes/01-computer-architectures.md).

---

## Substitute practice sources

**Why this section exists.** This course has no public past paper and no public
exercise sheet [S1] [S4], so there is no model answer to work from and nothing
to practise on. The sources below are **substitutes**: free, licence-clear
teaching material for the *same subject* from elsewhere, used to build the
practice set in [`../notes/11-practice-set.md`](../notes/11-practice-set.md) and
the solutions in [`../src/exercises/`](../src/exercises/README.md).

**The rule they are used under.** Nothing from them is presented as 360.242
material. Every exercise directory names its institution, course, year, licence
and retrieval date in its first table, and every solution file repeats it in its
header. Exercise texts are **restated in our words** and cited to chapter and
section; **nothing new is vendored**, even where the licence would permit it.

**[S8] and [S9] are the first of these sources and are already registered
above.** Schöberl's *Introduction to Scientific Computing* (LGPL-2.1) and its
code companion ASC-HPC (MIT) outrank every external substitute for one reason:
he is one of the five 2026W lecturers of 360.242 [S1] [S10]. His own exercises -
the CAS lock and the `RunParallel` matmul scaling study at the end of
*Performance → Parallelization* - are solved in
`../src/exercises/tuwien-introsc-2025/`.
His course is nevertheless a **different** course: it teaches finite elements,
not finite differences, and nothing in it is evidence about the 360.242 exam
*format*.

### S43 - V. Eijkhout, *The Art of HPC*, volume 1: *Introduction to High-Performance Scientific Computing* ★

- Author: Victor Eijkhout, Texas Advanced Computing Center, The University of
  Texas at Austin. Book © 2012–2022; the 2022 public source repository was used.
- URLs: <https://theartofhpc.com/> (series),
  <https://github.com/VictorEijkhout/TheArtOfHPC_vol1_scientificcomputing>
  (source, cloned 2026-09-22)
- Retrieved: 2026-09-22. Access: public, no login.
- **Licence: CC BY 4.0.** `booksources/copyright.tex` reads *"distributed under
  a Creative Commons Attribution 4.0 Unported (CC BY 4.0) license"*, and
  `README.md` repeats *"All material is released under a CC-By 4.0 license."*
  The repository's own `LICENSE` file is MIT (© 2022 Victor Eijkhout) and covers
  the sources and code. **Not vendored** - CC BY 4.0 would permit it, but the
  exercises are restated rather than copied so that nothing here can be mistaken
  for the original.
- **Why it is comparable.** Its chapter 1, *Single-processor Computing*, is
  360.242's topics 1 and 2 in the same order and at the same level: memory
  hierarchies, cache lines, direct-mapped and associative caches, TLB, prefetch,
  memory banks, multicore, false sharing, NUMA, locality, arithmetic intensity
  and the roofline model. Chapter 4, *Numerical treatment of differential
  equations*, is topic 4 (IVPs, BVPs, 1D/2D Poisson, the heat equation and its
  stability limit). Chapter 5, *Numerical linear algebra*, is topic 5 (sparse
  storage, stationary iteration, CG). Chapter 2 covers topic 7's shared-memory
  half. It is also, unusually, a book of **exercises with checkable answers**
  rather than programming projects - the format a 3-hour written exam uses.
- **Scope differences.** Roughly half of [S43] is distributed memory, MPI,
  network topology, GPUs, cloud, Top500 and power - none of which is on this
  topic list [S1]. Conversely it has **nothing** on mesh generation or
  visualisation (topic 9; the words do not occur in the book) and nothing on
  software engineering (topic 10, which lives in another volume of the series).
  Its Monte Carlo chapter has no exercises, so topic 6 drew nothing from it.
- Used for: [`../src/exercises/utaustin-theartofhpc-2022/cache_sim.py`](../src/exercises/utaustin-theartofhpc-2022/cache_sim.py)
  (the direct-mapped conflict exercise, the k-way associativity simulation, and
  the tree-vs-linear summation locality exercise) and for problems P1, P2, P3,
  P5, P6, P8, P10, P11, P12 and P18 of the practice note.

### S44 - D. Bindel, Cornell CS 5220 *Applications of Parallel Computers*, Fall 2015

- Institution: Cornell University, Department of Computer Science. Instructor:
  David Bindel. Offering: **Fall 2015**.
- URLs: course site source
  <https://github.com/cornell-cs5220-f15/cornell-cs5220-f15.github.io>,
  HW3 (all-pairs shortest paths) <https://github.com/cornell-cs5220-f15/path>,
  organisation <https://github.com/cornell-cs5220-f15>
- Retrieved: 2026-09-22 (both repositories cloned). Access: public, no login.
- **Licence: MIT**, © 2015 David Bindel - `LICENSE.md` in the site repository and
  in the `path`, `water` and `lecture` repositories alike. (`matmul-`, the HW1
  repository, carries **no licence**, so nothing was taken from it.)
  **Not vendored**: the MIT licence would permit it, but the assignment is
  restated and the solution is ours.
- **Why it is comparable.** CS 5220's first half is 360.242's performance half -
  single-core architecture and tuning, shared-memory parallelism, and a required
  *performance model that predicts the speedup*, which is the same verb as this
  course's learning outcome *"judge the challenges regarding computing time"*
  [S1]. HW3 in particular puts algorithmic complexity (topic 8) and memory
  access pattern (topics 2, 7) on the table at once: $O(n^3)$ Floyd–Warshall
  against $O(n^3 \log n)$ repeated squaring in the $(\min,+)$ semiring, the
  slower algorithm being chosen for its parallel shape.
- **Scope differences.** HW3's second task is explicitly MPI, and the 2015 class
  ran on Xeon Phi accelerators; neither distributed memory nor accelerators is
  on this topic list [S1] - E360 teaches those in separate courses [S7]. CS 5220
  is assessed by project reports, 360.242 by a 3-hour written exam [S1], so the
  *deliverable* does not transfer even though the analysis does. It has nothing
  on random numbers (topic 6) or mesh generation (topic 9).
- Used for: [`../src/exercises/cornell-cs5220-2015/minplus_path.py`](../src/exercises/cornell-cs5220-2015/minplus_path.py)
  and problems P7, P19 and P20 of the practice note.

### Substitute sources considered and rejected

- **MIT 18.335 *Introduction to Numerical Methods* (S. G. Johnson).** The
  problem sets are public at <https://github.com/mitmath/18335>, but the
  repository carries **no licence file** (GitHub API reports `"license": null`),
  so it is all rights reserved and nothing may be copied or adapted from it.
  It is also the wrong half of this syllabus: 18.335 is floating point, dense
  factorisations, Krylov methods and eigenvalue algorithms at a depth 360.242
  does not reach, and it has no architecture, parallelism, mesh or software
  engineering content. Not used, and no problem in the practice note derives
  from it.
- **Cornell CS 5220 HW1 (`matmul-`).** No licence file. Also redundant - the
  blocked-matmul study already exists in
  [`../src/cpp/matmul_opt.cpp`](../src/cpp/matmul_opt.cpp). Not used.
- **Anything for topic 9 (Mesh Generation and Visualisation).** No free,
  licence-clear *exercise set* was found. What exists is normative
  documentation - the legacy VTK format [S12] [S13] and Shewchuk's Delaunay
  paper [S32] - which the notes already follow and
  [`../src/py/vtk_check.py`](../src/py/vtk_check.py) already tests. The practice
  note's topic-9 problems are therefore **ours**, written against the
  specification, and are marked as such.

---


## Sources deliberately not used

- **TUWEL** (`tuwel.tuwien.ac.at`). The TISS page says the TUWEL course opens
  05.10.2026 [S1]. Slides, exercise sheets and hand-in specifications live
  there. It requires a TU Wien login and its contents are not ours to
  redistribute. **Not fetched.**
- **The course Mattermost channel** `numerical-simulation-and-scientific-computing-i`
  (linked from S4): requires registration. Not joined.
- **Student assignment repositories.** A GitHub repository search for
  `"Numerical Simulation and Scientific Computing" TU Wien` returns exactly one
  repository, `tellocam/NSSC2` - the **sibling** course 360.243, last pushed
  2022, and it contains the assignment PDFs themselves. Reproducing a hand-in
  specification is not ours to do and the material is for the other course, so
  it was not used. Recorded here so the next reader does not repeat the search.
- **TISS course-materials page** for older offerings: redirects to the TU Wien
  IdP. Not followed.
- **MIT 18.335 problem sets** and **Cornell CS 5220 HW1**: unlicensed
  repositories. See "Substitute sources considered and rejected" above.
