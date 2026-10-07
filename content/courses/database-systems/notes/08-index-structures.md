# 08 Index structures and their effect on plans

> **Sourcing.** [S6] ch. 14 (index terminology, B+ tree definition, occupancy,
> split procedure, height bound, bitmap indexes, extendible hashing); origins
> Bayer-McCreight [S13] and Fagin et al. [S15] (neither read); [S21] eqp.html
> and queryplanner.html for how sqlite reports and uses indexes. All traces are
> output of `bplustree.py`, `hashing.py`, `sql_lab.index_demo` and pinned by tests.

## Terminology [S6]

| term | meaning |
|---|---|
| search key | attribute(s) the index is built on (not necessarily a key) |
| clustering (primary) index | file sorted on the index's search key; at most one per table |
| non-clustering (secondary) index | entries point to records in arbitrary order; one page fetch per matching record in the worst case |
| dense / sparse | an entry per search-key value / per page (sparse needs a clustering order) |
| multilevel | an index on the index; a B+ tree is the balanced, self-maintaining version |

## B+ trees

Convention of [S6]: **$n$ = maximum number of pointers per node** (fan-out).

| node | keys | pointers |
|---|---|---|
| leaf (not root) | $\lceil (n-1)/2 \rceil$ to $n-1$ | one per key to the record (or the record itself) + next-leaf pointer |
| inner (not root) | one fewer than pointers | $\lceil n/2 \rceil$ to $n$ children |
| root | at least 1 | at least 2 children unless it is a leaf |

Inner node $P_1, K_1, P_2, \dots, K_{m-1}, P_m$: subtree $P_i$ holds keys
$K_{i-1} \le k < K_i$. All leaves are on the same level; the leaves form a
sorted linked list.

**Height.** A tree with $K$ keys has at most $\lceil \log_{\lceil n/2\rceil} K \rceil$
levels [S6]; at least $\lceil \log_n (K/(n-1)) \rceil + 1$ (full nodes). A
point search reads one node per level; a range search descends once and then
follows the leaf chain.

For $n = 100$ and $K = 10^6$: upper bound $\lceil \log_{50} 10^6 \rceil = \lceil 3.53\rceil = 4$;
three levels hold at most $100 \cdot 100 \cdot 99 = 990{,}000 < 10^6$ keys, so
the height is **exactly 4** whatever the insertion order. `bplustree.py` builds
it with sequential inserts and gets height 4.

**Insertion** [S6]: find the leaf; insert in order; if it now holds $n$ keys,
split: the first $\lceil n/2 \rceil$ keys stay, the rest go to a new right
sibling, and the sibling's **first key is copied** into the parent. If the parent
now has $n + 1$ pointers, split it: the first $\lceil (n+1)/2 \rceil$ pointers
stay, the key between the halves **moves** up (it is not kept in either half).
A root split adds a level: the only way the tree grows in height.

**Deletion** (not implemented here): remove from the leaf; on underflow borrow
from a sibling (redistribute) or merge with it and delete the separator from
the parent, recursively [S6].

### Worked trace, $n = 4$ (leaves hold at most 3 keys)

Insert 10 20 5 6 12 30 7 17 3 25 27 8:

| insert | event | tree afterwards |
|---|---|---|
| 10, 20, 5 | fill leaf | `[5 10 20]` |
| 6 | leaf `[5 6 10 20]` splits 2 / 2, copy up 10 | `[10]` / `[5 6] [10 20]` |
| 12, then 30 | `[10 12 20 30]` splits, copy up 20 | `[10 20]` / `[5 6] [10 12] [20 30]` |
| 7, 17, 3 | `[3 5 6 7]` splits, copy up 6 | `[6 10 20]` / `[3 5] [6 7] [10 12 17] [20 30]` |
| 25, 27 | `[20 25 27 30]` splits, copy up 27; root `[6 10 20 27]` has 5 pointers: keep 3, **move up 20** | `[20]` / `[6 10] [27]` / `[3 5] [6 7] [10 12 17] [20 25] [27 30]` |
| 8 | fits | leaf `[6 7 8]` |

Final: height 3, five splits (four leaf, one inner), five leaves. Search 17:
root (17 < 20) then `[6 10]` (17 ≥ 10, third child) then leaf: **3 node reads**.
Range $[7, 20]$: 3 reads to the first leaf, then 2 leaf hops, returns
7 8 10 12 17 20 (`test_bplustree.py::test_demo_tree_shape`).

**Other conventions.** Some texts define a B-tree "of degree $k$" in which every
non-root node holds between $k$ and $2k$ entries; [S7] is commonly cited for this
convention (not checked here). Convert before comparing: degree $k$ corresponds
roughly to $n = 2k + 1$ pointers. Do the exercise in the course's convention.

## Hash indexes

**Static hashing**: $B$ buckets, bucket $h(k) \bmod B$, overflow chains when a
bucket is full; equality search 1 page plus overflow; **no range queries**.
**Extendible hashing** [S15], [S6]: a directory of $2^G$ pointers indexed by
$G$ bits of $h(k)$ (global depth); each bucket has a local depth $d \le G$ and is
shared by $2^{G-d}$ directory entries. On overflow: if $d < G$, split the bucket
and repoint half its entries; if $d = G$, double the directory first.

Worked (`hashing.py` demo): capacity 2, $h(k) = k$, the **low-order** bits
([S6] uses high-order bits of a 32-bit hash; the mechanics are the same):

| insert | binary | event | $G$ |
|---|---|---|---|
| 1, 4 | 001, 100 | one bucket | 0 |
| 5 | 101 | overflow, $d = G$: double, split on bit 0: {4} / {1, 5} | 1 |
| 7 | 111 | {1, 5} full, $d = G$: double, split on bit 1: {1, 5} stays (both have bit 1 = 0), 7 goes to 11 | 2 |
| 10 | 1010 | into {4} (entries 00 and 10 still share it, $d = 1$) | 2 |
| 12 | 1100 | {4, 10} full, $d = 1 < G$: split without doubling on bit 1: {4, 12} at 00, {10} at 10 | 2 |
| 13 | 1101 | {1, 5} full, $d = G$: double, split on bit 2: {1} at 001, {5, 13} at 101 | 3 |

Result: $G = 3$, 5 buckets, 8 directory entries (`test_hashing.py::test_demo_trace`).

**Bitmap index** [S6]: one bit vector per distinct value; predicates become
bitwise AND/OR/NOT, counts a popcount. Size = (distinct values) × (rows) bits:
worthwhile for low-cardinality columns. Demo: `gender = 'f' AND level IN ('MSc', 'PhD')`
over 8 rows is `00100100` (rows 2, 5).

## Effect on plans

Clustered vs non-clustered for a range selecting a fraction $s$ of $n$ records
on $b = n/\mathit{bf}$ pages, tree height $h$:

$$C_{\text{clustered}} \approx h + s\,b,\qquad C_{\text{non-clustered}} \approx h + s\,n \ (\text{one page per record}),\qquad C_{\text{scan}} = b.$$

The non-clustered index beats a scan only while $s\,n < b$, i.e.
$s < 1/\mathit{bf}$. With $\mathit{bf} = 40$ (note 07): **below 2.5 %**. This is
why an optimiser ignores an index for unselective predicates.

What sqlite does with the lab database (`sql_lab.index_demo`, [S21] eqp.html:
SCAN = full scan, SEARCH = index lookup):

| query | plan |
|---|---|
| `exam WHERE cid = 'DBS'`, no index | `SCAN exam` |
| same, after `CREATE INDEX ix_exam_cid ON exam(cid)` | `SEARCH exam USING INDEX ix_exam_cid (cid=?)` |
| `exam WHERE sid = 101` | `SEARCH ... sqlite_autoindex_exam_1 (sid=?)`: the PK index on $(sid, cid, attempt)$ serves its **leftmost prefix** |
| `exam WHERE attempt = 2` | `SCAN exam`: `attempt` is not a prefix of that index |
| `student JOIN exam ... WHERE e.cid = 'DBS'` | index search on `e`, then primary-key lookups on `s` (an index nested-loop join, note 09) |

## Pitfalls

- Leaf splits **copy** the separator up; inner splits **move** it up.
- Count occupancy in the course's convention (pointers vs keys vs "degree").
- Height bound uses $\lceil n/2 \rceil$, the minimum fan-out, not $n$.
- Hash indexes do not support ranges or prefix searches.
- An extendible-hashing split may not resolve the overflow (all keys agree on
  the next bit): split again, possibly doubling again.
- A composite index $(a, b)$ helps predicates on $a$ or $(a, b)$, not on $b$ alone.

## Exam-style questions

1. *True or false: in a B+ tree all leaves are at the same depth.* **True** [S6].
2. *$n = 4$, keys 1, 2, 3 in one leaf; insert 4. Result?* **Root `[3]`, leaves `[1 2]` `[3 4]`** (`test_first_split_n4`).
3. *$n = 100$, $10^6$ keys. Can the tree have 3 levels?* **No**: at most 990,000 keys fit in 3 levels.
4. *Extendible hashing: a bucket with local depth 2 overflows while the global depth is 3. Does the directory double?* **No**; only the bucket splits.
5. *Non-clustered index, 1 % selectivity, 40 records per page, $10^6$ records. Index or scan?*
   Index $\approx h + 10^4$ page reads, scan $25{,}000$: **index** (1 % < 2.5 %). At 5 %: **scan**.

## Code

`src/py/bplustree.py`: `bplustree.BPlusTree` (`insert`, `search`, `range`,
`check` for every invariant, `dump`, `accesses`), `bplustree.max_height`.
`src/py/hashing.py`: `hashing.ExtendibleHash`, `hashing.BitmapIndex`.
`src/py/sql_lab.py`: `sql_lab.index_demo`, `sql_lab.query_plan`.
