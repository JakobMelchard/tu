/* sendrecv.c - blocking point-to-point communication.
 *
 * Run: mpirun --oversubscribe -np 4 ./sendrecv
 *
 * Covers MPI_Send/MPI_Recv, message envelope (source, tag, communicator),
 * MPI_Status + MPI_Get_count, wildcards MPI_ANY_SOURCE/MPI_ANY_TAG, tag
 * matching order, MPI_Sendrecv / MPI_Sendrecv_replace for a ring shift, and
 * MPI_Probe to receive a message of unknown length.  Every step checks its
 * result; the program exits non-zero if anything is wrong.
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

static int fails = 0;
#define CHECK(cond, ...) do { if (!(cond)) { fails++; printf("FAIL: " __VA_ARGS__); printf("\n"); } } while (0)

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    if (size < 2) {
        if (rank == 0) fprintf(stderr, "need at least 2 ranks\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    /* 1. A plain pair.  The receive buffer may be LARGER than the message
     *    (never smaller: that is an error).  MPI_Get_count on the status
     *    reports how many elements actually arrived. */
    const int TAG_DATA = 7;
    if (rank == 0) {
        double x[5] = {1, 2, 3, 4, 5};
        MPI_Send(x, 5, MPI_DOUBLE, 1, TAG_DATA, MPI_COMM_WORLD);
    } else if (rank == 1) {
        double buf[100];
        MPI_Status st;
        MPI_Recv(buf, 100, MPI_DOUBLE, MPI_ANY_SOURCE, MPI_ANY_TAG, MPI_COMM_WORLD, &st);
        int n;
        MPI_Get_count(&st, MPI_DOUBLE, &n);
        printf("rank 1: received %d doubles from rank %d, tag %d, last value %g\n",
               n, st.MPI_SOURCE, st.MPI_TAG, buf[n - 1]);
        CHECK(n == 5 && st.MPI_SOURCE == 0 && st.MPI_TAG == TAG_DATA && buf[4] == 5.0, "plain pair");
    }

    /* 2. Tags select which message you want.  Rank 0 sends A (tag 1) then
     *    B (tag 2); rank 1 asks for tag 2 first.  Non-matching messages wait
     *    in the "unexpected message" queue, so this is legal and works.
     *    Ordering is only guaranteed among messages that match the same
     *    receive (same source, same communicator). */
    if (rank == 0) {
        int a = 111, b = 222;
        MPI_Send(&a, 1, MPI_INT, 1, 1, MPI_COMM_WORLD);
        MPI_Send(&b, 1, MPI_INT, 1, 2, MPI_COMM_WORLD);
    } else if (rank == 1) {
        int a = 0, b = 0;
        MPI_Recv(&b, 1, MPI_INT, 0, 2, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Recv(&a, 1, MPI_INT, 0, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("rank 1: tag 2 gave %d, tag 1 gave %d\n", b, a);
        CHECK(a == 111 && b == 222, "tag matching");
    }

    /* 3. Ring shift with MPI_Sendrecv: send to the right, receive from the
     *    left, in ONE call that can never deadlock.  (Send then Recv on every
     *    rank may deadlock: see deadlock.c.) */
    int right = (rank + 1) % size, left = (rank - 1 + size) % size;
    int sendval = rank * rank, recvval = -1;
    MPI_Sendrecv(&sendval, 1, MPI_INT, right, 0,
                 &recvval, 1, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    CHECK(recvval == left * left, "ring: rank %d got %d, expected %d", rank, recvval, left * left);

    /* 4. MPI_Sendrecv_replace uses one buffer for both directions.  After
     *    `size` shifts every value is back where it started. */
    int v = rank;
    for (int step = 0; step < size; step++)
        MPI_Sendrecv_replace(&v, 1, MPI_INT, right, 0, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    CHECK(v == rank, "full ring rotation on rank %d gave %d", rank, v);

    /* 5. Unknown message length: MPI_Probe blocks until a matching message is
     *    available, fills a status, and leaves the message in the queue. */
    if (rank == 0) {
        int n = 17, *data = malloc(n * sizeof *data);
        for (int i = 0; i < n; i++) data[i] = i;
        MPI_Send(data, n, MPI_INT, 1, 3, MPI_COMM_WORLD);
        free(data);
    } else if (rank == 1) {
        MPI_Status st;
        int n;
        MPI_Probe(0, 3, MPI_COMM_WORLD, &st);
        MPI_Get_count(&st, MPI_INT, &n);
        int *data = malloc(n * sizeof *data);
        MPI_Recv(data, n, MPI_INT, 0, 3, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        printf("rank 1: probe announced %d ints, data[n-1] = %d\n", n, data[n - 1]);
        CHECK(n == 17 && data[16] == 16, "probe");
        free(data);
    }

    int total;
    MPI_Allreduce(&fails, &total, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    if (rank == 0) printf(total ? "sendrecv: %d checks FAILED\n" : "sendrecv: all checks OK\n", total);
    MPI_Finalize();
    return total ? 1 : 0;
}
