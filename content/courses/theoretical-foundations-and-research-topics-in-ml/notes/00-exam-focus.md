# 00 Exam focus: what is actually assessed

Built from the TISS records for **all ten offerings** of 194.100 (2020W–2026W),
the TISS record for its 6 ECTS twin 194.201, the lecturers' own course pages for
nine semesters [S5], and the VoWi page, all read on 2026-09-22; TISS re-read on
2026-09-27 with no field changed [S1]. Sources registered in
[`../refs/SOURCES.md`](../refs/SOURCES.md).


> **Read the next two sections before anything else.** They answer the two
> questions that determine how you should spend your time, and one of them has a
> genuinely surprising answer.

## 1. There is a written-and-spoken **oral exam**. This is not a seminar.

It would be reasonable to guess, from the words "Research Topics" in the title
and 3 ECTS on the label, that this is a seminar graded by a paper presentation
and a report. **It is not**, and has not been since 2021.

TISS is unambiguous [S1, S2]:

> Students will be evaluated on (1) mandatory and regularly submitted written
> coursework, (2) a practical project, and (3) a final oral exam. … For a final
> positive mark, students are required to:
> - Obtain at least 50 % of the total points on the coursework and project,
>   collectively. …
> - Obtain at least 50 % of the points on the oral exam.
>
> The oral exam is repeatable once in case of a negative grade.

So: **three components, two independent hurdles.**

| component | what it is | hurdle |
|---|---|---|
| Written coursework | submitted regularly through the semester, **mandatory** | ≥ 50 % of (coursework + project) **combined** |
| Practical project | the 15 h "final project" of the workload split [S2] | same combined pot |
| **Final oral exam** | dates via TUWEL | **≥ 50 % on its own** |

Consequences you should act on:

- **The oral exam is a separate hurdle you cannot buy off with coursework.**
  Perfect coursework and project do not carry a failed oral; the two thresholds
  are evaluated independently. This is the single most important structural fact
  on this page.
- **Coursework is mandatory, not optional credit.** TISS says "mandatory and
  regularly submitted".
- Coursework + project are pooled, so a weak project can be offset by strong
  weekly submissions and vice versa.
- **You get one retake of the oral**, and only of the oral.
- Mode of examination is recorded as **"Immanent"** (continuous assessment) [S1],
  which is why there is no exam date in TISS; see §4.

Note 12, [`12-oral-exam-question-bank.md`](12-oral-exam-question-bank.md), is
therefore the right shape of preparation. **But see §3 on where its questions
come from.**

## 2. The three eras, and why the "seminar" guess is a 2021 memory

The course has run **every semester since 2020W** and its assessment has been
rewritten twice. Reading an old description will mislead you [S3, S7]:

| era | semesters | topics | how it was graded |
|---|---|---|---|
| **I** | 2020W – 2021S | Statistical learning theory; kernel-based learning; **online learning; clustering; semi-supervised learning** | coursework + "a larger final project, **such as a written report or a (recorded or online presented) talk**" |
| **II** | 2022W – 2024S | the current list (ERM/regularisation, PAC, VC, SVM, least squares, deep learning) | coursework + practical project + **"a final discussion"** |
| **III** | **2024W – 2026W** | unchanged from era II | coursework + practical project + **"a final oral exam"**, with the explicit 50 %/50 % thresholds and one repeat |

Two things follow.

- **Era I is where the "presentation/seminar" impression comes from.** The
  `sose21` course page is the only one that mentions "a presentation of an
  advanced research topic in machine learning" [S7]. That option disappeared
  from TISS in 2022W. If you find a description of this course promising that
  you will be graded on a talk, it is at least five years out of date.
- **The topic list was rewritten in 2022W.** Online learning, clustering and
  semi-supervised learning were *dropped*; PAC learning, VC dimension and least
  squares were *added*. Notes 01–10 follow the current (era II/III) list. Do not
  revise online learning or clustering for this course: they are no longer in
  the syllabus, though "understand, summarise and present ML research papers"
  remains a stated learning outcome [S2], which is what note 11 serves.
- The 2024S → 2024W change from "a final discussion" to "a final oral exam" with
  hard percentage thresholds is a **tightening**, not a rewording: era II stated
  no thresholds and no repeat rule at all.

## 3. There are no past exam questions. Anywhere. None.

This has to be said plainly, because the absence is easy to mistake for a failure
to look.

- **VoWi has a page for this course, and it is empty** [S8]. Every section
  (Inhalt, Ablauf, Vorkenntnisse, Vortrag, Übungen, **Prüfung/Benotung**,
  Zeitaufwand, Unterlagen, Tipps, Kritik) reads "noch offen". The page has **no
  attachments**: "Diese Seite hat noch keine Anhänge."
- The same is true of the group's sibling pages (*Seminar in AI – Theoretical
  Aspects of ML*, *ML Algorithms and Applications*) [S8].
- **TISS states "No lecture notes are available."** [S1]
- **Every course page since 2021 says only "The course will be held on TUWEL."**
  [S6, S7] The slides, recordings, notebooks, forum and assignment sheets are all
  behind the TUWEL login. Nothing was fetched from there.

An oral exam leaves no paper trail, so this is not surprising. But it means:

> **Every question in [note 12](12-oral-exam-question-bank.md) is ours.** None is
> modelled on a real past paper, because no real past paper exists in public.
> They are derived from the TISS learning outcomes and from the theorems the
> named topics rest on. Treat them as a self-test, not as a leaked syllabus.

The one genuine signal about what is asked comes from the lecturers' own
description of the coursework [S6]:

> "there will be coursework for you to submit, for instance, tackling a learning
> problem with advanced machine learning methods **or understanding and
> explaining a proof**."

Combined with the learning outcome "**prove** learning theoretical results and
algorithmic properties of machine learning" [S2], the message is consistent and
worth taking literally: **you will be asked to reproduce proofs, not just state
results.** That is why the notes carry full proofs rather than statements, and
why note 12 ends with a list of proofs to rehearse.

## 4. Dates: what is fixed and what is not

| what | when | source |
|---|---|---|
| Registration | **14.09.2026 00:00 – 27.10.2026 23:59** | [S1] |
| Deregistration | not given | [S1] |
| Weekly slot | **Wed 10:00–12:00, 07.10.2026 – 20.01.2027**, Seminarraum FAV EG A, labelled "Exercise Sessions"; the only timetabled slot | [S1] |
| Coursework deadlines | **not public; announced in TUWEL** | [S1] |
| Project deadline | **not public; announced in TUWEL** | [S1] |
| **Oral exam date** | **not public; announced in TUWEL** | [S1] |


"The dates for the partial performance evaluations will be communicated via
TUWEL" [S1]. So the *only* hard dates you can plan around from public sources are
the registration window and the weekly slot; since coursework is mandatory and
regular, missing the start of the semester is expensive.

**The slot moved this year.** In 2025W it was Wed **16:00–18:00** in Seminarraum
FAV 01 A; in 2026W it is Wed **10:00–12:00** in Seminarraum FAV EG A [S1, S3].


## 5. Lecturers, and the 6 ECTS twin

Lecturers for 2026W: **Thomas Gärtner, Sagar Malhotra, Christoph Sandrock** [S1].
The team has shrunk each year: 2025S had six (adding Tamara Drucks, Patrick
Indri, Fabian Jogl), 2025W had four. **Patrick Indri, who was the named contact
on the 2025W course page [S6], is no longer listed for 2026W** [S1, S3].

**194.100 (3 ECTS) and 194.201 (6 ECTS) are the same lecture.** The course page
links both TISS entries side by side as "3 ECTS version" and "6 ECTS version"
[S6], and VoWi files them on one page under both numbers [S8]. 194.201 first
appeared in 2025W.

This matters because **194.201's topic list tells you what the lectures actually
contain** [S4]. It repeats the six 3 ECTS topics and then adds:

- Theory of deep learning
- Deep learning architectures
- Graph neural networks
- Expressivity and logics
- Interpretability, robustness, privacy, and fairness

Its learning outcomes are correspondingly sharper: "**rigorously prove** key
theoretical results in machine learning, and analyse the algorithmic properties,
**convergence**, and limitations of learning methods", and "design and conduct
small-scale research or application projects".

How to use this: the extra five topics are **not examinable for you** at 3 ECTS:
the 3 ECTS topic list has been stable since 2022W and stops at "Deep learning".
But they are what the lecturers work on (graph neural networks and expressivity
are Gärtner's and Malhotra's own research areas), so they are the likely subject
of the *project* and of any research paper you are asked to read. Note 10 is
written at the depth it is for that reason, and note 11 lists the group's own
directions.

## 6. Where to put your hours

The official workload split is explicit [S2], and it is not what you might guess:

| hours | on what |
|---|---|
| 20 h | (re)viewing lectures and lecture materials |
| 10 h | (re)viewing **background material** |
| 10 h | exercises |
| 20 h | **coursework** |
| 15 h | **final project** |
| **75 h** | = 3 ECTS |

**35 of the 75 hours are coursework and project**, nearly half, and they are
where the first hurdle is decided. The course is blended learning: "introductory
online lectures (recorded and/or live)" with "live sessions where the assignments
are discussed" [S1]; the Wednesday slot is labelled *Exercise Sessions*, not
lectures. Treat the recorded material as the lecture and the Wednesday slot as the
place assignments are discussed. The 2025W homepage describes the rhythm: a new
unit about once a week (recordings, notes, notebooks), questions in the TUWEL
forum, live sessions announced in advance [S6]; no 2026W page exists yet [S5].

The 10 h of "background material" is real: the course assumes probability,
linear algebra and convex optimisation. [`../refs/README.md`](../refs/README.md)
gives the reading order.

## 7. A realistic preparation plan

1. **Before 07.10.2026.** Register in TISS (window in §4), **check TUWEL** for
   the actual deadlines, and put them in a calendar: they are the only dates that
   matter and they are not public.
2. **Throughout.** Do the coursework *on time*; it is mandatory and half the
   first hurdle. When a task says "understand and explain a proof" [S6], that is
   a rehearsal for the oral; write it out properly.
3. **Proofs.** Notes 01–06 carry the twelve proofs listed at the end of note 12.
   For the oral, be able to *state* a theorem with its constants and then prove
   it. [`../refs/README.md`](../refs/README.md) names two constants that are
   routinely misquoted.
4. **Project.** Expect it to lean towards the group's research (note 11, §5).
5. **Oral exam.** Use note 12. Remember it is a separate 50 % hurdle.

## What this page cannot tell you

Honest list of what stayed unsourced, because it is not public anywhere:

- The **points split** between coursework and project, and the number of
  coursework assignments. TISS gives only the combined 50 % rule.
- The **format and length of the oral exam**: how long, how many questions,
  whether a blackboard or slides are involved, whether the project is defended
  in the same session.
- **Whether the project is individual or group work.**
- **Any real past question.**
- The **grading scale** above the 50 % thresholds.

All of these are decided in TUWEL, which these notes do not draw on. The contact named on the most recent course page is the person to
ask [S6], bearing in mind that Patrick Indri is not on the 2026W lecturer list.
