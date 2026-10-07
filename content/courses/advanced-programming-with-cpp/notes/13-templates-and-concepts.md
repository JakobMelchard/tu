# 13 Templates and concepts: SFINAE vs requires, concept design, variadic templates, folds

Templates are how C++ writes one algorithm for many types; concepts (C++20) state what
those types must provide, checked at the call site. The learning outcome "design own
C++ libraries using language features and the standard library efficiently" [S1] is
mostly this note. 2021W: items 011 (function templates) and 012 (class templates);
hand-outs ex2.1 (variadic forwarding wrapper) and ex2.2 (class template, CTAD) [S3] [S4];
concepts were not yet taught (C++17). T.10, T.20 [S10].

Code: `src/cpp/concepts.cpp` and the library hand-in example `src/cpp/matrix/`.

## Definitions [S8 [temp.constr.decl], [temp.variadic], [expr.prim.fold]]

- **Template**: a pattern; **instantiation** generates a function/class for concrete
  arguments at compile time (in every TU that uses it: templates live in headers).
  Kinds of parameters: type (`class T`), non-type (`std::size_t N`, since C++20 also
  floating and literal class types), template template (`template<class> class C`).
- **Two-phase lookup**: non-dependent names are checked at definition, dependent ones
  at instantiation; `typename T::value_type` and `x.template get<0>()` disambiguate.
- **SFINAE** ("substitution failure is not an error"): if substituting deduced types
  into a declaration fails, that overload is silently removed. `std::enable_if_t<cond, int> = 0`
  hides a constraint in a default template argument. Works, but errors are unreadable
  and constraints are not part of the visible interface.
- **Concept**: a named compile-time predicate on types, `template<class T> concept C = expr;`.
  **Requires-expression** `requires(T a, T b) { a + b; { a * b } -> std::convertible_to<T>; typename T::value_type; }`
  checks that expressions compile (and their result types).
- Four equivalent spellings of a constrained template:
  `template<C T> void f(T)`, `template<class T> requires C<T> void f(T)`,
  `template<class T> void f(T) requires C<T>`, `void f(C auto)` (abbreviated).
- **Subsumption**: if concept `A` is defined as `B && extra`, an overload constrained by
  `A` is *more constrained* than one constrained by `B` and wins. Only works through
  named concepts (atomic constraints must be the same expression), not through two
  separately spelled `std::is_..._v` traits (`concepts.cpp`: ambiguous).
- **Concept design** (T.20): model semantic requirements (a "Scalar" that supports
  field operations), not syntactic accidents (`HasPlus`). Prefer the standard concepts
  (`std::integral`, `std::floating_point`, `std::regular`, `std::ranges::range`, `std::invocable`).
- **Variadic template**: `template<class... Ts> void f(Ts&&... xs)`; `sizeof...(Ts)`;
  pack expansion `g(std::forward<Ts>(xs)...)`.
- **Fold expression** (C++17): `(xs + ...)`, `(... + xs)`, `(xs + ... + 0)` (with init:
  safe for empty packs), `((std::cout << xs), ...)` (comma: do something for each in order).
  Empty pack: `&&` gives `true`, `||` `false`, `,` `void()`, others need an init.

## Complete example

```cpp
// complete example: concepts
#include <complex>
#include <concepts>
#include <cstdio>
#include <list>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

template <class T>
concept Scalar = std::regular<T> && requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
    { a * b } -> std::convertible_to<T>;
    { a / b } -> std::convertible_to<T>;
    T{0};
};
static_assert(Scalar<double> && Scalar<std::complex<double>> && !Scalar<std::string>);

template <std::ranges::sized_range R>
    requires Scalar<std::ranges::range_value_t<R>>
auto mean(const R& r) {
    std::ranges::range_value_t<R> s{0};
    for (const auto& x : r) s = s + x;
    return s / static_cast<std::ranges::range_value_t<R>>(std::ranges::size(r));
}

constexpr int pick(std::integral auto) { return 1; }
constexpr int pick(std::signed_integral auto) { return 2; }      // more constrained: wins for int

template <class... Ts> constexpr auto sum(Ts... xs) { return (xs + ... + 0); }

template <class F, class... Args> decltype(auto) timed(F&& f, Args&&... args) {   // ex2.1 shape
    // (start clock)
    decltype(auto) r = std::forward<F>(f)(std::forward<Args>(args)...);
    // (stop clock)
    return r;
}

int main() {
    std::printf("%g %d\n", mean(std::vector{1.0, 2.0, 6.0}), mean(std::list{2, 4}));   // 3 3
    std::printf("%d %d %d\n", pick(1u), pick(1), sum(1, 2, 3));                          // 1 2 6
    auto m = mean(std::vector<std::complex<double>>{{1, 1}, {1, -1}});
    std::printf("(%g,%g)\n", m.real(), m.imag());                                          // (1,0)
    std::string s = "x";
    std::printf("%zu\n", timed([](std::string& t, int n) { t.append(n, '!'); return t.size(); }, s, 3));   // 4
    // mean(std::vector<std::string>{});   // error: constraints not satisfied, names Scalar
}
```

## The library hand-in example: `la::Matrix` (`src/cpp/matrix/`)

The kind of thing the learning outcomes ask for [S1], in the shape of the 2021W
hand-outs (header in `include/`, tests in `tests/`, CMake + ctest) [S4]:

| design decision | why |
|---|---|
| `template <Scalar T> class Matrix` with a `Scalar` concept | errors at the call site ("`std::string` does not satisfy `Scalar`", checked in `compile_fail/matrix_of_string.cpp`); `int`, `double`, `std::complex` all work (Pauli-matrix test) |
| `std::vector<T>` storage, row-major | rule of zero: copy, move, destructor all correct and `noexcept` move for free |
| `m[i, j]` (C++23) and `m(i, j)`; `at(i, j)` throws `out_of_range` | unchecked fast path + checked path; `operator[]` guarded by `__cpp_multidimensional_subscript` |
| `row(i)` returns `std::span`, `col(j)` a view, `md()` a `std::mdspan` | no copies, standard vocabulary types, ranges algorithms apply directly |
| `operator+(Matrix a, const Matrix& b) { a += b; return a; }` | rvalue left operands reuse storage (tested: same data pointer) |
| `operator*` throws `invalid_argument`; `try_multiply` returns `std::expected<Matrix, Error>` | contract violation vs expected outcome: the caller chooses |
| `matvec(const Matrix<T>&, R&& x)` for any `sized_range` convertible to `T` | works with `vector`, `list`, `views::iota` |
| everything `constexpr` | `static_assert(trace_of_square() == 29)`: the product is computed by the compiler |
| `std::formatter<la::Matrix<T>>` forwarding the element spec | `std::format("{:.1f}", m)` |

Build and test: `make -C src/cpp test` (direct), `make -C src/cpp cmake` (CMake,
ASan + UBSan, ctest). 28 checks + 3 `static_assert`s + 1 compile-fail.

## Pitfalls

- Template code in a `.cpp` file: "undefined symbol" at link time for every
  instantiation the `.cpp` did not see. Put it in the header (or explicitly instantiate).
- Constraining with a concept that is too weak (`requires { a + b; }`) accepts
  `std::string` into numerical code; too strong (`std::floating_point`) rejects
  `std::complex`. Design around the operations the algorithm uses.
- Concepts check syntax, not semantics: `Scalar<Matrix<double>>` might be true while
  multiplication is not commutative. Document the semantic requirements.
- Forwarding the same pack twice (`f(std::forward<Ts>(xs)...); g(std::forward<Ts>(xs)...);`):
  the second call may see moved-from objects.
- `decltype(auto)` + returning a local by name in parentheses returns a dangling reference.
- Error novels: with SFINAE, the error points deep into the library; with concepts, it
  names the unsatisfied requirement. Prefer concepts in new code.
- Code bloat: every distinct `T` instantiates everything; keep type-independent code in
  non-template helpers.

## Discussion questions

1. **SFINAE vs `requires`: same effect, why prefer concepts?** Both remove non-matching
   overloads. Concepts are part of the declaration (readable interface), allow
   subsumption-based overload ordering, give errors naming the failed requirement, and
   can be reused and composed; `enable_if` hides the constraint in a dummy parameter.
2. **Why does `pick(std::signed_integral auto)` beat `pick(std::integral auto)` for an `int`?**
   `std::signed_integral<T>` is defined as `std::integral<T> && std::is_signed_v<T>`, so
   its normal form contains `integral`'s: it subsumes it, is more constrained, and is
   chosen. With two raw `requires std::is_integral_v<T>` spellings the compiler cannot
   see that relation: ambiguous.
3. **How do you write a function that forwards any number of arguments of any category to a callable?**
   `template<class F, class... Args> decltype(auto) call(F&& f, Args&&... args)
   { return std::forward<F>(f)(std::forward<Args>(args)...); }` (or `std::invoke` to also
   support member pointers). Forwarding references + pack expansion + `std::forward`;
   `decltype(auto)` preserves a returned reference. This was hand-out ex2.1 [S4].
4. **What is a fold expression, and what happens with an empty pack?** A single
   expression that applies a binary operator over a pack. Unary folds over an empty pack
   are valid only for `&&` (`true`), `||` (`false`) and `,`; otherwise use a binary fold
   with an initial value, `(xs + ... + 0)`.
5. **How did you decide what the `Scalar` concept requires?** From the operations the
   algorithms actually perform (`+ - *` unary `-`, construction from `0` and `1` for
   `identity`/`trace`, `std::regular` for copy/compare in tests), checked against the types
   that must pass (`int`, `double`, `complex`) and the ones that must fail (`string`, pointers).

## In the code

- `src/cpp/concepts.cpp`: `enable_if` vs `requires` vs abbreviated templates; subsumption and the raw-trait ambiguity; a `Scalar` and a `SizedContainer` concept; constrained `mean`; folds (`sum`, `all_positive`, `all_same`, comma-fold `join`); `call_counted` forwarding; pack recursion vs fold; `std::apply`.
- `src/cpp/matrix/`: `include/la/matrix.hpp`, `tests/test_matrix.cpp`, `CMakeLists.txt`.
