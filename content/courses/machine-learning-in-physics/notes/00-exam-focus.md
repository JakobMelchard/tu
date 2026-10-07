# 00 Exam focus: what is assessed and how to prepare

Built from the 2027S and 2026S TISS pages [S1, S2, S3], the lecturer's public
course page, exercise notebooks and lecture videos [S4, S5, S11], and VoWi [S12],
all read 2026-09-28. The course is **offered in summer semesters**; nothing here
has been checked in TUWEL or JupyterHub.

## 0. Status as of 2026-09-28

| what | state | source |
|---|---|---|
| 2027S TISS page | **published** | [S1] |
| Type | VU, 3.0 h, 5.0 ECTS, English, "immanent" (continuous assessment) | [S1] |
| Place in the curriculum | **mandatory elective** in 066 558 QIST | [S1] |
| Introduction | **Wed 03.03.2027 16:00-17:00**, FAV Hörsaal 1 Helmut Veith | [S1] |
| Lecture | **Fri 12:00-14:00**, Hörsaal 6 RPL, **05.03.2027-25.06.2027** | [S1] |
| Test 1 | **Wed 05.05.2027 16:00-18:00**, FAV Hörsaal 1 | [S1] |
| Test 2 | **Wed 23.06.2027 16:00-18:00**, Hörsaal 6 RPL | [S1] |
| Registration | **07.03.2027 10:30 - 14.03.2027 12:00**; deregistration until **19.03.2027 23:00** | [S1] |
| Grade | weekly coding exercises **40 %** (equal weight, JupyterHub notebooks) + two written tests **30 % each** | [S1, S2] |
| Scale | Genügend **above 1/2**, Befriedigend **2/3**, Gut **4/5**, Sehr gut **9/10** of the points | [S1] |
| Q&A sessions | weekly, recommended, not compulsory; **not in the TISS date table**, time unknown | [S1] |
| Lecturers | Andergassen, Ipp, Smolyanyuk, Wallerberger (E138); 2026S listed eight. Wallerberger's version won TU Wien's Best Lecture 2023 | [S1, S3, S4, S13] |
| Stale rows on the 2027S page | exam table still shows the **2026S retake, Mon 05.10.2026** (registration 03.-10.07.2026); "General Kick-off meeting ... 2 March 2026" | [S1] |
| TUWEL | 2027S page links no TUWEL course yet | [S1] |
| Follow-up | **138.129 Machine Learning and Data Compression in Physics PR**, offered in winter semesters: [`../../../ws2027/machine-learning-and-data-compression-in-physics/`](../../machine-learning-and-data-compression-in-physics/index.md) | [S37] |

Note that the intro on 03.03 comes *before* the registration window (07.03-14.03.2027) opens.


## 1. The 40/30/30 arithmetic

Let $e,t_1,t_2\in[0,1]$ be the fractions scored. The grade fraction is

$$p=0.4\,e+0.3\,t_1+0.3\,t_2=0.4\,e+0.6\,\bar t,\qquad \bar t=\tfrac12(t_1+t_2).$$

Solving $p\ge p_\text{grade}$ for the required test average:

| exercises $e$ | pass ($p>1/2$) | Befriedigend ($2/3$) | Gut ($4/5$) | Sehr gut ($9/10$) |
|---|---|---|---|---|
| 1.0 | $\bar t>16.7\,\%$ | $44.4\,\%$ | $66.7\,\%$ | $83.3\,\%$ |
| 0.9 | $23.3\,\%$ | $51.1\,\%$ | $73.3\,\%$ | $90.0\,\%$ |
| 0.8 | $30.0\,\%$ | $57.8\,\%$ | $80.0\,\%$ | $96.7\,\%$ |
| 0.6 | $43.3\,\%$ | $71.1\,\%$ | $93.3\,\%$ | impossible |

Consequences:

- **The exercises are the cheapest points.** With about 12 weekly notebooks [S1]
  of equal weight, each is worth $\approx 3.3\,\%$ of the final grade. Missing two
  moves the Sehr gut bar from $83\,\%$ to $94\,\%$ on the tests.
- **The tests decide the grade.** With full exercises, a pass is almost free;
  every grade step costs $\approx 22$ test-percentage points ($\Delta p/0.6$).
- TISS states **no per-component minimum**. Whether a test can be failed on its
  own and still pass the course is unverified; ask at the intro.
- The 2021S notebooks were "graded using JupyterHub and nbgrader" [S5]: visible
  `assert` cells plus, typically, hidden tests. Passing the visible asserts is
  not proof of full marks.

## 2. What the tests likely ask

**No past test is public.** VoWi is empty with no attachments [S12]; the public
notebooks contain exercises only [S5]; the video channel has lectures only [S11].
TISS says the tests check "that you understood the concepts" [S2]. The best
available proxy is the free-text "YOUR ANSWER HERE" questions of the 2021S
notebooks [S5], which are conceptual and short:

| notebook | question type (paraphrased) | our note |
|---|---|---|
| Ex01-02 GD | effect of $\eta$, starting point, momentum $\gamma$; step size that reaches the minimum in one step | 01 |
| Ex03 Newton | classify stationary points via the Hessian; why GD lands off the minimum; Newton vs GD from a saddle | 01 |
| Ex05-06 SVD | **prove** the SVD form of $(X^TX+N\lambda^2)^{-1}X^T$; why pinv coefficients explode; which singular vectors carry noise | 02, 03 |
| Ex07 deblurring | why spectra get spiky with more GD steps; why early stopping helps; why SGD saturates above GD | 03, 10 |
| Ex08-09 SUSY | imbalance, sensitivity vs specificity; which features fail; why more neurons need not help | 04, 05, 10 |
| Ex10-11 Ising | what the k-means clusters are; role of the $\mathbb Z_2$ symmetry; "randomness is information" | 06, 07, 10 |
| Ex12 CartPole | observation/action/reward; Markovian?; state vs observation | 09 |

Expect short derivations by hand (a GD step on a quadratic, a $2\times2$ SVD or
PCA, a logistic gradient, one backprop step, one k-means iteration, one Bellman
update) and interpretation questions. Every note ends with five such questions.

**Which topics in which test** is not published. By lecture order [S2, S11] and
dates, test 1 (05.05, a little past the middle of the 05.03-25.06 period) plausibly covers
optimisation, supervised learning and regularisation, the linear model and SVD,
possibly classification; test 2 (23.06) the rest (neural networks, clustering,
PCA, autoencoders, RL). Whether test 2 is cumulative: **unverified**.

## 3. How to spend the hours

5 ECTS = 125 h. A defensible split, given 40/60:

1. **Weekly (about 5 h/week):** watch the matching 2021-2023 videos [S11] before
   the Friday lecture if the 2027S lecture follows the same order, do the
   notebook, then the matching note's questions.
2. **Before each test (about 15 h each):** redo the hand derivations of notes
   01-04 (test 1) or 04-09 (test 2); run `src/py` demos and predict their output
   first.
3. **Exercise domains:** note 10 is the physics glue; the tests may ask why a
   method works *on that physics problem* (e.g. why PC1 of Ising configurations is
   the magnetisation).

The general-ML background (evaluation metrics, model selection, trees, SVMs) is in
the CSE notes [`../../../../cse/ws2026/machine-learning/notes/`](../../machine-learning/notes/README.md);
read those for depth, these for the physics and the course's own topic list.

## 4. To verify at the intro, 03.03.2027

- Test format: closed or open book, formula sheet, calculator, duration within the
  16:00-18:00 slot.
- Minimum per component or per test; what happens if a test is missed.
- **Retake:** 2026S had a written exam on 05.10.2026 [S1, S3]. Is it a retake of
  one test, of both, or a full exam; how is it weighted?
- Exercises: number of notebooks, deadlines, hidden tests, late policy, individual
  or group work, whether TUWEL or only JupyterHub is used.
- When and where the weekly Q&A is (not in TISS).
- Whether autoencoders and Q-learning (newest topics; no autoencoder video exists
  in the public channel [S11]) are on test 2.

## What this page cannot tell you

Any real past test question; the points split inside a test; exercise deadlines;
the Q&A slot; whether the 2027S exercises reuse the public 2021S notebooks. All of
these live in TUWEL/JupyterHub or are announced at the intro.
