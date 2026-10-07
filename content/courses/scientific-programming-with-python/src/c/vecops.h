/* vecops.h - prototypes for libvecops (note 09).
 *
 * The one place the C signatures are written down: vecops.c and
 * test_vecops.c include it, and src/py/interfaces.py mirrors it in ctypes
 * argtypes/restype and in the cffi cdef.  Change all three together.
 */
#ifndef VECOPS_H
#define VECOPS_H

#include <stddef.h>
#include <stdint.h>

double  vec_dot(const double *x, const double *y, size_t n);
void    vec_axpy(size_t n, double a, const double *x, double *y);
double  vec_norm2(const double *x, size_t n);
int64_t count_primes(int64_t n);

#endif
