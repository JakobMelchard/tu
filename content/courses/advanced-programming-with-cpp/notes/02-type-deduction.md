# 02 Type deduction: auto, decltype, template argument deduction, CTAD

The compiler infers types in four places; three of them follow **one** rule set
(template argument deduction), `decltype` follows another. Lecture items 005, 011,
012 [S3]; Meyers Items 1-4 [S16]; hand-out ex2.2 (CTAD) [S4].

Code: `src/cpp/deduction.cpp` (almost all `static_assert`s: it compiles, so the table holds).

## Definitions

- **Template argument deduction** [S8 [temp.deduct.call]]: for `template<class T> void f(P);`
  called as `f(expr)`, find `T` such that `P` matches the type `A` of `expr`. Three cases:

| parameter `P` | `A` = `const int&` lvalue | `A` = `int[3]` | `A` = rvalue `int` | rule |
|---|---|---|---|---|
| `T` (by value) | `T = int` | `T = int*` | `T = int` | drop reference, then top-level `const`/`volatile`; arrays and functions decay |
| `T&` | `T = const int` | `T = int[3]` | no match | `const` becomes part of `T`, no decay |
| `T&&` (forwarding) | `T = const int&` | `T = int(&)[3]` | `T = int` | lvalue -> `T` is an lvalue reference; rvalue -> plain `T` |

- **`auto`** [S8 [dcl.spec.auto]]: `auto x = e;` deduces like `P = T`, `auto& x = e;` like
  `T&`, `auto&& x = e;` like `T&&`. One exception: `auto x = {1, 2};` is
  `std::initializer_list<int>` (templates cannot deduce from a braced list).
- **`decltype(e)`** [S8 [dcl.type.decltype]]: for an unparenthesised name, its declared
  type; for any other expression, the type plus the value category: lvalue `T&`,
  xvalue `T&&`, prvalue `T`. So `decltype(x)` is `int` but `decltype((x))` is `int&`.
- **`decltype(auto)`**: deduce with `decltype` rules. Used to return "exactly what the
  inner call returns" (forwarding wrappers). Parentheses in `return (x);` change the result.
- **CTAD** (C++17) [S8 [over.match.class.deduct]]: `std::vector v{1, 2};` deduces
  `vector<int>` from the constructors (implicit guides) plus user-written **deduction
  guides** `template<class R> Stats(const R&) -> Stats<typename R::value_type>;`.
  A copy-deduction candidate is preferred: `std::vector w{v};` copies `v`, it is not
  `vector<vector<int>>`.

## Complete example

```cpp
// complete example: deduction
#include <list>
#include <type_traits>
#include <vector>

template <class T> constexpr auto by_value(T) { return std::type_identity<T>{}; }
template <class T> constexpr auto by_fwd(T&&) { return std::type_identity<T>{}; }
template <class F> using T_of = typename F::type;

template <class T> struct Stats {
    T mean{};
    template <class R> explicit Stats(const R& r) {
        std::size_t n = 0;
        for (const auto& v : r) { mean += v; ++n; }
        if (n) mean /= static_cast<T>(n);
    }
};
template <class R> Stats(const R&) -> Stats<typename R::value_type>;   // without it: no CTAD

int main() {
    const int ci = 1;
    int x = 0;
    static_assert(std::is_same_v<T_of<decltype(by_value(ci))>, int>);          // const dropped
    static_assert(std::is_same_v<T_of<decltype(by_fwd(ci))>, const int&>);     // lvalue: T is a reference
    static_assert(std::is_same_v<T_of<decltype(by_fwd(1))>, int>);             // rvalue: T is plain
    static_assert(std::is_same_v<decltype(x), int> && std::is_same_v<decltype((x)), int&>);
    auto il = {1, 2};
    static_assert(std::is_same_v<decltype(il), std::initializer_list<int>>);
    std::vector v{1, 2, 3};
    std::vector w{v};                                     // copy: vector<int>
    static_assert(std::is_same_v<decltype(w), std::vector<int>>);
    Stats s{std::list<double>{1.0, 2.0, 4.5}};            // Stats<double> via the guide
    return s.mean == 2.5 ? 0 : 1;
}
```

## When deduction fails, and how to see types

- Conflicting deductions: `template<class T> T max(T, T); max(1, 2.0)` has `T = int`
  and `T = double`; **deduction does not consider conversions**. Fix: `max<double>(1, 2.0)`,
  or two parameters with `std::common_type_t`.
- Non-deduced contexts: `typename C::value_type` in a parameter, the left of `::`;
  `std::type_identity_t<T>` is used on purpose to switch deduction off for one parameter.
- Printing a type: provoke an error with an undefined template
  (`template<class> struct TD; TD<decltype(x)> t;` puts the type in the message), or
  paste the code into C++ Insights [S17], which shows every deduced type.

## Pitfalls

- `auto` copies: `for (auto x : vec_of_strings)` copies every string. Use `const auto&`,
  or `auto&&` in generic code.
- `auto x = expr_returning_proxy;`: `std::vector<bool>::operator[]` returns a proxy
  object, so `auto b = vb[0];` is not a `bool` and may dangle when `vb` changes.
- `auto s = "abc";` is `const char*`, not `std::string`; use `"abc"s` or `std::string`.
- `decltype(auto) f() { int x = 0; return (x); }` returns `int&` to a dead local.
- CTAD with one braced element: `std::vector v{v2}` copies, `std::vector v{v2, v2}` nests;
  surprising, but specified. Write the type when intent matters.
- `auto` on a function parameter makes a template (abbreviated function template,
  note 13): it must be in a header.
- Libraries: `__cpp_deduction_guides` is 201703 in Apple clang 21, i.e. the C++20
  extensions (CTAD for aggregates and alias templates) are not advertised [S13].
  Check before relying on them.

## Discussion questions

1. **`template<class T> void f(T&& x)` called with an lvalue `int i`: what is `T`, what is the type of `x`?**
   `T = int&`; `x` has type `int& &&`, which reference collapsing reduces to `int&`.
   With an rvalue, `T = int` and `x` is `int&&`. That is why `std::forward<T>(x)` can
   restore the category (note 05).
2. **Why is `decltype((x))` different from `decltype(x)`?** `decltype` of an
   unparenthesised id-expression reports the declaration; any other expression reports
   type and value category, and `(x)` is an lvalue expression, hence `int&`.
3. **What is `auto a = {1, 2.0};`?** Ill-formed: the `initializer_list` element type
   must deduce consistently (`int` vs `double`). `auto a{1};` is `int` (C++17 rule);
   `auto a = {1};` is `initializer_list<int>`.
4. **Your class template `Stats<T>` has a constructor `template<class R> Stats(const R&)`. Why does `Stats s{vec};` not compile, and what fixes it?**
   `T` does not appear in the constructor's parameter types, so the implicit guide cannot
   deduce it. A deduction guide `Stats(const R&) -> Stats<typename R::value_type>`
   supplies the mapping (this was the core of hand-out ex2.2 [S4]).
5. **When would you not use `auto`?** When the type is the documentation (public
   interfaces, numeric precision: `double` vs `float`), when the initialiser returns a
   proxy (`vector<bool>`, expression templates such as Eigen), or when a conversion is
   intended (`std::string s = "abc";`). Otherwise `auto` avoids silent conversions and
   repetition (Core Guidelines ES.11 in spirit [S10]).

## In the code

- `src/cpp/deduction.cpp`: the full table as `static_assert`s; `by_expr()` assigns through a `decltype(auto)` reference; `Stats` with its guide; `max_deducible` shows deduction ignoring conversions.
- `src/cpp/matrix/include/la/matrix.hpp`: `Matrix m{{1, 2}, {3, 4}}` deduces `Matrix<int>` from a nested braced list through the `initializer_list` constructor.
