# 360.251 Advanced Programming with C++ - reference programs

C++23 only (the course's language [S1]); no Python, no dependencies beyond the standard
library. One program per TISS topic, each a list of self-checks: `CHECK(expr)` from
[`cpp/check.hpp`](cpp/check.hpp) records pass/fail with file:line, `chk::skip` prints
why a missing feature was skipped, the exit code is non-zero on any failure. Most
compile-time claims are `static_assert`s: if the file compiles, they hold.

## Build and test (everything)

```sh
make -C cpp test        # probe the toolchain, build bin/, run all checks + the compile-fail suite (~30 s from clean)
make -C cpp features    # the C++23 support table of this toolchain
make -C cpp sanitize    # same tests with ASan + UBSan (bin-asan/)
make -C cpp tsan        # concurrency.cpp under ThreadSanitizer
make -C cpp cmake       # the matrix hand-in through CMake + ctest (ASan + UBSan on)
./cpp/bin/concurrency --bench   # seq vs par timings
make -C cpp clean
```

Toolchain: Apple clang 21.0.0, `clang++ -std=c++23 -O2 -Wall -Wextra` (no warnings);
CMake >= 3.25 only for `make cmake` (verified with 4.4.3) [S13]. Build output (`bin/`,
`bin-asan/`, `build/`) is git-ignored by `cpp/.gitignore`. No network at build or test time.

## Feature guards

`cpp/probe.sh` compiles, links **and runs** each `cpp/probes/*.cpp` once per build
directory and writes `bin/features.flags` (`-DHAVE_PRINT=1 ...`), `bin/features.txt`
(the table), `bin/experimental.flags` and `bin/modules.flags`. Every program is compiled
with the flags; missing library features are `#if defined(HAVE_...)`-guarded and print
`SKIP <feature>: <reason>` instead of breaking the build. The modules demo is skipped as
a whole (with a message) if no module interface can be precompiled. Probing is needed
because the `__cpp_lib_*` macros under-report on libc++ 21 (`zip`, `fold` present
without macros; parallel algorithms without any macro).

## Files

| file | note | what it checks |
|---|---|---|
| `basics_main.cpp`, `basics_other.cpp`, `basics.hpp` | 01 | two TUs: `inline` vs `static` vs `extern` vs `constexpr` variables compared by address; the ODR trap of an inline function using a per-TU static |
| `modules/geometry.cppm`, `modules/modules_main.cpp` | 01 | a named module (global module fragment, exported and non-exported names), built in four steps by the Makefile |
| `deduction.cpp` | 02 | `auto`/`decltype`/template deduction table as `static_assert`s, `decltype(auto)`, CTAD with a deduction guide, copy-deduction preference |
| `lifetime.cpp` | 03 | trivially copyable / standard-layout / aggregate / implicit-lifetime, `memcpy`, `bit_cast`, destruction order, temporary lifetime extension (incl. via a member and P2718 range-for), `construct_at`/`destroy_at`, implicit object creation |
| `pointers.cpp` | 04 | const placement, reference vs pointer, `span`, nullable observer, reallocation, `reference_wrapper`, ownership transfer |
| `value_categories.cpp` | 05 | category of 10 expressions via `decltype((e))`; copies/moves counted for construction, sinks, forwarding, `push_back`/`emplace_back`, `move_if_noexcept` on reallocation |
| `conversions.cpp` | 06 | promotions, signed/unsigned, narrowing detected by a concept, overload ranking and ambiguity, `explicit` constructors/conversions, `enum class`, `bit_cast` vs `static_cast` |
| `lambdas.cpp` | 07 | capture semantics, closure size, `mutable`, move-only init-capture, `this`/`*this`, generic and template lambdas, recursive lambda (deducing `this`), `static` lambda, `std::function` copies |
| `operators.cpp` | 08 | `phys::vec3` with hidden friends, ADL, defaulted `<=>` (partial ordering, NaN), `std::set`, `operator[]`, `operator<<`, `std::formatter`; `Rational` with strong ordering |
| `classes.cpp` | 09 | rule of five with copy-and-swap, rule of zero, destructor suppressing moves, abstract base / `final` / `dynamic_cast` / vptr size, slicing, CRTP |
| `smart_pointers.cpp` | 10 | deleter sizes, RAII `FILE*`, allocation count of `make_shared` (1) vs `new` (2), `weak_ptr`, a leaking cycle (on purpose) vs a weak back edge, aliasing ctor, `my::unique_ptr` |
| `ranges.cpp` | 11 | iterator concepts, a hand-written forward iterator, a sentinel range, lazy views, projections, `dangling`, `split`, `ranges::to`, `zip`, `fold_left`; SKIPs for `enumerate`, `chunk`, `stride`, `generator` |
| `constexpr.cpp` | 12 | `constexpr` with `vector`/`string`/`unique_ptr`, compile-time tables, `consteval`, `if consteval`, `constinit`, compile-time tests |
| `compile_fail/*.cpp`, `compile_fail/check.sh` | 12, 06, 10, 13 | 8 programs that must be rejected with a specific error: constexpr overflow and out-of-bounds, leaked constexpr allocation, `consteval` with a runtime value, narrowing, concept violation, copying a `unique_ptr`, `Matrix<std::string>` |
| `concepts.cpp` | 13 | `enable_if` vs `requires`, subsumption and its failure with raw traits, `Scalar`/`SizedContainer` concepts, folds, forwarding wrapper, `std::apply` |
| `concurrency.cpp` | 14 | mutex, atomic, private partials; release/acquire; `jthread` + `stop_token`; condition-variable channel; promise/future/`async` incl. exceptions; `latch`; `shared_ptr` across threads; `par`/`par_unseq` algorithms; `--bench` |
| `features.cpp` | all | prints the language/library support table and exercises every feature marked "yes" |
| `matrix/` | 13 | the library hand-in example, see below |

## `matrix/`: a library hand-in in the course's shape

```
matrix/
  include/la/matrix.hpp    header-only la::Matrix<Scalar T>
  tests/test_matrix.cpp    28 checks + static_asserts
  CMakeLists.txt           INTERFACE library, C++23 required, ctest, option LA_SANITIZE
```

Same layout as the 2021W hand-outs (`include/`, `tests/`, CMake + ctest) [S4], written
from scratch. Design decisions and the reasons are tabulated in
[note 13](../notes/13-templates-and-concepts.md#the-library-hand-in-example-lamatrix-srccppmatrix).
The tests cover algebraic identities (associativity, transpose rules, identity), Pauli
matrices over `std::complex<double>`, `matvec` with `vector`/`list`/`iota` inputs,
exceptions vs `std::expected`, storage reuse for rvalue operands, `mdspan` aliasing,
`std::format`, and a `constexpr` product checked by `static_assert`.

## Not here, on purpose

- No copies of the lecturers' hand-outs or solutions (no licence) [S3] [S4]. Clone them
  with `../refs/fetch-sources.sh`; building them on this Mac needs
  `-DCMAKE_POLICY_VERSION_MINIMUM=3.5` and their sanitizers are off under AppleClang
  (see [note 00](../notes/00-exam-focus.md#how-to-prepare-per-hand-in)).
- No benchmarks in the test target (timings are machine-dependent); only `--bench`.
