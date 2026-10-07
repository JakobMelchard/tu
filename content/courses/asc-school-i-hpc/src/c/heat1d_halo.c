/* heat1d_halo.c - 1D heat equation with domain decomposition and halo exchange.
 *
 * Run: mpirun --oversubscribe -np 4 ./heat1d_halo [-N points] [-T time]
 *
 *   u_t = u_xx on (0,1),  u(0,t) = u(1,t) = 0,  u(x,0) = sin(pi x)
 *   exact: u(x,t) = exp(-pi^2 t) sin(pi x)
 *
 * Explicit Euler / central differences (FTCS):
 *   u_i^{n+1} = u_i^n + r (u_{i-1}^n - 2 u_i^n + u_{i+1}^n),   r = dt/dx^2 <= 1/2
 *
 * The N interior points are cut into contiguous blocks.  Each rank stores its
 * n_loc points plus one ghost cell on each side.  Per time step:
 *   1. halo exchange: send my first point to the left neighbour's right ghost
 *      and my last point to the right neighbour's left ghost (MPI_Sendrecv,
 *      neighbours at the domain edge are MPI_PROC_NULL, which makes the call a
 *      no-op and leaves the Dirichlet zero in the ghost cell),
 *   2. update all local points from the previous array.
 * Afterwards rank 0 gathers everything (MPI_Gatherv), runs the serial solver
 * on the same grid and compares: the two must agree BITWISE because every
 * point sees exactly the same arithmetic in the same order.
 */
#include <math.h>
#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const double PI = 3.14159265358979323846;

static void step(double *u, double *unew, int n, double r) {
    for (int i = 1; i <= n; i++)
        unew[i] = u[i] + r * (u[i - 1] - 2 * u[i] + u[i + 1]);
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    int N = 400;
    double T = 0.05;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-N") && i + 1 < argc) N = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-T") && i + 1 < argc) T = atof(argv[++i]);
    }
    double dx = 1.0 / (N + 1), r = 0.4, dt = r * dx * dx;
    int steps = (int)ceil(T / dt);
    T = steps * dt;

    /* block decomposition of global interior indices 1..N */
    int base = N / size, rem = N % size;
    int n = base + (rank < rem);                      /* my points */
    int off = rank * base + (rank < rem ? rank : rem); /* global index of my first point is off+1 */
    int left = rank > 0 ? rank - 1 : MPI_PROC_NULL;
    int right = rank < size - 1 ? rank + 1 : MPI_PROC_NULL;

    double *u = calloc(n + 2, sizeof *u), *unew = calloc(n + 2, sizeof *unew);
    for (int i = 1; i <= n; i++) u[i] = sin(PI * (off + i) * dx);
    /* u[0] and u[n+1] stay 0 on the edge ranks = Dirichlet boundary */

    MPI_Barrier(MPI_COMM_WORLD);
    double t_par = MPI_Wtime();
    for (int s = 0; s < steps; s++) {
        /* halo exchange: my u[1] -> left's ghost u[n+1];  my u[n] -> right's ghost u[0] */
        MPI_Sendrecv(&u[1], 1, MPI_DOUBLE, left, 0,
                     &u[n + 1], 1, MPI_DOUBLE, right, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Sendrecv(&u[n], 1, MPI_DOUBLE, right, 1,
                     &u[0], 1, MPI_DOUBLE, left, 1, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        step(u, unew, n, r);
        double *tmp = u; u = unew; unew = tmp;     /* swap, no copy */
    }
    t_par = MPI_Wtime() - t_par;

    /* gather the interior points on rank 0 */
    int counts[size], displs[size];
    for (int p = 0; p < size; p++) {
        counts[p] = base + (p < rem);
        displs[p] = p * base + (p < rem ? p : rem);
    }
    double *full = rank == 0 ? malloc(N * sizeof *full) : NULL;
    MPI_Gatherv(&u[1], n, MPI_DOUBLE, full, counts, displs, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    int ok = 1;
    if (rank == 0) {
        /* serial reference on the same grid */
        double *v = calloc(N + 2, sizeof *v), *vnew = calloc(N + 2, sizeof *vnew);
        for (int i = 1; i <= N; i++) v[i] = sin(PI * i * dx);
        double t_ser = MPI_Wtime();
        for (int s = 0; s < steps; s++) { step(v, vnew, N, r); double *tmp = v; v = vnew; vnew = tmp; }
        t_ser = MPI_Wtime() - t_ser;

        double diff = 0, err = 0, decay = exp(-PI * PI * T);
        for (int i = 0; i < N; i++) {
            diff = fmax(diff, fabs(full[i] - v[i + 1]));
            err = fmax(err, fabs(full[i] - decay * sin(PI * (i + 1) * dx)));
        }
        printf("N = %d, %d steps to T = %.4f, r = %.2f, %d ranks\n", N, steps, T, r, size);
        printf("max |parallel - serial| = %.3e (must be 0)\n", diff);
        printf("max |parallel - exact|  = %.3e (discretisation error, O(dx^2))\n", err);
        printf("time: parallel %.3f s, serial %.3f s, speedup %.2f\n", t_par, t_ser, t_ser / t_par);
        printf("(per step and rank: ~%d flops vs 2 messages; a small -N is latency-bound, try -N 20000 -T 0.0005)\n", 4 * n);
        ok = diff == 0.0 && err < 1e-3;
        printf(ok ? "heat1d_halo: OK\n" : "heat1d_halo: FAILED\n");
        free(v); free(vnew); free(full);
    }
    free(u); free(unew);
    MPI_Bcast(&ok, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Finalize();
    return ok ? 0 : 1;
}
