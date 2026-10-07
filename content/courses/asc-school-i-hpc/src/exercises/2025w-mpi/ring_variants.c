/* ring_variants.c - the block-3 running exercise, seven ways.
 *
 * See README.md in this directory for what the labs ask and why this file
 * exists.  Every variant computes the same quantity and asserts it:
 *
 *      sum = 0 + 1 + ... + (P-1) = P(P-1)/2   on EVERY rank
 *
 *   P = 2 ->  1      P = 4 ->  6      P = 8 -> 28      P = 16 -> 120
 *
 * The invariant is what makes the exercise useful: seven completely different
 * mechanisms, one answer.  If a variant prints something else, that variant is
 * broken - not the ring.
 *
 * Variants:
 *   0  ordered Send/Recv    one rank receives first, the rest send first
 *   1  Sendrecv             one call, MPI orders it internally
 *   2  Sendrecv_replace     same buffer
 *   3  Issend + Recv + Wait the ASC/HLRS solution: a SYNCHRONOUS nonblocking
 *                           send, so buffering cannot hide a deadlock
 *   4  Irecv + Issend + Waitall
 *   5  Allreduce            the same answer in one collective (lab 04)
 *   6  Scan + Bcast         inclusive prefix; the last rank holds the total
 *
 * The deliberately WRONG version (Send then Recv on every rank, no ordering)
 * is not here: it lives in ../../c/deadlock.c, which runs it under an alarm so
 * the hang is observable without wedging the test suite.
 *
 *   mpicc -O2 -Wall -Wextra ring_variants.c -o ring_variants
 *   mpirun --oversubscribe -np 4 ./ring_variants
 *   mpirun --oversubscribe -np 7 ./ring_variants     # odd P: variant 0 matters
 */
#include <mpi.h>
#include <stdio.h>

static int failed = 0;

static void report(int rank, const char *name, long got, long want)
{
    if (got != want) {
        fprintf(stderr, "rank %d: %-22s = %ld, expected %ld\n", rank, name, got, want);
        failed = 1;
    } else if (rank == 0) {
        printf("  %-22s sum = %ld  OK\n", name, got);
    }
}

int main(int argc, char **argv)
{
    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    const int  right = (rank + 1) % size;
    const int  left  = (rank - 1 + size) % size;
    const long want  = (long)size * (size - 1) / 2;
    const int  TAG   = 17;

    if (rank == 0) printf("ring of %d processes, expected sum %ld\n", size, want);

    /* --- 0. ordered blocking Send/Recv ---------------------------------- */
    {
        /* Breaking the cycle needs exactly ONE rank to receive first; the usual
           "even sends, odd receives" rule is wrong for odd P, because rank 0 and
           rank size-1 are then both even and both send into a ring with nobody
           waiting.  One receiver is enough and works for every P >= 2:
             - rank size-1's Send matches rank 0's Recv;
             - rank size-1 then posts its Recv, which releases rank size-2;
             - the release cascades backwards to rank 1, whose Send releases
               rank 0's Send.
           No step depends on buffering, so this is correct at any message size. */
        int snd = rank, rcv, sum = 0;
        for (int i = 0; i < size; i++) {
            if (size == 1) {
                rcv = snd;
            } else if (rank == 0) {
                MPI_Recv(&rcv, 1, MPI_INT, left, TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                MPI_Send(&snd, 1, MPI_INT, right, TAG, MPI_COMM_WORLD);
            } else {
                MPI_Send(&snd, 1, MPI_INT, right, TAG, MPI_COMM_WORLD);
                MPI_Recv(&rcv, 1, MPI_INT, left, TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            }
            snd = rcv;
            sum += rcv;
        }
        report(rank, "ordered Send/Recv", sum, want);
    }

    /* --- 1. Sendrecv ------------------------------------------------------ */
    {
        int snd = rank, rcv, sum = 0;
        for (int i = 0; i < size; i++) {
            MPI_Sendrecv(&snd, 1, MPI_INT, right, TAG,
                         &rcv, 1, MPI_INT, left, TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            snd = rcv;
            sum += rcv;
        }
        report(rank, "Sendrecv", sum, want);
    }

    /* --- 2. Sendrecv_replace --------------------------------------------- */
    {
        int buf = rank, sum = 0;
        for (int i = 0; i < size; i++) {
            MPI_Sendrecv_replace(&buf, 1, MPI_INT, right, TAG, left, TAG,
                                 MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            sum += buf;
        }
        report(rank, "Sendrecv_replace", sum, want);
    }

    /* --- 3. Issend + Recv + Wait  (the course's solution) ----------------- */
    {
        int snd = rank, rcv, sum = 0;
        MPI_Request req;
        for (int i = 0; i < size; i++) {
            /* Issend, not Isend: a synchronous send completes only when the
               matching receive has started, so this version cannot be rescued
               by eager buffering.  If it runs, the exchange is genuinely correct. */
            MPI_Issend(&snd, 1, MPI_INT, right, TAG, MPI_COMM_WORLD, &req);
            MPI_Recv(&rcv, 1, MPI_INT, left, TAG, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Wait(&req, MPI_STATUS_IGNORE);
            snd = rcv;
            sum += rcv;
        }
        report(rank, "Issend/Recv/Wait", sum, want);
    }

    /* --- 4. Irecv + Issend + Waitall -------------------------------------- */
    {
        int snd = rank, rcv, sum = 0;
        MPI_Request req[2];
        for (int i = 0; i < size; i++) {
            /* post the receive FIRST: the message then has somewhere to land */
            MPI_Irecv(&rcv, 1, MPI_INT, left, TAG, MPI_COMM_WORLD, &req[0]);
            MPI_Issend(&snd, 1, MPI_INT, right, TAG, MPI_COMM_WORLD, &req[1]);
            MPI_Waitall(2, req, MPI_STATUSES_IGNORE);
            snd = rcv;
            sum += rcv;
        }
        report(rank, "Irecv/Issend/Waitall", sum, want);
    }

    /* --- 5. Allreduce: the whole loop in one call ------------------------- */
    {
        int sum;
        MPI_Allreduce(&rank, &sum, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
        report(rank, "Allreduce", sum, want);
    }

    /* --- 6. Scan (+ Bcast of the total) ----------------------------------- */
    {
        int prefix;
        MPI_Scan(&rank, &prefix, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
        /* inclusive prefix: rank r holds 0+1+...+r, so rank size-1 holds the total */
        long want_prefix = (long)rank * (rank + 1) / 2;
        if (prefix != want_prefix) {
            fprintf(stderr, "rank %d: Scan prefix = %d, expected %ld\n",
                    rank, prefix, want_prefix);
            failed = 1;
        }
        int total = prefix;
        MPI_Bcast(&total, 1, MPI_INT, size - 1, MPI_COMM_WORLD);
        report(rank, "Scan + Bcast", total, want);
    }

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (rank == 0)
        printf("ring_variants: %s\n", any_failed ? "FAILED" : "all seven variants agree");

    MPI_Finalize();
    return any_failed;
}
