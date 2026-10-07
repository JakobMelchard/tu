# Sources — 057.020 ASC-School I Courses in High Performance Computing

Register of every source used to write and verify `../notes` and `../src`.
Notes cite these as `[S<n>]`. Retrieval dates are the day the page or file was
fetched; TISS pages, Indico event pages and the ASC documentation change, so
re-check before you rely on a number.

**Vendoring policy.** Five third-party files are in `vendor/` and are
**committed**, because each carries an explicit redistribution grant (MPI Forum
copy permission; CC BY-SA 4.0). Everything else is cited only: live web pages,
PDFs with a copyright line and no grant, and one deck (**S12**, the HLRS MPI
course) whose owner explicitly forbids redistribution. See
[`README.md`](README.md) for the file-by-file licence table and
[`fetch-sources.sh`](fetch-sources.sh) to pull the cite-only PDFs onto your own
machine. **No TUWEL material was fetched** — this course has no TUWEL presence
anyway; the hands-on material lives on a public GitLab and on Indico. (The
"no TUWEL presence" statement was inferred on 2026-09-22 from the public TISS
and ASC pages, not from a TUWEL login.)


**Semester.** The course is offered in winter semesters. The 2027W TISS page does not
exist yet, so S1 is still the 2026W page. S25 records the ASC training
catalogue as it stood on 2026-09-28.

**No cluster was logged into.** Every ASC/VSC fact below comes from a public
page, a public slide deck or the public documentation. Nothing was measured on
VSC-4, VSC-5 or MUSICA, and no job was submitted.

---

## Course-authoritative

### S1 — TISS course page, 2026W (latest published instance)

- Title: 057.020 ASC-School I Courses in High Performance Computing, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=057020&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript)
- Access: public, no login
- Used for: scope (three blocks, learning outcomes, subject of course, teaching
  methods), ECTS (1.5), type (VU, 2.0 h, hybrid, blocked), lecturer
  (Blaas-Schenner), institute (E057-09), examination modalities, registration
  modalities, previous knowledge, `Attendance Required!`, and the statement
  **"No lecture notes are available."** under *Literature*.
  **The 2026W page carries no course dates** as of the retrieval date.
  Diffed against [`../docs/tiss.md`](../docs/tiss.md); see
  `../notes/CHANGELOG.md`.

### S2 — TISS course page, 2025W (previous offering) ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=057020&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the year-on-year diff and, crucially, **the block dates that the
  2026W page lacks**:
  - Wed 09:00–16:00, 08.10.2025, online via Zoom — *Linux command line
    (participation is required for Linux newbies only)*
  - Wed 09:00–17:00, 15.10.2025, online via Zoom — *Introduction to Working on
    the ASC Clusters (1 day — either 15.10.2025 or in January 2026)*
  - 09:00–13:30, 17.11.2025 – 20.11.2025, **Seminar room BA 10A (10th floor),
    TU Wien, Getreidemarkt 9, 1060 Wien OR online via Zoom (hybrid)** —
    *Parallelization with MPI (4 morning sessions)*

  Everything else (ECTS, lecturer, outcomes, subject, exam modalities) is
  byte-identical to S1.

### S3 — TISS course page, 2024W (two offerings back) ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=057020&semester=2024W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the **rename**. In 2024W the course is titled *057.020
  **VSC**-School I Courses in High Performance Computing*, and every occurrence
  of "ASC" on the 2025W/2026W pages reads "VSC" here: *Introduction to Working
  on the **VSC** Clusters*, "login to the **VSC** Systems", registration at
  `https://vsc.ac.at/training`, contact `training@vsc.ac.at`. The rename to ASC
  happened between 2024W and 2025W. Content otherwise identical.
  2024W dates: Linux 09.10.2024; VSC-Clusters intro 24.10.2024 **or**
  16.01.2025; MPI 18.11.2024 – 21.11.2024, 09:30–14:00, Seminar room 2/2,
  Operngasse 11 or online.
  Earlier offerings exist back to 2019W (semester selector on the page).

### S4 — ASC training portal

- URL: <https://asc.ac.at/training> and <https://asc.ac.at/>
- Retrieved: 2026-09-22. Access: public.
- Used for: the identity **ASC = Austrian Scientific Computing** (footer:
  "© ASC - Austrian Scientific Computing"); that ECTS for this course are
  obtained by registering for the individual training events and mailing
  `training@asc.ac.at`; that students from other Austrian universities need a
  co-registration at TU Wien; and the sibling lecture 057.021 (ASC-School II,
  "participation in at least 18 hours is required"). The page still calls the
  lectures "VSC-School I / II" and its *"Lectures in the current semester"*
  block was last updated for **2025S** — it is stale, so the Indico calendar
  (S5) is the reliable schedule.
- **Re-checked 2026-09-28.** Unchanged: the *"Lectures in the current
  semester"* block still names 2025S (057.021 and 057.033 only), the ECTS
  paragraph is the same, and *"Upcoming training events"* is only a link, via
  `https://asc.ac.at/training/training-events/`, to the Indico category S5.
  The page states no minimum number of training days for either School.
- **Broken link, worth knowing:** TISS's *Course homepage* field for 057.020
  (2026W) is `https://vsc.ac.at/training`. The apex domain `vsc.ac.at` has no
  A record any more (only MX); `www.vsc.ac.at`, `docs.vsc.ac.at` and
  `events.vsc.ac.at` are CNAMEs to the `asc.ac.at` equivalents. Use
  `https://asc.ac.at/training`. Re-checked 2026-09-28: `vsc.ac.at` still has
  no A record (fetch fails with `ENOTFOUND`), and `https://www.vsc.ac.at/training`
  answers `302` to `https://asc.ac.at/training`.

### S5 — ASC/EuroCC Indico event calendar ★

- URL: <https://events.asc.ac.at/category/4/> ("Trainings"); machine-readable
  export used: `https://events.asc.ac.at/export/categ/4.json?limit=400&from=…&to=…`
- Retrieved: 2026-09-22. Access: public, no login.
- Used for: **the real schedule of the three blocks**, every offering
  2023-10 → 2026-09, and for the finding that recorded in
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): **as of 2026-09-22
  no 2026W instance of any of the three blocks is announced.** The pattern of
  the previous three years is Linux Command Line in the first half of October,
  Introduction to Working on the ASC Clusters mid-October with a January repeat,
  and Parallelization with MPI over four mornings in mid-November.
  Relevant events (title | dates | event id):
  - Linux Command Line | 03.10.2023, 07.03.2024, 09.10.2024, 10.03.2025,
    08.10.2025, 02.03.2026 | 102, 124, 155, 181, 206, 260
  - Introduction to Working on the VSC/ASC Clusters | 12.10.2023, 16.01.2024,
    14.03.2024, 20.06.2024, 24.10.2024, 16.01.2025, 13.03.2025, 15.10.2025,
    23.03.2026 | 103, 112, 125, 131, 156, 161, 182, 191, 275
  - Parallelization with MPI (4 days) | 06.–09.11.2023, 15.–18.04.2024,
    18.–21.11.2024, 17.–20.11.2025 | 107, 128, 158, 213
  - Parallelization with MPI split into *(Beginner)* + *(Intermediate–Advanced)*
    2-day events since 2025: 28.–29.04.2025 / 05.–06.05.2025, and
    09.–10.07.2026 / 16.–17.07.2026 | 183, 184, 316, 317
- The state of the calendar from 2026-09-28 onwards is S25.

### S6 — Indico: *Linux Command Line*, 8 October 2025 (event 206) ★

- URLs: overview <https://events.asc.ac.at/event/206/>,
  agenda <https://events.asc.ac.at/event/206/page/587-agenda-content>,
  material <https://events.asc.ac.at/event/206/page/588-course-material>,
  pre-assignment <https://events.asc.ac.at/event/206/page/589-login-pre-assignment>
- Retrieved: 2026-09-22. Access: public.
- Used for: **block 1 as actually taught** — one day, 09:00–16:00, four
  lecture/exercise/demo/break cycles, lunch 12:00–13:00, syllabus line
  *"Linux primer: command-line basics, editors, environment variables, .bashrc
  file"*; lecturers **Luis Casillas Trujillo** and **Atul Singh** (ASC Research
  Center, TU Wien) — *not* Blaas-Schenner, who is the TISS lecturer of record;
  that every participant gets a temporary `trainee##` account on **vsc5**;
  the pre-assignment (log in before the course); the login recipes and hosts in
  note 03; the Windows recommendation (PuTTY + FileZilla/WinSCP); the no-show
  blacklist policy. The material page links S7.

### S7 — ASC *Linux Primer* slides ★ (vendored)

- Authors: ASC Research Center, TU Wien. Title on the deck: *Linux Intro*.
- URL: <https://gitlab.tuwien.ac.at/vsc-public/training/linux-primer>
  (`linux_primer.md`, `linux_primer.pdf`, `vsc_linux_intro.sh`, `readme.md`)
- Retrieved: 2026-09-22; upstream last activity 2026-03-02 (the deck's own
  `date:` line reads "March 2, 2026").
- **Licence: CC BY-SA 4.0** (`license` file in the repository root).
  **Vendored** as [`vendor/asc-linux-primer.md`](vendor/asc-linux-primer.md),
  byte-identical.
- Used for: **everything in notes 01–03**. It fixes which commands the course
  actually teaches and in what order (terminal & prompt, execution, history,
  completion, flags, order, filesystem, path, navigation, file operations, I/O
  redirection, `scp`/`rsync`/FileZilla/WinSCP, `find`/`grep`/wildcards,
  ownership and permissions, `du`/`df`, pipes, `sed`/`awk`, escapes and quotes,
  variables, environment variables, `top`, editors nano/vim/emacs, scripting,
  shebang, loops, expansion, if/else, case, functions, `man`, alias, `.bashrc`),
  the four exercise sets, and the fact that the prompt on VSC-5 looks like
  `zen trainee00@l55:~$` — the first field is the **software environment**
  (`skylake`, `zen`, `cuda-zen`), not a hostname.

### S8 — Indico: *Introduction to Working on the ASC Clusters* (events 191 and 275) ★

- URLs: <https://events.asc.ac.at/event/191/> (15.10.2025) and
  <https://events.asc.ac.at/event/275/> (23.03.2026), each with
  `page/…-agenda-content` and `page/…-course-material`
- Retrieved: 2026-09-22. Access: public.
- Used for: **block 2 as actually taught** — one day, 09:00–17:00, running
  order *welcome → ASC intro & login → file storage → modules → Spack → EESSI →
  Conda → Slurm (basics) → Slurm (advanced) → GPUs → wrap-up*, then individual
  support 15:30–17:00. Both pages mark **Compiling** and **Singularity** as
  *OUTDATED* and drop them from the running order. The slide PDFs (S9) are
  linked from these pages.

### S9 — Blaas-Schenner *et al.*, ASC-Intro slide decks, March 2026 ★

- Author: Claudia Blaas-Schenner, ASC Research Center, TU Wien (the `gpus` and
  `slurm_advanced` decks are undated/unattributed but distributed with the rest).
- URLs (all under `https://events.asc.ac.at/event/…/attachments/…`):
  - `asc_intro+login.pdf` — <https://events.asc.ac.at/event/275/attachments/270/815/asc_intro+login.pdf>
  - `slurm_basics.pdf` — <https://events.asc.ac.at/event/275/attachments/270/816/slurm_basics.pdf>
  - `slurm_advanced.pdf` — <https://events.asc.ac.at/event/275/attachments/270/813/slurm_advanced.pdf>
  - `gpus.pdf` — <https://events.asc.ac.at/event/275/attachments/270/812/gpus.pdf>
  - `file_storage.pdf` — <https://events.asc.ac.at/event/191/attachments/179/639/file_storage.pdf>
- Retrieved: 2026-09-22. Access: **public download, no login**.
  **Licence: none stated ⇒ all rights reserved. Not vendored**; fetch with
  [`fetch-sources.sh`](fetch-sources.sh).
- Used for: **almost every ASC/VSC-specific fact in notes 04, 05 and 06** —
  the system generations and their TOP500 placings, node counts and CPU/memory
  configurations, the login-node ranges, the 2-level fat-tree sketch, the
  latency/bandwidth ladder, the Amdahl slide (with the **sequential**-fraction
  convention), the partition/QoS names, the requirement to give **both**
  `--qos` and `--partition`, the VSC-4 and VSC-5 quickstart job scripts,
  `sqos`, the array-job and single-node-multiple-jobs patterns, pinning with
  `srun --cpu-bind=map_cpu:` and `I_MPI_PIN_PROCESSOR_LIST`, the 72 h hard
  limit and backfilling, the `--reservation=training` alias used during the
  course, and the GPU table. Figures in these decks are credited by the author
  to Rolf Rabenseifner (HLRS) and Georg Hager (RRZE/NHR@FAU).

### S10 — ASC *vsc-intro* slide sources ★ (partly vendored)

- Authors: VSC/ASC team; `compiling.md` names **Jan Zabloudil, Moritz Siegel**.
- URL: <https://gitlab.tuwien.ac.at/vsc-public/training/vsc-intro>
- Retrieved: 2026-09-22; upstream last activity 2025-10-14.
- **Licence: CC BY-SA 4.0** (`license` file in the repository root).
  **Vendored**: `modules/modules.md`, `compiling/compiling.md`,
  `file_storage/file_storage.md` → `vendor/`, byte-identical.
  Not vendored: `conda/`, `eessi/`, `spack/`, `singularity/` (same licence,
  simply out of scope for these notes).
- Used for: note 05 in full (the module system is **Environment Modules**, not
  Lmod), the compiler/MPI-wrapper tables in note 05, the partition lists per CPU
  architecture, and the `$HOME`/`$DATA`/`/local`/`/tmp` quota figures in note 04.
  Note that `compiling.md` is the deck the course now marks *OUTDATED* [S8]:
  its module hashes are from Spack 0.19 and will not resolve today. It is cited
  for the **shape** of the commands, never for a literal version string.

### S11 — ASC MPI hands-on repository (Jupyter notebooks + tasks) ★

- Author: **Claudia Blaas-Schenner** (ASC Research Center, TU Wien) — the
  lecturer of record for 057.020.
- URL: <https://gitlab.tuwien.ac.at/vsc-public/training/mpi>
  (`git clone https://gitlab.tuwien.ac.at/vsc-public/training/MPI`)
- Retrieved: 2026-09-22; upstream last activity 2025-11-14 (i.e. during the
  November 2025 block).
- **Licence: CC BY-SA 4.0** *for the notebooks*, stated in `README.md`, **but**
  the same file states that the repository is based on Rabenseifner's HLRS
  course and that "some images, some exercise descriptions, some code snippets"
  are HLRS-copyrighted and "used with permission" — permission granted to the
  author, not obviously sublicensable. **Not vendored** for that reason;
  `fetch-sources.sh` clones it instead. This is a deliberate, conservative call
  and is recorded in [`README.md`](README.md).
- Used for: the **exact hands-on sequence of block 3**, which is the backbone of
  notes 07–16 and of `../src/exercises/2025w-mpi/`:
  `01_hello`, `02_pingpong`, `03_ring`, `04_allreduce`, `05_comm-split`,
  `06_virtual_cartesian_topologies`, `07_derived-datatypes`, `08_1sided`,
  `09_1sided-shmem`, in C, Fortran and Python (mpi4py). Also for the
  observation that the course's running example is one and the same **ring sum**
  re-implemented with every mechanism, whose answer is always
  $\sum_{r=0}^{P-1} r = P(P-1)/2$.

### S12 — Rabenseifner, *MPI course* slides, HLRS Stuttgart

- Author: Rolf Rabenseifner, HLRS, University of Stuttgart.
- URLs: <https://fs.hlrs.de/projects/par/par_prog_ws/pdf/mpi_3.1_rab.pdf>
  (13.7 MB) and the animated variant `mpi_3.1_rab-animated.pdf`; exercise
  archives `MPI31single.tar.gz` / `.zip` and `TEST.tar.gz` under
  <https://fs.hlrs.de/projects/par/par_prog_ws/practical/> and
  <https://fs.hlrs.de/projects/par/events/>; landing page
  <https://www.hlrs.de/training/self-study-materials/mpi-course-material>
- Retrieved (headers only): 2026-09-22. Access: public download, no login.
- **Licence: explicitly cite-only.** The ASC course-material page [S13] states:
  *"You may download the slides and exercises for your personal use and pass on
  the link above. Any other form of public distribution of the provided pdf
  files themselves or any derived material is not allowed, except with written
  permission by HLRS."* **Not vendored, not quoted, not paraphrased at slide
  granularity.** `fetch-sources.sh` downloads it for personal use.
- Used for: knowing **what the block-3 slide deck is** and that the ASC course
  runs on it with chapter-level slide-number references [S13]. Every technical
  claim attributed to the deck in these notes is re-derived from the MPI
  standard [S15] instead.

### S13 — Indico: *Parallelization with MPI*, 17–20 November 2025 (event 213) ★

- URLs: <https://events.asc.ac.at/event/213/>,
  agenda <https://events.asc.ac.at/event/213/page/599-agenda-content>,
  material <https://events.asc.ac.at/event/213/page/600-course-material>,
  pre-assignment <https://events.asc.ac.at/event/213/page/601-login-pre-assignment>
- Retrieved: 2026-09-22. Access: public.
- Used for: **the lecture order of block 3**, which notes 07–16 now follow:

  | day | 09:00 | 10:45 | 12:15 | 13:00 |
  |---|---|---|---|---|
  | 1 | Welcome; MPI overview | Process model and language bindings | Messages and point-to-point communication | — |
  | 2 | Ping-pong benchmark — solution and results; Nonblocking communication | Collective communication | Optimizing MPI communication — a real world example; Short tour: other MPI topics | Fortran and MPI |
  | 3 | Groups & communicators | Virtual topologies (10:15) | Derived datatypes | — |
  | 4 | One-sided communication | Shared memory one-sided communication | Short tour: MPI I/O; Best practice, Summary, Q&A | — |

  Also for: the course tracks **MPI 5.0** (the "standard document" link on that
  page is the MPI-5.0 report [S15]); `mpi4py` is an equally supported language
  binding; the hands-on labs run on the **ASC JupyterHub** with a fallback to
  plain terminals; the HLRS copyright statement quoted under S12; and the
  student feedback route (TISS survey for 057.020).

### S14 — Blaas-Schenner, *Best Practice for Code Parallelization* and *MPI I/O* decks ★

- Author: Claudia Blaas-Schenner, VSC Research Center, TU Wien.
- URLs: <https://asc.ac.at/fileadmin/user_upload/vsc/online-courses/MPI/mpi_bp_cb.pdf>
  and <https://asc.ac.at/fileadmin/user_upload/vsc/online-courses/MPI/mpi_io_cb.pdf>
  (the course-material page [S13] still links the `vsc.ac.at` hostnames, which
  no longer resolve — substitute `asc.ac.at`)
- Retrieved: 2026-09-22. Access: public download.
  **Licence: none stated ⇒ all rights reserved. Not vendored.**
- Used for: the two **reference results** reproduced in notes 08 and 16 —
  (a) the measured ping-pong latency ladder on VSC-3 (`MPI_Send`, Intel MPI /
  Open MPI, µs): intra-socket 0.3, inter-socket 0.6–0.7, InfiniBand edge
  1.2–1.5, leaf 1.6–1.9, spine 2.1–2.4, with `MPI_Ssend` costing 1.2–1.3 µs
  intra-socket and up to 14–18 µs over Open MPI on the fabric; and (b) the
  "real world example" optimisation ladder (a Fortran code, problem sizes 6×6
  and 8×8): original 1500 s / 21 000 s → remove the barriers 960 s / 3500 s →
  correct nonblocking 425 s / 960 s → replace the send loop by `MPI_Bcast`
  420 s / 1025 s. Also for the rule she puts in capitals: **never use
  `MPI_BARRIER` in production code**, and for "aggregate communication into
  longer messages" and Foster's design methodology.

---

## Standards and specifications

### S15 — MPI Forum, *MPI: A Message-Passing Interface Standard*, Version 5.0 (5 June 2025) ★ (vendored)

- URL: <https://www.mpi-forum.org/docs/mpi-5.0/mpi50-report.pdf>;
  landing <https://www.mpi-forum.org/docs/>
- Retrieved: 2026-09-22. 6 012 433 bytes,
  `sha256 2d4e6ae09ed04cf5eaf1bda2716d5a1023e282d78f577aa84538a89623c18051`.
- **Licence: redistributable.** Page ii: *"©1993 … 2025 University of Tennessee,
  Knoxville, Tennessee. Permission to copy without fee all or part of this
  material is granted, provided the University of Tennessee copyright notice and
  the title of this document appear, and notice is given that copying is by
  permission of the University of Tennessee."*
  **Vendored** as [`vendor/mpi-5.0-standard.pdf`](vendor/mpi-5.0-standard.pdf).
- Used for: **the normative statement of every MPI routine, argument,
  completion semantics, matching rule and assertion in notes 07–16**, including
  the communication modes (standard / buffered / synchronous / ready), the
  non-overtaking rule, `MPI_PROC_NULL`, `MPI_IN_PLACE`, `MPI_Comm_split`,
  `MPI_Cart_create`/`_shift`/`_coords`/`_rank`, derived-datatype constructors
  and `MPI_Type_create_resized`, the RMA window models and `MPI_Win_fence`
  assertions, `MPI_Comm_split_type(MPI_COMM_TYPE_SHARED)` and
  `MPI_Win_allocate_shared` (+ `MPI_Win_shared_query`), the thread levels, and
  `MPI_File_*` with the four data-access families. The version history on
  page i is the source for the release dates quoted in note 07.

### S16 — Slurm documentation, SchedMD

- URLs: <https://slurm.schedmd.com/documentation.html>,
  `sbatch.html`, `srun.html`, `salloc.html`, `squeue.html`, `sacct.html`,
  `scontrol.html`, `sinfo.html`, `job_array.html`, `sched_config.html`
- Retrieved: 2026-09-22. Access: public. Slurm itself is GPL-2.0; the manual
  pages are freely readable and freely citable, and are better read online than
  pinned, so **not vendored**.
- Used for: the meaning of every `#SBATCH` option, of `SLURM_*` variables, of
  job states and exit codes, of dependency types, and of backfill scheduling in
  note 06 — everything that is Slurm behaviour rather than ASC policy.

### S17 — Environment Modules, `modules.sourceforge.net`

- URLs: <http://modules.sourceforge.net/> (the URL the ASC slides give) →
  <https://modules.readthedocs.io/en/latest/>; `module(1)` man page.
- Retrieved: 2026-09-22. Access: public. Environment Modules is GPL-2.0-or-later;
  documentation cited, not vendored.
- Used for: the correction at the head of note 05. The ASC systems run **Tcl
  Environment Modules** (`module-whatis`, `prepend-path`, `module load --auto`,
  `MODULES_AUTO_HANDLING`) — all Environment Modules 4.x/5.x features — and
  **not Lmod**, so `ml`, `module spider`, `module keyword`, `module save` and
  the Lmod compiler/MPI *hierarchy* do not apply. Cross-checked against S10 and
  S19.

### S18 — Lmod documentation, TACC

- URL: <https://lmod.readthedocs.io/>
- Retrieved: 2026-09-22. Access: public; Lmod is MIT-licensed, docs cited only.
- Used for: stating *what the notes previously assumed* and why it is wrong
  here — the hierarchical MODULEPATH, `module spider`, `ml`, `(D)` default
  markers. Kept in note 05 as a clearly-labelled contrast, because most other
  HPC sites (and the sibling course's reading) do run Lmod.

---

## ASC / VSC user documentation

### S19 — ASC User Documentation ★

- URL: <https://docs.asc.ac.at/> (= <https://docs.vsc.ac.at/>, a CNAME).
  Pages used: `running_jobs/vsc4_queues.html`, `running_jobs/vsc5_queues.html`,
  `running_jobs/submit_jobs.html`, `running_jobs/monitoring_jobs.html`,
  `running_jobs/array_jobs.html`, `running_jobs/gpus.html`,
  `software/modules.html`, `storage/*`, `login/*`, `first_steps/hpc_intro.html`.
- Source repository: <https://gitlab.tuwien.ac.at/vsc-public/documentation>
  (public, **no LICENSE file ⇒ all rights reserved**). **Not vendored.**
- Retrieved: 2026-09-22. Access: public, no login.
- Used for: **the authoritative, current partition and QoS tables** that the
  notes and the job templates now carry, in preference to the March-2026 slides
  where the two differ:

  | VSC-4 partition | nodes | CPU | cores/CPU (phys/HT) | RAM |
  |---|---|---|---|---|
  | `skylake_0096` (default) | 698 | 2× Xeon Platinum 8174 | 24/48 | 96 GB |
  | `skylake_0384` | 78 | 2× Xeon Platinum 8174 | 24/48 | 384 GB |
  | `skylake_0768` | 12 | 2× Xeon Platinum 8174 | 24/48 | 768 GB |

  | VSC-5 partition | nodes | CPU | cores/CPU (phys/HT) | GPU | RAM |
  |---|---|---|---|---|---|
  | `zen3_0512` (default) | 638 | 2× AMD EPYC 7713 | 64/128 | — | 512 GB |
  | `zen3_1024` | 136 | 2× AMD EPYC 7713 | 64/128 | — | 1 TB |
  | `zen3_2048` | 20 | 2× AMD EPYC 7713 | 64/128 | — | 2 TB |
  | `zen2_0256_a40x2` | 45 | 2× AMD EPYC 7252 | 8/16 | 2× NVIDIA A40 | 256 GB |
  | `zen3_0512_a100x2` | 61 | 2× AMD EPYC 7713 | 64/128 | 2× NVIDIA A100 | 512 GB |

  plus: default run-time limit **24 h**, hard limit **72 h** on every normal
  QoS; `*_devel` QoS = 5 nodes (2 on `zen3_0512_a100x2`) for 10 min; `idle_*`
  QoS for projects out of compute time; private-project QoS up to 240 h; the
  defaults *"If partition and QOS are not given, default values are `zen3_0512`
  for both on VSC-5 and `skylake_0096` for both on VSC-4"*; the `--gres=gpu:`
  values 1 or 2; the `sinfo -o %P` / `sqos` /
  `sacctmgr show user \`id -u\` withassoc …` recipes; the `squeue` job reason
  codes; `lastjobs`; and the warning not to submit thousands of short jobs.

---

## Primary literature — original papers

### S20 — R. Thakur, R. Rabenseifner, W. Gropp, "Optimization of Collective Communication Operations in MPICH", *Int. J. High Perf. Comput. Appl.* **19**(1), 49–66, 2005 ★

- DOI: <https://doi.org/10.1177/1094342005051521>; author copy
  <https://www.mcs.anl.gov/~thakur/papers/ijhpca-coll.pdf>
- Retrieved: 2026-09-22. Access: author copy free; SAGE holds the copyright.
  **Not vendored.** On 2026-09-28 the author-copy URL (and its
  `web.cels.anl.gov` alias) answered `403` to `curl`, so `fetch-sources.sh`
  reports it as `FAILED` and moves on; open it in a browser or use the DOI.
- Used for: **the corrected collective cost table in note 09**, which was wrong
  before this pass. The paper's model is $\alpha + n\beta$ per message plus
  $n\gamma$ per reduction element, and it gives, for $p$ processes and $n$ bytes:
  binomial-tree broadcast $\lceil\lg p\rceil(\alpha + n\beta)$; scatter +
  ring-allgather broadcast $(\lg p + p - 1)\alpha + 2\frac{p-1}{p}n\beta$;
  recursive-doubling allreduce $\lg p\,(\alpha + n\beta + n\gamma)$ —
  **one** $\lg p\,\alpha$, not two; Rabenseifner's reduce-scatter + allgather
  allreduce $2\lg p\,\alpha + 2\frac{p-1}{p}n\beta + \frac{p-1}{p}n\gamma$;
  recursive-doubling allgather $\lg p\,\alpha + \frac{p-1}{p}n\beta$; Bruck
  all-to-all $\lg p\,\alpha + \frac{n}{2}\lg p\,\beta$ and pairwise-exchange
  all-to-all $(p-1)(\alpha + n\beta)$. Implemented and tested in
  [`../src/py/mpi_cost.py`](../src/py/mpi_cost.py).

### S21 — G. M. Amdahl, "Validity of the single processor approach to achieving large scale computing capabilities", *AFIPS Spring Joint Computer Conference*, 483–485, 1967

- DOI: <https://doi.org/10.1145/1465482.1465560>
- Retrieved: not retrieved — cited by DOI only. Access: ACM paywall; the
  statement of the law is standard and is taken from [S9], the lecturer's own
  slide, which is what this course teaches. Not vendored.
- Used for: the law itself. **The convention matters and is stated everywhere it
  is used**: in these notes, as on the lecturer's slide [S9], $f$ is the
  **sequential** fraction, $T_p = f\,T_1 + (1-f)T_1/p$ and
  $S_p = 1/(f + (1-f)/p) < 1/f$. The sibling course's note 07 uses the same
  convention; see S24.

### S22 — TOP500 list, November 2025 ★

- URL: <https://www.top500.org/lists/top500/list/2025/11/> (pages 1–5 read)
- Retrieved: 2026-09-22. Access: public web page; cited, not vendored.
- Used for: **independently confirming the lecturer's figures** in [S9], which
  match line for line. Top ten ranks and Rmax agree exactly (El Capitan 1809.00,
  Frontier 1353, Aurora 1012, JUPITER Booster 1000, Eagle 561.20, HPC6 477.90,
  Fugaku 442.01, Alps ~435, LUMI 379.70, Leonardo 241.20 PFlop/s). The two
  Austrian entries:
  - **#60 MUSICA Phase 1** — Lenovo ThinkSystem SD665-N V3, AMD EPYC 9654 96C
    2.4 GHz, NVIDIA H100 SXM5 94 GB, InfiniBand NDR200, 161 280 cores,
    Rmax 31.84 PFlop/s.
  - **#465 VSC-4** — Lenovo ThinkSystem SD650, Xeon Platinum 8174 24C 3.1 GHz,
    **Intel Omni-Path**, 37 920 cores, Rmax 2.73 PFlop/s, Rpeak 3.76.
    37 920 / 48 = **790 nodes**, which is exactly the node count on [S9].
  - **VSC-5 is no longer in the list** — consistent with [S9], which shows it
    falling to #499 in 11/2024.
  This is also the only public source found for an ASC interconnect: VSC-4 uses
  Omni-Path. VSC-5's fabric is *not* named on any public page read here (see
  note 04).

---

## Within this repository

### S23 — `ws2026/numerical-simulation-and-scientific-computing-i` ★

- Path: `../../../ws2026/numerical-simulation-and-scientific-computing-i/`
  (this repository; its own register is
  `../../../ws2026/numerical-simulation-and-scientific-computing-i/refs/SOURCES.md`)
- Retrieved: 2026-09-22 (read from disk). Access: local.
- Used for: **avoiding duplication.** That course (360.242, 5 ECTS) covers the
  memory hierarchy, roofline, serial optimisation, OpenMP from the specification,
  races and false sharing, Amdahl/Gustafson/Karp–Flatt, strong and weak scaling,
  and the software-engineering toolchain, all with measured numbers on the same
  laptop. Where this course's notes need those, they **link** to it rather than
  restating it: note 04 → its note 01, note 07 → its note 07, note 16 → its
  notes 01, 02 and 07. Where the two genuinely differ (its OpenMP vs this
  course's MPI; its `std::thread` task manager vs this course's Slurm) both are
  kept. Its `refs/SOURCES.md` S11 (OpenMP 5.2, vendored there) is the companion
  to S15 here; the two specs are deliberately not duplicated.

### S24 — The host machine (measured, not read)

- Apple M3 Pro, macOS 15 (Darwin 25.6.0), Apple clang, **Open MPI 5.0.11**
  (`mpicc --showme:version`), Homebrew. Not a URL: this is the machine the
  reference code runs on.
- Retrieved: 2026-09-22 (measured on the machine). Access: local.
- Used for: every timing printed by `../src/c/*` and quoted in the notes. These
  are **laptop, shared-memory, oversubscribed** numbers: they show the *shape*
  of a curve (latency floor, overlap gain, tree vs loop), never the magnitude
  you would see on VSC-5. Where the notes give a cluster magnitude it comes from
  S9 or S14 and says so.

---

## Added 2026-09-28

### S25: ASC Indico *Trainings* calendar, catalogue as of 2026-09-28 ★

- URL: <https://events.asc.ac.at/category/4/>, reached from
  <https://asc.ac.at/training> → *View ASC training events*; export used:
  `https://events.asc.ac.at/export/categ/4.json?from=2026-09-01&to=2028-12-31&limit=400`
  (the whole-site export `categ/0.json` returns the same events; category 5 is
  empty). `https://vsc.ac.at/training`, the address in the TISS note, does not
  resolve (S4).
- Retrieved: 2026-09-28. Access: public, no login.
- Used for: **what could actually be booked on 2026-09-28.** From 28.09.2026 the
  calendar lists 47 events, the last real one on 20.04.2027 (plus a
  *"Template: AI:AT-Training"* placeholder dated 01.06.2028 and a
  *"TESTING - Indico update"* clone on 06.–07.10.2026, both ignored).
  **None of the three 057.020 blocks is announced**: no *Linux Command Line*,
  no *Introduction to Working on the ASC Clusters*, no *Parallelization with
  MPI*, and nothing at all dated in 2027W (October 2027 to January 2028).
  The events that are at least a full day (times Europe/Vienna):

  | id | dates | days × hours | title | format |
  |---|---|---|---|---|
  | 358 | 29.–30.09.2026 | 2 × 4.5 h (09:00–13:30) | Multi-GPU Programming Bootcamp | online |
  | 307 | 06.–29.10.2026 | multi-week, 09:00–17:00 | European AI Hackathon | hybrid |
  | 273 | 12.–15.10.2026 | 4 × 6.5 h (09:00–15:30) | Modern C++ Software Design (Intermediate) | online |
  | 324 | 03.11.2026 | 1 × 7 h (10:00–17:00) | AI Cities Austria (summit, Operngasse 17-21) | on site |
  | 330 | 23.–24.11.2026 | 2 × 7 h (09:00–16:00) | Introduction to Deep Learning | online |
  | 382 | 10.02.2027 | 1 × 6.5 h (09:00–15:30) | Breaking the Silo: Efficiently Integrating Industrial Data Streams with Digital Twins | online |

  Everything else (about 40 events) is a 1 to 4 hour AI:AT / EuroCC webinar or
  workshop, mostly on AI adoption, trustworthy AI and the AI Act.
  The multi-GPU bootcamp (358) starts the day after retrieval.

### S26: 057.021 ASC-School II, TISS transcription (2026S) in this repository

- Path: [`../../../ss2028/asc-school-ii-hpc/docs/tiss.md`](../../asc-school-ii-hpc/docs/tiss.md)
  (course folder [`../../../ss2028/asc-school-ii-hpc/`](../../asc-school-ii-hpc/index.md),
  maintained separately; linked, not copied).
- Retrieved: 2026-09-28 (read from disk; transcribed there on 2026-09-28 from
  the 2026S TISS page). Access: local.
- Used for: the source of the **"at least 3 full training days"** rule. It is
  057.021's examination modality (grade on request; *"Participation in at
  least 3 full training days is required."*), and ASC
  states the same course's requirement as *"participation in at least 18
  hours"* (S4). **057.020's own TISS page (S1) has no such rule**: its
  assessment is participation in the three blocks plus reviewed program
  examples. 057.021 is offered in summer semesters.

---

## Sources deliberately not used

- **The ASC clusters themselves.** No login, no `sinfo`, no job. The brief for
  this pass forbade it and the account would not exist outside a training block.
  Every partition name, core count and quota below therefore carries a citation
  to a public page, and where a figure could not be confirmed from a public page
  it is marked `(unsourced: …)` rather than guessed.
- **TUWEL.** 057.020 has no TUWEL course (registration and material are on
  Indico and GitLab). Nothing was fetched. This rests on the public pages, not
  on a TUWEL login, so it has not been re-checked.
- **The `trainee##` accounts and the ASC JupyterHub.** The credentials are
  mailed to accepted participants; no attempt was made.
- **VoWi** (<https://vowi.fsinf.at>). Searched on 2026-09-22 for `057.020`,
  `VSC-School`, `ASC-School`, `Blaas-Schenner`, `High Performance Computing`,
  `MPI`, `VSC`, and with `insource:"057.020"`, in the article and *TU Wien*
  namespaces. **There is no VoWi page for 057.020 or for 057.021**; the only
  hit is a generic *LVA-Bewertungen* list page last edited 2019-10-12. Recorded
  so the next reader does not repeat the search. Consequence: there are no
  student-reported exam questions, because there is no exam — see
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
- **TISS course-materials page** (`/education/course/documents.xhtml`): redirects
  to the TU Wien IdP. Not followed.
- **Student GitHub/GitLab copies of the HLRS exercises.** Reproducing an
  exercise sheet is not ours to do, and the official repository [S11] is public
  anyway.
