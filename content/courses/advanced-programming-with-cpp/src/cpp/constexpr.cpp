// constexpr.cpp -- constexpr, consteval, constinit, if consteval, compile-time tests (note 12).
// The static_asserts ARE the tests: if this file compiles, they passed.
// compile_fail/*.cpp holds the programs that must NOT compile (UB and misuse in
// constant evaluation); `make test` checks that each one is rejected.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <memory>
#include <numeric>
#include <string>
#include <string_view>
#include <vector>
#include "check.hpp"

// constexpr function: CAN run at compile time, runs at runtime when called at runtime
constexpr std::uint64_t factorial(unsigned n) { return n <= 1 ? 1 : n * factorial(n - 1); }
static_assert(factorial(20) == 2432902008176640000ull);

// loops, locals, mutation, even std::vector/std::string: allowed in constexpr since C++20,
// as long as every allocation is freed before the constant evaluation ends
constexpr int sum_of_primes_below(int n) {
    std::vector<bool> composite(static_cast<std::size_t>(n), false);
    int s = 0;
    for (int i = 2; i < n; ++i) {
        if (composite[static_cast<std::size_t>(i)]) continue;
        s += i;
        for (int j = i * i; j < n; j += i) composite[static_cast<std::size_t>(j)] = true;
    }
    return s;
}
static_assert(sum_of_primes_below(100) == 1060);

constexpr std::size_t count_words(std::string_view s) {
    std::string copy{s};                        // transient allocation, freed on return
    return static_cast<std::size_t>(std::ranges::count(copy, ' ')) + 1;
}
// clang with GCC 14's libstdc++ cannot evaluate std::string construction at compile time
#if !(defined(__clang__) && defined(__GLIBCXX__))
static_assert(count_words("a b c d") == 4);
#endif

#if __cpp_lib_constexpr_memory >= 202202L
constexpr int via_unique_ptr() { auto p = std::make_unique<int>(41); return *p + 1; }   // C++23
static_assert(via_unique_ptr() == 42);
#endif

// a lookup table built at compile time by an immediately invoked lambda
constexpr auto binomial_row = [] {
    std::array<std::uint64_t, 11> row{};
    for (unsigned k = 0; k <= 10; ++k) row[k] = factorial(10) / (factorial(k) * factorial(10 - k));
    return row;
}();
static_assert(binomial_row[5] == 252 && std::accumulate(binomial_row.begin(), binomial_row.end(), 0ull) == 1024);

// consteval: an immediate function, every call MUST be a constant expression
consteval double checked_sqrt(double x) {
    if (x < 0) throw "negative argument";       // reaching a throw makes the call non-constant: compile error
    double r = x;                               // Newton iteration, constexpr-friendly
    for (int i = 0; i < 60; ++i) r = 0.5 * (r + x / r);
    return r;
}
constexpr double sqrt2 = checked_sqrt(2.0);
static_assert(sqrt2 * sqrt2 - 2.0 < 1e-15 && sqrt2 * sqrt2 - 2.0 > -1e-15);

// if consteval (C++23): different code at compile time and at runtime
constexpr double my_sqrt(double x) {
    if consteval { return checked_sqrt(x); }    // may call consteval here
    else { return std::sqrt(x); }               // runtime: the libm call
}
static_assert(my_sqrt(16.0) == 4.0);

// constinit: static storage initialised at compile time (no static-init-order fiasco),
// but the variable itself is NOT const
constinit int call_count = 0;
constinit const char* greeting = "hello";

// compile-time unit test of a generic algorithm
template <class It> constexpr bool is_sorted_desc(It b, It e) { return std::is_sorted(b, e, std::greater<>{}); }
static_assert([] { std::array a{5, 3, 1}; return is_sorted_desc(a.begin(), a.end()); }());

// a non-type template parameter must be a constant expression
template <std::uint64_t N> struct Fact { static constexpr std::uint64_t value = factorial(N); };
static_assert(Fact<5>::value == 120);

int main() {
    // the same constexpr function at runtime (argument unknown at compile time)
    volatile unsigned n = 10;
    CHECK(factorial(n) == 3628800);
    CHECK(my_sqrt(static_cast<double>(n) * 10) == 10.0);    // takes the std::sqrt branch
    ++call_count;
    CHECK(call_count == 1 && std::string_view(greeting) == "hello");
    CHECK(sum_of_primes_below(static_cast<int>(n)) == 17);
    return chk::report("constexpr");
}
