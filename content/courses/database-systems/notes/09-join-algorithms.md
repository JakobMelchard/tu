# 09 Join algorithms

> **Sourcing.** [S6] ch. 15: algorithms, the nested-loop numbers of the running
> example, the index-nested-loop, merge and hash costs, hybrid hash. The block
> nested-loop formula is an image in the slide PDF and is **derived here**.
> Comparison and page counts come from `python src/py/joins.py`.

Notation: $n_r$ tuples and $b_r$ pages of the outer relation $r$, likewise $s$;
$M$ buffer pages; costs in page transfers, output not counted. Example numbers
use [S6]'s `student` ($n = 5000$, $b = 100$) and `takes` ($n = 10{,}000$, $b = 400$).

## The algorithms

| algorithm | predicate | idea |
|---|---|---|
| nested loop (NLJ) | any $\theta$ | for each $r$-tuple scan $s$ |
| block nested loop (BNLJ) | any $\theta$ | for each **chunk** of $r$ pages scan $s$ once |
| index nested loop (INLJ) | equi, index on $s$'s join attribute | for each $r$-tuple, index lookup in $s$ |
| sort-merge | equi | sort both on the join attribute, merge; join duplicate groups pairwise |
| hash (Grace) | equi | partition both with $h_1$ into $k$ buckets; per bucket build a hash table on $s_i$ (build input) and probe with $r_i$ |

### Costs

**NLJ**, one buffer page per relation [S6]:
$$C = n_r\, b_s + b_r.$$
`student` outer: $5000 \cdot 400 + 100 = 2{,}000{,}100$; `takes` outer:
$10{,}000 \cdot 100 + 400 = 1{,}000{,}400$ [S6].

**BNLJ** (derived). Keep $M - 2$ pages of $r$ in memory, one page for $s$, one
for output. $r$ is read once, in $\lceil b_r/(M-2)\rceil$ chunks, and $s$ is
scanned once per chunk:
$$C = b_r + \left\lceil \frac{b_r}{M-2} \right\rceil b_s.$$
$M = 3$: $b_r + b_r b_s$ ($= 40{,}100$ for `student` outer). If $r$ fits
($b_r \le M - 2$): $b_r + b_s = 500$. The **smaller** relation belongs outside:
$b_r = 100$, $b_s = 400$, $M = 12$ gives $100 + 10 \cdot 400 = 4100$, the other
way round $400 + 40 \cdot 100 = 4400$. `joins.block_nested_loop` counts the
pages it reads and matches the formula (`test_bnlj_pages_match_formula`).

**INLJ** [S6]: $C = b_r + n_r \cdot c$ with $c$ the cost of one index lookup plus
fetching the matches (e.g. $h + 1$ for a B+ tree of height $h$ on a key). With
indexes on both sides the outer should be the relation with fewer **tuples**.

**Sort-merge** [S6]: $C = b_r + b_s$ if both are sorted, plus the sort costs of
note 07 otherwise. Each page is read once provided all tuples of one join value
fit in memory.

**Hash join** [S6], no recursive partitioning: partition both (read + write),
then read both again to build and probe:
$$C = 3(b_r + b_s)\quad (+\,4 n_h \text{ for partially filled partition blocks}).$$
$100 + 400$ pages: $1500$. Requirement: each build partition fits in memory, so
$\lceil b_s/(M-1) \rceil \le M - 2$, roughly $M > \sqrt{b_s}$; build on the
**smaller** relation. If the build input fits entirely, $C = b_r + b_s$.
**Hybrid hash** keeps the first build partition in memory: [S6]'s example goes
from 1500 to 1300 page transfers.

### Summary

| algorithm | page I/O | needs |
|---|---|---|
| NLJ | $n_r b_s + b_r$ | nothing |
| BNLJ | $b_r + \lceil b_r/(M-2)\rceil b_s$ | nothing; good if one side is small |
| INLJ | $b_r + n_r c$ | index on the inner join attribute |
| sort-merge | $b_r + b_s$ + sorting | equi-join; sorted inputs are a bonus for later operators (interesting orders, note 10) |
| hash | $3(b_r + b_s)$ | equi-join; $M \gtrsim \sqrt{\min(b_r, b_s)}$ |

## Worked example: the same join five ways

`joins.sample()`: $r$ = 60 tuples $(i, k)$, $s$ = 90 tuples $(k, \text{label})$,
join attribute $k \in \{0..19\}$, 10 tuples per page. All five produce the same
**289** rows (compared as bags, and against sqlite in `test_joins.py`):

| algorithm | work counted |
|---|---|
| nested loop | 5400 comparisons ($60 \cdot 90$) |
| block NL, $M = 4$ | 5400 comparisons, **33** pages: $6 + \lceil 6/2 \rceil \cdot 9$ |
| index NL | 60 probes |
| sort-merge | 22 key comparisons in the merge (after sorting) |
| hash, $k = 4$ | 90 build tuples, 60 probes |

The merge compares keys, not tuples: $\le n_r + n_s$ comparisons plus the
output. Nested loops pay $n_r n_s$ whatever the result size.

## Pitfalls

- NLJ cost is $n_r b_s$, not $b_r b_s$: tuple-at-a-time rescans per **tuple**.
- In BNLJ, the chunk has $M - 2$ pages, not $M$.
- Merge join with many duplicates of one value degenerates towards a nested loop on that group.
- Hash join and merge join need an equality predicate; $r.a < s.b$ needs (block) nested loop.
- Output cost is not in these formulas; it is the same for every algorithm.

## Exam-style questions

1. *$b_r = 50$, $b_s = 200$, $M = 52$. BNLJ with $r$ outer?* $r$ fits in 50 = $M - 2$ pages: **250**.
2. *True or false: NLJ cost with `student` outer is lower than with `takes` outer.* **False**: 2,000,100 vs 1,000,400 [S6].
3. *Hash join of 100 and 400 pages without recursive partitioning?* **1500** [S6].
4. *Which algorithms can compute $r \bowtie_{r.a < s.b} s$?* **Nested loop and block nested loop** only.
5. *True or false: sort-merge join costs $b_r + b_s$ even if neither input is sorted.* **False**: add both sort costs.

## Code

`src/py/joins.py`: `joins.nested_loop`, `joins.block_nested_loop`,
`joins.index_nested_loop`, `joins.sort_merge`, `joins.hash_join`, and the
formulas `joins.cost_nlj`, `joins.cost_bnlj`, `joins.cost_merge`,
`joins.cost_hash`; `test_joins.py::test_silberschatz_numbers` reproduces the
[S6] numbers.
