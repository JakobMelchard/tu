# Sources: 138.128 Machine Learning in Physics

Register of every source used for [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). Cited as `[S<n>]`, with a locator where useful
(`[S6 sec. VII.C.1]`, `[S7 sec. 4.6]`, `[S8 sec. 3.4.1]`). Retrieval date is
2026-09-28 unless stated. "Verified" means the page or PDF was opened on that day;
"bibliographic" means the reference is standard and was not re-fetched.

**Vendoring policy.** Nothing third-party is committed. The only permissively
licensed material found (Mehta et al.'s notebooks, MIT, S14; one MIT script in
S5) is not needed by the code here, so it is linked, not copied.
[`fetch-sources.sh`](fetch-sources.sh) downloads the four free PDFs (S6-S9) into
git-ignored `cite-only/` for personal reading. Never TUWEL, never JupyterHub:
both need a login, and JupyterHub is where the graded notebooks live.

## One-line summary of what this register found

The course is public to an unusual degree: the 2021S exercise notebooks (S5) and
the lecture videos 2021-2023 (S11) are online, and they name the three exercise
domains of TISS precisely (Doppler/temperature deblurring in exercise 07, SUSY
collision classification in 08-09, Ising phases in 10-11). **No past written test
is public anywhere** (VoWi empty, S12; the notebooks contain no test material).

---

## Course records

### S1: TISS course page, 138.128, 2027S
- <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=138128&semester=2027S>
- Transcribed 2026-09-28: [`../docs/tiss.md`](../docs/tiss.md). Verified via the transcription.
- Used for: dates, rooms, registration, grading, lecturers, curricula, literature, the stale 2026S retake row.

### S2: TISS API record, 138.128, 2027S
- `https://tiss.tuwien.ac.at/api/course/138128-2027S` (token). Stored: `../docs/tiss-api.md`.
- Used for: topic list (nine lecture topics, three exercise domains), learning outcomes, literature list.

### S3: TISS course page, 138.128, 2026S
- Read the same day; differences tabulated at the end of [`../docs/tiss.md`](../docs/tiss.md).
- Used for: 2026S test dates (06.05, 24.06.2026), eight lecturers, TUWEL link.

### S4: Wallerberger, "Machine Learning in Physics" course page
- <https://wallerberger.at/mlphys/>. Verified.
- Taught "since Spring 2021"; Best Lecture 2023, shortlisted 2021-2022. Three parts: Python and optimisation (exercises 1-3), linear models "the centrepiece" (4-7), advanced models (8-11). Links S5 and S11.

### S5: `mwallerb/ml-phys-exercises` (GitHub, branch `mainline`)
- <https://github.com/mwallerb/ml-phys-exercises>. Verified; last push 2023-06-26.
- README: exercise notebooks for Spring 2021, "graded using JupyterHub and nbgrader".
- **Licence: none** (GitHub API `license: null`; only `shared/get_susy.py` carries SPDX MIT). Cite only; nothing copied. Numbers used as test anchors are facts from its asserts: cond of the 101x30 Vandermonde matrix 51785875457 (Ex06), stationary point (0.752619, 0) and Hessian [[26,16],[16,50]] at (1,2) (Ex03), $E'(0.5)=48$ (Ex02).
- Notebooks: Ex00 test run, Ex01 GD in 1D, Ex02 advanced GD (Nesterov, backprop by chain rule), Ex03 Newton, Ex04 Hooke's law, Ex05 polynomial fitting, Ex06 SVD and ridge, **Ex07 "Undoing temperature"** (Doppler-broadened spectrum, GD, early stopping, SGD), **Ex08 SUSY logistic** (SGDClassifier, confusion matrix, sensitivity/specificity), **Ex09 SUSY neural nets** (MLPClassifier, grid search), **Ex10 Ising k-means** (magnetisation and staggered magnetisation), **Ex11 low-rank Ising** (truncated SVD, PCA), Ex12 CartPole Q-table (gymnasium).

### S11: TU Wien LectureTube channel "Machine Learning in Physics"
- <https://video.tuwien.ac.at/@49500/mlphys>, read in a browser (JavaScript page). Verified.
- 48 videos, 03.2021-06.2023, series: Python 1-7, Optimization 1-5 (GD 1D, accelerated GD, backpropagation, Newton, stochasticity), Learning 1-7 (philosophical prelude, supervised learning, over-/underfitting, SVD, early stopping, unsupervised, reinforcement), Regression 1-5 (OLS, regularisation, generalised/extended linear models, error analysis, convergence), Classification 1-3 (logistic, backpropagation, confusion matrix), Neural Networks 1-3, clustering with k-means, Low-rank 1-3 (truncated SVD, PCA, tensor networks), guest lectures (Grüneis, Ipp, Huber), Reinforcement 1-2 (2023: basics, Q-learning). **No autoencoder video**: autoencoders are newer than 2023 on TISS, or taught live only (unverified).

### S12: VoWi, "Machine Learning in Physics VU (Andergassen)"
- <https://vowi.fsinf.at/wiki/TU_Wien:Machine_Learning_in_Physics_VU_(Andergassen)>, read in a browser (the plain fetch is blocked). Verified.
- Every section "noch offen"; "Diese Seite hat noch keine Anhänge". Last offering 2026S; lists a Mattermost channel `machine-learning-in-physics`.

### S13: TU Wien E138 news, Best Teaching / Best Lecture Award 2023
- <https://www.tuwien.at/en/phy/ifp/e138-news/news/best-teaching-und-best-lecture-award-2023>. Verified.
- 138.128 Best Lecture 2023 (Wallerberger, Karner, Klebel-Knobloch).

### S37: semester schedule
- `_schedule/dates.json` of the source repo (not published), entry 138.128. Used for: the follow-up course 138.129 PR.


## Textbooks named on TISS (S2 "Lecture notes / further reading")

### S6: Mehta, Bukov, Wang, Day, Richardson, Fisher, Schwab, "A high-bias, low-variance introduction to Machine Learning for physicists", Phys. Rep. 810 (2019) 1-124
- arXiv:1803.08823v3, <https://arxiv.org/abs/1803.08823>. PDF verified (116 pp.), sha256 `7db49ff1...8a7e38`.
- Licence: arXiv non-exclusive distribution. **Cite only.**
- Locators used: IV (GD, A Newton, C SGD, D momentum/Nesterov, E Adam), VI (linear regression, B ridge, C lasso), VII (logistic; C.1 Ising phases, C.2 SUSY; D softmax), IX (DNNs; C backprop; D regularisation, early stopping), XII.B (PCA), XIII (clustering; A.1 k-means; B GMM), XIV.B (EM), XVII.C (VAE), App. A (datasets: Ising 16 x 10^4 samples, L = 40, Metropolis; SUSY).

### S7: Deisenroth, Faisal, Ong, *Mathematics for Machine Learning*, CUP 2020
- <https://mml-book.github.io/>, PDF verified (417 pp.), sha256 `3f87b70c...838911bc`.
- Licence (copyright page): "free to view and download for personal use only. Not for re-distribution". **Cite only.**
- Locators: 4.5 SVD, 4.6 matrix approximation (Eckart-Young), 5.6 backpropagation, 7.1 GD, 7.3 convexity, 8.2 ERM, 9 linear regression, 10 PCA (10.2 max variance, 10.3 projection, 10.7 latent variable), 11 GMM (11.3 EM), 12 SVM.

### S8: Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, 2nd ed., Springer, 12th printing 2017
- <https://hastie.su.domains/ElemStatLearn/>; PDF via the author's Google Drive link (print12 with TOC), verified (764 pp.), sha256 `8d098d65...afe2e0f`.
- Copyright Springer, "agreed to allow us to keep the book available on the web". **Cite only.**
- Locators: 3.2 least squares, 3.4.1 ridge (SVD view, effective dof), 3.4.2 lasso, 3.5.1 PC regression, 4.4 logistic (4.4.1 IRLS), 7.3 bias-variance, 7.10 cross-validation and GCV, 8.5 EM, 11 neural networks (11.5 training issues), 14.3.6 k-means, 14.3.7 GMM as soft k-means, 14.5 PCA.

### S9: James, Witten, Hastie, Tibshirani, Taylor, *An Introduction to Statistical Learning with Applications in Python*, Springer 2023
- <https://www.statlearning.com/>; PDF via the author link, verified (613 pp.), sha256 `278d3bdd...ad60`. TISS lists "Springer (2010)"; the R first edition is 2013 per statlearning.com, so the TISS year is a typo. Chapter numbers below are ISLP's.
- **Cite only.** Locators: 2.2 accuracy, bias-variance; 4.3 logistic; 6.2 shrinkage; 10 deep learning (10.7 fitting, 10.8 double descent); 12.2 PCA; 12.4 clustering.

### S10: Hansen, *Discrete Inverse Problems: Insight and Algorithms*, SIAM 2010 (Fundamentals of Algorithms 7), ISBN 978-0-898716-96-2
- Not free, **not fetched**. The SIAM page returns 403 to a plain fetch; ISBN and chapter titles verified via MathWorks and Google Books listings. Chapter numbers are **inferred from the TOC order**: 2 Fredholm equation, 3 discretisation (SVD, discrete Picard condition), 4 regularisation methods (TSVD, Tikhonov), 5 parameter choice (discrepancy, GCV, L-curve), 6 iterative regularisation (Landweber, CGLS), 8 smoothing norms. Check against a library copy.

## Physics and method papers

| id | reference | status | used in |
|---|---|---|---|
| S14 | Mehta et al., notebooks `drckf/mlreview_notebooks`, <https://github.com/drckf/mlreview_notebooks>, **MIT** | verified | 10 (NB4/6 Ising, NB5 SUSY, NB15 clustering) |
| S15 | Carrasquilla, Melko, "Machine learning phases of matter", Nat. Phys. 13, 431 (2017), arXiv:1605.01735 | arXiv/DOI verified | 10 |
| S16 | Wang, "Discovering phase transitions with unsupervised learning", PRB 94, 195105 (2016), arXiv:1606.00318 | verified | 07, 10 |
| S17 | Baldi, Sadowski, Whiteson, "Searching for exotic particles in high-energy physics with deep learning", Nat. Commun. 5, 4308 (2014), arXiv:1402.4735 | verified | 04, 10 |
| S18 | Onsager, Phys. Rev. 65, 117 (1944): $T_c=2/\ln(1+\sqrt2)$ | bibliographic; $T_c$ also stated in S6 sec. VII.C.1 | 10 |
| S19 | Binder, Z. Phys. B 43, 119 (1981): fourth-order cumulant | bibliographic | 10 |
| S20 | Metropolis, Rosenbluth, Rosenbluth, Teller, Teller, J. Chem. Phys. 21, 1087 (1953) | bibliographic | 10 |
| S21 | Hansen, "Analysis of discrete ill-posed problems by means of the L-curve", SIAM Rev. 34, 561 (1992) | bibliographic | 03 |
| S22 | Jarrell, Gubernatis, "Bayesian inference and the analytic continuation of imaginary-time QMC data", Phys. Rep. 269, 133 (1996) | bibliographic | 03, 10 |
| S23 | Wallerberger et al., "sparse-ir: optimal compression and sparse sampling of many-body propagators", SoftwareX 21, 101266 (2023), arXiv:2206.11762 | verified | 03, 07, 10 |
| S24 | Sutton, Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press 2018, free PDF <http://incompleteideas.net/book/RLbook2020trimmed.pdf> (linked from S11) | URL verified | 09 |
| S25 | Watkins, Dayan, "Q-learning", Machine Learning 8, 279 (1992) | bibliographic | 09 |
| S26 | Kingma, Ba, "Adam", arXiv:1412.6980 (ICLR 2015) | verified | 01, 05 |
| S27 | Cybenko, Math. Control Signals Syst. 2, 303 (1989); Hornik, Neural Networks 4, 251 (1991) | bibliographic | 05 |
| S28 | Baldi, Hornik, "Neural networks and principal component analysis", Neural Networks 2, 53 (1989) | bibliographic | 08 |
| S29 | Eckart, Young, Psychometrika 1, 211 (1936) | bibliographic; theorem in S7 sec. 4.6 | 07, 08 |
| S30 | Polyak, USSR Comput. Math. Math. Phys. 4, 1 (1964); Nesterov, Soviet Math. Dokl. 27, 372 (1983) | bibliographic; both cited in S6 sec. IV.D | 01 |
| S31 | Hoerl, Kennard, Technometrics 12, 55 (1970) (ridge); Tibshirani, JRSS B 58, 267 (1996) (lasso) | bibliographic | 02 |
| S32 | Dempster, Laird, Rubin, JRSS B 39, 1 (1977) (EM) | bibliographic | 06 |
| S33 | Lloyd, IEEE Trans. Inf. Theory 28, 129 (1982); Arthur, Vassilvitskii, SODA 2007 (k-means++) | bibliographic | 06 |
| S34 | Gymnasium `CartPole-v1`, <https://gymnasium.farama.org/environments/classic_control/cart_pole/> (named in S5 Ex12) | not fetched | 09 |
| S35 | Hinton, Salakhutdinov, "Reducing the dimensionality of data with neural networks", Science 313, 504 (2006) | bibliographic | 08 |
| S36 | Vincent, Larochelle, Bengio, Manzagol, "Extracting and composing robust features with denoising autoencoders", ICML 2008 | bibliographic | 08 |

## Not used, and why

- **TUWEL** (2026S course page, forum, slides): login required. The 2027S TISS page links no TUWEL course yet [S1].
- **JupyterHub / nbgrader** (the graded notebooks): login required; the public S5 notebooks are the 2021S versions.
- **Earlier-semester TISS pages** beyond 2026S: not read in this pass; the 2021S grading scheme is therefore unverified.
- **Spaun et al., Nature 2016** (the absorption-spectrum figure of S5 Ex07): not read; only its role as motivation is reported.
