"""Amdahl, Gustafson, and why they are the same law (topic 07).

Note 07 states both speedup laws. They are usually presented as opposites --
"Amdahl says parallelism is hopeless, Gustafson says it is fine" -- and that
reading is wrong: the two serial fractions are different quantities. Shi (1996)
[S21] shows that substituting one into the other gives the same formula.

Definitions, following [S19], [S20], [S21]:

  ts      time of the serial part           (same on 1 and on p processors)
  tp(1)   time of the parallel part on 1 processor
  tp(p)   = tp(1) / p

  f  = ts / (ts + tp(1))   Amdahl's serial fraction,   measured on 1 processor
  s  = ts / (ts + tp(p))   Gustafson's serial fraction, measured on p processors

  S_amdahl(p)    = 1 / (f + (1 - f)/p)
  S_gustafson(p) = s + (1 - s) p

`amdahl_f_from_gustafson_s` converts, and the tests show the two formulas then
return the *same* speedup. Also here: Karp-Flatt, the experimental serial
fraction, which is the right way to read a measured scaling table.

Run `python3 scaling.py` for the tables. Tests: test_scaling.py.
"""
import numpy as np


def amdahl(f, p):
    """Fixed-size (strong) speedup with serial fraction f on p workers [S19]."""
    p = np.asarray(p, dtype=float)
    return 1.0 / (f + (1.0 - f) / p)


def gustafson(s, p):
    """Scaled (weak) speedup with serial fraction s measured on p workers [S20]."""
    p = np.asarray(p, dtype=float)
    return s + (1.0 - s) * p


def amdahl_f_from_gustafson_s(s, p):
    """Convert Gustafson's p-dependent serial fraction to Amdahl's [S21].

    s = ts/(ts + tp(1)/p) and f = ts/(ts + tp(1)); eliminating ts and tp(1)
    gives f = s / (s + (1 - s) p).
    """
    return s / (s + (1.0 - s) * p)


def gustafson_s_from_amdahl_f(f, p):
    """The inverse of `amdahl_f_from_gustafson_s` [S21]: s = f p / (1 + (p-1) f)."""
    return f * p / (1.0 + (p - 1.0) * f)


def karp_flatt(speedup, p):
    """Karp-Flatt experimental serial fraction e from a measured speedup.

    e = (1/S - 1/p) / (1 - 1/p). Invert Amdahl for f. A *rising* e as p grows
    is the signature of parallel overhead (or of a bandwidth limit) rather than
    of a genuinely serial section -- which is the usual situation for the
    memory-bound kernels of this course (note 01).
    """
    speedup, p = np.asarray(speedup, float), np.asarray(p, float)
    return (1.0 / speedup - 1.0 / p) / (1.0 - 1.0 / p)


def efficiency(speedup, p):
    return np.asarray(speedup, float) / np.asarray(p, float)


def strong_scaling_table(times, p=None):
    """(p, speedup, efficiency, Karp-Flatt e) from a list of wall times.

    times[0] must be the 1-worker time; p defaults to 1, 2, 4, ... .
    """
    t = np.asarray(times, float)
    p = np.asarray(p if p is not None else [2**i for i in range(len(t))], float)
    s = t[0] / t
    e = np.full_like(s, np.nan)
    e[1:] = karp_flatt(s[1:], p[1:])
    return p, s, efficiency(s, p), e


def _main():
    print("Amdahl [S19]: max speedup for a fixed problem")
    print(f"{'f':>8}" + ''.join(f"{f'p={q}':>10}" for q in (2, 4, 8, 16, 1024)) + f"{'p->inf':>10}")
    for f in (0.001, 0.01, 0.05, 0.10, 0.50):
        row = ''.join(f"{amdahl(f, q):>10.2f}" for q in (2, 4, 8, 16, 1024))
        print(f"{f:>8.3f}{row}{1 / f:>10.1f}")

    print("\nGustafson [S20]: scaled speedup, serial fraction measured on p workers")
    print(f"{'s':>8}" + ''.join(f"{f'p={q}':>10}" for q in (2, 4, 8, 16, 1024)))
    for s in (0.004, 0.008, 0.05, 0.10):
        print(f"{s:>8.3f}" + ''.join(f"{gustafson(s, q):>10.1f}" for q in (2, 4, 8, 16, 1024)))

    print("\nThey are one law in two normalisations [S21]: p = 1024")
    print(f"{'s (Gustafson)':>15}{'f (Amdahl)':>14}{'S_gustafson':>14}{'S_amdahl':>12}")
    for s in (0.004, 0.008, 0.05):
        f = amdahl_f_from_gustafson_s(s, 1024)
        print(f"{s:>15.4f}{f:>14.3e}{gustafson(s, 1024):>14.1f}{amdahl(f, 1024):>12.1f}")

    print("\nKarp-Flatt on the measured OpenMP table of note 07 (omp_examples, 2026-09-27)")
    times = [0.01460, 0.00743, 0.00384, 0.00326]
    p, s, eff, e = strong_scaling_table(times, [1, 2, 4, 8])
    print(f"{'threads':>8}{'time[ms]':>10}{'speedup':>9}{'eff':>7}{'Karp-Flatt e':>14}")
    for i in range(len(p)):
        ee = '     -' if np.isnan(e[i]) else f"{e[i]:>6.3f}"
        print(f"{int(p[i]):>8}{times[i] * 1e3:>10.2f}{s[i]:>9.2f}{eff[i]:>7.2f}{ee:>14}")
    print("  e is flat while all threads are P-cores and jumps at 8 threads (two on E-cores):")
    print("  a shared limit, not a serial section.")


if __name__ == "__main__":
    _main()
