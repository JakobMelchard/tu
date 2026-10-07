# 07 Lambdas: captures, generic lambdas, closures, std::function vs templates

A lambda expression is shorthand for "define a class with an `operator()` and create
one object of it". Everything about lambdas follows from that translation. Item 017
[S3]; hand-out ex2.1 (a timing wrapper that must accept any callable) [S4]; F.50-F.53 [S10].

Code: `src/cpp/lambdas.cpp`.

## Definitions [S8 [expr.prim.lambda.capture]]

- **Closure type**: the unique, unnamed class the compiler generates for each lambda
  expression. **Closure object**: the prvalue the expression evaluates to. Two
  identical lambdas have different types.
- `captures specifiers -> ret { body }`. The captures become data members;
  the body becomes `operator() const` (non-`const` with `mutable`).
- **Capture by copy** `[x]`, `[=]`: member initialised when the lambda is *created*
  (snapshot). **By reference** `[&x]`, `[&]`: member is a reference; valid only while
  `x` lives. **Init-capture** `[p = std::move(ptr)]`, `[n = 0]`: arbitrary member with
  initialiser (move-only captures). `[this]` captures the pointer, `[*this]` (C++17) a copy.
  Globals and `static` locals are never captured, they are simply used.
- **Captureless lambdas** convert implicitly to a function pointer (C callbacks).
- **Generic lambda**: `auto` parameter -> `operator()` is a template. **Template lambda**
  (C++20): `[]<class T>(const std::vector<T>& v) {...}`.
- **C++23**: `static` lambdas (`[](int x) static {...}`, no object passed),
  **deducing `this`** (`[](this auto self, int n) {...}`) allows recursion, and the
  `()` may be omitted before `mutable`/`->`.
- **`std::function<R(Args...)>`**: a type-erased owner of *any* copyable callable with
  that signature. Costs: an indirect call, possibly a heap allocation (small-buffer
  optimisation for small closures), and it copies the callable. Cannot hold move-only
  closures (`std::move_only_function`, C++23, is **not in libc++ 21** [S12] [S13]).
- **Template parameter** `template<class F> void run(F&& f)`: the closure type is known,
  the call is inlined, no allocation; but every callable type instantiates a new function.

## Complete example

```cpp
// complete example: lambdas
#include <algorithm>
#include <cstdio>
#include <functional>
#include <memory>
#include <vector>

template <class F> double integrate(F&& f, double a, double b, int n) {   // template: inlined
    double h = (b - a) / n, s = 0.5 * (f(a) + f(b));
    for (int i = 1; i < n; ++i) s += f(a + i * h);
    return s * h;
}
double integrate_erased(const std::function<double(double)>& f, double a, double b, int n) {
    return integrate(f, a, b, n);                                          // indirect call per f(x)
}

int main() {
    int k = 1;
    auto snap = [k] { return k; };                  // copy taken now
    auto live = [&k] { return k; };                 // reads k later
    k = 5;
    std::printf("%d %d\n", snap(), live());         // 1 5

    auto counter = [n = 0]() mutable { return ++n; };
    counter();
    std::printf("%d\n", counter());                 // 2: the closure keeps state

    auto owns = [p = std::make_unique<double>(2.0)](double x) { return *p * x; };
    std::printf("%g\n", owns(3));                   // 6; `owns` is move-only: no std::function

    double omega = 2.0;
    auto f = [omega](double x) { return omega * x * x; };
    std::printf("%.6f %.6f\n", integrate(f, 0, 1, 1000), integrate_erased(f, 0, 1, 1000));

    auto fib = [](this auto self, int n) -> long { return n < 2 ? n : self(n - 1) + self(n - 2); };
    std::vector<int> xs{5, 3, 8, 1};
    std::ranges::sort(xs, [](int a, int b) { return a > b; });
    std::printf("fib(20)=%ld max=%d sizeof(f)=%zu\n", fib(20), xs.front(), sizeof f);   // 6765 8 8
}
```

`sizeof f == sizeof(double)`: the closure is exactly its captures.

## What the compiler generates (roughly)

```cpp
// [omega](double x) { return omega * x * x; }  becomes
class __lambda_17 {
    double omega;                                   // the capture
public:
    explicit __lambda_17(double o) : omega(o) {}
    double operator()(double x) const { return omega * x * x; }
};
```

C++ Insights [S17] shows the real translation for any lambda.

## Pitfalls

- **Dangling reference capture**: `[&]` in a lambda that is returned, stored, or run on
  another thread after the frame is gone. F.53: capture by value for non-local use [S10].
- `[=]` in a member function captured `this` implicitly (deprecated since C++20):
  the lambda then dangles when the object dies. Write `[this]` or `[*this]` explicitly.
- `[=]` does not copy what you think for pointers: the pointer is copied, not the pointee.
- A captured-by-copy variable is `const` inside the body unless `mutable`.
- `std::function` copies its callable (libc++ 21 takes it by value: 2 copies of an
  lvalue closure measured [S13], while C++23 specifies `function(F&&)` [S8]); with
  expensive captures, wrap them in `std::ref` or pass the lambda as a template.
- Every generic or template lambda call with new argument types instantiates new code.
- Recursion without deducing `this` needs `std::function` (slow) or a Y-combinator.

## Discussion questions

1. **What is the type of a lambda, and why can't you name it?** A unique unnamed class
   type created per lambda *expression*. You use `auto`, `decltype`, a template
   parameter, or type-erase it with `std::function`.
2. **When is a captured value evaluated?** Captures by copy are initialised when the
   lambda expression is evaluated (creation time), not when it is called. By-reference
   captures read the variable at call time. (Item 017 calls this evaluation time vs
   execution time [S3].)
3. **`std::function` or a template parameter for a callback?** Template: zero overhead,
   inlinable, works with move-only callables; but it must be in a header and each type
   makes a new instantiation. `std::function`: one signature, storable in containers and
   non-template classes, ABI-stable; costs an indirect call per invocation and possibly
   an allocation. Hot numerical loops: template. Stored event handlers: `std::function`.
4. **How do you capture a `std::unique_ptr` into a lambda, and what follows?** Init
   capture `[p = std::move(ptr)]`. The closure becomes move-only, so it cannot be
   stored in `std::function`; use a template, `std::move_only_function` (C++23, not in
   libc++ 21), or a `shared_ptr`.
5. **What changes when a lambda is `mutable`?** `operator()` is no longer `const`, so
   by-copy members can be modified and keep their state between calls (`counter()`
   above). The closure object then cannot be called through a `const` reference.

## In the code

- `src/cpp/lambdas.cpp`: snapshot vs reference, closure size, function-pointer conversion, `mutable` counter, move-only init-capture (`!is_copy_constructible`), `this` vs `*this`, generic and template lambdas, sort/count_if predicates, immediately invoked lambda for `const` init, recursion via deducing `this`, `static` lambda, `std::function` copy count and equal integration results.
- `src/cpp/concepts.cpp` `call_counted`: forwarding any callable with any arguments (the ex2.1 pattern).
