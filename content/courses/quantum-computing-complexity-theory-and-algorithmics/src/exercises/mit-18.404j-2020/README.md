# MIT 18.404J *Theory of Computation*, Fall 2020 — sample final [S59]

> **Provenance.** This is **MIT's** examination paper, not TU Wien's, and not
> 192.043's. 192.043 has no past paper in any year [S24]. Source: MIT
> OpenCourseWare, *18.404J / 18.4041J / 6.840J Theory of Computation*, Prof.
> Michael Sipser, Fall 2020, "Sample Final Exam" and "Sample Final Exam
> Solutions" (the Fall 2006 paper), retrieved 2026-09-22.
> **Licence: CC BY-NC-SA 4.0** — attribution as required by
> <https://ocw.mit.edu/terms/>. Because this folder *adapts* CC BY-NC-SA
> material, **treat this folder (README and `solution.py`) as CC BY-NC-SA 4.0**.
> No question text is reproduced: every question below is restated in our own
> words, and the solutions are ours.

Solution: [`solution.py`](solution.py) — run it, or let
[`../../py/test_substitute_exercises.py`](../../py/test_substitute_exercises.py)
run it.

## Why this paper and not another

Pichler's complexity block is examined, in his own course, by asking students to
**prove the correctness of a reduction that is handed to them** — not to invent
one [S23]. 18.404J's complexity half (7 of its 12 weeks) is the only free,
licence-clear, *solved* paper found that examines exactly that skill on exactly
this class list. Its syllabus names **P, NP, L, NL, PSPACE, BPP, complete
problems, quantifiers and games, hierarchy theorems, oracles, probabilistic
computation** [S59] — set that beside 192.043's own complexity bullets [S1] and
Pichler's heading list [S7, S14] and the middle is nearly all of both.

## What it covers that 192.043's TISS list also covers

| this paper asks about | our note |
|---|---|
| the settled and the open inclusions among P, NP, PSPACE, EXPTIME, L, NL | B01, B02, B03 |
| Savitch's theorem, the hierarchy theorems, PSPACE under complement | B02 |
| NP-completeness of a combinatorial puzzle, **both directions of the correctness proof** | B01 |
| EXPTIME-completeness by simulating a machine for $2^{n^k}$ steps | B02 |
| log-space reductions, PATH, why one direction would settle L vs NL | B03 |
| BPP $\subseteq$ PSPACE by enumerating coin sequences | B05 |

## What it covers that 192.043 does not

Five of its twelve weeks. **Do not study these for 192.043.**

- Automata and language theory — finite automata, regular expressions, pushdown
  automata, context-free grammars, pumping lemmas. Not on 192.043's list [S1],
  not on 192.219's [S5], not in Pichler's headings [S14].
- Computability — the halting problem, the recursion theorem, undecidability.
  Question 4 of this paper is a mapping reduction from $A_{TM}$; skipped here.
- Interactive proof systems. Question 7; skipped here. IP is not on any of the
  three syllabi.

And the converse: 192.043 examines things 18.404J never reaches — **random
access machines** [S4], **circuit classes and P/poly** [S1], **PP**, and the
**polynomial hierarchy** as a named object [S5, S7]. Those are why [S60] is in
the second folder.

## The four questions worked here, in our own words

1. **A block of one-line claims, each to be marked true, false or open.**
   Sixteen on the paper; the point is not the marking but knowing *which are
   settled*. Worked: the three with computational content (PATH decidable in
   polynomial time, NL = coNL by inductive counting, Savitch's recursion) are
   checked against the reference implementations in
   [`../../py/complexity/reachability.py`](../../py/complexity/reachability.py);
   the rest are listed as settled / open / refuted.

2. **A one-player stone puzzle, shown NP-complete.** A board carries red and
   blue stones, at most one per cell. A move deletes all stones of one colour
   from one column. You win if you can reach a position in which no column holds
   both colours and every row still holds at least one stone. Show the problem
   is NP-complete.

   *(The same puzzle is Problem 7.28 in Sipser's textbook, which 18.404J sets
   [S59]. The statement above is ours.)*

3. **Log-space reductions.** Does ODD-PARITY reduce to PATH in log space? Does
   PATH reduce to ODD-PARITY in log space? Justify each answer.

4. **BPP $\subseteq$ PSPACE.** Show that a probabilistic polynomial-time machine
   can be simulated in polynomial space.

Two more questions on the paper are in scope but are pure prose, so they are not
in `solution.py`: **EXPTIME-completeness** of the "does machine $M$ write symbol
$\alpha$ in cell $i$ at step $j$" language (B02 — the reduction is the padding
argument, and it is worth writing out), and a second reduction question.

## Answers

1. Settled: $\mathrm P\subseteq\mathrm{NP}\subseteq\mathrm{PSPACE}\subseteq\mathrm{EXPTIME}$;
   $\mathrm P\neq\mathrm{EXPTIME}$ (time hierarchy); $\mathrm{PSPACE}=\mathrm{NPSPACE}$
   (Savitch); $\mathrm{NL}=\mathrm{coNL}$ (Immerman–Szelepcsényi);
   $\mathrm{PATH}\in\mathrm P$; PSPACE closed under complement; TQBF is
   PSPACE-complete. Open: $\mathrm P=\mathrm{NP}$, $\mathrm{NP}=\mathrm{coNP}$,
   $\mathrm L=\mathrm{NL}$, $\mathrm P=\mathrm{PSPACE}$,
   $\mathrm{NP}=\mathrm{PSPACE}$, $\mathrm{BPP}=\mathrm P$,
   $\mathrm{PSPACE}=\mathrm{EXPTIME}$. **False:**
   $\mathrm{PSPACE}=\mathrm{NL}$ — Savitch puts NL inside
   $\mathrm{SPACE}(\log^2 n)$, which the space hierarchy theorem separates from
   PSPACE. That asymmetry (some of these are open, one is a theorem) is the
   whole question.

2. **In NP:** the certificate is one bit per column, saying which colour
   survives; checking costs $O(\text{rows}\times\text{columns})$.
   **NP-hard, from 3SAT:** variable $x_i$ becomes column $i$, clause $c_j$
   becomes row $j$; the literal $x_i\in c_j$ puts a *blue* stone at $(j,i)$ and
   $\lnot x_i\in c_j$ a *red* one. Tautological clauses (containing $x_i$ and
   $\lnot x_i$) are dropped first — they constrain nothing, and they are the one
   case where the map would want two stones in one cell.
   - $(\Rightarrow)$ From a satisfying assignment, keep blue in column $i$ when
     $x_i$ is true and red when it is false. The stone surviving in row $j$ is a
     literal the assignment satisfies, and every clause has one.
   - $(\Leftarrow)$ From a winning play, read the assignment off the surviving
     colours. Every row keeps a stone, so every clause has a true literal.
   - The map is computable in time linear in the formula, and the board is
     $|\text{clauses}|\times|\text{vars}|$.

   `q3_reduction_correctness` checks the equivalence on **112 791** formulas —
   every 3-CNF over three variables with up to four distinct clauses — and finds
   zero mismatches. A numerical check is not the proof; it is the thing that
   catches the tautological-clause case, which the three-line proof silently
   assumes away.

3. ODD-PARITY $\in\mathrm L$ and PATH is NL-complete, so ODD-PARITY $\le_L$
   PATH — and `q5_logspace_reductions` builds the reduction explicitly (nodes
   $(i,p)$ for position and running parity) and verifies it on all 510 strings
   of length $\le 8$. The other direction would put PATH in L and hence settle
   $\mathrm L=\mathrm{NL}$, so no one can give it.

4. A machine tossing $r$ coins has $2^r$ branches. Enumerate them **one at a
   time**, reusing the same $r$ cells, and keep one counter of accepting
   branches; accept iff the count exceeds $2^{r-1}$. Time $2^r$, space $O(r)$.
   `q6_bpp_in_pspace` runs the enumeration for a concrete machine (guess an
   assignment, accept iff it satisfies a fixed 3-CNF) and reports 7 accepting
   branches of 16 — so that machine, on that input, is *not* a BPP acceptor with
   the usual gap, which is the second thing the question is checking you noticed.

## The trap in this folder

The paper is **open book** and MIT's grading conventions are not TU Wien's.
192.043's exams are **closed book** in the sibling course that shares its slots
[S5], and Egly's quantum test is closed book too [S15]. Practise these without
the notes.
