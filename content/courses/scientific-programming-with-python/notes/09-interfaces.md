# 09 Interfaces to other languages

Code: [`../src/py/interfaces.py`](../src/py/interfaces.py), C library [`../src/c/vecops.c`](../src/c/vecops.c) with prototypes in [`../src/c/vecops.h`](../src/c/vecops.h), built by [`../src/c/Makefile`](../src/c/Makefile) (`make -C src/c`; C-side test `make -C src/c test`), Python tests in `test_interfaces.py`. Built and tested on this Mac (Apple Silicon, `cc` = Apple clang 21, arm64 Mach-O) on 2026-09-27.

Sources: CPython's `ctypes` and `subprocess` docs [S11], `numpy.ctypeslib` [S12],
cffi [S27], `numpy.f2py` [S28], pybind11 [S29], PythonCall.jl/juliacall [S30],
Numba [S31]; cross-checked against the *Interfacing with C* chapter of the
*Scientific Python Lectures* (CC BY 4.0) [S39]. **Verified against CPython
3.12.13 and cffi 2.1.1** [S40], last re-run 2026-09-27. f2py, pybind11, Cython, Numba and juliacall are
**not installed** in this venv, so §6–§8 are documentation-only and nothing in
`src/` demonstrates them.

TISS names this topic as *"Interfaces to other programming languages (e.g.,
Julia)"* [S1] — Julia by name, which is why §8 exists at all.

## 1. Why and when to leave Python

Python's per-operation overhead is ~50-100 ns of interpreter dispatch plus object allocation; C does the same arithmetic in ~1 ns. When the work is expressible as numpy operations, the gap vanishes because numpy *is* C. Drop to compiled code when: the algorithm has sequential dependencies or irregular control flow that numpy cannot express (recursions, tree traversals, per-element branching), memory for vectorised temporaries is prohibitive, an existing C/C++/Fortran/Julia library does the job, or profiling (note 10) shows one small hot loop. `count_primes_py` vs `count_primes_c`: 35x for a trial-division loop. Do not drop to C for code that is dominated by BLAS or I/O, or before profiling. The ladder: algorithm > numpy > numba > Cython/C extension.

## 2. Compiling a shared library

A **shared library** (`.dylib` macOS, `.so` Linux, `.dll` Windows) contains position-independent machine code with an exported symbol table; the OS loader maps it into a process at run time (`dlopen`) and resolves symbol names to addresses (`dlsym`). C has a stable, simple ABI: functions with primitive arguments, pointers to contiguous memory, no name mangling. That is what every FFI targets. C++ mangles names and passes objects, so it needs `extern "C"` wrappers or a binding generator.

```make
cc -O2 -Wall -Wextra -std=c11 -fPIC -dynamiclib -install_name @rpath/libvecops.dylib \
   -o libvecops.dylib vecops.c -lm                                   # macOS (cc is Apple clang)
cc -O2 -Wall -Wextra -std=c11 -fPIC -shared -o libvecops.so vecops.c -lm   # Linux
```

`nm -gU libvecops.dylib` lists the exported symbols (`_vec_dot`, ...); `file libvecops.dylib` says `Mach-O 64-bit dynamically linked shared library arm64` here. `vecops.c` exposes `vec_dot`, `vec_axpy` (in place), `vec_norm2` (scaled to avoid overflow) and `count_primes`, declared once in `vecops.h`. The C test `test_vecops.c` links against the library as a C program would (`-L. -lvecops`), and the `@rpath` install name plus `-Wl,-rpath,@loader_path` let it find the library next to itself from any working directory. ctypes and cffi need neither: they `dlopen` an absolute path.

## 3. ctypes

In the standard library; no compiler needed at call time [S11]. `ctypes.CDLL(path)` loads the library; attributes are the functions. **Declare `argtypes` and `restype`** for every function: the documented default return type is C `int`, so a `double` return silently becomes garbage. Types: `c_double`, `c_int`, `c_int64`, `c_size_t`, `c_char_p`, `POINTER(c_double)`, `Structure` subclasses, `byref(x)` for output parameters. Arrays: `numpy.ctypeslib.ndpointer(dtype, ndim, flags="C_CONTIGUOUS")` [S12] as an argtype makes ctypes accept a numpy array, check dtype/ndim/contiguity, and pass `arr.ctypes.data` (the raw pointer). A non-contiguous or wrong-dtype array raises `ArgumentError` instead of corrupting memory (`test_ndpointer_rejects_wrong_dtype_and_noncontiguous`). Use `np.ascontiguousarray(x, dtype=np.float64)` on inputs (copies only when needed) and remember that in-place functions like `vec_axpy` modify the *caller's* buffer, so a silently made copy would be lost.

Costs: each call has ~1 µs of overhead (argument conversion), so call C on whole arrays, not per element. Memory ownership: C must not free numpy buffers and numpy must not free C-malloc'ed ones (wrap with a finalizer or provide a `free` function). Callbacks: `CFUNCTYPE(restype, *argtypes)(python_function)` passes a Python function to C (slow per call). `load_ctypes`, `dot_ctypes`, `axpy_ctypes`.

## 4. cffi

Two modes [S27]. **ABI mode** (used here): `ffi.cdef("double vec_dot(const double*, const double*, size_t);")` parses C declarations as text (`load_cffi` feeds it `vecops.h` itself, minus the `#` lines cdef rejects), `ffi.dlopen(path)`, then call; pointers into numpy come from `ffi.cast("double *", arr.ctypes.data)` or `ffi.from_buffer(arr)`. **API mode**: `ffi.set_source("_vecops", '#include "vecops.h"', libraries=[...])` and `ffi.compile()` generate and compile a small C extension against the real header, so types are checked by the C compiler and calls are faster (no run-time conversion). cffi is what PyPy recommends and what many wheels use (`cryptography`); it needs `pip install cffi` but reads C headers almost verbatim, whereas ctypes needs the types re-declared in Python.

## 5. subprocess: the coarsest interface

`subprocess.run([prog, arg1, ...], input=text, capture_output=True, text=True, check=True, timeout=30, cwd=..., env=...)` runs any external program (a Fortran simulation, Julia script, `gnuplot`, `ffmpeg`), returns `CompletedProcess` with `returncode`, `stdout`, `stderr`. Pass a list, not a shell string (`shell=True` invites injection and quoting bugs). Communicate via files (`np.savetxt`, HDF5, NetCDF) or stdin/stdout streams for larger data; for many small calls the process startup (ms) dominates. `Popen` for long-running processes with streaming I/O. `run_external`, `python_version_via_subprocess`.

## 6. f2py (Fortran)

`numpy.f2py` [S28] compiles Fortran 77/90 into an extension module: `python -m numpy.f2py -c -m fmod vecops.f90` (needs `gfortran` and, since numpy 1.26, `meson` — `distutils` support went with Python 3.12). Argument intents come from the source or `!f2py intent(in)` comments: `intent(in)` arrays are passed (copied if not Fortran-contiguous), `intent(out)` become return values, `intent(inout)` are modified in place. Fortran is **column-major**, so pass `np.asfortranarray(A)` or accept transposed views; scalars pass by reference automatically. Ideal for legacy numerical codes and BLAS-like kernels.

## 7. pybind11 and C++ (also nanobind, Cython)

pybind11 [S29] is a header-only C++11 library: 

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
double dot(pybind11::array_t<double> x, pybind11::array_t<double> y) { ... }
PYBIND11_MODULE(vecops_cpp, m) { m.def("dot", &dot, "dot product"); }
```

It converts STL containers, Eigen matrices, `array_t` (with buffer protocol, optional `c_style | forcecast`), wraps classes with methods, properties and inheritance, translates C++ exceptions to Python ones, and can release the GIL (`py::call_guard<py::gil_scoped_release>()`). Built with CMake/scikit-build-core or setuptools. nanobind is its leaner successor. **Cython** is different: a Python superset compiled to C, where `cdef double` typed variables and `cimport numpy` typed memoryviews turn loops into C speed inside Python-looking code, and `cdef extern from "vecops.h"` wraps C libraries. Choose: ctypes/cffi for calling an *existing* C library quickly; Cython/numba for speeding up *your* Python loops; pybind11 for C++ code and classes.

## 8. Julia

Julia is a JIT-compiled (LLVM) dynamic language with C-like speed for typed numeric loops, multiple dispatch, and 1-based column-major arrays. Two bridges:

- **juliacall / PythonCall.jl** [S30] (`pip install juliacall`): `from juliacall import Main as jl`; `jl.seval("using LinearAlgebra")`; `jl.norm(x)` or `jl.seval("f(x) = sum(x .^ 2)")` then `jl.f(np_array)`. Arrays are **shared without copying** (a numpy array becomes a Julia `PyArray` wrapping the same memory; a C-ordered 2D array appears as its transpose because Julia is column-major). Julia's first call compiles the function (seconds), later calls are fast; the runtime starts in-process once (~1-3 s) and is managed by juliacall's own environment (`juliapkg`).
- **PyCall.jl** is the older Python-from-Julia bridge (`using PyCall; np = pyimport("numpy")`), and **PyJulia** its Python side (`from julia import Main`); it copies arrays by default and had trouble with statically linked Pythons. PythonCall/juliacall is the current recommendation.
- Use cases: an existing Julia package (DifferentialEquations.jl, JuMP), or writing a hot kernel in Julia without a C toolchain. Costs: two runtimes in one process, startup latency, deployment complexity. Not installed in this repo; the concept is in `JULIA_IDEA`.

## 9. Decision guide

| Situation | Tool |
|---|---|
| numpy expresses it | numpy (nothing to build) |
| hot Python loop over arrays | numba `@njit` (no build step) |
| existing C library, simple signatures | ctypes (stdlib) or cffi |
| C++ classes / templates / Eigen | pybind11 / nanobind |
| Fortran code | f2py |
| standalone program | subprocess with files |
| Julia ecosystem | juliacall |
| cluster-scale | mpi4py + compiled kernels |

## Pitfalls

- Missing `restype`: `lib.vec_dot(...)` returns a nonsense `int`. Missing `argtypes`: Python floats are passed as ints.
- Non-contiguous or wrong-dtype arrays silently copied (in-place results lost) or, without `ndpointer`, garbage read.
- `size_t` vs `int` for lengths (64 vs 32 bit), `int64_t` vs `long` across platforms.
- Per-element FFI calls (overhead dominates); Python callbacks in tight C loops.
- Memory ownership across the boundary; releasing the GIL in C while touching Python objects.
- Column-major vs row-major with Fortran and Julia; 1-based indices in Julia.
- Building on one machine and copying the `.dylib` to another with a different architecture (`arm64` vs `x86_64`).

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md).

1. Without setting `restype`, a ctypes call to a C function returning `double`
   (a) raises `TypeError` (b) returns the correct float (c) returns the value interpreted as a C `int` (garbage) (d) returns `None`
   **c.** ctypes assumes `int` by default.

2. `numpy.ctypeslib.ndpointer(np.float64, ndim=1, flags="C_CONTIGUOUS")` as an `argtypes` entry
   (a) copies the array into C memory (b) validates dtype, dimensionality and layout and passes the data pointer (c) converts the array to a Python list (d) transposes the array
   **b.**

3. The main advantage of cffi API mode over ABI mode is
   (a) no compiler needed (b) the declarations are checked against the real header by the C compiler and calls are faster (c) it supports Fortran (d) it runs without the GIL
   **b.**

4. A C-contiguous numpy array of shape `(3, 4)` passed to Julia through juliacall without copying appears in Julia as
   (a) a 3x4 matrix with the same element order (b) a 4x3 matrix (transposed view) because Julia is column-major (c) a vector of 12 elements (d) an error
   **b.**

5. When is dropping from numpy to C most likely to pay off?
   (a) for `A @ B` with large dense matrices (b) for a loop with a sequential dependency `x[i] = f(x[i-1])` that numpy cannot vectorise (c) for reading a CSV file (d) for a program dominated by network I/O
   **b.** Matrix products already run in BLAS; I/O-bound code gains nothing.
