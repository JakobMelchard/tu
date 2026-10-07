/* test_vecops.c - C-side test of libvecops (note 09), run by `make test`.
 *
 * Links against the shared library, not vecops.c, so it exercises exactly
 * the file ctypes and cffi load.  Each check is against a value known in
 * closed form.  Exit status 0 = all passed.
 */
#include <math.h>
#include <stdio.h>
#include "vecops.h"

static int failures = 0;

static void check(int ok, const char *what)
{
    printf("%s  %s\n", ok ? "ok  " : "FAIL", what);
    failures += !ok;
}

int main(void)
{
    double x[4] = {1.0, 2.0, 3.0, 4.0}, y[4] = {1.0, 1.0, 1.0, 1.0};

    check(vec_dot(x, y, 4) == 10.0, "vec_dot(1..4, ones) == 10");
    check(vec_dot(x, y, 0) == 0.0, "vec_dot with n = 0 is the empty sum");

    vec_axpy(4, 2.0, x, y);                  /* y <- 2x + 1, in place */
    check(y[0] == 3.0 && y[3] == 9.0, "vec_axpy writes into the caller's buffer");

    double big[2] = {1e200, 1e200};          /* naive sum of squares overflows */
    double r = vec_norm2(big, 2);
    check(isfinite(r) && fabs(r / (sqrt(2.0) * 1e200) - 1.0) < 1e-15,
          "vec_norm2 scales to avoid overflow");

    check(count_primes(1000) == 168, "count_primes(1000) == 168 = pi(1000)");
    check(count_primes(1) == 0, "count_primes(1) == 0");

    printf("%d failure(s)\n", failures);
    return failures != 0;
}
