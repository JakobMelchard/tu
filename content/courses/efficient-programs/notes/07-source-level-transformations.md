# 07 Source-level transformations

Slides 39 to 68 [S3], thirty slides, the largest block of the deck; from
Bentley's *Writing Efficient Programs* [S11] with additions for current
hardware [S4]. Each is a correctness-preserving rewrite with a **condition**
under which it is valid and a **cost** it trades. The interview can pick any
one; the table is the checklist, the sections below add the arithmetic where
there is some.

## The catalogue

| # | transformation [S3] | before → after | valid when | trade |
|---|---|---|---|---|
| 39 | Code motion out of loops | `for(...) { … f(x) … }` → `t = f(x); for(...) { … t … }` | `f(x)` has no side effects and uses no loop-computed value | compilers do it when they can prove it (note 01: traps, aliasing) |
| 40 | Combining tests, sentinel | `for (i=0; i<n && a[i]!=key; i++)` → `a[n]=key; for (i=0; a[i]!=key; i++)` | `a[n]` is writable | one compare+branch per iteration; costs maintainability and reentrancy |
| 41 | Loop unrolling | `body(i)` → `body(i); body(i+1)` + remainder loop | always | fewer counter/branch instructions, more ILP; code size |
| 42 | Transfer-driven unrolling, modulo variable renaming | `new_a=…; …a…; a=new_a` unrolled by 2 → alternate `a1`, `a2`, no copies | always | removes the copy instructions the unrolled loop would need |
| 43 | Software pipelining | compute `a` for the *next* iteration at the end of this one | computing `a` has no side effects | the load/compute of iteration $i+1$ overlaps the use of iteration $i$ |
| 44 | Unconditional branch removal | `while (t) code;` → `if (t) do code; while (t);` | always | one branch per iteration instead of two |
| 45 | Loop peeling | `while (t) code;` → `if (t) { code; while (t) code; }` | always | first iteration specialised (removes a check from the loop) |
| 46 | Loop fusion | two loops over `i` → one | iteration $k$ of `code2` does not depend on iteration $j > k$ of `code1`; `code2` does not overwrite data `code1` reads | half the loop overhead, one pass over the data (locality) |
| 47 | Algebraic identities | `~a & ~b` → `~(a|b)` | true in the machine's arithmetic: integers are not $\mathbb Z$ (overflow: $a > b \not\Leftrightarrow a+n > b+n$), FP is not $\mathbb R$ (rounding: $a+(b+c) \ne (a+b)+c$) | |
| 48 | Short-circuiting monotone functions | `sum += x[i]` all, then `flag = sum > cutoff` → stop as soon as `sum > cutoff` | all `x[i] >= 0`, `sum` and `i` unused later | fewer iterations; unroll to cut the added compares |
| 49 | Arithmetic with flags | `if (flag) x++` → `x += (flag != 0)` | always | `setne` + `add` instead of a branch: constant cost, no misprediction; a data dependence instead |
| 50 | Different representation of flags | `(a<0) != (b<0)` → `(a^b) < 0` | two's complement | 2 instructions instead of 4 |
| 51 | Long-circuiting | `A && B` → `A & B` | `A`, `B` compute flags, `B` has no side effects | use when `B` is cheap and `A` hard to predict |
| 52 | Reordering tests in `A && B` | → `B && A` | both side-effect free | cheaper first; more predictable first; higher probability of short-circuit first |
| 53 | Reordering `if/else if` | test `B` before `A` | side-effect free, $\neg(A \land B)$ | (our gloss, the slide gives none) the more frequent or cheaper case first |
| 54 | Boolean/state variable elimination | `flag = …; S1; if (flag) S2 else S3` → `if (…) { S1; S2 } else { S1; S3 }` | `flag` unused later | removes the variable and its test; duplicates `S1` |
| 55 | Collapsing procedure hierarchies | inlining; specialisation `foo(1, a)` → `foo_1(a)` | always | call overhead gone, constants propagate; code size |
| 56 | Precompute functions | `int foo(char c) {…}` → `foo_table[c]` | `foo` has no side effects, small domain | a load instead of a computation; table must be in cache to pay |
| 57 | Exploit common cases | memoization; special code for frequent parameters | results must stay correct for all cases | |
| 58 | Coroutines | producer/consumer coroutines instead of multi-pass processing | | no intermediate data set; pipelines, iterators |
| 59 to 61 | Recursion | tail-call → loop (`p = p->r; goto start`); inline; replace one recursive call by a counter (`code1` × count, then `code2` × count); explicit stack; another method for small sizes; and the reverse: **use recursion for automatic cache blocking** (`mm6`, note 09) | | |
| 62 | Compile-time initialisation | build tables at compile time | | CPU time vs load time from disk |
| 63 | Strength reduction, incremental algorithms | `y = x*x; x += 1; y = x*x` → `y += 2*x - 1` | exact in the arithmetic used | multiply → add; compilers do it for induction variables |
| 64 | Common subexpression / partial redundancy elimination | `a = Exp; b = Exp` → `b = a` | `Exp` side-effect free and unchanged between | |
| 65 | Pairing computation | `div` gives quotient and remainder; `sincos` | | second result almost free |
| 66 | Data structure augmentation | redundant data for a fast path: caching, memoization, hints (branch prediction is one); Gforth's dictionary = linked list + hash table | redundancy must be kept consistent (or be a hint that may be wrong) | speed vs consistency risk |
| 67 | Automata | state encodes something complex: FSM for scanning, pushdown for parsing, tree automata for instruction selection ("iburg (not an automaton) → burg") | | table-driven speed |
| 68 | Lazy evaluation | generate DFA states on first use | | the full DFA is large, only a small part is used |

## Cost models worth deriving

**Reordering tests** [S3 p.52]. For `A && B` with costs $c_A, c_B$ and
probabilities $p_A, p_B$ of being true (independent):

$$E[A \,\&\&\, B] = c_A + p_A c_B, \qquad E[B \,\&\&\, A] = c_B + p_B c_A,$$

so test $A$ first iff $c_A + p_A c_B < c_B + p_B c_A$, i.e. iff
$c_A/(1-p_A) < c_B/(1-p_B)$: order by cost divided by the probability of
short-circuiting. Add a misprediction term $20\,\min(p, 1-p)$ to each test's
cost and "more predictable first" falls out of the same formula.

**Flag arithmetic vs branch** [S3 p.49, 51]. A branch costs
$\approx 20 \min(p,1-p)$ c; the arithmetic form costs a fixed 1 to 3 c but
puts the condition on the data path. Measured (note 03, four runs):
unpredictable branch 2.4 to 2.7 ns, predicted branch 0.26 to 0.28 ns,
arithmetic 0.27 to 0.28 ns per element. The arithmetic form costs the same
as a perfectly predicted branch within noise, so on this kernel it wins as
soon as there are any mispredictions at all (break-even
$\min(p, 1-p) \lesssim 0.005/4.3 \approx 0.1\,\%$).

**Sentinel** [S3 p.40]. Saves one compare and one (predictable) branch per
iteration, ≈1 c of throughput on a wide core, nothing if the loop is latency
bound. The script measured tsp9 *slower* than tsp8 (13.4 M vs 13.2 M
cycles) and says it has not investigated why [S4]. Our conjecture, untested:
the loop was bound by something else, and the sentinel added an `if (j < i)`
inside the rarely taken branch and turned `<` into `<=` [S3 p.84].

**How often does the min update?** In a scan for the minimum of $m$ random
values, candidate $j$ is a new minimum with probability $1/j$, so the
expected number of updates is $H_m = \sum_{j=1}^m 1/j \approx \ln m + 0.577$.
The script uses this to explain why CSE of the second `dist()` call in tsp2
gained almost nothing: the second call sat inside the `if`, executed $H_n$
times per pass, not $n$ times [S4]. The same fact makes the update branch
in an argmin predictable (almost never taken), which note 08 needs.

**Short-circuiting a monotone bound** [S3 p.48, 81]. If $g(x) \le f(x)$ and
we only need to know whether $f(x) < \text{best}$, test $g$ first: when
$g(x) \ge \text{best}$ the answer is known. For the TSP, $g = \Delta x^2 \le
\Delta x^2 + \Delta y^2 = f$. Expected saving: the fraction of candidates with
$\Delta x^2 \ge \text{best}$, which after a few candidates is nearly all of
them.

## Where the TSP steps sit in the catalogue [S3 p.77 to 84]

| step | transformation |
|---|---|
| tsp1 → tsp2 | 64 common subexpression elimination (`dist()` once) |
| tsp2 → tsp3 | 47 algebraic identity (monotone `sqrt` dropped from a comparison) + 55 specialisation (`DistSqrd` copy, `dist` kept for other callers) |
| tsp3 → tsp4 | data structure change: `visited[]` → compaction in `tour[]`; removes a test (49 to 54 family) and halves iterations |
| tsp4 → tsp5 | 55 inlining, 39 code motion (`ThisX`, `ThisY` hoisted) |
| tsp5 → tsp6 | 48 short-circuit on the monotone x-part (lazy y-distance) |
| tsp6 → tsp8 | 66/data layout: `tour` becomes an array of points; removes an indirection |
| tsp8 → tsp9 | 40 sentinel |
| tspi4 | manual SIMD, structure of arrays (note 06) |

Our `src/c/tsp_greedy.c` uses steps 47+39 (v2), the data-structure change
(v3) and 48 (v4); note 08 has the numbers.

## Worked example: apply three catalogue entries to one loop

```c
for (i = 0; i < n; i++)
    if (a[i] != 3 && expensive(a[i])) count++;
```

52: `a[i] != 3` is cheap and, if most values are 3, short-circuits often:
keep it first. 51: if `a[i] != 3` is unpredictable and `expensive` is not
expensive after all, `&` beats `&&`. 49: `count += (a[i] != 3) & expensive(a[i])`
removes the last branch. 56: if `expensive` has a small domain, a table
lookup. 39: if `expensive` depends only on a loop-invariant, hoist it. Each
step needs one measurement; the order of trying them follows the cost
models above.

## Pitfalls

- Applying 47 with real-number reasoning: overflow and rounding.
- Applying 39/46 across a call that may have side effects.
- A sentinel in a buffer that is not yours (40) or in reentrant code.
- Arithmetic flags (49) on a predictable branch: no gain, a new dependence.
- Memoization (57, 66) without a bound on the table.
- Unrolling (41) until the loop no longer fits the instruction cache.
- Forgetting that the compiler already does 39, 41, 55, 63, 64 in the easy
  cases; measure before hand-applying them.

## Exam-style questions

1. **When is loop fusion valid, and what does it buy on current hardware?** When no iteration of the second loop depends on a later iteration of the first and the second does not overwrite what the first still reads. Buys one pass over the data (temporal locality, fewer misses) besides the halved loop overhead [S3 p.46].
2. **Give the condition and the cost of the sentinel technique.** The slot past the end must be writable; the search loop then needs no bound check. Saves a compare and branch per iteration; costs reentrancy (the buffer is modified), maintainability, and nothing if the loop is latency bound [S3 p.40] [S4].
3. **Two side-effect-free tests, `A` costs 1 c and is true 90 % of the time, `B` costs 10 c and is true 50 %. Which order for `A && B`?** $E[A\&\&B] = 1 + 0.9 \cdot 10 = 10$, $E[B\&\&A] = 10 + 0.5 \cdot 1 = 10.5$: `A` first, barely. Adding misprediction costs $20 \min(p, 1-p)$ (A: 2 c, B: 10 c) gives $3 + 0.9 \cdot 20 = 21$ c vs $20 + 0.5 \cdot 3 = 21.5$ c: still `A` first, still barely, because `B` is evaluated in 90 % of the cases either way [S3 p.52].
4. **Why did dropping `sqrt` work in the TSP and what would make it invalid?** Only the *order* of distances is used; $\sqrt{}$ is monotone on non-negative arguments, so comparing squares gives the same argmin. Invalid if the value were used (the tour length in `main` keeps `dist`), or if arguments could be negative or overflow [S3 p.78].
5. **Explain strength reduction with the slide's example and say who normally does it.** Replace `y = x*x` after `x += 1` by `y += 2*x - 1` (the difference of consecutive squares): a multiply becomes an add. Compilers do it for induction variables in address arithmetic; for application-level recurrences the programmer does [S3 p.63].

Code: `src/c/tsp_greedy.c` (v2 to v4), `src/c/branch_predict.c` (49/51). Sources: [S3 p.39 to 68, 77 to 85] [S4] [S11].
