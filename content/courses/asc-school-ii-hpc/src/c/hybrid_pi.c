/* hybrid_pi.c - MPI + OpenMP midpoint rule for pi (notes/01).
 *
 *   pi = int_0^1 4/(1+x^2) dx  ~  h * sum_{i=0}^{N-1} f((i+1/2) h),  h = 1/N
 *
 * Two levels of decomposition: MPI gives each rank a contiguous block of the
 * N intervals, OpenMP splits that block among the rank's threads.  MPI is
 * called only outside the parallel region (the "masteronly" style), so
 * MPI_THREAD_FUNNELED suffices; the program checks that the library grants it.
 *
 * Checks (exit 1 on failure):
 *   1. |pi_N - pi| <= h^2/3 + 4 N eps: the midpoint-rule bound
 *      h^2/24 * max|f''| (max|f''| = 8 on [0,1]) plus the worst-case rounding
 *      of N additions of terms <= 4, times h;
 *   2. the result agrees with a serial sum on rank 0 within 2 N eps relative,
 *      i.e. the P x T decomposition changes only the summation order (the
 *      observed difference is printed and is orders of magnitude smaller);
 *   3. the total thread count seen via MPI_Allreduce equals P * OMP_NUM_THREADS.
 *
 * Build: see Makefile (mpicc + OpenMP flags).
 * Run:   OMP_NUM_THREADS=2 mpirun --oversubscribe -np 4 ./hybrid_pi [-n N]
 * Slurm: ../sh/slurm_templates/hybrid.sbatch
 */
#include <float.h>
#include <math.h>
#include <mpi.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static double f(double x) { return 4.0 / (1.0 + x * x); }

/* Block distribution of N items over P owners: the first N%P get one extra. */
static void block_range(long n, int p, int r, long *lo, long *hi)
{
    long q = n / p, rem = n % p;
    *lo = r * q + (r < rem ? r : rem);
    *hi = *lo + q + (r < rem ? 1 : 0);
}

int main(int argc, char **argv)
{
    int provided, rank, size;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long n = 20000000L;
    for (int a = 1; a < argc; a++)
        if (!strcmp(argv[a], "-n") && a + 1 < argc) n = atol(argv[++a]);

    if (provided < MPI_THREAD_FUNNELED) {
        if (rank == 0) fprintf(stderr, "MPI library gives thread level %d < FUNNELED\n", provided);
        MPI_Abort(MPI_COMM_WORLD, 2);
    }

    const double h = 1.0 / (double)n;
    long lo, hi;
    block_range(n, size, rank, &lo, &hi);

    MPI_Barrier(MPI_COMM_WORLD); /* timing only; never needed for correctness */
    double t0 = MPI_Wtime();

    double local = 0.0;
    int nthreads = 0;
    /* schedule(static): each thread gets one contiguous chunk, which keeps the
     * pages it touches on its own NUMA domain if the data were arrays. */
#pragma omp parallel reduction(+ : local)
    {
#pragma omp single
        nthreads = omp_get_num_threads();
#pragma omp for schedule(static)
        for (long i = lo; i < hi; i++) local += f(((double)i + 0.5) * h);
    }
    local *= h;
    double t_compute = MPI_Wtime() - t0;

    double pi = 0.0;
    int threads_total = 0;
    MPI_Allreduce(&local, &pi, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
    MPI_Allreduce(&nthreads, &threads_total, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    double t_total = MPI_Wtime() - t0;

    /* Max over ranks: the slowest rank is the runtime of the program. */
    double t_compute_max, t_total_max;
    MPI_Reduce(&t_compute, &t_compute_max, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    MPI_Reduce(&t_total, &t_total_max, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    int ok = 1;
    if (rank == 0) {
        const char *lvl[] = {"SINGLE", "FUNNELED", "SERIALIZED", "MULTIPLE"};
        int li = provided == MPI_THREAD_SINGLE       ? 0
                 : provided == MPI_THREAD_FUNNELED   ? 1
                 : provided == MPI_THREAD_SERIALIZED ? 2
                                                     : 3;
        printf("hybrid_pi: N=%ld  P=%d ranks x T=%d threads (rank 0)  thread level %s\n",
               n, size, nthreads, lvl[li]);

        /* 1. discretisation error bound + rounding allowance (N adds of ~4) */
        double err = fabs(pi - M_PI);
        double bound = h * h / 3.0 + 4.0 * (double)n * DBL_EPSILON;
        printf("  pi_N = %.15f   |pi_N - pi| = %.3e   bound %.3e\n", pi, err, bound);
        if (!(err <= bound)) { printf("  FAIL: error above midpoint bound\n"); ok = 0; }

        /* 2. serial reference: same N, one summation order */
        double serial = 0.0;
        for (long i = 0; i < n; i++) serial += f(((double)i + 0.5) * h);
        serial *= h;
        double rel = fabs(pi - serial) / serial;
        printf("  serial reference %.15f   rel. diff %.2e (summation order only)\n", serial, rel);
        if (!(rel <= 2.0 * (double)n * DBL_EPSILON)) { printf("  FAIL: decomposition changed the result\n"); ok = 0; }

        /* 3. thread accounting */
        const char *env = getenv("OMP_NUM_THREADS");
        if (env && *env) {
            int expect = size * atoi(env);
            printf("  threads in total %d, expected P*OMP_NUM_THREADS = %d\n", threads_total, expect);
            if (threads_total != expect) { printf("  FAIL: thread count\n"); ok = 0; }
        }
        printf("  time: compute %.4f s, compute+allreduce %.4f s (max over ranks)\n",
               t_compute_max, t_total_max);
        printf("%s\n", ok ? "hybrid_pi: OK" : "hybrid_pi: FAILED");
    }
    MPI_Bcast(&ok, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Finalize();
    return ok ? 0 : 1;
}
