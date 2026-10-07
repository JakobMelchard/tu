// lambdas.cpp -- captures, closures, generic lambdas, std::function vs templates (note 07).
#include <algorithm>
#include <functional>
#include <memory>
#include <numeric>
#include <string>
#include <type_traits>
#include <vector>
#include "check.hpp"

int copies = 0;
struct Probe {
    int v = 1;
    Probe() = default;
    Probe(const Probe& o) : v(o.v) { ++copies; }
};

// template parameter: the closure type is known, the call can be inlined
template <class F> double integrate(F&& f, double a, double b, int n) {
    double h = (b - a) / n, s = 0.5 * (f(a) + f(b));
    for (int i = 1; i < n; ++i) s += f(a + i * h);
    return s * h;
}
// std::function: type-erased, one indirect call per evaluation, may allocate
double integrate_erased(const std::function<double(double)>& f, double a, double b, int n) {
    return integrate(f, a, b, n);
}

struct Counter {
    int n = 0;
    auto incrementer() { return [this] { return ++n; }; }       // captures the pointer
    auto snapshot() const { return [*this] { return n; }; }     // C++17: captures a copy
};

int main() {
    // capture by value is a snapshot taken when the lambda is created
    int k = 1;
    auto by_val = [k] { return k; };
    auto by_ref = [&k] { return k; };
    k = 5;
    CHECK(by_val() == 1 && by_ref() == 5);

    // the closure is an object: its size is the size of its captures
    auto empty = [] {};
    auto two = [a = 1, b = 2] { return a + b; };
    static_assert(sizeof(empty) == 1 && sizeof(two) == 2 * sizeof(int));
    CHECK(two() == 3);

    // captureless lambdas convert to function pointers (C callbacks, qsort)
    int (*fp)(int) = [](int x) { return 2 * x; };
    CHECK(fp(4) == 8);

    // mutable: operator() is const by default, mutable lets it modify its own copies
    auto counter = [n = 0]() mutable { return ++n; };
    counter();
    CHECK(counter() == 2);

    // init-capture moves a move-only object into the closure
    auto up = std::make_unique<int>(42);
    auto owns = [p = std::move(up)] { return *p; };
    CHECK(owns() == 42 && up == nullptr);
    static_assert(!std::is_copy_constructible_v<decltype(owns)>);  // hence not storable in std::function

    // this vs *this
    Counter c;
    auto inc = c.incrementer();
    auto snap = c.snapshot();
    inc();
    CHECK(c.n == 1 && snap() == 0);

    // generic lambda (auto parameter) and explicit template lambda (C++20)
    auto add = [](auto a, auto b) { return a + b; };
    CHECK(add(1, 2) == 3 && add(std::string("a"), "b") == "ab");
    auto front_or = []<class T>(const std::vector<T>& v, T fallback) { return v.empty() ? fallback : v.front(); };
    CHECK(front_or(std::vector<int>{}, 7) == 7);

    // lambdas as predicates, comparators and projections
    std::vector<int> xs{5, 3, 8, 1};
    std::ranges::sort(xs, std::greater{});
    CHECK(xs.front() == 8);
    int threshold = 4;
    CHECK(std::ranges::count_if(xs, [threshold](int x) { return x > threshold; }) == 2);

    // immediately invoked lambda: complex initialisation of a const variable
    const auto table = [] { std::vector<int> t(5); std::iota(t.begin(), t.end(), 0); return t; }();
    CHECK(table[4] == 4);

    // recursion: a lambda cannot name itself ... unless it deduces `this` (C++23)
#if defined(HAVE_DEDUCING_THIS)
    auto fib = [](this auto self, int n) -> long { return n < 2 ? n : self(n - 1) + self(n - 2); };
    CHECK(fib(20) == 6765);
#else
    chk::skip("recursive lambda via deducing this", "P0847 not supported by this compiler");
#endif

    // static operator() (C++23): no closure object is passed at all
    auto sq = [](double x) static { return x * x; };
    CHECK(sq(3.0) == 9.0);

    // template vs std::function: same result; std::function copies its target
    Probe pr;
    auto f = [pr](double x) { return pr.v * x * x; };
    copies = 0;
    std::function<double(double)> erased = f;          // copies the closure (and its Probe)
    CHECK(copies >= 1);   // libc++ 21 takes F by value: 2 copies here (Probe has no move ctor)
    double i1 = integrate(f, 0, 1, 1000), i2 = integrate_erased(erased, 0, 1, 1000);
    CHECK(i1 == i2 && std::abs(i1 - 1.0 / 3) < 1e-6);

#if defined(__cpp_lib_move_only_function)
    std::move_only_function<int()> mof = std::move(owns);
    CHECK(mof() == 42);
#else
    chk::skip("std::move_only_function", "P0288 not in this libc++ (use a template parameter instead)");
#endif
    return chk::report("lambdas");
}
