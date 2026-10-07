# 00 What is assessed (and what is not)

Read this before any other note. It is short, and it changes what you should do
with the rest.

## There is no exam

TISS, on the 2026W page (the latest published) and on every previous offering read here [S1] [S2] [S3]:

- **Mode of examination: Immanent.**
- **Examination modalities:** *"The performance review takes place by
  participation in the courses and by reviewing the submitted program
  examples."*
- **Miscellaneous: Attendance Required!**
- **Literature:** *"No lecture notes are available."*

So: no written exam, no oral exam, no test dates, no grade weighting to
optimise. The two things that produce a grade are **being there** and
**handing in program examples that work**. There are correspondingly **no past
papers anywhere** — VoWi has no page for 057.020 or for the continuation
057.021 at all (searched 2026-09-22 for the course number, both course titles,
the lecturer's name, `MPI`, `VSC`, and `insource:"057.020"`, in the article and
*TU Wien* namespaces) [see `../refs/SOURCES.md`, "Sources deliberately not
used"].

Every "exam-style question" in notes 01–16 is therefore **ours**, and is
labelled as ours. They exist to let you check yourself, not because anyone
asked them. Where a question restates something the course's own exercise sheet
or agenda actually asks, it says so and cites the source.

## What you actually have to produce

The hands-on labs, in the block you attend. For block 3 these are public and
enumerated [S11]: `01_hello`, `02_pingpong`, `03_ring`, `04_allreduce`,
`05_comm-split`, `06_virtual_cartesian_topologies`, `07_derived-datatypes`,
`08_1sided`, `09_1sided-shmem`, in C, Fortran **or** Python (mpi4py) — you pick
the language, and each comes with a skeleton and a solution. Exercises are done
"alone or in teams of two students", with discussion among participants and
one-to-one with the instructors [S1].

Our versions, written independently and checked against the one number every
variant must produce, are in
`../src/exercises/2025w-mpi/` and in
[`../src/c/`](../src/README.md).

Blocks 1 and 2 have exercises inside the slide decks rather than a hand-in
repository: four exercise sets in the Linux primer [S7] and one per topic in the
cluster intro [S10].

## Registration is the hard part, not the exam

057.020 has **no TISS registration**. You register *per block*, at
<https://asc.ac.at/training> → the Indico event, with your institutional e-mail,
and ASC then mails you the access details and a temporary `trainee##` account
[S1] [S4] [S6]. Points that bite:

- Registration can close early when a course fills, and reopens on cancellations
  [S6]. Watch the Indico calendar, not TISS.
- **Your registration is binding and there is a no-show blacklist**: *"If you do
  not cancel and do not show up at the course you will be blacklisted and
  excluded from future training events."* [S6]
- You must give an international mobile number: login to every ASC system needs
  an SMS one-time password [S6] [S13].
- There is a **pre-assignment**: log in to `vsc5` (or the JupyterHub) *before*
  the course, so the first hour is not spent on 2FA problems [S6] [S13].
- The TISS *Course homepage* link is `https://vsc.ac.at/training`, and that
  hostname no longer resolves. Use `https://asc.ac.at/training` [S4].
- Students from other Austrian universities need a co-registration at TU Wien
  during the admission period [S4].
- The ASC page also says to e-mail `training@asc.ac.at` stating that you are a
  VSC-School student, in addition to registering for the events [S4].

## Status: offered in winter semesters, nothing bookable yet


State of 2026-09-28. The 2027W TISS page does not exist
yet; the transcription in [`../docs/tiss.md`](../docs/tiss.md) and [S1] is the
2026W page. Re-read TISS when the 2027W page appears and compare it with S1.

**What ASC has on its calendar.** The TISS note says to book at
`vsc.ac.at/training`; that hostname does not resolve, and `www.vsc.ac.at`
redirects to <https://asc.ac.at/training>, whose event list is the Indico
category <https://events.asc.ac.at/category/4/> [S4] [S25]. On 2026-09-28 it
lists 47 events, the last real one on 20.04.2027, and **none of the three
057.020 blocks**: no Linux Command Line, no Introduction to Working on the ASC
Clusters, no Parallelization with MPI, and nothing dated in 2027W at all
[S25]. The catalogue is almost entirely AI:AT / EuroCC webinars. The multi-day
or full-day events are:

| dates | event | length |
|---|---|---|
| 29.–30.09.2026 | Multi-GPU Programming Bootcamp | 2 × 4.5 h, online |
| 06.–29.10.2026 | European AI Hackathon | multi-week, hybrid |
| 12.–15.10.2026 | Modern C++ Software Design (Intermediate) | 4 × 6.5 h, online |
| 03.11.2026 | AI Cities Austria (a summit, not a course) | 7 h, on site |
| 23.–24.11.2026 | Introduction to Deep Learning | 2 × 7 h, online |
| 10.02.2027 | Breaking the Silo: industrial data streams with digital twins | 6.5 h, online |

**The "at least 3 full training days" rule is not this course's rule.** It is
the examination modality of the sibling **057.021 ASC-School II** [S26], which
ASC words as "at least 18 hours" and which accepts any ASC training event
*except MPI*, because MPI belongs to School I [S4]. 057.020's own page asks
for participation in its three blocks plus reviewed program examples [S1].
Measured against the 3-day rule anyway, only **Modern C++ Software Design**
(4 × 6.5 h) reaches three full days in a single event; the hackathon is longer
but is not a training course, and Introduction to Deep Learning plus Breaking
the Silo add up to three days only in combination. None of them is a
057.020 block, and all of them fall in 2026W or 2027S, before 2027W. ASC gives ECTS only to students *enrolled in the respective
semester* [S4]; whether an event attended in 2026W could still be credited in
2027W is not stated anywhere (unsourced: ask `training@asc.ac.at`).

057.021 is offered in summer semesters; its folder is
[`../../../ss2028/asc-school-ii-hpc/`](../../asc-school-ii-hpc/index.md).

**What to expect in 2027W.** The pattern of the last three winters
[S5] [S2] [S3] is:

| block | 2023W | 2024W | 2025W | expected 2027W |
|---|---|---|---|---|
| Linux command line (1 day) | 03.10.2023 | 09.10.2024 | 08.10.2025 | early October 2027 |
| Working on the ASC clusters (1 day) | 12.10.2023 *or* 16.01.2024 | 24.10.2024 *or* 16.01.2025 | 15.10.2025 *or* January 2026 | mid-October 2027 *or* January 2028 |
| Parallelization with MPI (4 mornings) | 06.–09.11.2023 | 18.–21.11.2024 | 17.–20.11.2025 | mid-November 2027 |

Treat that last column as a **prediction, not a date**: the winter pattern
already broke once, since no 2026W instance of any block was announced by
late September 2026 [S25], and the MPI material has meanwhile also run as two
2-day events in spring and summer [S5]. Practical consequence: subscribe to
the ASC newsletter and check <https://events.asc.ac.at/category/4/> regularly
from summer 2027; the registration window is the thing to catch, and TISS will
not tell you about it. Cluster facts in notes 03 to 06 (partitions, quotas,
login hosts) date from September 2026 and should be re-checked against the
ASC documentation [S19] before the blocks.

## What the three blocks are worth to you

1.5 ECTS for all three together, which is about 37 hours of work, against
roughly 7 + 8 + 4×4.5 = 33 contact hours if you attend everything. This is a
practical skills course with essentially no private-study component built in;
the private study is the point of these notes, not of the course.

Only block 3 has real intellectual depth (four mornings, MPI 5.0, through to
one-sided and shared-memory RMA [S13]). Blocks 1 and 2 are a fast tour; TISS
itself says block 1 is *"required for Linux newbies only"* [S2]. If you already
live in a terminal, the honest plan is: skim notes 01–03, work notes 04–06 with
the real partition names in front of you, and spend the time on notes 07–16.

## Self-check

These are **our** questions — there is no paper they are modelled on.

1. **What produces your grade in 057.020?** Attendance at the blocks you
   registered for, plus program examples you submit and that are reviewed [S1].
2. **Where do you register, and what happens if you register and do not turn
   up?** Per block, at the ASC Indico under <https://asc.ac.at/training>; a
   no-show without cancellation gets you blacklisted from future ASC training
   [S4] [S6].
3. **Which block can you skip, according to the course itself?** Block 1, if you
   are not a "Linux newbie" — TISS says so in the date description [S2].
4. **Which of the three blocks is actually four days long, and what is on day
   three?** Parallelization with MPI; day 3 is groups & communicators, virtual
   topologies and derived datatypes [S13].
5. **What is the single number that every block-3 lab from `03_ring` onwards has
   to print?** $P(P-1)/2$ on every rank, for $P$ processes [S11].
6. **Does "at least 3 full training days" decide your 057.020 grade?** No. That
   is 057.021's rule [S26]; 057.020 is graded on its three blocks and the
   reviewed program examples [S1], and School II excludes the MPI block that
   School I is built around [S4].
