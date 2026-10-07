/* shmem_onesided.c - shared-memory one-sided communication, "MPI+MPI"
 * (notes/14).
 *
 * Block 3, day 4: "Shared memory one-sided communication"; our own version of
 * the ASC/HLRS lab 09_1sided-shmem.  Three parts:
 *
 *   1. MPI_Comm_split_type(MPI_COMM_TYPE_SHARED) - who can share memory with me
 *   2. the ring again, on comm_sm, with the MPI_Put replaced by a PLAIN STORE
 *      into the neighbour's piece of a shared window.  Invariant:
 *          sum = P_sm (P_sm - 1) / 2       with P_sm = ranks on MY node
 *   3. one copy of a read-only table per node instead of one per rank, with
 *      MPI_Win_shared_query used properly (no reliance on contiguity)
 *
 * On a laptop or a single-node job comm_sm == MPI_COMM_WORLD and part 2's answer
 * equals the world answer; across nodes it does not, which is exactly the thing
 * the lab is built to show.
 *
 *   mpicc -O2 -Wall -Wextra shmem_onesided.c -o shmem_onesided
 *   mpirun --oversubscribe -np 4 ./shmem_onesided
 */
#include <mpi.h>
#include <stdio.h>

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

    /* ---- 1. the shared-memory communicator ------------------------------- */
    MPI_Comm comm_sm;
    int rank_sm, size_sm;
    MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &comm_sm);
    MPI_Comm_rank(comm_sm, &rank_sm);
    MPI_Comm_size(comm_sm, &size_sm);

    if (rank_sm == 0 && world_rank == 0)
        printf("MPI_COMM_WORLD is %s\n",
               size_sm == world_size ? "one shared-memory region"
                                     : "split into 2 or more shared-memory islands");

    /* ---- 2. the ring, with a store instead of an MPI_Put ------------------ */
    {
        int *rcv_ptr;
        MPI_Win win;
        MPI_Win_allocate_shared((MPI_Aint)sizeof(int), sizeof(int),
                                MPI_INFO_NULL, comm_sm, &rcv_ptr, &win);

        /* Do NOT assume the pieces are contiguous: ask.  (They are, by default,
           but MPI_Info "alloc_shared_noncontig" may change that.) */
        int right = (rank_sm + 1) % size_sm;
        MPI_Aint      right_size;
        int           right_disp;
        int          *right_ptr;
        MPI_Win_shared_query(win, right, &right_size, &right_disp, &right_ptr);
        check(world_rank, "neighbour's window size", (long)right_size, (long)sizeof(int));
        check(world_rank, "neighbour's disp_unit", right_disp, (long)sizeof(int));

        *rcv_ptr = -1;
        int snd = rank_sm, sum = 0;
        for (int i = 0; i < size_sm; i++) {
            MPI_Win_fence(0, win);          /* assertions are easy to get wrong
                                               once ordinary stores are involved */
            *right_ptr = snd;               /* this replaces MPI_Put entirely */
            MPI_Win_fence(0, win);
            snd = *rcv_ptr;
            sum += *rcv_ptr;
        }

        long answer_sm = (long)size_sm * (size_sm - 1) / 2;
        check(world_rank, "shared-memory ring sum", sum, answer_sm);
        printf("PE world %2d of %2d | comm_sm %2d of %2d | sum = %d (expected %ld)\n",
               world_rank, world_size, rank_sm, size_sm, sum, answer_sm);
        fflush(stdout);

        MPI_Win_free(&win);
    }

    /* ---- 3. one copy of a table per node --------------------------------- */
    {
        /* rank_sm == 0 allocates the whole table; everybody else contributes 0
           bytes and then reads it through the shared window. */
        const int  n = 1024;
        double    *table;
        MPI_Win    win;
        MPI_Aint   bytes = (rank_sm == 0) ? (MPI_Aint)n * (MPI_Aint)sizeof(double) : 0;

        MPI_Win_allocate_shared(bytes, sizeof(double), MPI_INFO_NULL, comm_sm, &table, &win);

        MPI_Aint  sz;
        int       du;
        double   *base;
        MPI_Win_shared_query(win, 0, &sz, &du, &base);      /* rank 0's piece */
        check(world_rank, "table bytes visible to everyone", (long)sz,
              (long)n * (long)sizeof(double));
        check(world_rank, "table disp_unit", du, (long)sizeof(double));

        MPI_Win_fence(0, win);
        if (rank_sm == 0)
            for (int i = 0; i < n; i++) base[i] = 0.5 * i;
        MPI_Win_fence(0, win);

        /* every rank on the node now reads the SAME memory: no copy, no message */
        double s = 0.0;
        for (int i = 0; i < n; i++) s += base[i];
        /* 0.5 * sum_{i=0}^{n-1} i = 0.5 * n(n-1)/2 */
        check(world_rank, "table sum", (long)s, (long)(0.5 * n * (n - 1) / 2));

        if (world_rank == 0)
            printf("read-only table: %d doubles, one copy per node instead of %d copies\n",
                   n, size_sm);
        MPI_Win_free(&win);
    }

    /* ---- 4. the two-level pattern: node leaders talk to each other -------- */
    {
        MPI_Comm leaders;
        MPI_Comm_split(MPI_COMM_WORLD, rank_sm == 0 ? 0 : MPI_UNDEFINED, world_rank, &leaders);
        int n_nodes = 0;
        if (leaders != MPI_COMM_NULL) {
            MPI_Comm_size(leaders, &n_nodes);
            MPI_Comm_free(&leaders);
        }
        /* broadcast the node count back down inside each node */
        MPI_Bcast(&n_nodes, 1, MPI_INT, 0, comm_sm);
        if (n_nodes < 1) { fprintf(stderr, "rank %d: no node leaders?\n", world_rank); failed = 1; }
        if (world_rank == 0) printf("shared-memory islands in this job: %d\n", n_nodes);
    }

    MPI_Comm_free(&comm_sm);

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (world_rank == 0) printf("shmem_onesided: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
