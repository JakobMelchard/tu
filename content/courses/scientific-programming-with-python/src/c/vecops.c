/* vecops.c - tiny vector kernels exposed as a C shared library.
 *
 * Note 09.  Called from Python through ctypes and cffi (src/py/interfaces.py);
 * prototypes in vecops.h, C-side test in test_vecops.c (`make test`).
 * Plain C ABI: no name mangling, no structs, contiguous double arrays.
 * Build with `make` in this directory -> libvecops.dylib (macOS) / .so (Linux).
 */
#include <math.h>
#include "vecops.h"

/* dot product of two length-n arrays */
double vec_dot(const double *x, const double *y, size_t n)
{
    double s = 0.0;
    for (size_t i = 0; i < n; ++i)
        s += x[i] * y[i];
    return s;
}

/* y <- a*x + y, in place: the caller's buffer is modified (no copy) */
void vec_axpy(size_t n, double a, const double *x, double *y)
{
    for (size_t i = 0; i < n; ++i)
        y[i] = a * x[i] + y[i];
}

/* Euclidean norm, two-pass scaling to avoid overflow in the squares */
double vec_norm2(const double *x, size_t n)
{
    double scale = 0.0;
    for (size_t i = 0; i < n; ++i)
        if (fabs(x[i]) > scale)
            scale = fabs(x[i]);
    if (scale == 0.0)
        return 0.0;
    double s = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double t = x[i] / scale;
        s += t * t;
    }
    return scale * sqrt(s);
}

/* number of primes <= n by trial division: a CPU-bound kernel that is slow
 * in pure Python and fast here, used to show when dropping to C pays off */
int64_t count_primes(int64_t n)
{
    int64_t count = 0;
    for (int64_t k = 2; k <= n; ++k) {
        int is_prime = 1;
        for (int64_t d = 2; d * d <= k; ++d) {
            if (k % d == 0) { is_prime = 0; break; }
        }
        count += is_prime;
    }
    return count;
}
