# Sources — 184.702 Machine Learning

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). Retrieval dates are the day the page or file
was fetched; TISS and VoWi change, so re-check before an exam.

**Citation form.** The notes cite an entry as `[S<n>]`, optionally with a
locator — `[S23 §3.4]`, `[S26 ch. 9]`, `[S21 §2.4]` — and several together as
`[S12, S18]`. **Every entry below is cited somewhere**; an entry that ends up
supporting nothing is withdrawn rather than left in the register, which is why
the numbering has a gap at S19 (see "Sources deliberately not used").

**Vendoring policy.** Nothing in this directory is a third-party file. The
course's own material lives in TUWEL, which needs a login and is not ours to
copy. Everything below is either a live web page (cited) or a PDF whose licence
could not be established (cited, with a fetch command in
[`fetch-sources.sh`](fetch-sources.sh) so it can be downloaded for personal use
into the git-ignored `vendor/`). See [`README.md`](README.md).

**The one-line summary of what this register found.** This course has *no*
public lecture script. All five lecturers were checked; none hosts slides. What
*is* public is an unusually deep exam archive on VoWi — 17 transcribed papers
from 2017 to 2026 plus a 24-page answered question catalogue — and it shows the
examined scope is materially wider than the TISS subject line suggests:
**reinforcement learning, CNNs, AutoML/metalearning, 1R and rule learning, and
ML security** are all examined and were all missing from the notes.

---

## Course-authoritative

### S1 — TISS course page, 184.702 Machine Learning, 2026W (the semester studied) ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184702&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript for the DeltaSpike window id)
- Re-read: 2026-09-27 in a logged-in browser. **No field changed.** Dates as
  transcribed: lectures Tue 08:00-10:00 (06.10.2026-26.01.2027) and Thu
  16:00-18:00 (08.10.2026-14.01.2027), both HS 17 Friedrich Hartmann; exams
  26.01.2027 (registration 03.01.-21.01.2027) and 04.03.2027 (03.02.-01.03.2027),
  times not published, plus a 23.06.2027 row, all three with stale
  2025W / 2026S labels; course registration until 02.10.2026 12:00,
  deregistration until 05.10.2026 18:00; TUWEL course from 01.10.2026.
- Access: public, no login
- Used for: scope ("Subject of course", learning outcomes), lecturers
  (Musliu, Rauber, Gärtner, Mayer, **Kletzander**), ECTS (4.5, 3.0 h, VU,
  immanent), dates, registration windows, examination modalities
  ("Solving of exercises … using a software toolkit of the student's choice …",
  "Written exam at the end of the semester"), curricula (066 646 CSE: elective),
  literature (**"No lecture notes are available."**), ECTS breakdown
  (13 classes 26 h / 2 presentation classes 8 h / assignments 46.5 h / exam 32 h).
  Diffed against [`../docs/tiss.md`](../docs/tiss.md); see
  `../notes/CHANGELOG.md`.

### S2 — TISS course page, 184.702, 2025W (previous winter offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184702&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public
- Used for: the year-on-year diff. Four lecturers (no Kletzander); a separate
  preliminary-talk slot Thu 02.10.2025 16:00 EI 3; the Thursday lecture in
  EI 9 Hlawka rather than HS 17; two extra "AI Festival" slots
  (02.12.2025 EI 7, 03.12.2025 EI 8); registration 30.07.2025–03.10.2025.
  Everything else byte-identical to S1.

### S3 — TISS course page, 184.702, 2024W (two winter offerings back)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=184702&semester=2024W&locale=en>
- Retrieved: 2026-09-22. Access: public
- Used for: the diff. Four lecturers; preliminary talk 01.10.2024 17:00 EI 9;
  registration 31.07.2024–30.09.2024. **Curricula differ**: 066 646 CSE was
  "Not specified" (it became "Elective" in 2025W), and 066 931 Logic and
  Computation, 066 937 SE&IC and 860 GW were still listed — they moved to S4.

### S4 — TISS course page, **192.183 Machine Learning**, 2026S — the sibling course ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192183&semester=2026S&locale=en>
- Retrieved: 2026-09-22. Access: public
- Used for: **the "similarly named LVA" check, which came out the opposite way
  round from usual.** 192.183 is a *new, larger* Machine Learning course
  (VU, 4.0 h, **6.0 ECTS**, lecturers **Bellec**, Musliu, Marty) that first ran
  in 2026S for the new curricula 066 931 Logic and AI (mandatory, 2nd sem.),
  066 937 Software Engineering and 066 926 Business Informatics. Its stated
  scope adds *machine-learning theory*, *reinforcement learning and the main
  tabular methods*, and *automated machine learning* explicitly, and its
  examination modalities are **50 % written exam + 50 % projects**.
  VoWi files S10/S11 merge the two course numbers onto one page, so exam
  material dated 2026S belongs to **192.183, not to this course** — see S16.
  It also shows where the extra topics in the 184.702 exams come from: the two
  courses share Musliu and a large part of the syllabus.

### S5 — Nysret Musliu, DBAI staff page

- URL: <https://www.dbai.tuwien.ac.at/staff/musliu/> and
  <https://informatics.tuwien.ac.at/people/nysret-musliu>
- Retrieved: 2026-09-22. Access: public
- Used for: confirming that the teaching section links only to the TISS pages of
  184.702 and 181.190 and hosts **no slides, notes or past papers**. Research
  group: Databases and Artificial Intelligence, E192-02.

### S6 — Andreas Rauber, IFS / TU Wien Informatics

- URL: <https://www.ifs.tuwien.ac.at/~andi/> and
  <https://informatics.tuwien.ac.at/people/andreas-rauber>
- Retrieved: 2026-09-22. Access: public
- Used for: the same check. No 184.702 material is public; the IFS teaching
  pages that do exist cover Information Retrieval, not this course.

### S7 — Thomas Gärtner, Machine Learning research unit (E192-06)

- URL: <https://ml-tuw.github.io/> and <https://ml-tuw.github.io/teaching/>
- Retrieved: 2026-09-22. Access: public
- Used for: the same check. The unit publishes per-semester pages for
  *Introduction to Machine Learning* (bachelor, 6 ECTS), *Theoretical
  Foundations and Research Topics in ML*, and the ML project course — but **not**
  for 184.702. Confirms 184.702 is not one of the unit's own lectures even
  though Gärtner co-teaches it.

### S8 — Rudolf Mayer, SBA Research

- URL: <https://www.sba-research.org/team/rudolf-mayer/>
- Retrieved: 2026-09-22. Access: public
- Used for: lecturer identity; he leads SBA's Machine Learning and Data
  Management group, which is where the "ML security / privacy / explainability"
  block of the lecture and the sibling course 194.055 come from.

### S9 — Lucas Kletzander, TU Wien Informatics

- URL: <https://informatics.tuwien.ac.at/people/lucas-kletzander>
- Retrieved: 2026-09-22. Access: public
- Used for: identifying the **lecturer added for 2026W** [S1 vs S2]. DBAI
  (E192-02), Musliu's group; research on automated algorithm selection and
  configuration for scheduling. No public 184.702 material.

---

## Student-reported (VoWi)

VoWi is the TU Wien informatics student wiki. It is a *secondary* source:
excellent for exam format and past questions, unreliable for statements of
theory. The site runs an Anubis proof-of-work bot gate, so plain HTTP clients
get a challenge page; everything below was read through a browser (the MediaWiki
`api.php` works once the gate cookie is set).

### S10 — VoWi course page: `TU Wien:Machine Learning VU (Musliu)` ★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)>
- Retrieved: 2026-09-22 (page id 12343, last edit 2026-03-04)
- Access: public
- Used for: the exercise structure across a decade (2 → 3 group assignments in
  groups of 3; WS15 regression / classification / WEKA-API; WS18 regression /
  classification / free choice incl. CNN; SS21 the three-assignment shape that
  is still current), the reported exam style ("At least last two exams (WS2022)
  were entirely MC tests, no open questions"; "make sure you know the most
  current [true/false] questions"; "there's always one [Naive Bayes
  calculation] in each exam"), Rudolf Mayer's written exercise feedback
  (preprocessing-before-splitting, experiment design, metric choice, report and
  presentation rules) which is quoted almost verbatim in
  [`../notes/17-exercise-playbook.md`](../notes/17-exercise-playbook.md), the
  workload complaint (students report the course is worth 6 ECTS of work, not
  4.5), and the note that Musliu "has no slides of his own" and works from
  freely downloadable books — which is how S21 was identified.
  **Caveat:** the page's own `LVA-Daten` block says `ects=6.0` and
  `id=192183; 184702`; that is the *sibling* course S4, not 184.702.

### S11 — VoWi exam transcripts, 2017–2026 (17 pages) ★★

All are subpages of S10. Student transcripts from memory; no marking scheme is
attached to most of them. Retrieved 2026-09-22.

| our label | page | term |
|---|---|---|
| **E26a** | [`/Exam 2026-01-27`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2026-01-27) | 2025W main |
| **E25b** | [`/Exam 2025-06-25`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2025-06-25) | 2025S main |
| **E24a** | [`/Exam 2024-01-23`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2024-01-23) | 2023W main |
| **E23a** | [`/Exam 2023-01-24`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2023-01-24) | 2022W main |
| **E22b** | [`/Exam-2022-06-30`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam-2022-06-30) | 2022S |
| **E22a** | [`/Exam 2022-01-28`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2022-01-28) | 2021W main |
| **E21d** | [`/Exam 2021-12-07`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2021-12-07) | 2021W |
| **E21c** | [`/Exam 2021-10-21`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2021-10-21) | 2020W re-take |
| **E21b** | [`/Exam 2021-06-24`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2021-06-24) | 2021S — the longest transcript |
| **E21a** | [`/Exam 2021-01-25`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2021-01-25) | 2020W main |
| **E20c** | [`/Exam 2020-09-09`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2020-09-09) | 2019W/2020S |
| **E20b** | [`/Exam 2020-06-25`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2020-06-25) | 2020S |
| **E19b** | [`/Exam 2019-10-18`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2019-10-18) | 2018W re-take |
| **E19a** | [`/Exam 2019-06-27`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2019-06-27) | 2019S |
| **E18a** | [`/exam 2018 01 26`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/exam_2018_01_26) | 2017W — has the point split |
| **E17b** | [`/Exam 2017 06 14`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Exam_2017_06_14) | 2017S |
| **E17a** | [`/Prüfung 2017-03-17`](https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_VU_(Musliu)/Prüfung_2017-03-17) | 2016W re-take |

- Used for: **everything in [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)** —
  the paper structure and its evolution (long-answer 2017–2021 → all
  multiple-choice from 2022W), the three-section 2024–2026 format with its
  negative marking, the recurring true/false bank, and the five recurring
  calculation types. Also the evidence that RL, CNNs, AutoML and 1R are
  examined. Every exam-style question in the notes that is modelled on one of
  these says so by label.
- **Licence: student-written wiki text. VoWi carries no site-wide free licence
  notice; not vendored.** Nothing is reproduced verbatim in this repo; the
  questions are described in our own words.

### S12 — VoWi file: `Questions previousExams answered2024S.pdf` ★★★ — the single most valuable source

- URL: <https://vowi.fsinf.at/images/6/6b/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_Questions_previousExams_answered2024S.pdf>
  (description page: <https://vowi.fsinf.at/wiki/Datei:TU_Wien-Machine_Learning_VU_(Musliu)_-_Questions_previousExams_answered2024S.pdf>)
- 24 pages, 6.8 MB, text layer present. Retrieved 2026-09-22.
- Access: public download (behind the bot gate). **Licence: a student's own
  answer key, no licence statement ⇒ all rights reserved. Not vendored.**
- Used for: the *answers*. Its own header: "Here you can find all the exam
  questions from VOWI exams posted from 2017 till 2024. … last updated
  24.06.2024", with the explicit disclaimer "No guarantee for the correctness".
  It settles what the lecturers count as correct for ~120 true/false items —
  including several where the expected answer differs from what a textbook
  would say (see the "Where the course's expected answer is not the textbook
  answer" table in [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)).
  Cross-checked against S18 wherever the two overlap; disagreements are flagged.

### S13 — VoWi file: `Formlen ML.pdf` — the course formula sheet ★★

- URL: <https://vowi.fsinf.at/images/6/65/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Formlen_ML.pdf>
- 9 pages, 1.0 MB, mixed text and slide screenshots. Retrieved 2026-09-22.
- Access: public. **Licence: none stated; contains screenshots of the TUWEL
  slides ⇒ not redistributable. Not vendored.**
- Used for: the exact formula conventions the exam expects — min–max scaling,
  $F_1$, RSS, gradient descent, ridge/lasso, the **WEKA error family**
  (MAE, MSE, relative squared error, root relative squared error, relative
  absolute error, correlation coefficient), Naive Bayes, the three d-separation
  cases in the lecture's own wording, entropy/information gain/Gini with the
  lecture's notation $IG(X_A,X_B) = H(X) - p(x_a)H(X_A) - p(x_B)H(X_B)$,
  cross-entropy, majority and weighted majority voting, AdaBoost's
  $\alpha^{(t)} = \tfrac12\log\frac{1-\text{TotalError}}{\text{TotalError}}$ with
  $D_{t+1}(i) = D_t(i)e^{\mp\alpha}$, gradient boosting's logistic link, and
  "degrees of freedom = number of runs − 1" for the paired $t$-test.
  This is what drove the additions to `../src/py/metrics.py`.

### S14 — VoWi file: `PracticalHowTos.pdf` ★★

- URL: <https://vowi.fsinf.at/images/6/6b/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_PracticalHowTos.pdf>
- 4 pages, 252 kB, text layer present. Retrieved 2026-09-22.
- Access: public. **Licence: none stated. Not vendored.**
- Used for: the step-by-step recipes for the four hand-calculation question
  types, in the course's own order: *How to Predict a Class with Naive Bayes*
  (including a fully worked four-row example with the number $0.05555$, which
  `../src/py/test_bayes.py` now reproduces), *How to Build a Decision Tree*
  (three split scores: absolute error rate, information gain, Gini gain),
  *How to Construct a Bayesian Network* (known structure → count
  probabilities + Laplace; unknown structure → maximise
  $\log P(D\mid M) - \alpha\,\#M$ by hill climbing over add/remove/reverse-arc
  neighbourhoods), and *How to do AdaBoost*. It also pins down the course's
  **non-standard Laplace convention** — see the correction table in
  `../notes/CHANGELOG.md`.

### S43 — VoWi file: `Fragenkatalog 2019S.docx` — the older question catalogue ★

*(Numbers are allocation order, not file order; this one was registered after
the primary-source block below.)*

- URL: <https://vowi.fsinf.at/images/0/0d/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Fragenkatalog_2019S.docx>
- 121 kB Word document, title "Aufbereitung Prüfungsfragen vor 2019".
  Retrieved: 2026-09-22.
- Access: public. **Licence: a student's compilation, none stated. Not
  vendored.**
- Used for: the long-answer era that S12 does not cover — the HMM questions
  (S38), the "compare SVM with perceptron" answer the course expects, the SVM
  advantages/disadvantages list, the $C$ and $\gamma$ story
  ("high $C$ → overfit, high $\gamma$ → underfit" as the catalogue puts it),
  the z-score vs min–max answer, the feature-selection method list, and the
  bagging-vs-boosting comparison. Topically organised, which is how the
  per-topic sections of `00-exam-focus.md` are arranged.

### S15 — VoWi file: `Exercise1 ML 2021S.pdf` — a real assignment sheet

- URL: <https://vowi.fsinf.at/images/3/32/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Exercise1_ML_2021S.pdf>
- 4 pages, 64 kB, text layer present. Retrieved 2026-09-22.
- Access: public. **Licence: the lecturers' own assignment sheet, posted by a
  student. Not redistributable, not vendored.**
- Used for: the actual requirements of Exercise 1 (classification): groups of
  exactly 3; 4 datasets × 3 classifiers "from different types of learning
  algorithms"; deliberately diverse datasets (small/large, low/high
  dimensional, few/many classes); several parameter settings per classifier,
  not just the best; significance testing against at least one baseline;
  hold-out vs cross-validation comparison; runtime measurements; a **10–15 page
  report** plus code; a ≤10-minute presentation of 2 of the 3 exercises; and
  the in-class **Kaggle competition**. Rewrote
  [`../notes/17-exercise-playbook.md`](../notes/17-exercise-playbook.md)
  around this.

### S16 — VoWi files: `Exam 2026-06-23 Part2.1.pdf` / `Part2.2.pdf` — **192.183, not this course**

- URLs: <https://vowi.fsinf.at/images/2/22/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_Exam_2026-06-23_Part2.1.pdf>
  and <https://vowi.fsinf.at/images/c/c3/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_Exam_2026-06-23_Part2.2.pdf>
- Retrieved: 2026-09-22. Access: public. Not vendored.
- Used for: the *exclusion*. Part 2.1 states on its own first page:
  "Machine Learning Exam (23rd July 2026) Multiple-Choice Part of Prof. Bellec …
  **Course 192.183, 2026S**". Its questions are deep-learning engineering
  (int8 range, parameter count of a linear layer, FLOPs of $Wx$, Conv1d weight
  count, $\sigma = 1/\sqrt d$ initialisation, softmax-CE derivative
  $p_k - l_k$, decoder-only Transformer next-token loss, peak memory of
  backprop) plus k-means and PCA. That is **S4's** syllabus, not S1's.
  Recorded here so that nobody studies it for 184.702 by mistake — and as
  evidence of where the subject is drifting.

### S17 — VoWi file: `RLbook2020.pdf`

- URL: <https://vowi.fsinf.at/images/4/4c/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_RLbook2020.pdf> (73 MB)
- Retrieved: 2026-09-22 (metadata only; the file itself was not downloaded)
- Used for: **identifying the reinforcement-learning reading.** A student
  uploaded the complete Sutton & Barto book to the course's VoWi page; that is
  the freely-downloadable book S10 says Musliu teaches from. Read the
  authors' own copy instead — **S21**. Not vendored (it is a re-upload of a
  copyrighted book).

---

## Student summaries (secondary, but the only evidence of lecture order)

### S18 — Sueszli, *TU Wien data-science summaries*, `ml - machine learning 184.702` ★★

- URL: <https://github.com/sueszli/tu-wien-data-science-summaries/tree/main/ml%20-%20machine%20learning%20184.702>
  (`summary.md`, `exams.md`, `backprop.md`)
- Linked from S10 as "Sueszli's summary + altprüfungen".
- Retrieved: 2026-09-22 (repo last pushed 2025-12-16)
- Access: public. Licence: **AGPL-3.0** on the repository — but the content is a
  summary of the TUWEL slides, so the student's licence cannot clear the
  underlying material. **Cited, not vendored.**
- Used for: (a) **the lecture unit order**, which nothing else reveals:
  basics/preprocessing → evaluation → kNN → decision trees → naive Bayes →
  Bayesian networks → SVM → MLP → RNN → reinforcement learning → combining
  models (transfer learning, ensembles) → AutoML → ML security → MLOps. See
  [`lecture-notes-map.md`](lecture-notes-map.md). (b) `exams.md` carries two
  papers that are **not** on VoWi, **2023-06-21** and **2023-10-20**, with
  worked answers; both are used in `00-exam-focus.md` (labels **E23b**,
  **E23c**). (c) A second opinion on every answer in S12.

*(S19 was withdrawn — see "Sources deliberately not used". Numbers are not
reused, so the gap is intentional.)*

### S20 — PreyMaTU, *ML25S*

- URL: <https://github.com/PreyMaTU/ML25S> (linked from S10 as
  "GitHub Repo 2025S"). Licence: MIT. Retrieved: 2026-09-22.
- Used for: confirming that the 2025S assignments still had the three-project
  shape of S15. Nothing is copied from it.

---

## Books the course actually works from

TISS says flatly "No lecture notes are available." [S1], so there is no
prescribed textbook. S10 reports Musliu lectures from "books that are free and
available as PDF without registration"; S17 identifies one of them outright.

### S21 — Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press 2018 ★

- URL: <http://incompleteideas.net/book/the-book-2nd.html>, PDF
  <http://incompleteideas.net/book/RLbook2020.pdf> (the exact file name that was
  re-uploaded to VoWi as S17)
- Retrieved: 2026-09-22. Access: free download from the author's page.
  **Licence: © 2014–2018 Sutton & Barto / MIT Press, "may not be reproduced".
  Not vendored.**
- Used for: the whole of [`../notes/14-reinforcement-learning.md`](../notes/14-reinforcement-learning.md)
  — the $k$-armed bandit, sample-average and constant-$\alpha$ incremental
  updates, $\varepsilon$-greedy / optimistic-initial-values / UCB, the MDP
  formalism, the Bellman equations, first-visit Monte-Carlo prediction and
  Monte-Carlo ES control. The exam's bandit and "Monte-Carlo updates only at
  the end of an episode" questions come straight out of its chapters 2 and 5.

### S22 — Witten, Frank, Hall & Pal, *Data Mining: Practical Machine Learning Tools and Techniques*, and WEKA

- URLs: <https://www.cs.waikato.ac.nz/ml/weka/> (WEKA, GPL-2.0),
  book page <https://www.cs.waikato.ac.nz/ml/weka/book.html> (moved; the Waikato
  ML group page above links the current edition)
- Retrieved: 2026-09-22. Book: commercial (Morgan Kaufmann/Elsevier), not free,
  **not vendored**.
- Used for: the provenance of the course's vocabulary and its metric set. WEKA
  is still named in S1's examination modalities and was the exercise tool until
  ~2019 [S10]. The relative error measures on S13 (RAE, RSE, RRSE) and the
  "correlation coefficient" as a regression metric are WEKA's output block, not
  scikit-learn's; **1R** and the **covering algorithm (PRISM)** are chapters of
  this book and appear in the exams. Implemented in
  [`../src/py/rules.py`](../src/py/rules.py) and
  [`../src/py/metrics.py`](../src/py/metrics.py).

### S23 — Hastie, Tibshirani & Friedman, *The Elements of Statistical Learning*, 2nd ed., Springer 2009

- URL: <https://hastie.su.domains/ElemStatLearn/>
- Retrieved: 2026-09-22. Access: the authors host a free PDF; the page permits
  personal download and printing only. **Not vendored.**
- Used for: bias–variance decomposition, ridge via the SVD, lasso soft
  thresholding, CART and cost-complexity pruning, bagging/forests/boosting
  theory, the statement that AdaBoost is forward stagewise additive modelling
  on the exponential loss. Used where the course's own material states a result
  without a derivation.

### S24 — Bishop, *Pattern Recognition and Machine Learning*, Springer 2006

- URL: <https://www.microsoft.com/en-us/research/publication/pattern-recognition-machine-learning/>
  (Microsoft Research hosts a free PDF). Access: free download; © Springer.
  **Not vendored.**
- Used for: the SVM dual and KKT conditions, kernels, EM and mixtures, neural
  network back-propagation notation.

### S25 — Russell & Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed.

- URL: <https://aima.cs.berkeley.edu/>. Access: not free; code and figures are
  free. **Not vendored.**
- Used for: the Bayesian-network chapter — the **alarm network numbers** that
  `../src/py/bayesnet.py` reproduces, d-separation, inference by enumeration and
  variable elimination, "explaining away". The exam's BN questions use exactly
  this vocabulary.

### S26 — Goodfellow, Bengio & Courville, *Deep Learning*, MIT Press 2016

- URL: <https://www.deeplearningbook.org/>
- Retrieved: 2026-09-22. Access: free to read online (HTML per chapter).
  **Licence: © MIT Press; not redistributable. Not vendored.**
- Used for: [`../notes/13-deep-learning.md`](../notes/13-deep-learning.md) —
  convolution arithmetic, pooling, the output-size formula, initialisation,
  batch normalisation, dropout as an ensemble, data augmentation, the
  vanishing/exploding gradient analysis and gradient clipping.

### S27 — Mitchell, *Machine Learning*, McGraw-Hill 1997

- URL: <https://www.cs.cmu.edu/~tom/mlbook.html>
- Retrieved: 2026-09-22. Access: book not free; some chapters are on the page.
  **Not vendored.**
- Used for: the $\langle T, P, E\rangle$ definition of learning quoted in note 01,
  ID3/information gain, the version-space/inductive-bias framing.

### S28 — James, Witten, Hastie & Tibshirani, *An Introduction to Statistical Learning*

- URL: <https://www.statlearning.com/>
- Retrieved: 2026-09-22. Access: free PDF from the authors. **Not vendored.**
- Used for: the gentler statements of cross-validation, the bootstrap, ridge vs
  lasso and tree pruning, at the level the exam actually asks for.

---

## Primary sources for individual results

Each is cited in the note where the result is used.

### S29 — Holte, "Very Simple Classification Rules Perform Well on Most Commonly Used Datasets", *Machine Learning* 11:63–90, 1993

- DOI/URL: <https://link.springer.com/article/10.1023/A:1022631118932>.
  Access: paywalled. Not vendored.
- Used for: **1R**, which appears in more of this course's exams than almost
  anything else (E17b, E18a, E19a, E20b, E21b, E24a, E26a). Defines the
  algorithm (one rule per attribute, majority class per value, pick the
  attribute with the lowest training error) and the small-bucket rule for
  numeric attributes. Implemented in `../src/py/rules.py`.

### S30 — Rice, "The Algorithm Selection Problem", *Advances in Computers* 15:65–118, 1976

- DOI: <https://doi.org/10.1016/S0065-2458(08)60520-3>. Access: paywalled.
  Not vendored.
- Used for: **Rice's framework**, asked by name in E19b, E21b and E21c: problem
  space $P$, feature space $F$, algorithm space $A$, performance space $Y$,
  and the selection mapping $S(f(x))$ that maximises $\|y(a(x))\|$.

### S31 — Wolpert & Macready, "No Free Lunch Theorems for Optimization", *IEEE Trans. Evolutionary Computation* 1(1):67–82, 1997; Wolpert, "The Lack of A Priori Distinctions Between Learning Algorithms", *Neural Computation* 8(7):1341–1390, 1996

- DOIs: <https://doi.org/10.1109/4235.585893>, <https://doi.org/10.1162/neco.1996.8.7.1341>.
  Access: paywalled. Not vendored.
- Used for: the **no-free-lunch theorem**, asked in E20c, E21a, E21c and E21b.
  The course wants the *implication* ("no single algorithm is best on every
  problem; averaged over all problems all algorithms tie; therefore we need the
  closed-classification-world assumption before comparing") rather than the
  proof [S12].

### S32 — Pfahringer, Bensusan & Giraud-Carrier, "Meta-Learning by Landmarking Various Learning Algorithms", ICML 2000, 743–750

- No free author copy located (the Waikato URL that used to serve it now
  returns HTTP 410). ACM DL: <https://dl.acm.org/doi/10.5555/645529.658105>.
  Not vendored.
- Used for: **landmarking features**, asked verbatim in E21b, E21d and E22a
  ("Which features are used in metalearning? What are landmarking features?").

### S33 — Breiman: "Bagging Predictors" (1996) and "Random Forests" (2001)

- URLs: <https://www.stat.berkeley.edu/~breiman/bagging.pdf>,
  <https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf>;
  journal versions <https://link.springer.com/article/10.1007/BF00058655>,
  <https://link.springer.com/article/10.1023/A:1010933404324>
- Retrieved: 2026-09-22. Access: free author copies. **Licence: none stated.
  Not vendored.**
- Used for: the bootstrap, out-of-bag estimation, and the two sources of
  randomness in a random forest — the exact content of "What is the randomness
  in random forests?" (E21b) and "RF heterogeneous ensemble learner?"
  (E17b, E19b).

### S34 — Freund & Schapire, "A Decision-Theoretic Generalization of On-Line Learning and an Application to Boosting", *JCSS* 55(1):119–139, 1997; Friedman, "Greedy Function Approximation: A Gradient Boosting Machine", *Annals of Statistics* 29(5):1189–1232, 2001

- DOIs: <https://doi.org/10.1006/jcss.1997.1504>, <https://www.jstor.org/stable/2699986>.
  Access: paywalled. Not vendored.
- Used for: AdaBoost's $\alpha_m$ and weight update (which S13 states in the
  same form) and gradient boosting's $F_0$ / pseudo-residual construction — the
  basis of the recurring "Is gradient boosting 0 Rule?" question (E24a, E23b,
  E26a; answer: **true** as the course means it).

### S35 — Cortes & Vapnik, "Support-Vector Networks", *Machine Learning* 20:273–297, 1995

- URL: <https://link.springer.com/article/10.1007/BF00994018>. Access: open
  access at Springer. Not vendored (no redistribution notice).
- Used for: the maximum-margin formulation, the soft margin with $C$, the dual
  and the kernel trick, in note 10.

### S36 — Dietterich, "Approximate Statistical Tests for Comparing Supervised Classification Learning Algorithms", *Neural Computation* 10(7):1895–1923, 1998; Nadeau & Bengio, "Inference for the Generalization Error", *Machine Learning* 52:239–281, 2003; Demšar, "Statistical Comparisons of Classifiers over Multiple Data Sets", *JMLR* 7:1–30, 2006

- URLs: <https://doi.org/10.1162/089976698300017197>,
  <https://link.springer.com/article/10.1023/A:1024068626366>,
  <https://www.jmlr.org/papers/volume7/demsar06a/demsar06a.pdf>
- Retrieved: 2026-09-22. Demšar is open access (JMLR); the other two are
  paywalled. Not vendored.
- Used for: why the plain paired $t$-test over CV folds is anti-conservative,
  the corrected resampled $t$-test, and McNemar's test — all of which the
  course examines as *true/false* items about "paired t-tests are used for
  holdout / for cross-validation" (E17b, E18a, E19a, E19b, E20b, E22a, E23b).
  **Note the conflict flagged in `00-exam-focus.md`:** S12 marks *both* the
  holdout and the cross-validation variant "True", while S18 and S36 mark the
  holdout variant False.

### S37 — Bergstra & Bengio, "Random Search for Hyper-Parameter Optimization", *JMLR* 13:281–305, 2012

- URL: <https://www.jmlr.org/papers/volume13/bergstra12a/bergstra12a.pdf>
- Retrieved: 2026-09-22. Access: open access (JMLR). Not vendored.
- Used for: why random search beats grid search at a fixed budget — the
  justification for the exam answer "state-of-the-art AutoML systems use grid
  search: **false**" (E21b, E21c, E23c).

### S38 — Rabiner, "A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition", *Proc. IEEE* 77(2):257–286, 1989

- URL: <https://ieeexplore.ieee.org/document/18626>. Access: paywalled.
  Not vendored.
- Used for: the **three problems of an HMM** (evaluation, decoding, learning),
  asked in E17a and E17b. Marked in note 09 as historical: HMMs appear in no
  paper after 2017.

### S39 — Goodfellow, Shlens & Szegedy, "Explaining and Harnessing Adversarial Examples", ICLR 2015

- URL: <https://arxiv.org/abs/1412.6572>. Access: open (arXiv). **Licence:
  arXiv non-exclusive licence; not vendored** (cited only).
- Used for: the **fast gradient sign method** $x + \varepsilon\,\mathrm{sign}(\nabla_x J(\theta, x, y))$
  in note 16, which S18 records as lecture content.

### S40 — LeCun, Bottou, Bengio & Haffner, "Gradient-Based Learning Applied to Document Recognition", *Proc. IEEE* 86(11), 1998 (LeNet); He, Zhang, Ren & Sun, "Deep Residual Learning for Image Recognition", CVPR 2016 (ResNet)

- URLs: <http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf>,
  <https://arxiv.org/abs/1512.03385>
- Retrieved: 2026-09-22. Access: free author copies / arXiv. Not vendored.
- Used for: the architecture names the exam asks you to recognise — "Which of
  the following are well-known CNN architectures? LeNet / LSTM / ResNet /
  Reception / TeNet" (E25b, E26a).

### S41 — Ester, Kriegel, Sander & Xu, "A Density-Based Algorithm for Discovering Clusters" (DBSCAN), KDD 1996; Chawla, Bowyer, Hall & Kegelmeyer, "SMOTE", *JAIR* 16:321–357, 2002

- URLs: <https://cdn.aaai.org/KDD/1996/KDD96-037.pdf>,
  <https://www.jair.org/index.php/jair/article/view/10302>
- Retrieved: 2026-09-22. Access: free (AAAI / JAIR open access). Not vendored.
- Used for: DBSCAN's core/border/noise definitions (note 12) and SMOTE's
  interpolation rule (note 02).

### S42 — scikit-learn documentation

- URLs: <https://scikit-learn.org/stable/modules/model_evaluation.html>,
  <https://scikit-learn.org/stable/modules/tree.html>,
  <https://scikit-learn.org/stable/modules/ensemble.html>
- Retrieved: 2026-09-22. Access: public. Licence: BSD-3-Clause (redistributable,
  but only cited — there is no need for a copy).
- Used for: the conventions every test in `../src/py` cross-checks against, and
  for S1's own suggestion that scikit-learn is an acceptable exercise toolkit.

---

## Sources deliberately not used

- **TUWEL** (`tuwel.tuwien.ac.at/course/view.php?id=…`). The slides, the
  assignment sheets, the forum and the current exercise data live there, as do
  exercise submission and the lecture recordings
  (the course opens there on 01.10.2026 [S1]). It
  requires a TU Wien login and its contents are not ours to copy. **Not
  fetched.** S13, S14 and S15 are the public stand-ins; they are older
  (2019–2021) and partly out of date, and every note says so where it matters.
- **alexl4123, `ml-summary`** (<https://github.com/alexl4123/ml-summary>, linked
  from S10 as "Summary-source"). Opened on 2026-09-22 and then **withdrawn from
  the register**: it was last touched 2023-02, so it predates the current exam
  format, it carries no licence, and in the end no claim in `../notes` rests on
  it. It briefly held the number S19; that number is not reused.
- **The Kaggle in-class competition** linked from S15: needs an account.
- **The course Mattermost channel** `machine-learning` listed on S10: needs
  registration.
- **`Machine-Learning-Summary-WS-2021-2022.zip`, `Mlsummary.pdf`,
  `Summary.pdf`, `ML S25 Summary Schott.pdf`** and the other student summaries
  in VoWi's file list: redundant with S18, and none carries a licence.
- **`Exam29012020.docx`, `Prüfung 2011-01-27.jpg`, `prf08.042014.txt`,
  `ML Prüfung 2016-05-18 … .jpeg`, `IMG 20110127 141903.jpg`**: pre-2017 scraps
  predating the current syllabus. Not used; listed here so the next pass knows
  they were seen and skipped.
