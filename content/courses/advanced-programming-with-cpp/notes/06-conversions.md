# 06 Conversions: implicit, explicit, narrowing, user-defined

C inherited "usual arithmetic conversions" that silently change signedness and
precision; C++ added user-defined conversions that the compiler chains into overload
resolution. Both are frequent sources of "it compiles but computes the wrong thing".
Item 005 (types, expressions, conversions, precedence) [S3]; ES.46, C.46, C.164 [S10].

Code: `src/cpp/conversions.cpp` (mostly `static_assert`s).

## Definitions [S8 [conv.rank], [dcl.init.list], [over.ics.rank]]

- **Integral promotion**: operands of rank below `int` (`char`, `short`, `bool`,
  `unsigned char`) become `int` before arithmetic. `uc + uc` is `int`.
- **Usual arithmetic conversions** (binary operators): if either is floating, convert
  to the wider floating type; else promote, then if signedness differs and the unsigned
  type's rank >= the signed one's, **the signed operand becomes unsigned**. Hence
  `-1 < 0u` is `false` and `v.size() - 4` wraps for small vectors.
- **Floating-integral**: `double -> int` truncates toward zero; if the value does not
  fit, UB. `int64 -> double` rounds above $2^{53}$.
- **Narrowing conversion**: float to int; double to float (unless a constant that fits);
  integer to float (unless a constant that fits exactly); integer to a type that
  cannot represent all its values (incl. signed <-> unsigned). **Ill-formed inside
  braces**: `int i{3.7};` is an error, `int i = 3.7;` a silent truncation.
- **Standard conversion sequence** ranks [S8 [over.ics.rank]]: *exact match*
  (incl. lvalue-to-rvalue, array/function decay, qualification) > *promotion* > *conversion*.
  Then **user-defined conversion sequence** (at most **one** user-defined conversion,
  surrounded by standard ones), then ellipsis.
- **User-defined conversions** [S8 [class.conv.ctor], [class.conv.fct]]: a
  **converting constructor** (any non-`explicit` constructor callable with one argument)
  and a **conversion function** `operator U() const`. `explicit` removes them from
  implicit conversion; `explicit operator bool` still works in *contextual* conversions
  (`if`, `&&`, `!`, `?:`).
- **Casts**: `static_cast` (checked, value-preserving intent), `const_cast` (add/remove
  const only), `reinterpret_cast` (bits as another type, mostly UB to use),
  `dynamic_cast` (checked downcast at run time, note 09), `std::bit_cast` (C++20,
  copy the object representation; the safe way to type-pun). C-style `(T)x` tries
  them in sequence: avoid.

## Complete example

```cpp
// complete example: conversions
#include <cstdio>
#include <utility>
#include <vector>

void f(int) { std::puts("f(int)"); }
void f(double) { std::puts("f(double)"); }

struct Celsius { double v; Celsius(double x) : v(x) {} };                 // converting ctor
struct Kelvin { double v; explicit Kelvin(double x) : v(x) {} };          // explicit
double heat(Celsius c) { return c.v + 1; }

template <class To, class From> concept brace_ok = requires(From x) { To{x}; };
static_assert(brace_ok<long, int> && !brace_ok<int, double> && !brace_ok<unsigned, int>);

int main() {
    f('a');                 // f(int): char -> int is a promotion
    f(2.0f);                // f(double): float -> double is a promotion
    // f(2L);               // error: long -> int and long -> double are both conversions: ambiguous
    std::printf("%d %d\n", -1 < 0u, std::cmp_less(-1, 0u));              // 0 1
    std::vector<int> v{1, 2, 3};
    std::printf("%zu %td\n", v.size() - 4, std::ssize(v) - 4);            // 18446744073709551615 -1
    std::printf("%g\n", heat(20.0));                                       // implicit double -> Celsius
    // heat(Kelvin{1});     // error: no conversion Kelvin -> Celsius
    Kelvin k{300.0};        // explicit construction is fine
    std::printf("%d %ld\n", static_cast<int>(-2.7), static_cast<long>(k.v));   // -2 300
}
```

## Pitfalls

- Mixed signed/unsigned comparisons and subtractions (`for (int i = 0; i < v.size() - 1; ++i)`
  loops ~2^64 times on an empty vector). Use `std::ssize` or `std::cmp_less`. Clang
  warns (`-Wsign-compare`) only with `-Wextra`, not with `-Wall` alone (checked [S13]);
  the 2021W hand-outs built with `-Wall -pedantic -Werror` [S4], which misses it under
  clang (GCC's documentation puts `-Wsign-compare` into `-Wall` for C++; not checked here).
- `double` loop counters and `float` accumulators: conversions hide the precision loss.
- A non-`explicit` single-argument constructor makes every function taking that class
  accept the argument type (`void simulate(Grid g); simulate(100);`). Default to
  `explicit` (C.46).
- An implicit `operator bool()` lets `obj + 1` and `obj == other_obj` compile via
  `bool -> int`. Use `explicit operator bool`.
- Two user-defined conversions are never chained: `Wrapper(Celsius)` does not accept
  a `double`.
- `enum` (unscoped) converts to `int` implicitly; `enum class` does not
  (`std::to_underlying`, C++23).
- `reinterpret_cast<uint32_t&>(f)` to read float bits: strict-aliasing UB; `std::bit_cast`.
- Out-of-range floating -> integer is UB, not saturation; check with a range test first
  (`std::in_range<T>` works for integers).

## Discussion questions

1. **Why is `-1 < 0u` false?** Usual arithmetic conversions: `int` and `unsigned int`
   have the same rank, so the `int` is converted to `unsigned`; `-1` becomes
   `UINT_MAX`. `std::cmp_less` (C++20) compares mathematical values.
2. **Why are brace initialisers recommended?** They forbid narrowing (`int i{d}` is an
   error), work uniformly for aggregates, containers and classes, and avoid the most
   vexing parse. Caveat: a class with an `initializer_list` constructor prefers it
   (`std::vector<int>{5}` is one element, `(5)` is five).
3. **Given `f(int)` and `f(double)`, which is called for `f('a')`, `f(1.0f)`, `f(1L)`?**
   `f(int)` (promotion beats conversion), `f(double)` (promotion), ambiguous (both
   conversions, equal rank): a compile error.
4. **When should a constructor be `explicit`?** Whenever the argument is not "the same
   value in another representation". `std::string(const char*)` is implicit on purpose;
   `std::vector(size_t)` is explicit, otherwise `v = 5;` would compile. For units and
   physical quantities, explicit prevents unit mix-ups (`Meters` in `conversions.cpp`).
5. **What is the difference between `static_cast<uint32_t>(1.0f)` and `std::bit_cast<uint32_t>(1.0f)`?**
   Value vs representation: the first gives `1`, the second `0x3f800000` (IEEE 754
   single-precision 1.0). `bit_cast` requires equal sizes and trivially copyable types
   and is `constexpr`.

## In the code

- `src/cpp/conversions.cpp`: promotions and arithmetic conversions as `static_assert`s; the `brace_convertible` concept detects narrowing; overload ranking incl. two ambiguities tested with a concept; `explicit` ctor and conversion operator; `explicit operator bool`; `enum class` + `to_underlying`; the $2^{53}$ rounding; `bit_cast`.
- `src/cpp/compile_fail/narrowing.cpp`: `int i{d};` must be rejected.
