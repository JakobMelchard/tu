# 00 Exam focus — what is actually assessed

Read this before deciding how much time to give a topic. Sources are `[S<n>]` in
[`../refs/SOURCES.md`](../refs/SOURCES.md); the TISS diff it rests on is at the
bottom of [`../docs/tiss.md`](../docs/tiss.md).

## Status on 2026-09-27

- Deregistration possible until **20.10.2026** [S1]. TISS re-read on
  2026-09-27: no field changed [S1].
- **Eight lectures**, Tue 11:00-13:00, HS 6 RPL, 13.10.2026 to 01.12.2026 [S1].
- **Exams**: Tue 19.01.2027 and Tue 23.02.2027, both 13:00-15:00 (table below).
- **TUWEL** opens 01.10.2026 [S1]. It was not read for these notes: every
  statement on this page about what TUWEL holds (the exercises, the Part 1/Part
  2 point split, the exam duration) is unverified.


## Start here: there is no past paper, and there is a written exam

Both halves of that sentence matter, and neither is a guess.

**There is a written exam.** This is not one of the 2 ECTS programming courses
that are graded by submission alone. TISS 2026W states two assessment parts —
*"Part 1: successfully completing the exercises"* and *"Part 2: written exam
with multiple choice and programming exercises"* — and backs it with two
scheduled sittings in booked lecture halls, each with its own TISS registration
window [S1]:

| | date | time | room | registration |
|---|---|---|---|---|
| Exam 1 | **19.01.2027** | 13:00–15:00 | HS 17 Friedrich Hartmann · EI 9 Hlawka | 06.12.2026 – 17.01.2027 |
| Exam 2 | **23.02.2027** | 13:00–15:00 | Informatikhörsaal | 20.01.2027 – 19.02.2027 |

Two rooms for one sitting, and an earlier offering that scheduled three separate
**exam-inspection** appointments afterwards [S3], is what a real, individually
marked paper looks like. Mode of examination is *immanent*, so Part 1 runs all
semester and Part 2 is the paper at the end, in a 13:00-15:00 slot; how much of
the two hours the paper itself takes is not published.

**There is no past paper.** Every offering puts its material in TUWEL, which
needs a login and was not touched. Concretely, and each checked on 2026-09-22:

- TISS's literature field reads "No lecture notes are available." in all seven
  pages, 2019W through 2026W [S1]–[S7].
- The only course homepage the lecturer ever published — 191.116, 2019W, alive
  now only in the Internet Archive — says, in full, *"All material will be
  published on TUWEL"* [S8]. No page for 191.125 was ever archived at all.
- The VoWi page exists and is **empty**: *Inhalt, Ablauf, Vortrag, Übungen,
  Prüfung/Benotung, Zeitaufwand, Unterlagen, Tipps* all read "noch offen", and
  it has no attachments [S9]. A full-text VoWi search for the lecturer's name
  returns that one page.
- Nothing on `hunoldscience.net` or the institute pages [S10].

So **the point split between exercises and exam, the pass mark, the number of
questions and the duration of Part 1 are not public**, and every exam-style
question in these notes is ours. They are marked as such at the end of each
note. Do not read a question here as "this was asked".

## What the six-year TISS diff does tell you

Three changes, all sourced, all worth acting on.

### 1. Multiple choice is new since 2024W — and it is half the format

2021W–2023W: *"written exam with programming exercises"* [S4]–[S6].
2024W onwards: *"written exam with **multiple choice** and programming
exercises"* [S3], repeated verbatim in 2025W and 2026W [S1], [S2].

The same year the course became a **mandatory 5th-semester subject in the
*Technische Informatik* bachelor** (033 535) on top of CSE [S3]; before that it
was a CSE course only. A cohort several times larger, examined on paper, is the
ordinary reason multiple choice appears. Plan for it: MC rewards exactly the
kind of knowledge that is cheap to check and expensive to guess — *which of
these returns a view*, *what does this fancy-index assignment print*, *which
`minimize` method needs no gradient*. That is why every note here ends in five
MC questions with a one-line justification of the right answer, and why the
pitfall lists are written as things that have a definite right answer.

### 2. The programming half is written on paper, not in TUWEL

In 2021W and 2022W the exam mode line said *"TUWEL quiz or Jupyter notebook —
required infrastructure: Computer with Internet connection, Webcam"* [S5], [S6].
That line was **dropped in 2023W** and the course went back to lecture halls
[S4]. So "programming exercises" now means *writing Python on paper in HS 17*,
with no interpreter, no tab completion and no documentation.

The consequence for how to study is concrete: you must be able to **write** — by
hand, correctly — the idioms, not merely recognise them. `fig, ax =
plt.subplots()`; `rng = np.random.default_rng(seed)`;
`df.groupby("k")["v"].transform("mean")`; `with mp.Pool() as pool:`;
`@pytest.mark.parametrize("a,b", [...])`; `minimize(f, x0, jac=g,
constraints=[{"type": "ineq", "fun": c}])`. Argument *names* and *order* matter
on paper in a way they never do with an editor open.

### 3. The lecture is eight sessions, and the exercises carry the rest

2022W and 2023W ran the full semester. 2024W onwards stops in early December,
and 2026W has exactly **eight** Tuesdays: 13.10, 20.10, 27.10, 03.11, 10.11,
17.11, 24.11, 01.12 [S1]. That is the same count as the eight-lecture plan on
the 2019W homepage [S8], for a course that has since doubled its semester hours.

Eight two-hour lectures cannot cover ten topics in depth. TISS says the teaching
methods are *"programming exercises"* and *"small software projects using
Jupyter notebooks"* [S1] and attendance is required. Read that as: the lecture
sets direction, the assignments are where the eight-item subject list is
actually worked through, and Part 1 is not a formality you can defer.

## Weighting the ten notes against the TISS subject list

The subject list is byte-identical in all seven TISS pages [S1]–[S7] — eight
items, in this order. Our ten notes map onto it one-to-one except that 08/09/10
split the last two items:

| TISS subject item | note | weight |
|---|---|---|
| Introduction to the Python programming language | [01](01-python-for-scientists.md) | **high** — the only item that is pure language, and the easiest to examine by MC |
| The SciPy and NumPy ecosystem | [02](02-numpy.md), [03](03-scipy.md) | **highest** — two of the five learning outcomes name NumPy and SciPy explicitly [S1] |
| Data processing and plotting (Matplotlib) | [04](04-matplotlib-and-data.md) | **high** — a learning outcome names 2D *and 3D* plotting by name |
| Code testing | [05](05-testing.md) | medium |
| Reproducible and interactive data processing with IPython/Jupyter | [06](06-reproducibility-jupyter.md) | medium — the "small software projects using Jupyter notebooks" are here |
| Introduction to solving optimization problems (e.g. SciPy, PuLP) | [07](07-optimisation.md) | **high** — a learning outcome, and the only item TISS names libraries for |
| Parallel processing in Python | [08](08-parallel-processing.md) | **high** — the lecturer's own research area is parallel computing and MPI [S10] |
| Interfaces to other programming languages (e.g. Julia) | [09](09-interfaces.md) | medium |
| — (not in the subject list) | [10](10-performance.md) | low as an exam topic; high as a prerequisite for 08 and 09 |

Two judgements in that table, stated so you can disagree with them:

- **08 is weighted above what a generic Python syllabus would give it.** Sascha
  Hunold is an associate professor in the Research Unit of Parallel Computing;
  his published work is MPI collectives, performance portability and
  shared-memory programming [S10]. A lecturer examines what they know. The GIL,
  threads-vs-processes, `spawn` and Amdahl are the highest-value items in that
  note.
- **10 exists because 08 and 09 need it**, not because TISS asks for it. Nothing
  in the subject list mentions profiling. Read it, do not memorise it.

## The five learning outcomes, read as exam instructions

TISS's outcome list [S1] is unusually operational. Each line is a thing you
could be asked to *do* on paper:

1. *"a solid background in the main packages used in scientific programming
   (NumPy, SciPy)"* → notes 02 and 03; expect API recall.
2. *"solve their own scientific problems with Python"* → a short program.
3. *"simulate a specific phenomenon"* → an ODE with `solve_ivp`, or a seeded
   Monte Carlo. Note 03 and note 08's π example are both of this shape.
4. *"formulate and solve various optimization problems"* → note 07. "Formulate"
   is doing work in that sentence: translating a word problem into
   $\min c^\top x$ with the right inequality signs is examinable on its own.
5. *"analyze and visualize scientific data by plotting 2D or 3D graphs"* →
   note 04, including `projection="3d"`.

## How to prepare

1. **Be able to write the idioms by hand.** See §2 above. This is the single
   highest-return activity, because the paper has no interpreter.
2. **Learn the things with one right answer**, since that is what MC asks:
   which operations return a view and which copy; what broadcasts with what;
   `ddof` defaults (NumPy 0, pandas 1); `rtol`/`atol` defaults; which `minimize`
   methods need a gradient; the sign convention of a SLSQP `ineq` constraint;
   why threads do not speed up pure-Python loops; Amdahl's bound.
3. **Do the exercises properly and early.** Part 1 is a hard gate, attendance is
   required, and deregistration closes 20.10.2026, one week after the first
   lecture [S1]. The exercises themselves are in TUWEL, so TUWEL access
   comes before any of this.
4. **Run the notes' code.** Every claim in notes 02–10 is exercised by a test in
   `../src/py`; reading a pitfall is worth much less than watching
   it fire.
5. **Check the versions.** The notes were verified on 2026-09-27 against the
   exact library versions in [`../refs/SOURCES.md`](../refs/SOURCES.md) §S40
   (NumPy 2.5, SciPy 1.18, pandas 3.0, Matplotlib 3.11.2, PuLP 4.0). If the
   course's environment pins older ones, two notes change: note 04's
   copy-on-write section (pandas 2 behaves differently) and note 07 §7 (PuLP 3.x
   still has `LpVariable(...)`, `LpStatus` and a bundled CBC; the box there
   lists both spellings). What the course pins is itself a TUWEL fact, so
   unverified for now.

## What would change this page

The three things that would supersede most of the above, in order of value:

1. The TUWEL course, open from **01.10.2026** [S1], which presumably states the
   point split and the exam duration. Not public.
2. The first lecture (13.10.2026), which usually settles format questions.
3. Anyone filling in the VoWi page [S9] — it has been a stub through six
   offerings, so do not wait for it.

## Our exam-style questions

Every note ends with five multiple-choice questions in the style the 2024W+
format implies. **All of them are ours.** No public paper for this course, this
lecturer or the predecessor number 191.116 exists to model them on [S9], and
this page would say so with the term attached if one did.
