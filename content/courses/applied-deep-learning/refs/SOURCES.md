# Sources — 194.077 Applied Deep Learning

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). The notes cite these as `[S<n>]`. Retrieval
dates are the day the page or file was fetched; TISS and VoWi change, so
re-check before the semester starts.

**Vendoring policy.** Nothing in this directory is a third-party file. The
course's own slides and submission portal live in TUWEL/ILEA, which needs a
login and is not ours to copy. Everything below is either a live web page
(cited), a YouTube video (cited; captions can be pulled locally with
[`fetch-sources.sh`](fetch-sources.sh)), or a PDF whose licence could not be
established (cited, fetched into a git-ignored `vendor/`). See
[`README.md`](README.md).

**The one-line summary of what this register found.** Unlike most TU Wien
courses, **this one is public in full.** Alexander Pacha publishes the entire
lecture series on YouTube, re-recorded every year, with per-lecture chapter
marks and per-lecture literature lists [S4]; and the three **official assignment
sheets** — the real deliverables, the real deadlines, the real grading rubric
and the real late policy — are on VoWi [S12, S13, S14]. Between them they settle
everything the first writer of these notes had to guess, and they contradict the
guesses in three places that matter: the presentation is **four minutes, not
ten**; the report is **five pages, not four to eight**; and the project types are
a **fixed set of four with names**, not an informal taxonomy. There is **no
written exam** [S1, S5].

---

## Course-authoritative

### S1 — TISS course page, 194.077, 2026W (the semester being studied) ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=194077&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript for the DeltaSpike window id)
- Access: public, no login
- Used for: scope (the eight advanced topics, "the project must use at least one
  of them"), learning outcomes, lecturers (Eidenberger, Pacha), ECTS (3.0, VU,
  2.0 h, blended learning, **mode of examination: immanent**), the ECTS
  breakdown (16 h lecture / 45 h programming / 10 h report and presentation /
  4 h presenting = 75 h), dates, registration window, curricula
  (066 646 CSE: **elective**), literature (Goodfellow et al.), preceding course
  (183.663 Deep Learning for Visual Computing). Diffed against
  [`../docs/tiss.md`](../docs/tiss.md); see
  `../notes/CHANGELOG.md`.
- **Note a defect in the source itself:** the Teaching-methods block describes
  *three* phases and then says the final report "contains the results from those
  **four** phases". The number four is a leftover; every other statement on the
  page, and all of [S5, S12, S13, S14], say three assignments.

### S2 — TISS course page, 194.077, 2025W (previous offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=194077&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public
- Used for: the year-on-year diff, and for anchoring the assignment deadlines in
  [S12, S13, S14] (which are 2025W dates) to the lecture calendar. Preliminary
  lecture 01.10.2025; weekly Q&A 08.10.2025–07.01.2026 plus three extra
  Wed 10:00–11:00 slots 19.11.–03.12.2025; presentations
  **16:00–18:00**, 14.01.–28.01.2026, FAV HS 1; registration
  31.07.2025 10:00 – 02.10.2025 09:00, deregistration to 08.10.2025 14:00.
  Subject, learning outcomes, teaching methods and examination modalities are
  byte-identical to S1.

### S3 — TISS course page, 194.077, 2024W (two offerings back)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=194077&semester=2024W&locale=en>
- Retrieved: 2026-09-22. Access: public
- Used for: the diff, and it produces the single substantive scope change in
  three years: **"Large Language Model" is absent from the 2024W subject list.**
  2024W names seven advanced topics (CNN, RNN, deep RL, autoencoders/generative,
  transformers, GNN, XAI); LLMs were added for 2025W, i.e. the topic list grew
  from seven to eight. Also: format **Online** (not blended); presentations by
  Zoom, not in person; curricula differ — 066 646 CSE was *Not specified*
  (it became *Elective* in 2025W), 066 645 Data Science and 066 932 Visual
  Computing were listed then and are not now.

### S4 — *Applied Deep Learning 2025 — TU Wien*, YouTube playlist ★★★ — the single most valuable source

- Author: Alexander Pacha. 15 videos, ~13 h, published Sept 2025 – Jan 2026.
- URL: <https://www.youtube.com/playlist?list=PLNsFwZQ_pkE8H1o874cZbiwnNRJ6hCDJI>
- Retrieved: 2026-09-22 (titles, descriptions and auto-captions)
- Access: public, no login. **Licence: standard YouTube licence, all rights
  reserved. Not vendored.** [`fetch-sources.sh`](fetch-sources.sh) pulls the
  captions and descriptions into `vendor/` for personal study.
- Used for: **the lecture order, the scope of each lecture, and the per-lecture
  reading list.** This is the course. Each video's description carries
  timestamped chapter marks and a numbered `== Literature ==` block, which is
  where most of the primary sources below (S20–S45) come from. Mapped
  section-by-section onto our notes in
  [`lecture-notes-map.md`](lecture-notes-map.md). The order is:

  | # | lecture |
  |---|---|
  | 0 | Preliminary Information |
  | 1 | Introduction to Deep Learning |
  | 2 | Neural Networks, Optimization, and Backpropagation |
  | 3 | Convolutional Neural Networks and Visual Computing |
  | 4 | Recurrent Neural Networks |
  | 5 | Libraries and Practical Aspects |
  | 6 | Deep Reinforcement Learning |
  | 7 | Autoencoders and Generative Adversarial Networks (GANs) |
  | 8 | Transformers |
  | 9 | Preprocessing, Augmentation, Regularization, Visualization |
  | 10 | Explainable AI |
  | 11 | Graph Neural Networks |
  | 12 | Serving, Optimizing, and Practical Aspects |
  | 13 | Large Language Models (LLMs) |
  | 14 | Outlook, Feedback, and Goodbye |

### S5 — *Applied Deep Learning 2025 — Lecture 0 — Preliminary Information* ★★★

- URL: <https://www.youtube.com/watch?v=vlTnIjhhmzA> (17:40)
- Retrieved: 2026-09-22 (auto-generated English captions)
- Access: public. Not vendored.
- Used for: **everything in [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)
  that the assignment sheets do not state.** In the lecturer's own words:
  grading is "immanent"; there are **five graded parts** (three assignments, the
  report, the presentation); the grading criteria are **results, creativity,
  complexity, code quality, presentation**, with "code quality … an integral part
  of the software development project — name your variables properly, add some
  tests, add documentation"; a **failure is acceptable** if the problem was hard
  and the practice was correct ("just being lazy and not handing anything in
  obviously is not"); points are reported after each assignment so you know where
  you stand; the four project types and the fact that *Beat the stars* is
  "recommended only to advanced students, potentially some PhD students"; the
  assignments are named **Initiate, Hacking, Deliver**; presentations are in
  person with a **hard four-minute limit**; a **cap of about 60–70 students**;
  own compute ("you unfortunately also have to bring your own computing
  resources", Google Colab suggested, and Colab is how the lecture examples are
  shared); individual work; deadlines are "always the day before one of the
  lectures", with everything due before the first presentation slot because
  presenters are drawn at random. Two further points worth recording: students
  "often spend upwards of 100 hours" against a nominal 40–50 h of coding; and
  the lecturer recommends taking 183.663 **after** this course, which is the
  opposite of what S1's Previous-knowledge block says.

### S6 — *Applied Deep Learning 2024 — TU Wien*, YouTube playlist

- URL: <https://www.youtube.com/playlist?list=PLNsFwZQ_pkE8tSQuU3jN71fmmGFFCi7Dc> (14 videos)
- Retrieved: 2026-09-22 (titles only). Access: public. Not vendored.
- Used for: confirming the lecture order is stable, and dating the one change:
  in 2024 *Serving, Optimizing, and Practical Aspects* was Lecture 10 and
  *Explainable AI* Lecture 12; in 2025 XAI moved up to 10, GNNs to 11 and
  Serving down to 12. LLMs are Lecture 13 in both.

### S7 — *Applied Deep Learning 2023 — TU Wien*, YouTube playlist

- URL: <https://www.youtube.com/playlist?list=PLNsFwZQ_pkE87JO3T_mvedVTlw0sjUzKh> (14 videos)
- Retrieved: 2026-09-22 (titles only). Access: public. Not vendored.
- Used for: the same check one year further back, and independent confirmation
  of S3: the 2023 playlist has **no LLM lecture** (its Lecture 13 is the
  epilogue). Older editions exist for 2022, 2021 and 2020 on the same channel.

### S8 — Alexander Pacha, "Deep Learning Course" (personal site)

- URL: <https://alexanderpacha.com/2020/11/18/applied-deep-learning-course/>
- Retrieved: 2026-09-22. Access: public
- Used for: establishing that the YouTube series is the lecturer's own, official
  channel for the course ("This year's edition of the Applied Deep Learning
  course at the TU Wien has moved to YouTube"), and for the 2020 playlist link.
  The site hosts **no slides, notes or past papers**.

### S9 — Alexander Pacha, lecturer

- URLs: <https://www.youtube.com/@AlexanderPacha/playlists>, <https://alexanderpacha.com/>
- Retrieved: 2026-09-22. Access: public
- Used for: lecturer identity and the provenance of the course's running
  examples. PhD in optical music recognition at TU Wien; now a machine-learning
  engineer at Canva [S5]. The OMR work is why music-score detection, the
  *Deep Optical Measure Detector* demo [S14] and the `apacha/OMR-Datasets`
  release [S13] appear throughout the course material.

### S10 — Horst Eidenberger, co-lecturer

- URL: <https://tiss.tuwien.ac.at/person/38133.html> (linked from S1)
- Retrieved: 2026-09-22. Access: public
- Used for: lecturer identity only. E193 Visual Computing and Human-Centered
  Technology. No 194.077 material of his is public; all public course material
  is Pacha's.

---

## The official assignment sheets (student-uploaded, but the lecturers' own documents)

These three PDFs are the graded specification of the course. They are the
lecturers' own documents, uploaded by a student to VoWi. **Licence: none stated
⇒ all rights reserved. Not vendored, and nothing is reproduced verbatim here** —
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) describes them in our
own words. The dates in them are the **2025W** dates; the 2026W dates will be
announced in the preliminary lecture and in TUWEL/ILEA.

### S11 — VoWi course page: `TU Wien:Applied Deep Learning VU (Pacha)` ★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Applied_Deep_Learning_VU_(Pacha)>
- Retrieved: 2026-09-22 (through a browser; the wiki runs an Anubis
  proof-of-work bot gate, so plain HTTP clients get a challenge page)
- Access: public
- Used for: locating S12–S14; the student-reported workload (**61 h total**
  including watching the lectures, for a grade of 1 — against the nominal 75 h
  of S1 and the "upwards of 100 h" of S5, so the spread is wide); the reporting
  turnaround (2024W grades posted **20.02.2025**); the deliverable summary from a
  student's point of view (proposal → code on GitHub → demo video and a 5-page
  report); the eLearning platform being called **ILEA**; the confirmation that
  lectures are pre-recorded and "recorded fresh every year"; and the
  similarly-named-LVA check, which found `Applied Deep Learning VU (Eidenberger)`
  and `Applied Deep Learning VU (Lukasiewicz)` — **both with zero materials**, so
  unlike most TU Wien courses there is no second course number hiding an exam
  archive. There is none because there is no exam.
- **Licence: student-written wiki text; VoWi carries no site-wide free licence
  notice. Not vendored.**

### S12 — *Applied Deep Learning — Assignment 1 — Initiate* ★★★

- URL: <https://vowi.fsinf.at/images/5/5d/TU_Wien-Applied_Deep_Learning_VU_%28Pacha%29_-_Assignment_1_-_Initiate.pdf>
  (description page: <https://vowi.fsinf.at/wiki/Datei:TU_Wien-Applied_Deep_Learning_VU_(Pacha)_-_Assignment_1_-_Initiate.pdf>)
- 4 pages, text layer present. Retrieved: 2026-09-22.
- Used for: the deliverables of assignment 1 (≥2 related scientific papers; the
  topic; the project type; a written summary containing the idea and intended
  approach, the dataset, and a **work-breakdown structure with time estimates in
  hours** for six named buckets); the submission mechanics (a Git repository
  named `<matr-number>_<subject-description>`, read access for the tutors, a
  README or PDF, notification by e-mail with a fixed subject line); the
  **inspiration list of topics** (computer vision, audio processing, NLP,
  reinforcement learning, with sub-items); the **four official project types**
  with their bonus-point conditions; and the **grading rubric** — five criteria,
  **maximum 10 points per assignment** — and the **late policy of −1 point per
  day**. Due date on the sheet: **21 October 2025**.

### S13 — *Applied Deep Learning — Assignment 2 — Hacking* ★★★

- URL: <https://vowi.fsinf.at/images/f/f6/TU_Wien-Applied_Deep_Learning_VU_%28Pacha%29_-_Assignment_2_-_Hacking.pdf>
- 3 pages, text layer present. Retrieved: 2026-09-22.
- Used for: the four-step recommended approach (fix an **error metric and a
  target value for it** first; get an end-to-end pipeline working as a baseline;
  instrument to detect under/overfitting; then iterate); the deliverables (the
  metric, its target, the **achieved** value, and the time actually spent per
  work-breakdown task — with the explicit statement that the amount of time does
  **not** affect the grade); and the course's **software-engineering
  requirements**, which are graded under "code quality": intention-revealing
  names, documentation that explains *why*, **at least a few tests of pre- and
  post-processing** (tests of the training loop itself are optional and earn
  bonus points), a green CI, a pinned Python version and `requirements.txt` (or
  `uv`/Poetry/Pipenv), auto-formatting with `black` or `ruff`, and **no binaries
  in Git** (GitHub releases instead). The sheet's own link list is where our
  `src/project_template` recommendation of
  [`ashleve/lightning-hydra-template`](https://github.com/ashleve/lightning-hydra-template)
  comes from — it is the template the assignment points at. Due: **16 December 2025**.

### S14 — *Applied Deep Learning — Assignment 3 — Deliver* ★★★

- URL: <https://vowi.fsinf.at/images/0/08/TU_Wien-Applied_Deep_Learning_VU_%28Pacha%29_-_Assignment_3_-_Deliver.pdf>
- 3 pages, text layer present. Retrieved: 2026-09-22.
- Used for: the three separate deliverables of the final assignment and the fact
  that the **demo application, the report and the presentation are each worth up
  to 10 points** (which, with S12 and S13, makes the course **50 points over five
  graded parts** and matches S5's "five parts"); the demo-application options
  (CLI tool → Docker container → in-browser JS app, with Streamlit, Gradio, ONNX
  Runtime, TensorFlow.js, Anvil, Dash named, and the *Deep Optical Measure
  Detector* given as the reference example); the **report spec** — at most
  **5 pages**, one PDF, answering *what is the problem / why is it a problem /
  what is your solution / why is it a solution (and in particular why is or is
  not deep learning a solution)*, plus take-aways, what you would do differently,
  and time spent versus estimate; and the **presentation spec** — **must not be
  longer than four minutes**, first two minutes topic/approach/results, last two
  minutes insights and ideally a demo, PDF or online-slides link, screencast if
  you want to demo. Also the parts of the late policy that are specific to the
  presentation: it is **exempt** from the −1/day rule because it is live, and
  **absence scores 0**. Due: **13 January 2026** — the day before the first
  presentation slot, because presenters are drawn at random.

---

## Named literature

### S15 — Goodfellow, Bengio & Courville, *Deep Learning*, MIT Press 2016 ★★

- URL: <https://www.deeplearningbook.org/>
- Retrieved: 2026-09-22. Access: the authors host the full HTML for free
  reading. **Licence: © MIT Press; the HTML is free to read online, the PDF is
  not offered for redistribution. Not vendored.**
- The one book TISS names [S1] and the book the lecture slides cite most [S4].
- Used for: every chapter reference in the notes — ch. 5 (ML basics,
  bias–variance), 6 (feedforward nets, losses, backprop), 7 (regularisation:
  augmentation, early stopping, dropout), 8 (optimisation, init, batch norm),
  9 (convolutional nets), 10 (sequence modelling, LSTM/GRU, BPTT),
  11 (**practical methodology** — this is the chapter Lecture 5 follows almost
  section for section: performance metrics, default baselines, more data vs.
  better model, hyperparameters, debugging), 14 (autoencoders), 20.10.3–4
  (VAE, GAN).

### S16 — Sutton & Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press 2018

- URL: <http://incompleteideas.net/book/the-book-2nd.html>
- Retrieved: 2026-09-22. Access: free PDF from the authors' page.
  **Licence: © 2014–2018 Sutton & Barto / MIT Press, "may not be reproduced".
  Not vendored.**
- Used for: [`../notes/04-deep-rl.md`](../notes/04-deep-rl.md) — MDP formalism,
  Bellman equations, TD and Q-learning, the deadly triad (ch. 11), the policy
  gradient theorem (ch. 13). Goodfellow does not cover RL, so this is the
  standard substitute; note that Lecture 6 itself works from S17, not from this
  book.

### S17 — Amini & Soleimany, *MIT 6.S191 Introduction to Deep Learning*

- URL: <http://introtodeeplearning.com/>
- Retrieved: 2026-09-22. Access: public; slides and videos free. Not vendored.
- Used for: it is **reference 1 of Lecture 6's literature list** [S4], i.e. the
  deep-RL lecture's own primary source. Its framing (classes of learning
  problems; key concepts; quality/value/policy functions; Q-function → policy)
  is the structure of that lecture, and our note follows it.

### S18 — Pramerdorfer, *Deep Learning for Visual Computing* (TU Wien 183.663)

- URL: <https://github.com/cpra/dlvc2016>
- Retrieved: 2026-09-22. Access: public repository. Not vendored.
- Used for: identifying the preceding course S1 names, and because Pramerdorfer's
  slides are cited in Lectures 2, 3 and 9 [S4]. Relevant mainly as the thing this
  course assumes you may have done.

### S19 — Karpathy, *A Recipe for Training Neural Networks* (2019)

- URL: <http://karpathy.github.io/2019/04/25/recipe/>
- Retrieved: 2026-09-22. Access: public blog post. Not vendored.
- Used for: the debugging order in
  [`../notes/10-practical.md`](../notes/10-practical.md). Not on a lecture
  reading list, but it is the standard statement of the "get one batch to
  overfit first" discipline that Lecture 5's *Debugging Neural Networks* chapter
  and S13's recommended approach both describe.

---

## Primary sources for the notes' technical claims

Every one of these is either on a lecture's own `== Literature ==` block [S4]
(marked **[L*n*]** with the lecture number) or is the original paper for a
result the notes state. All are cited, none is vendored; arXiv links are to the
abstract page, from which the authors' PDF is one click away.

| id | source | where used | on a lecture list? |
|---|---|---|---|
| **S20** | Rumelhart, Hinton & Williams (1986), *Learning representations by back-propagating errors*, Nature 323 | note 01, backprop | — |
| **S21** | Baydin et al. (2018), *Automatic differentiation in machine learning: a survey*, JMLR 18, <https://arxiv.org/abs/1502.05767> | note 01, reverse-mode AD cost | — |
| **S22** | Kingma & Ba (2015), *Adam*, <https://arxiv.org/abs/1412.6980> | note 01, Adam and its bias correction | L2 (via Ruder) |
| **S23** | Loshchilov & Hutter (2019), *Decoupled weight decay regularization*, <https://arxiv.org/abs/1711.05101> | note 01, AdamW | — |
| **S24** | Loshchilov & Hutter (2017), *SGDR*, <https://arxiv.org/abs/1608.03983> | note 01, cosine schedule | — |
| **S25** | Ruder (2016), *An overview of gradient descent optimization algorithms*, <https://arxiv.org/abs/1609.04747> | note 01, optimiser family | **L2 #6** |
| **S26** | Glorot & Bengio (2010), *Understanding the difficulty of training deep feedforward neural networks*, AISTATS | note 01, Xavier init | — |
| **S27** | He et al. (2015), *Delving deep into rectifiers*, <https://arxiv.org/abs/1502.01852> | note 01, He init | — |
| **S28** | Ioffe & Szegedy (2015), *Batch normalization*, <https://arxiv.org/abs/1502.03167> | notes 01, 02 | **L9 #21** |
| **S29** | Santurkar et al. (2018), *How does batch normalization help optimization?*, <https://arxiv.org/abs/1805.11604> | note 01, why BN works | **L9 #22** |
| **S30** | Ba, Kiros & Hinton (2016), *Layer normalization*, <https://arxiv.org/abs/1607.06450> | notes 01, 06 | L9 (Layer Normalization chapter) |
| **S31** | Srivastava et al. (2014), *Dropout*, JMLR 15 | note 01 | **L9 #12** |
| **S32** | Izmailov et al. (2018), *Averaging weights leads to wider optima and better generalization* (SWA), <https://arxiv.org/abs/1803.05407> | note 01, stochastic weight averaging | **L9 #30** |
| **S33** | DeVries & Taylor (2017), *Improved regularization of CNNs with Cutout*, <https://arxiv.org/abs/1708.04552> | notes 01, 02 | **L9 #17** |
| **S34** | Goodfellow, Shlens & Szegedy (2015), *Explaining and harnessing adversarial examples*, <https://arxiv.org/abs/1412.6572> | note 01, adversarial training and FGSM | **L9 #6** |
| **S35** | Su, Vargas & Sakurai (2017), *One pixel attack for fooling deep neural networks*, <https://arxiv.org/abs/1710.08864> | note 01, adversarial attacks | **L9 #28** |
| **S36** | Park et al. (2019), *SpecAugment*, <https://arxiv.org/abs/1904.08779> | note 01, audio augmentation | **L9 #9** |
| **S37** | Wei & Zou (2019), *EDA: easy data augmentation*, <https://arxiv.org/abs/1901.11196> | note 01, text augmentation | **L9 #13** |
| **S38** | Dumoulin & Visin (2018), *A guide to convolution arithmetic for deep learning*, <https://arxiv.org/abs/1603.07285> | note 02, output-size and transposed-conv formulas; `src/py/shape_formulas.py` | **L3 #1** |
| **S39** | He et al. (2016), *Deep residual learning*, <https://arxiv.org/abs/1512.03385> | note 02, ResNet | **L3 #4** |
| **S40** | Szegedy et al. (2015), *Going deeper with convolutions*, <https://arxiv.org/abs/1409.4842> | note 02, Inception | **L3 #2** |
| **S41** | Dai et al. (2017), *Deformable convolutional networks*, <https://arxiv.org/abs/1703.06211> | note 02; also named in S12 as an example of a "novel idea" for *Beat the stars* | **L3 #3** |
| **S42** | Lin, Chen & Yan (2014), *Network in network*, <https://arxiv.org/abs/1312.4400> | note 02, global average pooling and $1\times1$ conv | L3 (via Cook #5) |
| **S43** | Howard et al. (2017), *MobileNets*, <https://arxiv.org/abs/1704.04861> | note 02, depthwise separable convolutions | **L3 #14** (Wang's introduction) |
| **S44** | Tan & Le (2020), *EfficientNet*, <https://arxiv.org/abs/1905.11946> | note 01/02, compound scaling — Lecture 5's *Efficiently scaling up a model* | **L5 #8** |
| **S45** | Ren et al. (2016), *Faster R-CNN*, <https://arxiv.org/abs/1506.01497>; He et al. (2018), *Mask R-CNN*, <https://arxiv.org/abs/1703.06870> | note 02, detection and segmentation heads | **L3 #8, #10** |
| **S46** | Hochreiter & Schmidhuber (1997), *Long short-term memory*, Neural Computation 9(8) | note 03, LSTM and the adding problem (task 5) | — |
| **S47** | Pascanu, Mikolov & Bengio (2013), *On the difficulty of training recurrent neural networks*, <https://arxiv.org/abs/1211.5063> | note 03, vanishing/exploding gradients, clipping | L4 (Gradient Clipping chapter) |
| **S48** | Graves et al. (2006), *Connectionist temporal classification*, ICML, <https://www.cs.toronto.edu/~graves/icml_2006.pdf> | note 03 and `src/py/ctc_loss.py` — Lecture 4 devotes a chapter to CTC | **L4 #9** (Hannun's explainer) |
| **S49** | Bahdanau, Cho & Bengio (2015), *Neural machine translation by jointly learning to align and translate*, <https://arxiv.org/abs/1409.0473> | notes 03, 06, attention | **L4 #10** |
| **S50** | Cho et al. (2014), *Learning phrase representations…* (GRU), <https://arxiv.org/abs/1406.1078>; Olah (2015), *Understanding LSTMs* | note 03 | **L4 #5** |
| **S51** | Mnih et al. (2015), *Human-level control through deep reinforcement learning*, Nature 518 | note 04, DQN | **L6 #11** |
| **S52** | Schulman et al. (2017), *PPO*, <https://arxiv.org/abs/1707.06347>; Schulman et al. (2016), *GAE*, <https://arxiv.org/abs/1506.02438> | note 04 | — (PPO is the default the note recommends) |
| **S53** | Andrychowicz et al. (2017), *Hindsight experience replay*, <https://arxiv.org/abs/1707.01495>; Pathak et al. (2017), *Curiosity-driven exploration*, <https://arxiv.org/abs/1705.05363> | note 04, sparse-reward remedies — Lecture 6's *Reward Shaping, Auxiliary Tasks, and HER* chapter | **L6 #9, #8** |
| **S54** | Ng, Harada & Russell (1999), *Policy invariance under reward transformations*, ICML | note 04, potential-based shaping | — |
| **S55** | Karpathy (2016), *Deep reinforcement learning: Pong from pixels* | note 04 — Lecture 6 works this example live | **L6 #14** |
| **S56** | Kingma & Welling (2014), *Auto-encoding variational Bayes*, <https://arxiv.org/abs/1312.6114> | note 05, VAE and the reparameterisation trick | L7 (via Doersch #7) |
| **S57** | Higgins et al. (2017), *β-VAE*, ICLR | note 05 | **L7 #14** |
| **S58** | Goodfellow et al. (2014), *Generative adversarial nets*, <https://arxiv.org/abs/1406.2661> | note 05 | **L7 #10** |
| **S59** | Arjovsky, Chintala & Bottou (2017), *Wasserstein GAN*, <https://arxiv.org/abs/1701.07875>; Gulrajani et al. (2017), *WGAN-GP*, <https://arxiv.org/abs/1704.00028> | note 05 — Lecture 7 has a *Wasserstein distance* chapter | L7 |
| **S60** | Salimans et al. (2016), *Improved techniques for training GANs*, <https://arxiv.org/abs/1606.03498> | note 05, evaluating GANs | **L7 #16** |
| **S61** | Ho, Jain & Abbeel (2020), *Denoising diffusion probabilistic models*, <https://arxiv.org/abs/2006.11239>; Luo (2022), *Understanding diffusion models*, <https://arxiv.org/abs/2208.11970> | note 05 | **L7 #20** |
| **S62** | Vaswani et al. (2017), *Attention is all you need*, <https://arxiv.org/abs/1706.03762> | note 06 | **L8 #2, L13 #1** |
| **S63** | Carion et al. (2020), *End-to-end object detection with transformers* (DETR), <https://arxiv.org/abs/2005.12872> | note 06 and `src/py/set_prediction.py` — Lecture 8 spends ~25 of its 62 minutes on DETR, bipartite matching and object queries | **L8 #3** |
| **S64** | Dosovitskiy et al. (2021), *An image is worth 16×16 words* (ViT), <https://arxiv.org/abs/2010.11929>; Liu et al. (2021), *Swin Transformer*, <https://arxiv.org/abs/2103.14030> | note 06 | **L8 #16, #17** |
| **S65** | Devlin et al. (2019), *BERT*, <https://arxiv.org/abs/1810.04805> | notes 06, 09 | **L8 #12** |
| **S66** | Kipf & Welling (2017), *Semi-supervised classification with graph convolutional networks*, <https://arxiv.org/abs/1609.02907> | note 07, GCN and the $\hat D^{-1/2}\tilde A\hat D^{-1/2}$ normalisation | **L11 #7** |
| **S67** | Veličković et al. (2018), *Graph attention networks*, <https://arxiv.org/abs/1710.10903> | note 07, GAT | **L11 #6** |
| **S68** | Hamilton (2020), *Graph representation learning*, <https://www.cs.mcgill.ca/~wlh/grl_book/> | note 07 — free book, the lecture's reference 2 | **L11 #2** |
| **S69** | Gilmer et al. (2017), *Neural message passing for quantum chemistry*, <https://arxiv.org/abs/1704.01212> | note 07 — Lecture 11's *Neural Message Passing* chapter | L11 |
| **S70** | Simonyan, Vedaldi & Zisserman (2014), *Deep inside convolutional networks* (saliency maps), <https://arxiv.org/abs/1312.6034> | note 08 | **L10 #16** |
| **S71** | Ribeiro, Singh & Guestrin (2016), *"Why should I trust you?"* (LIME), <https://arxiv.org/abs/1602.04938> | note 08 | **L10 #6** |
| **S72** | Petsiuk, Das & Saenko (2018), *RISE*, <https://arxiv.org/abs/1806.07421> | note 08 | **L10 #3** |
| **S73** | Lundberg & Lee (2017), *A unified approach to interpreting model predictions* (SHAP), <https://arxiv.org/abs/1705.07874> | note 08 | **L10 #8** |
| **S74** | Zhou et al. (2016), *Learning deep features for discriminative localization* (CAM), <https://arxiv.org/abs/1512.04150>; Selvaraju et al. (2017), *Grad-CAM*, <https://arxiv.org/abs/1610.02391> | notes 02, 08 | **L9 #26**, L10 |
| **S75** | Sundararajan, Taly & Yan (2017), *Axiomatic attribution for deep networks* (integrated gradients), <https://arxiv.org/abs/1703.01365> | note 08, completeness axiom, checked in `src/py/test_xai_saliency.py` | — |
| **S76** | Arrieta et al. (2020), *Explainable AI (XAI): concepts, taxonomies, opportunities and challenges*, <https://arxiv.org/abs/1910.10045>; Molnar, *Interpretable Machine Learning*, <https://christophm.github.io/interpretable-ml-book/> | note 08, the taxonomy and the interpretability-vs-explainability distinction Lecture 10 opens with | **L10 #2, #1** |
| **S77** | Hu et al. (2021), *LoRA*, <https://arxiv.org/abs/2106.09685> | note 09 and `src/py/llm_finetune_sketch.py` | — |
| **S78** | Radford et al. (2021), *Learning transferable visual models from natural language supervision* (CLIP), <https://arxiv.org/abs/2103.00020> | note 09 — Lecture 13's *Multiple Modalities and CLIP* chapter | **L13 #26** |
| **S79** | Wei et al. (2022), *Chain-of-thought prompting*, <https://arxiv.org/abs/2201.11903>; Yao et al. (2023), *Tree of thoughts*, <https://arxiv.org/abs/2305.10601> | note 09 — both are named chapters of Lecture 13 | L13 |
| **S80** | Lewis et al. (2020), *Retrieval-augmented generation*, <https://arxiv.org/abs/2005.11401> | note 09 — Lecture 13's RAG chapter | L13 |
| **S81** | Anthropic (2024), *Introducing the Model Context Protocol*, <https://modelcontextprotocol.io/> | note 09 — Lecture 13 has an MCP chapter, added for the 2025 edition | **L13 #25** |
| **S82** | Shumailov et al. (2024), *AI models collapse when trained on recursively generated data*, Nature 631 | note 09, model collapse / "AI slop" | **L13 #24** |
| **S83** | Martin et al. (2024), *Knowledge Return Oriented Prompting (KROP)*, <https://arxiv.org/abs/2406.11880> | note 09, adversarial prompting | **L13 #7** |
| **S84** | Frankle & Carbin (2019), *The lottery ticket hypothesis*, <https://arxiv.org/abs/1803.03635> | note 12 and `src/py/deploy_optimize.py` | **L12 #14** |
| **S85** | Micikevicius et al. (2018), *Mixed precision training*, <https://arxiv.org/abs/1710.03740> | notes 10, 12, fp16/bf16 | **L12 #2** |
| **S86** | Goyal et al. (2018), *Accurate, large minibatch SGD*, <https://arxiv.org/abs/1706.02677> | note 12 — the source of the linear LR scaling rule and of gradual warmup, both chapters of Lecture 12 | **L12 #5** |
| **S87** | Jacob et al. (2018), *Quantization and training of neural networks for efficient integer-arithmetic-only inference*, <https://arxiv.org/abs/1712.05877> | note 12 and `src/py/deploy_optimize.py`, affine int8 quantisation | L12 (Floating point quantization chapter) |
| **S88** | ONNX, <https://onnx.ai/>; ONNX Runtime, <https://onnxruntime.ai/> | note 12 — a named chapter of Lecture 12 and a named option in S14 | **L12**, **S14** |
| **S89** | Wilkinson et al. (2016), *The FAIR guiding principles for scientific data management and stewardship*, Scientific Data 3; <https://www.go-fair.org/fair-principles/> | note 12 — Lecture 12's *Publishing your dataset — FAIR* chapter, and the bonus-point condition in S12's *Bring your own data* | **L12 #15, #16** |
| **S90** | Gebru et al. (2021), *Datasheets for datasets*, CACM 64(12); Mitchell et al. (2019), *Model cards*, FAT* | note 11, data card | — |
| **S91** | Hestness et al. (2017), *Deep learning scaling is predictable, empirically*, <https://arxiv.org/abs/1712.00409> | note 11, power-law learning curves | — |
| **S92** | Guo et al. (2017), *On calibration of modern neural networks*, <https://arxiv.org/abs/1706.04599> | note 11, ECE and temperature scaling | — |
| **S93** | Henderson et al. (2018), *Deep reinforcement learning that matters*, <https://arxiv.org/abs/1709.06560>; Bouthillier et al. (2021), *Accounting for variance in ML benchmarks*, <https://arxiv.org/abs/2103.03098> | notes 04, 11, seed variance | — |
| **S94** | Bergstra & Bengio (2012), *Random search for hyper-parameter optimization*, JMLR 13; Feurer & Hutter (2019), *Hyperparameter optimization*, <https://www.automl.org/wp-content/uploads/2019/05/AutoML_Book_Chapter1.pdf> | note 10 — Lecture 5's *Automatic Hyperparameter Optimization* chapter | **L5 #4, #5** |
| **S95** | Towers et al. (2023), *Gymnasium*, <https://gymnasium.farama.org/> | note 04, the `reset`/`step` API | — |

---

## Tools whose behaviour the notes assert

### S96 — PyTorch 2.14 documentation

- URL: <https://docs.pytorch.org/docs/stable/>
- Retrieved: 2026-09-22 (and, more to the point, **executed**: the repo venv has
  torch 2.14.0, so every shape and parameter-count claim in the notes is checked
  by running it rather than by reading the docs — see
  `src/py/shape_formulas.py` and `src/py/test_shape_formulas.py`)
- Used for: `nn.LSTM`/`nn.GRU` keeping two bias vectors, `nn.Conv2d` and
  `nn.Linear` default initialisation, `nn.CTCLoss` conventions,
  `BatchNorm2d` momentum, `torch.quantize_per_tensor`, autograd semantics.

### S97 — `ashleve/lightning-hydra-template`

- URL: <https://github.com/ashleve/lightning-hydra-template>
- Retrieved: 2026-09-22. Licence: **MIT**. Not vendored (not needed: our
  `src/project_template` is our own and much smaller).
- Used for: it is the template **S13 links to** as "a suitable template to help
  structuring the project". Recorded so that `src/project_template/README.md` can
  say which one the course actually recommends.
