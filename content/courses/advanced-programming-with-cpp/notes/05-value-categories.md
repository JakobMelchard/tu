# 05 Value categories: lvalue, xvalue, prvalue, move semantics, forwarding, copy elision

Every expression has a type **and** a value category. The category decides which
overload binds (`const T&` vs `T&&`), whether a move is possible, and whether a
temporary exists at all. This is the topic of the first 2021W hand-out block (ex1.1:
initialise a member from a by-value, lvalue-ref or rvalue-ref parameter as cheaply as
possible, and explain the benchmark) [S4]. Items 006 and 008 [S3]; Meyers Items 23-30 [S16].

Code: `src/cpp/value_categories.cpp` (counts copies and moves; 30 checks).

## Definitions [S8 [basic.lval]]

```
            expression
           /          \
      glvalue        rvalue
      /     \        /     \
  lvalue    xvalue       prvalue
```

- **glvalue** ("generalised lvalue"): an expression whose evaluation determines the
  identity of an object. **prvalue** ("pure rvalue"): computes a value or initialises
  an object; has no identity until it is *materialised*.
- **lvalue** = glvalue that is not an xvalue: names (`x`, even of type `T&&`!),
  `*p`, `a[i]`, `++i`, string literals, function calls returning `T&`.
- **xvalue** ("expiring"): `std::move(x)`, `static_cast<T&&>(x)`, a call returning
  `T&&`, a member of an rvalue (`make().m`). Identity, but resources may be stolen.
- **prvalue**: literals (except strings), `x + 1`, `i++`, `T{}`, a call returning `T`
  by value, lambdas.
- Test: `decltype((e))` is `T&` for lvalues, `T&&` for xvalues, `T` for prvalues.
- **Binding**: `T&` binds lvalues; `const T&` binds everything; `T&&` binds rvalues
  (xvalues and prvalues). Overload resolution prefers `T&&` for rvalues.
- **Move semantics**: a move constructor `T(T&&) noexcept` steals the source's
  resources and leaves it *valid but unspecified* (for the library types: usually empty).
  `std::move` moves nothing: it is a cast to `T&&` (an xvalue).
- **Forwarding reference**: `T&&` where `T` is a *deduced* template parameter (or
  `auto&&`). With reference collapsing (`& &&` -> `&`, `&& &&` -> `&&`) it binds
  anything; `std::forward<T>(x)` recreates the argument's original category.
- **Copy elision** [S8 [class.copy.elision]]: since C++17 a prvalue initialising an
  object of the same type **is** that object: `T x = T{};`, `return T{};`,
  `f(T{})` for a by-value parameter: no copy, no move, not even required to exist.
  **NRVO** (`T x; ...; return x;`) is permitted, not guaranteed; if it does not happen,
  `return x;` of a local is an implicit move (C++23 extended the implicit move rules, P2266).

## Measured on this Mac (`value_categories.cpp`, Apple clang 21, -O2 and -O0 identical) [S13]

| expression | copies | moves |
|---|---|---|
| `Counted b = a;` | 1 | 0 |
| `Counted b = std::move(a);` | 0 | 1 |
| `Counted c = std::move(const_obj);` | **1** | 0 |
| `Counted d = make_prvalue();` | 0 | 0 |
| `Counted e = make_named();` (NRVO) | 0 | <= 1 |
| sink `by_cref(obj)` / `by_cref(Counted{})` | 1 / **1** | 0 / 0 |
| sink `by_value(obj)` / `by_value(Counted{})` | 1 / 0 | 1 / 1 |
| sink `by_rref(Counted{})` | 0 | 1 |
| `v.push_back(local)` / `push_back(std::move(local))` / `emplace_back()` | 1 / 0 / 0 | 0 / 1 / 0 |
| reallocation of 4 elements, `noexcept` move | 0 | 4 |
| reallocation of 4 elements, move **not** `noexcept` | **4** | 0 |

The last two rows are `std::move_if_noexcept`: `vector` keeps the strong exception
guarantee on reallocation, so it only moves if the move cannot throw.

## Complete example

```cpp
// complete example: value_categories
#include <cstdio>
#include <utility>
#include <vector>

int copies = 0, moves = 0;
struct Big {
    std::vector<double> data = std::vector<double>(1000);
    Big() = default;
    Big(const Big& o) : data(o.data) { ++copies; }
    Big(Big&& o) noexcept : data(std::move(o.data)) { ++moves; }
};
struct Widget { Big b; };

Widget init_value(Big b) { return Widget{std::move(b)}; }   // the ex1.1 question, our version
Widget init_rref(Big&& b) { return Widget{std::move(b)}; }  // b is an lvalue inside: move it
Widget init_lref(const Big& b) { return Widget{b}; }        // must copy: caller keeps b

template <class... Args> Widget make_widget(Args&&... args) {
    return Widget{Big(std::forward<Args>(args)...)};        // prvalue straight into the member
}

void report(const char* what) { std::printf("%-28s copies=%d moves=%d\n", what, copies, moves); copies = moves = 0; }

int main() {
    Big big;
    init_value(big);            report("init_value(lvalue)");      // 1 copy, 1 move
    init_value(Big{});          report("init_value(prvalue)");     // 0 copies, 1 move
    init_rref(std::move(big));  report("init_rref(xvalue)");       // 0 copies, 1 move
    init_lref(big);             report("init_lref(lvalue)");       // 1 copy
    Big c = std::move(std::as_const(big));  report("move of a const");  // 1 copy!
    make_widget();              report("make_widget()");           // 0, 0
    (void)c;
}
```

## Pitfalls

- `std::move` on a `const` object silently copies (`const T&&` binds to `const T&`).
- A named rvalue reference is an lvalue: inside `f(T&& x)`, `g(x)` copies; write
  `g(std::move(x))`.
- `return std::move(local);` **prevents** NRVO and is at best useless (clang warns
  `-Wpessimizing-move`). `return a += b;` returns a reference, so the result is copied,
  not moved (a real bug found while writing `matrix.hpp`, see note 13).
- Forgetting `noexcept` on the move constructor: `std::vector` copies on every
  reallocation (row "not noexcept" above). C.66 [S10].
- Use after move: allowed only to assign or destroy (or what the type documents,
  e.g. `std::vector` is empty after move in practice, but that is not a guarantee for
  all types).
- `std::forward` without a forwarding reference, or forwarding the same argument
  twice (the second use sees a moved-from object).
- Declaring a destructor (even `= default` in the class body counts as user-declared)
  suppresses the implicit move operations: "moves" become copies (note 09).

## Discussion questions

1. **Classify `x`, `std::move(x)`, `x + 1`, `"abc"`, `f()` (returns `T&`), `g()` (returns `T`).**
   lvalue, xvalue, prvalue, lvalue (string literals are arrays with identity), lvalue,
   prvalue. Check with `decltype((e))`.
2. **`void f(Widget&& w) { Widget local = w; }` - copy or move?** Copy: `w` is a named
   variable, hence an lvalue, even though its type is `Widget&&`. `std::move(w)` makes
   it a move.
3. **Explain the four numbers of an init-by-value benchmark: lvalue arg vs rvalue arg, with and without `std::move` inside.**
   Without the inner `std::move`: lvalue arg = 2 copies, rvalue arg = 1 copy (parameter
   elided or moved, then copied into the member). With it: lvalue = 1 copy + 1 move,
   rvalue = 0 copies + 1 move. For a 1000-element vector a copy is an allocation +
   memcpy, a move is three pointer swaps: that is the order-of-magnitude difference the
   2021W solution reports [S3] (item 007).
4. **What does `std::forward<T>(x)` do, and why is it needed?** It is
   `static_cast<T&&>(x)`: with `T = U&` (lvalue argument) it yields `U&`, with `T = U`
   it yields `U&&`. Without it every forwarded argument would be an lvalue (it has a
   name) and would be copied.
5. **Is copy elision an optimisation?** For prvalues since C++17, no: it is the
   semantics (the prvalue initialises the target directly, so a non-movable type can
   be returned by value). NRVO for named locals remains an optional optimisation;
   when skipped, the return is an implicit move.

## In the code

- `src/cpp/value_categories.cpp`: `CATEGORY(e)` macro via `decltype((e))`; the whole table above as checks; `make_box` shows the prvalue-into-member rule; `CountedMayThrow` shows `move_if_noexcept`.
- `src/cpp/matrix/include/la/matrix.hpp`: `operator+(Matrix a, const Matrix& b)` takes the left operand by value so `std::move(a) + b` reuses storage (checked in `test_matrix.cpp`).
