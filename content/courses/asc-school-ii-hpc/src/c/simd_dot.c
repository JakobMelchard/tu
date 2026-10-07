/* simd_dot.c - scalar vs vectorised dot product (notes/03).
 *
 * Four ways to compute s = sum_i x_i y_i:
 *   scalar    plain loop.  Under strict IEEE semantics (no -ffast-math) the
 *             compiler may NOT reorder the additions, so it cannot vectorise
 *             the reduction: one add per cycle-latency, one lane.
 *   unroll4   four independent accumulators written by hand: breaks the
 *             dependency chain (latency -> throughput), still scalar lanes.
 *   omp_simd  `#pragma omp simd reduction(+:s)`: we grant the reassociation,
 *             the compiler vectorises.  Needs only -fopenmp-simd, no runtime.
 *   intrin    NEON (arm64) or AVX2+FMA (x86 with -march=native) intrinsics,
 *             4 vector accumulators.  Skipped if neither ISA is enabled.
 *
 * Two sizes: one that fits in L1 (compute bound) and one far larger than the
 * last-level cache (memory bound).  2 flops per 16 bytes loaded is an
 * arithmetic intensity of 1/8 flop/byte, left of every ridge point: from
 * memory the vector variants run into the bandwidth roof I*B, the scalar one
 * stays below it because its add chain is latency-bound (notes/03).
 *
 * Checks (exit 1 on failure):
 *   1. integer-valued data: every variant equals the exact int64 sum;
 *   2. random data: variants differ only by rounding,
 *      |s_a - s_b| <= 2 n eps sum|x_i y_i|.
 *
 * Build: cc -O2 -fopenmp-simd simd_dot.c -o simd_dot -lm   (Makefile)
 * Run:   ./simd_dot [--quick]      `make vecreport` shows what was vectorised
 */
#include <float.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#if defined(__ARM_NEON)
#include <arm_neon.h>
#define ISA "NEON"
#elif defined(__AVX2__) && defined(__FMA__)
#include <immintrin.h>
#define ISA "AVX2+FMA"
#else
#define ISA NULL
#endif

typedef double (*dot_fn)(const double *, const double *, long);

__attribute__((noinline)) static double dot_scalar(const double *x, const double *y, long n)
{
    double s = 0.0;
#if defined(__clang__)
#pragma clang loop vectorize(disable) interleave(disable)
#endif
    for (long i = 0; i < n; i++) s += x[i] * y[i];
    return s;
}

__attribute__((noinline)) static double dot_unroll4(const double *x, const double *y, long n)
{
    double s0 = 0, s1 = 0, s2 = 0, s3 = 0;
    long i = 0;
#if defined(__clang__)
#pragma clang loop vectorize(disable) interleave(disable)
#endif
    for (; i + 4 <= n; i += 4) {
        s0 += x[i] * y[i];
        s1 += x[i + 1] * y[i + 1];
        s2 += x[i + 2] * y[i + 2];
        s3 += x[i + 3] * y[i + 3];
    }
    for (; i < n; i++) s0 += x[i] * y[i];
    return (s0 + s1) + (s2 + s3);
}

__attribute__((noinline)) static double dot_omp_simd(const double *x, const double *y, long n)
{
    double s = 0.0;
#pragma omp simd reduction(+ : s)
    for (long i = 0; i < n; i++) s += x[i] * y[i];
    return s;
}

#if defined(__ARM_NEON)
__attribute__((noinline)) static double dot_intrin(const double *x, const double *y, long n)
{
    float64x2_t a0 = vdupq_n_f64(0), a1 = a0, a2 = a0, a3 = a0;
    long i = 0;
    for (; i + 8 <= n; i += 8) { /* 4 accumulators x 2 lanes */
        a0 = vfmaq_f64(a0, vld1q_f64(x + i), vld1q_f64(y + i));
        a1 = vfmaq_f64(a1, vld1q_f64(x + i + 2), vld1q_f64(y + i + 2));
        a2 = vfmaq_f64(a2, vld1q_f64(x + i + 4), vld1q_f64(y + i + 4));
        a3 = vfmaq_f64(a3, vld1q_f64(x + i + 6), vld1q_f64(y + i + 6));
    }
    double s = vaddvq_f64(vaddq_f64(vaddq_f64(a0, a1), vaddq_f64(a2, a3)));
    for (; i < n; i++) s += x[i] * y[i];
    return s;
}
#elif defined(__AVX2__) && defined(__FMA__)
__attribute__((noinline)) static double dot_intrin(const double *x, const double *y, long n)
{
    __m256d a0 = _mm256_setzero_pd(), a1 = a0, a2 = a0, a3 = a0;
    long i = 0;
    for (; i + 16 <= n; i += 16) { /* 4 accumulators x 4 lanes */
        a0 = _mm256_fmadd_pd(_mm256_loadu_pd(x + i), _mm256_loadu_pd(y + i), a0);
        a1 = _mm256_fmadd_pd(_mm256_loadu_pd(x + i + 4), _mm256_loadu_pd(y + i + 4), a1);
        a2 = _mm256_fmadd_pd(_mm256_loadu_pd(x + i + 8), _mm256_loadu_pd(y + i + 8), a2);
        a3 = _mm256_fmadd_pd(_mm256_loadu_pd(x + i + 12), _mm256_loadu_pd(y + i + 12), a3);
    }
    __m256d a = _mm256_add_pd(_mm256_add_pd(a0, a1), _mm256_add_pd(a2, a3));
    double t[4];
    _mm256_storeu_pd(t, a);
    double s = (t[0] + t[1]) + (t[2] + t[3]);
    for (; i < n; i++) s += x[i] * y[i];
    return s;
}
#endif

static const char *names[] = {"scalar", "unroll4", "omp_simd", "intrin"};
static dot_fn fns[] = {dot_scalar, dot_unroll4, dot_omp_simd,
#if defined(__ARM_NEON) || (defined(__AVX2__) && defined(__FMA__))
                       dot_intrin
#else
                       NULL
#endif
};
enum { NV = 4 };

static double now(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

/* Best-of-5 time per call, each sample long enough (>= ~20 ms) to be timed. */
static double time_fn(dot_fn f, const double *x, const double *y, long n, double *sink)
{
    long reps = 1;
    for (;;) {
        double t = now();
        for (long r = 0; r < reps; r++) {
            *sink += f(x, y, n);
            __asm__ volatile("" ::: "memory"); /* stop hoisting the call */
        }
        if (now() - t > 0.02) break;
        reps *= 2;
    }
    double best = 1e30;
    for (int k = 0; k < 5; k++) {
        double t = now();
        for (long r = 0; r < reps; r++) {
            *sink += f(x, y, n);
            __asm__ volatile("" ::: "memory");
        }
        double dt = (now() - t) / reps;
        if (dt < best) best = dt;
    }
    return best;
}

int main(int argc, char **argv)
{
    int quick = argc > 1 && !strcmp(argv[1], "--quick");
    int ok = 1;
    printf("simd_dot: intrinsics path %s\n", ISA ? ISA : "none (build with -march=native on x86)");

    /* ---- 1. exactness on integer-valued data ------------------------------ */
    long n = 1000003; /* odd: exercises every remainder loop */
    double *x = malloc(n * sizeof *x), *y = malloc(n * sizeof *y);
    int64_t exact = 0;
    for (long i = 0; i < n; i++) {
        x[i] = (double)(i % 7 + 1);
        y[i] = (double)(i % 5 - 1);
        exact += (int64_t)(i % 7 + 1) * (int64_t)(i % 5 - 1);
    }
    for (int v = 0; v < NV; v++) {
        if (!fns[v]) continue;
        double s = fns[v](x, y, n);
        if (s != (double)exact) { printf("  FAIL %s: %.1f != %lld\n", names[v], s, (long long)exact); ok = 0; }
    }
    printf("  integer data, n=%ld: all variants = %lld exactly: %s\n", n, (long long)exact,
           ok ? "yes" : "NO");

    /* ---- 2. rounding-only differences on random data ----------------------- */
    srand(42);
    double absum = 0.0;
    for (long i = 0; i < n; i++) {
        x[i] = 2.0 * rand() / RAND_MAX - 1.0;
        y[i] = 2.0 * rand() / RAND_MAX - 1.0;
        absum += fabs(x[i] * y[i]);
    }
    double ref = dot_scalar(x, y, n), bound = 2.0 * n * DBL_EPSILON * absum;
    for (int v = 1; v < NV; v++) {
        if (!fns[v]) continue;
        double d = fabs(fns[v](x, y, n) - ref);
        printf("  random data: |%s - scalar| = %.2e  (bound %.2e)\n", names[v], d, bound);
        if (!(d <= bound)) ok = 0;
    }
    free(x);
    free(y);

    /* ---- 3. timing: in-cache vs out-of-cache ------------------------------- */
    long sizes[2] = {2048, quick ? (1L << 22) : (1L << 24)};
    double sink = 0.0;
    for (int k = 0; k < 2; k++) {
        long m = sizes[k];
        double *a = malloc(m * sizeof *a), *b = malloc(m * sizeof *b);
        for (long i = 0; i < m; i++) { a[i] = 1.0 + 1e-9 * i; b[i] = 1.0 - 1e-9 * i; }
        printf("  n = %ld (%.1f MiB for x and y)\n", m, 2.0 * m * 8 / 1048576.0);
        double t_scalar = 0.0;
        for (int v = 0; v < NV; v++) {
            if (!fns[v]) continue;
            double t = time_fn(fns[v], a, b, m, &sink);
            if (v == 0) t_scalar = t;
            printf("    %-9s %8.3f ns/elem  %6.2f GFlop/s  %6.1f GB/s  speed-up %4.1fx\n",
                   names[v], 1e9 * t / m, 2.0 * m / t * 1e-9, 16.0 * m / t * 1e-9, t_scalar / t);
        }
        free(a);
        free(b);
    }
    printf("  (sink %.3g)\n%s\n", sink, ok ? "simd_dot: OK" : "simd_dot: FAILED");
    return ok ? 0 : 1;
}
