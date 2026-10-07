/* util.h -- shared helpers for the 185.190 reference programs.
 *
 * now_s()      monotonic wall clock in seconds (clock_gettime; needs
 *              _POSIX_C_SOURCE defined by the including .c before any include)
 * rng_*        xorshift64* so that every run and every version of a program
 *              sees the same input; random()/rand() differ between libcs
 * CHECK()      assertion that prints a message and exits 1 (make test relies
 *              on the exit code)
 * has_arg()    "--test", "--bench" style flag lookup
 * arg_long()   "--n 512" style value lookup with a default
 */
#ifndef UTIL_H
#define UTIL_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

static inline double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static inline uint64_t rng_next(uint64_t *s)
{
    uint64_t x = *s;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    *s = x;
    return x * 0x2545F4914F6CDD1DULL;
}

/* uniform in [0,1) with 53 random bits */
static inline double rng_unit(uint64_t *s)
{
    return (double)(rng_next(s) >> 11) * (1.0 / 9007199254740992.0);
}

#define CHECK(cond, ...)                                                   \
    do {                                                                   \
        if (!(cond)) {                                                     \
            fprintf(stderr, "CHECK failed at %s:%d: ", __FILE__, __LINE__); \
            fprintf(stderr, __VA_ARGS__);                                  \
            fputc('\n', stderr);                                           \
            exit(1);                                                       \
        }                                                                  \
    } while (0)

static inline int has_arg(int argc, char **argv, const char *flag)
{
    for (int i = 1; i < argc; i++)
        if (strcmp(argv[i], flag) == 0)
            return 1;
    return 0;
}

static inline long arg_long(int argc, char **argv, const char *flag, long def)
{
    for (int i = 1; i + 1 < argc; i++)
        if (strcmp(argv[i], flag) == 0)
            return atol(argv[i + 1]);
    return def;
}

static inline double arg_double(int argc, char **argv, const char *flag, double def)
{
    for (int i = 1; i + 1 < argc; i++)
        if (strcmp(argv[i], flag) == 0)
            return atof(argv[i + 1]);
    return def;
}

#endif
