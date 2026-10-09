# Notes — 192.043 Quantum Computing, Complexity Theory, and Algorithmics

Three subjects, three blocks, two exams. Read
[`00-exam-focus.md`](00-exam-focus.md) first; it says what is known and what is
inferred about the examination, and it carries the real questions from the
sibling courses. Then
[`01-practice-set-substitute-sources.md`](01-practice-set-substitute-sources.md),
which is the bounded practice set built from **other institutions'** free
material, every problem tagged with where it came from. The block structure, the lecturers and the conventions are in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md); every `[S<n>]`
resolves in [`../refs/SOURCES.md`](../refs/SOURCES.md).

Every note has the same six sections: definitions, results, worked example,
pitfalls, exam-style questions, code.

## Block A: Algorithmics · Chen (decks [S62]) and Pichler, 01.10-23.10 · **Exam 1, 11 Dec**

The 2026W session-by-session schedule and the chapter-to-note map are in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md); notes A01-A03
carry a "2026W lectures" section with drill cards checked against the decks
[S62].

Taught jointly with 192.219 in EI 10 / EI 8 / EI 5 [S5]. Kleinberg & Tardos
order [S25].

| note | topic |
|---|---|
| [A01](A01-asymptotics-and-recurrences.md) | O-notation, asymptotic growth, recurrences, the master theorem |
| [A02](A02-graphs.md) | graphs, adjacency structures, BFS/DFS, connectivity, bipartiteness, DAGs, Dijkstra |
| [A03](A03-greedy.md) | greedy: interval scheduling, interval partitioning, lateness, minimum spanning trees |
| [A04](A04-divide-and-conquer.md) | merge sort, counting inversions, closest pair, Karatsuba, Strassen |
| [A05](A05-dynamic-programming.md) | weighted intervals, knapsack, Bellman–Ford, edit distance |
| [A06](A06-network-flow.md) | Ford–Fulkerson, max-flow/min-cut, matchings and the other applications |
| [A07](A07-approximation.md) | approximation ratios, greedy and LP-rounding bounds, inapproximability |
| [A08](A08-lp-vs-ilp.md) | linear programming, duality, integrality gaps, ILP |

## Block B: Complexity theory · Pichler (inferred), 12.10 and 28.10-06.11 [S62] · **Exam 1** (B06 → Exam 2)

Papadimitriou order [S26]; Pichler's own heading list [S14].

| note | topic |
|---|---|
| [B01](B01-models-and-np-completeness.md) | Turing machines, **random access machines**, P, NP, reductions, Cook–Levin, NP-completeness |
| [B02](B02-pspace-and-exptime.md) | PSPACE, TQBF, EXPTIME, the hierarchy theorems, **the polynomial hierarchy** |
| [B03](B03-inside-p-l-and-nl.md) | L, NL, PATH, log-space reductions, Immerman–Szelepcsényi |
| [B04](B04-circuit-complexity.md) | circuits, P/poly, Karp–Lipton, NC and AC, the parallel computation thesis |
| [B05](B05-probabilistic-classes.md) | RP, coRP, ZPP, BPP, PP, amplification, Adleman, Sipser–Gács–Lautemann |
| [B06](B06-quantum-complexity.md) | uniform quantum circuits, BQP, the extended Church–Turing thesis, QMA, quantum query complexity — **examined on Exam 2** |

B06 is filed under *Complexity theory* on the TISS subject list [S1] but is
written for Exam 2, whose title is "Quantum Algorithms **and Complexity**".

## Block C: Quantum computing · Egly (inferred), 09.11-30.11, quantum complexity 07.12-16.12 [S62] · **Exam 2, 21 Jan**

In the order of Egly's own lecture, reconstructed from the student summary of
192.070 [S20]; conventions from his exercise sheets [S16, S17].

| note | topic |
|---|---|
| [C01](C01-qubits-gates-and-measurement.md) | qubits, the postulates, gates, tensor bookkeeping, **the course's conventions**, measurement, entanglement, noise and decoherence |
| [C02](C02-programming-techniques-and-reversible-computation.md) | reversible computation, Toffoli, garbage and uncomputation, oracles, phase kickback, multi-controlled gates |
| [C03](C03-deutsch-jozsa-bernstein-vazirani-teleportation.md) | superdense coding, teleportation, Deutsch, Deutsch–Jozsa, Bernstein–Vazirani |
| [C04](C04-grover.md) | Grover, the diffusion operator, amplitude amplification, counting, the BBBV lower bound |
| [C05](C05-simon.md) | Simon's problem, Fourier sampling over $\mathbb{Z}_2^n$, GF(2) linear algebra |
| [C06](C06-qft-phase-estimation-order-finding.md) | the QFT and its recursive construction, phase estimation, order finding, continued fractions |
| [C07](C07-shor.md) | Shor: the reduction to order finding, the number theory, worked $N=15$ and $N=21$ |
| [C08](C08-variational-and-hybrid-algorithms.md) | VQE, QAOA, the parameter-shift rule, barren plateaus — sourced from 194.027, not from a sibling quantum course |

## Cross-block

| note | topic |
|---|---|
| [00](00-exam-focus.md) | what is actually asked, and what is inference |
| [01](01-practice-set-substitute-sources.md) | 23 exam-shaped problems from MIT OCW 18.404J and 6.046J, from Arora & Barak, and ours — **provenance on every one** [S59–S61] |

## What to read alongside

- [`../refs/README.md`](../refs/README.md) — what was and was not established,
  and why nothing is vendored.
- [`../src/exercises`](../src/exercises/README.md): three substitute folders
  built from MIT OCW and Arora & Barak [S59–S61].
- `CHANGELOG.md` — what the source-verification pass changed.
- [`../src/README.md`](../src/README.md) — how to run everything.
