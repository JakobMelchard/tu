/* tsp_greedy.c -- greedy nearest-neighbour TSP in four versions.
 *
 * Bentley's running example (slides 75-85, refs/cite-only/S9-*) is a greedy
 * tour: from the current city go to the nearest unvisited one. O(n^2), about
 * 25 % longer than optimal. These are our own versions, not the lecturer's
 * tsp1..tsp9; the steps are chosen in the same spirit and each is checked to
 * produce the identical tour:
 *
 *   v1  baseline: visited[] flags, distance = sqrt(dx^2 + dy^2) via a function,
 *       called a second time when a new minimum is found (tsp1's shape; clang
 *       -O2 merges the two calls, so one fsqrt per candidate is executed)
 *   v2  algebraic identity + code motion: sqrt is monotone, so compare squared
 *       distances; hoist the current city's coordinates out of the inner loop
 *   v3  data structure change: no visited[] test. The unvisited cities are
 *       kept compacted in tour[i..n-1]; picking city j swaps it to tour[i].
 *       Halves the inner-loop iterations and removes an unpredictable branch
 *   v4  short-circuit: compare dx^2 alone first, add dy^2 only when it can
 *       still win (lazy evaluation of the y part)
 *
 * usage: ./tsp_greedy [--n N] [--seed S]   demo, default n = 2000
 *        ./tsp_greedy --test               tours identical + nearest-neighbour
 *                                          property verified for small n
 *        ./tsp_greedy --bench              n = 10000, each version timed
 * Ties (two unvisited cities at exactly the same distance) could make v3/v4
 * pick a different city than v1/v2 because the scan order changes; with
 * random doubles a tie never occurs.
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"
#include <math.h>
#include <float.h>

typedef struct { double x, y; size_t id; } city;

static double dist(const city *a, const city *b)
{
    double dx = a->x - b->x, dy = a->y - b->y;
    return sqrt(dx * dx + dy * dy);
}

/* v1: the obvious program */
static void tsp_v1(const city *c, size_t n, size_t *tour)
{
    char *visited = calloc(n, 1);
    CHECK(visited != NULL, "oom");
    size_t cur = 0;
    tour[0] = 0; visited[0] = 1;
    for (size_t i = 1; i < n; i++) {
        double best = DBL_MAX; size_t bestj = 0;  /* always overwritten: n - i >= 1 cities left */
        for (size_t j = 0; j < n; j++)
            if (!visited[j] && dist(&c[cur], &c[j]) < best) {
                best = dist(&c[cur], &c[j]);
                bestj = j;
            }
        tour[i] = bestj; visited[bestj] = 1; cur = bestj;
    }
    free(visited);
}

/* v2: no sqrt, current coordinates hoisted */
static void tsp_v2(const city *c, size_t n, size_t *tour)
{
    char *visited = calloc(n, 1);
    CHECK(visited != NULL, "oom");
    size_t cur = 0;
    tour[0] = 0; visited[0] = 1;
    for (size_t i = 1; i < n; i++) {
        double cx = c[cur].x, cy = c[cur].y, best = DBL_MAX;
        size_t bestj = 0;
        for (size_t j = 0; j < n; j++) {
            if (visited[j]) continue;
            double dx = c[j].x - cx, dy = c[j].y - cy, d = dx * dx + dy * dy;
            if (d < best) { best = d; bestj = j; }
        }
        tour[i] = bestj; visited[bestj] = 1; cur = bestj;
    }
    free(visited);
}

/* v3: remaining cities compacted in rest[i..n-1]; no flag test */
static void tsp_v3(const city *c, size_t n, size_t *tour)
{
    city *rest = malloc(n * sizeof *rest);
    CHECK(rest != NULL, "oom");
    memcpy(rest, c, n * sizeof *rest);
    for (size_t i = 1; i < n; i++) {
        double cx = rest[i - 1].x, cy = rest[i - 1].y, best = DBL_MAX;
        size_t bestj = i;
        for (size_t j = i; j < n; j++) {
            double dx = rest[j].x - cx, dy = rest[j].y - cy, d = dx * dx + dy * dy;
            if (d < best) { best = d; bestj = j; }
        }
        city t = rest[i]; rest[i] = rest[bestj]; rest[bestj] = t;
    }
    for (size_t i = 0; i < n; i++) tour[i] = rest[i].id;
    free(rest);
}

/* v4: as v3, but the y part is only computed when dx^2 alone is a candidate */
static void tsp_v4(const city *c, size_t n, size_t *tour)
{
    city *rest = malloc(n * sizeof *rest);
    CHECK(rest != NULL, "oom");
    memcpy(rest, c, n * sizeof *rest);
    for (size_t i = 1; i < n; i++) {
        double cx = rest[i - 1].x, cy = rest[i - 1].y, best = DBL_MAX;
        size_t bestj = i;
        for (size_t j = i; j < n; j++) {
            double dx = rest[j].x - cx, d = dx * dx;
            if (d < best) {
                double dy = rest[j].y - cy;
                d += dy * dy;
                if (d < best) { best = d; bestj = j; }
            }
        }
        city t = rest[i]; rest[i] = rest[bestj]; rest[bestj] = t;
    }
    for (size_t i = 0; i < n; i++) tour[i] = rest[i].id;
    free(rest);
}

typedef void (*tsp_fn)(const city *, size_t, size_t *);
static const struct { const char *name; tsp_fn fn; } versions[] = {
    {"v1 baseline", tsp_v1}, {"v2 no-sqrt+hoist", tsp_v2},
    {"v3 compaction", tsp_v3}, {"v4 lazy-y", tsp_v4}};
#define NV (sizeof versions / sizeof *versions)

static city *make_cities(size_t n, uint64_t seed)
{
    city *c = malloc(n * sizeof *c);
    CHECK(c != NULL, "oom");
    for (size_t i = 0; i < n; i++) { c[i].x = rng_unit(&seed); c[i].y = rng_unit(&seed); c[i].id = i; }
    return c;
}

static double tour_length(const city *c, const size_t *tour, size_t n)
{
    double s = 0;
    for (size_t i = 1; i < n; i++) s += dist(&c[tour[i - 1]], &c[tour[i]]);
    return s;
}

/* independent check of the greedy property: at each step no unvisited city
   is strictly closer than the one chosen */
static void check_greedy(const city *c, const size_t *tour, size_t n)
{
    char *seen = calloc(n, 1);
    CHECK(seen != NULL, "oom");
    CHECK(tour[0] == 0, "tour must start at city 0");
    seen[0] = 1;
    for (size_t i = 1; i < n; i++) {
        CHECK(tour[i] < n, "city index %zu out of range", tour[i]);
        CHECK(!seen[tour[i]], "city %zu visited twice", tour[i]);
        double chosen = dist(&c[tour[i - 1]], &c[tour[i]]);
        for (size_t j = 0; j < n; j++)
            CHECK(seen[j] || dist(&c[tour[i - 1]], &c[j]) >= chosen,
                  "step %zu: city %zu closer than chosen %zu", i, j, tour[i]);
        seen[tour[i]] = 1;
    }
    free(seen);
}

static void run(size_t n, uint64_t seed, int verbose)
{
    city *c = make_cities(n, seed);
    size_t *ref = malloc(n * sizeof *ref), *tour = malloc(n * sizeof *tour);
    CHECK(ref && tour, "oom");
    double t_ref = 0, its = 0.5 * (double)n * (double)(n - 1);
    for (size_t v = 0; v < NV; v++) {
        size_t *out = v == 0 ? ref : tour;
        double t0 = now_s();
        versions[v].fn(c, n, out);
        double t = now_s() - t0;
        if (v == 0) t_ref = t;
        else
            for (size_t i = 0; i < n; i++)
                CHECK(out[i] == ref[i], "%s: tour differs from v1 at position %zu (n=%zu)",
                      versions[v].name, i, n);
        if (verbose)
            printf("  %-18s %9.2f ms  %6.2f ns/candidate  speedup %5.2f  length %.6f\n",
                   versions[v].name, 1e3 * t, its > 0 ? 1e9 * t / its : 0, t_ref / t,
                   tour_length(c, out, n));
    }
    if (n <= 2000) check_greedy(c, ref, n);
    free(c); free(ref); free(tour);
}

int main(int argc, char **argv)
{
    if (has_arg(argc, argv, "--test")) {
        size_t sizes[] = {1, 2, 3, 10, 100, 1000};
        for (size_t s = 0; s < sizeof sizes / sizeof *sizes; s++)
            for (uint64_t seed = 1; seed <= 3; seed++)
                run(sizes[s], seed, 0);
        puts("tsp_greedy: 4 versions give identical tours for 6 sizes x 3 seeds; greedy property verified");
        return 0;
    }
    if (has_arg(argc, argv, "--bench")) {
        puts("tsp_greedy --bench, n = 10000 (ns/candidate = ns per inner-loop candidate, n(n-1)/2 of them)");
        run(10000, 42, 1);
        return 0;
    }
    long nl = arg_long(argc, argv, "--n", 2000);
    CHECK(nl >= 1, "--n must be >= 1");
    size_t n = (size_t)nl;
    uint64_t seed = (uint64_t)arg_long(argc, argv, "--seed", 42);
    printf("tsp_greedy demo, n = %zu, seed = %llu\n", n, (unsigned long long)seed);
    run(n, seed, 1);
    return 0;
}
