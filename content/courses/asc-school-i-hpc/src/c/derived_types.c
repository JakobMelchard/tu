/* derived_types.c - derived datatypes (notes/12).
 *
 * Block 3, day 3: "Derived datatypes"; the ASC/HLRS lab 07_derived-datatypes is
 * the struct part.  The point of this program is that it MEASURES the two
 * numbers people get wrong from memory - MPI_Type_size and the *extent* - and
 * asserts them against values derived by hand in the note, instead of trusting
 * either.
 *
 *   size   = bytes actually transferred
 *   extent = span from the lowest to the highest byte touched, i.e. the stride
 *            MPI uses when count > 1.  These are NOT equal for strided types.
 *
 * Covers: contiguous, vector (a matrix column), create_resized (so that
 * count > 1 works), create_struct with MPI_Get_address, and create_subarray
 * (a halo face).
 *
 *   mpicc -O2 -Wall -Wextra derived_types.c -o derived_types
 *   mpirun --oversubscribe -np 4 ./derived_types
 */
#include <mpi.h>
#include <stdio.h>
#include <string.h>

#define N 4                     /* the matrix is N x N doubles, row-major */

static int failed = 0;

static void check(int rank, const char *what, long got, long want)
{
    if (got != want) {
        fprintf(stderr, "rank %d: %s = %ld, expected %ld\n", rank, what, got, want);
        failed = 1;
    }
}

typedef struct { int id; double x[3]; char tag; } Particle;

int main(int argc, char **argv)
{
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    if (size < 2) { fprintf(stderr, "need at least 2 ranks\n"); MPI_Abort(MPI_COMM_WORLD, 1); }

    /* ---- 1. a column of a row-major matrix ------------------------------- */
    double A[N][N];
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) A[i][j] = 10.0 * i + j;      /* A[i][j] = i*10 + j */

    MPI_Datatype col;
    MPI_Type_vector(N, 1, N, MPI_DOUBLE, &col);   /* N blocks of 1, stride N elements */
    MPI_Type_commit(&col);

    int size_bytes;
    MPI_Aint lb, extent;
    MPI_Type_size(col, &size_bytes);
    MPI_Type_get_extent(col, &lb, &extent);

    /* Derived, not recalled:
     *   size   = N blocks * 1 element * sizeof(double)
     *   extent = (N-1) * stride_bytes + blocklength * sizeof(double)
     *          = (N-1) * N * 8 + 8            = 104 for N = 4          */
    check(rank, "MPI_Type_size(col)",   size_bytes, (long)N * (long)sizeof(double));
    check(rank, "MPI_Type_get_extent(col)", extent,
          (long)(N - 1) * N * (long)sizeof(double) + (long)sizeof(double));
    check(rank, "lower bound of col", lb, 0);
    if (rank == 0)
        printf("column type: size %d B, extent %ld B (they differ: the stride is the extent)\n",
               size_bytes, (long)extent);

    /* send column 2; the receiver takes it as N contiguous doubles.
       Type SIGNATURES must match; type MAPS need not. */
    if (rank == 0) {
        MPI_Send(&A[0][2], 1, col, 1, 0, MPI_COMM_WORLD);
    } else if (rank == 1) {
        double got[N];
        MPI_Recv(got, N, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        for (int i = 0; i < N; i++) check(rank, "column element", (long)got[i], 10L * i + 2);
        printf("rank 1 received column 2 as %g %g %g %g\n", got[0], got[1], got[2], got[3]);
    }

    /* ---- 2. why count > 1 needs MPI_Type_create_resized ------------------- */
    MPI_Datatype col_resized;
    MPI_Type_create_resized(col, 0, (MPI_Aint)sizeof(double), &col_resized);
    MPI_Type_commit(&col_resized);
    MPI_Type_get_extent(col_resized, &lb, &extent);
    check(rank, "extent after resize", extent, (long)sizeof(double));

    if (rank == 0) {
        MPI_Send(&A[0][1], 2, col_resized, 1, 1, MPI_COMM_WORLD);   /* columns 1 AND 2 */
    } else if (rank == 1) {
        double got[2 * N];
        MPI_Recv(got, 2 * N, MPI_DOUBLE, 0, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        /* first N values are column 1, next N are column 2 */
        for (int i = 0; i < N; i++) {
            check(rank, "resized col 1", (long)got[i],     10L * i + 1);
            check(rank, "resized col 2", (long)got[N + i], 10L * i + 2);
        }
    }

    /* ---- 3. a struct, with the compiler's own offsets --------------------- */
    MPI_Datatype ptype;
    {
        Particle probe = {0, {0.0, 0.0, 0.0}, 0};
        int          blen[3] = {1, 3, 1};
        MPI_Datatype typ[3]  = {MPI_INT, MPI_DOUBLE, MPI_CHAR};
        MPI_Aint     disp[3], base;

        MPI_Get_address(&probe,     &base);
        MPI_Get_address(&probe.id,  &disp[0]);
        MPI_Get_address(&probe.x,   &disp[1]);
        MPI_Get_address(&probe.tag, &disp[2]);
        for (int i = 0; i < 3; i++) disp[i] -= base;

        MPI_Datatype raw;
        MPI_Type_create_struct(3, blen, disp, typ, &raw);
        /* resize to sizeof(Particle) so that count > 1 walks an array correctly:
           without this the extent stops at `tag` and the trailing padding is
           skipped. */
        MPI_Type_create_resized(raw, 0, (MPI_Aint)sizeof(Particle), &ptype);
        MPI_Type_commit(&ptype);
        MPI_Type_free(&raw);

        MPI_Type_get_extent(ptype, &lb, &extent);
        check(rank, "struct extent == sizeof(Particle)", extent, (long)sizeof(Particle));
        MPI_Type_size(ptype, &size_bytes);
        check(rank, "struct size == int + 3 doubles + char", size_bytes,
              (long)(sizeof(int) + 3 * sizeof(double) + sizeof(char)));
    }

    {
        const int np = 5;
        Particle p[5];
        if (rank == 0) {
            for (int i = 0; i < np; i++) {
                p[i].id = 100 + i;
                for (int k = 0; k < 3; k++) p[i].x[k] = i + 0.25 * k;
                p[i].tag = (char)('a' + i);
            }
            MPI_Send(p, np, ptype, 1, 2, MPI_COMM_WORLD);
        } else if (rank == 1) {
            memset(p, 0, sizeof p);
            MPI_Recv(p, np, ptype, 0, 2, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            for (int i = 0; i < np; i++) {
                check(rank, "particle id", p[i].id, 100 + i);
                check(rank, "particle tag", p[i].tag, 'a' + i);
                for (int k = 0; k < 3; k++)
                    check(rank, "particle x*4", (long)(4.0 * p[i].x[k]), 4L * i + k);
            }
            printf("rank 1 received %d particles, last: id %d tag %c x %g %g %g\n",
                   np, p[np - 1].id, p[np - 1].tag,
                   p[np - 1].x[0], p[np - 1].x[1], p[np - 1].x[2]);
        }
    }

    /* ---- 4. a halo face with MPI_Type_create_subarray --------------------- */
    {
        /* a (N+2)^2 array with one ghost layer; the face is one interior row */
        int sizes[2]    = {N + 2, N + 2};
        int subsizes[2] = {1, N};
        int starts[2]   = {1, 1};
        MPI_Datatype face;
        MPI_Type_create_subarray(2, sizes, subsizes, starts, MPI_ORDER_C, MPI_DOUBLE, &face);
        MPI_Type_commit(&face);

        MPI_Type_size(face, &size_bytes);
        check(rank, "face size", size_bytes, (long)N * (long)sizeof(double));
        MPI_Type_get_extent(face, &lb, &extent);
        /* the subarray type is defined with lb = 0 and extent = the whole array */
        check(rank, "face extent == whole array", extent,
              (long)(N + 2) * (N + 2) * (long)sizeof(double));

        double G[N + 2][N + 2];
        for (int i = 0; i < N + 2; i++)
            for (int j = 0; j < N + 2; j++) G[i][j] = (i == 1) ? (double)j : -1.0;

        if (rank == 0) {
            MPI_Send(&G[0][0], 1, face, 1, 3, MPI_COMM_WORLD);
        } else if (rank == 1) {
            double got[N];
            MPI_Recv(got, N, MPI_DOUBLE, 0, 3, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            for (int j = 0; j < N; j++) check(rank, "face element", (long)got[j], j + 1);
        }
        MPI_Type_free(&face);
    }

    MPI_Type_free(&col_resized);
    MPI_Type_free(&col);
    MPI_Type_free(&ptype);

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (rank == 0) printf("derived_types: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
