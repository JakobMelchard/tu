# Sources: 194.100 Theoretical Foundations and Research Topics in Machine Learning

Register of every source used to write and verify [`../notes`](../notes/README.md)
and [`../src`](../src/README.md). Retrieval dates are the day the page or file
was fetched; TISS and the lecturers' pages change, so re-check before the oral
exam.

**Citation form.** The notes cite an entry as `[S<n>]`, usually with a locator —
`[S9 Thm 6.8]`, `[S10 Cor. 5.11]`, `[S9 ch. 26]` — and several together as
`[S9, S10]`. **Every entry below is cited somewhere**; an entry that supports
nothing is withdrawn rather than left in the register (see "Sources deliberately
not used" at the end).

**Vendoring policy.** Nothing in this directory is a third-party file. The
course's own material lives in TUWEL, which needs a login and is not ours to
copy [S6]. Of the two standard textbooks, **S9 is explicitly not
redistributable** and **S10 is CC-BY-NC-ND and therefore would be** — we still
fetch rather than vendor it, to keep the repo small and the policy uniform.
[`fetch-sources.sh`](fetch-sources.sh) downloads both into a git-ignored
`vendor/`. See [`README.md`](README.md).

## The one-line summary of what this register found

**This course has no public past-exam material of any kind, and no public
lecture notes.** Its VoWi page exists but every section reads "noch offen" and
it has no attachments [S8]; the lecturers' own course pages say only "The course
will be held on TUWEL" [S6, S7]. What the register *did* establish is the
assessment mode, its three-era history, and the existence of a 6 ECTS twin
course under a different number — see
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

---

## Course records

### S1: TISS course page, 194.100, 2026W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=194100&semester=2026W&locale=en>
- Retrieved 2026-09-22 (browser; the page needs JavaScript).
- Access: public. Not redistributable; transcribed in [`../docs/tiss.md`](../docs/tiss.md).
- Used for: the authoritative statement of the examination modalities (coursework
  + practical project + final oral exam, 50 %/50 % thresholds, one repeat), the
  topic list, lecturers, dates, registration window, curricula. Verified against
  the stored transcription: **no change**.
- **Re-read 2026-09-27**: no field changed. Blended
  learning; the single timetabled slot, Wed 10:00-12:00, Seminarraum FAV EG A,
  07.10.2026-20.01.2027, is the exercise session; registration until 27.10.2026
  23:59.

### S2: TISS API record, 194.100, 2026W

- URL: `https://tiss.tuwien.ac.at/api/course/194100-2026W` (bearer token required)
- Retrieved 2026-09-22. Stored at `../docs/tiss-api.xml`.
- Access: authenticated API, read-only. Byte-identical to the stored copy.
- Used for: learning outcomes, subject of course, workload split, examination
  modalities in machine-readable form.

### S3: TISS records for the previous offerings of 194.100

- URLs: `https://tiss.tuwien.ac.at/api/course/194100-<sem>` and the matching
  `courseDetails.xhtml` pages, for `2025W`, `2025S`, `2024W`, `2024S`, `2023W`,
  `2023S`, `2022W`, `2021S`, `2020W`.
- Retrieved 2026-09-22.
- Access: public pages plus the authenticated read-only API. Not redistributable; the diff is summarised in `../docs/tiss.md`.
- Used for: the year-on-year comparison table in [`../docs/tiss.md`](../docs/tiss.md)
  and the three-era assessment history in
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md). **This is where the
  "is it a seminar?" question was settled.** The course runs *every* semester;
  TISS lists it back to 2020W.

### S4: TISS course page, 194.201 (the 6 ECTS twin), 2026W and 2025W

- URL: <https://tiss.tuwien.ac.at/course/educationDetails.xhtml?courseNr=194201>
- Retrieved 2026-09-22. First offered 2025W (2025S and earlier return HTTP 404).
- Access: public TISS page. Not redistributable; cite only.
- Used for: the extended topic list the same lectures cover for 6 ECTS students
  (theory of deep learning, deep learning architectures, graph neural networks,
  expressivity and logics, interpretability/robustness/privacy/fairness) and the
  more detailed learning outcomes. **Same lectures, same lecturers, same TUWEL
  course** — S6 links both numbers side by side, and VoWi files them on one page
  [S8]. Useful as a statement of what the group considers the full syllabus, and
  as the reason note 10 exists at the depth it does.

### S5: ML research unit teaching page, TU Wien Informatics

- URL: <https://ml-tuw.github.io/teaching/>
- Retrieved 2026-09-22.
- Access: public web page. Cite only.
- Used for: the archive of per-semester course pages (S6, S7), and confirmation
  that the course has run every semester since SoSe 2021 under this group.
- As of 2026-09-27 there is still **no 2026W page**.

### S6: Course homepage, WiSe 2025/26 (most recent published offering)

- URL: <https://ml-tuw.github.io/teaching/ws2526/tfrtML.html>
- Retrieved 2026-09-22. (The TISS *Course homepage* link of S1 points at this
  site; no `ws2627` page exists yet as of the retrieval date.)
- Access: public web page, no licence statement. Cite only; nothing to vendor: the page is three paragraphs and two links.
- Used for: the format, in the lecturers' own words: "A new lecture unit will be
  available about once a week and consists of recordings …, lecture notes,
  videos, and/or notebooks"; coursework is "tackling a learning problem with
  advanced machine learning methods **or understanding and explaining a proof**";
  questions in the TUWEL forum; live in-person discussion sessions "whenever the
  need is clear", announced in advance. It links the 3 ECTS and 6 ECTS TISS entries as two versions of
  one lecture, and names Patrick Indri as contact.
  **Crucially: "The course will be held on TUWEL."** Hence no public material.
- Still the most recent page on 2026-09-27 (no 2026W page, S5).

### S7: Course homepages, earlier offerings

- URLs: `https://ml-tuw.github.io/teaching/<sem>/tfrtML.html` for `sose25`,
  `ws2425`, `sose24`, `ws2324`, `sose23`, `ws2223`, `sose22`, `ws2122`, `sose21`.
- Retrieved 2026-09-22.
- Access: public web pages, no licence statement. Cite only.
- Used for: the history of the format. The `sose21` page is the only one that
  mentions "a **presentation of an advanced research topic** in machine
  learning" as coursework, matching the 2020W–2021S TISS era [S3]; every page
  from `ws2223` on has the current wording. All say the course lives on TUWEL.

### S8: VoWi page for this course

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Theoretical_Foundations_and_Research_Topics_in_Machine_Learning_VU_(Gärtner)>
- Retrieved 2026-09-22 (browser; VoWi runs a proof-of-work bot gate that blocks `curl`).
- Access: public student wiki, CC-BY-SA. **Nothing to vendor: the page has no attachments.**
- Used for: the negative result. Every section (Inhalt, Ablauf, Vorkenntnisse,
  Vortrag, Übungen, **Prüfung/Benotung**, Zeitaufwand, Unterlagen, Tipps) reads
  "noch offen". The page's own metadata links **both** `tiss:194201` and
  `tiss:194100`, confirming the two numbers are one LVA, records ECTS as 6,0 and
  "Letzte Abhaltung 2025W", and names a Mattermost channel
  `theoretical-foundations-and-research-topics-in-machine-learning`.
- Checked the same day and equally empty: the VoWi pages for
  *Seminar in Artificial Intelligence – Theoretical Aspects of Machine Learning SE*
  and *Machine Learning Algorithms and Applications PR*.


---

## Textbooks

### S9: Shalev-Shwartz & Ben-David, *Understanding Machine Learning: From Theory to Algorithms* (UML)

- Shai Shalev-Shwartz, Shai Ben-David. Cambridge University Press, 2014.
- Author-hosted PDF: <https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/>
  (download page `.../copy.html`; file `understanding-machine-learning-theory-algorithms.pdf`)
- Retrieved 2026-09-22, 2 601 512 bytes.
- **Licence: cite only, do NOT vendor.** The download page states verbatim:
  "PDF of manuscript posted by permission of Cambridge University Press. Users
  may download a copy for **personal use only. Not for distribution.**"
- Used for: **the backbone of notes 01–06 and 08–09.** Every theorem number cited
  in the notes was read out of this PDF, not from memory. Verified locators:
  Lemma 2.2 (union bound), Cor. 2.3 (realisable finite class,
  $m\ge\log(|\mathcal H|/\delta)/\varepsilon$), Lemma 4.2
  ($\varepsilon/2$-representative ⇒ ERM), Cor. 4.4, Lemma 4.5 (Hoeffding),
  Cor. 4.6 (finite class uniform convergence,
  $\log(2|\mathcal H|/\delta)/(2\varepsilon^2)$), Thm 5.1 (No-Free-Lunch,
  $m<|\mathcal X|/2$, probability $1/7$, risk $1/8$), Cor. 5.2, Lemma 6.1,
  Cor. 6.4, Thm 6.6, Thm 6.7 and Thm 6.8 (fundamental theorem, qualitative and
  quantitative), Lemma 6.10 (Sauer–Shelah–Perles), Thm 6.11 (growth-function
  bound, with the $1/\delta$ rather than $\log(1/\delta)$), Thm 7.2/7.3/7.4/7.5
  (nonuniform learnability, SRM), Lemma 7.6 (Kraft), Thm 7.7 (MDL/Occam),
  Thm 13.2 (stability ⇒ generalisation), Lemma 13.5 (strong convexity),
  Cor. 13.6 (RLM is $2\rho^2/(\lambda m)$-stable), Cor. 13.8, Cor. 13.9
  ($\sqrt{8\rho^2B^2/m}$), Lemma 15.2, Thm 15.8 (support vectors), Lemma 15.9
  (Fritz John), Thm 16.1 (representer theorem), Lemma 16.2, Lemma 26.2
  (symmetrisation), Thm 26.5 (Rademacher generalisation), Lemma 26.8 (Massart,
  **centred** form), Lemma 26.9 (contraction), Lemma 26.10 ($\ell_2$ linear
  class), Lemma 26.11 ($\ell_1$), Lemma A.2.

### S10: Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning*, 2nd ed. (FoML)

- Mehryar Mohri, Afshin Rostamizadeh, Ameet Talwalkar. MIT Press, 2018.
- Book page: <https://cs.nyu.edu/~mohri/mlbook/> — "Download (official online
  versions from MIT Press)". PDF: <https://www.dropbox.com/s/38p0j6ds5q9c8oe/10290.pdf?dl=1>
- Retrieved 2026-09-22, 6 224 448 bytes.
- **Licence: CC-BY-NC-ND.** The book page states: "Copyright in this Work has
  been licensed exclusively to The MIT Press … under a Creative Commons
  CC-BY-NC-ND license", and the PDF's own copyright page repeats it. Verbatim,
  non-commercial redistribution *would* be permitted; we fetch rather than
  vendor (see the policy note at the top).
- Used for: the second opinion on every bound in notes 04, 05, 07, 09; it is the
  better source for margin theory and kernels. Verified locators: Thm 3.3
  (Rademacher bound, $2\mathfrak R_m$ and
  $2\hat{\mathfrak R}_S+3\sqrt{\log(2/\delta)/2m}$), Lemma 3.4, Thm 3.5, Thm 3.7
  (**Massart's lemma**, $\frac rm\sqrt{2\log|A|}$), Cor. 3.8, Cor. 3.9,
  **Thm 3.13 (Radon's theorem)**, Thm 3.17 (Sauer's lemma), Cor. 3.18, Cor. 3.19
  (VC generalisation bound,
  $\sqrt{2d\log(em/d)/m}+\sqrt{\log(1/\delta)/2m}$), Thm 3.20 and Thm 3.23 (lower
  bounds, realisable and non-realisable), Lemma 5.3, **Thm 5.4 (leave-one-out /
  support-vector bound)**, Lemma 5.7 (Talagrand's lemma), **Thm 5.8 (margin
  bound)**, Thm 5.9, Thm 5.10 ($\hat{\mathfrak R}_S\le\sqrt{r^2\Lambda^2/m}$),
  Cor. 5.11, Thm 6.2 (Mercer), Lemma 6.7, Thm 6.8 (RKHS), Thm 6.10 (closure
  properties), Thm 6.11 (representer theorem), Thm 6.12, Cor. 6.13, Thm 6.24
  (Bochner), Thm 11.3, Thm 11.11, Lemma 11.12 (push-through identity), Thm 11.15
  ($\ell_1$ Rademacher), Appendix D (McDiarmid).

### S11: Telgarsky, *Deep learning theory lecture notes*

- Matus Telgarsky, University of Illinois. <https://mjt.cs.illinois.edu/dlt/>
  (PDF <https://mjt.cs.illinois.edu/dlt/index.pdf>, 1 022 594 bytes)
- Retrieved 2026-09-22.
- **Licence: none stated.** The page gives only a "How to cite" block asking for
  the version string. No redistribution permission ⇒ cite only.
- Used for: note 10 — the approximation / optimisation / generalisation
  decomposition, the sawtooth depth-separation construction, and the NTK and
  implicit-bias material, cross-checked against the primary papers S29–S36.

### S12: Bach, *Learning Theory from First Principles*

- Francis Bach. MIT Press, 2024. Author-hosted PDF:
  <https://www.di.ens.fr/~fbach/ltfp_book.pdf> (6 963 140 bytes)
- Retrieved 2026-09-22.
- **Licence: no statement located in the PDF's front matter ⇒ cite only.**
- Used for: a third opinion on the least-squares and kernel chapters (notes 07,
  08), in particular the ridge bias–variance split and the effective dimension
  $\mathrm{df}(\lambda)=\sum_j\mu_j/(\mu_j+\lambda)$.

---

## Primary sources for individual results

Each is cited at the point in the notes where the corresponding theorem is
stated. All URLs checked 2026-09-22.

| id | source | used for |
|---|---|---|
| **S13** | W. Hoeffding, "Probability inequalities for sums of bounded random variables", *JASA* 58 (1963) 13–30. <https://doi.org/10.1080/01621459.1963.10500830> | note 02: Hoeffding's lemma and inequality |
| **S14** | C. McDiarmid, "On the method of bounded differences", *Surveys in Combinatorics* (1989) 148–188. <https://doi.org/10.1017/CBO9781107359949.008> | notes 02, 05: bounded-differences inequality |
| **S15** | S. Boucheron, G. Lugosi, P. Massart, *Concentration Inequalities*, OUP 2013. <https://doi.org/10.1093/acprof:oso/9780199535255.001.0001> | note 02: Bernstein's inequality, the Chernoff method. Commercial, cite only |
| **S16** | V. N. Vapnik, A. Ya. Chervonenkis, "On the uniform convergence of relative frequencies of events to their probabilities", *Theory Probab. Appl.* 16 (1971) 264–280. <https://doi.org/10.1137/1116025> | note 04: VC dimension, growth function, the double-sample argument |
| **S17** | N. Sauer, "On the density of families of sets", *J. Combin. Theory A* 13 (1972) 145–147; S. Shelah, *Pacific J. Math.* 41 (1972) 247–261. <https://doi.org/10.1016/0097-3165(72)90019-2> | note 04: Sauer–Shelah lemma attribution |
| **S18** | A. Blumer, A. Ehrenfeucht, D. Haussler, M. Warmuth, "Learnability and the Vapnik–Chervonenkis dimension", *JACM* 36 (1989) 929–965. <https://doi.org/10.1145/76359.76371> | note 04: finite VC ⇔ PAC learnable; note 03: the axis-aligned rectangle learner |
| **S19** | P. L. Bartlett, S. Mendelson, "Rademacher and Gaussian complexities: risk bounds and structural results", *JMLR* 3 (2002) 463–482. <https://www.jmlr.org/papers/volume3/bartlett02a/bartlett02a.pdf> — open access | note 05: Rademacher generalisation bound and structural results; note 09: margin bound |
| **S20** | O. Bousquet, A. Elisseeff, "Stability and generalization", *JMLR* 2 (2002) 499–526. <https://www.jmlr.org/papers/volume2/bousquet02a/bousquet02a.pdf> — open access | note 06: uniform stability, stability of RLM |
| **S21** | G. Kimeldorf, G. Wahba, "Some results on Tchebycheffian spline functions", *J. Math. Anal. Appl.* 33 (1971) 82–95; B. Schölkopf, R. Herbrich, A. J. Smola, "A generalized representer theorem", *COLT* 2001. <https://doi.org/10.1016/0022-247X(71)90184-3> | note 08: representer theorem |
| **S22** | N. Aronszajn, "Theory of reproducing kernels", *Trans. AMS* 68 (1950) 337–404. <https://doi.org/10.1090/S0002-9947-1950-0051437-7> | note 08: Moore–Aronszajn theorem |
| **S23** | C. Cortes, V. Vapnik, "Support-vector networks", *Machine Learning* 20 (1995) 273–297. <https://doi.org/10.1007/BF00994018> | note 09: the soft-margin SVM |
| **S24** | A. B. J. Novikoff, "On convergence proofs for perceptrons", *Symp. Math. Theory of Automata* 12 (1962) 615–622. | note 09: the perceptron mistake bound $(R/\gamma)^2$ |
| **S25** | J. Platt, "Sequential minimal optimization: a fast algorithm for training support vector machines", Microsoft Research MSR-TR-98-14 (1998). <https://www.microsoft.com/en-us/research/publication/sequential-minimal-optimization-a-fast-algorithm-for-training-support-vector-machines/> | note 09: SMO |
| **S26** | D. Haussler, "Sphere packing numbers for subsets of the Boolean $n$-cube with bounded Vapnik–Chervonenkis dimension", *J. Combin. Theory A* 69 (1995) 217–232. <https://doi.org/10.1016/0097-3165(95)90052-7> | note 05: the $n$-independent covering-number bound behind $\mathfrak R\lesssim\sqrt{d/n}$ |
| **S27** | R. M. Dudley, "The sizes of compact subsets of Hilbert space and continuity of Gaussian processes", *J. Funct. Anal.* 1 (1967) 290–330. <https://doi.org/10.1016/0022-1236(67)90017-1> | note 05: the entropy integral |
| **S28** | M. Ledoux, M. Talagrand, *Probability in Banach Spaces*, Springer 1991, Thm 4.12. <https://doi.org/10.1007/978-3-642-20212-4> | note 05: the contraction lemma |

## Primary sources for note 10 (deep learning theory)

| id | source | used for |
|---|---|---|
| **S29** | G. Cybenko, "Approximation by superpositions of a sigmoidal function", *Math. Control Signals Systems* 2 (1989) 303–314; K. Hornik, "Approximation capabilities of multilayer feedforward networks", *Neural Networks* 4 (1991) 251–257; M. Leshno, V. Lin, A. Pinkus, S. Schocken, "Multilayer feedforward networks with a nonpolynomial activation function can approximate any function", *Neural Networks* 6 (1993) 861–867. <https://doi.org/10.1016/S0893-6080(05)80131-5> | universal approximation; the sharp hypothesis is a **non-polynomial** activation |
| **S30** | A. R. Barron, "Universal approximation bounds for superpositions of a sigmoidal function", *IEEE Trans. Inf. Theory* 39 (1993) 930–945. <https://doi.org/10.1109/18.256500> | the $O(C_g/\sqrt m)$ approximation rate |
| **S31** | M. Telgarsky, "Benefits of depth in neural networks", *COLT* 2016. <https://arxiv.org/abs/1602.04485> | depth separation; the tent-map / sawtooth construction |
| **S32** | P. L. Bartlett, N. Harvey, C. Liaw, A. Mehrabian, "Nearly-tight VC-dimension and pseudodimension bounds for piecewise linear neural networks", *JMLR* 20 (2019) 1–17. <https://arxiv.org/abs/1703.02930> | VC dimension of ReLU networks in terms of parameter count $W$ and depth $L$ |
| **S33** | A. Jacot, F. Gabriel, C. Hongler, "Neural tangent kernel: convergence and generalization in neural networks", *NeurIPS* 2018. <https://arxiv.org/abs/1806.07572> | the NTK parametrisation and the infinite-width limit |
| **S34** | D. Soudry, E. Hoffer, M. S. Nacson, S. Gunasekar, N. Srebro, "The implicit bias of gradient descent on separable data", *JMLR* 19 (2018) 1–57. <https://arxiv.org/abs/1710.10345> | implicit bias towards the max-margin direction, and its logarithmic rate |
| **S35** | M. Belkin, D. Hsu, S. Ma, S. Mandal, "Reconciling modern machine-learning practice and the classical bias–variance trade-off", *PNAS* 116 (2019) 15849–15854. <https://arxiv.org/abs/1812.11118> | double descent; the worked paper summary in note 11 |
| **S36** | T. Hastie, A. Montanari, S. Rosset, R. J. Tibshirani, "Surprises in high-dimensional ridgeless least squares interpolation", *Ann. Statist.* 50 (2022) 949–986. <https://arxiv.org/abs/1903.08560> | Thm 1: the asymptotic risk of minimum-norm interpolation on either side of $\gamma=d/n=1$; Prop. 1: GD from zero converges to the min-norm solution |
| **S37** | G. Montúfar, R. Pascanu, K. Cho, Y. Bengio, "On the number of linear regions of deep neural networks", *NeurIPS* 2014. <https://arxiv.org/abs/1402.1869> | Cor. 5: $\Omega\big((m/d)^{(L-1)d}m^d\big)$ linear regions |
| **S38** | P. L. Bartlett, D. J. Foster, M. Telgarsky, "Spectrally-normalized margin bounds for neural networks", *NeurIPS* 2017. <https://arxiv.org/abs/1706.08498> | Thm 1.1 and the spectral complexity $R_A$ of eq. (1.2) |
| **S39** | A. Maurer, "A note on the PAC-Bayesian theorem" (2004). <https://arxiv.org/abs/cs/0411099>; D. McAllester, "PAC-Bayesian model averaging", *COLT* 1999; J. Langford, M. Seeger, "Bounds for averaging classifiers" (2001). | the $\mathrm{kl}$-form PAC-Bayes bound — **the $\log(2\sqrt n/\delta)/n$ version is Maurer's, not McAllester's** |
| **S40** | G. K. Dziugaite, D. M. Roy, "Computing nonvacuous generalization bounds for deep (stochastic) neural networks with many more parameters than training data", *UAI* 2017. <https://arxiv.org/abs/1703.11008> | the first non-vacuous bound for a real network; Table 1 gives 0.161 on binary MNIST |
| **S41** | P. L. Bartlett, P. M. Long, G. Lugosi, A. Tsigler, "Benign overfitting in linear regression", *PNAS* 117 (2020) 30063–30070. <https://arxiv.org/abs/1906.11300> | the **two** effective-rank conditions $r_k(\Sigma)$ and $R_k(\Sigma)$ |
| **S42** | V. Nagarajan, J. Z. Kolter, "Uniform convergence may be unable to explain generalization in deep learning", *NeurIPS* 2019. <https://arxiv.org/abs/1902.04742> | the vacuity-of-uniform-convergence construction |
| **S43** | C. Zhang, S. Bengio, M. Hardt, B. Recht, O. Vinyals, "Understanding deep learning requires rethinking generalization", *ICLR* 2017. <https://arxiv.org/abs/1611.03530> | fitting random labels |
| **S44** | S. S. Du, X. Zhai, B. Poczos, A. Singh, "Gradient descent provably optimizes over-parameterized neural networks", *ICLR* 2019. <https://arxiv.org/abs/1810.02054>; K. Kawaguchi, "Deep learning without poor local minima", *NeurIPS* 2016. <https://arxiv.org/abs/1605.07110> | the overparameterised linear-rate convergence result; the deep-linear landscape result |

---

## Sources deliberately not used

- **TUWEL.** The course is held there [S6] and it needs a login. Never fetched,
  so every TUWEL claim in the notes (units, forum, announcements, coursework,
  project and oral dates) is second-hand from S1 and S6 and unverified.
  Its forum, slides, recordings, assignment sheets, notebooks and the dates of
  the partial performance evaluations are all behind that login; this is why
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) can describe the
  *structure* of the assessment but not a single real question.
- **VoWi exam PDFs for *Einführung in Machine Learning* (194.025).** That page
  does carry three exam PDFs, but it is a different course — a 6 ECTS bachelor
  introduction with a *written* exam, sharing only some lecturers. Its questions
  are about applied ML (naive Bayes tables, decision trees, evaluation metrics),
  not learning theory, so they would mislead rather than help here.
- **Schölkopf & Smola, *Learning with Kernels* (MIT Press 2002).** Excellent for
  note 08 but commercial, no free copy, and S9 ch. 16 + S10 ch. 6 already cover
  everything the notes state.
- **Vapnik, *Statistical Learning Theory* (Wiley 1998)** and **Devroye, Györfi &
  Lugosi, *A Probabilistic Theory of Pattern Recognition* (1996)**: the origin of
  the $4\tau_{\mathcal H}(2n)e^{-n\varepsilon^2/8}$ form quoted in note 04, but
  commercial and not consulted directly — note 04 says so, and flags that the
  constants in that form vary between books.
