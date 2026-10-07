# 00 What is actually assessed

**There is no written exam in 194.077.** The mode of examination is *immanent*
[S1]: you are graded continuously on what you hand in. There is no question
catalogue to learn, no past papers exist, and VoWi's page for the course has an
empty "Prüfung, Benotung" section for exactly that reason [S11]. What this page
documents instead is the thing that *is* assessed — five deliverables, fifty
points, five criteria — sourced from the lecturer's own preliminary lecture [S5]
and from the three official assignment sheets [S12, S13, S14].

Everything below was read on 2026-09-22. Sources registered in
[`../refs/SOURCES.md`](../refs/SOURCES.md).

**Why this page can be specific where other courses' cannot.** Alexander Pacha
publishes the entire lecture series publicly on YouTube, re-recorded every year
[S4, S8, S11], and the three assignment sheets are on VoWi [S12–S14]. The
course's contract is therefore fully public before you register. Read Lecture 0
[S5] — 17 minutes — before the registration deadline.

---

## The five graded parts and the fifty points

| # | part | when | max | source |
|---|---|---|---|---|
| 1 | **Assignment 1 — Initiate**: topic, papers, dataset, work-breakdown structure | ~3 weeks after the preliminary lecture | **10** | [S12] |
| 2 | **Assignment 2 — Hacking**: working pipeline, trained model, metric vs. target | end of the lecture period | **10** | [S13] |
| 3 | **Assignment 3a — Demo application** | day before the first presentation slot | **10** | [S14] |
| 4 | **Assignment 3b — Final report**, ≤ 5 pages, one PDF | same | **10** | [S14] |
| 5 | **Assignment 3c — Presentation**, ≤ 4 minutes, live and in person | in one of the last three lectures | **10** | [S14] |
| | | | **50** | |

This is what [S5] means by "there are five parts … the three assignments, the
report and the presentation". TISS's "three parts … graded separately" [S1] is
the same thing counted by assignment rather than by deliverable; the two are not
in conflict, but the five-way split is the one that maps onto points.

**The grade boundaries are shown on a slide in Lecture 0 [S5] but are not
spoken, and no public source states them.** *(unsourced: the mapping from points
to the grades 1–5 is announced in the preliminary lecture; assume nothing.)*
What is sourced is that **you are told your points after each assignment**, so
you always know where you stand [S5].

### The five criteria, applied to every assignment

Each assignment is graded on these, "as applicable" [S12, S13, S14]:

1. **Results** — but explicitly *not* only whether you won. [S5]: if you attempt
   *Beat the stars* and only reach the baseline, "failure would still be
   acceptable … if you can show afterwards that you apply the correct practices
   but still the problem maybe was too hard". What is not acceptable is "just
   being lazy and not handing anything in".
2. **Creativity** — the topic is yours; a rote MNIST classifier scores badly here.
3. **Complexity** — of the problem, not of the code.
4. **Code quality** — see below. This is a real, weighted criterion, not a
   formality.
5. **Presentation** — of the deliverable in question, i.e. also of the README and
   the report, not only of the four-minute talk.

### Late policy

**−1 point per day**, applied per assignment, with no cap mentioned [S12, S13,
S14]. Two days late caps you at 8/10. The **presentation is exempt**, because it
is live: if you are absent it is **0 points**, and if you know in advance you
cannot make one of the three dates you are to e-mail the lecturers and an
arrangement is made [S14].

---

## What "code quality" concretely means here

This is the part students underestimate, and [S13] spells it out. It is a
software-engineering checklist, and it is graded:

- **Intention-revealing names.** `input_image`, `number_of_epochs`,
  `training_batch_size`; short names only in small scopes (`i` in a loop);
  abbreviations avoided unless the abbreviation is the better-known form (HTML,
  XML, HTTP).
- **Documentation that explains *why***, not what. Architectural diagrams count.
  A comment "computes the scaling factor" above `compute_scaling_factor()` is
  named as an example of a useless comment.
- **Tests.** "At least a few tests that make sure your pre-processing and
  post-processing work correctly." Testing the training procedure itself is
  *not* mandatory — but it earns **bonus points**, and the sheet suggests how:
  train on the CI's CPU on a tiny fraction of the data for a single epoch.
  Test-first is recommended.
- **Runnable, with green tests, documented.** A CI server that builds and tests
  on every commit is the recommended way to demonstrate this.
- **Pinned environment.** State the Python version and provide at least a
  `requirements.txt`; `uv`, Poetry or Pipenv preferred.
- **Auto-formatted** with `black` or `ruff` before submission.
- **No binaries in Git.** Training data and model weights go to GitHub releases,
  not into the repository. Git LFS is possible but quota-limited.

The repository itself is the submission vehicle for assignments 1 and 2: one Git
repository, named `<matriculation-number>_<subject-description>`, public or
private with read access granted to the tutors [S12]. Submission is by e-mail
with a fixed subject line; the repository link is given once, in assignment 1.

---

## The four project types

These are **official and named** [S5, S12], not an informal taxonomy. Pick one in
assignment 1. Each has a stated bonus-point condition.

| type | what you do | bonus point if |
|---|---|---|
| **Bring your own data** | Collect a comprehensive dataset semi-automatically (hundreds to thousands of samples) and annotate it. You must still train and run at least a simple network on it, to establish a baseline for future users. | you publish the dataset at the end of the course |
| **Bring your own method** | Build or re-implement an architecture on an existing public dataset. It should reflect the state of the art; using an existing implementation is fine, but you must alter it and try to improve the results. | you improve on the state of the art |
| **Beat the classics** | Pick a problem with an established *traditional* algorithm (edge detection is the sheet's example) and solve it with deep learning instead. **Both approaches must be evaluated with the same metric.** | your approach beats the traditional one |
| **Beat the stars** | Take a recent idea (deformable convolutional layers [S41] is the sheet's example) and try to beat the current state of the art. Beating a result up to a year old is acceptable given the pace of the field. | you beat it — and you may then consider publishing |

[S5] recommends *Beat the stars* "only to advanced students, potentially some
PhD students". *Beat the classics* is described there as "one of the more
challenging project types".

The topic list in [S12] is inspiration, not a menu: computer vision
(classification, detection, segmentation, style transfer, text recognition,
colourisation, image generation), audio (genre classification, beat/key/onset/
tempo tracking, source separation, generation, harmonisation), NLP (fake-news
detection), RL (cart control, chess). Kaggle, Papers With Code and Hugging Face
are named as places to look.

---

## Assignment 1 — Initiate

Deliverables [S12]:

1. References to **at least two** scientific papers related to your topic.
2. The topic.
3. The project type.
4. A written summary containing:
   a. the project idea and the approach you intend to use;
   b. the dataset you will use or collect;
   c. **a work-breakdown structure with time estimates in hours**, for six named
      buckets: dataset collection; designing and building the network; training
      and fine-tuning it; **building an application to present the results**;
      writing the final report; preparing the presentation.

A README (Markdown) or a PDF, in the Git repository. Use a spell-checker.

Two things follow from (c) that are easy to miss. First, *building an
application* is a first-class, estimated task from week one — assignment 3 is
graded on it [S14], so a project whose output cannot be demonstrated
interactively is a bad choice. Second, you will later be asked for the
**actual** hours against these estimates [S13, S14], so estimate honestly rather
than optimistically; the estimate's accuracy is what you have to discuss, not
its ambition.

[S5]: "After sending your submission, please start immediately with the second
assignment."

---

## Assignment 2 — Hacking

The sheet gives a four-step recommended approach [S13], which is Goodfellow
chapter 11 [S15] and Lecture 5 [S4] in four lines:

1. **Specify an error metric and a reasonable target value for it** — before
   training anything.
2. **Establish a working end-to-end pipeline as a baseline.** The sheet links
   [`ashleve/lightning-hydra-template`](https://github.com/ashleve/lightning-hydra-template)
   [S97] as a suitable starting structure.
3. **Instrument the system** to detect the defects or bottlenecks that cause
   under- or overfitting.
4. **Iterate incrementally**: more data, adjusted hyperparameters, a changed
   algorithm as insight accumulates.

Deliverables: the implementation in the repository, plus a brief README summary
of the metric, its target, the **achieved** value, and the time spent per task
from your own work-breakdown structure.

**The time you spent does not affect the grade** [S13]. It is collected so you
learn to estimate. Report it accurately.

If you chose *Bring your own data*, you still have to build and train a pipeline,
even a very simple one; its results are the baseline for your dataset [S13].

---

## Assignment 3 — Deliver

Three separate deliverables, 10 points each [S14].

### 3a Demo application

"Even the best scientific research is worthless if you can't share your
knowledge and communicate your results." In ascending order of what the sheet
suggests: a command-line tool that takes input and writes a file; that tool
wrapped in a **Docker** container and deployable; or — the option it recommends —
a small **JavaScript web application that runs your trained model in the browser**
with a minimal interface. Named tools: Streamlit, Gradio, ONNX Runtime,
TensorFlow.js, Anvil, Dash. Models are fetched at runtime from a GitHub release,
not committed.

The reference example given is the *Deep Optical Measure Detector*
(<https://measure-detector.edirom.de/>, a Vue.js app, source on GitHub) — the
lecturer's own optical-music-recognition work [S9].

This is Lecture 12's content end to end; see
[`12-serving-and-deployment.md`](12-serving-and-deployment.md). Note the
scheduling trap: **Lecture 12 is among the last of the semester, after
assignment 2 is due.** Watch the previous year's recording early [S4, S6].

### 3b Final report

At most **five pages**, one PDF. Much of it can be lifted from the assignment-1
proposal with edits [S14]. It must answer four questions:

- What is the problem you tried to solve?
- Why is it a problem?
- What is your solution?
- Why is it a solution — and **in particular, why is or is not deep learning a
  solution**?

and additionally cover: the main take-aways and insights (the sheet's own
examples are of the form "batch normalisation improved the results
significantly", "Adadelta worked much better than SGD on my data", "setting up
the pre-processing took much more time than I expected"); what you would do
differently if you did the project again; and how much time you spent versus
your initial estimate, with reasons for any underestimate.

### 3c Presentation

**Must not be longer than four minutes** [S14]. Structure prescribed by the
sheet:

- **first two minutes**: a quick introduction to the topic, the selected
  approach, and the final results;
- **remaining two minutes**: insights you want to share with your colleagues,
  and ideally a small demo.

A PDF or a link to online slides (Canva, Google Slides, PowerPoint Online, Prezi
are named). If you want to demo, **record a screencast and embed it** rather than
demoing live.

Reserve the **full two hours** of each of the last three lecture slots. All
submissions are due **before the first** of the three, and the actual presenters
are **drawn at random** [S5, S14] — which is the reason for that rule, and the
reason there is no way to buy an extra two weeks by presenting last. The
sessions may be streamed for people who genuinely cannot attend, but in-person
is the expectation [S14].

[S5] on the four-minute limit: with 60–70 students there are "quite a couple of
presentations to go through. That's why there is a hard four-minute limit."

---

## The deadline pattern, and the 2026W dates

[S5]: the assignment deadlines "are always the day before one of the lectures",
and the last one is the day before the first presentation slot.

The sheets are from the **2025W** run and carry 2025W dates [S12, S13, S14],
which fit that pattern against the 2025W calendar [S2]:

| | 2025W deadline (official, [S12–S14]) | the lecture it precedes [S2] |
|---|---|---|
| Assignment 1 — Initiate | **Tue 21.10.2025** | Wed 22.10.2025 Q&A |
| Assignment 2 — Hacking | **Tue 16.12.2025** | Wed 17.12.2025 Q&A |
| Assignment 3 — Deliver | **Tue 13.01.2026** | Wed 14.01.2026, first presentation slot |

Applying the same pattern to the 2026W calendar [S1] gives the following.
**These three dates are inferred, not announced.** The official 2026W dates come
from the preliminary lecture on 07.10.2026 and from ILEA/TUWEL; overwrite them
the moment you have them.

| | 2026W, **inferred** | anchor in the 2026W calendar [S1] |
|---|---|---|
| Assignment 1 — Initiate | ~Tue **27.10.2026** | three weeks after the preliminary lecture, as in 2025W |
| Assignment 2 — Hacking | ~Tue **15.12.2026** | day before the last weekly Q&A, Wed 16.12.2026 |
| Assignment 3 — Deliver | **Tue 12.01.2027** | day before the first presentation slot, Wed 13.01.2027 — this one follows directly from the stated rule and is the most reliable of the three |

Fixed, official 2026W dates [S1]:

| date | time | what |
|---|---|---|
| 30.07.2026 10:00 – 07.10.2026 23:59 | | registration window (TISS) |
| Wed 07.10.2026 | 16:00–17:00 | **preliminary lecture**, Zoom — the deadlines are announced here |
| 14.10.2026 23:59 | | deregistration deadline |
| Wed 14.10.2026 – 16.12.2026 | 16:00–17:00 | weekly Q&A, Zoom |
| Thu 07.01.2027 | 16:00–17:00 | Q&A, Zoom |
| Wed 13.01, 20.01, 27.01.2027 | **10:00–12:00** | **presentations, FAV Hörsaal 1, in person** |

Note the time change: presentations were 16:00–18:00 in 2025W [S2] and the
assignment sheet still says so [S14]; for 2026W TISS says **10:00–12:00** [S1].
Reserve the full two hours of all three.

---

## Enrolment and capacity

- **About 60–70 places** [S5], a cap the lecturer has raised over the years and
  keeps because every student gets individual feedback on the project and the
  code. TISS shows no group registration and no explicit limit [S1], so the cap
  is administered by hand.
- Registration questions go to Alexander Pacha, **with your matriculation
  number** [S1]. Horst Eidenberger is the co-lecturer of record [S1, S10]; all
  public course material is Pacha's.
- [S5] asks, in so many words, that you not take a place and then drop out after
  assignment 1: "just be fair to your colleagues."
- 066 646 CSE: **elective** [S1]. It was *not specified* for CSE as recently as
  2024W [S3].

## Workload — the numbers disagree, and you should know by how much

| source | figure |
|---|---|
| TISS ECTS breakdown [S1] | 75 h total: 16 lecture, 45 programming, 10 report and presentation, 4 presenting |
| Lecturer [S5] | "in theory you can probably code this project in 40 to 50 hours", but students "often spend upwards of **100 hours**" |
| A student on VoWi [S11] | **61 h** including watching the lectures, grade 1 |

The spread is real and it is the project type that drives it. A *Bring your own
method* project on a public dataset is nearer 60 h; a *Beat the stars* attempt or
a data-collection project is where the 100 h comes from. [S5] is blunt: sign up
only if you have the capacity.

## Two facts that surprise people

- **Work is individual.** [S1]: "Exercises have to be solved by each student
  individually." [S5] encourages talking to colleagues, asking questions in the
  forum, and helping peers — but the implementation is yours alone. VoWi lists
  "no group work" as a highlight [S11].
- **You bring your own compute.** [S5]: "You unfortunately also have to bring
  your own computing resources." A modern GPU trains smaller models locally;
  otherwise Google Colab, which is also how the lecture's own code examples are
  shared. Budget for this in the assignment-1 work-breakdown structure — on a
  laptop, a training run you cannot finish is the classic way to lose points in
  assignment 2.

## And two the lecturer says that TISS contradicts

Recorded because both are in the sources and they disagree:

- TISS [S1] says taking **183.663 Deep Learning for Visual Computing first** is
  highly recommended. [S5] says the opposite: "In case you haven't taken it
  before, I recommend taking it maybe **after** this lecture", and VoWi reports
  "no strict prerequisites since students choose their own projects based on
  their skill level" [S11]. Treat 183.663 as complementary, not as a gate; its public material is at [S18].
- TISS's Teaching-methods block describes three phases and then refers to "the
  results from those **four** phases" [S1]. There are three assignments. The
  "four" is a leftover in the TISS text and has been there unchanged since at
  least 2024W [S2, S3].

---

## Preparation checklist

Not exam revision — there is no exam — but the things that cost points if left
undone. Ordered by when they bite.

**Before registering.** Watch Lecture 0 [S5]. Confirm you have ~70 h and a
machine (or a Colab budget). Confirm the four-minute in-person presentation dates
are ones you can attend.

**Week 1–3 (assignment 1).** Two papers read, not skimmed. A dataset whose
licence you have actually checked. One of the four project types named
explicitly. A work-breakdown structure with an hours column that includes
*building the demo application*. A Git repository with the required name, and
read access granted.

**Week 3–11 (assignment 2).** An error metric and a target value written down
before the first training run. An end-to-end pipeline that produces a number in
week 4, however bad. Tests for pre- and post-processing. CI green.
`requirements.txt` pinned. `ruff`/`black` clean. No weights in Git. A running log
of hours per task.

**Week 11–14 (assignment 3).** A demo someone else can run — the browser or
Docker route, not "clone my repo and install CUDA". A five-page PDF that answers
the four questions and states time-spent versus estimate. Slides that fit in four
minutes: that is roughly **four to six slides**, with the first half on
problem/approach/result and the second half on insights. A recorded screencast if
you want to show the demo. Everything submitted before the *first* presentation
slot, because you may be called in it.
