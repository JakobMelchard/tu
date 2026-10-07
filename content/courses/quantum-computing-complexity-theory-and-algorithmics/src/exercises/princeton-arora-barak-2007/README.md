# Arora & Barak, *Computational Complexity: A Modern Approach* — free draft [S60]

> **Provenance.** Sanjeev Arora and Boaz Barak, Princeton University. The
> authors' free internet draft, dated January 2007, at
> <https://theory.cs.princeton.edu/complexity/book.pdf> (retrieved 2026-09-22;
> the published book is Cambridge University Press, 2009, ISBN
> 978-0-521-42426-4). **Licence: none — the draft's title page says "Not to be
> reproduced or distributed without the authors' permission".**
> So this folder is **cite-only**: nothing is vendored, no exercise text is
> copied, and every exercise below is one **we built ourselves** for a theorem
> the book states. This is **not** 192.043 material and not a past paper.

Solution: [`solution.py`](solution.py).

## Why this book

It is the one free complexity reference that covers the four things 192.043
examines and the MIT paper in `../mit-18.404j-2020` never
reaches, namely **the polynomial hierarchy, circuit classes and P/poly,
Adleman's theorem, and BQP**. Three of those four are named by Pichler's own
course [S7, S14] and by 192.219 [S5]; the fourth is B06, examined on Exam 2
[S1]. Papadimitriou [S26] is the book 192.043 and Pichler actually set, and it
is commercial; Arora & Barak covers the same material in the same order with a
free draft, so it is the substitute, not the replacement.

## What it covers that 192.043's TISS topic list also covers

| chapter (published edition) | topic | our note |
|---|---|---|
| 1–2 | Turing machines, P, NP, NP-completeness, reductions, Cook–Levin | B01 |
| 3 | diagonalisation, the time and space hierarchy theorems, oracles | B02 |
| 4 | space complexity, PSPACE, TQBF, Savitch, NL, Immerman–Szelepcsényi | B02, B03 |
| **5** | **the polynomial hierarchy and alternations**, $\Sigma_k^p$, $\Pi_k^p$, $\mathrm{PH}\subseteq\mathrm{PSPACE}$ | **B02** |
| **6** | **Boolean circuits, P/poly, Karp–Lipton, NC and AC** | **B04** |
| **7** | **randomised computation: RP, coRP, ZPP, BPP, Adleman, Sipser–Gács–Lautemann** | **B05** |
| **10** | **quantum computation: BQP, $\mathrm{BPP}\subseteq\mathrm{BQP}\subseteq\mathrm{PSPACE}$, Simon, Shor, Grover** | **B06** |
| 17 | counting complexity, #P, **PP**, Toda | B05 |

The four bold rows are what this folder works. Chapter numbers are those of the
**published** edition; the 2007 draft's numbering differs in Parts II and III, so
check the draft's own table of contents before following a cross-reference.

## What it covers that 192.043 does not

Most of Parts II and III: average-case complexity, derandomisation and
pseudorandomness, the PCP theorem and hardness of approximation, proof
complexity, communication complexity, natural proofs, expanders. **None of these
is on 192.043's list [S1], on 192.219's [S5] or in Pichler's headings [S14].**
Chapter 8 (interactive proofs) and chapter 9 (cryptography) are likewise out.

And the converse, again: **random access machines** are on 192.042's list, which
merged into 192.043 in 2026W [S4], and Arora & Barak works with Turing machines
throughout. No free source found examines the RAM model; see the practice note.

## The four exercises, all ours

1. **The polynomial hierarchy is inside PSPACE, and $\Sigma_2^p$ dualises to
   $\Pi_2^p$.** Write an evaluator for $Q_1x_1\cdots Q_nx_n\,\varphi$ over an
   arbitrary quantifier prefix. Show (a) that
   $\lnot(\exists x\forall y\,\varphi) \equiv \forall x\exists y\,\lnot\varphi$
   on random instances, (b) that the prefix $\exists^n$ reproduces SAT, so
   $\Sigma_1^p = \mathrm{NP}$, and (c) that the evaluator's workspace is $O(n)$,
   which *is* the proof of $\mathrm{PH}\subseteq\mathrm{PSPACE}$.

2. **Shannon's counting bound.** Bound the number of fan-in-2 circuits with $s$
   gates over $n$ inputs by $\bigl(16(n+s+2)^2\bigr)^s$, and find for each $n$
   the smallest $s$ for which that number can still cover all $2^{2^n}$ Boolean
   functions. Confirm it grows like $2^n/n$.

3. **P/poly contains undecidable languages.** Exhibit one and give its circuits.

4. **Adleman's theorem, $\mathrm{BPP}\subseteq\mathrm{P/poly}$.** Amplify a
   $2/3$-correct machine until its per-input error is below $2^{-n}$, union-bound
   over the $2^n$ inputs, and then *find* a single random string that is correct
   on every input of that length.

5. **$\mathrm{BQP}\subseteq\mathrm{PSPACE}$ by the Feynman path sum.** Compute
   the output amplitude of a small circuit as a sum over all intermediate basis
   paths, and check it against the statevector simulator.

## Answers

1. The evaluator is `eval_qbf`; `sigma2_sat` fixes the prefix
   $\exists^k\forall^{n-k}$. Duality and $\Sigma_1^p=\mathrm{NP}$ are checked on
   200 random instances. The worked instance
   $\varphi = (x_1\lor\lnot x_2\lor x_4)\land(x_1\lor\lnot x_2\lor x_3)\land(\lnot x_2\lor\lnot x_3\lor\lnot x_4)\land(x_1\lor x_3\lor\lnot x_4)\land(\lnot x_2\lor x_3)$
   is **false** as $\exists x_1\forall x_2x_3x_4$ and **true** as
   $\exists x_1x_2\forall x_3x_4$: moving one variable across the alternation
   changes the answer, which is why nobody expects the levels to collapse.
   $\mathrm{PH}\subseteq\mathrm{PSPACE}$ because the recursion holds one
   assignment and a stack of depth $n$; it never materialises the $2^n$ leaves.

2. The smallest covering size, computed for $n=2\ldots12$: 1, 1, 2, 4, 6, 11,
   19, 35, 63, 114, 209 — against $2^n/n$ = 2.0, 2.7, 4.0, 6.4, 10.7, 18.3,
   32.0, 56.9, 102.4, 186.2, 341.3. The ratio settles near $0.6$, which is the
   $2^n/n$ of Shannon's bound with the constants of *this* encoding. The
   statement to carry into the exam is qualitative: **almost every Boolean
   function needs circuits of size $\Theta(2^n/n)$, and no explicit function is
   known to need more than about $3n$** [S56].

3. Take any $A\subseteq\mathbb N$, however uncomputable, and let
   $L=\{1^n: n\in A\}$. $L$ has exactly one string per input length, so the
   circuit for length $n$ is the **constant** $[n\in A]$ — size 1. So P/poly
   contains undecidable languages, and non-uniformity, not power, is the whole
   difference between P and P/poly. This is the standard warning attached to
   Karp–Lipton (B04).

4. With $p=2/3$ and $n=6$, $t=39$ repetitions put the per-input error at
   $0.0155 < 2^{-6}$, so the union bound over 64 inputs is $0.992 < 1$ and a
   good advice string must exist. Sampling finds one in a couple of draws. The
   proof is non-constructive — that is the point, and it is also why
   $\mathrm{BPP}\subseteq\mathrm{P/poly}$ says nothing about derandomising BPP.

5. `pt4_path_sum` sums $8^4 = 4096$ paths per output string of a five-gate,
   three-qubit circuit and reproduces the statevector exactly. Each term needs
   one path index and one running product, so the amplitude — and therefore the
   acceptance probability — is computable in polynomial space.

## The endianness check, done rather than assumed

Any quantum exercise borrowed from outside this course must be checked against
the course's qubit ordering before it is offered as practice [S17]. Done here:

- Arora & Barak write $|x_1\cdots x_n\rangle$ with $x_1$ the **first tensor
  factor**, which is also Egly's convention (leftmost symbol = most significant
  bit) [S16, S20]. So the book's matrices transfer unchanged.
- `pt4_path_sum` does not assume that. It builds every gate matrix *through*
  [`../../py/quantum/sim.py`](../../py/quantum/sim.py), whose big-endian
  convention is the course's, instead of writing Kronecker products by hand.
- It then reads one amplitude both ways, and the two numbers differ: in the
  course's order $\langle 011|\psi\rangle = 0$, while the same index string read
  in Qiskit's reversed order gives $\tfrac{1}{2}(1+i)/\sqrt2 \neq 0$. A zero
  amplitude becoming non-zero is what the trap costs.
