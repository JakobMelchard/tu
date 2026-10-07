/* matmul_steps.c -- C = A B for n x n doubles, row-major, five versions.
 *
 * The lecturer's example (refs/cite-only/S8-*, slides 86-96) walks from a
 * textbook triple loop to a blocked, vectorised kernel. These are our own
 * versions of the same steps, each checked bitwise against the first
 * (the inputs are small integers, so every summation order is exact):
 *
 *   ijk      textbook: one scalar accumulator per c[i][j]; the inner loop
 *            reads b[k][j] with stride n (one cache line per element) and
 *            every add depends on the previous one (a 1-term recurrence)
 *   ikj      loop interchange: the inner loop is c[i][:] += a[i][k] * b[k][:],
 *            stride 1 on b and c, no loop-carried dependence, vectorisable
 *   dotT     transpose B once, then a stride-1 dot product; the recurrence is
 *            cut by 4 independent accumulators (latency 4c / 4 chains)
 *   blocked  ikj inside bs x bs tiles, so the tile of B and the row block of
 *            C are re-used from L1/L2 instead of streaming from L3/DRAM
 *   ikj4     ikj with the k loop unrolled by 4: four a[i][k..k+3] in
 *            registers and one read-modify-write of c[i][j] per four products
 *            (the same idea as the lecturer's mm5)
 *
 * usage: ./matmul_steps [--n N]      demo, default n = 256
 *        ./matmul_steps --test        n = 1, 5, 33, 64, 100: all versions bit-identical
 *                                     to ijk, and ijk equal to an exact reference
 *                                     entry computed independently
 *        ./matmul_steps --bench       n = 512, 1024, one pass each
 * Reports ms, ns per inner iteration (n^3 of them) and GFLOP/s (2 n^3 flops).
 * Only the multiply is timed (dotT includes its transpose); allocation and
 * fill are outside the timer.
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"
#include <math.h>

#define BS 64  /* tile edge; 3 tiles of 64x64 doubles = 96 KB, fits L1+L2 */

static void mm_ijk(const double *a, const double *b, double *c, size_t n)
{
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < n; j++) {
            double r = 0.0;
            for (size_t k = 0; k < n; k++)
                r += a[i * n + k] * b[k * n + j];
            c[i * n + j] = r;
        }
}

static void mm_ikj(const double *a, const double *b, double *c, size_t n)
{
    memset(c, 0, n * n * sizeof *c);
    for (size_t i = 0; i < n; i++)
        for (size_t k = 0; k < n; k++) {
            double aik = a[i * n + k];
            for (size_t j = 0; j < n; j++)
                c[i * n + j] += aik * b[k * n + j];
        }
}

static void mm_dotT(const double *a, const double *b, double *c, size_t n, double *bt)
{
    for (size_t k = 0; k < n; k++)
        for (size_t j = 0; j < n; j++)
            bt[j * n + k] = b[k * n + j];
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < n; j++) {
            const double *ai = a + i * n, *bj = bt + j * n;
            double r0 = 0, r1 = 0, r2 = 0, r3 = 0;  /* 4 independent chains */
            size_t k = 0;
            for (; k + 4 <= n; k += 4) {
                r0 += ai[k] * bj[k];
                r1 += ai[k + 1] * bj[k + 1];
                r2 += ai[k + 2] * bj[k + 2];
                r3 += ai[k + 3] * bj[k + 3];
            }
            for (; k < n; k++)
                r0 += ai[k] * bj[k];
            c[i * n + j] = (r0 + r1) + (r2 + r3);
        }
}

static void mm_blocked(const double *a, const double *b, double *c, size_t n)
{
    memset(c, 0, n * n * sizeof *c);
    for (size_t ii = 0; ii < n; ii += BS)
        for (size_t kk = 0; kk < n; kk += BS)
            for (size_t jj = 0; jj < n; jj += BS) {
                size_t ie = ii + BS < n ? ii + BS : n;
                size_t ke = kk + BS < n ? kk + BS : n;
                size_t je = jj + BS < n ? jj + BS : n;
                for (size_t i = ii; i < ie; i++)
                    for (size_t k = kk; k < ke; k++) {
                        double aik = a[i * n + k];
                        for (size_t j = jj; j < je; j++)
                            c[i * n + j] += aik * b[k * n + j];
                    }
            }
}

static void mm_ikj4(const double *a, const double *b, double *c, size_t n)
{
    memset(c, 0, n * n * sizeof *c);
    for (size_t i = 0; i < n; i++) {
        size_t k = 0;
        for (; k + 4 <= n; k += 4) {
            double a0 = a[i * n + k], a1 = a[i * n + k + 1];
            double a2 = a[i * n + k + 2], a3 = a[i * n + k + 3];
            const double *b0 = b + k * n, *b1 = b0 + n, *b2 = b1 + n, *b3 = b2 + n;
            for (size_t j = 0; j < n; j++)
                c[i * n + j] += ((a0 * b0[j] + a1 * b1[j]) + (a2 * b2[j] + a3 * b3[j]));
        }
        for (; k < n; k++) {  /* remainder when n % 4 != 0 */
            double aik = a[i * n + k];
            for (size_t j = 0; j < n; j++)
                c[i * n + j] += aik * b[k * n + j];
        }
    }
}

/* integer-valued entries, a in [-3, 3], b in [-5, 5]: every product and
   partial sum is an integer below 2^53, so every summation order is exact.
   (The multipliers must not be multiples of the moduli, or the matrix is
   constant: an earlier (i * 7 + 3) % 7 made A identically zero.) */
static double a_val(size_t i) { return (double)((i * 5 + 2) % 7) - 3.0; }
static double b_val(size_t i) { return (double)((i * 3 + 1) % 11) - 5.0; }

static void fill(double *a, double *b, size_t n)
{
    for (size_t i = 0; i < n * n; i++) {
        a[i] = a_val(i);
        b[i] = b_val(i);
    }
}

/* independent check of ijk: c[i][j] recomputed from a_val/b_val, not from the arrays */
static void check_ref(const double *ref, size_t n)
{
    int nonzero = 0;
    for (size_t i = 0; i < n; i++)
        for (size_t j = 0; j < n; j++) {
            double s = 0.0;
            for (size_t k = 0; k < n; k++) s += a_val(i * n + k) * b_val(k * n + j);
            CHECK(ref[i * n + j] == s, "ijk wrong at (%zu,%zu), n=%zu", i, j, n);
            nonzero |= s != 0.0;
        }
    CHECK(n < 2 || nonzero, "degenerate test matrices (C == 0), n=%zu", n);
}

typedef void (*mm_fn)(const double *, const double *, double *, size_t);

struct version { const char *name; mm_fn fn; };

static double run_one(const char *name, size_t n, const double *a, const double *b,
                      double *c, double *bt, mm_fn fn, const double *ref, int quiet)
{
    double t0 = now_s();
    if (fn) fn(a, b, c, n); else mm_dotT(a, b, c, n, bt);
    double t = now_s() - t0;
    double its = (double)n * (double)n * (double)n;
    if (ref)
        for (size_t i = 0; i < n * n; i++)
            CHECK(c[i] == ref[i], "%s differs from ijk at %zu (n=%zu): %g vs %g",
                  name, i, n, c[i], ref[i]);
    if (!quiet)
        printf("  %-8s n=%5zu  %9.2f ms  %6.3f ns/it  %6.2f GFLOP/s%s\n", name, n,
               1e3 * t, 1e9 * t / its, 2.0 * its / t / 1e9, ref ? "  ok" : "");
    return t;
}

static void run_all(size_t n, int check, int quiet)
{
    double *a = malloc(n * n * sizeof *a), *b = malloc(n * n * sizeof *b);
    double *c = malloc(n * n * sizeof *c), *ref = malloc(n * n * sizeof *ref);
    double *bt = malloc(n * n * sizeof *bt);
    CHECK(a && b && c && ref && bt, "out of memory");
    fill(a, b, n);
    run_one("ijk", n, a, b, ref, bt, mm_ijk, NULL, quiet);
    if (check && n <= 128) check_ref(ref, n);
    const double *r = check ? ref : NULL;
    run_one("ikj", n, a, b, c, bt, mm_ikj, r, quiet);
    run_one("dotT", n, a, b, c, bt, NULL, r, quiet);
    run_one("blocked", n, a, b, c, bt, mm_blocked, r, quiet);
    run_one("ikj4", n, a, b, c, bt, mm_ikj4, r, quiet);
    free(a); free(b); free(c); free(ref); free(bt);
}

int main(int argc, char **argv)
{
    if (has_arg(argc, argv, "--test")) {
        size_t sizes[] = {1, 5, 33, 64, 100};
        for (size_t s = 0; s < sizeof sizes / sizeof *sizes; s++)
            run_all(sizes[s], 1, 1);
        puts("matmul_steps: ijk exact and all versions bit-identical to it for n = 1, 5, 33, 64, 100");
        return 0;
    }
    if (has_arg(argc, argv, "--bench")) {
        puts("matmul_steps --bench (ns/it = ns per inner-loop iteration, n^3 of them)");
        run_all(512, 1, 0);
        run_all(1024, 1, 0);
        return 0;
    }
    size_t n = (size_t)arg_long(argc, argv, "--n", 256);
    printf("matmul_steps demo, n = %zu\n", n);
    run_all(n, 1, 0);
    return 0;
}
