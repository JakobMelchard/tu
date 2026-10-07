# Sources: 101.973 Numerical Computation

Register of every source used to write and verify `../notes` and `../src`.
Notes cite these as `[S<n>]`. Retrieval dates are the day the page or file was
fetched; TISS and VoWi pages change, so re-check before an exam.

**Vendoring policy.** Nothing in this directory is a third-party file. Every
source below is either a public web page (cited) or a PDF whose licence could
not be established (cited, with a fetch command in [`fetch-sources.sh`](fetch-sources.sh)
so the file can be downloaded for personal use into the git-ignored `vendor/`).
No TUWEL material was fetched; TUWEL requires a login and is not ours to copy.

## Course-authoritative

### S1: TISS course page, 2026W (the semester being studied)

- Title: 101.973 Numerical Computation, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=101973&semester=2026W&locale=en>
- Retrieved: 2026-09-21 (browser; the page needs JavaScript). **Re-read
  2026-09-27 in a logged-in browser.**
- Access: public, no login (registration status needs the login)
- Used for: scope (subject of course, learning outcomes), lecturers
  (Faustmann, Bringmann, E101), ECTS (6.0), dates, group registration, examination
  modalities ("Short tests, Collaboration in exercise, final overall test"),
  literature ("There will be lecture notes in TUWEL!"). Diffed against
  [`../docs/tiss.md`](../docs/tiss.md); see `../notes/CHANGELOG.md`.
- State on 2026-09-27: Gruppe A Tue 10:00-11:00, Sem.R. DA grün 03 A, from
  13.10. Gruppe C moved to Tue 10:00-11:00 (DA04G10), Gruppe B Tue 11:00-12:00.
  Lectures Tue 08:00-10:00 FH HS 3 (06.10-26.01; held 27.10 and 03.11, not
  08.12) and Wed 09:00-10:00 FH HS 4 (07.10-20.01). Fri 20.11 14:00-16:00 EI 9
  "Reservation"; final exam Wed 27.01.2027 16:00-18:00 HS 18 Czuber; re-test
  Fri 19.02.2027 13:00-15:00 DA 04 G10. A TUWEL course exists.

### S2: TISS course page, 2025W (previous offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=101973&semester=2025W&locale=en>
- Retrieved: 2026-09-21
- Access: public
- Used for: the year-on-year diff. 5.5 ECTS, lecturers Sturm and Nguyen,
  examination modalities "Checkmark exercise and two tests", test dates
  21.11.2025 and 21.01.2026, re-test 20.02.2026.

### S3: TISS course page, 2024W (two offerings back)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=101973&semester=2024W&locale=en>
- Retrieved: 2026-09-21
- Access: public
- Used for: the diff. 5.5 ECTS, lecturers Sturm and Wörgötter, "Checkmark
  exercise and two tests", tests 22.11.2024 and 22.01.2025, re-test 21.02.2025.
  This page still carries a "Go to Course Materials" link; that link
  (`/education/course/documents.xhtml?courseNr=101973&semester=2024W`) redirects
  to the TU Wien IdP and was **not** followed.

### S4: Melenk & Faustmann, *Lecture Notes Numerical Computation*, WS 2023/24 ★

- Authors: J. M. Melenk, M. Faustmann, Institute of Analysis and Scientific
  Computing, TU Wien. 160 pages, "version 2 of the lecture notes, written
  during the winter term 2023" (Introduction, p. 1).
- URL: <https://www.tuwien.at/index.php?eID=dumpFile&t=f&f=202609&token=57cfb2dfeef43abeefd966ce28dc8d35e3bff56e>
  (listed as "Numerical Computation (WS 23/24)" on S5)
- Retrieved: 2026-09-21. SHA-256 and size recorded in [`README.md`](README.md).
- Access: public download, no login. **Licence: none stated ⇒ all rights
  reserved. Not vendored.** Fetch it yourself with `./fetch-sources.sh`.
- Used for: **everything**. This is the course's own script, written by the
  2026W lecturer for his own last run of 101.973 (2023W, see S9). It fixes the
  chapter order, the definitions, the theorem statements, the algorithms, the
  worked examples and (through its `(CSE)` section markers) which material is
  examined in the CSE variant of the course. Section-by-section map in
  [`lecture-notes-map.md`](lecture-notes-map.md).

### S5: Markus Faustmann, "Lecture Notes" (teaching page)

- URL: <https://www.tuwien.at/en/mg/asc/faustmann/teaching/lecture-notes>
- Retrieved: 2026-09-21
- Access: public
- Used for: locating S4, and confirming it is hosted by the lecturer himself.
  Also lists "Applied Mathematics Foundations (CSE, WT 25/26)" and "Numerics for
  PDEs (CSE, ST 25)", the sibling CSE courses; S4's introduction points at the
  first for prerequisites.

### S6: Markus Faustmann, institute profile

- URL: <https://www.tuwien.at/en/mg/asc/faustmann>
- Retrieved: 2026-09-21
- Access: public
- Used for: lecturer identity and affiliation (E101 ASC, tenure-track assistant
  professor; TU Best Teacher Award 2022, Faculty of Mathematics and
  Geoinformation).

### S7: Philipp Bringmann, institute profile

- URL: <https://www.tuwien.at/en/mg/asc/numpdes/bringmann> and
  <https://www.asc.tuwien.ac.at/~pbringma/>
- Retrieved: 2026-09-21
- Access: public
- Used for: the second lecturer named on S1. Workgroup Numerics of PDEs;
  research on least-squares FEM, adaptive mesh refinement, iterative
  linearisation, multigrid, DPG. No Numerical Computation material of his own is
  public; which half of the course he takes is **not** established.

## Student-reported (VoWi)

VoWi is the TU Wien informatics student wiki. It is a secondary source: useful
for exam format and past questions, unreliable for statements of theory. Every
solution in the exam PDFs below is a *student's* solution, explicitly marked as
such. The site is behind an Anubis proof-of-work gate, so plain HTTP clients are
refused; the pages were read in a browser.

### S8: VoWi: Numerical Computation VU (Sturm): this course, tiss:101973 ★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Numerical_Computation_VU_(Sturm)>
- Retrieved: 2026-09-21 (page last edited 2026-06-12)
- Access: public
- Used for: the topic list *as students saw it taught* in 2025W, the grading
  split (exercises 33 + written exams 66), the two-partial-exam format
  (November / January, pencil and paper), the exercise-class format (weekly
  checkmark sheets, blackboard theory + Python/MATLAB on the projector,
  attendance mandatory with one tolerated absence), the statement that the
  TUWEL lecture notes are "old (outdated)", and the student remark that
  differential equations are covered only "if time".

### S9: VoWi: Numerical Computation VU (Faustmann): tiss:101973

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Numerical_Computation_VU_(Faustmann)>
- Retrieved: 2026-09-21
- Access: public
- Used for: confirming that Faustmann last held 101.973 in **2023W** (the term
  S4 was written for) and that 101.973 is the CSE master's "Modul Numerical
  Computation".

### S10: VoWi: Computernumerik VU (Faustmann): the same lecture, tiss:101484 ★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Computernumerik_VU_(Faustmann)>
- Retrieved: 2026-09-21
- Access: public
- Used for: **three past tests set by the 2026W lecturer**, read via the page
  (scans, no text layer):
  - `Test1 02.12.2022.pdf`: <https://vowi.fsinf.at/images/8/87/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test1_02.12.2022.pdf>
  - `Test2 26.01.2023.pdf`: <https://vowi.fsinf.at/images/8/81/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test2_26.01.2023.pdf>
  - `Test3 24.02.2023.pdf`: <https://vowi.fsinf.at/images/3/39/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test3_24.02.2023.pdf>
  Plus a prose description of the 2023W Test 1 in the "Prüfung, Benotung"
  section. Digested into [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
  **Licence: student uploads of exam papers; not redistributable. Not vendored.**

### S11: VoWi: Computernumerik VU (Sturm): the same lecture, tiss:101484

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Computernumerik_VU_(Sturm)>
- Retrieved: 2026-09-21
- Access: public
- Used for: two more past tests and the grading detail:
  - `Computernumerik Test 1 2024-11-22.pdf`: <https://vowi.fsinf.at/images/e/e9/TU_Wien-Computernumerik_VU_%28Sturm%29_-_Computernumerik_Test_1_2024-11-22.pdf>
  - `Computernumerik Test 2 2025-02-22.pdf`: <https://vowi.fsinf.at/images/9/97/TU_Wien-Computernumerik_VU_%28Sturm%29_-_Computernumerik_Test_2_2025-02-22.pdf>
    (file name says 2025-02-22; the paper's own header says "22.January 2025",
    which matches the S3 test date 22.01.2025)
  and the pass criteria: >50 points overall, >60 % of exercises checked, a
  positive presentation grade, and >33 of 66 points in the written tests; a
  third test at the end of the semester covering everything if the first two
  are not enough. Exercise sheets: 10 sheets, 5 tasks each, checkmarked in
  TUWEL the day before, random selection to present.
  The page also links a copy of S4 (`skript WS23-24.pdf`), which confirms the
  script used for Computernumerik and for Numerical Computation is the same.
  **Not vendored** (same reason as S10).

## General references (cited, not course material)

Used only where the course script is silent and the notes still need a claim
sourced. Each is flagged in the note where it is used.

### S12: Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM 2002

- URL: <https://epubs.siam.org/doi/book/10.1137/1.9780898718027> (paywalled)
- ISBN 978-0-89871-521-7. Access: not free.
- Used for: the standard model of floating-point arithmetic, the $\gamma_n$
  notation, summation error bounds, the Rigal–Gaches backward-error theorem,
  growth-factor statements for Gaussian elimination. None of this is in S4;
  S4 §3 treats conditioning and stability qualitatively only.

### S13: Goldberg, "What Every Computer Scientist Should Know About Floating-Point Arithmetic", *ACM Computing Surveys* 23(1), 1991

- URL: <https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html>
- Retrieved: 2026-09-21. Access: public, hosted by Oracle. ACM copyright;
  not redistributable, **not vendored**.
- Used for: IEEE 754 formats, machine epsilon vs unit round-off, cancellation.

### S14: IEEE 754-2019, *Standard for Floating-Point Arithmetic*

- URL: <https://standards.ieee.org/ieee/754/6210/> (paywalled)
- Access: not free; **not vendored**.
- Used for: binary32/binary64 parameters quoted in the conditioning note.
  Cross-checked against `numpy.finfo` in `../src/py/test_errors.py`.

### S15: Trefethen & Bau, *Numerical Linear Algebra*, SIAM 1997

- URL: <https://epubs.siam.org/doi/book/10.1137/1.9780898719574> (paywalled)
- ISBN 978-0-89871-361-9. Access: not free; **not vendored**.
- Used for: the CGS/MGS orthogonality-loss hierarchy ($\kappa^2 u$ vs $\kappa u$),
  which S4 does not quantify (S4 only says Gram–Schmidt "is not numerically
  stable", §4.7.2).

### S16: Golub & Van Loan, *Matrix Computations*, 4th ed., JHU Press 2013

- ISBN 978-1-4214-0794-4. Access: not free.
- Used for: flop counts and the precise Householder statements. S4 explicitly
  refers the reader to "the book by Golub–van Loan" in Remark 4.52.

### S17: Shewchuk, "An Introduction to the Conjugate Gradient Method Without the Agonizing Pain", CMU-CS-94-125, 1994

- URL: <https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf>
- Retrieved: 2026-09-21. Access: public download, free. Licence: no
  redistribution notice on the title page, so **not vendored**.
- Used for: the geometric derivation of CG and the $\sqrt\kappa$ rate, as a
  companion to S4 §8.1 (four pages).

### S18: Saad, *Iterative Methods for Sparse Linear Systems*, 2nd ed., SIAM 2003

- URL: <https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf>
- Retrieved: 2026-09-21. Access: free download from the author's page.
  Licence: the front matter reads "Copyright © 2003 by the Society for
  Industrial and Applied Mathematics", so **not vendored**.
- Used for: Arnoldi and GMRES details beyond S4 §8.2, and the fill-in /
  reordering material behind S4 §4.6.

### S19: Hairer, Nørsett & Wanner, *Solving Ordinary Differential Equations I*, 2nd rev. ed., Springer 1993

- ISBN 978-3-540-56670-0. Access: not free.
- Used for: the Dormand–Prince 5(4) coefficients and the step-size controller in
  `../src/py/ode.py`. S4 §9 stops at RK4, the θ-scheme and A-stability; embedded
  pairs are **not** part of the course.

### S20: NumPy and SciPy reference documentation

- URLs: <https://numpy.org/doc/stable/reference/routines.fft.html>,
  <https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html>,
  <https://docs.scipy.org/doc/scipy/reference/interpolate.html>
- Retrieved: 2026-09-21. Access: public. Licence: BSD-3-Clause
  (redistributable), but only cited: no need to vendor a copy.
- Used for: the FFT sign and $1/N$ conventions our code matches, and the
  library routines the tests cross-check against. S4 names
  `numpy.polynomial.legendre.leggauss` (Remark 2.19),
  `scipy.interpolate.CubicSpline` (Remark 1.33), `scipy.linalg.lu`
  (Remark 4.10), `numpy.linalg.qr` (Remark 4.45) and `numpy.linalg.svd`
  (Remark 5.10) itself.

## Sources deliberately not used

- **TUWEL** (`tuwel.tuwien.ac.at`), 2026W course **id 82717**: the course's
  slides, exercise sheets and the current lecture notes are promised there
  [S1]. It requires a TU Wien login and its contents are not ours to
  redistribute. Not fetched, so nothing there has been seen: every "in TUWEL"
  statement in these notes is a TISS or VoWi claim, not a checked fact. S4 is
  the public stand-in, and S8 reports the 2025W TUWEL notes were outdated
  relative to the lecture.
- **TISS course-materials page** for 2024W (S3): redirects to the IdP login.
  Not followed.
- **The course's Mattermost channel** (`numerical-computation`, linked from S8):
  requires registration.
