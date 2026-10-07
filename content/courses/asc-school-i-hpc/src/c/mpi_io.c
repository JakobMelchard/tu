/* mpi_io.c - parallel I/O (notes/15).
 *
 * Block 3, day 4: "Short tour: MPI I/O".  No lab in the course, so this is ours.
 * Writes one shared file four ways and reads it back, checking every byte:
 *
 *   1. explicit offsets, collective        MPI_File_write_at_all
 *   2. a file VIEW built from a derived datatype, then MPI_File_write_all with
 *      no offset arithmetic at all - the pattern of the lecture's "scenery B"
 *   3. an interleaved (round-robin) view, to show that the view is what decides
 *      the layout, not the call
 *   4. error handling: file handles default to MPI_ERRORS_RETURN, NOT fatal
 *
 * The file is written into the current directory and deleted at the end.
 *
 *   mpicc -O2 -Wall -Wextra mpi_io.c -o mpi_io
 *   mpirun --oversubscribe -np 4 ./mpi_io
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define NLOC 8                      /* doubles per rank */

static int failed = 0;

static void check(int rank, const char *what, long got, long want)
{
    if (got != want) {
        fprintf(stderr, "rank %d: %s = %ld, expected %ld\n", rank, what, got, want);
        failed = 1;
    }
}

/* MPI I/O errors are NOT fatal by default - every call must be checked. */
static void must(int rank, const char *what, int err)
{
    if (err != MPI_SUCCESS) {
        char msg[MPI_MAX_ERROR_STRING]; int len = 0;
        MPI_Error_string(err, msg, &len);
        fprintf(stderr, "rank %d: %s failed: %.*s\n", rank, what, len, msg);
        failed = 1;
    }
}

int main(int argc, char **argv)
{
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const char *fname = "mpi_io_demo.bin";
    double mine[NLOC], got[NLOC];
    for (int i = 0; i < NLOC; i++) mine[i] = 100.0 * rank + i;   /* rank*100 + i */

    /* ---- 0. the error handler really is non-fatal ------------------------ */
    {
        MPI_File fh;
        int err = MPI_File_open(MPI_COMM_WORLD, "no/such/directory/x.bin",
                                MPI_MODE_RDONLY, MPI_INFO_NULL, &fh);
        /* If this aborted the job we would never get here.  That it returns an
           error code instead is the whole point of the section. */
        if (err == MPI_SUCCESS) {
            fprintf(stderr, "rank %d: opening a bogus path unexpectedly succeeded\n", rank);
            failed = 1;
            MPI_File_close(&fh);
        } else if (rank == 0) {
            int cls = 0;
            MPI_Error_class(err, &cls);
            printf("opening a bogus path returned error class %d (non-fatal by default)\n", cls);
        }
    }

    /* ---- 1. explicit offsets, collective --------------------------------- */
    {
        MPI_File fh;
        must(rank, "open(1)", MPI_File_open(MPI_COMM_WORLD, fname,
                 MPI_MODE_CREATE | MPI_MODE_WRONLY, MPI_INFO_NULL, &fh));
        MPI_Offset off = (MPI_Offset)rank * NLOC;    /* in etypes = doubles */
        must(rank, "write_at_all", MPI_File_write_at_all(fh, off * (MPI_Offset)sizeof(double),
                 mine, NLOC, MPI_DOUBLE, MPI_STATUS_IGNORE));
        must(rank, "close(1)", MPI_File_close(&fh));

        /* read back somebody else's block to prove it is one shared file */
        int other = (rank + 1) % size;
        must(rank, "open(1r)", MPI_File_open(MPI_COMM_WORLD, fname,
                 MPI_MODE_RDONLY, MPI_INFO_NULL, &fh));
        MPI_Status st;
        must(rank, "read_at_all", MPI_File_read_at_all(fh,
                 (MPI_Offset)other * NLOC * (MPI_Offset)sizeof(double),
                 got, NLOC, MPI_DOUBLE, &st));
        int n_read = 0;
        MPI_Get_count(&st, MPI_DOUBLE, &n_read);
        check(rank, "elements read", n_read, NLOC);
        for (int i = 0; i < NLOC; i++)
            check(rank, "block contents", (long)got[i], 100L * other + i);

        MPI_Offset fsize;
        MPI_File_get_size(fh, &fsize);
        check(rank, "file size", (long)fsize, (long)size * NLOC * (long)sizeof(double));
        must(rank, "close(1r)", MPI_File_close(&fh));

        if (rank == 0)
            printf("explicit offsets: %lld bytes, %d blocks of %d doubles\n",
                   (long long)fsize, size, NLOC);
    }

    /* ---- 2. the same layout with a VIEW and no offset arithmetic ---------- */
    {
        MPI_File fh;
        must(rank, "open(2)", MPI_File_open(MPI_COMM_WORLD, fname,
                 MPI_MODE_RDONLY, MPI_INFO_NULL, &fh));

        /* filetype: my contiguous block, placed by `disp`.  Every process sets a
           different disp, so one collective read gets each its own block. */
        MPI_Offset disp = (MPI_Offset)rank * NLOC * (MPI_Offset)sizeof(double);
        must(rank, "set_view(2)", MPI_File_set_view(fh, disp, MPI_DOUBLE, MPI_DOUBLE,
                 "native", MPI_INFO_NULL));
        must(rank, "read_all(2)", MPI_File_read_all(fh, got, NLOC, MPI_DOUBLE,
                 MPI_STATUS_IGNORE));
        for (int i = 0; i < NLOC; i++)
            check(rank, "view block", (long)got[i], 100L * rank + i);
        must(rank, "close(2)", MPI_File_close(&fh));
    }

    /* ---- 3. an interleaved view: the view decides the layout -------------- */
    {
        /* filetype = one double every `size` doubles, i.e. a round-robin
           distribution.  Same call, completely different file layout. */
        MPI_Datatype strided;
        MPI_Type_vector(NLOC, 1, size, MPI_DOUBLE, &strided);
        MPI_Type_create_resized(strided, 0, (MPI_Aint)sizeof(double), &strided);
        MPI_Type_commit(&strided);

        MPI_File fh;
        must(rank, "open(3)", MPI_File_open(MPI_COMM_WORLD, "mpi_io_demo2.bin",
                 MPI_MODE_CREATE | MPI_MODE_RDWR, MPI_INFO_NULL, &fh));
        must(rank, "set_view(3w)", MPI_File_set_view(fh,
                 (MPI_Offset)rank * (MPI_Offset)sizeof(double),
                 MPI_DOUBLE, strided, "native", MPI_INFO_NULL));
        must(rank, "write_all(3)", MPI_File_write_all(fh, mine, NLOC, MPI_DOUBLE,
                 MPI_STATUS_IGNORE));
        must(rank, "close(3)", MPI_File_close(&fh));

        /* read the whole file linearly on rank 0 and verify the interleaving */
        if (rank == 0) {
            must(rank, "open(3r)", MPI_File_open(MPI_COMM_SELF, "mpi_io_demo2.bin",
                     MPI_MODE_RDONLY, MPI_INFO_NULL, &fh));
            int n = size * NLOC;
            double *all = malloc((size_t)n * sizeof *all);
            must(rank, "read(3)", MPI_File_read(fh, all, n, MPI_DOUBLE, MPI_STATUS_IGNORE));
            for (int k = 0; k < n; k++) {
                int r = k % size, i = k / size;          /* round robin */
                check(rank, "interleaved element", (long)all[k], 100L * r + i);
            }
            printf("interleaved view: first %d values %g %g %g %g (rank-major, "
                   "written by 4 collective calls)\n",
                   size < 4 ? size : 4, all[0], all[1], all[2], all[3]);
            free(all);
            must(rank, "close(3r)", MPI_File_close(&fh));
        }
        MPI_Type_free(&strided);
    }

    MPI_Barrier(MPI_COMM_WORLD);
    if (rank == 0) {                       /* delete is LOCAL, not collective */
        MPI_File_delete(fname, MPI_INFO_NULL);
        MPI_File_delete("mpi_io_demo2.bin", MPI_INFO_NULL);
    }

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (rank == 0) printf("mpi_io: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
