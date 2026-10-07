/* comm_split.c - groups and communicators (notes/10).
 *
 * Block 3, day 3: "Groups & communicators".  Mirrors the ASC/HLRS lab
 * 05_comm-split without copying it: split MPI_COMM_WORLD in two halves, run the
 * same MPI_Allreduce on the world and on the sub-communicator, and check both
 * against closed-form answers.  Also demonstrates MPI_Comm_group / _incl,
 * rank translation, and MPI_Comm_split_type(MPI_COMM_TYPE_SHARED).
 *
 * Reference results, for P processes (P even for the halves):
 *   world sum  = sum_{r=0}^{P-1} r        = P(P-1)/2
 *   lower half = sum_{r=0}^{P/2-1} r      = (P/2)(P/2-1)/2
 *   upper half = world - lower            = (P/2)(3P/2-1)/2
 * For P = 4: 6, 1, 5.
 *
 *   mpicc -O2 -Wall -Wextra comm_split.c -o comm_split
 *   mpirun --oversubscribe -np 4 ./comm_split
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

static int failed = 0;

static void check(int rank, const char *what, long got, long want)
{
    if (got != want) {
        fprintf(stderr, "rank %d: %s = %ld, expected %ld\n", rank, what, got, want);
        failed = 1;
    }
}

int main(int argc, char **argv)
{
    int world_rank, world_size;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);

    /* ---- 1. the same reduction on two different communicators ------------ */
    int world_sum;
    MPI_Allreduce(&world_rank, &world_sum, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    check(world_rank, "world sum", world_sum, (long)world_size * (world_size - 1) / 2);

    /* colour = which half I am in; key = old rank, so the order is preserved */
    int half = world_size / 2;
    int colour = (world_rank < half) ? 0 : 1;

    MPI_Comm sub;
    MPI_Comm_split(MPI_COMM_WORLD, colour, world_rank, &sub);

    int sub_rank, sub_size, sub_sum;
    MPI_Comm_rank(sub, &sub_rank);
    MPI_Comm_size(sub, &sub_size);
    /* NOTE: we reduce the WORLD rank, so the answer differs per half. */
    MPI_Allreduce(&world_rank, &sub_sum, 1, MPI_INT, MPI_SUM, sub);

    if (world_size % 2 == 0) {
        long lower = (long)half * (half - 1) / 2;
        long upper = (long)world_size * (world_size - 1) / 2 - lower;
        check(world_rank, "sub sum", sub_sum, colour == 0 ? lower : upper);
        check(world_rank, "sub size", sub_size, half);
    }

    /* the rank inside the sub-communicator is NOT the world rank */
    check(world_rank, "sub rank", sub_rank, colour == 0 ? world_rank : world_rank - half);

    printf("PE world %2d of %2d | colour %d | sub %2d of %2d | world sum %3d | sub sum %3d\n",
           world_rank, world_size, colour, sub_rank, sub_size, world_sum, sub_sum);
    fflush(stdout);

    /* ---- 2. building a communicator from an explicit group --------------- */
    MPI_Group world_grp, even_grp;
    MPI_Comm_group(MPI_COMM_WORLD, &world_grp);

    int n_even = (world_size + 1) / 2;
    int *even = malloc((size_t)n_even * sizeof *even);
    for (int i = 0; i < n_even; i++) even[i] = 2 * i;
    MPI_Group_incl(world_grp, n_even, even, &even_grp);

    MPI_Comm even_comm;
    MPI_Comm_create(MPI_COMM_WORLD, even_grp, &even_comm);   /* collective on the PARENT */

    if (even_comm != MPI_COMM_NULL) {
        int r, s, sum;
        MPI_Comm_rank(even_comm, &r);
        MPI_Comm_size(even_comm, &s);
        MPI_Allreduce(&world_rank, &sum, 1, MPI_INT, MPI_SUM, even_comm);
        /* sum of even numbers 0,2,...,2(n-1) = n(n-1) */
        check(world_rank, "even-group sum", sum, (long)n_even * (n_even - 1));
        check(world_rank, "even-group rank", r, world_rank / 2);
        check(world_rank, "even-group size", s, n_even);
        MPI_Comm_free(&even_comm);
    } else {
        check(world_rank, "odd rank excluded", world_rank % 2, 1);
    }

    /* rank translation between groups */
    if (world_rank == 0) {
        int from[2] = {0, 1}, to[2];
        MPI_Group_translate_ranks(world_grp, 2, from, even_grp, to);
        /* world rank 0 is rank 0 of the even group; world rank 1 is not in it */
        check(0, "translate(0)", to[0], 0);
        check(0, "translate(1)", to[1], MPI_UNDEFINED);
    }
    MPI_Group_free(&even_grp);
    MPI_Group_free(&world_grp);
    free(even);

    /* ---- 3. who shares memory with me? ----------------------------------- */
    MPI_Comm comm_sm;
    int sm_rank, sm_size;
    MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &comm_sm);
    MPI_Comm_rank(comm_sm, &sm_rank);
    MPI_Comm_size(comm_sm, &sm_size);
    if (sm_rank == 0 && world_rank == 0) {
        printf("shared-memory communicator: %d of %d ranks (%s)\n", sm_size, world_size,
               sm_size == world_size ? "one island" : "several islands");
    }
    if (sm_size < 1 || sm_size > world_size) {
        fprintf(stderr, "rank %d: implausible shared-memory size %d\n", world_rank, sm_size);
        failed = 1;
    }
    MPI_Comm_free(&comm_sm);
    MPI_Comm_free(&sub);

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (world_rank == 0) printf("comm_split: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
