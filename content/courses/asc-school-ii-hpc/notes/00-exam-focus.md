# 00 How the grade is formed, and which three days to pick

Read first. Written 2026-09-28 for a course offered in **summer semesters**; the 2028S
TISS page does not exist yet; everything is transcribed from 2026S [S1] and
from the ASC training portal and calendar [S3] [S4].

## There is no exam

- Mode: immanent. "The performance review takes place by participation in the
  courses and by reviewing the submitted program examples." [S1] [S2]
- "A grade will be given upon request." **At least 3 full training days**
  [S1]. The ASC portal states the same requirement as **at least 18 hours**
  [S3]. Plan for both: three full days *and* $\ge 18$ h.
- "Attendance Required!" [S1]; format online or hybrid [S1].
- **MPI events do not count**: they are ASC-School I content [S3].
- No lecture notes, no past papers. VoWi has no page for 057.021 (sibling
  register, searched 2026-09-22). The questions in notes 01-07 are ours.

So the grade comes from (a) being present for the whole of each chosen event
and (b) program examples from the hands-on labs, reviewed by the lecturers
(Störi, Blaas-Schenner, E057-09) [S1]. How examples are submitted and graded
is not published anywhere read: **ask** (below).

## Registration: per event, not in TISS

1. TISS has no registration for 057.021 (type `EXTERNAL`) [S1] [S2]. It
   counts as ALG "for all students", i.e. a free elective [S1].
2. Register for each event in the ASC Indico calendar,
   <https://events.asc.ac.at/category/4/>, with the TU Wien e-mail. The link
   on TISS, `vsc.ac.at/training`, no longer resolves; use
   <https://asc.ac.at/training> [S3] (domain note in `../refs/SOURCES.md`).
3. Mail `training@asc.ac.at` (TISS still says `training@vsc.ac.at`) that you
   attend for 057.021 and want the ECTS [S1] [S3].
4. Registration is **binding**; no-shows are **blacklisted** from future
   training; forms close early when full, with a waiting list by mail [S4].
   A mobile number is needed for the training account's SMS second factor [S4].
5. The *Hybrid Programming* course registers **through HLRS**, not Indico
   [S4]. Whether it counts for 057.021 like an ASC-run event: verify.

## What related courses in this repository already cover

| course (repo folder) | semester | covers |
|---|---|---|
| NSSC I (`numerical-simulation-and-scientific-computing-i`) | winter | memory hierarchy, roofline, serial optimisation, OpenMP |
| Efficient Programs (`efficient-programs`) | winter | measurement, `perf`, vectorisation, cache effects |
| Scientific Programming with Python | winter | numpy, `multiprocessing`, performance |
| ASC-School I (`asc-school-i-hpc`) | winter | Linux, ASC clusters, Slurm, MPI in depth |
| Many-Core Architectures (`computational-science-on-many-core-architectures`) | winter | GPU programming (CUDA/OpenCL) |
| Advanced Multiprocessor Programming (`advanced-multiprocessor-programming`) | winter | memory models, lock-free data structures |
| Advanced Programming with C++ (`advanced-programming-with-cpp`) | winter | modern C++ |

## The candidates, by what they add

Hours from the published times of the last instance, breaks included [S4].

| event | days, h | adds beyond those courses | overlap | verdict |
|---|---|---|---|---|
| **Python for HPC** | 3 full, ~22 h | Numba, Dask (distributed), mpi4py, CuPy, Python in Slurm [S7] | little (Sci. Prog. Python is single-node) | **only event that alone meets both thresholds** |
| **Hybrid Programming MPI+X** | 2.5, ~14 h content | pinning, MPI+OpenMP, MPI-3 shared memory, overlap, MPI+GPU [S5] | builds on School I and NSSC I, repeats neither | **best content**, but not 3 full days alone |
| **Multi-GPU Programming Bootcamp** | 1.5 (09:00 to 13:30 next day) | scaling over GPUs and nodes, profiler-driven optimisation, communication topology, NVIDIA libraries [S4] | needs Many-Core CUDA first | good second event |
| Linaro Forge / Extrae+Paraver / POP workshop | 0.6-3 d | parallel profilers (note 02) | Efficient Programs is serial-only | good filler; irregular |
| N-Ways GPU Bootcamp | 1.5 (09:00 to 12:30 next day) | OpenACC, OpenMP offload, stdpar | CUDA part = Many-Core | acceptable |
| OpenMP (2 d) | 2 full, ~15 h | little | NSSC I | skip |
| CUDA 4 Dummies (2 d) | 2 full, 16 h | little | Many-Core | skip |
| Modern C++ Software Design (4 d) | 4, ~26 h | design, not HPC | Adv. Programming with C++ | skip for this course |
| Introduction to Deep Learning (2 d) | 2, ~14 h | PyTorch on the cluster | ML courses | skip |

## Recommendation

- **Plan A (minimum risk):** *Python for HPC*, 3 full days, ~22 h, online,
  Basic, ASC's own trainers, public CC BY-SA material [S6] [S7]. Satisfies
  "3 full days" and "18 h" in one registration. Prepare with note 05.
  **Risk:** the last instance is May 2025 (spring pattern 2024, 2025; winter
  2023, 2024); none is listed for 2026 or 2027 as of 2026-09-28 [S4].
- **Plan B (best content):** *Hybrid Programming MPI+X* (Jan/Feb pattern
  2024-2026 [S4]) + *Multi-GPU Programming Bootcamp* (May-Sep pattern), about
  4 calendar days; hours: 14 of content plus the bootcamp's (the first
  day's end time is on its agenda page, not read). Uses exactly what School I
  and Many-Core taught.
  Prepare with notes 01, 03, 04, 07. Risks: HLRS registration (step 5
  above); half days may not count as "full days".
- **Fallback filler:** a profiling event (note 02) to top up hours.

Timing: 2028S runs March to June 2028. Historical spring slots [S4]:
Hybrid late Jan to mid Feb (still 2027W in TU terms), Modern C++ Advanced and
Deep Learning in March/April, N-Ways GPU in April (2024, 2025), Python for HPC
and Multi-GPU in May/June (2024, 2025), OpenMP in April or July. Since the
grade is "on request", whether an event in February 2028 counts for 2028S is
a question for the lecturers.

## What to verify in early 2028

1. The 2028S TISS page: still 1.5 ECTS, still "3 full training days", same
   lecturers; date the transcription in `../docs/tiss.md` (refetch
   `https://tiss.tuwien.ac.at/api/course/057021-2028S` for the API record).
2. The 2028 catalogue: `bash ../refs/fetch-sources.sh` fetches the Indico JSON;
   list HPC events from January to July 2028.
3. By mail to `training@asc.ac.at`: which threshold applies (3 full days or
   18 h), whether HLRS-registered Hybrid counts, whether February events count
   for 2028S, and **how program examples are submitted** (format, deadline,
   to whom).
4. That nothing already counted for ASC-School I is double-counted.
5. The cluster in use: MUSICA partitions and QoS names (`sinfo -o %P`,
   `sacctmgr show user $(id -u) withassoc format=qos%200`) [S13]; VSC-4/5 may
   be retired by then.

## What to hand in, concretely

Our reference programs are written to double as hand-ins: each checks its
own result and exits non-zero on failure (`make -C ../src/c test`). For any
event, the pattern is: the lab's program, a job script from
`../src/sh/slurm_templates/`, the `affinity_report` output of the job, and a
scaling table as in note 07.
