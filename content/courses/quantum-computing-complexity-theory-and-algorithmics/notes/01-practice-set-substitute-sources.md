# 01 Practice set — built from substitute sources

*Licence: CC BY-NC-SA 4.0, adapted from MIT OpenCourseWare 18.404J (Fall 2020) and 6.046J (Spring 2015), <https://ocw.mit.edu/terms/>; not CC BY-SA, see [LICENSE.md](https://github.com/JakobMelchard/tu/blob/main/LICENSE.md).*

**None of this is 192.043 material.** 192.043 publishes no exercise sheet, no
script and no past paper, in any year [S24], and
[`00-exam-focus.md`](00-exam-focus.md) says so at length. This note closes the
practice gap with **other institutions' free material**, and every problem below
is tagged:

| tag | means |
|---|---|
| **[MIT-18.404]** | adapted from MIT OCW 18.404J's sample final, CC BY-NC-SA 4.0 [S59] |
| **[MIT-6.046]** | adapted from MIT OCW 6.046J's final, CC BY-NC-SA 4.0 [S61] |
| **[AB]** | ours, written for a theorem Arora & Barak state; their draft is cite-only [S60] |
| **[ours]** | ours, modelled on the TISS bullet, with no external source |

A tag is not a claim that the question will be asked here. It says where the
question came from. Sources, licences and the comparability argument for each
are in [`../refs/SOURCES.md`](../refs/SOURCES.md) §Substitute sources.

**Twenty problems.** Eighteen for Exam 1 (11 Dec, A01–A08 + B01–B05):
eight on algorithmics, ten on complexity. Two for Exam 2 (21 Jan, B06 +
C01–C08), which gets far fewer *because a lecturer of this course has his own
sheets for it*, and they beat any substitute.

---

## Exam 1, part A — algorithmics

**A1. Recurrences.** [MIT-6.046] Solve $T(n)=2T(n/2)+\Theta(n^2)$,
$T(n)=2T(n/2)+\Theta(n)$ and $T(n)=7T(n/2)+\Theta(n^2)$, and say which master
case each is. → A01, A04. *Answers: $\Theta(n^2)$ (case 3),
$\Theta(n\log n)$ (case 2), $\Theta(n^{\log_2 7})$ (case 1, Strassen).*
Code: `algorithmics/divide_conquer.py::master_theorem`.

**A2. Greedy with an exchange argument.** [MIT-6.046] Tasks cost $p_i$ hours;
helpers absorb up to $t_j$ hours of one task each; the remainder comes out of a
shared budget $T$. Prove that only the $k$ cheapest tasks and $k$ most capable
helpers matter, give the feasibility test, and find the largest feasible $k$.
→ A03. Worked: `../src/exercises/mit-6.046j-2015`
`p5_greedy_exchange`.

**A3. Minimum spanning trees, two traps.** [MIT-6.046] (a) Does negating every
weight and running Kruskal give a *maximum* spanning tree? (b) With all edge
weights distinct the MST is unique — is the **second**-best spanning tree
unique? → A03. *Answers: yes; and no — a five-edge counterexample is in the
same folder, `p1_true_false`.*

**A4. Floyd–Warshall, what the recursion means.** [MIT-6.046] In
$d^{(k)}_{uv}=\min\{d^{(k-1)}_{uv},\,d^{(k-1)}_{uk}+d^{(k-1)}_{kv}\}$, is
$d^{(k)}_{uv}$ the shortest $u\to v$ path with at most $k$ edges? → A05.
*Answer: no — intermediate vertices from $\{1,\dots,k\}$, any number of edges.
An instance separating the two readings is in the folder.*

**A5. One Edmonds–Karp iteration by hand.** [MIT-6.046] Given a flow network
carrying a flow of value 25, draw the residual graph, name the **shortest**
augmenting path, augment, and state the new value. → A06. *Answer: the path
$s\to3\to2\to5\to t$ uses a backward residual edge; bottleneck 1; new value
**26**. Running to completion gives max flow **27**, certified by the cut
$\{s,3,4,7\}$.* This is the one number in this note that another institution
published and that our code reproduces — see
`test_substitute_exercises.py::test_edmonds_karp_reproduces_mits_published_flow_value`.

**A6. MaxFlow–MinCut, stated and used.** [ours] State the theorem, prove
$|f|\le \mathrm{cap}(A,B)$ for every cut, and then use it to read a maximum
bipartite matching off a flow. → A06. Code: `algorithmics/flow.py`.
*This is the single most likely A-question: it is the only result on either
syllabus written in capitals [S1, S5].*

**A7. A 2-approximation, with its lower bound.** [MIT-6.046] $n$ jobs on $m$
identical machines, minimise the makespan. Give the greedy, prove the
$2$-approximation from $\mathrm{OPT}\ge\max(\frac1m\sum t_i,\max t_i)$, and give
a family on which the bound is tight. → A07. *Answer: $m(m-1)$ unit jobs plus
one job of length $m$ gives $2-\frac1m$; for $m=4$, 7 against 4.*

**A8. LP, ILP and the integrality gap.** [ours] Write VERTEX COVER as an ILP,
relax it, round at $x_v\ge\frac12$, and show the rounding is a
$2$-approximation. Exhibit a graph where the LP optimum is $n/2$ and the ILP
optimum is $n-1$. → A08, A07. *Answer: $K_n$ — the LP takes $x_v=\frac12$
everywhere.* Code: `algorithmics/lp_ilp.py::integrality_gap`.

---

## Exam 1, part B — complexity theory

**B1. Prove a given reduction correct.** [MIT-18.404] A board holds red and blue
stones, at most one per cell. A move deletes all stones of one colour from one
column. You win if no column ends up holding both colours and every row still
holds a stone. You are *given* the map from 3SAT — variable $\to$ column, clause
$\to$ row, positive literal $\to$ blue, negative $\to$ red. **Prove both
directions and that the map is polynomial.** → B01.
Worked: `../src/exercises/mit-18.404j-2020`
`q3_reduction_correctness`, checked on 112 791 formulas.

> **This is the highest-value problem in the note.** Pichler's own admission
> test and written test both consist of proving the correctness of a reduction
> he has already written down [S23]. Do this one, then do the 3-dimensional
> matching reduction in the 6.046 folder, then do the Karp chain in
> `complexity/sat.py` the same way.

**B2. The settled, the open and the false.** [MIT-18.404] Mark each: $\mathrm P
= \mathrm{NP}$; $\mathrm{NP}=\mathrm{coNP}$; $\mathrm L=\mathrm{NL}$;
$\mathrm{NL}=\mathrm{coNL}$; $\mathrm{PSPACE}=\mathrm{NPSPACE}$;
$\mathrm{PSPACE}=\mathrm{NL}$; $\mathrm P=\mathrm{EXPTIME}$;
$\mathrm{PSPACE}=\mathrm{EXPTIME}$; PSPACE closed under complement. → B01–B03.
*The trap is that they are not all open: $\mathrm{NL}=\mathrm{coNL}$ and
$\mathrm{PSPACE}=\mathrm{NPSPACE}$ are theorems, $\mathrm P\ne\mathrm{EXPTIME}$
and $\mathrm{PSPACE}\ne\mathrm{NL}$ follow from hierarchy theorems, and
$\mathrm{PSPACE}=\mathrm{EXPTIME}$ is open.*

**B3. Savitch, written out.** [ours] Prove
$\mathrm{NSPACE}(s)\subseteq\mathrm{SPACE}(s^2)$ and derive
$\mathrm{PSPACE}=\mathrm{NPSPACE}$. → B02. Code:
`complexity/reachability.py::savitch_reach` — the recursion depth is the proof.

**B4. Log-space reductions.** [MIT-18.404] Does ODD-PARITY reduce to PATH in log
space? Does PATH reduce to ODD-PARITY in log space? → B03. *Answers: yes, since
PATH is NL-complete and ODD-PARITY $\in\mathrm L$ (the reduction is explicit in
the folder); and nobody can give the other direction, because it would prove
$\mathrm L=\mathrm{NL}$.*

**B5. Immerman–Szelepcsényi.** [ours] Prove $\mathrm{NL}=\mathrm{coNL}$ by
inductive counting, and say why the same argument does not give
$\mathrm{NP}=\mathrm{coNP}$. → B03. Code:
`complexity/reachability.py::inductive_count`.

**B6. The polynomial hierarchy.** [AB] Define $\Sigma_k^p$ and $\Pi_k^p$ by
alternating quantifiers; prove $\mathrm{PH}\subseteq\mathrm{PSPACE}$; show
$\lnot(\exists x\forall y\,\varphi)\equiv\forall x\exists y\,\lnot\varphi$; and
say what $\Sigma_2^p=\Pi_2^p$ would imply. → B02.
Worked: `../src/exercises/princeton-arora-barak-2007`
`pt1_polynomial_hierarchy`. *PH is named by 192.219 [S5] and by Pichler's own
course [S7] but not by 192.043's own bullet list [S1] — see
[`00-exam-focus.md`](00-exam-focus.md).*

**B7. Circuit complexity, both halves.** [AB] (a) Shannon's counting argument:
show almost every Boolean function on $n$ bits needs circuits of size
$\Theta(2^n/n)$. (b) Show P/poly contains **undecidable** languages, and say
what that does to the Karp–Lipton statement. → B04.
*Answer to (b): $L=\{1^n: n\in A\}$ for any $A$ whatsoever has constant-size
circuits. Non-uniformity, not power, is the difference.*
Worked: `pt2_shannon_counting`, `pt2_ppoly_contains_undecidable`.

**B8. Adleman: $\mathrm{BPP}\subseteq\mathrm{P/poly}$.** [AB] Amplify below
$2^{-n}$, union-bound over the $2^n$ inputs, conclude that one advice string
works for all of them — and say why the proof gives you no way to find it.
→ B05. Worked: `pt3_adleman` (with $p=\frac23$, $n=6$: $t=39$ repetitions,
per-input error $0.0155<2^{-6}$, union bound $0.992<1$).

**B9. $\mathrm{BPP}\subseteq\mathrm{PSPACE}$.** [MIT-18.404] Simulate a
probabilistic polynomial-time machine in polynomial space. → B05.
*Answer: enumerate the $2^r$ coin sequences one at a time, reusing the same $r$
cells, and keep one counter. Exponential time, $O(r)$ space.*

**B10. The Chernoff bound in anger.** [ours] How many repetitions turn a
$\frac12+\varepsilon$ algorithm into a $1-\delta$ one? Derive it, then check it
numerically. → B05. Code: `complexity/bpp_amplify.py`.

---

## Exam 2 — B06 and block C

**Egly's own sheets, programming exercises and written exercise test** are the
only real questions from a lecturer of this course, and he reuses them [S18].
They are graded work of a running course and are not solved here. Everything
below is a *supplement*.

**C1. $\mathrm{BQP}\subseteq\mathrm{PSPACE}$ by the Feynman path sum.** [AB]
Write the amplitude $\langle y|U_d\cdots U_1|0\rangle$ as a sum over intermediate
basis states, and count the space one term needs. → B06, C01.
Worked: `pt4_path_sum`, which sums $8^4$ paths and reproduces the statevector.

**C2. State the BQP sandwich.** [ours] Prove
$\mathrm{BPP}\subseteq\mathrm{BQP}$ and
$\mathrm{BQP}\subseteq\mathrm{PSPACE}$; then state the BBBV bound and say why it
rules out a black-box exponential speedup for NP. → B06, C04.
Code: `complexity/query_complexity.py`; sources [S41], [S54].

---

## The endianness check, and why block C is not topped up further

[`00-exam-focus.md`](00-exam-focus.md) records the trap: **the leftmost symbol of
a ket is the first tensor factor and the most significant bit** [S16, S20], and
Qiskit is the reverse [S17]. Any borrowed quantum exercise has to be checked
against that before it is offered as practice, or it teaches the wrong matrices.

That check was actually done, not assumed. C4's path sum builds every gate matrix
*through* [`../src/py/quantum/sim.py`](../src/py/quantum/sim.py), whose
convention is the course's, and then reads one amplitude both ways: in the
course's order $\langle 011|\psi\rangle = 0$, while the same index string read in
Qiskit's order gives $\tfrac{1+i}{2\sqrt2}\neq0$. A zero becoming non-zero is
what the trap costs, and it is pinned by
`test_substitute_exercises.py::test_feynman_path_sum_uses_the_courses_qubit_order`.

It is also **why the Qiskit textbook was rejected** as a substitute source even
though its licence is the cleanest of all the candidates (Apache-2.0): it is
written in the opposite qubit order throughout, and its repository has been
archived since January 2024 [`../refs/SOURCES.md`](../refs/SOURCES.md)
§Considered and deliberately not used.

## TISS topics with no good free practice material

Said here rather than padded around.

- **Random access machines.** On 192.042's list, and 192.042 merged into 192.043
  for 2026W [S4]. Every free complexity source found — S59, S60, S31, S26 —
  works with Turing machines and mentions the RAM only to say it is polynomially
  equivalent. **No practice problems found.** Ask at the first meeting whether
  the RAM model is examined at all.
- **PP as distinct from BPP.** Arora & Barak ch. 17 defines it and proves Toda's
  theorem, but neither MIT paper examines it and no solved exercise was found.
  B05 carries the definitions; there is nothing to drill.
- **Quantum error correction and decoherence.** The *German* learning outcome
  asks for "elementare Fehlerkorrekturstrategien"; the English one does not, and
  neither sibling course teaches it [S1, S20]. Free material is abundant
  (Nielsen & Chuang ch. 10, de Wolf ch. 15 [S30, S31]) but **nothing establishes
  that it is examined**, so no practice set was built for it. C01's short
  section stands.
- **Variational and hybrid algorithms (C08).** On 192.043's list [S1] and in no
  sibling quantum course; its treatment comes from De Maio's 194.027 [S10, S22].
  The free practice that exists is Qiskit-flavoured and therefore
  reverse-endian; `quantum/vqe.py` and `quantum/qaoa.py` are the practice.
- **Fermüller's block.** Still unestablished [S13]. If he teaches logic or
  proof complexity, none of the sources above covers it and this note does not
  pretend to.

## How to use this note

1. **B1 first**, then the 3D-matching reduction in the 6.046 folder. Writing two
   reduction-correctness proofs cleanly is the single best-evidenced use of
   preparation time for Exam 1 [S23].
2. **A5 and A6 second.** Max-flow/min-cut is the only capitalised result on
   either syllabus, and A5 is an exercise you can be asked to do with a pen.
3. **B2 and B6–B9** are the class-inclusion half. They are one afternoon.
4. For Exam 2, **Egly's sheets**, not this note. C1 and C2 are the top-up.
5. Every worked answer runs:
   `python -m pytest src/py -q` from the course folder.
