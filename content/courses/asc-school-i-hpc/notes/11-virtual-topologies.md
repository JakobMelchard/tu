# 11 Virtual topologies

Block 3, **day 3, 10:15** [S13]. Lab `06_virtual_cartesian_topologies`
(`cart-create`, `cart-shift`) [S11]. Code:
[`src/c/cart_topology.c`](../src/c/cart_topology.c). Semantics from MPI 5.0 §8
[S15].

## What a virtual topology is, and what it is not

A **virtual topology** attaches a communication *graph* to a communicator: it
says which ranks talk to which. It is virtual because it describes your
algorithm, not the machine. MPI may (and is allowed to) use it to renumber ranks
so that neighbours in your graph land on nearby hardware — that is what the
`reorder` flag asks for — but it is never required to, and on a flat fat tree
there is usually nothing to gain [S15].

So the real payoff is not performance. It is that **MPI computes your neighbour
ranks for you, correctly, including at the edges**, and the off-by-one arithmetic
that eats an afternoon of every hand-written stencil code disappears.

## Cartesian topologies

```c
int dims[2]    = {0, 0};        /* 0 = "you choose" */
int periods[2] = {1, 0};        /* wrap around in dim 0, hard boundary in dim 1 */
int reorder    = 1;

MPI_Dims_create(size, 2, dims);                 /* fills the zeros: a balanced factorisation */
MPI_Cart_create(MPI_COMM_WORLD, 2, dims, periods, reorder, &cart);
if (cart == MPI_COMM_NULL) { /* more ranks than grid points: this one is unused */ }

int my_rank, coords[2];
MPI_Comm_rank(cart, &my_rank);                  /* MAY differ from the world rank if reorder */
MPI_Cart_coords(cart, my_rank, 2, coords);      /* rank  -> (i, j) */
MPI_Cart_rank(cart, coords, &r);                /* (i, j) -> rank  */
```

`MPI_Dims_create(nnodes, ndims, dims)` fills any zero entries with a balanced
factorisation of `nnodes` — for 12 ranks in 2D it gives $4\times3$ [S15]. Fix a
dimension by passing a non-zero value.

`MPI_Cart_create` is **collective over the old communicator**, and if the
product of `dims` is smaller than `size` the surplus processes get
`MPI_COMM_NULL` and must not use it.

### `MPI_Cart_shift` — the reason to bother

```c
int left, right;
MPI_Cart_shift(cart, 0 /* direction */, 1 /* displacement */, &left, &right);
```

Returns the rank you would *receive from* (`left`, the source) and the rank you
would *send to* (`right`, the destination) if every process shifted its data by
`+1` along dimension 0 [S15]. The argument order is *source first, destination
second*, which is the opposite of the reading order of "left, right" and is
worth writing down.

Two properties make it worth using instead of `(rank+1) % size`:

- **Periodic dimensions wrap**, non-periodic ones return **`MPI_PROC_NULL`** at
  the edges. `MPI_PROC_NULL` in a send or receive is a no-op that succeeds
  [S15], so the *same* `MPI_Sendrecv` line works for interior and boundary
  processes and the `if (rank == 0)` special case vanishes.
- A negative displacement gives the other direction; `MPI_Cart_shift(cart, d,
  -1, &s, &d)` is the mirror image.

The canonical halo exchange is then one line per dimension, with no branches:

```c
for (int d = 0; d < ndims; d++) {
    int src, dst;
    MPI_Cart_shift(cart, d, 1, &src, &dst);
    MPI_Sendrecv(&send_hi[d], 1, face[d], dst, 100 + d,
                 &recv_lo[d], 1, face[d], src, 100 + d, cart, MPI_STATUS_IGNORE);
    MPI_Cart_shift(cart, d, -1, &src, &dst);
    MPI_Sendrecv(&send_lo[d], 1, face[d], dst, 200 + d,
                 &recv_hi[d], 1, face[d], src, 200 + d, cart, MPI_STATUS_IGNORE);
}
```

with `face[d]` a derived datatype describing the non-contiguous face
([12](12-derived-datatypes.md)).

### `MPI_Cart_sub`

```c
int keep[2] = {0, 1};                     /* keep dimension 1 */
MPI_Cart_sub(cart, keep, &row_comm);      /* one communicator per row, still Cartesian */
```

The topology-aware version of `MPI_Comm_split`
([10](10-groups-and-communicators.md)) — the standard way to get row and column
communicators out of a 2D grid for matrix algorithms [S15].

## The course's version: a 1D ring

The `06_virtual_cartesian_topologies` lab rewrites the ring of
[08](08-point-to-point.md) on a Cartesian communicator [S11]:

```c
dims[0] = size; periods[0] = 1; reorder = 1;
MPI_Cart_create(MPI_COMM_WORLD, 1, dims, periods, reorder, &new_comm);
MPI_Comm_rank(new_comm, &my_rank);        /* NOTE: after the create, not before */
MPI_Cart_shift(new_comm, 0, 1, &left, &right);
/* ... the same Issend / Recv / Wait loop as before, on new_comm ... */
```

and the answer is still $\sum_{r=0}^{P-1} r = P(P-1)/2$ — 6 for $P=4$ — because
a ring is a ring however you number it [S11]. That invariance is the point of
the exercise: with `reorder = 1` the ranks may be permuted, every rank may print
a different rank number than it did yesterday, and the sum is unchanged.

## Graph topologies

For irregular neighbour relations (unstructured meshes, sparse matrices) MPI
offers a distributed graph: `MPI_Dist_graph_create_adjacent` (each process names
its own in- and out-neighbours — the scalable one) and
`MPI_Dist_graph_create` (any process may specify any edge), queried with
`MPI_Dist_graph_neighbors_count` and `MPI_Dist_graph_neighbors` [S15]. The older
`MPI_Graph_create`, in which every process passes the whole graph, is there for
compatibility and does not scale.

## Neighbourhood collectives

Any topology communicator — Cartesian or graph — supports
`MPI_Neighbor_allgather`, `MPI_Neighbor_alltoall` and their `v`/`w` and
non-blocking variants [S15]. One call replaces the whole halo-exchange loop
above: each process sends one buffer to each neighbour and receives one from
each, in the order `MPI_Cart_shift` / `MPI_Dist_graph_neighbors` defines. Worth
knowing about even if the course only mentions it: it hands the entire exchange
pattern to the library in one call, which is the only way the library can
optimise it as a whole.

## Pitfalls

- **Calling `MPI_Comm_rank` before `MPI_Cart_create` and reusing that number.**
  With `reorder = 1` the Cartesian rank may differ from the world rank. Query
  the new communicator [S11] [S15].
- Mixing up the two outputs of `MPI_Cart_shift`. It is `(source, destination)`.
  Writing `MPI_Cart_shift(c, 0, 1, &right, &left)` compiles and silently reverses
  your grid.
- Forgetting that a non-periodic edge returns `MPI_PROC_NULL` and adding an
  `if` to skip the call — harmless but pointless, and it reintroduces the bug
  the topology removed.
- `MPI_Dims_create` with all dimensions zero when `size` is prime: you get a
  $1 \times P$ grid, which is a slab decomposition with the worst
  surface-to-volume ratio ([16](16-best-practice-and-debugging.md)).
- Using the Cartesian communicator for some messages and `MPI_COMM_WORLD` for
  others with `reorder = 1`: the rank numbers do not agree.
- Assuming `reorder = 1` actually reorders. Most implementations ignore it; do
  not build correctness on it, and do not expect a speed-up from it.
- Not handling `MPI_COMM_NULL` when `dims` covers fewer processes than you have.

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q1–Q3 are what the `06_virtual_cartesian_topologies`
lab makes you notice [S11].

1. **Rewrite the ring on a 1D Cartesian communicator. What must `periods[0]` be,
   and what does the program print for $P = 4$?** `periods[0] = 1`, so the shift
   wraps; the sum is $P(P-1)/2 = 6$ on every rank, exactly as with hand-computed
   neighbours [S11].
2. **Your Cartesian version prints different rank numbers from run to run but
   the same sum. Bug?** No — `reorder = 1` permits MPI to renumber. The sum is
   invariant under a permutation of a ring, which is why the lab checks the sum
   and not the rank [S15].
3. **Why is `MPI_Cart_shift` better than `(rank+1) % size` even for a plain
   ring?** It encodes periodicity in one place, returns `MPI_PROC_NULL` (a legal
   no-op) rather than a wrong rank when the dimension is not periodic, and it
   keeps working unchanged when you go to 2D or 3D [S15].
4. **12 ranks, 2D grid, no dimension fixed. What does `MPI_Dims_create` give,
   and what if you want 2 in the first dimension?** $4\times3$; pass
   `dims = {2, 0}` and it fills $2\times6$ [S15].
5. **Write the two `MPI_Cart_shift` calls and the two `MPI_Sendrecv` calls for a
   full halo exchange in dimension $d$ of a 3D grid, with no `if` statements.**
   As in the loop above: `+1` gives (src, dst) for the "up" exchange, `-1` for
   the "down" one, and `MPI_PROC_NULL` handles the physical boundary.
6. **What would `MPI_Neighbor_alltoall` replace in that loop, and why might the
   library do better with it?** The whole loop. One call exposes the complete
   exchange pattern, so the implementation can schedule, aggregate or offload it
   as a unit instead of seeing $2d$ unrelated point-to-point pairs [S15].
