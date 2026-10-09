# Sources — 192.043 Quantum Computing, Complexity Theory, and Algorithmics

Register of every source used to write and verify `../notes` and
`../src`. Notes cite these as `[S<n>]`. Retrieval dates are the day the
page or file was fetched; TISS and VoWi change, so re-check before an exam.

**Vendoring policy.** Nothing in this directory is a third-party file. Every
source below is either a public web page (cited) or a PDF whose licence is
absent or reserved (cited, with a fetch command in
[`fetch-sources.sh`](fetch-sources.sh) so it can be downloaded for personal use
into the git-ignored `vendor/`). TUWEL material needs a login and is not ours
to copy: since 2026-10-09 the TUWEL course is read for facts and cited as
[S62], in our own words, and nothing from it is vendored. See
[`README.md`](README.md) for the licence reasoning.

**The two things to internalise before reading further.**

1. **192.043 has no VoWi page, no public slides and no past paper of its own**
   [S24]. What it *does* have is a set of **sibling courses that share its
   lecturers, its material and — for the algorithmics third — its actual lecture
   slots**: 192.219 [S5], 192.036 [S6, S15–S19], 192.070 [S20, S21],
   192.165 [S7], 194.027 [S10, S22]. Everything this pass knows about the real
   shape of the course comes from those.
2. **2026W is the first 10 ECTS run.** In 2025W and 2024W the course was 7.0
   ECTS / 4.0 h and had to be combined with the 3.0 ECTS preparation course
   192.042 [S2, S3, S4]. For 2026W 192.042 is gone and its content is inside
   192.043. Year-on-year table in [`../docs/tiss.md`](../docs/tiss.md).

## Course-authoritative (TISS)

### S1 — TISS course page, 192.043, 2026W ★

- Title: 192.043 Quantum Computing, Complexity Theory, and Algorithmics, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192043&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript). Access: public, no login.
- Used for: the whole scope (three-part subject list, learning outcomes), the
  six named textbooks (S25–S30), 6.0 h / 10.0 ECTS, VU, immanent examination
  ("Exercises + written exam"), the four lecturers, the **48 single
  appointments** behind the nine date rows (expanded via "Show single
  appointments"; transcribed into `../docs/tiss.md`), the three exam dates, the
  registration and group-registration windows, "No lecture notes are available",
  and the two internal contradictions recorded in `../docs/tiss.md` §Discrepancies.
- The German `objective` field of the API record names **decoherence and
  elementary error-correction strategies**; the English one does not, and
  neither appears in the English subject list. See `../notes/00-exam-focus.md`.

### S2 — TISS course page, 192.043, 2025W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192043&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the year-on-year diff. **VU 4.0 h, 7.0 ECTS**, a TUWEL course link,
  "This course must be combined with 192.042 Introduction to Quantum Computing,
  Complexity Theory, and Algorithmics", "The first lecture is taking place on
  October 1st, **15:00** in FAV Hörsaal 3 Zemanek", the typo "MaxCut versus
  MinFlow" in the network-flow bullet, and only two date rows (Wed 15:00–19:00
  Zemanek all term + Fri 09:00–18:00 Seminarraum 384).
- **Caveat:** the Exams table on this page shows the **2026W** exam rows. TISS
  serves current exam entries regardless of which semester tab is selected, so
  exam rows are not evidence about past offerings.

### S3 — TISS course page, 192.043, 2024W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192043&semester=2024W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the diff. **VU 4.0 h, 7.0 ECTS**; six lecturers — the current four
  plus **Hans Tompits** and **Vincenzo De Maio**; "First lecture on October 28,
  14:00, Zemanek!"; **no textbook list at all**; no "O-notation / asymptotic
  order of growth" and no "Approximation" bullet; the same "MaxCut versus
  MinFlow" typo; two *written exams* on 07.02.2025 and 07.03.2025, 10:00–12:00,
  FAV HS 1 — i.e. a completely different examination pattern from 2026W.

### S4 — TISS 192.042 Introduction to Quantum Computing, Complexity Theory, and Algorithmics ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192042&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public. Offerings listed: 2025W, 2024W — **no 2026W**.
- VU 2.0 h, **3.0 ECTS**, same four lecturers, "This is the preparation part of
  the whole VU", "must be combined with 192.043".
- Used for: **the scope that moved into 192.043 in 2026W**. Its own subject list
  is: graphs (connectivity, traversal, bipartiteness, topological ordering);
  greedy (interval scheduling, MST); *basic notions of computability and
  complexity*; **problem reductions**; **formal models of computation (Turing
  machines, random access machines, …)**; discussion of the (extended)
  Church–Turing thesis; quantum basic notions; programming techniques and
  reverse computation. 7.0 + 3.0 = 10.0 ECTS is exactly the 2026W figure.

### S5 — TISS 192.219 Supplementary Course Algorithms and Data Structures, 2026W ★★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192219&semester=2026W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- **The single most valuable source of this pass.** VU 4.0 h, 6.0 ECTS,
  lecturers **Chen, Pichler** plus five tutors (Mondejar, Unterberger, Sorge,
  Saghafian, Manrique Merchan).
- It shares five date rows with S1 **verbatim**: first meeting Thu 01.10.2026 in
  EI 11 HS, Fri 10:00–13:00 EI 10 (02.10–06.11), Mon 14:00–17:00 EI 8
  (05.10–19.10), Wed 15:00–18:00 EI 5 (07.10–04.11), Fri 09.10 EI 10. Its main
  exam is **Fri 11.12.2026, 09:00–12:00** — the same slot as 192.043's Exam 1 —
  and its retake is **Tue 09.03.2027, 14:00–17:00**.
- Used for: (i) establishing that the **algorithmics block of 192.043 is taught
  jointly with 192.219 by Chen and Pichler in October–November**; (ii) resolving
  the first-meeting time (its prose *and* its date table both say 14:00–17:00);
  (iii) corroborating a 14:00 start for the March retake; (iv) a **finer
  syllabus** than S1 for the algorithmics part — it additionally names *data
  structures for graphs*, *interval partitioning*, *priority queues*, *merge
  sort*, the *MaxFlow–MinCut theorem*, and in the complexity part *basic notions
  of Turing machines* and **the polynomial hierarchy**; (v) the format
  statement: "all lectures and exercises will be given from October to
  No[v]ember: 3 sessions per week, 3 hours per session. There will be five
  exercise sessions"; (vi) examination modalities "Exercises with presentation
  and closed book written exam"; (vii) the two named books, Kleinberg–Tardos and
  Papadimitriou.

### S6 — TISS 192.036 Introduction to Quantum Computing (Einführung in Quantencomputing)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192036>
- Retrieved: 2026-09-22. Access: public.
- Egly + Tompits, 6.0 ECTS, bachelor Informatics. Last held 2026S [S15].
- Used for: identifying the course whose exercise sheets, programming
  assignments and exam protocols are public on VoWi (S15–S19) and whose lecture
  order matches 192.043's quantum third.

### S7 — TISS 192.165 Complexity Theory, 2026W (Pichler)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192165&semester=2026W&locale=en>
- Retrieved: 2026-09-22. Access: public. VU 4.0 h, 6.0 ECTS, **Pichler alone**.
- Subject: "basic notions of complexity theory, deterministic und
  non-deterministic complexity classes, in particular: the classes L, NL, P, NP,
  **the polynomial hierarchy**, PSPACE, and EXPTIME. We also look **inside the
  class P to study parallelizable problems**."
- Used for: Pichler's own authoritative topic list and ordering for the
  complexity third of 192.043, and as the justification for the polynomial
  hierarchy and NC/circuit material in `../notes/B02`, `B03`, `B04`. Its dates
  (Tue 09:00–11:00 Gödel, Wed 13:00–15:00 Zemanek) do **not** coincide with
  192.043's, so this is a separate course, not a co-taught block.

### S8 — TISS 181.142 Complexity theory (old number, cancelled in 2026W)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=181142&semester=2026W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the "same lecture, two course numbers" trail. The page states it is
  the old-curriculum course "replaced by the new course 192.165 Complexity
  Theory with 6 ECTS" from 2025W. Its VoWi page [S23] and its course homepage
  [S14] carry the past exam and the only public slides.

### S9 — TISS 192.017 Theoretical Computer Science, 2026W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192017&semester=2026W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: checking whether Fermüller's bachelor course shares slots with
  192.043 (it does **not**: Mon 12:00–14:00 and Wed 13:00–15:00,
  Informatikhörsaal). Its scope — automata, formal languages, computability and
  complexity, formal semantics — is the background 192.043 assumes.

### S10 — TISS 194.027 Hybrid Quantum-Classical Systems

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=194027>
- Retrieved: 2026-09-22. Access: public. Brandic, De Maio, Friis, Guggemos et al.
- Used for: locating the material behind 192.043's "variational solvers and
  examples for combined classical/quantum algorithms" bullet. **De Maio was a
  192.043 lecturer in 2024W** [S3], and this is his course.

## Lecturers

### S11 — Jiehua Chen

- URLs: <https://informatics.tuwien.ac.at/people/jiehua-chen>, <https://www.ac.tuwien.ac.at/people/jchen/>
- Retrieved: 2026-09-22. Access: public.
- Associate Professor, research unit **Algorithms and Complexity (E192-01)**.
  2026W/2027S teaching: 186.819, **192.163 Beyond Exact Algorithms**, 194.203,
  **192.043**, 194.204, 193.052, 180.773, 180.010, **192.219 Supplementary
  Course Algorithms and Data Structures**, 192.021, 186.199. VoWi lists her
  under Algorithms in Graph Theory, Algorithmic Social Choice, Beyond Exact
  Algorithms, Advanced Research in Algorithmics [S24].
- Used for: attributing the **algorithmics** block. No lecture notes, script or
  slides of hers are public anywhere that was searched.

### S12 — Uwe Egly

- URL: <https://informatics.tuwien.ac.at/people/uwe-egly>
- Retrieved: 2026-09-22. Access: public.
- **Ao.Univ.-Prof. i.R.** (retired), research unit Knowledge-Based Systems
  (E192-03). 2026W teaching: 184.713 and **192.043**.
- Used for: attributing the **quantum computing** block — he is the lecturer of
  192.036 [S6, S15] and 192.070 [S20], whose exercise sheets, programming
  assignments and student summary are the only public teaching material of any
  192.043 lecturer on the quantum side.

### S13 — Christian Fermüller

- URL: <https://informatics.tuwien.ac.at/people/christian-fermueller>
- Retrieved: 2026-09-22. Access: public.
- Ao.Univ.Prof., research unit **Theory and Logic (E192-05)**. 2026W/2027S
  teaching includes 184.766 Introduction to Logical Methods in CS, 185.A45
  **Logic and Computability**, 192.017 **Theoretical Computer Science**,
  **192.043**, 194.203/194.204 (the QIST project and seminar).
- Used for: the lecturer attribution attempt. **Which part he teaches could not
  be established** — see `../refs/lecture-notes-map.md`. His own courses are the
  computability / formal-models end (Turing machines, Church–Turing, reductions),
  which is exactly the block 192.042 [S4] used to carry, so that is the
  inference recorded, explicitly flagged as an inference.

### S14 — Reinhard Pichler, and his Complexity Theory course homepage ★

- URLs: <https://informatics.tuwien.ac.at/people/reinhard-pichler>,
  <https://www.dbai.tuwien.ac.at/staff/pichler/complexity/>
- Slides fetched: <https://www.dbai.tuwien.ac.at/staff/pichler/complexity/slides/cc01.pdf>
  (299 431 bytes) and `cc02.pdf` (215 563 bytes).
- Retrieved: 2026-09-22. Access: public download, no login. **Licence: none
  stated ⇒ all rights reserved. Not vendored.** Fetch with `./fetch-sources.sh`.
- Probing `cc03.pdf` … `cc16.pdf` returns 404: **only the first two decks are
  public.** They are the general-information deck and the recapitulation deck.
- Used for: Pichler's own wording of the complexity syllabus and its order —
  "Turing Machines, Complexity Classes / Logarithmic Space / Boolean Logic,
  proof of the Cook–Levin Theorem / More NP-Completeness / The polynomial
  hierarchy / The class PSPACE / Applications (Database Theory, Abduction, …) /
  Fixed-Parameter Tractability"; his recapitulation checklist (decision vs
  function vs optimization vs enumeration vs counting problems; Cook and Karp
  reductions; L, NL, co-NL, P, NP, co-NP, PSPACE, EXPTIME, NEXPTIME,
  co-NEXPTIME, EXPSPACE); and his two references, Papadimitriou [S26] and
  Garey & Johnson. The page also links six papers he sets as reading
  (Johnson 1990, Vollmer 1999, Cook 2003, Dantsin et al. 2001, Eiter & Gottlob
  1995, Hermann & Pichler 2007) — `fetch-sources.sh` pulls them.

## Student-reported (VoWi)

VoWi is the TU Wien informatics student wiki. It is a **secondary** source:
reliable for format, dates and which topics were taught, unreliable for
statements of theory. Every summary and protocol below is a *student's* work.
The site runs an Anubis proof-of-work bot gate, so plain HTTP clients get a
challenge page; everything below was read in a browser, and the PDFs were
extracted with pdf.js from inside the page.

### S15 — VoWi: Einführung in Quantencomputing VU (Egly) — tiss:192036 ★★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Einf%C3%BChrung_in_Quantencomputing_VU_(Egly)>
- Retrieved: 2026-09-22 (page last edited 2026-07-05). Access: public.
- Used for: **the split of the quantum material between the two lecturers**, in
  the students' words: "Der Inhalt der LVA ist in 2 Teile geteilt: **Formale
  Grundlagen (Prof. Tompits)** … **Quantenalgorithmen (Prof. Egly)**", with
  Egly's half listed as "Superdense Coding, Quantenteleportation oder Deutsch &
  co. über Suchalgorithmen wie Grover, … Quantum Fourier Transformation, Quantum
  Phase Estimation und letztendlich zum … Shor". Also: Qiskit/Python is the tool;
  no recordings, no script, slides only in TUWEL; the SS26 assessment split
  (exercise test 15 %, three programming assignments 8/8/9 = 25 %, final exam
  60 %, with hurdles 7/15 and 30/60); prerequisites (complex vector spaces,
  matrices, eigenvectors/eigenvalues); the warning that the slides alone are
  hard to learn from.

### S16 — VoWi: Egly's Exercise Sheets 1–4 (192.036) ★★

- URLs (VoWi image store, `.../images/<hash>/TU_Wien-Einführung_in_Quantencomputing_VU_(Egly)_-_Exercise_Sheet_<k>.pdf`):
  1 → `c/cc`, 2 → `8/8d`, 3 → `6/64`, 4 → `f/f9`
- Headers: Sheet 1 "VU Introduction to Quantum Computing SS 2024"; Sheet 2
  "192.036 … SS 2025 … Uwe Egly"; Sheets 3 and 4 "192.036 … **SS 2026** … Uwe Egly".
- Retrieved: 2026-09-22. Access: public. **Licence: none. Not vendored.**
- Used for: **the single richest source of verifiable course-specific content in
  this pass.** Sheet 1 is Tompits' mathematics (complex numbers, inner-product
  norms, the parallelogram law, self-adjoint/unitary/projection operators,
  eigenvalue facts, $A\otimes B$ unitary, expectation values real, and
  **Exercise 10: every pair of Pauli matrices commutes or anticommutes**).
  Sheets 2–4 are Egly's: a three-qubit circuit with the register written
  $t\otimes i_1\otimes i_0$ (the course's qubit ordering); a model-counting +
  uncomputation exercise on
  $x_6\wedge\lnot(x_5\wedge x_4\wedge x_3\wedge\lnot(x_2\wedge\lnot(x_1\wedge x_0)))$;
  a construction of formulas with a prescribed number of models; a
  **$k$-balanced generalisation of Deutsch–Jozsa**; the orthogonality
  $\langle\psi_s|\psi_t\rangle=\delta_{s,t}$ of Bernstein–Vazirani states; the
  identity $-D = H^{\otimes n}X^{\otimes n}C^{n-1}Z\,X^{\otimes n}H^{\otimes n}$;
  three state-preparation targets (GHZ, a $\tfrac1{\sqrt{12}}(3,1,1,1)$ state, the
  W state); **the course's own non-Qiskit rotation gate**
  $R_x(\theta)=\bigl(\begin{smallmatrix}\cos\theta/2&\sin\theta/2\\-\sin\theta/2&\cos\theta/2\end{smallmatrix}\bigr)$
  with the explicit remark "The rotation gate here is different from the RX gate
  in Qiskit"; the decomposition $U=e^{i\delta}P(\alpha)R_x(\theta)P(\beta)$;
  $cR_x$ from two CNOTs; $V=\tfrac12\bigl(\begin{smallmatrix}1+i&1-i\\1-i&1+i\end{smallmatrix}\bigr)$
  as a product of $H$ and $T$; amplitude amplification with certainty at
  $p_G=\tfrac12$; the rotate-by-one gate $K_n$; the tensor form
  $D_N=\bigotimes_{i=1}^n P(\pi/2^i)$; and the **recursive QFT identity**
  $F_{2N}=(H\otimes I^{\otimes n})(|0\rangle\langle0|\otimes I^{\otimes n}+|1\rangle\langle1|\otimes D_{2^n})(I\otimes F_N)K_{n+1}$.
  The sheets are graded work of a running course; this wiki does not solve them.

### S17 — VoWi: Egly's Programming Exercises 1–3 (192.036)

- URLs: `.../images/5/52/…Programming_exercise_sheet_1.pdf` (SS 2024),
  `.../images/9/9c/…_2.pdf` (SS 2026), `.../images/3/34/…_3.pdf` (SS 2026)
- Retrieved: 2026-09-22. Access: public. Licence: none. Not vendored.
- Used for: what the programming half actually asks. PE1: build a reversible
  **integer division** gate from given `subo`/`cadd` gates and use it to invert a
  number. PE2: the gate $M_3$ with $M_3^3=I$, a controlled $cM_3$, and a
  `mod[q]` Hamming-weight gate for **recursive Fourier sampling**; it prints
  *both* the lecture's matrix and "the following matrix is generated by Qiskit
  (with Qiskit's bit order)" — the two differ by bit-reversal conjugation, which
  is reproduced in the tests. PE3: Grover over a propositional formula with a
  prescribed number of models.

### S18 — VoWi: "Gedächtnisprotokoll exercise test qci" (192.036)

- URL: `https://vowi.fsinf.at/images/d/da/TU_Wien-Einf%C3%BChrung_in_Quantencomputing_VU_%28Egly%29_-_Ged%C3%A4chtnisprotokoll_exercise_test_qci.pdf`
- Retrieved: 2026-09-22. Access: public. One page, three questions, student-written.
- Used for: **real exam-style questions** (see `../notes/00-exam-focus.md`):
  prove $(T\circ S)^* = S^*\circ T^*$ from the defining property of the adjoint;
  count models of the sheet-2 formula *without enumerating* and build an
  uncomputed circuit for it; construct and *prove correct* a gate array
  preparing $\tfrac1{\sqrt2}(|000\rangle+|111\rangle)$.

### S19 — VoWi: "Gedächtnisprotokoll oral exam qci" (192.036)

- URL: `https://vowi.fsinf.at/images/c/c5/TU_Wien-Einf%C3%BChrung_in_Quantencomputing_VU_%28Egly%29_-_Ged%C3%A4chtnisprotokoll_oral_exam_qci.txt`
- Retrieved: 2026-09-22. Access: public. Plain text, student-written.
- Used for: how the oral is conducted. Tompits asks the definitional chain
  (qubit → unit vector in a 2-dimensional Hilbert space → $\mathbb{C}^2$ →
  several qubits → tensor product → *why* the tensor product → postulate 4 → the
  other postulates → Schrödinger equation → its solution → "what kind of
  equation is that and what does it mean" → linear ⇒ superposition principle).
  Egly asks one algorithm in depth — here **amplitude amplification**, "eine
  Generalisation vom Grover", with the two bases on the unit circle, and the
  protocol records that **no exact iteration count or calculation was demanded**.

### S20 — VoWi: Quantum Computing VU (Egly, Tompits) — tiss:192070 — and the WS2023 summary ★

- Page: <https://vowi.fsinf.at/wiki/TU_Wien:Quantum_Computing_VU_(Egly)>
- File: `https://vowi.fsinf.at/images/2/25/TU_Wien-Quantum_Computing_VU_%28Egly%29_-_Summary_QC_WS2023.pdf`
  (541 KB, 21 pages, "Quantum Computing – Summary WS2023/24, Manuel Waibel,
  February 15, 2024")
- Retrieved: 2026-09-22. Access: public. **Licence: none. Not vendored.**
- Used for: **the lecture order of the quantum block**, which is the closest
  thing to a syllabus that exists for this material:
  0 Introduction (qubit, entanglement, **noise: gate infidelity and
  decoherence**) · 1 Principles of QM I (classes of operators, bra-ket) ·
  2 Principles of QM II & quantum gates (the four postulates, registers,
  NOT/H/phase/T/rotation/CNOT/SWAP, universality) · 3 Preparatory concepts
  (multi-controlled gates and **Gray code**, reversibility and garbage,
  **phase kickback**) · 4 Algorithms I (**superdense coding**, teleportation,
  Deutsch, Deutsch–Jozsa, Bernstein–Vazirani) · 5 Algorithms II (Grover, Simon) ·
  6 Algorithms III (QFT, QPE) · 7 Algorithms IV (Shor).
  Also for the course's stated conventions: the Grover iteration counts
  $\lfloor\frac\pi4\sqrt{2^n}\rfloor$ and $\lfloor\frac\pi4\sqrt{2^n/k}\rfloor$;
  $D=H^{\otimes n}(2|0^n\rangle\langle0^n|-I_n)H^{\otimes n}$; the BV register
  written $|z\rangle=|z_{n-1}\cdots z_0\rangle$ and the optimisation
  $H\cdot\mathrm{CNOT}\cdot H=\mathrm{CNOT}$ with control and target exchanged;
  the QFT product form with the **output in reverse bit order** and the remark
  that one may either add SWAPs or relabel; the QPE error bound
  $0\le|\delta|\le2^{-(t+1)}$; and Shor's register-size rule $N^2\le q\le 2N^2$
  with $q=2^\ell$.
  **This is a student summary and it contains errors** (its Deutsch–Jozsa and
  Simon sections state the promise incorrectly). It is used for *scope, order
  and convention*, never for a statement of theory; theory is cited to
  S30/S31/S35–S40.

### S21 — VoWi: Quantum Computing VU (Egly, Tompits), oral exam 2021-03-12

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Quantum_Computing_VU_(Egly,_Tompits)/Pr%C3%BCfung_2021/03/12>
- Retrieved: 2026-09-22. Access: public. Three candidates' recollections.
- Used for: the shape of an Egly/Tompits oral — one mathematics/postulates
  question plus one algorithm question each: (1) linear operators, their types,
  eigenvalues of a self-adjoint operator + **explain Grover: what it does, what
  diffusion is, how often to repeat**; (2) the postulates, 2 and 3 in detail +
  **explain Shor: what is computed, how, why should $q$ be large**;
  (3) qubit/register/algorithm, which gates exist, explain the Hadamard +
  **explain Deutsch–Jozsa: what it does, what is measured**. Closing remark:
  "bei den Algorithmen wurden keine Formeln oder Berechnungen gefragt".

### S22 — VoWi: Hybrid Quantum-Classical Systems VU (De Maio) — tiss:194027

- Page: <https://vowi.fsinf.at/wiki/TU_Wien:Hybrid_Quantum_-_Classical_Systems_VU_(De_Maio)>
- Files used: `.../images/e/ea/…HQCS_Second_assignment_2024.pdf`, and the page
  lists the first assignment, its solution, and the group assignment.
- Retrieved: 2026-09-22. Access: public. Licence: none. Not vendored.
- Used for: the treatment of the variational bullet. The second assignment is
  exactly VQA theory (step size and loss landscape, where VQAs could beat
  gradient-based classical methods, whether VQAs have better runtime
  complexity), **bin packing → quadratic model → QUBO → QAOA → warm-start QAOA →
  quantum annealing**, with ansatz depth $p\in\{1,3\}$, optimisers COBYLA /
  SLSQP / SPSA, noiseless and noisy simulators; and Grover applied to a
  Hamiltonian-path and a graph-3-colouring instance. Grading: assignments
  10/15/25 %, written exam 50 %, presentation 5 %, bonus 10 %.

### S23 — VoWi: Komplexitätstheorie VU (Pichler) — tiss:181142

- Page: <https://vowi.fsinf.at/wiki/TU_Wien:Komplexit%C3%A4tstheorie_VU_(Pichler)>
  (redirect target of `TU_Wien:Complexity_Theory_VU_(Pichler)`)
- Files: `.../images/f/f4/…-_Exam-ws2021.pdf`,
  `.../images/7/7a/…-_Folien_Einstufungstest_L%C3%B6sungen%281%292023.pdf`
- Retrieved: 2026-09-22. Access: public. Licence: none. Not vendored.
- Used for: how Pichler examines complexity theory. Reported format (WS 2021/22
  and WS 2023/24): an **admission test** ("Eintrittstest: Beweise Korrektheit
  einer NP-Hardness Reduktion", the reduction itself given — in WS2023/24
  Vertex Cover ↔ Dominating Set), a **written test** ("Beweise Korrektheit einer
  $\Pi_2^p$ Reduktion", again with the reduction given), and an **optional oral**
  that can move the grade by $\pm1$. Prerequisite chain named by students:
  Theoretische Informatik und Logik, Formale Methoden der Informatik (NP,
  reductions), Algorithmen auf Graphen.

### S24 — VoWi: **192.043 has no page**, and the searches that establish it

- Searches run on 2026-09-22 at <https://vowi.fsinf.at/index.php?title=Spezial:Suche>
  with `profile=all&fulltext=1`: `192043` → no results; `Quantum Computing,
  Complexity Theory` → no results; `Quantum Computing` → 19 hits, none of them
  192.043; `Chen`, `Pichler` → the lecturers' other courses only.
- Access: public.
- Used for: the **central negative result**. There is no student page, no
  Gedächtnisprotokoll and no past paper for 192.043 itself. Everything in
  `../notes/00-exam-focus.md` is therefore inferred from the sibling courses and
  is marked as such.

## Textbooks named on the TISS page

TISS lists six with no editions or links [S1]. All six are commercial; none is
vendored. Kleinberg–Tardos and Papadimitriou are the two the algorithmics /
complexity lecturers also name on their own pages [S5, S14].

### S25 — Kleinberg & Tardos, *Algorithm Design*

- Jon Kleinberg, Éva Tardos, Addison-Wesley/Pearson, 2006, ISBN 0-321-29535-8.
- Author-hosted companion: <https://www.cs.princeton.edu/~wayne/kleinberg-tardos/>
  (Kevin Wayne's slide set for the book, public, no licence statement).
- Retrieved: 2026-09-22. Access: book commercial; slides public.
- Used for: **the entire A-series**. The 192.043 and 192.219 subject lists are
  effectively a chapter list of this book: ch. 2 (asymptotics), 3 (graphs),
  4 (greedy: interval scheduling, scheduling to minimise lateness, MST),
  5 (divide and conquer: inversions, closest pair, recurrences), 6 (dynamic
  programming: weighted interval scheduling, knapsack, Bellman–Ford),
  7 (network flow: Ford–Fulkerson, max-flow/min-cut, applications),
  8 (NP-completeness), 11 (approximation), 11.6 (LP rounding).
- Note: 192.219's TISS page [S5] links a GitHub copy of the book PDF. That copy
  is an unauthorised upload; it is **not** cited here and not fetched.

### S26 — Papadimitriou, *Computational Complexity*

- Christos H. Papadimitriou, Addison-Wesley, 1994, ISBN 0-201-53082-1.
- Publisher record: <https://dl.acm.org/doi/book/10.5555/1074100>
- Access: commercial. Not vendored.
- Used for: **the entire B-series**, and it is the book Pichler sets in his own
  complexity course [S14]. ch. 2 (Turing machines), 7 (P, NP), 8 (NP-complete
  problems), 9 (reductions), 16 (PSPACE, games), 17 (PH), 11 (randomised
  classes), 15 (circuit complexity), 16.2 (L, NL, Immerman–Szelepcsényi).

### S27 — Aaronson, *Quantum Computing since Democritus* — and the free lecture notes it grew from

- Scott Aaronson, Cambridge University Press, 2013, ISBN 978-0-521-19956-8.
- **Free precursor:** the PHYS 771 lecture notes, <https://www.scottaaronson.com/democritus/>
  (retrieved 2026-09-22; public; no licence statement ⇒ cite-only).
- Used for: the conceptual framing of B05/B06 and C04 — what BQP is and is not,
  why "quantum parallelism" is not a speedup, the sceptical reading of quantum
  advantage claims, and the standard narrative order (lectures 9 quantum,
  10 quantum computing, 11 penrose, 12 decoherence, 13 proofs, 14 how big are
  quantum states, 24 complexity of religion).

### S28 — Kaye, Laflamme, Mosca, *An Introduction to Quantum Computing*

- Phillip Kaye, Raymond Laflamme, Michele Mosca, Oxford University Press, 2007
  (2006 printing), ISBN 978-0-19-857049-3.
  <https://global.oup.com/academic/product/an-introduction-to-quantum-computing-9780198570004>
- Access: commercial. Not vendored.
- Used for: C01–C07. This is the book whose treatment is closest to the way the
  course presents the algorithms (oracle conventions, the $\mathbb{Z}_2^n$
  Fourier view of Deutsch–Jozsa/BV, Simon before Shor, order finding as phase
  estimation). ch. 2–4 background, 5–6 simple algorithms, 7 QFT/phase
  estimation/order finding, 8 Grover and amplitude amplification.

### S29 — Rieffel & Polak, *Quantum Computing: A Gentle Introduction*

- Eleanor G. Rieffel, Wolfgang H. Polak, MIT Press, 2011 (paperback 2014),
  ISBN 978-0-262-01506-6. (TISS spells the second author "Pollak" and dates it
  2014 [S1].) <https://mitpress.mit.edu/9780262526678/quantum-computing/>
- Access: commercial. Not vendored.
- Used for: C01–C03 (state spaces, entanglement, teleportation, superdense
  coding) and C08's framing.

### S30 — Nielsen & Chuang, *Quantum Computation and Quantum Information* (10th anniversary ed.)

- Michael A. Nielsen, Isaac L. Chuang, Cambridge University Press, 2010,
  ISBN 978-1-107-00217-3.
  <https://www.cambridge.org/highereducation/books/quantum-computation-and-quantum-information/01E10196D0A682A6AEFFEA52D53BE9AE>
- Access: commercial. Not vendored.
- Used for: **the default citation for every theorem statement in C01–C07**:
  1.3 (circuit model), 1.4.3–1.4.4 (Deutsch, Deutsch–Jozsa), 2.2 (postulates),
  2.3 (teleportation, superdense coding), 4.2–4.5 (gates, universality,
  Solovay–Kitaev), 4.3 (controlled-$U$ from CNOTs), 5.1–5.3 (QFT, phase
  estimation, order finding, factoring), 6.1–6.6 (Grover, optimality),
  Appendix 4 (number theory, continued fractions, Theorem A4.13).

## Free lecture notes and reference works

### S31 — de Wolf, *Quantum Computing: Lecture Notes* ★

- Ronald de Wolf, QuSoft/CWI and University of Amsterdam. arXiv:1907.09415,
  latest version v6 (2026-08-27).
  <https://arxiv.org/abs/1907.09415>
- Retrieved: 2026-09-22. Access: free download.
  **Licence: arXiv non-exclusive distribution licence (v1.0)** — that licence
  grants arXiv the right to distribute, not third parties. **Not vendored**;
  `fetch-sources.sh` downloads it.
- Used for: the best free substitute for the missing course script, written from
  exactly this course's angle (theoretical computer science). Chapters used:
  1–2 (circuit model), 4 (Deutsch–Jozsa, Bernstein–Vazirani), 5 (Simon),
  6 (QFT, period finding), 7 (Shor), 9 (Grover and its optimality),
  10 (query lower bounds, polynomial and adversary methods),
  13–14 (quantum complexity theory), plus the exercises with hints.

### S32 — Watrous, quantum computation lecture notes

- John Watrous, University of Waterloo. <https://cs.uwaterloo.ca/~watrous/QC-notes/>
- Retrieved: 2026-09-22. Access: public, no licence statement ⇒ cite-only.
- Used for: the complexity-theoretic notes in B06 (BQP definitions and
  robustness, QMA, the Feynman path sum giving BQP ⊆ PP).

### S33 — Matuschak & Nielsen, *Quantum computing for the very curious*

- Andy Matuschak, Michael A. Nielsen, 2019. <https://quantum.country/qcvc>
- Retrieved: 2026-09-22. Access: free to read in the browser; **no licence
  statement on the page ⇒ all rights reserved**. Not vendored, not scraped.
- Used for: nothing load-bearing. It is listed because the course brief names it
  and because it is the gentlest correct treatment of C01–C03 for someone
  meeting the circuit model for the first time; every claim it supports here is
  also cited to S30 or S31.

### S34 — Complexity Zoo

- <https://complexityzoo.net/Complexity_Zoo>
- Retrieved: 2026-09-22. Access: public wiki.
- Used for: cross-checking the definitions and known inclusions of the classes
  in B02–B06 (L, NL, NC, AC, P/poly, ZPP, RP, BPP, PP, ⊕P, PH, PSPACE, BQP,
  QMA, QCMA, MA) and for the standard references attached to each. Secondary
  source; every inclusion asserted in the notes is additionally sourced to a
  paper or to S26/S30/S31.

## Primary papers

Each entry gives the DOI or arXiv identifier and what it is cited for.
Publisher pages for older SIAM/Royal Society items block scripted access;
the DOIs are the durable identifiers.

### S35 — Deutsch 1985

- D. Deutsch, "Quantum theory, the Church–Turing principle and the universal
  quantum computer", *Proc. R. Soc. Lond. A* **400**, 97–117.
  doi:[10.1098/rspa.1985.0070](https://doi.org/10.1098/rspa.1985.0070)
- Used for: the universal quantum computer, the quantum Church–Turing principle
  (B06), and Deutsch's one-query algorithm (C03).

### S36 — Deutsch & Jozsa 1992

- D. Deutsch, R. Jozsa, "Rapid solution of problems by quantum computation",
  *Proc. R. Soc. Lond. A* **439**, 553–558.
  doi:[10.1098/rspa.1992.0167](https://doi.org/10.1098/rspa.1992.0167)
- Used for: the Deutsch–Jozsa problem and its exact one-query algorithm (C03).

### S37 — Bernstein & Vazirani 1997

- E. Bernstein, U. Vazirani, "Quantum complexity theory", *SIAM J. Comput.*
  **26**(5), 1411–1473 (STOC 1993).
  doi:[10.1137/S0097539796300921](https://doi.org/10.1137/S0097539796300921)
- Used for: the BV problem and the recursive-Fourier-sampling separation (C03);
  the definition of BQP, its robustness, the universal quantum Turing machine,
  and **BQP ⊆ PSPACE** (B06).

### S38 — Simon 1997

- D. R. Simon, "On the power of quantum computation", *SIAM J. Comput.*
  **26**(5), 1474–1483 (FOCS 1994).
  doi:[10.1137/S0097539796298637](https://doi.org/10.1137/S0097539796298637)
- Used for: Simon's problem, the $O(n)$-query algorithm and the
  $\Omega(2^{n/2})$ classical bound (C05).

### S39 — Grover 1996

- L. K. Grover, "A fast quantum mechanical algorithm for database search",
  STOC '96, 212–219. doi:[10.1145/237814.237866](https://doi.org/10.1145/237814.237866);
  arXiv:[quant-ph/9605043](https://arxiv.org/abs/quant-ph/9605043)
- Used for: the search algorithm and the diffusion operator (C04).

### S40 — Shor 1997

- P. W. Shor, "Polynomial-time algorithms for prime factorization and discrete
  logarithms on a quantum computer", *SIAM J. Comput.* **26**(5), 1484–1509
  (FOCS 1994). doi:[10.1137/S0097539795293172](https://doi.org/10.1137/S0097539795293172);
  arXiv:[quant-ph/9508027](https://arxiv.org/abs/quant-ph/9508027)
- Used for: factoring and discrete log (C07), including the register-size rule
  $N^2\le q\le 2N^2$ that S20 quotes.

### S41 — Bennett, Bernstein, Brassard, Vazirani 1997 (BBBV)

- "Strengths and weaknesses of quantum computing", *SIAM J. Comput.* **26**(5),
  1510–1523. doi:[10.1137/S0097539796300933](https://doi.org/10.1137/S0097539796300933);
  arXiv:[quant-ph/9701001](https://arxiv.org/abs/quant-ph/9701001)
- Used for: the $\Omega(\sqrt N)$ lower bound for unstructured search and the
  hybrid argument (C04), and "NP ⊄ BQP relative to a random oracle" (B06).

### S42 — Bennett et al. 1993 (teleportation)

- C. H. Bennett, G. Brassard, C. Crépeau, R. Jozsa, A. Peres, W. K. Wootters,
  "Teleporting an unknown quantum state via dual classical and
  Einstein–Podolsky–Rosen channels", *Phys. Rev. Lett.* **70**, 1895.
  doi:[10.1103/PhysRevLett.70.1895](https://doi.org/10.1103/PhysRevLett.70.1895)
- Used for: the teleportation protocol and its correction table (C03).

### S43 — Bennett & Wiesner 1992 (superdense coding)

- "Communication via one- and two-particle operators on Einstein–Podolsky–Rosen
  states", *Phys. Rev. Lett.* **69**, 2881.
  doi:[10.1103/PhysRevLett.69.2881](https://doi.org/10.1103/PhysRevLett.69.2881)
- Used for: superdense coding (C03), which S20 shows the course teaches *before*
  teleportation.

### S44 — Bennett 1973 (reversible computation)

- C. H. Bennett, "Logical reversibility of computation", *IBM J. Res. Dev.*
  **17**(6), 525–532. doi:[10.1147/rd.176.0525](https://doi.org/10.1147/rd.176.0525)
- Used for: compute–copy–uncompute and the garbage argument (C02). Landauer's
  principle: R. Landauer, *IBM J. Res. Dev.* **5**(3), 183–191 (1961),
  doi:[10.1147/rd.53.0183](https://doi.org/10.1147/rd.53.0183).

### S45 — Kitaev 1995 (phase estimation)

- A. Yu. Kitaev, "Quantum measurements and the Abelian Stabilizer Problem",
  arXiv:[quant-ph/9511026](https://arxiv.org/abs/quant-ph/9511026)
- Used for: phase estimation (C06).

### S46 — Brassard, Høyer, Mosca, Tapp 2002 (amplitude amplification)

- "Quantum amplitude amplification and estimation", *AMS Contemporary
  Mathematics* **305**, 53–74.
  arXiv:[quant-ph/0005055](https://arxiv.org/abs/quant-ph/0005055)
- Used for: amplitude amplification and quantum counting (C04). This is the
  topic the oral protocol S19 records Egly asking about.

### S47 — Boyer, Brassard, Høyer, Tapp 1998 (BBHT)

- "Tight bounds on quantum searching", *Fortschritte der Physik* **46**, 493–505.
  arXiv:[quant-ph/9605034](https://arxiv.org/abs/quant-ph/9605034)
- Used for: search with an unknown number of solutions, the
  $\frac1m\sum_{k<m}\sin^2\frac{(2k+1)\theta}2 = \frac12-\frac{\sin 2m\theta}{4m\sin\theta}$
  identity (verified numerically), and the $\frac\pi4\sqrt{N/M}$ count (C04).

### S48 — Farhi, Goldstone, Gutmann 2014 (QAOA)

- "A Quantum Approximate Optimization Algorithm",
  arXiv:[1411.4028](https://arxiv.org/abs/1411.4028)
- Used for: the QAOA construction, the ring-of-disagrees ratio
  $\frac{2p+1}{2p+2}$, and the 3-regular $p=1$ ratio $0.6924$ (C08).

### S49 — Peruzzo et al. 2014 (VQE)

- A. Peruzzo, J. McClean, P. Shadbolt, M.-H. Yung, X.-Q. Zhou, P. J. Love,
  A. Aspuru-Guzik, J. L. O'Brien, "A variational eigenvalue solver on a photonic
  quantum processor", *Nat. Commun.* **5**, 4213.
  doi:[10.1038/ncomms5213](https://doi.org/10.1038/ncomms5213)
- Used for: VQE (C08).

### S50 — O'Malley et al. 2016 (the H₂ coefficients) ★

- P. J. J. O'Malley et al., "Scalable quantum simulation of molecular energies",
  *Phys. Rev. X* **6**, 031007.
  doi:[10.1103/PhysRevX.6.031007](https://doi.org/10.1103/PhysRevX.6.031007);
  arXiv:[1512.06860](https://arxiv.org/abs/1512.06860)
- Used for: the two-qubit reduced H₂ Hamiltonian in C08's worked example and the
  bond-length-0.735 Å coefficients, and as the **reference result** the test
  `test_vqe.py::test_exact_ground_energy_by_diagonalisation` reproduces.

### S51 — McClean, Boixo, Smelyanskiy, Babbush, Neven 2018 (barren plateaus)

- "Barren plateaus in quantum neural network training landscapes",
  *Nat. Commun.* **9**, 4812.
  doi:[10.1038/s41467-018-07090-4](https://doi.org/10.1038/s41467-018-07090-4);
  arXiv:[1803.11173](https://arxiv.org/abs/1803.11173)
- Used for: the $\Theta(2^{-n})$ gradient variance (C08).

### S52 — Cerezo et al. 2021 (variational algorithms review)

- "Variational Quantum Algorithms", *Nat. Rev. Phys.* **3**, 625–644.
  doi:[10.1038/s42254-021-00348-9](https://doi.org/10.1038/s42254-021-00348-9);
  arXiv:[2012.09265](https://arxiv.org/abs/2012.09265)
- Used for: the parameter-shift rule in the form used in C08, the optimiser
  survey, and the cost-function-dependent barren-plateau results.

### S53 — Raz & Tal 2018/2022

- "Oracle separation of BQP and PH", STOC 2019 / *J. ACM* **69**(4).
  doi:[10.1145/3313276.3316315](https://doi.org/10.1145/3313276.3316315)
- Used for: the oracle against BQP ⊆ PH (B06).

### S54 — Adleman, DeMarrais, Huang 1997

- "Quantum computability", *SIAM J. Comput.* **26**(5), 1524–1540.
  doi:[10.1137/S0097539795293639](https://doi.org/10.1137/S0097539795293639)
- Used for: **BQP ⊆ PP** (B06).

### S55 — Kitaev, Shen, Vyalyi 2002 and Kempe, Kitaev, Regev 2006 (QMA)

- A. Yu. Kitaev, A. H. Shen, M. N. Vyalyi, *Classical and Quantum Computation*,
  AMS Graduate Studies in Mathematics 47, 2002 — QMA and the QMA-completeness of
  5-LOCAL HAMILTONIAN. doi:[10.1090/gsm/047](https://doi.org/10.1090/gsm/047)
- J. Kempe, A. Kitaev, O. Regev, "The complexity of the local Hamiltonian
  problem", *SIAM J. Comput.* **35**(5), 1070–1097;
  arXiv:[quant-ph/0406180](https://arxiv.org/abs/quant-ph/0406180) — 2-LOCAL
  HAMILTONIAN is QMA-complete.
- Used for: the QMA section of B06.

### S56 — The classical complexity classics

Cited in B01–B05. Grouped because each supports one named theorem.

| theorem | source |
|---|---|
| Cook–Levin | S. A. Cook, STOC 1971, doi:[10.1145/800157.805047](https://doi.org/10.1145/800157.805047); L. Levin, *Probl. Peredachi Inf.* 9(3), 1973 |
| 21 NP-complete problems | R. M. Karp, *Complexity of Computer Computations*, 1972, doi:[10.1007/978-1-4684-2001-2_9](https://doi.org/10.1007/978-1-4684-2001-2_9) |
| NSPACE(s) ⊆ SPACE(s²) | W. J. Savitch, *JCSS* 4(2), 1970, doi:[10.1016/S0022-0000(70)80006-X](https://doi.org/10.1016/S0022-0000\(70\)80006-X) |
| NL = coNL | N. Immerman, *SIAM J. Comput.* 17(5), 1988, doi:[10.1137/0217058](https://doi.org/10.1137/0217058); R. Szelepcsényi, *Acta Inf.* 26, 1987, doi:[10.1007/BF00299636](https://doi.org/10.1007/BF00299636) |
| NP-intermediate problems exist if P ≠ NP | R. E. Ladner, *JACM* 22(1), 1975, doi:[10.1145/321864.321877](https://doi.org/10.1145/321864.321877) |
| BPP ⊆ P/poly | L. Adleman, FOCS 1978, doi:[10.1109/SFCS.1978.37](https://doi.org/10.1109/SFCS.1978.37) |
| BPP ⊆ Σ₂ᵖ ∩ Π₂ᵖ | C. Lautemann, *IPL* 17(4), 1983, doi:[10.1016/0020-0190(83)90044-3](https://doi.org/10.1016/0020-0190\(83\)90044-3); M. Sipser, STOC 1983 |
| NP ⊆ P/poly ⇒ PH = Σ₂ᵖ | R. M. Karp, R. J. Lipton, STOC 1980, doi:[10.1145/800141.804678](https://doi.org/10.1145/800141.804678) |
| PH ⊆ P^#P | S. Toda, *SIAM J. Comput.* 20(5), 1991, doi:[10.1137/0220053](https://doi.org/10.1137/0220053) |
| BPP = P under a circuit-lower-bound assumption | R. Impagliazzo, A. Wigderson, STOC 1997, doi:[10.1145/258533.258590](https://doi.org/10.1145/258533.258590) |
| the ≈3n circuit lower bound | M. G. Find, A. Golovnev, E. A. Hirsch, A. S. Kulikov, FOCS 2016, doi:[10.1109/FOCS.2016.19](https://doi.org/10.1109/FOCS.2016.19) |
| Barrington's theorem (NC¹ = width-5 branching programs) | D. A. Barrington, *JCSS* 38(1), 1989, doi:[10.1016/0022-0000(89)90037-8](https://doi.org/10.1016/0022-0000\(89\)90037-8) |

### S57 — Query-complexity methods and Solovay–Kitaev

| result | source |
|---|---|
| polynomial method, $D(f) = O(Q(f)^6)$ for total $f$ | R. Beals, H. Buhrman, R. Cleve, M. Mosca, R. de Wolf, *JACM* 48(4), 2001, doi:[10.1145/502090.502097](https://doi.org/10.1145/502090.502097) |
| adversary method | A. Ambainis, *JCSS* 64(4), 2002, doi:[10.1006/jcss.2002.1826](https://doi.org/10.1006/jcss.2002.1826) |
| $D(f) = O(Q(f)^4)$, tight quartic separation | A. Ambainis, K. Balodis, A. Belovs, T. Lee, M. Santha, J. Smotrovs, STOC 2016, doi:[10.1145/2897518.2897644](https://doi.org/10.1145/2897518.2897644) |
| Solovay–Kitaev with $c\approx3.97$ | C. M. Dawson, M. A. Nielsen, *QIC* 6(1), 2006, arXiv:[quant-ph/0505030](https://arxiv.org/abs/quant-ph/0505030) |
| Goemans–Williamson 0.878 for MaxCut | M. X. Goemans, D. P. Williamson, *JACM* 42(6), 1995, doi:[10.1145/227683.227684](https://doi.org/10.1145/227683.227684) |

### S58 — Shor resource estimates

- C. Gidney, M. Ekerå, "How to factor 2048 bit RSA integers in 8 hours using
  20 million noisy qubits", *Quantum* **5**, 433 (2021);
  arXiv:[1905.09749](https://arxiv.org/abs/1905.09749)
- C. Gidney, "How to factor 2048 bit RSA integers with less than a million noisy
  qubits", arXiv:[2505.15917](https://arxiv.org/abs/2505.15917) (2025)
- Used for: the resource numbers in C07. Both titles verified verbatim on arXiv
  on 2026-09-22.

## Substitute sources — free practice material from elsewhere

**Read this paragraph before using anything in this section.** 192.043 publishes
no exercise sheet, no script and no past paper, in any year [S24]. Egly's own
192.036 sheets [S16–S18] are the closest thing that exists, and they only cover
the **quantum** third. The sources below are **other institutions' teaching material**, used to
close the practice gap for the **algorithmics and complexity** thirds. They are
not this course's material and must never be presented as it. Each carries its
institution, course code, year, licence and retrieval date; each has a folder
under `../src/exercises/` whose README repeats them; and the practice note
[`../notes/01-practice-set-substitute-sources.md`](../notes/01-practice-set-substitute-sources.md)
tags every problem with the source it came from or marks it as ours.

The selection rule was: **the thinnest blocks first**. Block C had five exercise
folders; blocks A and B had none. So one source was chosen for A, one for the
part of B that a solved undergraduate paper reaches, and one for the part of B
that it does not.

### S59 — MIT OCW 18.404J *Theory of Computation*, Fall 2020 (Sipser) ★

- MIT OpenCourseWare, 18.404J / 18.4041J / 6.840J, Prof. Michael Sipser,
  Fall 2020. Undergraduate and graduate.
  <https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/>
- Used: the syllabus, the "Sample Final Exam" and the **"Sample Final Exam
  Solutions"** (the Fall 2006 paper),
  <https://ocw.mit.edu/courses/18-404j-theory-of-computation-fall-2020/pages/exams/>;
  sample midterms of Fall 2001 and Fall 2006 exist but are on the automata and
  computability half and are out of scope here.
- Retrieved: 2026-09-22. Access: public, no login.
  **Licence: CC BY-NC-SA 4.0** (<https://ocw.mit.edu/terms/>). Not vendored —
  the folder cites it and restates every question in our own words. Because that
  folder adapts CC BY-NC-SA material, **the folder itself is CC BY-NC-SA 4.0**,
  and says so.
- **Why it is comparable.** Seven of its twelve weeks are complexity theory, and
  its own class list — "P, NP, L, NL, PSPACE, BPP and IP, complete problems, the
  P versus NP conjecture, quantifiers and games, hierarchy theorems, provably
  hard problems, relativized computation and oracles, probabilistic computation"
  — is 192.043's complexity bullet list [S1] plus Pichler's headings [S7, S14]
  almost item for item. More important, its final's central question is *prove
  a given combinatorial problem NP-complete, both directions*, which is exactly
  the skill Pichler's own admission test and written test examine [S23].
- **Where it does not match.** Five of its twelve weeks are automata, regular
  and context-free languages, computability, the recursion theorem and
  interactive proofs — **none of which is on 192.043's, 192.219's or Pichler's
  list**. And it never reaches circuit complexity, P/poly, PP, the polynomial
  hierarchy as a named object, or the RAM model, all of which 192.043 has
  [S1, S4, S5, S7]. That gap is what S60 is for. Its exams are also open book;
  192.219's are not [S5].
- Worked in `../src/exercises/mit-18.404j-2020`.

### S60 — Arora & Barak, *Computational Complexity: A Modern Approach* (free draft) ★

- Sanjeev Arora, Boaz Barak, Princeton University. Authors' free internet draft,
  dated January 2007. <https://theory.cs.princeton.edu/complexity/book.pdf>
  (landing page <https://theory.cs.princeton.edu/complexity/>). Published
  edition: Cambridge University Press, 2009, ISBN 978-0-521-42426-4.
- Retrieved: 2026-09-22. Access: free download, no login.
  **Licence: none.** The draft's title page reads "Not to be reproduced or
  distributed without the authors' permission". So: **cite-only**, not vendored,
  no exercise text copied, and the exercises in its folder are **ours**, written
  for theorems the book states.
- **Why it is comparable.** It is the free book that covers the four complexity
  topics 192.043 examines and S59 never reaches: the **polynomial hierarchy**
  (ch. 5), **Boolean circuits and P/poly** (ch. 6), **randomised classes and
  Adleman** (ch. 7), **BQP** (ch. 10), plus **PP and #P** (ch. 17). Chapters 1–4
  cover the same ground as Papadimitriou ch. 2, 7–9, 16 [S26], which is the book
  Pichler actually sets [S14], in the same order.
- **Where it does not match.** Most of Parts II and III — average-case
  complexity, derandomisation and pseudorandomness, PCP and hardness of
  approximation, proof complexity, communication complexity, natural proofs,
  expanders, interactive proofs, cryptography — is on no 192.043-adjacent
  syllabus. It also uses Turing machines throughout and never treats the **RAM
  model**, which 192.042 named and which merged into 192.043 in 2026W [S4].
  Chapter numbers above are the **published** edition's; the 2007 draft
  renumbers Parts II and III.
- Worked in `../src/exercises/princeton-arora-barak-2007`.

### S61 — MIT OCW 6.046J *Design and Analysis of Algorithms*, Spring 2015 ★

- MIT OpenCourseWare, 6.046J / 18.410J, Profs. Erik Demaine, Srini Devadas,
  Nancy Lynch, Spring 2015. Undergraduate.
  <https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/>
- Used: the lecture list, and the **"Final Exam" with "Solutions to Final Exam"**
  (23 May 2015),
  <https://ocw.mit.edu/courses/6-046j-design-and-analysis-of-algorithms-spring-2015/pages/exams/>.
  Ten problem sets, all with published solutions, and two quizzes with solutions
  are on the same site and are the obvious next thing to work.
- Retrieved: 2026-09-22. Access: public, no login.
  **Licence: CC BY-NC-SA 4.0** (<https://ocw.mit.edu/terms/>). Not vendored;
  questions restated in our own words; the folder is itself CC BY-NC-SA 4.0 and
  says so.
- **Why it is comparable.** Its lectures 10–17 — advanced dynamic programming,
  all-pairs shortest paths, minimum spanning trees, **max flow and min cut**,
  matching, **linear programming and simplex**, **P/NP/NP-completeness and
  reductions**, **approximation algorithms** — are Kleinberg & Tardos ch. 4–8 and
  11, the book 192.043 and 192.219 both set [S1, S5, S25], and they are the
  second half of 192.219's own bullet list [S5]. Its final is a 180-minute
  closed-form written paper, the same length and shape as 192.043's Exam 1 [S1].
- **Where it does not match.** Half of it: van Emde Boas trees, skip lists,
  hashing, range trees, amortised and competitive analysis, distributed
  algorithms, cryptography, cache-oblivious algorithms, fixed-parameter
  tractability. And it omits things 192.043 has — graph traversal, connectivity,
  bipartiteness, topological order, counting inversions, closest pair, interval
  partitioning. It allows three crib sheets; 192.219 is closed book [S5].
- Worked in `../src/exercises/mit-6.046j-2015`.

### Considered and deliberately not used

Recorded because the reasons are the useful part.

- **The Qiskit textbook.** Licence is clean — **Apache-2.0**, from
  <https://github.com/Qiskit/textbook> — but the repository was **archived on
  18 January 2024** and its own README says the content "has been superseded by
  IBM Quantum Learning" and "may contain errors". Worse for this course, it is
  written in **Qiskit's little-endian qubit order**, the exact reverse of Egly's
  [S16, S17, S20]. Borrowing its exercises would teach the wrong matrices, which
  is the trap [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) already
  documents. Not used.
- **Preskill, Ph219/CS219 (Caltech)** and **Aaronson's lecture notes** [S27].
  Both free, both with problem sets, both excellent — and both aimed at the
  block that already has five exercise folders. Preskill is also physics-first
  where this course is theoretical-computer-science-first, and neither states a
  qubit ordering that can be assumed to be Egly's. Left as reading, not
  converted into practice.
- **MIT OCW 18.404J's own problem sets.** They are lists of problem *numbers*
  from Sipser's textbook, which is commercial; the OCW page carries no problem
  text. Only the sample exams are usable, and those are what S59 uses.
- **de Wolf's lecture notes** [S31] already carry exercises with hints and are
  already the registered substitute for the missing script. Nothing was added
  on top of them.

## The 2026W TUWEL course (added 2026-10-09; cite-only)

### S62: 192.043 TUWEL course 83986, 2026W (login, cite-only)

- What was read on 2026-10-09: the course page and its section list; the
  "Organization slides" (5 pages, by Chen); the page "Lecture and exercise
  schedule" (last modified 01.10.2026); the algorithmics decks by Chen, "Warm
  Up" (chapter 1, 35 pages), chapter 2 (graphs, 33 pages) and chapter 3
  (greedy, 40 pages), plus three annotated copies of chapters 1 and 2; the
  exercise section (group registration and six hand-in activities); the
  announcement forum (empty).
- Where: TUWEL, course 83986, linked from the TISS API record [S1] since
  2026-10-09. Login only, so no URL beyond the course id is given.
- **Licence: all rights reserved. Not vendored, cite-only.** Nothing from the
  slides or pages is copied into this wiki beyond names of topics; the notes
  summarise in their own words.
- Used for: the grading scheme, exercise format and exam lengths in
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md), the 2026W schedule
  and block order in [`lecture-notes-map.md`](lecture-notes-map.md), the
  TISS-against-TUWEL comparison in [`../docs/tiss.md`](../docs/tiss.md), and the
  2026W lecture sections and cards of notes A01-A03. Where it disagrees with an
  inference elsewhere in this folder, S62 wins.
- Caveat: the six hand-in activities still carry 2025 dates (October 2025 to
  January 2026). They show the sheet structure but no 2026 deadline.

---

## What could not be sourced

- **Which lecturer teaches which block is not stated anywhere public.** The
  attribution in `lecture-notes-map.md` is an inference from S5 (shared slots
  with Chen and Pichler), S12/S15/S20 (Egly owns the quantum material) and
  S7/S14 (Pichler owns the complexity material). **Fermüller's role is
  genuinely unknown** [S13]. Update 2026-10-09: the algorithmics decks are
  Chen's [S62]; the other blocks have no material yet.
- ~~**The grading split of 192.043.**~~ Resolved 2026-10-09 by the
  organization slides [S62]: see [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
  TISS itself still says only "Exercises + written exam" [S1].
- **Any past paper of 192.043**, in any year [S24].
- ~~**The lecture-by-lecture schedule.**~~ Resolved 2026-10-09: TUWEL has a
  schedule page with topic and room per slot [S62]; TISS's 48 single
  appointments still carry no topic [S1].
- **Free practice material for the RAM model.** 192.042's subject list names
  *random access machines* [S4] and 192.042 merged into 192.043 for 2026W. Every
  free complexity source found — S26, S31, S59, S60 — works with Turing machines
  and mentions the RAM only to say it is polynomially equivalent. No exercise,
  solved or otherwise, was found. Same for **PP** as distinct from BPP:
  definitions exist [S60] ch. 17, [S34], solved problems do not.
- **Any evidence that quantum error correction is examined in 192.043.** Only
  the German learning outcome mentions it [S1]; no sibling course teaches it
  [S20]. Free material is abundant [S30, S31] and deliberately not turned into a
  practice set. See
  [`../notes/01-practice-set-substitute-sources.md`](../notes/01-practice-set-substitute-sources.md).
