/* hybrid_omp_mpi.c - OpenMP threads inside MPI ranks.
 *
 * Build (macOS/Apple clang):
 *   mpicc -O2 -Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include \
 *         hybrid_omp_mpi.c -o hybrid_omp_mpi -L/opt/homebrew/opt/libomp/lib -lomp
 * Build (Linux/GCC):  mpicc -O2 -fopenmp hybrid_omp_mpi.c -o hybrid_omp_mpi
 * Run:  OMP_NUM_THREADS=2 mpirun --oversubscribe -np 4 ./hybrid_omp_mpi
 * Cluster: one rank per socket/node, OMP_NUM_THREADS = cores per rank,
 *          see ../sh/slurm/hybrid.sbatch
 *
 * Same integral as pi_reduce.c.  Work is split twice: MPI cuts the interval
 * into one block per rank (distributed memory, explicit messages), OpenMP
 * cuts each block among the threads of the rank (shared memory, no messages).
 * MPI_Init_thread with MPI_THREAD_FUNNELED: only the thread that called
 * MPI_Init_thread (the master) makes MPI calls, which is all this code needs.
 */
#include <math.h>
#include <mpi.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>

static const double PI_REF = 3.14159265358979323846;

int main(int argc, char **argv) {
    int provided;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
    int rank, size, len;
    char host[MPI_MAX_PROCESSOR_NAME];
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Get_processor_name(host, &len);
    if (provided < MPI_THREAD_FUNNELED) {
        if (rank == 0) fprintf(stderr, "MPI library does not support MPI_THREAD_FUNNELED\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    long n = argc > 1 ? atol(argv[1]) : 100000000L;
    double h = 1.0 / n;
    long base = n / size, rem = n % size;
    long lo = rank * base + (rank < rem ? rank : rem), hi = lo + base + (rank < rem);

    int nthreads = 1;
    MPI_Barrier(MPI_COMM_WORLD);
    double t = MPI_Wtime(), part = 0;
    /* threads share `part` through the reduction clause; nothing MPI in here */
    #pragma omp parallel reduction(+ : part)
    {
        #pragma omp master
        nthreads = omp_get_num_threads();
        #pragma omp for schedule(static)
        for (long i = lo; i < hi; i++) {
            double x = (i + 0.5) * h;
            part += 4.0 / (1.0 + x * x);
        }
    }
    part *= h;
    double pi;
    MPI_Allreduce(&part, &pi, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);   /* master thread only */
    t = MPI_Wtime() - t;

    printf("rank %d on %s: %d threads, points [%ld, %ld)\n", rank, host, nthreads, lo, hi);
    int ok = fabs(pi - PI_REF) < 1e-8;
    if (rank == 0) {
        const char *lvl[] = {"SINGLE", "FUNNELED", "SERIALIZED", "MULTIPLE"};
        printf("thread support: %s; %d ranks x %d threads = %d workers; pi = %.15f, err %.1e, %.3f s\n",
               lvl[provided], size, nthreads, size * nthreads, pi, fabs(pi - PI_REF), t);
        printf(ok ? "hybrid_omp_mpi: OK\n" : "hybrid_omp_mpi: FAILED\n");
    }
    MPI_Finalize();
    return ok ? 0 : 1;
}
