/* pointer_chase.c -- our own version of the exercise-3 program "memory1".
 *
 * Builds a cyclic linked list without payload: element i lives at
 * buf + i*stride and its first 8 bytes hold the address of the next element.
 * Then follows the pointers for A accesses. Each load depends on the previous
 * one, so the time per access is the load latency of whatever level of the
 * memory hierarchy the working set (elements * stride bytes) lands in.
 *
 *   linear   element i -> element i+1 (mod elements); spatial locality and the
 *            hardware prefetcher help; stride 8 puts 8 elements in a 64 B line
 *   random   the elements are linked in a random single cycle (Fisher-Yates
 *            permutation); no locality, no prefetching, TLB misses at large
 *            strides
 *
 * usage: ./pointer_chase random|linear <elements> <stride> [accesses]
 *        ./pointer_chase --sweep [--stride S] [--accesses A]   random, sizes 2 KB .. 128 MB
 *        ./pointer_chase --test
 * Prints ns per access. Init (linking) and chase are timed separately; the
 * allocation and the page-touching memset are in neither (memory1 measures
 * all of it inside one perf stat). On Linux wrap it in
 *   perf stat -e cycles:u -e L1-dcache-load-misses:u -e dTLB-load-misses:u ./pointer_chase ...
 * to reproduce the exercise questions on cache size, line size, associativity
 * and TLB reach. Refs: S7 (exercise 3), S3 p.16-17, p.21.
 */
#define _POSIX_C_SOURCE 200809L
#include "util.h"

static unsigned char *alloc_list(size_t elements, size_t stride)
{
    size_t bytes = elements * stride + sizeof(void *);
    bytes = (bytes + 4095) & ~(size_t)4095;
    unsigned char *buf = aligned_alloc(4096, bytes);
    CHECK(buf != NULL, "cannot allocate %zu bytes", bytes);
    memset(buf, 0, bytes);  /* touch every page so init cost is paid here */
    return buf;
}

#define NODE(buf, i, stride) ((void **)((buf) + (size_t)(i) * (stride)))

static void link_linear(unsigned char *buf, size_t elements, size_t stride)
{
    for (size_t i = 0; i < elements; i++)
        *NODE(buf, i, stride) = NODE(buf, (i + 1) % elements, stride);
}

static void link_random(unsigned char *buf, size_t elements, size_t stride, uint64_t seed)
{
    size_t *perm = malloc(elements * sizeof *perm);
    CHECK(perm != NULL, "out of memory");
    for (size_t i = 0; i < elements; i++) perm[i] = i;
    for (size_t i = elements - 1; i > 0; i--) {  /* Fisher-Yates */
        size_t j = (size_t)(rng_next(&seed) % (i + 1));
        size_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    /* one cycle through all elements in permutation order */
    for (size_t k = 0; k < elements; k++)
        *NODE(buf, perm[k], stride) = NODE(buf, perm[(k + 1) % elements], stride);
    free(perm);
}

/* the end pointer is stored here so the chase is never dead code, even where
   the caller ignores it (--sweep): a side-effect-free terminating loop whose
   result is unused may be deleted (C11 6.8.5p6) */
static volatile uintptr_t chase_sink;

/* the measured loop: A dependent loads */
static void *chase(void *start, size_t accesses)
{
    void **p = start;
    for (size_t a = 0; a < accesses; a++)
        p = *p;
    return p;
}

static double measure(int random, size_t elements, size_t stride, size_t accesses,
                      double *init_ms, size_t *end_off)
{
    unsigned char *buf = alloc_list(elements, stride);
    double t0 = now_s();
    if (random) link_random(buf, elements, stride, 0x9E3779B97F4A7C15ULL);
    else link_linear(buf, elements, stride);
    double t1 = now_s();
    void *end = chase(buf, accesses);
    chase_sink = (uintptr_t)end;
    double t2 = now_s();
    *init_ms = 1e3 * (t1 - t0);
    *end_off = (size_t)((unsigned char *)end - buf);
    free(buf);
    return 1e9 * (t2 - t1) / (double)accesses;
}

static void self_test(void)
{
    size_t els[] = {1, 2, 7, 64, 1000, 4097};
    size_t strides[] = {8, 24, 64, 128};
    for (size_t e = 0; e < sizeof els / sizeof *els; e++)
        for (size_t s = 0; s < sizeof strides / sizeof *strides; s++)
            for (int random = 0; random < 2; random++) {
                size_t n = els[e], st = strides[s];
                unsigned char *buf = alloc_list(n, st);
                if (random) link_random(buf, n, st, 12345); else link_linear(buf, n, st);
                /* the list must be one cycle of length n: walking n-1 steps
                   never returns to the start, the n-th step does */
                void **p = NODE(buf, 0, st);
                for (size_t k = 1; k < n; k++) {
                    p = *p;
                    CHECK(p != (void **)buf, "cycle shorter than %zu (%s, stride %zu)",
                          n, random ? "random" : "linear", st);
                    CHECK(((unsigned char *)p - buf) % st == 0, "misaligned node");
                }
                CHECK(*p == (void **)buf, "cycle longer than %zu", n);
                void *q = chase(buf, n);
                CHECK(q == (void *)buf, "chase(n) did not return to start");
                free(buf);
            }
    puts("pointer_chase: single-cycle property holds for 6 sizes x 4 strides x 2 modes");
}

static void sweep(size_t stride, size_t accesses)
{
    printf("pointer_chase --sweep: random order, stride %zu B, %zu accesses per size\n",
           stride, accesses);
    printf("  %10s %10s %10s %10s\n", "bytes", "elements", "ns/access", "init ms");
    for (size_t bytes = 2048; bytes <= (size_t)128 << 20; bytes *= 2) {
        size_t elements = bytes / stride;
        if (elements < 2) continue;
        double init_ms; size_t off;
        double ns = measure(1, elements, stride, accesses, &init_ms, &off);
        printf("  %10zu %10zu %10.2f %10.1f\n", bytes, elements, ns, init_ms);
    }
}

int main(int argc, char **argv)
{
    if (has_arg(argc, argv, "--test")) { self_test(); return 0; }
    if (has_arg(argc, argv, "--sweep")) {
        sweep((size_t)arg_long(argc, argv, "--stride", 128),
              (size_t)arg_long(argc, argv, "--accesses", 10000000));
        return 0;
    }
    if (argc < 4) {
        fprintf(stderr, "usage: %s random|linear <elements> <stride> [accesses]\n"
                        "       %s --sweep [--stride S] [--accesses A] | --test\n", argv[0], argv[0]);
        return 2;
    }
    int random = strcmp(argv[1], "random") == 0;
    CHECK(random || strcmp(argv[1], "linear") == 0, "mode must be random or linear");
    size_t elements = (size_t)atol(argv[2]), stride = (size_t)atol(argv[3]);
    size_t accesses = argc > 4 ? (size_t)atol(argv[4]) : 100000000u;
    CHECK(elements >= 1 && stride >= sizeof(void *), "elements >= 1, stride >= 8");
    double init_ms; size_t off;
    double ns = measure(random, elements, stride, accesses, &init_ms, &off);
    printf("size: %zu B, %s, %zu elements, stride %zu, %zu accesses\n",
           elements * stride, random ? "randomized" : "linear", elements, stride, accesses);
    printf("init %.1f ms, chase %.3f ns/access (end offset %zu)\n", init_ms, ns, off);
    return 0;
}
