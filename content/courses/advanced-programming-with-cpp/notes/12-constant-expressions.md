# 12 Constant expressions: constexpr, consteval, constinit, compile-time tests

C++ can run a large subset of itself inside the compiler. Two payoffs: values computed
once at build time (tables, physical constants, dimension checks), and **undefined
behaviour becomes a compile error** during constant evaluation, which turns
`static_assert` into a unit-test framework that runs in the compiler. 2021W only
touched `if constexpr` (item 012) and the history (item 025) [S3]; the rest is from the
standard [S8]. Per.11 [S10].

Code: `src/cpp/constexpr.cpp` (the `static_assert`s are the tests) and
`src/cpp/compile_fail/` (programs that must be rejected; `make test` checks the error).

## Definitions [S8 [expr.const], [dcl.constexpr], [dcl.constinit]]

- **Constant expression**: an expression the compiler can evaluate, with no UB, no
  unknown runtime values, and every allocation freed before the evaluation ends. Required
  in `static_assert`, array bounds, template arguments, `case` labels, `constexpr`
  variable initialisers.
- **`constexpr` variable**: `const`, initialised by a constant expression.
- **`constexpr` function**: *may* be evaluated at compile time; is evaluated at run time
  when called with runtime arguments. Since C++20 it may contain loops, mutation, `try`,
  virtual calls, `new`/`delete` (transient), `std::vector` and `std::string`
  (libc++ 21: `__cpp_lib_constexpr_vector`/`_string` = 201907 [S13]); since C++23
  `std::unique_ptr` (`__cpp_lib_constexpr_memory` 202202, present).
- **`consteval` function** (C++20): an *immediate function*; every call must be a
  constant expression. A runtime argument is a compile error
  (`compile_fail/consteval_runtime_arg.cpp`).
- **`if consteval`** (C++23): branch on "am I being constant-evaluated?"; the first
  branch may call `consteval` functions. Replaces `std::is_constant_evaluated()`.
- **`constinit`** (C++20): a static/thread-storage variable must be initialised at
  compile time (no dynamic initialisation, no static-init-order fiasco); the variable
  itself stays mutable.
- **`if constexpr`** (C++17): discards the untaken branch at instantiation; the
  discarded branch need not compile for this `T`.
- **UB in constant evaluation is diagnosed**: signed overflow, out-of-bounds, reading an
  uninitialised object, a leaked allocation, calling a non-`constexpr` function, reaching
  a `throw`. This is why a `static_assert` over a `constexpr` function is a stronger
  test than a runtime assertion.

## Complete example

```cpp
// complete example: constexpr
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <vector>

constexpr std::uint64_t factorial(unsigned n) { return n <= 1 ? 1 : n * factorial(n - 1); }
static_assert(factorial(20) == 2432902008176640000ull);          // a unit test run by the compiler

constexpr int sum_primes_below(int n) {                          // std::vector in a constant expression
    std::vector<bool> comp(static_cast<std::size_t>(n));
    int s = 0;
    for (int i = 2; i < n; ++i) {
        if (comp[static_cast<std::size_t>(i)]) continue;
        s += i;
        for (int j = i * i; j < n; j += i) comp[static_cast<std::size_t>(j)] = true;
    }
    return s;
}
static_assert(sum_primes_below(100) == 1060);

constexpr auto legendre_p2 = [] {                                // table built at compile time
    std::array<double, 5> t{};
    for (std::size_t i = 0; i < t.size(); ++i) { double x = -1.0 + 0.5 * static_cast<double>(i); t[i] = 0.5 * (3 * x * x - 1); }
    return t;
}();
static_assert(legendre_p2[2] == -0.5 && legendre_p2[4] == 1.0);

consteval double sqrt_ce(double x) { double r = x; for (int i = 0; i < 60; ++i) r = 0.5 * (r + x / r); return r; }
constexpr double root(double x) {
    if consteval { return sqrt_ce(x); } else { return std::sqrt(x); }
}
constinit int counter = 0;                                       // compile-time init, mutable

int main(int argc, char**) {
    static_assert(root(2.0) > 1.41421356 && root(2.0) < 1.41421357);
    ++counter;
    std::printf("%llu %d %g %d\n", static_cast<unsigned long long>(factorial(static_cast<unsigned>(argc) + 4)),
                sum_primes_below(10 * argc), root(9.0 * argc), counter);   // 120 17 3 1
}
```

## Pitfalls

- `constexpr` on a function is a permission, not a guarantee: `int x = f(3);` may run at
  run time. Force compile time with `constexpr int x = f(3);`, a template argument, or
  `consteval`.
- A `constexpr` function that is *never* valid in a constant expression was ill-formed
  NDR before C++23 (P2448 relaxed it); do not rely on the compiler telling you.
- Transient allocation only: `constexpr std::vector<int> v{1, 2};` as a variable is an
  error (`compile_fail/leaked_allocation.cpp`); return a `std::array` instead.
- `<cmath>` functions are not `constexpr` in libc++ 21 (`__cpp_lib_constexpr_cmath`
  undefined [S13]): write your own iteration (as above) or use `if consteval`.
- Floating-point results at compile time may differ in the last bit from run time
  (no FMA contraction, different rounding of library calls). Compare with tolerances,
  or keep compile-time tests to exactly representable values.
- `constinit` does not imply `const`; `constexpr` implies `const`. `static constexpr`
  data members are implicitly `inline` (one object per program, note 01).
- Deep recursion or long loops hit the evaluator's step limit
  (`-fconstexpr-steps`, `-fconstexpr-depth` in clang).

## Discussion questions

1. **What is the difference between `constexpr` and `consteval`?** `constexpr`: may be
   evaluated at compile time, falls back to run time. `consteval`: must be evaluated at
   compile time; a call with runtime arguments does not compile. Use `consteval` for
   things that are meaningless at run time (compile-time format string checks,
   unit-conversion factors, validated literals).
2. **Why is a `static_assert` over a `constexpr` function a good test?** It runs on
   every build, cannot be forgotten, and the constant evaluator rejects UB (overflow,
   out-of-bounds, uninitialised reads) that a runtime test would silently pass. The
   compile-fail suite here shows each case being rejected.
3. **What problem does `constinit` solve?** The static initialisation order fiasco: a
   global whose dynamic initialiser runs at program start may be used by another TU's
   initialiser before it has run. `constinit` guarantees constant initialisation (no
   code runs), and errors if that is impossible.
4. **When would you use `if consteval`?** When the best run-time implementation is not
   usable in constant evaluation (libm `std::sqrt`, SIMD intrinsics, `memcpy`), but you
   want one function for both: the `consteval` branch computes portably, the other calls
   the fast path.
5. **`if constexpr` vs `if`: what is discarded, and why does it matter for templates?**
   With `if constexpr`, the untaken branch is not instantiated for that `T`, so it may
   contain code that would not compile for `T` (e.g. `x.size()` for an `int`). With an
   ordinary `if`, both branches must compile. (Item 012 makes exactly this point [S3].)

## In the code

- `src/cpp/constexpr.cpp`: factorial, a sieve with `std::vector` in constant evaluation, a transient `std::string`, `constexpr std::unique_ptr` (C++23), a binomial table via IIFE, `consteval` Newton square root with a `throw` for negative input, `if consteval`, `constinit`, a compile-time test of a generic algorithm, a non-type template argument; the same functions at run time.
- `src/cpp/compile_fail/`: `overflow_in_constexpr`, `out_of_bounds_in_constexpr`, `consteval_runtime_arg`, `leaked_allocation`, `narrowing`, `concept_violation`, `copy_unique_ptr`, `matrix_of_string`; `check.sh` requires each to fail with its `// expect:` message.
- `src/cpp/matrix/tests/test_matrix.cpp`: `static_assert` on the trace of a matrix product computed at compile time.
