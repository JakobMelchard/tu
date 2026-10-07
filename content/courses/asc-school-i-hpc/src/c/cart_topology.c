/* cart_topology.c - virtual topologies (notes/11).
 *
 * Block 3, day 3: "Virtual topologies".  Covers the ASC/HLRS lab
 * 06_virtual_cartesian_topologies (cart-create, cart-shift) with our own code:
 *
 *   1. MPI_Dims_create        - balanced factorisations, checked against P
 *   2. 1D periodic ring       - the block's running example, on a Cartesian
 *                               communicator; the answer is still P(P-1)/2
 *   3. MPI_Cart_shift         - source/destination order, and MPI_PROC_NULL at
 *                               a non-periodic boundary (no `if` needed)
 *   4. MPI_Cart_coords/_rank  - round trip
 *   5. MPI_Cart_sub           - row communicators of a 2D grid
 *
 *   mpicc -O2 -Wall -Wextra cart_topology.c -o cart_topology
 *   mpirun --oversubscribe -np 4 ./cart_topology
 */
#include <mpi.h>
#include <stdio.h>

static int failed = 0;

static void check(int rank, const char *what, long got, long want)
{
    if (got != want) {
        fprintf(stderr, "rank %d: %s = %ld, expected %ld\n", rank, what, got, want);
        failed = 1;
    }
}

int main(int argc, char **argv)
{
    int world_rank, size;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /* ---- 1. MPI_Dims_create ---------------------------------------------- */
    {
        int d2[2] = {0, 0}, d3[3] = {0, 0, 0}, dfix[2] = {2, 0};
        MPI_Dims_create(size, 2, d2);
        MPI_Dims_create(size, 3, d3);
        check(world_rank, "Dims_create 2D product", (long)d2[0] * d2[1], size);
        check(world_rank, "Dims_create 3D product", (long)d3[0] * d3[1] * d3[2], size);
        /* the factors come back in non-increasing order */
        check(world_rank, "Dims_create 2D ordered", d2[0] >= d2[1], 1);
        if (size % 2 == 0) {
            MPI_Dims_create(size, 2, dfix);      /* first dimension fixed at 2 */
            check(world_rank, "Dims_create with a fixed dim", dfix[0], 2);
            check(world_rank, "Dims_create with a fixed dim", (long)dfix[0] * dfix[1], size);
        }
        if (world_rank == 0)
            printf("MPI_Dims_create(%d, 2) = %d x %d ; (%d, 3) = %d x %d x %d\n",
                   size, d2[0], d2[1], size, d3[0], d3[1], d3[2]);
    }

    /* ---- 2. the ring on a 1D periodic Cartesian communicator -------------- */
    MPI_Comm ring;
    int dims[1]    = {size};
    int periods[1] = {1};            /* periodic: the ring wraps */
    int reorder    = 1;              /* MPI may renumber; the sum is invariant */
    MPI_Cart_create(MPI_COMM_WORLD, 1, dims, periods, reorder, &ring);

    int my_rank, coord;
    MPI_Comm_rank(ring, &my_rank);           /* query the NEW communicator */
    MPI_Cart_coords(ring, my_rank, 1, &coord);
    check(world_rank, "Cart_coords of my own rank", coord, my_rank);

    int back;
    MPI_Cart_rank(ring, &coord, &back);
    check(world_rank, "Cart_rank(Cart_coords(r)) == r", back, my_rank);

    int left, right;
    MPI_Cart_shift(ring, 0, 1, &left, &right);   /* (source, destination) */
    check(world_rank, "periodic left  neighbour", left,  (my_rank - 1 + size) % size);
    check(world_rank, "periodic right neighbour", right, (my_rank + 1) % size);

    int snd = my_rank, rcv, sum = 0;
    MPI_Request req;
    for (int i = 0; i < size; i++) {
        /* Issend, not Isend: a synchronous send cannot be rescued by buffering,
           so this loop proves the exchange is correct and not merely lucky. */
        MPI_Issend(&snd, 1, MPI_INT, right, 17, ring, &req);
        MPI_Recv(&rcv, 1, MPI_INT, left, 17, ring, MPI_STATUS_IGNORE);
        MPI_Wait(&req, MPI_STATUS_IGNORE);
        snd = rcv;
        sum += rcv;
    }
    check(world_rank, "ring sum on a Cartesian communicator", sum, (long)size * (size - 1) / 2);
    printf("PE world %2d -> cart %2d: ring sum = %d (expected %d)\n",
           world_rank, my_rank, sum, size * (size - 1) / 2);
    fflush(stdout);

    /* ---- 3. a NON-periodic dimension gives MPI_PROC_NULL at the edges ----- */
    {
        MPI_Comm line;
        int d[1] = {size}, p[1] = {0};       /* not periodic */
        MPI_Cart_create(MPI_COMM_WORLD, 1, d, p, 0, &line);
        int r, lo, hi;
        MPI_Comm_rank(line, &r);
        MPI_Cart_shift(line, 0, 1, &lo, &hi);
        if (r == 0)        check(world_rank, "left edge is MPI_PROC_NULL", lo, MPI_PROC_NULL);
        if (r == size - 1) check(world_rank, "right edge is MPI_PROC_NULL", hi, MPI_PROC_NULL);

        /* the payoff: the SAME line works on the edges and in the interior. */
        int send = r, recv = -1;
        MPI_Sendrecv(&send, 1, MPI_INT, hi, 0,
                     &recv, 1, MPI_INT, lo, 0, line, MPI_STATUS_IGNORE);
        /* a receive from MPI_PROC_NULL leaves the buffer untouched */
        check(world_rank, "shift on a line", recv, r == 0 ? -1 : r - 1);
        MPI_Comm_free(&line);
    }

    /* ---- 4. MPI_Cart_sub: rows of a 2D grid ------------------------------ */
    {
        int d[2] = {0, 0}, p[2] = {0, 0};
        MPI_Dims_create(size, 2, d);
        MPI_Comm grid;
        MPI_Cart_create(MPI_COMM_WORLD, 2, d, p, 0, &grid);

        int r, c[2];
        MPI_Comm_rank(grid, &r);
        MPI_Cart_coords(grid, r, 2, c);

        int keep[2] = {0, 1};              /* keep dimension 1 -> one comm per row */
        MPI_Comm row;
        MPI_Cart_sub(grid, keep, &row);
        int row_rank, row_size, row_sum;
        MPI_Comm_rank(row, &row_rank);
        MPI_Comm_size(row, &row_size);
        MPI_Allreduce(&c[1], &row_sum, 1, MPI_INT, MPI_SUM, row);

        check(world_rank, "row size", row_size, d[1]);
        check(world_rank, "row rank == column coordinate", row_rank, c[1]);
        /* the column coordinates in one row are 0 .. d[1]-1 */
        check(world_rank, "row sum of column coords", row_sum, (long)d[1] * (d[1] - 1) / 2);

        if (world_rank == 0)
            printf("2D grid %d x %d: row communicators of size %d\n", d[0], d[1], row_size);
        MPI_Comm_free(&row);
        MPI_Comm_free(&grid);
    }

    MPI_Comm_free(&ring);

    int any_failed = 0;
    MPI_Allreduce(&failed, &any_failed, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
    if (world_rank == 0) printf("cart_topology: %s\n", any_failed ? "FAILED" : "all checks OK");

    MPI_Finalize();
    return any_failed;
}
