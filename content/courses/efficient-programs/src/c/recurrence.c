/* recurrence.c -- latency-bound vs throughput-bound loops (slides 16-19).
 *
 * A recurrence is a value that lives from one iteration to the next. If the
 * operation that produces it has latency L cycles, the loop cannot run faster
 * than L cycles per iteration whatever the width of the machine; the slides'
 * numbers on Rocket Lake (S3 p.16-18): int64 array sum 1.52 c/it, linked-list
 * sum 5 c/it (the load is on the chain), double sum 3.73 c/it (FP add latency
 * 4), the independent a[i] = a[i] + f loop 1.27 c/it and 0.16 c/it vectorised.
 * Cutting the chain into k independent accumulators divides the bound by k
 * until throughput (number of adders, load ports) takes over.
 *
 * Kernels, on a 4096-element array (32 KB of doubles; the list nodes are 16 B,
 * 64 KB: both stay in the M3's 128 KB L1d, the list would not fit a 48 KB
 * L1d), repeated; the timers bracket only the repeated kernel calls:
 *   sum1 / sum2 / sum4 / sum8   double sum with 1, 2, 4, 8 accumulators
 *   isum1 / isum4               the same, converted to int64 (add latency 1;
 *                               integer addition is associative, so clang
 *                               vectorises both at -O2, isum1 with
 *                               interleave 4, isum4 with interleave 2)
 *   list                        sum through a linked list laid out in order
 *                               (one dependent load per element)
 *   axpy                        a[i] = a[i] + f: no recurrence, vectorised
 * Integer-valued doubles make every summation order exact, so the sums are
 * compared bitwise.
 *
 * usage: ./recurrence [--ghz G]   demo (cycle estimates = ns x G, default 4.05,
 *                                 an assumed clock: macOS exposes none)
 *        ./recurrence --test | --bench
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"

#define N 4096

static double sum1(const double *a, size_t n)
{
    double r = 0;
    for (size_t i = 0; i < n; i++) r += a[i];
    return r;
}

static double sum2(const double *a, size_t n)
{
    double r0 = 0, r1 = 0;
    for (size_t i = 0; i < n; i += 2) { r0 += a[i]; r1 += a[i + 1]; }
    return r0 + r1;
}

static double sum4(const double *a, size_t n)
{
    double r0 = 0, r1 = 0, r2 = 0, r3 = 0;
    for (size_t i = 0; i < n; i += 4) { r0 += a[i]; r1 += a[i + 1]; r2 += a[i + 2]; r3 += a[i + 3]; }
    return (r0 + r1) + (r2 + r3);
}

static double sum8(const double *a, size_t n)
{
    double r[8] = {0};
    for (size_t i = 0; i < n; i += 8)
        for (int k = 0; k < 8; k++) r[k] += a[i + k];
    return ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
}

static double isum1(const double *a, size_t n)  /* integers, latency-1 add */
{
    long long r = 0;
    for (size_t i = 0; i < n; i++) r += (long long)a[i];
    return (double)r;
}

static double isum4(const double *a, size_t n)
{
    long long r0 = 0, r1 = 0, r2 = 0, r3 = 0;
    for (size_t i = 0; i < n; i += 4) {
        r0 += (long long)a[i]; r1 += (long long)a[i + 1];
        r2 += (long long)a[i + 2]; r3 += (long long)a[i + 3];
    }
    return (double)((r0 + r1) + (r2 + r3));
}

struct node { struct node *next; double val; };

static double list_sum(const struct node *p)
{
    double r = 0;
    while (p) { r += p->val; p = p->next; }
    return r;
}

static void axpy(double *a, size_t n, double f)
{
    for (size_t i = 0; i < n; i++) a[i] = a[i] + f;
}

typedef double (*sum_fn)(const double *, size_t);

static double bench_sum(sum_fn fn, const double *a, int reps, double *result)
{
    double (*volatile f)(const double *, size_t) = fn;
    double t0 = now_s(), acc = 0;
    for (int r = 0; r < reps; r++) acc += f(a, N);
    double t = now_s() - t0;
    *result = acc / reps;
    return 1e9 * t / ((double)reps * N);
}

int main(int argc, char **argv)
{
    double ghz = arg_double(argc, argv, "--ghz", 4.05);
    int test = has_arg(argc, argv, "--test");
    int reps = has_arg(argc, argv, "--bench") ? 200000 : (test ? 200 : 50000);

    static double a[N];
    static struct node nodes[N];
    for (size_t i = 0; i < N; i++) {
        a[i] = (double)((i * 31 + 7) % 13) - 6.0;  /* integers in [-6, 6] */
        nodes[i].val = a[i];
        nodes[i].next = i + 1 < N ? &nodes[i + 1] : NULL;
    }
    double exact = 0;
    for (size_t i = 0; i < N; i++) exact += a[i];

    struct { const char *name; sum_fn fn; } ks[] = {
        {"sum1  (1 chain, double)", sum1}, {"sum2  (2 chains)", sum2},
        {"sum4  (4 chains)", sum4}, {"sum8  (8 chains)", sum8},
        {"isum1 (1 chain, int64)", isum1}, {"isum4 (4 chains, int64)", isum4}};
    if (!test) printf("recurrence: %d-element array in L1, %d reps, cycles assume %.2f GHz\n", N, reps, ghz);
    for (size_t k = 0; k < sizeof ks / sizeof *ks; k++) {
        double res, ns = bench_sum(ks[k].fn, a, reps, &res);
        CHECK(res == exact, "%s: %g != %g", ks[k].name, res, exact);
        if (!test) printf("  %-24s %6.3f ns/elem  ~%5.2f cycles/elem\n", ks[k].name, ns, ns * ghz);
    }
    {   /* linked list: one dependent load per element */
        double (*volatile f)(const struct node *) = list_sum;
        double t0 = now_s(), acc = 0;
        for (int r = 0; r < reps; r++) acc += f(nodes);
        double ns = 1e9 * (now_s() - t0) / ((double)reps * N);
        CHECK(acc / reps == exact, "list sum wrong");
        if (!test) printf("  %-24s %6.3f ns/elem  ~%5.2f cycles/elem\n", "list  (dependent loads)", ns, ns * ghz);
    }
    {   /* axpy: no recurrence at all */
        void (*volatile f)(double *, size_t, double) = axpy;
        double t0 = now_s();
        for (int r = 0; r < reps; r++) f(a, N, r % 2 ? -1.0 : 1.0);
        double ns = 1e9 * (now_s() - t0) / ((double)reps * N);
        double s = 0; for (size_t i = 0; i < N; i++) s += a[i];
        CHECK(s == exact, "axpy did not return the array to its start value");
        if (!test) printf("  %-24s %6.3f ns/elem  ~%5.2f cycles/elem\n", "axpy  (independent)", ns, ns * ghz);
    }
    if (test) puts("recurrence: all 8 kernels return the exact sum");
    return 0;
}
