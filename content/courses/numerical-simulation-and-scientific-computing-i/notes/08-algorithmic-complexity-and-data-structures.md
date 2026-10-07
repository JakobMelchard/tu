# 08 Algorithmic complexity and data structures

Asymptotic cost decides feasibility; constants and memory layout decide the wall clock. Both matter for meshes and sparse matrices.

The complexity column of the container table is **normative**, not folklore: the C++ standard states each container's complexity requirements as part of the container requirements [S14], so an implementation that misses them is non-conforming. The measured columns are from `src/cpp/containers_bench.cpp` on this machine [S34]; they are the part that varies.

## Big-O

$f(n) = O(g(n))$ if $f(n) \le c\,g(n)$ for all $n \ge n_0$ (upper bound); $\Omega$ lower bound; $\Theta$ both. Common classes and what $n = 10^6$ costs at $10^9$ ops/s:

| class | example | $n = 10^6$ |
|---|---|---|
| $O(1)$ | array index, hash lookup (average) | ns |
| $O(\log n)$ | binary search, balanced tree | 20 ns |
| $O(n)$ | scan, SpMV, Thomas algorithm | 1 ms |
| $O(n \log n)$ | sort, FFT | 20 ms |
| $O(n^2)$ | dense matvec, naive pair search | 17 min |
| $O(n^3)$ | dense LU, matmul | 30 years |
| $O(2^n)$ | subset enumeration | never |

**Amortised** cost: `vector::push_back` is required to be **amortised constant** [S14]; implementations get that by growing capacity geometrically, so a single push may copy $n$ elements but $n$ pushes cost $O(n)$ total. (The standard mandates the amortised bound, not the growth factor: libstdc++ doubles, libc++ doubles, MSVC uses 1.5.) **Recurrences**: mergesort $T(n) = 2T(n/2) + n \Rightarrow \Theta(n \log n)$; binary search $T(n) = T(n/2) + 1 \Rightarrow \Theta(\log n)$; Strassen $T = 7T(n/2) + n^2 \Rightarrow n^{2.81}$ (master theorem). **Space complexity** counts memory the same way; for PDE codes it is often the binding constraint (note 05).

Big-O hides constants and the memory hierarchy. A hash lookup is $O(1)$ but a cache miss; a sorted-vector binary search is $O(\log n)$ but its top levels are always in cache. Measured (`./bin/containers_bench --test`, three runs, 2026-09-27), $n = 10^5$ ints, $10^5$ lookups with 50% misses: `std::map` 6.2-7.0 ms, sorted vector + `lower_bound` 4.3-4.4 ms, `unordered_map` 0.8-0.9 ms.

## STL containers

Complexity columns from the C++ standard's container requirements [S14]; "layout" and "use for" are ours.

| container | layout | access | insert/erase | find | use for |
|---|---|---|---|---|---|
| `std::array<T,N>` | fixed, on stack | $O(1)$ | - | - | small fixed tuples (coordinates, stencils) |
| `std::vector<T>` | contiguous, heap | $O(1)$ | end $O(1)$ amortised; middle $O(n)$ | $O(n)$, $O(\log n)$ if sorted | the default for everything |
| `std::deque<T>` | blocks | $O(1)$ | both ends $O(1)$; middle $O(n)$ | $O(n)$ | queues, BFS frontier |
| `std::list<T>` | doubly linked nodes | $O(n)$ | $O(1)$ *given an iterator* | $O(n)$ | almost never (pointer chasing, 3 pointers per element) |
| `std::map<K,V>` / `set` | red-black tree | $O(\log n)$ | $O(\log n)$ | $O(\log n)$, ordered iteration | sorted keys, range queries |
| `std::unordered_map` / `set` | hash table, chained buckets | $O(1)$ avg, $O(n)$ worst | $O(1)$ avg, $O(n)$ worst | $O(1)$ avg, unordered | lookups by id, deduplication |
| `std::priority_queue` | binary heap in a vector | top $O(1)$ | push/pop $O(\log n)$ | - | Dijkstra, event queues, adaptive refinement |

Iterator invalidation [S14]: `vector` insert/erase invalidates every iterator and pointer **if reallocation happens**, and everything from the insertion point onward otherwise; `list`, `map` and `unordered_map` keep references to elements valid across insertion (`unordered_map` invalidates *iterators* on rehash but not references). `vector<bool>` is a bit-packed special case without real references. Reserve capacity (`v.reserve(n)`) when the size is known: avoids the doubling copies and pointer invalidation.

`./bin/containers_bench --test` numbers ($n = 10^5$, three runs): `push_back` vector 0.3 ms, list 1.2-1.3 ms; middle insertion of 1000 elements: vector 3.6 ms ($O(n)$ memmove each, but 50 KB memmove is fast), list below the table's 0.1 ms resolution *if you already hold the iterator* and 60-61 ms if you have to walk to the middle each time. The very first run after a build read 0.5 ms and 8.8 ms for the two vector rows; repeat runs agree to about 10 %, so discard the first. The $O(1)$ list insertion is only real when the position is known.

## Data structures for meshes

Structured grid: no connectivity storage, neighbours by index arithmetic `idx(i,j) = i*(N+1) + j`; a field is one flat `vector<double>`. Never `vector<vector<double>>`: rows are separate allocations, no contiguity, no blocking.

Unstructured mesh (note 09), the minimal representation:

```cpp
std::vector<std::array<double,3>> nodes;      // node id -> coordinates
std::vector<std::array<int,3>>    triangles;  // element id -> 3 node ids (counter-clockwise)
std::vector<int>                  boundary;   // tags per boundary edge or node
```
Queries you will need and their structures:
- node -> elements around it (for assembly, smoothing): CSR-style adjacency, built in $O(n_{el})$ by counting then filling: `offset[n+1]`, `elems[...]`. Not `vector<vector<int>>` (one allocation per node) and not `multimap`.
- element -> neighbouring elements across each edge (flux computations): sort all edges as `(min, max, elem)` triples, $O(n \log n)$, or hash `pair<int,int>` -> element, $O(n)$ average.
- point location (which element contains $x$?): uniform bucket grid or k-d tree, $O(\log n)$ per query, instead of $O(n)$ scan.
- Node numbering matters: reverse Cuthill-McKee reordering reduces the matrix bandwidth and improves cache behaviour of SpMV.

## Data structures for sparse matrices

Assembly phase: entries arrive in random order and duplicates must be summed. Options: (a) `std::vector` of COO triplets, then sort by (row, col) $O(\text{nnz} \log \text{nnz})$ and merge duplicates, then convert to CSR by counting rows $O(\text{nnz} + n)$; (b) `std::unordered_map<int64,double>` keyed by `row*n + col`, then sort; (c) if the sparsity pattern is known (stencil, mesh adjacency), preallocate CSR and add into positions found by binary search in the row. Solve phase: CSR (note 05). Never a `std::map<std::pair<int,int>,double>` in the inner solve loop: $O(\log \text{nnz})$ and a cache miss per coefficient.

## Worked example: choosing for a particle-in-cell step

$10^6$ particles must find the grid cell they fall in and be summed into cell densities. Cells: flat `vector<double>` indexed by `(int)(x/h)`: $O(1)$, contiguous. Particles: struct-of-arrays (`vector<double> x, y, vx, vy`) rather than array-of-structs when loops touch one component at a time (SIMD, cache lines fully used). Sorting the particles by cell every few steps ($O(n \log n)$, or counting sort $O(n)$) makes the deposition sequential in memory: the sort pays for itself many times over. A `map<cell, vector<particle>>` would cost a tree lookup and an allocation per particle.

## Pitfalls

- `v.insert(v.begin(), x)` in a loop: $O(n^2)$; build then reverse, or use a deque.
- `std::endl` (flush) on every line of a large output file: use `'\n'`.
- `std::list` because "insertion is O(1)": measure it; almost always slower than vector for elements under ~100 bytes.
- `unordered_map` with a bad hash for `pair<int,int>` (many collisions -> $O(n)$).
- Passing large containers by value; returning by value is fine (move semantics).
- Signed/unsigned: `for (size_t i = n-1; i >= 0; --i)` never terminates.
- Recursion depth: a recursive tree traversal on $10^7$ nodes overflows the stack; use an explicit stack.

## Exam-style questions

1. **A loop calls `v.erase(v.begin())` $n$ times on a vector of $n$ elements. Complexity? Faster alternative?** Each erase shifts the remaining elements: $O(n^2)$ total. Use `std::deque::pop_front` ($O(1)$), an index into the vector, or `std::remove_if` + one erase ($O(n)$).
2. **Compare `std::map` and `std::unordered_map` for storing sparse-matrix entries during assembly; when do you convert to CSR?** Both give $O(\log n)$ / $O(1)$ insertion with duplicate summing; `map` iterates in sorted order (directly convertible to CSR), `unordered_map` needs a sort. Convert as soon as assembly ends: the solve phase needs $O(\text{nnz})$ SpMV with contiguous memory, which neither map provides.
3. **Why is a linked list slow to traverse even though traversal is $O(n)$, the same as a vector?** Each node is a separate heap allocation reached through a pointer; the next address is unknown until the current node is loaded, so the prefetcher cannot help and every node can be a cache miss (~90 ns) versus 0.3 ns per contiguous element.
4. **Give a data structure and complexity for "all elements sharing node $i$" queries on a mesh with $n$ nodes and $m$ elements.** CSR-style adjacency: `offset[n+1]` and `elems[3m]` (triangles), built in $O(m)$ by counting occurrences per node and filling; query $O(\deg i)$, typically 6. Memory $12m + 4n$ bytes.
5. **Explain amortised $O(1)$ for `push_back`.** Capacity doubles on overflow; the copies over $n$ pushes sum to $1 + 2 + 4 + \dots + n < 2n$, so the total is $O(n)$ and the average per push is $O(1)$ even though individual pushes cost $O(n)$.

Code: `src/cpp/containers_bench.cpp`; CSR construction in `src/cpp/csr.cpp` (`poisson2d`), mesh arrays in `src/cpp/vtk_writer.cpp` (`square_triangles`), mesh connectivity in `src/py/delaunay.py`. Sources: [S14] [S22] [S34] [S35].
