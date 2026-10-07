/* hello_mpi.c - the smallest complete MPI program.
 *
 * Build: mpicc -O2 -Wall hello_mpi.c -o hello_mpi
 * Run:   mpirun --oversubscribe -np 4 ./hello_mpi     (cluster: srun ./hello_mpi)
 *
 * Shows MPI_Init/MPI_Finalize, MPI_Comm_rank/MPI_Comm_size (who am I, how many
 * are we), MPI_Get_processor_name (which node am I on) and why output from
 * several processes interleaves arbitrarily unless you serialise it yourself.
 * The same binary runs on every process: SPMD, single program multiple data.
 */
#include <mpi.h>
#include <stdio.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);            /* nothing MPI before this line */

    int rank, size, len;
    char host[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);   /* 0 .. size-1 */
    MPI_Comm_size(MPI_COMM_WORLD, &size);   /* the -np N */
    MPI_Get_processor_name(host, &len);

    /* Unordered: each process prints as soon as it gets here. */
    printf("hello from rank %d of %d on %s\n", rank, size, host);
    fflush(stdout);

    /* Ordered: a token travels 0 -> 1 -> ... -> size-1; rank r prints only after
     * it received the token, so the lines come out in rank order (modulo the
     * launcher's stdout forwarding, which is usually but not formally in order). */
    int token = 0;
    if (rank > 0)
        MPI_Recv(&token, 1, MPI_INT, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    printf("ordered: rank %d says hi\n", rank);
    fflush(stdout);
    if (rank < size - 1)
        MPI_Send(&token, 1, MPI_INT, rank + 1, 0, MPI_COMM_WORLD);

    int ver, sub;
    MPI_Get_version(&ver, &sub);
    if (rank == 0) printf("MPI standard version %d.%d, %d processes\n", ver, sub, size);

    MPI_Finalize();                    /* nothing MPI after this line */
    return 0;
}
