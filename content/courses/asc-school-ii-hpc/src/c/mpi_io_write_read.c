/* mpi_io_write_read.c - collective MPI-IO write, read back, verify (notes/06).
 *
 * A global NY x NX array of doubles, A[i][j] = i*NX + j, lives distributed on a
 * 2-D process grid (MPI_Dims_create + MPI_Cart_create).  Each rank owns one
 * rectangular block.  Steps:
 *
 *   1. write: subarray filetype -> MPI_File_set_view -> MPI_File_write_all.
 *      One collective call; the file is the row-major global array, i.e. the
 *      same bytes a serial program would write.  Hints (collective buffering,
 *      striping) are passed via MPI_Info and the ones the library kept are
 *      printed: on Lustre/GPFS they matter, on a laptop they are ignored.
 *   2. read back with a DIFFERENT decomposition (contiguous row blocks,
 *      MPI_File_read_at_all with explicit offsets) and check every element.
 *   3. rank 0 re-reads the whole file with plain stdio and checks it too, which
 *      proves the layout is independent of the process grid.
 *
 * The data representation is "native", so the file is only portable between
 * machines with the same endianness and double format.  The file is deleted
 * at the end.  Exit 1 on any mismatch.
 *
 * Run: mpirun --oversubscribe -np 4 ./mpi_io_write_read [NY NX]
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define CHECK(call)                                                            \
    do {                                                                       \
        int e_ = (call);                                                       \
        if (e_ != MPI_SUCCESS) {                                               \
            char s_[MPI_MAX_ERROR_STRING];                                     \
            int l_;                                                            \
            MPI_Error_string(e_, s_, &l_);                                     \
            fprintf(stderr, "%s:%d %s: %s\n", __FILE__, __LINE__, #call, s_); \
            MPI_Abort(MPI_COMM_WORLD, 3);                                      \
        }                                                                      \
    } while (0)

static void block_range(int n, int p, int r, int *lo, int *cnt)
{
    int q = n / p, rem = n % p;
    *lo = r * q + (r < rem ? r : rem);
    *cnt = q + (r < rem ? 1 : 0);
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int NY = argc > 2 ? atoi(argv[1]) : 1000, NX = argc > 2 ? atoi(argv[2]) : 777;
    char fname[64];
    snprintf(fname, sizeof fname, "io_demo_%d.bin", size);

    /* ---- process grid and my block ------------------------------------ */
    int dims[2] = {0, 0}, periods[2] = {0, 0}, coords[2];
    MPI_Dims_create(size, 2, dims);
    MPI_Comm cart;
    MPI_Cart_create(MPI_COMM_WORLD, 2, dims, periods, 1, &cart);
    int crank;
    MPI_Comm_rank(cart, &crank);
    MPI_Cart_coords(cart, crank, 2, coords);
    int y0, ny, x0, nx;
    block_range(NY, dims[0], coords[0], &y0, &ny);
    block_range(NX, dims[1], coords[1], &x0, &nx);

    double *blk = malloc((size_t)ny * nx * sizeof *blk + 1);
    for (int i = 0; i < ny; i++)
        for (int j = 0; j < nx; j++) blk[(size_t)i * nx + j] = (double)(y0 + i) * NX + (x0 + j);

    /* ---- 1. collective write through a file view ----------------------- */
    MPI_Datatype filetype;
    int gsizes[2] = {NY, NX}, lsizes[2] = {ny, nx}, starts[2] = {y0, x0};
    MPI_Type_create_subarray(2, gsizes, lsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &filetype);
    MPI_Type_commit(&filetype);

    MPI_Info info;
    MPI_Info_create(&info);
    MPI_Info_set(info, "romio_cb_write", "enable"); /* two-phase collective buffering */
    MPI_Info_set(info, "striping_factor", "4");     /* Lustre: stripe over 4 OSTs    */
    MPI_Info_set(info, "striping_unit", "1048576"); /* 1 MiB stripes                */

    MPI_File fh;
    /* File handles default to MPI_ERRORS_RETURN, so check every call. */
    CHECK(MPI_File_open(cart, fname, MPI_MODE_CREATE | MPI_MODE_WRONLY, info, &fh));
    CHECK(MPI_File_set_size(fh, 0)); /* truncate a leftover file */
    CHECK(MPI_File_set_view(fh, 0, MPI_DOUBLE, filetype, "native", info));
    double t0 = MPI_Wtime();
    CHECK(MPI_File_write_all(fh, blk, ny * nx, MPI_DOUBLE, MPI_STATUS_IGNORE));
    double t_write = MPI_Wtime() - t0;

    if (rank == 0) {
        MPI_Info used;
        CHECK(MPI_File_get_info(fh, &used));
        int nkeys;
        MPI_Info_get_nkeys(used, &nkeys);
        const char *want[] = {"romio_cb_write", "striping_factor", "striping_unit", "cb_nodes"};
        printf("mpi_io_write_read: %d x %d doubles, grid %d x %d, %d info keys kept, e.g.\n",
               NY, NX, dims[0], dims[1], nkeys);
        for (int k = 0; k < 4; k++) {
            char val[MPI_MAX_INFO_VAL + 1];
            int flag;
            MPI_Info_get(used, want[k], MPI_MAX_INFO_VAL, val, &flag);
            printf("    %-16s %s\n", want[k], flag ? val : "(not kept by this MPI-IO layer)");
        }
        MPI_Info_free(&used);
    }
    CHECK(MPI_File_close(&fh));
    MPI_Type_free(&filetype);

    /* ---- 2. read back with row blocks and explicit offsets ------------- */
    int r0, nr;
    block_range(NY, size, rank, &r0, &nr);
    double *rows = malloc((size_t)nr * NX * sizeof *rows + 1);
    CHECK(MPI_File_open(MPI_COMM_WORLD, fname, MPI_MODE_RDONLY, info, &fh));
    MPI_Offset off = (MPI_Offset)r0 * NX * (MPI_Offset)sizeof(double);
    t0 = MPI_Wtime();
    CHECK(MPI_File_read_at_all(fh, off, rows, nr * NX, MPI_DOUBLE, MPI_STATUS_IGNORE));
    double t_read = MPI_Wtime() - t0;
    MPI_Offset fsize;
    CHECK(MPI_File_get_size(fh, &fsize));
    CHECK(MPI_File_close(&fh));

    long bad = 0;
    for (int i = 0; i < nr; i++)
        for (int j = 0; j < NX; j++)
            if (rows[(size_t)i * NX + j] != (double)(r0 + i) * NX + j) bad++;
    long bad_total = 0;
    MPI_Allreduce(&bad, &bad_total, 1, MPI_LONG, MPI_SUM, MPI_COMM_WORLD);

    /* ---- 3. serial re-read by rank 0 ----------------------------------- */
    int ok = bad_total == 0 && fsize == (MPI_Offset)NY * NX * (MPI_Offset)sizeof(double);
    if (rank == 0) {
        FILE *fp = fopen(fname, "rb");
        long bad_serial = 0;
        double v;
        for (long k = 0; fp && k < (long)NY * NX; k++)
            if (fread(&v, sizeof v, 1, fp) != 1 || v != (double)k) bad_serial++;
        if (!fp) bad_serial = -1;
        else fclose(fp);
        if (bad_serial) ok = 0;
        double mb = (double)fsize / 1048576.0;
        printf("  file %lld bytes (expected %lld)\n", (long long)fsize,
               (long long)NY * NX * (long long)sizeof(double));
        printf("  read-back with %d row blocks: %ld wrong elements; stdio re-read: %ld wrong\n",
               size, bad_total, bad_serial);
        printf("  write_all %.2f MiB in %.4f s, read_at_all in %.4f s (laptop, page cache)\n", mb,
               t_write, t_read);
        printf("%s\n", ok ? "mpi_io_write_read: OK" : "mpi_io_write_read: FAILED");
        MPI_File_delete(fname, MPI_INFO_NULL);
    }
    MPI_Bcast(&ok, 1, MPI_INT, 0, MPI_COMM_WORLD);

    MPI_Info_free(&info);
    free(blk);
    free(rows);
    MPI_Comm_free(&cart);
    MPI_Finalize();
    return ok ? 0 : 1;
}
