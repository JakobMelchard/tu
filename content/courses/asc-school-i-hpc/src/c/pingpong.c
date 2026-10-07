/* pingpong.c - measure point-to-point latency and bandwidth.
 *
 * Run: mpirun --oversubscribe -np 2 ./pingpong [--quick] [--max-bytes N]
 *      (extra ranks just wait; on a cluster run once with both ranks on one
 *       node and once with --ntasks-per-node=1 to compare intra- vs inter-node)
 *
 * Rank 0 sends a message of s bytes to rank 1, rank 1 sends it straight back.
 * Half the round-trip time is the one-way time t(s).  The simple model
 *     t(s) = t_lat + s / B
 * gives the latency t_lat = t(0) and the asymptotic bandwidth B = s / t(s)
 * for large s.  n_1/2 is the message size at which half of B is reached; it
 * tells you how big a message must be before bandwidth matters more than
 * latency.  Compare with ../../notes/10-patterns-and-performance.md.
 */
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    if (size < 2) { if (rank == 0) fprintf(stderr, "need at least 2 ranks\n"); MPI_Abort(MPI_COMM_WORLD, 1); }

    long max_bytes = 1L << 22;      /* 4 MiB */
    int quick = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--quick")) quick = 1;
        else if (!strcmp(argv[i], "--max-bytes") && i + 1 < argc) max_bytes = atol(argv[++i]);
    }

    char *buf = malloc(max_bytes > 0 ? max_bytes : 1);
    memset(buf, 1, max_bytes);

    if (rank == 0) {
        printf("ping-pong between rank 0 and rank 1 (%d ranks in total)\n", size);
        printf("%12s %14s %14s\n", "bytes", "one-way [us]", "bandwidth [MB/s]");
    }

    double best_bw = 0, lat0 = 0;
    long n_half = -1;
    /* sizes 0, 1, 2, 4, ..., max_bytes */
    for (long s = 0; s <= max_bytes; s = (s == 0) ? 1 : s * 2) {
        int reps = s < 16384 ? 1000 : s < (1L << 20) ? 200 : 40;
        if (quick) reps /= 10;
        int warm = 5;
        double t = 0;
        for (int i = 0; i < warm + reps; i++) {
            if (i == warm) { MPI_Barrier(MPI_COMM_WORLD); t = MPI_Wtime(); }
            if (rank == 0) {
                MPI_Send(buf, s, MPI_BYTE, 1, 0, MPI_COMM_WORLD);
                MPI_Recv(buf, s, MPI_BYTE, 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            } else if (rank == 1) {
                MPI_Recv(buf, s, MPI_BYTE, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
                MPI_Send(buf, s, MPI_BYTE, 0, 0, MPI_COMM_WORLD);
            } else if (i == warm) {
                /* idle ranks only take part in the barrier */
            }
        }
        if (rank == 0) {
            double one_way = (MPI_Wtime() - t) / reps / 2;     /* seconds */
            double bw = s / one_way / 1e6;                     /* MB/s (10^6) */
            printf("%12ld %14.2f %14.1f\n", s, one_way * 1e6, bw);
            if (s == 0) lat0 = one_way;
            if (bw > best_bw) best_bw = bw;
        }
        if (s == max_bytes) break;
    }
    if (rank == 0) {
        /* second pass over the printed numbers is not needed: recompute n_1/2
         * from the model t = lat + s/B  ->  bw(s) = B/2  when  s = lat * B */
        n_half = (long)(lat0 * best_bw * 1e6);
        printf("\nlatency t(0)         = %.2f us\n", lat0 * 1e6);
        printf("peak bandwidth B      = %.1f MB/s\n", best_bw);
        printf("n_1/2 = t_lat * B     ~ %ld bytes  (messages below this are latency-bound)\n", n_half);
    }
    free(buf);
    MPI_Finalize();
    return 0;
}
