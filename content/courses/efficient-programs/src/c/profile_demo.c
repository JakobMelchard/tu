/* profile_demo.c -- a program with one obvious hot spot, for the profilers.
 *
 * Counts primes below a limit twice: by trial division (hot: is_prime_trial,
 * called limit times, O(sqrt n) each) and by a sieve (cheap). Both counts
 * must agree with pi(x): pi(200000) = 17984, pi(2000000) = 148933.
 * Also runs a deliberately cheap checksum so the profile has something to
 * rank against.
 *
 * On the course machine g0 (Linux), slide 9 and 22 commands:
 *   /usr/bin/time ./profile_demo                      # user vs sys vs elapsed, maxresident
 *   gcc -pg -O2 profile_demo.c -o profile_demo_pg && ./profile_demo_pg >/dev/null && gprof profile_demo_pg | head -40
 *   gcc -O2 --coverage -c profile_demo.c && gcc --coverage profile_demo.o -o profile_demo_cov \
 *       && rm -f *.gcda && ./profile_demo_cov >/dev/null && gcov profile_demo.c \
 *       && sort -rn profile_demo.c.gcov | head    # execution count per line (= make gcov;
 *       two steps so the .gcno/.gcda are named after the source, not the binary)
 *   perf stat -e cycles:u -e instructions:u -e branch-misses:u -e L1-dcache-load-misses:u ./profile_demo
 *   perf record -e cycles:u ./profile_demo && perf report --stdio | head -30 && perf annotate --stdio is_prime_trial
 *   perf stat -M TopdownL1 ./profile_demo              # slide 23
 * On macOS (no gprof, no perf): /usr/bin/time -l, and gcov via
 *   the same two-step cc --coverage sequence (make gcov)
 * The header of every gprof/gcov/perf output line is explained in notes/02.
 *
 * usage: ./profile_demo [--limit L]   default 200000, 0 <= L <= 2^31 (keeps n*n
 *                                     and d*d far from signed overflow)
 *        ./profile_demo --test | --bench (limit 2000000)
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"

static int is_prime_trial(long n)
{
    if (n < 2) return 0;
    if (n % 2 == 0) return n == 2;
    for (long d = 3; d * d <= n; d += 2)
        if (n % d == 0) return 0;
    return 1;
}

static long count_primes_trial(long limit)
{
    long count = 0;
    for (long n = 0; n < limit; n++)
        count += is_prime_trial(n);
    return count;
}

static long count_primes_sieve(long limit)
{
    unsigned char *comp = calloc((size_t)limit + 1, 1);
    CHECK(comp != NULL, "oom");
    long count = 0;
    for (long n = 2; n < limit; n++) {
        if (comp[n]) continue;
        count++;
        for (long m = n * n; m < limit; m += n) comp[m] = 1;
    }
    free(comp);
    return count;
}

static unsigned long checksum_cheap(long limit)
{
    unsigned long h = 1469598103934665603UL;
    for (long n = 0; n < limit; n++) h = (h ^ (unsigned long)n) * 1099511628211UL;
    return h;
}

static void run(long limit, long expected, int verbose)
{
    double t0 = now_s();
    long a = count_primes_trial(limit);
    double t1 = now_s();
    long b = count_primes_sieve(limit);
    double t2 = now_s();
    unsigned long h = checksum_cheap(limit);
    double t3 = now_s();
    CHECK(a == b, "trial %ld != sieve %ld", a, b);
    if (expected >= 0) CHECK(a == expected, "pi(%ld) = %ld, expected %ld", limit, a, expected);
    if (verbose)
        printf("pi(%ld) = %ld  trial %.1f ms (%.0f%%)  sieve %.1f ms  checksum %.1f ms (h=%lx)\n",
               limit, a, 1e3 * (t1 - t0), 100 * (t1 - t0) / (t3 - t0), 1e3 * (t2 - t1),
               1e3 * (t3 - t2), h);
}

int main(int argc, char **argv)
{
    if (has_arg(argc, argv, "--test")) {
        run(1, 0, 0); run(2, 0, 0); run(3, 1, 0); run(100, 25, 0); run(200000, 17984, 0);
        puts("profile_demo: trial division and sieve agree with pi(x) for 5 limits");
        return 0;
    }
    if (has_arg(argc, argv, "--bench")) { run(2000000, 148933, 1); return 0; }
    long limit = arg_long(argc, argv, "--limit", 200000);
    CHECK(limit >= 0 && limit <= (1L << 31), "--limit must be in [0, 2^31]");
    run(limit, limit == 200000 ? 17984 : -1, 1);
    return 0;
}
