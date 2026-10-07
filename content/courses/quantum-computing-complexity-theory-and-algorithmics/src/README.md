# Reference implementations — 192.043

Pure implementations first, library call as a cross-check in the test. Every
module runs standalone as a small demo. Conventions in
`docs/coursework-conventions.md`.

## Run everything

From the course folder, with the repo's Python environment:

```sh
python -m pytest src/py -q
make -C src/cpp test
```

The Python suite is ~130 tests and runs in about 10 s; the C++ targets build and
self-test in a few seconds. There is no `sh/` for this course.

## Layout

```
py/
  conftest.py            puts each topic folder on sys.path (plain `import sim`, `import dp`)
  test_substitute_exercises.py  runs the three substitute-source folders
  algorithmics/          block A  -> notes A01-A08
  complexity/            block B  -> notes B01-B06
  quantum/               block C  -> notes C01-C08, plus B06's query complexity
cpp/                     the four algorithms where the C++/Python comparison teaches something
exercises/               Egly's sheets + three substitute folders (see exercises/README.md)
```

### `py/algorithmics` — block A

| module | note | what |
|---|---|---|
| `divide_conquer.py` | A01, A04 | merge sort, inversion counting, closest pair, Karatsuba, Strassen, master-theorem checks |
| `graphs.py` | A02 | adjacency structures, BFS/DFS, connected components, bipartiteness, topological order, Dijkstra |
| `greedy.py` | A03 | interval scheduling, interval partitioning, union-find, Kruskal and Prim |
| `dp.py` | A05 | weighted interval scheduling, subset sum, 0/1 knapsack, Bellman–Ford, Floyd–Warshall, sequence alignment, LCS |
| `flow.py` | A06 | Ford–Fulkerson, Edmonds–Karp, capacity scaling, min cut, bipartite matching, project selection |
| `approx.py` | A07 | vertex cover 2-approximation, greedy set cover, load balancing (greedy and LPT), knapsack FPTAS, measured approximation ratios |
| `lp_ilp.py` | A08 | simplex on small instances, duality checks, ILP via `pulp`, integrality gaps |

### `py/complexity` — block B

| module | note | what |
|---|---|---|
| `sat.py` | B01 | DPLL, 3-SAT reductions, CNF encodings of the standard NP-complete problems |
| `reachability.py` | B03 | PATH as a nondeterministic log-space machine, Savitch's recursion, 2SAT via implication graph and SCC |
| `bpp_amplify.py` | B05 | majority amplification and the Chernoff bound, empirically |
| `query_complexity.py` | B06 | deterministic, randomised and quantum query complexity of small Boolean functions |

### `py/quantum` — block C (and B06)

| module | note | what |
|---|---|---|
| `sim.py` | C01 | the statevector simulator everything else uses. **Big-endian: qubit 0 is the most significant bit**, which is the course's own convention [S16, S20] |
| `deutsch_jozsa.py` | C03 | oracles in both forms, Deutsch, Deutsch–Jozsa |
| `bernstein_vazirani.py` | C03 | recovering the secret string in one query |
| `teleport.py` | C03 | teleportation and superdense coding |
| `grover.py` | C04 | oracle, diffusion, optimal iteration count, amplitude amplification |
| `simon.py` | C05 | the quantum sampling step plus GF(2) Gaussian elimination |
| `qft.py` | C06 | the $H$ + controlled-phase + swap circuit, and the dense matrix for cross-checks |
| `phase_estimation.py` | C06 | phase estimation with its output distribution |
| `order_finding.py` | C06 | controlled modular multiplication, inverse QFT, continued fractions |
| `shor.py` | C07 | the full algorithm with the classical pre- and post-processing |
| `vqe.py` | C08 | the two-qubit H₂ Hamiltonian, ansätze, the parameter-shift gradient |
| `qaoa.py` | C08 | MaxCut Hamiltonians, the QAOA state, barren-plateau variance |
| `gf2.py` | C05 | $\mathbb{F}_2$ linear algebra used by Simon |

### `cpp`

`dijkstra.cpp`, `kruskal.cpp`, `knapsack.cpp`, `edmonds_karp.cpp`, each with a
`--test` self-check. `make -C src/cpp test` builds and runs all four.

### `exercises`

Three **substitute folders built from other institutions' free material**
[S59-S61], because blocks A and B had no practice material of their own, each
with a `README.md` describing the questions in our own words. Every folder's
README opens with its provenance and licence. See
[`exercises/README.md`](exercises/README.md). They run under
`py/test_substitute_exercises.py` in the normal pytest run.

## Tests that reproduce a published number

The highest-value tests are the ones that reproduce a number somebody else
printed, because they validate the source reading and the implementation at once.

| test | reference | source |
|---|---|---|
| `test_vqe.py::test_exact_ground_energy_by_diagonalisation` | H₂ ground energy $-1.8572$ Ha at 0.735 Å, STO-3G | [S50] |
| `test_order_finding.py::test_worked_examples_in_the_notes` | every continued fraction printed in C06 and C07 | [S30] App. 4 |
| `test_phase_estimation.py::test_worked_numbers_in_note_c06` | the phase-estimation probabilities printed in C06 | [S30] 5.2 |
| `test_substitute_exercises.py::test_edmonds_karp_reproduces_mits_published_flow_value` | MIT's published answer: one augmentation takes the flow 25 -> **26** along $s\to3\to2\to5\to t$ | [S61] final, P6 |
| `test_substitute_exercises.py::test_list_scheduling_bound_is_tight` | greedy 7 against optimum 4 at $m=4$, i.e. exactly $2-\frac1m$ | [S61] final, P8 |
| `test_substitute_exercises.py::test_3sat_to_solitaire_is_answer_preserving` | the reduction agrees with brute-force SAT on all 112 791 formulas over 3 variables with $\le4$ clauses | [S59] final, Q3 |
| `test_substitute_exercises.py::test_feynman_path_sum_uses_the_courses_qubit_order` | the path sum reproduces the statevector, **and the same amplitude read in Qiskit's order does not** | [S60] ch. 10, [S17] |
