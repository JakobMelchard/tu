# 12 Derived datatypes

Block 3, **day 3, 12:15** [S13]. Lab `07_derived-datatypes` (`derived-struct`)
[S11]. Code: [`src/c/derived_types.c`](../src/c/derived_types.c), plus the
`MPI_Type_vector` column exchange in
[`src/c/collectives.c`](../src/c/collectives.c). Semantics from MPI 5.0 §5
[S15].

## The problem

Every MPI call describes memory as `(address, count, datatype)`. That works for
a contiguous block of one type. It does not describe a column of a row-major
matrix, a face of a 3D array, or a `struct` with mixed members and compiler
padding. Without derived datatypes you copy such data into a contiguous buffer
by hand, send it, and copy it out — two copies and a temporary buffer per
message.

A **derived datatype** is a *type map*: a list of `(basic type, byte
displacement)` pairs [S15]. Handing one to `MPI_Send` tells the library where
the pieces are, so it gathers and scatters them itself, possibly without ever
materialising the contiguous buffer.

## Three numbers that describe a datatype

These are the ones that bite, so state them before the constructors [S15]:

- **size** — the number of bytes actually transferred
  (`MPI_Type_size`). For a column of 4 doubles, 32.
- **extent** — the span from the lowest to the highest byte touched, including
  holes and alignment padding (`MPI_Type_get_extent` returns extent *and* lower
  bound). For that column with a row stride of 4 doubles, the extent is
  $(4-1)\times 32 + 8 = 104$ bytes, not 32.
- **lower bound** — where the type "starts" relative to the buffer address.

The extent, not the size, is the stride MPI uses when `count > 1`. That single
sentence explains every surprise in this note.

## The constructors

```c
MPI_Type_contiguous(count, oldtype, &newtype);
/*   count copies, back to back                                                */

MPI_Type_vector(count, blocklength, stride, oldtype, &newtype);
/*   count blocks of blocklength elements, every stride ELEMENTS               */

MPI_Type_create_hvector(count, blocklength, stride_bytes, oldtype, &newtype);
/*   same, but stride in BYTES                                                 */

MPI_Type_indexed(count, blocklengths[], displacements[], oldtype, &newtype);
/*   irregular blocks, displacements in ELEMENTS (_create_hindexed: bytes)     */

MPI_Type_create_subarray(ndims, sizes[], subsizes[], starts[],
                         MPI_ORDER_C, oldtype, &newtype);
/*   a rectangular block of an n-D array: THE tool for 2D/3D halo faces        */

MPI_Type_create_struct(count, blocklengths[], displacements[], types[], &newtype);
/*   mixed types; displacements in bytes, from offsetof()                      */

MPI_Type_create_resized(oldtype, lb, extent, &newtype);
/*   change the extent (and lower bound) without changing what is sent         */

MPI_Type_commit(&newtype);     /* REQUIRED before any communication call       */
MPI_Type_free(&newtype);       /* when done; committed types are a resource    */
```

`MPI_Type_commit` lets the implementation compile the type map into something
efficient; using an uncommitted type is an error [S15]. Types built from
committed types do not inherit the commit — commit the one you actually send.

## Worked example 1: a column of a row-major matrix

A $4\times4$ `double` matrix `A`, stored row-major. Row 2 is contiguous; column
2 has a stride of 4 doubles.

```c
MPI_Datatype col;
MPI_Type_vector(4 /* count: rows */, 1 /* blocklength */, 4 /* stride in elements */,
                MPI_DOUBLE, &col);
MPI_Type_commit(&col);
MPI_Send(&A[0][2], 1, col, dest, 0, MPI_COMM_WORLD);   /* start at the top of column 2 */
```

The receiver may take it as 4 contiguous doubles (`MPI_Recv(buf, 4, MPI_DOUBLE,
…)`) — **the type signatures must match, the type maps need not** [S15]. This is
the single most useful property of derived types and the reason a "pack on the
sender, unpack on the receiver" design is usually unnecessary.

`MPI_Type_size(col)` is $4\times 8 = 32$ bytes; `MPI_Type_get_extent(col)` is
$104$ bytes. So `MPI_Send(&A[0][2], 2, col, …)` does **not** send columns 2 and
3: it advances by 104 bytes, landing in the middle of nowhere. To send several
adjacent columns, resize first:

```c
MPI_Type_create_resized(col, 0, sizeof(double), &col2);   /* extent = one element */
MPI_Type_commit(&col2);
MPI_Send(&A[0][2], 2, col2, dest, 0, MPI_COMM_WORLD);     /* now columns 2 and 3 */
```

`derived_types.c` asserts both the size and the extent, and checks that the
resized version really moves two columns.

## Worked example 2: a struct

```c
typedef struct { int id; double x[3]; char tag; } Particle;

int          blen[3]  = {1, 3, 1};
MPI_Aint     disp[3];
MPI_Datatype typ[3]   = {MPI_INT, MPI_DOUBLE, MPI_CHAR};
Particle     probe;
MPI_Aint     base;

MPI_Get_address(&probe,      &base);
MPI_Get_address(&probe.id,   &disp[0]);
MPI_Get_address(&probe.x,    &disp[1]);
MPI_Get_address(&probe.tag,  &disp[2]);
for (int i = 0; i < 3; i++) disp[i] -= base;      /* relative to the struct start */

MPI_Datatype raw, ptype;
MPI_Type_create_struct(3, blen, disp, typ, &raw);
MPI_Type_create_resized(raw, 0, sizeof(Particle), &ptype);   /* so count>1 works */
MPI_Type_commit(&ptype);
MPI_Send(particles, n, ptype, dest, 0, comm);                /* an array of them  */
```

Two things are doing real work here. `MPI_Get_address` (never `offsetof` on a
`char*` cast, never hand-counted byte offsets) gets the displacements the
compiler actually chose, padding included. And `MPI_Type_create_resized` to
`sizeof(Particle)` is what makes `count = n` walk the array correctly: without
it the extent ends at the last member, and the trailing padding is skipped
[S15]. That is the `07_derived-datatypes` lab's lesson.

## Worked example 3: a 3D halo face

```c
int sizes[3]    = {nx + 2, ny + 2, nz + 2};   /* the array including ghost layers */
int subsizes[3] = {1, ny, nz};                /* one x-slab of the interior       */
int starts[3]   = {1, 1, 1};                  /* first interior cell              */
MPI_Type_create_subarray(3, sizes, subsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &xface);
MPI_Type_commit(&xface);
```

One type per face per direction, then one `MPI_Sendrecv` per direction, on the
Cartesian communicator of [11](11-virtual-topologies.md). No packing code at
all, and `MPI_ORDER_FORTRAN` handles the other storage order.

## When *not* to use a derived datatype

Derived types are not free: the library walks the type map, and for a strided
type with tiny blocks it may end up doing the same copy you would have written,
with worse cache behaviour. Rules of thumb:

- Contiguous data: just use `count` and the basic type.
- Large blocks, few of them: derived types win (zero copies on RDMA hardware).
- Thousands of single-element blocks: measure against `MPI_Pack` /
  `MPI_Unpack`, which lets you build one contiguous buffer explicitly [S15].
- Whatever you choose, **fewer and larger messages beat clever types** — the
  lecturer's best-practice deck reduces to "aggregate communication into longer
  messages" [S14].

Derived types are also the portable answer to **heterogeneity**: because the
type map is described in terms of MPI basic types rather than bytes, MPI can
convert representations between unlike nodes. `MPI_BYTE` cannot [S15].

## Pitfalls

- **Forgetting `MPI_Type_commit`.** Error at the first send, and the message
  points at the communication call, not the construction.
- **`count > 1` with an unresized strided or struct type.** Silently sends the
  wrong bytes. Check `MPI_Type_get_extent` against what you expect; the fix is
  `MPI_Type_create_resized`.
- Confusing `MPI_Type_size` (bytes moved) with extent (stride). Both are
  useful; they are rarely equal.
- Hand-computing struct offsets instead of `MPI_Get_address`: works until a
  compiler flag changes the padding.
- `MPI_Type_vector` stride in **elements**, `MPI_Type_create_hvector` in
  **bytes**. Same for `indexed` / `hindexed`.
- Never freeing types built inside a time loop.
- Sending a `struct` containing a pointer. The address is meaningless on the
  receiving rank — this is not serialisation.
- Assuming the sender's and receiver's type maps must be the same. Only the
  *type signature* (the sequence of basic types) must match [S15].

## Questions

Our questions — this course has no exam and no past papers
([00](00-exam-focus.md)). Q2 and Q3 are the `07_derived-datatypes` lab in words
[S11].

1. **Send row 3, then column 3, of a $100\times100$ row-major `double` matrix.
   Which needs a derived type?** The row is contiguous:
   `MPI_Send(&A[3][0], 100, MPI_DOUBLE, …)`. The column needs
   `MPI_Type_vector(100, 1, 100, MPI_DOUBLE, &col)`, commit, then send **1**
   element of `col` starting at `&A[0][3]`.
2. **Build a datatype for `struct {int id; double x[3]; char tag;}` so that
   `MPI_Send(arr, n, type, …)` sends `n` of them. Which two calls are
   essential?** `MPI_Get_address` for the displacements (the compiler's padding,
   not yours) and `MPI_Type_create_resized(raw, 0, sizeof(Particle), &type)` so
   that the extent equals the array stride [S15].
3. **`MPI_Type_size` says 32 and `MPI_Type_get_extent` says 104 for the same
   type. Explain, and say what breaks.** 32 bytes are transferred; the type
   spans 104 bytes of memory because of the stride. Nothing breaks for
   `count = 1`; for `count = 2` the second copy starts 104 bytes on, which is
   almost never what you want. Resize [S15].
4. **The sender uses a strided type of 4 doubles; the receiver posts
   `MPI_Recv(buf, 4, MPI_DOUBLE, …)`. Legal?** Yes. Type *signatures* must
   match — four doubles either way — type maps need not [S15].
5. **Why is `MPI_Type_create_subarray` the right tool for a 3D halo face rather
   than a nested `MPI_Type_vector`?** It takes the full array shape, the
   sub-block shape and the offset directly, handles C and Fortran ordering, and
   removes the extent bookkeeping that nesting vectors requires.
6. **When would you prefer `MPI_Pack` over a derived datatype?** When the layout
   is highly irregular with very small blocks, or when you need one buffer you
   can also write to a file or compress. Measure; for large regular blocks the
   derived type avoids a copy entirely.
