# 06 Parallel I/O: MPI-IO, HDF5, striping

No catalogue event 2023-2027 is dedicated to I/O [S4]; MPI I/O is a
short tour on day 4 of the School I MPI block. The MPI-IO semantics (file
views, the 18-cell access table, two-phase collective I/O, non-fatal errors)
are in ASC-School I note 15 [S11] and are not repeated. This note adds the
layer below (file systems, striping, hints) and the layer above (HDF5).

## Definitions

- **Parallel file system**: metadata servers (names, permissions, layout)
  plus many data servers/targets holding file contents; a file is spread over
  several targets so many clients can read and write it at once.
- **Striping (Lustre)**: a file is cut into stripes of `stripe_size` bytes
  distributed round-robin over `stripe_count` object storage targets (OSTs).
  Set per directory or file with `lfs setstripe`, inspect with `lfs getstripe`
  [S22]. **GPFS** (IBM Storage Scale) stripes by file-system block over all
  disks without a per-user knob; **WekaIO** is an all-flash distributed file
  system [S12] [S13].
- **Access patterns**: N-N (file per process), N-1 (one shared file), N-M
  (M aggregator ranks write M files or stripes).
- **Collective buffering / two-phase I/O**: in a collective call, data are
  first redistributed among ranks so that a few **aggregators** issue large
  contiguous requests aligned to the file system [S15].
- **Hints**: `MPI_Info` key/value pairs passed at open or `set_view`
  (`striping_factor`, `striping_unit`, `cb_nodes`, `romio_cb_write`). They are
  advisory; an implementation may ignore any of them [S15].
- **HDF5**: a self-describing file format and library (groups, datasets,
  attributes, datatypes). **Hyperslab**: a rectangular selection of a dataset.
  **Parallel HDF5** runs on top of MPI-IO [S22].

## What the ASC systems offer

| system | where | what | notes |
|---|---|---|---|
| VSC-4/5 | `$HOME`, `$DATA` | GPFS, same on both clusters; `$DATA` tiered NVMe/HDD, 10 TB quota (to 100 TB) | files counted: $10^6$ per project [S12] |
| VSC-4/5 | `/local`, `/tmp` | node NVMe (~450 GB / 1.8 TB), RAM | wiped after job; `/tmp` counts against memory [S12] |
| MUSICA | `$SCRATCH` | WekaIO all-flash, 4 PB, 5 TB project quota | **not backed up, may be cleared** [S13] |
| MUSICA | `$HOME`, `$DATA` | GPFS; `$DATA` 10 TB (Vienna) tiered | 10 million files [S13] |

**No ASC system runs Lustre** [S12] [S13]. `lfs setstripe` matters when you
move to a machine that does; on ASC the knobs are "which tier" and "how many
files".

## Worked example: collective write, re-read with another decomposition

[`../src/c/mpi_io_write_read.c`](../src/c/mpi_io_write_read.c): a
$1000 \times 777$ array of doubles with $A_{ij} = 777 i + j$ on a 2-D process
grid.

1. Each rank describes its block with `MPI_Type_create_subarray`, sets it as
   the file view, and calls `MPI_File_write_all` once. The file is the
   row-major global array, the bytes a serial code would write.
2. The file is read back with a different decomposition, contiguous row blocks
   at explicit offsets `r0 * NX * 8` via `MPI_File_read_at_all`.
3. Rank 0 re-reads it with `fread` and checks $A_{ij}$ element by element.

Run on the laptop [S10]:

```
$ mpirun --oversubscribe -np 4 ./mpi_io_write_read
mpi_io_write_read: 1000 x 777 doubles, grid 2 x 2, 0 info keys kept, e.g.
    romio_cb_write   (not kept by this MPI-IO layer)
    striping_factor  (not kept by this MPI-IO layer)
  file 6216000 bytes (expected 6216000)
  read-back with 4 row blocks: 0 wrong elements; stdio re-read: 0 wrong
```

($6\,216\,000 = 1000 \cdot 777 \cdot 8$.) With 3 ranks the grid becomes
$3 \times 1$ and the file is byte-identical. Open MPI 5.0.11 returned **no**
info keys from `MPI_File_get_info`: the hints were accepted and ignored, which
is legal [S15]. On a cluster the same query tells you whether your striping and
aggregator hints arrived.

## HDF5, the parallel version (not run: no HDF5 on this machine)

```c
hid_t fapl = H5Pcreate(H5P_FILE_ACCESS);
H5Pset_fapl_mpio(fapl, MPI_COMM_WORLD, MPI_INFO_NULL);      /* MPI-IO driver */
hid_t file = H5Fcreate("a.h5", H5F_ACC_TRUNC, H5P_DEFAULT, fapl);
hsize_t g[2] = {NY, NX}, start[2] = {y0, x0}, cnt[2] = {ny, nx};
hid_t fspace = H5Screate_simple(2, g, NULL);
hid_t dset = H5Dcreate(file, "A", H5T_NATIVE_DOUBLE, fspace,
                       H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
H5Sselect_hyperslab(fspace, H5S_SELECT_SET, start, NULL, cnt, NULL);
hid_t mspace = H5Screate_simple(2, cnt, NULL);
hid_t dxpl = H5Pcreate(H5P_DATASET_XFER);
H5Pset_dxpl_mpio(dxpl, H5FD_MPIO_COLLECTIVE);                /* collective, as write_all */
H5Dwrite(dset, H5T_NATIVE_DOUBLE, mspace, fspace, dxpl, blk);
```

Same decomposition as the MPI-IO program; the hyperslab replaces the subarray
type. Gains over raw MPI-IO: named datasets, stored shape and type (portable
across endianness, unlike the `"native"` representation), attributes for
metadata, readable from Python with `h5py`. Build with `h5pcc` [S22].

## Worked example: striping on a Lustre system

```bash
mkdir out && lfs setstripe -c 16 -S 1M out   # files created in out/ use 16 OSTs, 1 MiB
lfs getstripe out/field_0042.h5              # check what a file got
```

NERSC's recommendations for its Lustre scratch [S22]: a shared file written
from more than 16 nodes gets stripe count = number of nodes; file per process
keeps the default (count 1 there) unless read-intensive; stripe size 1 MiB
(the default) suits most codes; never more than 128 OSTs. Striping is fixed
when a file is first written and inherited from the directory, so set it on
the output directory **before** the job; restriping means copying.

## Pitfalls

- File per process at $10^4$ ranks: $10^4$ files per output step, a metadata
  storm, and project file quotas ($10^6$ on VSC-4/5 [S12]) filled quickly.
- Many small independent writes (`MPI_File_write_at` per element or per row
  in a loop): each is a request; collective calls let the library merge them.
- MPI-IO errors do not abort by default (`MPI_ERRORS_RETURN` on files):
  check every return code (`CHECK` macro in the program) [S15].
- `"native"` files are not portable between architectures; HDF5 or the
  `"external32"` representation are.
- Results left on `$SCRATCH` or `/local`: not backed up / wiped [S12] [S13].
- Timing I/O on a laptop measures the page cache, not a disk (the printed
  times say so).

## Questions (ours)

1. *1024 ranks on 32 nodes write 4 MiB each to one file on Lustre with stripe
   count 1. What limits the rate?* One OST serves all 4 GiB. Set the stripe
   count of the output directory to 32 before the run [S22]; keep collective
   writes.
2. *Why can a collective write be faster although it moves data between
   ranks first?* Network redistribution is cheaper than many small,
   unaligned file-system requests; aggregators issue few large aligned ones.
3. *What does `MPI_File_get_info` returning none of your hints mean?* The
   MPI-IO layer ignored them (legal); tuning has to go through that
   implementation's own hint names or MCA parameters.
4. *Why read back with a different decomposition in the test?* It proves the
   file layout is the global row-major array, independent of the writer's
   process grid, which is what a restart with another rank count needs.
5. *HDF5 or raw MPI-IO for checkpoint files read by a Python postprocessing
   script?* HDF5: self-describing, portable, `h5py` reads a hyperslab directly;
   raw binary needs shape, dtype and endianness out of band.

## Code

- [`../src/c/mpi_io_write_read.c`](../src/c/mpi_io_write_read.c):
  `MPI_Type_create_subarray`, `MPI_File_set_view`, `MPI_File_write_all`,
  `MPI_File_read_at_all`, `MPI_File_get_info`, three checks.
- Four MPI-IO access styles: sibling
  [`asc-school-i-hpc/src/c/mpi_io.c`](../../asc-school-i-hpc/src/c/mpi_io.c).
