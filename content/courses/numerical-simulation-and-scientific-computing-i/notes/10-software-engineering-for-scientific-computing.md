# 10 Software engineering principles for scientific computing

The practices that make a numerical code reproducible, testable and usable by someone else (including you in six months).

Sources: the CMake documentation [S36], the clang manual and sanitizer pages [S37], the AddressSanitizer paper [S38], the pybind11 documentation [S39], *Pro Git* [S40], and the SPDX/OSI licence texts [S41]. [S8] covers the same ground for this course's lecturer - development environment, documentation, automatic testing, Python bindings - and is worth reading alongside.

Reference: `src/cpp/CMakeLists.txt`, `src/cpp/Makefile`, `src/sh/git_workflow.sh`, `src/sh/sanitizers.sh`, `src/py/test_*.py`.

## Version control with git

- Repository = full history; commit = snapshot with message; branch = movable pointer to a commit; `main` should always build and pass tests.
- Feature-branch workflow [S40] (`git_workflow.sh` runs it on a throw-away repo): `git switch -c feature/x`, commit small logical steps with messages that say *why*, `git rebase main` to replay onto the latest main (linear history), `git merge --no-ff` (or a pull request with review) into main, `git tag -a v0.1` for every hand-in or paper figure.
- `.gitignore`: build output (`bin/`, `*.o`, `build/`), `__pycache__`, large data, `.vtk` results. Never commit binaries or secrets; use git LFS for unavoidable large files.
- Daily commands: `status`, `diff`, `log --oneline --graph`, `stash`, `blame`, `bisect` (binary search for the commit that broke a test).
- Merge vs rebase: rebase rewrites history (fine on your own branch, never on shared ones); merge preserves it. Conflicts are resolved by editing, `git add`, `git rebase --continue` / `git commit`.

## Build systems

**Make**: rules `target: prerequisites` + recipe (tab-indented); rebuilds a target when any prerequisite is newer. Pattern rules `bin/%: %.cpp`, automatic variables `$@` (target) `$<` (first prerequisite) `$^` (all), variables `CXXFLAGS := ...`, `.PHONY` for targets that are not files (`all test clean`), `make -j8` parallel builds. The course Makefile (`src/cpp/Makefile`) is a complete small example with a per-target override for the OpenMP program.

**CMake** [S36]: generates Makefiles or Ninja files from `CMakeLists.txt`; handles dependencies, platforms, `find_package`. The working file is [`src/cpp/CMakeLists.txt`](../src/cpp/CMakeLists.txt); the core of it is

```cmake
cmake_minimum_required(VERSION 3.20)
project(nssc1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)     # see below: without this it is only a request
if(APPLE)                               # see below: FindOpenMP cannot find a Homebrew keg
    execute_process(COMMAND brew --prefix libomp
                    OUTPUT_VARIABLE BREW_LIBOMP OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)
    if(BREW_LIBOMP)
        set(OpenMP_ROOT "${BREW_LIBOMP}")
    endif()
endif()
find_package(OpenMP REQUIRED)
add_executable(omp_examples omp_examples.cpp)
target_link_libraries(omp_examples PRIVATE OpenMP::OpenMP_CXX)
add_executable(csr csr.cpp)
enable_testing()
add_test(NAME csr COMMAND csr --test)   # a target name resolves to its binary; no path needed
```

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure
```

Out-of-source builds keep the tree clean. `CMAKE_BUILD_TYPE` picks the flags; on this toolchain `cmake --system-information` reports [S34]

| build type | `CMAKE_CXX_FLAGS_<TYPE>` |
|---|---|
| `Debug` | `-g` - note: **not** `-O0`, it is simply the absence of an `-O` flag |
| `Release` | `-O3 -DNDEBUG` |
| `RelWithDebInfo` | `-O2 -g -DNDEBUG` |
| `MinSizeRel` | `-Os -DNDEBUG` |

**There is no default build type.** Configure without `-DCMAKE_BUILD_TYPE` and `${CMAKE_BUILD_TYPE}` is the empty string, so *none* of those flag sets is applied and you get an unoptimised build - the commonest way to benchmark a debug build by accident. Our file forces `Release` when none is given.

**Two things this snippet gets right that the obvious version does not.** Both were found by installing CMake (4.4.3) and running it [S34]; the earlier version of this note was written with no CMake on the machine and had both bugs.

1. **`set(CMAKE_CXX_STANDARD 17)` alone is a request, not a requirement.** With `CXX_STANDARD_REQUIRED` unset or `OFF` - the default - the standard is, in CMake's own words, "treated as optional and may 'decay' to a previous standard if the requested is not available" [S36]. You get a silently older dialect instead of an error. Always set both, and `set(CMAKE_CXX_EXTENSIONS OFF)` to get `-std=c++17` rather than `-std=gnu++17`.
2. **`find_package(OpenMP REQUIRED)` fails outright with Apple's clang.** Verbatim:

   ```
   CMake Error at .../FindPackageHandleStandardArgs.cmake:290 (message):
     Could NOT find OpenMP_CXX (missing: OpenMP_CXX_FLAGS OpenMP_CXX_LIB_NAMES)
   ```

   Xcode's clang does not ship `libomp`, and `FindOpenMP` does not look inside a Homebrew keg. Setting `OpenMP_ROOT` to `$(brew --prefix libomp)` fixes it - CMake's `<PackageName>_ROOT` variable is searched first by every `find_package` module [S36]. With it, configuration reports `Found OpenMP_CXX: -Xclang -fopenmp (found version "5.1")` and `ctest` runs 10/10 green. On Linux with gcc the `if(APPLE)` block is a no-op.

Python: `pyproject.toml`, a virtual environment (`python -m venv .venv`), pinned `requirements.txt`; `pip install -e .` for an importable package.

## Compilers and linking

Pipeline: preprocess (`-E`: includes, macros) -> compile to assembly (`-S`) -> assemble to object file (`-c`, `.o`) -> link (`ld`, called by `clang++`) objects and libraries into an executable or library.

- Headers declare, one `.cpp` defines (one-definition rule); `inline`/templates may live in headers.
- Static library `libfoo.a` (archive of `.o`, copied into the executable) vs shared `libfoo.so`/`.dylib` (loaded at run time, `DYLD_LIBRARY_PATH`/`LD_LIBRARY_PATH` or rpath). Flags: `-I dir` (headers), `-L dir` (library search path), `-l foo` (link `libfoo`), `-fPIC -shared` to build a shared library.
- "undefined symbol" = declared, used, but no definition linked (missing `-l`, wrong order: libraries after the objects that use them, or a C function called from C++ without `extern "C"`: name mangling). "multiple definition" = a non-inline function defined in a header included twice.
- `nm`, `objdump -d`, `otool -L` / `ldd` to inspect symbols and dependencies. Compiler explorer (godbolt.org) to see what a loop compiles to.

## Debugging

1. Compile with `-g -O0` (or `-O1 -g` when the bug vanishes without optimisation, itself a hint at undefined behaviour).
2. `lldb ./bin/csr -- --test`: `b csr.cpp:42` (breakpoint), `r` (run), `bt` (backtrace after a crash), `f 2` (select frame), `p x` / `p v[3]` / `p *this`, `n` (next line), `s` (step into), `c` (continue), `watch set var x` (stop when `x` changes), `q`. gdb has the same commands with slightly different spellings.
3. **Sanitizers** [S37] (`sanitizers.sh`): `-fsanitize=address` (ASan: heap/stack/global buffer overflow, use-after-free, use-after-return, double free, leaks; the paper reports **~2x** slowdown and ~2-3x memory [S38]), `-fsanitize=undefined` (UBSan: signed overflow, misaligned access, out-of-bounds on arrays of known size, division by zero, almost free), `-fsanitize=thread` (TSan: data races in OpenMP/pthread code, **5-15x** slowdown and 5-10x memory [S37]). ASan and TSan cannot be combined; ASan and UBSan can. The demo shows the same bugs printing garbage or nothing without instrumentation: at `-O1` clang removed the `printf` after the out-of-bounds read because a path with undefined behaviour is assumed unreachable. Sanitizer reports name the bug class, file and line, and the allocation site.
4. `valgrind --tool=memcheck` (Linux; slower but no recompilation), `--tool=cachegrind` for cache misses.
5. `assert(cond)` for invariants (removed by `-DNDEBUG`); the `CHECK` macro in `common.hpp` survives release builds. Print statements with the values that matter, not "here".
6. Floating-point: enable FP exceptions (`feenableexcept` on Linux) to trap the first NaN; check `std::isfinite` at stage boundaries.

## Testing

- **Unit test**: one function, known input and output (`thomas` vs `numpy.linalg.solve`; SpMV vs dense). **Regression test**: output must not change (stored reference file, tolerance). **Integration test**: the whole program on a small case (`make test` runs every program with `--test`).
- Numerical tests need tolerances: relative $10^{-12}$ for algebra, discretisation-order tests for PDE solvers (observed order within 0.1 of the theory: `test_poisson1d_second_order_and_scipy`), statistical tests for random code (KS test, error within $4\sigma$: `test_montecarlo.py`; fix the seed).
- **Method of manufactured solutions**: pick $u$, compute $f = L u$ analytically, solve $Lu_h = f$, check $\|u_h - u\| = O(h^p)$. Avoid eigenfunctions of $L_h$ (note 04 pitfall).
- Cross-check against a library (scipy, LAPACK) rather than against your own second implementation.
- Frameworks: pytest (discovery of `test_*.py`, `assert`, fixtures, `pytest -q`), Catch2 / GoogleTest / doctest for C++, `ctest` as the runner. Continuous integration (GitHub Actions) runs them on every push.
- Test the failure modes too: unstable time step must blow up (`test_explicit_beyond_cfl_blows_up`), CG on a non-SPD matrix must be rejected.

## Documentation

README (what, how to build, how to run, how to cite), a `--help` for every executable, docstrings (Python: first line summary; NumPy style `Parameters/Returns`) and Doxygen comments (`/** ... @param @return */`) for C++, generated with Sphinx / Doxygen. Comment the algorithm and the non-obvious decisions (why this tolerance, why this ordering), not the syntax. Keep a CHANGELOG or tagged releases. Record the environment: compiler version, flags, library versions, seed, machine (`build_and_bench.sh` prints CPU and compiler on top of every table).

## Software licences

Checked against the licence texts themselves [S41], not from memory. The identifiers are SPDX's.

| licence | type | you may | you must |
|---|---|---|---|
| MIT, BSD-2/3 | permissive | use, modify, sell, close source | keep the copyright notice |
| Apache-2.0 | permissive | same | keep the notice and the `NOTICE` file, **state your changes**; you get an express patent grant that terminates if you sue over patents |
| GPL v2/v3 | strong copyleft | use, modify | distribute derived works under GPL with source |
| LGPL-2.1/3.0 | weak copyleft | link as a library from closed code | changes to the library itself stay LGPL, and the user must be able to relink against a modified version |
| MPL 2.0 | file-level copyleft | mix with proprietary files | modified MPL files stay MPL |
| no licence | all rights reserved | nothing beyond reading | ask the author |

Consequences: linking GPL code (e.g. FFTW's default licence, GSL) makes your **distributed** program GPL - the obligations trigger on distribution, not on use; MIT/BSD/Apache libraries impose nothing beyond attribution. Worth knowing for this course: numpy and scipy are BSD-3, Eigen is MPL-2.0, LLVM is Apache-2.0-with-LLVM-exception, VTK is BSD-3 [S13], and the reference PDFs in [`../refs/`](../refs/README.md) are almost all *unlicensed free downloads*, which means all rights reserved - the default that catches people out. Choose a licence for your own code before publishing; put it in `LICENSE`. Cite software you use in publications (many packages have a `CITATION.cff`).

## Language interfaces: C++ from Python

Prototype in Python, move the hot loop to C++, keep the driver in Python.

**ctypes** (standard library, C ABI only):
```cpp
// dot.cpp:  clang++ -O2 -shared -fPIC dot.cpp -o libdot.dylib
extern "C" double dot(const double* a, const double* b, int n) {
    double s = 0; for (int i = 0; i < n; ++i) s += a[i] * b[i]; return s;
}
```
```python
import ctypes, numpy as np
lib = ctypes.CDLL("./libdot.dylib")
lib.dot.restype = ctypes.c_double
lib.dot.argtypes = [ctypes.POINTER(ctypes.c_double)] * 2 + [ctypes.c_int]
a = np.arange(1e6); b = np.ones_like(a)
p = lambda x: x.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
lib.dot(p(a), p(b), a.size)        # numpy memory passed by pointer, no copy
```
`extern "C"` disables name mangling; arrays must be contiguous (`np.ascontiguousarray`) and of the right dtype.

**pybind11** [S39] (header-only, C++ classes, exceptions, numpy via `py::array_t<double>`):
```cpp
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;
double dot(py::array_t<double> a, py::array_t<double> b) {
    auto x = a.unchecked<1>(), y = b.unchecked<1>();
    double s = 0; for (py::ssize_t i = 0; i < x.shape(0); ++i) s += x(i) * y(i); return s;
}
PYBIND11_MODULE(fastdot, m) { m.def("dot", &dot, "dot product"); }
```
Built with `setup.py`/scikit-build or `c++ -O3 -shared -fPIC $(python3 -m pybind11 --includes) dot.cpp -o fastdot$(python3-config --extension-suffix)`; then `import fastdot`. Alternatives: Cython, nanobind, numba (`@njit`, no C++ needed), `cffi`. Release the GIL in long C++ calls (`py::gil_scoped_release`) if Python threads should overlap.

## Pitfalls

- Committing generated files, then fighting merge conflicts in them.
- A Makefile without header dependencies: edit `common.hpp`, nothing rebuilds (use `-MMD` generated dependency files or CMake, which tracks them for you). Our `src/cpp/Makefile` has this flaw; `make cmake` does not.
- Configuring CMake without `-DCMAKE_BUILD_TYPE`: no optimisation flags at all, and every benchmark is meaningless.
- Tests that pass because the tolerance is huge, or that compare a code with itself.
- Debugging an optimised build without `-g`: no line numbers; debugging `-O0` only and never running sanitizers on the `-O2` build where UB actually bites.
- `float` counters, `int` overflow at $2^{31}$ for index arithmetic on large grids: use `std::size_t`/`int64_t`; UBSan catches the overflow.
- ctypes with a non-contiguous or `float32` array: silently wrong numbers, no error.
- "Works on my machine": undocumented compiler flags, hard-coded paths, unrecorded seeds.

## Exam-style questions

1. **Explain the difference between `git merge` and `git rebase` and when each is appropriate.** Merge creates a commit with two parents, preserving both histories; rebase replays your commits on top of another branch, producing a linear history but new commit ids. Rebase your private feature branch onto main before merging; never rebase commits others have already pulled.
2. **What does the linker do, and what causes an "undefined reference to `foo`" error?** It resolves symbol references across object files and libraries and lays out the executable. The error means `foo` was declared and called but no object or library on the command line defines it: missing source file or `-lfoo`, library listed before the object using it, or C/C++ name mangling mismatch (`extern "C"`).
3. **Name three classes of bugs AddressSanitizer finds and one it does not.** Heap/stack buffer overflow, use-after-free, memory leaks (also double free, use-after-return). It does not find uninitialised reads (MemorySanitizer/valgrind), data races (ThreadSanitizer) or logic errors.
4. **Design a test suite for a new 2D Poisson solver.** (a) SpMV against a dense matrix; (b) solver on a tiny system with a known solution; (c) manufactured non-eigenfunction solution with observed order 2 over three refinements; (d) residual below tolerance and iteration counts in the expected range; (e) a regression case with stored output; (f) failure modes: non-square input rejected. Run under `make test` and in CI with a fixed seed.
5. **You want to distribute a code that links to a GPL library and to numpy. What are your options?** Distribute under GPL (source included), or replace the GPL dependency with a permissively licensed one, or keep the code internal (GPL obligations trigger on distribution). numpy (BSD) requires only its notice.

Code: `src/sh/git_workflow.sh`, `src/sh/sanitizers.sh` + `buggy_sample.cpp`, `src/cpp/CMakeLists.txt` (`make -C src/cpp cmake`), `src/cpp/Makefile`, `src/cpp/common.hpp` (`CHECK`), `src/py/test_*.py`. Sources: [S8] [S13] [S34] [S36] [S37] [S38] [S39] [S40] [S41].
