/* collectives.c - every common collective, each checked against the value it
 * must produce, plus one derived datatype and one timing comparison.
 *
 * Run: mpirun --oversubscribe -np 4 ./collectives
 *
 * Collectives are called by ALL ranks of the communicator with matching
 * arguments; there are no tags.  "root" arguments matter only on the root.
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
    const int root = 0;

    /* Bcast: one buffer, same on everybody afterwards. */
    double params[3] = {0, 0, 0};
    if (rank == root) { params[0] = 1.5; params[1] = -2; params[2] = 42; }
    MPI_Bcast(params, 3, MPI_DOUBLE, root, MPI_COMM_WORLD);
    CHECK(params[2] == 42, "bcast on rank %d", rank);

    /* Scatter / Gather: root's array of size*3 is cut into equal chunks. */
    int *all = NULL, chunk[3];
    if (rank == root) { all = malloc(3 * size * sizeof *all); for (int i = 0; i < 3 * size; i++) all[i] = i; }
    MPI_Scatter(all, 3, MPI_INT, chunk, 3, MPI_INT, root, MPI_COMM_WORLD);
    CHECK(chunk[0] == 3 * rank && chunk[2] == 3 * rank + 2, "scatter on rank %d", rank);
    for (int i = 0; i < 3; i++) chunk[i] *= 2;
    MPI_Gather(chunk, 3, MPI_INT, all, 3, MPI_INT, root, MPI_COMM_WORLD);
    if (rank == root) { CHECK(all[3 * size - 1] == 2 * (3 * size - 1), "gather"); free(all); }

    /* Scatterv / Gatherv: uneven blocks, the pattern used for N points on P
     * ranks when P does not divide N (see heat1d_halo.c). */
    enum { N = 10 };
    int counts[size], displs[size];
    for (int r = 0; r < size; r++) {
        counts[r] = N / size + (r < N % size);
        displs[r] = r * (N / size) + (r < N % size ? r : N % size);
    }
    double *g = NULL, loc[N];
    if (rank == root) { g = malloc(N * sizeof *g); for (int i = 0; i < N; i++) g[i] = i * 0.5; }
    MPI_Scatterv(g, counts, displs, MPI_DOUBLE, loc, counts[rank], MPI_DOUBLE, root, MPI_COMM_WORLD);
    CHECK(loc[0] == displs[rank] * 0.5, "scatterv on rank %d", rank);
    MPI_Gatherv(loc, counts[rank], MPI_DOUBLE, g, counts, displs, MPI_DOUBLE, root, MPI_COMM_WORLD);
    if (rank == root) { CHECK(g[N - 1] == (N - 1) * 0.5, "gatherv"); free(g); }

    /* Allgather: everybody ends up with everybody's value. */
    int mine = rank * rank, *sq = malloc(size * sizeof *sq);
    MPI_Allgather(&mine, 1, MPI_INT, sq, 1, MPI_INT, MPI_COMM_WORLD);
    CHECK(sq[size - 1] == (size - 1) * (size - 1), "allgather on rank %d", rank);
    free(sq);

    /* Reduce / Allreduce / Scan with built-in ops.  Result of Reduce is only
     * valid on root; Allreduce = Reduce + Bcast. */
    int sum = -1, mx = -1, asum = -1, prefix = -1;
    MPI_Reduce(&rank, &sum, 1, MPI_INT, MPI_SUM, root, MPI_COMM_WORLD);
    MPI_Reduce(&rank, &mx, 1, MPI_INT, MPI_MAX, root, MPI_COMM_WORLD);
    MPI_Allreduce(&rank, &asum, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    MPI_Scan(&rank, &prefix, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);   /* inclusive prefix sum */
    if (rank == root) CHECK(sum == size * (size - 1) / 2 && mx == size - 1, "reduce");
    CHECK(asum == size * (size - 1) / 2, "allreduce on rank %d", rank);
    CHECK(prefix == rank * (rank + 1) / 2, "scan on rank %d", rank);

    /* MAXLOC: which rank holds the maximum?  Needs the paired type. */
    struct { double val; int loc; } in = { (rank == size - 1) ? 1e3 : (double)rank, rank }, out;
    MPI_Reduce(&in, &out, 1, MPI_DOUBLE_INT, MPI_MAXLOC, root, MPI_COMM_WORLD);
    if (rank == root) CHECK(out.loc == size - 1 && out.val == 1e3, "maxloc");

    /* Alltoall: a transpose.  send[j] goes to rank j and lands in its recv[rank]. */
    int *sendb = malloc(size * sizeof *sendb), *recvb = malloc(size * sizeof *recvb);
    for (int j = 0; j < size; j++) sendb[j] = 100 * rank + j;
    MPI_Alltoall(sendb, 1, MPI_INT, recvb, 1, MPI_INT, MPI_COMM_WORLD);
    for (int i = 0; i < size; i++) CHECK(recvb[i] == 100 * i + rank, "alltoall on rank %d", rank);
    free(sendb); free(recvb);

    /* Derived datatype: send column 1 of a 4x4 row-major matrix as a unit.
     * MPI_Type_vector(count=4 blocks, blocklength=1, stride=4 elements). */
    int mat[16];
    for (int i = 0; i < 16; i++) mat[i] = rank == root ? i : 0;
    MPI_Datatype column;
    MPI_Type_vector(4, 1, 4, MPI_INT, &column);
    MPI_Type_commit(&column);
    if (size >= 2) {
        if (rank == root) MPI_Send(&mat[1], 1, column, 1, 0, MPI_COMM_WORLD);
        else if (rank == 1) {
            int col[4];
            MPI_Recv(col, 4, MPI_INT, root, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE); /* 4 contiguous ints */
            CHECK(col[0] == 1 && col[1] == 5 && col[2] == 9 && col[3] == 13, "type_vector column");
            printf("rank 1 received column 1 via MPI_Type_vector: %d %d %d %d\n", col[0], col[1], col[2], col[3]);
        }
    }
    MPI_Type_free(&column);

    /* Barrier: nobody leaves before everybody arrived.  Almost never needed
     * for correctness in pure MPI code; used here only to line up timings. */
    const int M = 1 << 20;                       /* 4 MB broadcast */
    int *big = malloc(M * sizeof *big);
    for (int i = 0; i < M; i++) big[i] = rank == root ? i : 0;
    MPI_Barrier(MPI_COMM_WORLD);
    double t1 = MPI_Wtime();
    if (rank == root) for (int r = 1; r < size; r++) MPI_Send(big, M, MPI_INT, r, 5, MPI_COMM_WORLD);
    else MPI_Recv(big, M, MPI_INT, root, 5, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    t1 = MPI_Wtime() - t1;
    MPI_Barrier(MPI_COMM_WORLD);
    double t2 = MPI_Wtime();
    MPI_Bcast(big, M, MPI_INT, root, MPI_COMM_WORLD);
    t2 = MPI_Wtime() - t2;
    double t1m, t2m;
    MPI_Reduce(&t1, &t1m, 1, MPI_DOUBLE, MPI_MAX, root, MPI_COMM_WORLD);
    MPI_Reduce(&t2, &t2m, 1, MPI_DOUBLE, MPI_MAX, root, MPI_COMM_WORLD);
    CHECK(big[M - 1] == M - 1, "bcast payload on rank %d", rank);
    if (rank == root)
        printf("4 MB to %d ranks: %d sequential Sends %.2f ms, MPI_Bcast %.2f ms "
               "(Bcast scales like log2(P), the loop like P)\n", size - 1, size - 1, t1m * 1e3, t2m * 1e3);
    free(big);

    int total;
    MPI_Allreduce(&fails, &total, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    if (rank == root) printf(total ? "collectives: %d checks FAILED\n" : "collectives: all checks OK\n", total);
    MPI_Finalize();
    return total ? 1 : 0;
}
