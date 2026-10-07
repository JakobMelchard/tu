# 057.020 ASC-School I Courses in High Performance Computing — TISS page (2026W)

Transcribed from https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=057020&semester=2026W&locale=en
on **2026-09-22** (first transcription 2026-09-21). Content sections are in
tiss-api.md. The 2025W and 2024W pages were fetched on the same
day for the comparison below.

VU, 2.0 h, 1.5 ECTS, hybrid, held in blocked form. Mode of examination:
immanent. Attendance required.

## Blocks

1. Linux command line: SSH to ASC systems, editor, ~25 core shell commands, shell scripts, environment configuration.
2. Introduction to working on the ASC clusters: cluster structure, login vs compute nodes, module environment, compiling, Slurm batch jobs, storage, workflows.
3. Parallelization with MPI: distributed vs shared memory, MPI concepts, communication patterns, deadlock avoidance, runtime comparison, debugging MPI programs.

## Teaching methods

Lecture plus practical exercises per block, delivered online via Zoom. Exercises alone or in pairs, discussion with instructors.

## Lecturers

Blaas-Schenner, Claudia. Institute E057-09 Service Unit of ASC Research Center.

## Examination modalities

Participation in the courses and review of submitted program examples.

## Registration

No TISS registration and no dates in TISS. Register per block at https://asc.ac.at/training; access details go to registered and accepted attendees only. Contact: training@asc.ac.at.

## Curricula

ALG for all students: not specified.

## Literature

"No lecture notes are available."

## Previous knowledge

Block 1: none. Block 2: block 1 skills. Block 3: block 1 skills plus ability to write, compile and run a serial program in C/C++, Fortran or Python. Continuative: 057.021 ASC-School II. Language: English.

---

## Year-on-year comparison

Offerings exist back to 2019W (semester selector on the page). The three most
recent were compared field by field on 2026-09-22.

| field | 2024W | 2025W | 2026W |
|---|---|---|---|
| **title** | 057.020 **VSC**-School I Courses in High Performance Computing | 057.020 **ASC**-School I … | 057.020 ASC-School I … |
| ECTS / hours / type / format | 1.5 / 2.0 / VU / hybrid, blocked | identical | identical |
| lecturer | Blaas-Schenner, Claudia | identical | identical |
| institute | E057-09 Service Unit of ASC Research Center | identical | identical |
| block 2 title | "Introduction to Working on the **VSC** Clusters" | "… on the **ASC** Clusters" | as 2025W |
| learning outcomes | "login to the **VSC** Systems", "batch jobs for the workload manager **SLURM** deployed at **VSC**" | same text with VSC → ASC and SLURM → Slurm | as 2025W |
| subject of course | "the actual structure of the **VSC**" | "… of the **ASC systems**" | as 2025W |
| registration | `https://vsc.ac.at/training`, `training@vsc.ac.at` | `https://asc.ac.at/training`, `training@asc.ac.at` | as 2025W |
| *Course homepage* field | `https://vsc.ac.at/training` | `https://vsc.ac.at/training` | **still** `https://vsc.ac.at/training` — **this hostname no longer resolves** |
| examination modalities | "participation in the courses and by reviewing the submitted program examples" | identical | identical |
| literature | "No lecture notes are available." | identical | identical |
| attendance | required | required | required |
| continuative course | 057.021 ASC-School II | identical | identical |
| **course dates** | present, 4 entries | present, 3 entries | **none** |

**The only substantive change in three years is the VSC → ASC rename**, which
happened between 2024W and 2025W. Scope, outcomes, lecturer, ECTS and
examination modalities are byte-identical apart from that substitution.

### Course dates as TISS listed them

**2024W** (all 09:00–17:00 unless noted):

| day | time | date | location | description |
|---|---|---|---|---|
| Wed | 09:00–16:00 | 09.10.2024 | Online via Zoom | Linux command line (participation is required for Linux newbies only) |
| Thu | 09:00–17:00 | 24.10.2024 | Online via Zoom | Introduction to Working on the VSC Clusters (1 day — either 24.10.2024 or 16.01.2025) |
| — | 09:30–14:00 | 18.11.2024 – 21.11.2024 | Seminar room 2/2 (2nd floor), Operngasse 11, 1040 Wien **or** Zoom (hybrid) | Parallelization with MPI (4 morning sessions) |
| Thu | 09:00–17:00 | 16.01.2025 | Online via Zoom | Introduction to Working on the VSC Clusters (the January alternative) |

**2025W**:

| day | time | date | location | description |
|---|---|---|---|---|
| Wed | 09:00–16:00 | 08.10.2025 | Online via Zoom | Linux command line (participation is required for Linux newbies only) |
| Wed | 09:00–17:00 | 15.10.2025 | Online via Zoom | Introduction to Working on the ASC Clusters (1 day — either 15.10.2025 or in January 2026) |
| — | 09:00–13:30 | 17.11.2025 – 20.11.2025 | Seminar room BA 10A (10th floor), Getreidemarkt 9, 1060 Wien **or** Zoom (hybrid) | Parallelization with MPI (4 morning sessions) |

**2026W**: no course dates on the page as of 2026-09-22, and no 2026W instance
of any of the three blocks is listed on the ASC Indico calendar
(https://events.asc.ac.at/category/4/) either. See
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

### Broken external link

The *Course homepage* field on all three pages is `https://vsc.ac.at/training`.
As of 2026-09-22 the apex domain `vsc.ac.at` has an MX record but **no A
record**, so the link fails to resolve; `www.vsc.ac.at`, `docs.vsc.ac.at` and
`events.vsc.ac.at` are CNAMEs to the corresponding `asc.ac.at` hosts. The
working address is **https://asc.ac.at/training**.
