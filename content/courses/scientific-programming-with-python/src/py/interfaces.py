"""Interfaces to other languages (note 09).

ctypes and cffi calls into src/c/libvecops (``make -C src/c``, prototypes in
src/c/vecops.h, C-side test ``make -C src/c test``),
subprocess for external programs, and the ideas behind f2py, pybind11 and
calling Julia (juliacall) in docstrings, since neither Fortran nor Julia
is guaranteed on the test machine.
"""
from __future__ import annotations

import ctypes
import functools
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from numpy.ctypeslib import ndpointer

C_DIR = Path(__file__).resolve().parent.parent / "c"
LIB_PATH = C_DIR / ("libvecops.dylib" if sys.platform == "darwin" else "libvecops.so")


@functools.cache
def build_library() -> Path:
    """Run make once per process: a no-op when libvecops is newer than
    vecops.c/vecops.h, a rebuild when it is not, so an edited kernel is never
    loaded stale.  Raises only if make fails and no library exists at all."""
    try:
        subprocess.run(["make", "-C", str(C_DIR)], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        if not LIB_PATH.exists():
            raise
    return LIB_PATH


# ---------------------------------------------------------------- ctypes
@functools.cache
def load_ctypes() -> ctypes.CDLL:
    """ctypes ships with Python and needs no compiler at call time.  Every
    function must have argtypes/restype declared, otherwise ctypes guesses
    (int) and doubles get truncated silently.  ndpointer checks dtype,
    ndim and contiguity of numpy arguments and passes the data pointer.
    The declarations mirror ../c/vecops.h."""
    lib = ctypes.CDLL(str(build_library()))
    dbl_in = ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS")
    dbl_inout = ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS, WRITEABLE")
    lib.vec_dot.argtypes = [dbl_in, dbl_in, ctypes.c_size_t]
    lib.vec_dot.restype = ctypes.c_double
    lib.vec_axpy.argtypes = [ctypes.c_size_t, ctypes.c_double, dbl_in, dbl_inout]
    lib.vec_axpy.restype = None
    lib.vec_norm2.argtypes = [dbl_in, ctypes.c_size_t]
    lib.vec_norm2.restype = ctypes.c_double
    lib.count_primes.argtypes = [ctypes.c_int64]
    lib.count_primes.restype = ctypes.c_int64
    return lib


def dot_ctypes(x: np.ndarray, y: np.ndarray) -> float:
    lib = load_ctypes()
    x = np.ascontiguousarray(x, dtype=np.float64)     # copies only if needed
    y = np.ascontiguousarray(y, dtype=np.float64)
    return lib.vec_dot(x, y, x.size)


def axpy_ctypes(a: float, x: np.ndarray, y: np.ndarray) -> None:
    """In place: y must already be a contiguous float64 array, otherwise
    ndpointer raises instead of silently modifying a temporary copy."""
    load_ctypes().vec_axpy(x.size, a, x, y)


def norm_ctypes(x: np.ndarray) -> float:
    return load_ctypes().vec_norm2(x, x.size)


def count_primes_c(n: int) -> int:
    return load_ctypes().count_primes(n)


def count_primes_py(n: int) -> int:
    c = 0
    for k in range(2, n + 1):
        d = 2
        while d * d <= k:
            if k % d == 0:
                break
            d += 1
        else:
            c += 1
    return c


# ---------------------------------------------------------------- cffi (ABI mode)
@functools.cache
def load_cffi():
    """cffi ABI mode: the C prototypes as text (cdef), then dlopen.  cdef
    reads C almost verbatim, so it takes vecops.h itself, minus the
    preprocessor lines it does not accept.  API mode would instead compile a
    small extension against the header, catching type errors at build time."""
    from cffi import FFI
    ffi = FFI()
    header = (C_DIR / "vecops.h").read_text().splitlines()
    ffi.cdef("\n".join(line for line in header if not line.lstrip().startswith("#")))
    lib = ffi.dlopen(str(build_library()))
    return ffi, lib


def dot_cffi(x: np.ndarray, y: np.ndarray) -> float:
    ffi, lib = load_cffi()
    x = np.ascontiguousarray(x, dtype=np.float64)
    y = np.ascontiguousarray(y, dtype=np.float64)
    px = ffi.cast("const double *", x.ctypes.data)     # pointer into numpy's buffer
    py = ffi.cast("const double *", y.ctypes.data)
    return lib.vec_dot(px, py, x.size)


# ---------------------------------------------------------------- subprocess
def run_external(args: list[str], stdin_text: str | None = None) -> tuple[int, str]:
    """subprocess.run with a list (no shell parsing), captured text output
    and a timeout; check=True would raise CalledProcessError on failure."""
    r = subprocess.run(args, input=stdin_text, capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout


def python_version_via_subprocess() -> str:
    return run_external([sys.executable, "-c", "import sys; print(sys.version_info[0])"])[1].strip()


# ---------------------------------------------------------------- concepts (no code run)
F2PY_IDEA = """
Fortran: `python -m numpy.f2py -c -m fmod vecops.f90` compiles a module whose
functions take numpy arrays directly; intent(in/out) comments in the
Fortran source control argument passing.  Column-major layout matters:
pass order='F' arrays or accept the transposition.
"""

PYBIND11_IDEA = """
C++: pybind11 (header only) wraps functions/classes with
`PYBIND11_MODULE(m, mod) { mod.def("dot", &dot); }`, converts
std::vector/Eigen/py::array_t automatically and keeps exceptions; build via
scikit-build-core or setuptools.  Prefer it over ctypes when you have C++
objects or need type checking at compile time.
"""

JULIA_IDEA = """
Julia: `pip install juliacall`; `from juliacall import Main as jl` starts a
Julia runtime in-process, `jl.seval("using LinearAlgebra")`, and
`jl.norm(np_array)` shares memory for arrays (Julia is column-major, so a
C-ordered 2D numpy array appears transposed).  PyCall.jl is the other
direction (Julia calling Python).  Julia's JIT gives C-like speed without
leaving a high-level language; the price is a multi-second startup.
"""


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    x, y = rng.random(10**6), rng.random(10**6)
    print("dot ctypes:", dot_ctypes(x, y), " numpy:", x @ y, " cffi:", dot_cffi(x, y))
    z = y.copy(); axpy_ctypes(2.0, x, z); print("axpy ok:", np.allclose(z, 2 * x + y))
    print("norm:", norm_ctypes(x), np.linalg.norm(x))
    for f in (count_primes_py, count_primes_c):
        t0 = time.perf_counter(); c = f(200_000)
        print(f"{f.__name__}: {c} primes, {time.perf_counter() - t0:.3f} s")
    print("subprocess python major:", python_version_via_subprocess())
