# Block structure, lecturers, and the map from sources to notes and code

192.043 is three courses in one folder. This file reconstructs which blocks
exist, who teaches them, when they run and how each is examined, from the
sources in [`SOURCES.md`](SOURCES.md). **Every attribution below is an
inference; the evidence for each is given, and the one that could not be made
is stated as such.**

## The 48 single appointments, grouped

Expanded from the nine date rows on the TISS page [S1]. Eight streams plus the
first meeting.

| # | stream | slots | dates |
|---|---|---|---|
| 0 | Thu, EI 11 HS, **first meeting** | 1 | 01.10 |
| 1 | Fri 10:00–13:00, **EI 10 Fritz Paschke** | 6 | 02.10, 09.10, 16.10, 23.10, 30.10, 06.11 |
| 2 | Mon 14:00–17:00, **EI 8 Pötzl** | 3 | 05.10, 12.10, 19.10 |
| 3 | Wed 15:00–18:00, **EI 5 Hochenegg** | 5 | 07.10, 14.10, 21.10, 28.10, 04.11 |
| 4 | Wed 15:00–19:00, **FAV HS 3 Zemanek** | 14 | 07.10 … 27.01, weekly except 23.12–06.01 |
| 5 | Mon 13:00–18:00, **FAV HS 3 Zemanek** | 10 | 12.10, 19.10, 09.11, 16.11, 23.11, 30.11, 07.12, 14.12, 11.01, 18.01 |
| 6 | Fri 10:00–13:00, **EI 5 Hochenegg** | 6 | 13.11, 20.11, 27.11, 04.12, 18.12, 08.01 |
| 7 | Wed 13:00–16:00, **Seminarraum FAV 01 A** | 3 | 02.12, 09.12, 16.12 |

Two structural facts follow immediately.

**(a) Ten of the 48 slots are double-booked, and in every case the EI or
seminar-room booking lies inside the Zemanek booking.** Wed 07.10–04.11:
EI 5 15:00–18:00 ⊂ Zemanek 15:00–19:00 (5×). Mon 12.10 and 19.10:
EI 8 14:00–17:00 ⊂ Zemanek 13:00–18:00 (2×). Wed 02.12–16.12: SR FAV 01 A
13:00–16:00 overlaps Zemanek 15:00–19:00 (3×). One cohort cannot be in two
rooms at once, so **streams 4 and 5 are a blanket semester-long hold on
Zemanek**, and the EI rooms are where the October–November teaching actually
happens.

**(b) Streams 0–3 are shared with 192.219 verbatim** [S5] — same first meeting
in EI 11, same Fri EI 10 series, same Mon EI 8 series, same Wed EI 5 series,
same 09.10 extra Friday, and the same 11.12 exam slot. 192.219 is
*Supplementary Course Algorithms and Data Structures*, taught by **Chen and
Pichler** with five tutors, and its own page says "all lectures and exercises
will be given from October to No[v]ember: 3 sessions per week, 3 hours per
session. There will be five exercise sessions."

Note also that **there is no Friday lecture on 11.12** — stream 6 skips it.
That is Exam 1 day (09:00–12:00).

## The three blocks

| block | when | rooms | lecturer(s) | examined by | evidence |
|---|---|---|---|---|---|
| **A — Algorithmics** (+ the complexity basics 192.042 used to carry) | Thu 01.10 – Fri 06.11, 9 h/week | EI 11, EI 10, EI 8, EI 5 | **Chen**, **Pichler**, with tutors | **Exam 1**, Fri 11.12.2026, 09:00–12:00, HS 8 Heinz Parkus | streams 0–3 identical to 192.219 [S5]; Chen's unit is Algorithms and Complexity [S11]; the 192.219 exam is the same slot |
| **B — Complexity theory** | mid-Nov – early Dec | FAV Zemanek (Mon/Wed), EI 5 (Fri) | **Pichler** | **Exam 1** (its title is "Algorithmics **& Complexity Theory**") | Pichler is the sole lecturer of 192.165 Complexity Theory 2026W [S7] and of its predecessor 181.142 [S8, S14, S23]; his topic list matches the B-series one-for-one |
| **C — Quantum computing** | Dec – 27.01 | FAV Zemanek, SR FAV 01 A | **Egly** | **Exam 2**, Thu 21.01.2027, 14:00–17:00, EI 9 Hlawka | Egly is the lecturer of 192.036 [S6, S15] and 192.070 [S20]; those courses' sheets, protocols and student summary match the C-series exactly |

**Fermüller's role is not established.** He is on the lecturer list of every
offering since 2024W [S1–S3] and on 192.042 [S4], his research unit is Theory
and Logic (E192-05), and his own courses are *Logic and Computability* and
*Theoretical Computer Science* [S13]. The block that fits is the
computability / formal-models-of-computation material that 192.042 named
explicitly — Turing machines, random access machines, problem reductions, the
(extended) Church–Turing thesis [S4] — which in 2026W has to live somewhere
inside 192.043 and which straddles blocks A and B. **That is an inference, not
a sourced fact.** His 192.017 does *not* share slots with 192.043 [S9].

Two lecturers were dropped after 2024W [S3]: **Tompits**, who in 192.036 teaches
the mathematical and quantum-mechanical foundations ("Formale Grundlagen" —
complex vector spaces, operators, the postulates) [S15], and **De Maio**, whose
own course 194.027 is where the variational/hybrid material lives [S10, S22].
Their former material is still on the 2026W subject list ("Basic notions
(including mathematical and quantum-mechanical background)", "Variational
solvers…") [S1], so somebody teaches it — presumably Egly.

## Why the exams split where they do

- **Exam 1 (11.12): "QIST Algorithmics & Complexity Theory"** — everything in
  the A-series plus B01–B05. It is the same slot as 192.219's main exam [S5],
  whose modalities are "Exercises with presentation and **closed book** written
  exam". Registration 01.11 09:00 – 07.12 09:00.
- **Exam 2 (21.01): "QIST Quantum Algorithms and Complexity"** — the C-series
  plus **B06** (the note that defines BQP, QMA and quantum query complexity; the
  title says "and Complexity" and the TISS subject list files BQP/QMA/query
  complexity under *Complexity theory*, so B06 sits on both sides of the split;
  it is written for Exam 2). Registration 01.12 09:00 – 19.01 09:00.
- **Retake (09.03.2027)** — split into two group-registered halves,
  "Algorithmics and Complexity" and "Quantum algorithms and complexity"; see
  `../docs/tiss.md` §Discrepancies for the date/time contradiction.

## Source → note → code

### Block A — Algorithmics (Kleinberg & Tardos order)

| K&T ch. | topic, as the two syllabi name it [S1, S5] | note | code |
|---|---|---|---|
| 2 | O-notation, asymptotic order of growth; running-time analysis | [A01](../notes/A01-asymptotics-and-recurrences.md) | `src/py/algorithmics/divide_conquer.py` (Master-theorem checks) |
| 3 | graphs: **data structures for graphs** [S5], connectivity, traversal, bipartiteness, topological ordering | [A02](../notes/A02-graphs.md) | `src/py/algorithmics/graphs.py`, `src/cpp/dijkstra.cpp` |
| 4 | greedy: interval scheduling, **interval partitioning** [S5], **priority queues** [S5], MST | [A03](../notes/A03-greedy.md) | `src/py/algorithmics/greedy.py`, `src/cpp/kruskal.cpp` |
| 5 | divide and conquer: **merge sort** [S5], recurrences, counting inversions, closest pair | [A04](../notes/A04-divide-and-conquer.md) | `src/py/algorithmics/divide_conquer.py` |
| 6 | DP: weighted interval scheduling, knapsack, shortest path | [A05](../notes/A05-dynamic-programming.md) | `src/py/algorithmics/dp.py`, `src/cpp/knapsack.cpp` |
| 7 | network flow: Ford–Fulkerson, **the MaxFlow–MinCut theorem** [S5], applications | [A06](../notes/A06-network-flow.md) | `src/py/algorithmics/flow.py`, `src/cpp/edmonds_karp.cpp` |
| 11 | approximation (new in 2025W [S2, S3]) | [A07](../notes/A07-approximation.md) | `src/py/algorithmics/approx.py` |
| 11.6 | LP vs ILP | [A08](../notes/A08-lp-vs-ilp.md) | `src/py/algorithmics/lp_ilp.py` |

### Block B — Complexity theory (Pichler's order [S14], Papadimitriou [S26])

| Pichler's heading [S14] / TISS bullet [S1] | note | code |
|---|---|---|
| Turing machines, complexity classes; **random access machines** [S4]; problem reductions; Cook–Levin; more NP-completeness | [B01](../notes/B01-models-and-np-completeness.md) | `src/py/complexity/sat.py` |
| The class PSPACE; EXPTIME; **the polynomial hierarchy** [S5, S7, S14] | [B02](../notes/B02-pspace-and-exptime.md) | — |
| Logarithmic space: L, NL | [B03](../notes/B03-inside-p-l-and-nl.md) | `src/py/complexity/reachability.py` |
| "inside the class P … parallelizable problems" [S7] = circuit classes NC/AC, P/poly | [B04](../notes/B04-circuit-complexity.md) | — |
| Probabilistic classes BPP, PP | [B05](../notes/B05-probabilistic-classes.md) | `src/py/complexity/bpp_amplify.py` |
| Uniform boolean and quantum circuits; extended Church–Turing thesis; BQP; QMA; quantum query complexity | [B06](../notes/B06-quantum-complexity.md) | `src/py/complexity/query_complexity.py` |

Pichler's own list also contains **fixed-parameter tractability** and
**applications (database theory, abduction)** [S14]; neither is on the 192.043
subject list [S1] and neither is in the notes. If block B follows 192.165 rather
than the TISS bullet list, FPT is the first thing that would appear.

### Block C — Quantum computing (the order of Egly's own lecture, from the WS2023 summary [S20])

| lecture section [S20] | note | code | sheet exercises [S16, S17] |
|---|---|---|---|
| 0 Introduction: qubit, entanglement, **noise — gate infidelity and decoherence** | [C01](../notes/C01-qubits-gates-and-measurement.md) | `src/py/quantum/sim.py` | — |
| 1 Principles of QM I: classes of operators, bra–ket | C01 | `sim.py` | Sheet 1 Ex. 2–8 |
| 2 Principles of QM II & gates: four postulates, registers, NOT/H/phase/T/rotation/CNOT/SWAP, universality | C01 | `sim.py` | Sheet 1 Ex. 9–10; Sheet 3 Ex. 3–5 |
| 3 Preparatory concepts: multi-controlled gates and **Gray code**, reversibility and garbage, **phase kickback** | [C02](../notes/C02-programming-techniques-and-reversible-computation.md) | `sim.py` | Sheet 2 Ex. 2; PE 1, PE 2 |
| 4 Algorithms I: **superdense coding**, teleportation, Deutsch, Deutsch–Jozsa, Bernstein–Vazirani | [C03](../notes/C03-deutsch-jozsa-bernstein-vazirani-teleportation.md) | `deutsch_jozsa.py`, `bernstein_vazirani.py`, `teleport.py` | Sheet 2 Ex. 1, 4, 5 |
| 5 Algorithms II: Grover, Simon | [C04](../notes/C04-grover.md), [C05](../notes/C05-simon.md) | `grover.py`, `simon.py` | Sheet 3 Ex. 1–2; Sheet 4 Ex. 1; PE 3 |
| 6 Algorithms III: QFT, QPE | [C06](../notes/C06-qft-phase-estimation-order-finding.md) | `qft.py`, `phase_estimation.py` | Sheet 4 Ex. 2–4 |
| 7 Algorithms IV: Shor | [C07](../notes/C07-shor.md) | `shor.py`, `order_finding.py` | — |
| (not in 192.036/192.070; on the 192.043 list [S1], material in 194.027 [S22]) | [C08](../notes/C08-variational-and-hybrid-algorithms.md) | `vqe.py`, `qaoa.py` | HQCS assignment 2 |

## Conventions the course uses, and where they are fixed

These are the silent killers. All of them are stated in [C01](../notes/C01-qubits-gates-and-measurement.md).

| convention | the course's version | source |
|---|---|---|
| qubit order in a ket | leftmost symbol = first tensor factor = most significant; Egly writes the three-qubit register as $t\otimes i_1\otimes i_0 = \|000\rangle$ and the BV secret as $\|z_{n-1}\cdots z_0\rangle$ | [S16] sheet 2 Ex. 1, [S20] §4.5 |
| Qiskit's order | the reverse. Egly's PE 2 prints **both** matrices for the same gate $M_3$ and says "the following matrix is generated by Qiskit (with Qiskit's bit order)". The two differ by conjugation with the bit-reversal permutation | [S17] PE 2 |
| the rotation gate $R_x(\theta)$ | $\bigl(\begin{smallmatrix}\cos\frac\theta2&\sin\frac\theta2\\-\sin\frac\theta2&\cos\frac\theta2\end{smallmatrix}\bigr)$ — **real**, and *not* $e^{-i\theta X/2}$. The sheet says so: "The rotation gate here is different from the RX gate in Qiskit." It equals the standard $R_y(-\theta)$ | [S16] sheet 3 Ex. 3 |
| Grover diffusion | $D = H^{\otimes n}(2\|0^n\rangle\langle 0^n\|-I)H^{\otimes n}$, with $-D = H^{\otimes n}X^{\otimes n}C^{n-1}Z\,X^{\otimes n}H^{\otimes n}$ | [S16] sheet 3 Ex. 1, [S20] §5.1 |
| Grover iteration count | $\lfloor\frac\pi4\sqrt{2^n}\rfloor$, and $\lfloor\frac\pi4\sqrt{2^n/k}\rfloor$ for $k$ solutions | [S20] §5.1 |
| QFT output order | reversed; "we can apply SWAP gates at the end to reorder … a simpler approach is to relabel the qubits" | [S20] §6.1 |
| QPE error | $0\le\|\delta\|\le 2^{-(t+1)}$ | [S20] §6.2 |
| Shor register size | $q = 2^\ell$ with $N^2\le q\le 2N^2$ | [S20] §7.1.2, [S40] |
