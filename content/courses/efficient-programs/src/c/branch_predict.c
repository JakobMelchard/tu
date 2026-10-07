/* branch_predict.c -- what a mispredicted branch costs.
 *
 * Kernel: copy the elements >= 128 of an array of values in [0, 256) into a
 * second array (a "filter"). Written with an if, the branch is taken at
 * random 50 % of the time for unsorted input and the predictor is useless;
 * for sorted input it is taken never, then always, and predicted correctly.
 * The conditional store keeps the compiler from turning the if into a select
 * (it cannot prove the unconditional store is in bounds), so the branch is
 * real; the branchless version does the unconditional store by hand:
 *   out[k] = v; k += (v >= 128);
 * Slide 14: correctly predicted branch 0-1 c, mispredicted ~20 c. Slide 49-51:
 * arithmetic with flags, long-circuiting.
 *
 * usage: ./branch_predict [--n N]   demo/bench, default n = 1 << 22
 *        ./branch_predict --test    results identical for all four runs
 *        ./branch_predict --bench   n = 1 << 24, prints ns/element and the
 *                                   estimated cost of one misprediction
 *        [--ghz G]                  cycles = ns x G, default 4.05: an assumed
 *                                   clock (macOS exposes none), so an estimate
 * Only the filter call is timed (best of reps); input generation, sorting and
 * the checks are outside the timer.
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"

static size_t filter_branch(const int *in, int *out, size_t n)
{
    size_t k = 0;
    for (size_t i = 0; i < n; i++)
        if (in[i] >= 128)
            out[k++] = in[i];
    return k;
}

static size_t filter_branchless(const int *in, int *out, size_t n)
{
    size_t k = 0;
    for (size_t i = 0; i < n; i++) {
        int v = in[i];
        out[k] = v;                 /* always store, advance only if kept */
        k += (size_t)(v >= 128);
    }
    return k;
}

static void counting_sort(int *a, size_t n)  /* values are in [0, 256) */
{
    size_t cnt[256] = {0};
    for (size_t i = 0; i < n; i++) cnt[a[i]]++;
    size_t p = 0;
    for (int v = 0; v < 256; v++)
        for (size_t c = 0; c < cnt[v]; c++) a[p++] = v;
}

/* order-independent fingerprint of the kept elements: their histogram */
static void histogram(const int *a, size_t k, size_t hist[256])
{
    memset(hist, 0, 256 * sizeof *hist);
    for (size_t i = 0; i < k; i++) hist[a[i]]++;
}

/* order-dependent fingerprint: branch and branchless must also keep the order */
static long long checksum(const int *a, size_t k)
{
    long long s = 0;
    for (size_t i = 0; i < k; i++) s += a[i] * (long long)(i % 1000 + 1);
    return s;
}

typedef size_t (*filter_fn)(const int *, int *, size_t);

static double time_filter(filter_fn fn, const int *in, int *out, size_t n, int reps,
                          size_t *k_out, long long *sum_out, size_t hist[256])
{
    size_t (*volatile f)(const int *, int *, size_t) = fn;  /* no inlining/hoisting */
    double best = 1e300;
    for (int r = 0; r < reps; r++) {
        double t0 = now_s();
        *k_out = f(in, out, n);
        double t = now_s() - t0;
        if (t < best) best = t;
    }
    *sum_out = checksum(out, *k_out);
    histogram(out, *k_out, hist);
    return best;
}

static void run(size_t n, int reps, int verbose, double ghz)
{
    int *in = malloc(n * sizeof *in), *sorted = malloc(n * sizeof *sorted);
    int *out = malloc((n + 1) * sizeof *out);
    CHECK(in && sorted && out, "oom");
    uint64_t seed = 7;
    for (size_t i = 0; i < n; i++) in[i] = (int)(rng_next(&seed) >> 56);  /* 0..255 */
    memcpy(sorted, in, n * sizeof *in);
    counting_sort(sorted, n);

    struct { const char *name; filter_fn fn; const int *data; } runs[] = {
        {"branch   unsorted", filter_branch, in}, {"branch   sorted  ", filter_branch, sorted},
        {"select   unsorted", filter_branchless, in}, {"select   sorted  ", filter_branchless, sorted}};
    size_t k[4], hist[4][256]; long long sum[4]; double t[4];
    for (int r = 0; r < 4; r++) {
        t[r] = time_filter(runs[r].fn, runs[r].data, out, n, reps, &k[r], &sum[r], hist[r]);
        if (verbose)
            printf("  %s  %8.2f ms  %6.3f ns/element\n", runs[r].name, 1e3 * t[r],
                   1e9 * t[r] / (double)n);
    }
    /* branch and branchless keep the same elements in the same order on the
       same input; unsorted and sorted input keep the same multiset (compared
       by histogram), and every kept element is >= 128 */
    CHECK(sum[0] == sum[2] && sum[1] == sum[3], "branch and branchless differ");
    for (int r = 0; r < 4; r++) {
        CHECK(k[r] == k[0], "count differs in run %d", r);
        CHECK(memcmp(hist[r], hist[0], sizeof hist[0]) == 0, "kept multiset differs in run %d", r);
    }
    size_t expect = 0;
    for (size_t i = 0; i < n; i++) expect += in[i] >= 128;
    CHECK(k[0] == expect, "kept %zu, expected %zu", k[0], expect);
    for (int v = 0; v < 128; v++) CHECK(hist[0][v] == 0, "kept a value < 128");
    if (verbose) {
        /* unsorted: ~n/2 mispredictions (random 50/50); sorted: ~0 */
        double per_miss = (t[0] - t[1]) / (0.5 * (double)n);
        printf("  kept %zu of %zu; est. misprediction cost %.2f ns = %.1f cycles at %.2f GHz\n",
               k[0], n, 1e9 * per_miss, per_miss * ghz * 1e9, ghz);
    }
    free(in); free(sorted); free(out);
}

int main(int argc, char **argv)
{
    double ghz = arg_double(argc, argv, "--ghz", 4.05);
    if (has_arg(argc, argv, "--test")) {
        run(1, 1, 0, ghz); run(1000, 1, 0, ghz); run(1 << 16, 1, 0, ghz);
        puts("branch_predict: branch and branchless filters agree on 3 sizes, sorted and unsorted");
        return 0;
    }
    if (has_arg(argc, argv, "--bench")) {
        puts("branch_predict --bench, n = 2^24, best of 5");
        run((size_t)1 << 24, 5, 1, ghz);
        return 0;
    }
    size_t n = (size_t)arg_long(argc, argv, "--n", 1 << 22);
    printf("branch_predict demo, n = %zu, best of 3\n", n);
    run(n, 3, 1, ghz);
    return 0;
}
