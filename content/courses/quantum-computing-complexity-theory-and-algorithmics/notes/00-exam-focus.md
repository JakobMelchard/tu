# 00 Exam focus — what is actually asked

Built on 2026-09-22 from the TISS page [S1] and from the **sibling courses that
share this course's lecturers and, in October and November, its lecture slots**.
Sources in [`../refs/SOURCES.md`](../refs/SOURCES.md); the block structure and
its evidence in [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Read the warning first.** 192.043 has **no VoWi page, no past paper and no
public slide deck of its own** [S24], and 2026W is the **first run in its present
form**: 6.0 h / 10.0 ECTS, merging the old 7.0 ECTS 192.043 with the 3.0 ECTS
preparation course 192.042, which has no 2026W offering [S1–S4]. In 2024W the
course examined with *two* written papers in February and March [S3]; in 2026W it
examines with two mid-term-style papers in December and January [S1]. So there is
no previous instance of *this* examination to learn from. Everything below is
either quoted from TISS or inferred from a sibling course, and each item says
which.

## The two exams — this part is sourced

| | Exam 1 | Exam 2 | Retake |
|---|---|---|---|
| TISS title | "Exam 1: **QIST Algorithmics & Complexity Theory**" | "Exam 2: **QIST Quantum Algorithms and Complexity**" | "Exam retake, March 9, 14:00-18:00" |
| date | **Fri 11.12.2026, 09:00–12:00** | **Thu 21.01.2027, 14:00–17:00** | Tue 09.03.2027, room booked 13:00–18:00 |
| room | HS 8 Heinz Parkus – CEE | EI 9 Hlawka HS – ETIT | HS 7 Schütte-Lihotzky – ARCH |
| registration | 01.11.2026 09:00 – 07.12.2026 09:00 | 01.12.2026 09:00 – 19.01.2027 09:00 | 01.12.2026 09:00 – 08.03.2027 09:00 |
| written? | yes (TISS "Mode of examination: written") | yes | yes |
| notes | **A01–A08 + B01–B05** | **B06 + C01–C08** | two group-registered halves, registration 25.01.2027 09:00 – 04.03.2027 09:00 |

Three hours each. Course-level mode of examination is **immanent**, and the
modalities are exactly six words: "Exercises + written exam" [S1]. **The
weighting of exercises against exams is not published.** Do not assume it; ask at
the first meeting.

**The retake is contradictory in TISS.** See
[`../docs/tiss.md`](../docs/tiss.md) §Discrepancies: the row says 09.03.2027
13:00–18:00, the row's own title says "March 9, 14:00–18:00", and the two
group-registration entries say "March 6, 13:00–15:00" and "March 6, 15:00–17:00".
The co-taught 192.219 has its retake on **Tue 09.03.2027 14:00–17:00** [S5],
which points at 9 March with a 14:00 start.

## Where the exercises come from

TISS says nothing beyond "Exercises". The co-taught 192.219 does: "all lectures
and exercises will be given from October to No[v]ember: **3 sessions per week, 3
hours per session. There will be five exercise sessions**", assessed by
"Exercises **with presentation** and **closed book** written exam", with six
exercise groups [S5]. That is the algorithmics block. For the quantum block the
model is Egly's own 192.036: exercise sheets discussed at the board, **three
Qiskit programming assignments graded in a 20-minute submission interview**, and
in SS 2026 a written **exercise test** replacing the marked sheets [S15].

## Exam 1 — Algorithmics and Complexity Theory

### What is certainly in scope

The union of two syllabi, because they are taught together [S1, S5]:

- **Algorithmics.** O-notation and asymptotic growth; graphs, *their data
  structures*, connectivity, traversal, bipartiteness, topological ordering;
  greedy — interval scheduling, *interval partitioning*, *priority queues*,
  minimum spanning tree; divide and conquer — *merge sort*, recurrences,
  counting inversions, closest pair; dynamic programming — weighted interval
  scheduling, knapsack, shortest path; network flow — Ford–Fulkerson, the
  **MaxFlow–MinCut theorem**, applications; approximation; LP vs ILP.
  (*Italics* = named only on 192.219's page.)
- **Complexity.** Turing machines and *random access machines* [S4]; problem
  reductions; P, NP, PSPACE, EXPTIME; L, NL; circuit classes; BPP, PP; **and the
  polynomial hierarchy**, which is named by 192.219 [S5] and by Pichler's own
  192.165 [S7] but *not* by 192.043's own bullet list [S1].

The textbooks are Kleinberg & Tardos and Papadimitriou [S1, S5, S14, S25, S26];
the A-series is a chapter-for-chapter walk through the first, the B-series
through the second.

### How Pichler examines complexity theory

From his own course, 181.142 / 192.165 [S7, S23]:

- An **admission test** whose task is "prove the correctness of an NP-hardness
  reduction" **with the reduction already given** — in WS 2023/24 Vertex Cover ↔
  Dominating Set.
- A **written test** whose task is "prove the correctness of a $\Pi_2^p$
  reduction", again with the reduction given.
- An optional oral that can move the grade by $\pm1$.

The skill being tested is therefore **not** inventing reductions; it is writing
the two directions of a correctness proof cleanly. Students name the prerequisite
chain as Theoretische Informatik und Logik → Formale Methoden (NP, reductions) →
Algorithmen auf Graphen [S23]. *(Inference: 192.043's Exam 1 is a different paper
with a different weight, but the same examiner and the same taste.)*

### Questions worth being able to answer cold

These are ours, modelled on the two syllabi and on Pichler's stated tasks; **no
public 192.043 paper exists to model them on** [S24]. Each note's own
"Exam-style questions" section has more.

1. Given a reduction $f$ from VERTEX COVER to DOMINATING SET, prove both
   directions of $x\in A \iff f(x)\in B$ and that $f$ is polynomial-time. (The
   shape of Pichler's admission test [S23].)
2. State and prove the max-flow/min-cut theorem; then use it on a bipartite
   matching instance (A06).
3. Prove Savitch's theorem and derive PSPACE = NPSPACE (B02).
4. Show $\mathrm{NL}\subseteq\mathrm{AC}^1$ (B04) and locate NC in
   $\mathrm L\subseteq\mathrm{NL}\subseteq\mathrm{NC}^2\subseteq\mathrm P$.
5. Define $\Sigma_k^p$ and $\Pi_k^p$, show $\mathrm{PH}\subseteq\mathrm{PSPACE}$,
   and say what $\mathrm{PH} = \mathrm{PSPACE}$ would imply (B02).
6. Prove $\mathrm{BPP}\subseteq\mathrm{P/poly}$ (B05).
7. Solve a knapsack or weighted-interval instance by dynamic programming and
   read off the optimum from the table (A05).
8. Give a $2$-approximation for VERTEX COVER and show the bound is tight (A07).

## Exam 2 — Quantum Algorithms and Complexity

### The lecture order — this is the most useful thing on the page

From the 21-page student summary of Egly & Tompits' 192.070 [S20], which is the
closest thing to a syllabus that exists for the quantum block:

| # | lecture section | our note |
|---|---|---|
| 0 | qubit, entanglement, **noise: gate infidelity and decoherence** | C01 |
| 1 | principles of QM I: classes of operators, bra–ket | C01 |
| 2 | principles of QM II and gates: the four postulates, registers, NOT/H/phase/$T$/rotation/CNOT/SWAP, universality | C01 |
| 3 | preparatory concepts: multi-controlled gates and **Gray code**, reversibility and garbage, **phase kickback** | C02 |
| 4 | algorithms I: **superdense coding**, teleportation, Deutsch, Deutsch–Jozsa, Bernstein–Vazirani | C03 |
| 5 | algorithms II: Grover, Simon | C04, C05 |
| 6 | algorithms III: QFT, quantum phase estimation | C06 |
| 7 | algorithms IV: Shor | C07 |

Two things follow. **Superdense coding comes before teleportation** and is on the
list even though 192.043's TISS bullet does not name it [S1]. And **variational
algorithms are not in the sibling course at all** — they are on 192.043's list
[S1] and their treatment lives in De Maio's 194.027 [S10, S22], which is why C08
is sourced entirely differently from C01–C07.

### Topics of Egly's written exercise test, SS 2026 [S18]

Three questions, on these topics: adjoints of composed operators from the
definition of the adjoint; counting the models of a propositional formula and
building a circuit for it with uncomputation; preparing a GHZ-type state with a
gate array and showing it correct. Two of the three come from 192.036's exercise
sheets, so **Egly reuses his sheets**; they are graded work of a running course
and are not solved in this wiki.

### Real questions — Egly & Tompits' oral, 2021 and 2026 [S19, S21]

Three candidates in 2021, each with one mathematics question and one algorithm
question:

- linear operators, their types, the eigenvalues of a self-adjoint operator
  **+ "explain Grover: what it does, what diffusion is, how often you have to
  repeat it"**;
- the postulates of quantum mechanics, 2 and 3 in detail **+ "explain Shor: what
  is computed, how, and why should $q$ be a large number"**;
- what a qubit, a register and an algorithm are, which gates exist, explain the
  Hadamard **+ "explain Deutsch–Jozsa: what it does, what is measured"**.

The 2026 protocol records Tompits walking the definitional chain
qubit → unit vector in a two-dimensional Hilbert space → $\mathbb{C}^2$ → several
qubits → tensor product → *why* the tensor product → postulate 4 → the remaining
postulates → the Schrödinger equation → its solution → "what kind of equation is
that and what does it mean?" → linear, hence the superposition principle; and
Egly asking for **amplitude amplification** as "a generalisation of Grover".

**And the closing remark of the 2021 protocol, which is the single most
load-bearing sentence here:** *"Allgemein wurden bei den Algorithmen keine
Formeln oder Berechnungen gefragt. Man musste nur verstehen worum es geht und wie
es ungefähr abläuft."* The 2026 protocol says the same of amplitude
amplification: the candidate drew the two bases on the unit circle, described the
operators and their intuitive effect, and **was not asked for the iteration
count**.

*(Caveat: those are **orals** of a **different course**. 192.043's Exam 2 is
written [S1]. The topics transfer; the format does not.)*

### The conventions that silently change answers

All of these are the course's own. Full table in [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

- **Qubit order.** Leftmost symbol of the ket = first tensor factor = most
  significant bit. Egly writes $t\otimes i_1\otimes i_0 = |000\rangle$ [S16] and
  $|z_{n-1}\cdots z_0\rangle$ [S20]. **Qiskit is the reverse**, and Programming
  Exercise 2 prints the same gate in both orders to make the point [S17]. State
  your convention in every answer that contains a matrix.
- **The rotation gate.** The course uses the *real*
  $R_x(\theta) = \bigl(\begin{smallmatrix}\cos\frac\theta2&\sin\frac\theta2\\-\sin\frac\theta2&\cos\frac\theta2\end{smallmatrix}\bigr)$,
  with the explicit remark that it is **not** Qiskit's RX [S16]. It is the
  standard $R_y(-\theta)$.
- **Diffusion.** The gate-level circuit
  $H^{\otimes n}X^{\otimes n}C^{n-1}Z\,X^{\otimes n}H^{\otimes n}$ equals
  **$-D$**, not $D$ [S16].
- **Grover count.** $\lfloor\frac\pi4\sqrt{2^n}\rfloor$ for one solution,
  $\lfloor\frac\pi4\sqrt{2^n/k}\rfloor$ for $k$ [S20].
- **QFT output is bit-reversed**; either SWAP or relabel [S20].
- **Shor register size.** $q = 2^\ell$ with $N^2\le q\le 2N^2$ [S20, S40].

### What the German learning outcome adds and the English one does not

TISS's German `objective` field says students should be able to "den Begriff und
die Konsequenzen der **Dekohärenz** erläutern und **elementare
Fehlerkorrekturstrategien** diskutieren und evaluieren". The English objective
drops it and neither appears in the English subject list [S1]. Decoherence is in
the sibling course's opening lecture [S20]; **error correction is in neither
sibling course**. C01 carries a short section on both and says exactly this.
*(unsourced: no public material shows error correction being taught in 192.043.)*

### Questions worth being able to answer cold

Marked **[real]** where a protocol or sheet records the question, **[ours]**
otherwise.

1. **[real, S21]** Explain Grover: what it does, what the diffusion operator is,
   how many iterations are needed (C04).
2. **[real, S19]** Describe amplitude amplification and its relation to Grover
   (C04).
3. **[real, S21]** Explain Shor: what is computed, how, and why $q$ must be large
   (C07).
4. **[real, S21]** Explain Deutsch–Jozsa: what it does and what is measured (C03).
5. **[real, S21]** The postulates of quantum mechanics, 2 and 3 in detail (C01).
6. **[real, S18]** Show $(TS)^* = S^*T^*$ from the defining property of the
   adjoint (C01).
7. **[real, S18/S16]** Count the models of a given formula without enumerating,
   and build an uncomputed oracle circuit for it (C02).
8. **[real, S18/S16]** Construct and *prove correct* a circuit preparing the GHZ
   state (C01).
9. **[real, S16]** Verify $-D = H^{\otimes n}X^{\otimes n}C^{n-1}Z X^{\otimes n}H^{\otimes n}$ (C04).
10. **[real, S16]** Build the QFT recursively from $K_n$ and $D_N$ and compare it
    with the Fourier matrix (C06).
11. **[real, S16]** Show $\langle\psi_s|\psi_t\rangle = \delta_{s,t}$ for the
    Bernstein–Vazirani states (C03).
12. **[ours]** Define BQP; prove $\mathrm{BPP}\subseteq\mathrm{BQP}$ and
    $\mathrm{BQP}\subseteq\mathrm{PSPACE}$ (B06).
13. **[ours]** Define QMA and state the QMA-completeness of $k$-LOCAL
    HAMILTONIAN (B06).
14. **[ours]** State the BBBV lower bound and explain why it means there is no
    black-box exponential speedup for NP (B06, C04).
15. **[ours]** Derive Simon's sampling distribution and the expected number of
    runs (C05).

## How to spend the time

- **Work Egly's four exercise sheets and three programming exercises.** They are
  the only real 192.043-adjacent tasks that exist, they recur in his own written
  test, and they fix the conventions. They are graded work of a running course,
  so this wiki does not solve them.
- For Exam 1, **practise writing reduction-correctness proofs**, both directions,
  with the reduction given. That is the tested skill [S23].
- **Do not over-index on the oral protocols.** They are orals of a different
  course; their "no formulas were asked" does not transfer to a three-hour
  written paper.
- Ask at the **first meeting** (Thu 1 Oct, EI 11 — see the time discrepancy in
  [`../docs/tiss.md`](../docs/tiss.md)) for the grading split, whether the
  algorithmics exercises are the 192.219 ones, and which lecturer takes which
  block. Those three answers would replace half of the inference on this page.
