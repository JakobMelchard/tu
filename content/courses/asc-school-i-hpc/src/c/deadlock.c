/* deadlock.c - the classic exchange deadlock and four ways to avoid it.
 *
 * Every rank swaps a buffer of COUNT ints with its ring neighbours: send to
 * the right, receive from the left.
 *
 *   ./deadlock                       run all SAFE variants, check + time them
 *   ./deadlock --unsafe recv-first   every rank Recv then Send: ALWAYS deadlocks
 *   ./deadlock --unsafe send-first   every rank Send then Recv: deadlocks once
 *                                    the message is larger than the eager limit
 *                                    (try -n 1 to see it "work" by accident)
 *   -n COUNT   ints per message (default 1000000 = 4 MB, well above eager)
 *   -t SEC     alarm() timeout for unsafe runs (default 5); on timeout the
 *              process prints a message and exits 3, mpirun then kills the rest
 *
 * Safe variants: ordered (even ranks send first, odd ranks receive first),
 * sendrecv (MPI_Sendrecv), nonblocking (Irecv + Isend + Waitall) and bsend
 * (buffered send with a user-attached buffer; legal but rarely the best tool).
 */
#include <mpi.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int rank, size, left, right;

static void on_alarm(int sig) {
    (void)sig;
    const char msg[] = "\n*** DEADLOCK: no progress before the timeout, giving up ***\n";
    write(2, msg, sizeof msg - 1);   /* async-signal-safe, unlike printf */
    _exit(3);
}

static void fill(int *s, int *r, int n) {
    for (int i = 0; i < n; i++) { s[i] = rank; r[i] = -1; }
}
static int verify(const int *r, int n) {
    for (int i = 0; i < n; i++) if (r[i] != left) return 0;
    return 1;
}

/* --- unsafe ------------------------------------------------------------ */
static void recv_first(int *s, int *r, int n) {          /* everybody waits for a send that never comes */
    MPI_Recv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Send(s, n, MPI_INT, right, 0, MPI_COMM_WORLD);
}
static void send_first(int *s, int *r, int n) {          /* works only while MPI buffers the send (eager) */
    MPI_Send(s, n, MPI_INT, right, 0, MPI_COMM_WORLD);
    MPI_Recv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
}

/* --- safe -------------------------------------------------------------- */
static void ordered(int *s, int *r, int n) {             /* break the symmetry */
    if (rank % 2 == 0) {
        MPI_Send(s, n, MPI_INT, right, 0, MPI_COMM_WORLD);
        MPI_Recv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    } else {
        MPI_Recv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        MPI_Send(s, n, MPI_INT, right, 0, MPI_COMM_WORLD);
    }
}
static void sendrecv(int *s, int *r, int n) {            /* MPI does the ordering for you */
    MPI_Sendrecv(s, n, MPI_INT, right, 0, r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
}
static void nonblocking(int *s, int *r, int n) {         /* post everything, then wait */
    MPI_Request req[2];
    MPI_Irecv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, &req[0]);
    MPI_Isend(s, n, MPI_INT, right, 0, MPI_COMM_WORLD, &req[1]);
    MPI_Waitall(2, req, MPI_STATUSES_IGNORE);
}
static void bsend(int *s, int *r, int n) {               /* buffered: Bsend copies and returns at once */
    int bufsize = n * (int)sizeof(int) + MPI_BSEND_OVERHEAD;
    char *buf = malloc(bufsize);
    MPI_Buffer_attach(buf, bufsize);
    MPI_Bsend(s, n, MPI_INT, right, 0, MPI_COMM_WORLD);
    MPI_Recv(r, n, MPI_INT, left, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    MPI_Buffer_detach(&buf, &bufsize);   /* blocks until the buffered send is done */
    free(buf);
}

typedef void (*exchange_fn)(int *, int *, int);

static int run(const char *name, exchange_fn fn, int *s, int *r, int n) {
    fill(s, r, n);
    MPI_Barrier(MPI_COMM_WORLD);
    double t = MPI_Wtime();
    fn(s, r, n);
    t = MPI_Wtime() - t;
    int ok = verify(r, n), all_ok;
    double tmax;
    MPI_Allreduce(&ok, &all_ok, 1, MPI_INT, MPI_MIN, MPI_COMM_WORLD);
    MPI_Reduce(&t, &tmax, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);
    if (rank == 0) printf("%-12s %s  %8.3f ms\n", name, all_ok ? "OK  " : "FAIL", tmax * 1e3);
    return all_ok;
}

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    left = (rank - 1 + size) % size;
    right = (rank + 1) % size;

    int n = 1000000, timeout = 5;
    const char *unsafe = NULL;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-n") && i + 1 < argc) n = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-t") && i + 1 < argc) timeout = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--unsafe") && i + 1 < argc) unsafe = argv[++i];
        else { if (rank == 0) fprintf(stderr, "usage: %s [-n COUNT] [-t SEC] [--unsafe recv-first|send-first]\n", argv[0]); MPI_Abort(MPI_COMM_WORLD, 2); }
    }
    if (size < 2) { if (rank == 0) fprintf(stderr, "need at least 2 ranks\n"); MPI_Abort(MPI_COMM_WORLD, 1); }

    int *s = malloc(n * sizeof *s), *r = malloc(n * sizeof *r);
    if (rank == 0) printf("exchange of %d ints (%.1f MB) among %d ranks\n", n, n * 4e-6, size);

    int ok = 1;
    if (unsafe) {
        signal(SIGALRM, on_alarm);
        alarm(timeout);
        if (!strcmp(unsafe, "recv-first")) ok = run("recv-first", recv_first, s, r, n);
        else if (!strcmp(unsafe, "send-first")) ok = run("send-first", send_first, s, r, n);
        else { if (rank == 0) fprintf(stderr, "unknown unsafe mode %s\n", unsafe); MPI_Abort(MPI_COMM_WORLD, 2); }
        alarm(0);
        if (rank == 0) printf("(no deadlock this time; that does not make it correct)\n");
    } else {
        ok &= run("ordered", ordered, s, r, n);
        ok &= run("sendrecv", sendrecv, s, r, n);
        ok &= run("nonblocking", nonblocking, s, r, n);
        ok &= run("bsend", bsend, s, r, n);
        if (rank == 0) printf(ok ? "deadlock: all safe variants OK\n" : "deadlock: FAILED\n");
    }
    free(s); free(r);
    MPI_Finalize();
    return ok ? 0 : 1;
}
