/* affinity_report.c - where did every rank and thread land? (notes/01)
 *
 * Every OpenMP thread of every MPI rank records host, rank, thread, the CPU it
 * is running on, its allowed-CPU mask, and its OpenMP place.  Rank 0 gathers
 * and prints one line per (rank, thread), sorted.  This is the first thing to
 * run in a new hybrid job: wrong pinning is the most common reason a hybrid
 * code is slower than pure MPI.
 *
 * Linux: sched_getcpu() and sched_getaffinity() give the real placement.
 * macOS: neither exists and threads cannot be pinned; the CPU columns read -1
 *        and the program still checks the bookkeeping.
 *
 * Checks (exit 1 on failure): exactly one row per (rank, thread) pair and
 * P * OMP_NUM_THREADS rows in total.  With binding active on Linux it also
 * warns when two threads of the same host share one CPU.
 *
 * Run:   OMP_NUM_THREADS=2 OMP_PROC_BIND=close OMP_PLACES=cores \
 *            mpirun --oversubscribe -np 4 ./affinity_report
 * On a cluster: srun --cpus-per-task=$SLURM_CPUS_PER_TASK ./affinity_report
 */
#define _GNU_SOURCE
#include <mpi.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#ifdef __linux__
#include <sched.h>
#endif

#define MAXT 256
#define HOSTLEN 64
#define MASKLEN 96

typedef struct {
    char host[HOSTLEN];
    int rank, thread, nthreads, cpu, place, nplaces;
    char mask[MASKLEN]; /* allowed CPUs as a compact list, e.g. "0-3,8" */
} row_t;

/* Allowed-CPU set of the calling thread as "a-b,c" (Linux only). */
static void cpu_mask_string(char *out, size_t len)
{
#ifdef __linux__
    cpu_set_t set;
    CPU_ZERO(&set);
    out[0] = '\0';
    if (sched_getaffinity(0, sizeof set, &set) != 0) { snprintf(out, len, "?"); return; }
    size_t used = 0;
    for (int c = 0; c < CPU_SETSIZE; c++) {
        if (!CPU_ISSET(c, &set)) continue;
        int e = c;
        while (e + 1 < CPU_SETSIZE && CPU_ISSET(e + 1, &set)) e++;
        int w = (e > c) ? snprintf(out + used, len - used, "%s%d-%d", used ? "," : "", c, e)
                        : snprintf(out + used, len - used, "%s%d", used ? "," : "", c);
        if (w < 0 || (size_t)w >= len - used) { snprintf(out + len - 4, 4, "..."); return; }
        used += (size_t)w;
        c = e;
    }
#else
    snprintf(out, len, "n/a");
#endif
}

static int current_cpu(void)
{
#ifdef __linux__
    return sched_getcpu();
#else
    return -1;
#endif
}

static int cmp_row(const void *a, const void *b)
{
    const row_t *x = a, *y = b;
    return x->rank != y->rank ? x->rank - y->rank : x->thread - y->thread;
}

int main(int argc, char **argv)
{
    int provided, rank, size;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    char host[HOSTLEN];
    gethostname(host, sizeof host);
    host[HOSTLEN - 1] = '\0';

    row_t mine[MAXT];
    memset(mine, 0, sizeof mine);
    int nt = 0;
#pragma omp parallel
    {
        int t = omp_get_thread_num();
#pragma omp single
        nt = omp_get_num_threads();
        if (t < MAXT) {
            row_t *r = &mine[t];
            snprintf(r->host, HOSTLEN, "%s", host);
            r->rank = rank;
            r->thread = t;
            r->nthreads = omp_get_num_threads();
            r->cpu = current_cpu();
            r->place = omp_get_place_num();  /* -1 if threads are not bound */
            r->nplaces = omp_get_num_places();
            cpu_mask_string(r->mask, MASKLEN);
        }
    }
    if (nt > MAXT) nt = MAXT;

    /* Ranks may run different thread counts: gather counts first, then rows. */
    int *counts = NULL, *displs = NULL;
    if (rank == 0) {
        counts = malloc(size * sizeof *counts);
        displs = malloc(size * sizeof *displs);
    }
    MPI_Gather(&nt, 1, MPI_INT, counts, 1, MPI_INT, 0, MPI_COMM_WORLD);
    int total = 0;
    if (rank == 0)
        for (int r = 0; r < size; r++) {
            displs[r] = total * (int)sizeof(row_t);
            total += counts[r];
            counts[r] *= (int)sizeof(row_t);
        }
    row_t *all = rank == 0 ? malloc((total ? total : 1) * sizeof(row_t)) : NULL;
    MPI_Gatherv(mine, nt * (int)sizeof(row_t), MPI_BYTE, all, counts, displs, MPI_BYTE, 0,
                MPI_COMM_WORLD);

    int ok = 1;
    if (rank == 0) {
        qsort(all, total, sizeof(row_t), cmp_row);
        const char *pb = getenv("OMP_PROC_BIND"), *pl = getenv("OMP_PLACES");
        printf("affinity_report: %d ranks, OMP_PROC_BIND=%s OMP_PLACES=%s, %d places\n", size,
               pb ? pb : "(unset)", pl ? pl : "(unset)", all[0].nplaces);
        printf("  %-16s %4s %6s %4s %5s  %s\n", "host", "rank", "thread", "cpu", "place", "allowed");
        for (int i = 0; i < total; i++)
            printf("  %-16.16s %4d %6d %4d %5d  %s\n", all[i].host, all[i].rank, all[i].thread,
                   all[i].cpu, all[i].place, all[i].mask);

        /* bookkeeping: rows are unique (rank, thread) pairs, threads 0..T-1 */
        for (int i = 1; i < total; i++)
            if (all[i].rank == all[i - 1].rank && all[i].thread == all[i - 1].thread) ok = 0;
        const char *env = getenv("OMP_NUM_THREADS");
        if (env && *env && total != size * atoi(env)) ok = 0;

        /* oversubscription warning: two threads on the same CPU of one host */
        int shared = 0;
        for (int i = 0; i < total; i++)
            for (int j = i + 1; j < total; j++)
                if (all[i].cpu >= 0 && all[i].cpu == all[j].cpu &&
                    !strcmp(all[i].host, all[j].host))
                    shared++;
        if (shared)
            printf("  note: %d pairs of threads report the same CPU (snapshot; pin to be sure)\n",
                   shared);
        printf("%s\n", ok ? "affinity_report: OK" : "affinity_report: FAILED");
        free(all);
        free(counts);
        free(displs);
    }
    MPI_Bcast(&ok, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Finalize();
    return ok ? 0 : 1;
}
