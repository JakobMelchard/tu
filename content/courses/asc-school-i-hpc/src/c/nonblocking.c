/* nonblocking.c - MPI_Isend / MPI_Irecv / MPI_Wait and friends.
 *
 * Run: mpirun --oversubscribe -np 4 ./nonblocking
 *
 * Rules demonstrated:
 *   - a non-blocking call returns immediately with an MPI_Request; the
 *     buffer belongs to MPI until MPI_Wait/MPI_Test says the request is done,
 *   - post receives early (before the matching sends) to avoid unexpected-
 *     message copies and to make deadlock impossible,
 *   - MPI_Waitall / MPI_Waitany / MPI_Test for several outstanding requests,
 *   - overlapping communication with independent computation.
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
    if (size < 2) { if (rank == 0) fprintf(stderr, "need at least 2 ranks\n"); MPI_Abort(MPI_COMM_WORLD, 1); }
    int left = (rank - 1 + size) % size, right = (rank + 1) % size;

    /* 1. Ring exchange in both directions: 4 requests, one Waitall.  With
     *    blocking calls this needs careful ordering; here order is irrelevant. */
    int send_r = rank, send_l = -rank, from_l = 99, from_r = 99;
    MPI_Request req[4];
    MPI_Irecv(&from_l, 1, MPI_INT, left, 0, MPI_COMM_WORLD, &req[0]);
    MPI_Irecv(&from_r, 1, MPI_INT, right, 1, MPI_COMM_WORLD, &req[1]);
    MPI_Isend(&send_r, 1, MPI_INT, right, 0, MPI_COMM_WORLD, &req[2]);
    MPI_Isend(&send_l, 1, MPI_INT, left, 1, MPI_COMM_WORLD, &req[3]);
    /* from_l / send_r etc. must NOT be read or written here */
    MPI_Waitall(4, req, MPI_STATUSES_IGNORE);
    CHECK(from_l == left && from_r == -right, "ring both ways on rank %d: %d %d", rank, from_l, from_r);

    /* 2. Overlap: send a large array to the right neighbour while computing
     *    something that does not touch the buffers.  Compare with the
     *    blocking version (communicate, then compute).  On a laptop with
     *    shared memory the gain is small or zero; on a cluster with an
     *    interconnect that progresses in hardware it can be substantial. */
    const int N = 1 << 22;                       /* 4 M doubles = 32 MB */
    double *sbuf = malloc(N * sizeof *sbuf), *rbuf = malloc(N * sizeof *rbuf);
    double *work = malloc(N * sizeof *work);
    for (int i = 0; i < N; i++) { sbuf[i] = rank; work[i] = i * 1e-9; }
    volatile double sink = 0;
    double t_block, t_overlap, acc;

    MPI_Barrier(MPI_COMM_WORLD);
    t_block = MPI_Wtime();
    MPI_Sendrecv(sbuf, N, MPI_DOUBLE, right, 0, rbuf, N, MPI_DOUBLE, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    acc = 0; for (int i = 0; i < N; i++) acc += work[i] * work[i];
    sink += acc;
    t_block = MPI_Wtime() - t_block;

    MPI_Barrier(MPI_COMM_WORLD);
    t_overlap = MPI_Wtime();
    MPI_Irecv(rbuf, N, MPI_DOUBLE, left, 0, MPI_COMM_WORLD, &req[0]);
    MPI_Isend(sbuf, N, MPI_DOUBLE, right, 0, MPI_COMM_WORLD, &req[1]);
    acc = 0; for (int i = 0; i < N; i++) acc += work[i] * work[i];   /* independent work */
    sink += acc;
    MPI_Waitall(2, req, MPI_STATUSES_IGNORE);
    t_overlap = MPI_Wtime() - t_overlap;
    CHECK(rbuf[N - 1] == left, "overlap payload on rank %d", rank);
    if (rank == 0) printf("32 MB exchange + compute: blocking %.1f ms, overlapped %.1f ms\n", t_block * 1e3, t_overlap * 1e3);

    /* 3. MPI_Test: poll instead of block.  Count how often we polled; the
     *    number itself is meaningless, the pattern (do useful work between
     *    polls) is the point. */
    int flag = 0, polls = 0;
    MPI_Irecv(rbuf, N, MPI_DOUBLE, left, 2, MPI_COMM_WORLD, &req[0]);
    MPI_Isend(sbuf, N, MPI_DOUBLE, right, 2, MPI_COMM_WORLD, &req[1]);
    while (!flag) { MPI_Test(&req[0], &flag, MPI_STATUS_IGNORE); polls++; }
    MPI_Wait(&req[1], MPI_STATUS_IGNORE);
    if (rank == 0) printf("rank 0 polled MPI_Test %d times before the receive completed\n", polls);

    /* 4. MPI_Waitany: rank 0 collects one number from every other rank and
     *    handles each in the order it ARRIVES, not in rank order. */
    if (rank == 0) {
        int vals[size]; MPI_Request rq[size];
        for (int r = 1; r < size; r++) MPI_Irecv(&vals[r], 1, MPI_INT, r, 3, MPI_COMM_WORLD, &rq[r]);
        int sum = 0;
        for (int k = 1; k < size; k++) {
            int idx;
            MPI_Waitany(size - 1, rq + 1, &idx, MPI_STATUS_IGNORE);   /* idx is relative to rq+1 */
            sum += vals[idx + 1];
        }
        CHECK(sum == size * (size - 1) / 2 * 10, "waitany sum %d", sum);
        printf("rank 0 collected %d values via Waitany, sum %d\n", size - 1, sum);
    } else {
        MPI_Request rq;
        int v = 10 * rank;
        MPI_Isend(&v, 1, MPI_INT, 0, 3, MPI_COMM_WORLD, &rq);
        MPI_Wait(&rq, MPI_STATUS_IGNORE);          /* every request must be completed (or freed) */
    }

    free(sbuf); free(rbuf); free(work);
    int total;
    MPI_Allreduce(&fails, &total, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    if (rank == 0) printf(total ? "nonblocking: %d checks FAILED\n" : "nonblocking: all checks OK\n", total);
    MPI_Finalize();
    return total ? 1 : 0;
}
