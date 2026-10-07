/* pi_reduce.c - parallel numerical integration with MPI_Reduce.
 *
 * Run: mpirun --oversubscribe -np 4 ./pi_reduce [n]
 *
 *   pi = int_0^1 4/(1+x^2) dx  ~  h * sum_{i=0}^{n-1} f((i+1/2) h),  h = 1/n
 *
 * The n midpoints are split into contiguous blocks, one per rank; every rank
 * sums its block; MPI_Reduce adds the partial sums on rank 0.  Rank 0 also
 * runs the serial loop to report the speedup.  The parallel result differs
 * from the serial one by a few ulp because the summation order changes.
 */
#include <math.h>
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

static const double PI_REF = 3.14159265358979323846;

static double f(double x) { return 4.0 / (1.0 + x * x); }

static double midpoint(long lo, long hi, double h) {
    double s = 0;
    for (long i = lo; i < hi; i++) s += f((i + 0.5) * h);
    return s * h;
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    long n = argc > 1 ? atol(argv[1]) : 100000000L;
    MPI_Bcast(&n, 1, MPI_LONG, 0, MPI_COMM_WORLD);     /* argv is the same everywhere with mpirun, but be explicit */
    double h = 1.0 / n;

    /* block decomposition: first n%size ranks get one extra point */
    long base = n / size, rem = n % size;
    long lo = rank * base + (rank < rem ? rank : rem);
    long hi = lo + base + (rank < rem);

    MPI_Barrier(MPI_COMM_WORLD);
    double t_par = MPI_Wtime();
    double part = midpoint(lo, hi, h), pi = 0;
    MPI_Reduce(&part, &pi, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);   /* pi valid on rank 0 only */
    t_par = MPI_Wtime() - t_par;

    int ok = 1;
    if (rank == 0) {
        double t_ser = MPI_Wtime();
        double pi_ser = midpoint(0, n, h);
        t_ser = MPI_Wtime() - t_ser;
        printf("n = %ld, %d ranks\n", n, size);
        printf("parallel: pi = %.15f  err = %.2e  %.3f s\n", pi, fabs(pi - PI_REF), t_par);
        printf("serial:   pi = %.15f  err = %.2e  %.3f s\n", pi_ser, fabs(pi_ser - PI_REF), t_ser);
        printf("speedup %.2f, efficiency %.0f%%\n", t_ser / t_par, 100 * t_ser / t_par / size);
        ok = fabs(pi - PI_REF) < 1e-8;
        printf(ok ? "pi_reduce: OK\n" : "pi_reduce: FAILED\n");
    }
    MPI_Bcast(&ok, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Finalize();
    return ok ? 0 : 1;
}
