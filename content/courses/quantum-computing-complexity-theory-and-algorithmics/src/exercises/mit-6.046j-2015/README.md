# MIT 6.046J *Design and Analysis of Algorithms*, Spring 2015 — final [S61]

> **Provenance.** This is **MIT's** examination paper, not TU Wien's, and not
> 192.043's. 192.043 has no past paper in any year [S24]. Source: MIT
> OpenCourseWare, *6.046J / 18.410J Design and Analysis of Algorithms*, Profs.
> Erik Demaine, Srini Devadas, Nancy Lynch, Spring 2015, "Final Exam" and
> "Solutions to Final Exam" (23 May 2015), retrieved 2026-09-22.
> **Licence: CC BY-NC-SA 4.0** (<https://ocw.mit.edu/terms/>). Because this
> folder *adapts* CC BY-NC-SA material, **treat this folder (README and
> `solution.py`) as CC BY-NC-SA 4.0**. No question text is reproduced: every
> question below is restated in our own words, and the solutions are ours.

Solution: [`solution.py`](solution.py).

## Why this paper

Exam 1 on 11 December covers **A01–A08 plus B01–B05** and is three hours long
[S1]. The A-half has, until now, had no practice material at all: the five
existing exercise folders are all Egly's quantum sheets. 6.046J's final is a
180-minute closed-book paper over exactly the second half of that syllabus —
**greedy with exchange arguments, dynamic programming and shortest paths,
max-flow/min-cut, linear programming, NP-completeness and approximation** —
which is lectures 10–17 of its own list [S61] and chapters 4–8 and 11 of
Kleinberg & Tardos, the book both 192.043 and 192.219 set [S1, S5, S25].

It is also, unlike 18.404J, a paper where the *format* transfers: a long
true/false block with one-line justifications, one "run the algorithm by hand"
question, and several "give an algorithm and argue it is correct" questions.
That is what a three-hour written algorithmics paper looks like.

## What it covers that 192.043's TISS list also covers

| this paper asks about | 192.043 / 192.219 bullet [S1, S5] | our note |
|---|---|---|
| recurrences and the master theorem | O-notation, asymptotic growth | A01, A04 |
| greedy with an exchange argument + binary search over the answer | greedy, interval scheduling | A03 |
| minimum spanning trees, uniqueness, negated weights | minimum spanning tree | A03 |
| Floyd–Warshall and its recursion's actual meaning | dynamic programming, shortest path | A05 |
| **one Edmonds–Karp iteration: residual graph, shortest augmenting path, new flow value** | **network flow, Ford–Fulkerson** | **A06** |
| max-flow/min-cut | **the MaxFlow–MinCut theorem** | A06 |
| list scheduling as a 2-approximation, with the lower-bound proof | approximation | A07 |
| NP-hardness by reduction from 3-dimensional matching | problem reductions | B01 |
| linear programming, reductions to LP, simplex | LP vs ILP | A08 |

## What it covers that 192.043 does not

Roughly half of it. **Do not study these for 192.043.**

- van Emde Boas trees, skip lists, universal and perfect hashing, range trees,
  augmented balanced search trees (its Problems 2 and 3).
- Amortised and competitive analysis.
- Synchronous and asynchronous **distributed** algorithms (its Problem 9).
- **Cryptography** — hash functions, encryption, Diffie–Hellman (several
  true/false parts).
- **Cache-oblivious** algorithms.
- Fixed-parameter tractability. Interesting, but not on either syllabus.

And the converse: 192.043 examines things 6.046J's final never touches —
**graph traversal, connectivity, bipartiteness and topological order** (A02),
**counting inversions and closest pair** (A04), **interval partitioning** (A03),
and the whole of block B beyond one NP-hardness question.

## The four questions worked here, in our own words

1. **A true/false block with one-line justifications.** Fourteen parts on the
   paper; four are on 192.043's syllabus and are worked here. (a) What does
   $T(n) = 2T(n/2) + \Theta(n^2)$ solve to? (b) In the Floyd–Warshall recursion,
   what does $d^{(k)}_{uv}$ actually mean? (c) Does negating all edge weights and
   running an MST algorithm give a maximum spanning tree? (d) With distinct edge
   weights, is the *second*-best spanning tree unique?

2. **"Be the computer".** Given a flow network with a flow already on it,
   draw the residual graph, name the shortest augmenting path, perform the
   augmentation, and state the resulting flow value.

3. **A greedy with an exchange argument.** Each of $m$ tasks costs $p_i$ hours;
   each of $n$ helpers will absorb up to $t_j$ hours of exactly one task, and the
   rest comes out of a shared budget $T$. Show that to finish $k$ tasks you need
   only consider the $k$ cheapest tasks and the $k$ most capable helpers; give a
   greedy feasibility test; then find the largest feasible $k$.

4. **Load balancing.** $n$ jobs of length $t_i$ on $m$ identical machines,
   minimising the makespan. Give a greedy algorithm and prove it is a
   2-approximation.

Two further in-scope questions are pure prose and are not in `solution.py`: an
**NP-hardness proof by reduction from 3-dimensional matching** (the same skill as
the 3SAT reduction in `../mit-18.404j-2020`, from a
different source problem — worth writing out by hand), and a probability
question on amplification by repetition, which is really B05.

## Answers

1. (a) $\Theta(n^2)$ — master theorem case 3, the root dominates; there is no
   extra $\log n$. (b) $d^{(k)}_{uv}$ is the shortest $u\to v$ path whose
   **intermediate vertices all lie in $\{1,\dots,k\}$**, *not* the shortest path
   with at most $k$ edges. The worked graph separates the two readings: the true
   $d_{14}=3$ along $1\to2\to3\to4$, while "at most two edges" would force the
   direct edge of weight 10. (c) True; verified against brute force over all
   spanning trees. (d) **False.** On $K_{1,3}$ plus two chords with weights
   $1,2,3,5,6$ the MST weighs 6 and *two* different single-edge swaps each cost
   $+3$, so two distinct trees tie at 9. Distinct weights make the MST unique;
   they do not make the runner-up unique.

2. Reading the figure gives a flow of value 25 (out of $s$ and into $t$, with
   conservation at all seven internal nodes — `p6_edmonds_karp_one_iteration`
   asserts this, and it is how the figure was checked before anything was
   computed). BFS finds the four-edge augmenting path
   $s\to 3\to 2\to 5\to t$, whose third edge is the **backward** residual of
   $2\to3$; the bottleneck is 1 and the new value is **26**, which is the
   paper's published answer. Running Edmonds–Karp to completion from zero gives
   a maximum flow of **27**, certified by the cut $\{s,3,4,7\}$ of the same
   capacity.

3. Sort tasks ascending and helpers descending; the $k$ cheapest tasks and $k$
   most capable helpers are enough (exchange argument: swapping in a cheaper
   task or a stronger helper never increases the budget used), and within those,
   pairing the cheapest task with the *weakest* selected helper is optimal.
   Feasible iff $\sum_i \max(0, p_i - t_i) \le T$. Feasibility is monotone in
   $k$, so binary search gives the largest $k$ in $O(n\log n)$ overall.
   `p5_greedy_exchange` checks the greedy against exhaustive search on 300
   random instances.

4. Greedy list scheduling: put each job on the currently least loaded machine.
   $\mathrm{OPT} \ge \max\bigl(\tfrac1m\sum_i t_i,\ \max_i t_i\bigr)$. The
   machine that finishes last started its final job $j$ when its load was at most
   the average, so its makespan is at most
   $\tfrac1m\sum_i t_i + t_j \le 2\,\mathrm{OPT}$. Sorting longest-first (LPT)
   improves the bound to $3/2$. Measured against brute-force optima on 40 small
   instances: worst greedy ratio 1.28, worst LPT ratio 1.12. The bound is tight:
   with $m(m-1)$ unit jobs and one job of length $m$, greedy gets $2m-1$ against
   an optimum of $m$ — for $m=4$ that is 7 against 4, a ratio of $1.75 = 2 - 1/m$.

## The trap in this folder

6.046J allows three double-sided crib sheets [S61]. 192.219, which shares
192.043's lecture slots and its 11 December exam slot, says **closed book**
[S5]. Practise these closed.
