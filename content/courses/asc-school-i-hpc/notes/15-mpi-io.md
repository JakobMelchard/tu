# 15 MPI I/O (short tour)

Block 3, **day 4, 12:15**, explicitly a *"short tour"* with no lab [S13]. Code:
[`src/c/mpi_io.c`](../src/c/mpi_io.c). Sources: the lecturer's own overview deck
[S14] and MPI 5.0 §14 [S15]. Section numbers the deck cites are MPI-3.1 §13, the
same chapter.

## Why it exists

A parallel program that writes results by gathering everything to rank 0 and
calling `fwrite` has a serial bottleneck and a memory bottleneck. One that has
every rank write `out.<rank>` produces thousands of files that a parallel
filesystem hates ([04](04-cluster-anatomy.md)) and that post-processing has to
stitch back together. MPI I/O is the third option: **one file, written in
parallel, in the layout the data already has.**

The lecturer's framing is worth keeping [S14]: *writing and reading a file is
like sending and receiving a message*, and the machinery is the same machinery:

| I/O needs | MPI already has |
|---|---|
| collective operations | a **file handle**, defined like a communicator |
| groups of processes | communicators and topologies ([10](10-groups-and-communicators.md), [11](11-virtual-topologies.md)) |
| non-contiguous access | derived datatypes ([12](12-derived-datatypes.md)) |
| overlapping I/O with computation | non-blocking calls ([08](08-point-to-point.md)) |

MPI I/O sits under the high-level libraries: parallel HDF5, NetCDF-4 and
PNetCDF are implemented on top of it, and above a parallel filesystem [S14].
Unless you have a reason, use HDF5 and let it call MPI I/O for you; but knowing
the layer below is how you read its tuning knobs.

## Files and views

```c
MPI_File fh;
MPI_File_open(comm, "out.bin", MPI_MODE_CREATE | MPI_MODE_WRONLY, MPI_INFO_NULL, &fh);
...
MPI_File_close(&fh);
MPI_File_delete("out.bin", MPI_INFO_NULL);     /* local: call it on ONE process */
```

`MPI_File_open` is **collective over `comm`**; the filename and the access mode
must be identical on every process. `MPI_COMM_SELF` gives you a private,
process-local file. Access modes: exactly one of `MPI_MODE_RDONLY`,
`MPI_MODE_WRONLY`, `MPI_MODE_RDWR`, optionally OR'd with `MPI_MODE_CREATE`,
`_EXCL`, `_APPEND`, `_DELETE_ON_CLOSE`, `_UNIQUE_OPEN`, `_SEQUENTIAL` [S14]
[S15]. A file is a contiguous sequence of bytes: **binary only, no text I/O**.

The central concept is the **view** — which part of the file this process can
see. A view is a triple [S14] [S15]:

- **disp** — a byte displacement from the start of the file, i.e. how many
  header bytes to skip;
- **etype** — the *elementary datatype*, the unit of access and of positioning
  (offsets are counted in etypes, not bytes);
- **filetype** — a datatype, usually derived, that **tiles** the file: the
  pattern of etypes this process may touch, repeated to cover the file.

```c
MPI_File_set_view(fh, disp, etype, filetype, "native", MPI_INFO_NULL);
```

The default view is `(0, MPI_BYTE, MPI_BYTE)`: everybody sees everything. Give
each process a *different* filetype and the file is partitioned among them with
no offset arithmetic anywhere in your code — a single `MPI_File_write_all` then
writes an interleaved or blocked layout correctly. `MPI_File_set_view` is
collective, the data representation and the etype extent must agree on all
processes, and it resets all file pointers to zero [S14].

Data representations: `"native"` (raw memory image, fastest, not portable
between architectures), `"internal"` (implementation-defined, portable within
one implementation), `"external32"` (a defined portable format) [S15].

## The data-access calls

Four independent choices, which is why there appear to be so many routines
[S14] [S15]:

- **positioning** — explicit offsets (`_AT`), the process's own individual file
  pointer (nothing), or a file pointer shared by all processes (`_SHARED`
  non-collective, `_ORDERED` collective);
- **synchronism** — blocking, non-blocking (`I…`), or split-collective
  (`_BEGIN` / `_END`);
- **coordination** — non-collective, or collective (`_ALL`);
- **atomicity** — non-atomic by default; `MPI_File_set_atomicity` for sequential
  consistency.

|  | non-collective | collective | split collective |
|---|---|---|---|
| explicit offset, blocking | `MPI_File_read_at` / `write_at` | `…_at_all` | `…_at_all_begin` / `_end` |
| explicit offset, non-blocking | `MPI_File_iread_at` / `iwrite_at` | `…_iread_at_all` | — |
| individual pointer, blocking | `MPI_File_read` / `write` | `…_read_all` / `write_all` | `…_all_begin` / `_end` |
| individual pointer, non-blocking | `MPI_File_iread` / `iwrite` | `…_iread_all` | — |
| shared pointer, blocking | `MPI_File_read_shared` / `write_shared` | `…_read_ordered` / `write_ordered` | `…_ordered_begin` / `_end` |
| shared pointer, non-blocking | `MPI_File_iread_shared` | (none) | — |

Table after the lecturer's, itself after Rabenseifner's [S14]; the routine set
is normative in MPI 5.0 §14.4 [S15]. For orientation: **POSIX `read()` and
`write()` are the non-collective, blocking, individual-file-pointer cell** of
this table — one box out of eighteen.

Supporting calls: `MPI_File_seek(fh, offset, MPI_SEEK_SET|_CUR|_END)`,
`MPI_File_get_position`, `MPI_File_get_byte_offset`, and `MPI_File_sync`
(MPI I/O may be buffered) [S14].

## The one thing to take away: use the collective calls

`MPI_File_write_all` does exactly what $P$ separate `MPI_File_write` calls do.
The difference is that the library knows all $P$ requests at once and may merge
them — *"opportunity for best speed"*, as the slide puts it [S14]. This is
**two-phase I/O**: a subset of processes ("aggregators") each collect many small,
scattered requests into a few large contiguous filesystem operations, then
redistribute. On a striped parallel filesystem this is often the difference
between a few GB/s and a few tens of MB/s, and it is why "collective, with a
view" is the shape to reach for.

Non-blocking and split-collective calls exist for the same reason as
non-blocking messages: overlap the write with computation, or overlap a
start-up read with initialisation [S14].

## Two scenarios, from the lecture

**A — every process needs the whole file** [S14]: same view on all processes,
`MPI_File_read_all` with individual file pointers. Then improve it:
`MPI_File_iread_all` (or `MPI_File_read_all_begin`), do the rest of your
initialisation, `MPI_Wait` (or `…_read_all_end`).

**B — the file holds a matrix, block-partitioned one block per process**
[S14]: build a process topology ([11](11-virtual-topologies.md)), give each
process a filetype describing its block with `MPI_Type_create_subarray` or
`MPI_Type_create_darray` ([12](12-derived-datatypes.md)), set the view, then a
single `MPI_File_read_at_all` with offset 0. Every process reads exactly its
block, in one collective call, and the code contains no offset arithmetic at
all. This is the pattern; the other 90 % of MPI I/O is variations on it.

## Error handling differs from the rest of MPI

File handles have their own error handler, and its default is
**`MPI_ERRORS_RETURN`** — *non*-fatal — whereas communicators default to
`MPI_ERRORS_ARE_FATAL` [S14] [S15]. So an I/O error does not abort your job: it
returns a code you are expected to check, and if you do not, the program
continues with a file that was never written. The default is attached to
`MPI_FILE_NULL`, so change it once after `MPI_Init`:

```c
MPI_File_set_errhandler(MPI_FILE_NULL, MPI_ERRORS_ARE_FATAL);
```

or, better, check the return value of every `MPI_File_*` call and print it with
`MPI_Error_string`.

## Pitfalls

- **Ignoring return codes**, because of the non-fatal default above. This is the
  MPI I/O bug.
- Using `MPI_File_write` where `MPI_File_write_all` would do: you lose the
  collective optimisation entirely, and the call site looks identical.
- Writing text. There is no formatted I/O; a file is bytes.
- `"native"` data representation plus a heterogeneous or cross-architecture
  read. Use `"external32"` if the file has to travel.
- Calling `MPI_File_delete` on every rank (it is local, not collective) [S14].
- Forgetting that `MPI_File_set_view` resets the file pointers.
- One file per rank "because it is simpler": thousands of small files are the
  pattern parallel filesystems handle worst [S19].
- Rank 0 gathering the whole field every step so that it can write it — the I/O
  version of the serial bottleneck ([16](16-best-practice-and-debugging.md)).
- Reaching for MPI I/O when parallel HDF5 would do. It usually would.

## Questions

Our questions — this course has no exam and no past papers, and this session has
no lab either ([00](00-exam-focus.md)).

1. **What are the three components of a file view, and what does each do?**
   `disp` skips header bytes; `etype` is the unit of access and of offsets;
   `filetype` tiles the file and so partitions it among processes [S14] [S15].
2. **Which cell of the data-access table is `POSIX read()`?** Non-collective,
   blocking, individual file pointer [S14].
3. **Why would `MPI_File_write_all` be faster than the same writes done
   non-collectively?** The library sees all requests at once and can merge many
   small scattered accesses into few large contiguous ones (two-phase I/O)
   [S14].
4. **A file holds an $N\times N$ matrix and you want each process to read its
   own block in one call. Sketch it.** Cartesian topology → per-process
   `MPI_Type_create_subarray` filetype → `MPI_File_set_view(fh, 0, MPI_DOUBLE,
   block, "native", …)` → `MPI_File_read_at_all(fh, 0, buf, n, MPI_DOUBLE, …)`
   [S14].
5. **Your job finishes "successfully" and the output file is empty. Name the
   MPI I/O-specific reason to suspect first.** File-handle errors default to
   `MPI_ERRORS_RETURN`, so a failing `MPI_File_*` call returns a code instead of
   aborting; nobody checked it [S14] [S15].
6. **When should you not use MPI I/O directly?** When parallel HDF5 or NetCDF-4
   fits — they are built on it, add self-describing metadata, and are what other
   people's tools can read [S14].
