/* onesided.c - one-sided communication / RMA (notes/13).
 *
 * Block 3, day 4: "One-sided communication"; our own version of the ASC/HLRS
 * lab 08_1sided.  Four parts, each checked against a closed-form answer:
 *
 *   1. the ring, with MPI_Put and MPI_Win_fence.  Same invariant as every other
 *      version of the ring in this course:  sum = P(P-1)/2  on every rank.
 *   2. MPI_Get: read the whole distributed vector out of everybody's window.
 *   3. MPI_Accumulate: many origins updating one location safely.
 *   4. passive target: MPI_Win_lock / MPI_Fetch_and_op as a distributed counter.
 *
 *   mpicc -O2 -Wall -Wextra onesided.c -o onesided
 *   mpirun --oversubscribe -np 4 ./onesided
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
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const long ring_answer = (long)size * (size - 1) / 2;

    /* ---- 1. the ring with MPI_Put ---------------------------------------- */
    {
        int rcv_buf = -1, snd_buf = rank, sum = 0;
        int right = (rank + 1) % size;
        MPI_Win win;

        /* expose ONE int.  disp_unit = sizeof(int), so displacements count ints. */
        MPI_Win_create(&rcv_buf, (MPI_Aint)sizeof(int), sizeof(int),
                       MPI_INFO_NULL, MPI_COMM_WORLD, &win);

        for (int i = 0; i < size; i++) {
            /* NOPRECEDE: no RMA before this fence in the epoch we are opening.
               NOSTORE:   we did not write our own window with a local store.   */
            MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPRECEDE, win);
            MPI_Put(&snd_buf, 1, MPI_INT, right, (MPI_Aint)0, 1, MPI_INT, win);
            /* NOPUT/NOSUCCEED: nothing follows in this epoch. */
            MPI_Win_fence(MPI_MODE_NOSTORE | MPI_MODE_NOPUT | MPI_MODE_NOSUCCEED, win);

            /* only NOW may we read our own window with a local load */
            snd_buf = rcv_buf;
            sum += rcv_buf;
        }
        check(rank, "ring sum via MPI_Put", sum, ring_answer);
        printf("PE %2d: MPI_Put ring sum = %d (expected %ld)\n", rank, sum, ring_answer);
        fflush(stdout);
        MPI_Win_free(&win);
    }

    /* ---- 2. MPI_Get: pull everybody's contribution ----------------------- */
    {
        int mine = 10 * rank + 1;
        int *all = malloc((size_t)size * sizeof *all);
        MPI_Win win;
        MPI_Win_create(&mine, (MPI_Aint)sizeof(int), sizeof(int),
                       MPI_INFO_NULL, MPI_COMM_WORLD, &win);

        MPI_Win_fence(MPI_MODE_NOPRECEDE, win);
        for (int r = 0; r < size; r++)
            MPI_Get(&all[r], 1, MPI_INT, r, (MPI_Aint)0, 1, MPI_INT, win);
        MPI_Win_fence(MPI_MODE_NOSUCCEED, win);

        for (int r = 0; r < size; r++) check(rank, "MPI_Get element", all[r], 10L * r + 1);
        MPI_Win_free(&win);
        free(all);
    }

    /* ---- 3. MPI_Accumulate: concurrent updates of one location ----------- */
    {
        int counter = 0;                     /* only rank 0's copy is used */
        MPI_Win win;
        MPI_Win_create(&counter, (MPI_Aint)sizeof(int), sizeof(int),
                       MPI_INFO_NULL, MPI_COMM_WORLD, &win);

        int contribution = rank + 1;
        MPI_Win_fence(MPI_MODE_NOPRECEDE, win);
        /* every rank adds to the SAME location on rank 0.  With MPI_Put this
           would be erroneous (concurrent conflicting accesses); accumulate is
           defined for exactly this. */
        MPI_Accumulate(&contribution, 1, MPI_INT, 0, (MPI_Aint)0, 1, MPI_INT,
                       MPI_SUM, win);
        MPI_Win_fence(MPI_MODE_NOSUCCEED, win);

        if (rank == 0) {
            /* sum_{r=1}^{P} r = P(P+1)/2 */
            check(rank, "MPI_Accumulate total", counter, (long)size * (size + 1) / 2);
            printf("MPI_Accumulate: %d ranks contributed, total %d (expected %ld)\n",
                   size, counter, (long)size * (size + 1) / 2);
        }
        MPI_Win_free(&win);
    }

    /* ---- 4. passive target: a distributed counter ------------------------ */
    {
        /* rank 0 owns a counter; every rank fetches-and-adds 1 exactly once, so
           the P values handed out are a permutation of 0 .. P-1 and the final
           counter is P.  The target never calls anything. */
        int *counter = NULL;
        MPI_Win win;
        if (rank == 0) {
            MPI_Alloc_mem((MPI_Aint)sizeof(int), MPI_INFO_NULL, &counter);
            *counter = 0;
            MPI_Win_create(counter, (MPI_Aint)sizeof(int), sizeof(int),
                           MPI_INFO_NULL, MPI_COMM_WORLD, &win);
        } else {
            MPI_Win_create(NULL, 0, sizeof(int), MPI_INFO_NULL, MPI_COMM_WORLD, &win);
        }

        int one = 1, ticket = -1;
        MPI_Win_lock(MPI_LOCK_SHARED, 0, 0, win);
        MPI_Fetch_and_op(&one, &ticket, MPI_INT, 0, (MPI_Aint)0, MPI_SUM, win);
        MPI_Win_unlock(0, win);              /* completes the operation */

        if (ticket < 0 || ticket >= size) {
            fprintf(stderr, "rank %d: ticket %d out of range\n", rank, ticket);
            failed = 1;
        }
        /* every ticket must be handed out exactly once */
        int *tickets = malloc((size_t)size * sizeof *tickets);
        MPI_Allgather(&ticket, 1, MPI_INT, tickets, 1, MPI_INT, MPI_COMM_WORLD);
        long ticket_sum = 0;
        for (int i = 0; i < size; i++) ticket_sum += tickets[i];
        check(rank, "tickets are a permutation of 0..P-1", ticket_sum, ring_answer);
        free(tickets);

        MPI_Barrier(MPI_COMM_WORLD);         /* only so the print below is safe */
        if (rank == 0) {
            check(rank, "final counter", *counter, size);
            printf("passive target: %d tickets handed out, counter = %d\n", size, *counter);
        }
        MPI_Win_free(&win);
        if (rank == 0) MPI_Free_mem(counter);
    }

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (rank == 0) printf("onesided: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
