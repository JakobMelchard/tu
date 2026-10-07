// concepts.cpp -- SFINAE vs requires, concept design, subsumption, variadic
// templates and fold expressions (note 13).
#include <complex>
#include <concepts>
#include <cstddef>
#include <list>
#include <string>
#include <tuple>
#include <type_traits>
#include <vector>
#include "check.hpp"

// --- the C++11/17 way: SFINAE with enable_if (the constraint hides in a default argument)
template <class T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
constexpr const char* kind_sfinae(T) { return "integral"; }
template <class T, std::enable_if_t<std::is_floating_point_v<T>, int> = 0>
constexpr const char* kind_sfinae(T) { return "floating"; }

// --- the C++20 way: requires clauses and named concepts
template <class T> requires std::integral<T> constexpr const char* kind(T) { return "integral"; }
constexpr const char* kind(std::floating_point auto) { return "floating"; }   // abbreviated template

// subsumption: signed_integral = integral && is_signed, so it is MORE constrained and wins
constexpr int pick(std::integral auto) { return 1; }
constexpr int pick(std::signed_integral auto) { return 2; }
static_assert(pick(1u) == 1 && pick(1) == 2);
// subsumption only works through concepts: the same test spelled as two raw traits is ambiguous
template <class T> requires std::is_integral_v<T> constexpr int raw(T) { return 1; }
template <class T> requires(std::is_integral_v<T> && std::is_signed_v<T>) constexpr int raw(T) { return 2; }
template <class T> concept raw_callable = requires(T t) { raw(t); };
static_assert(raw_callable<unsigned> && !raw_callable<int>);   // int: ambiguous

// --- designing a concept: what a numerical "scalar" must support
template <class T> concept Scalar = std::regular<T> && requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
    { a - b } -> std::convertible_to<T>;
    { a * b } -> std::convertible_to<T>;
    { a / b } -> std::convertible_to<T>;
    { -a } -> std::convertible_to<T>;
    T{0};
    T{1};
};
static_assert(Scalar<int> && Scalar<double> && Scalar<std::complex<double>>);
static_assert(!Scalar<std::string>);            // has +, lacks * and /
static_assert(!Scalar<int*>);                   // pointer arithmetic is not a field

// a requires expression checks members and nested types
template <class C> concept SizedContainer = requires(const C& c) {
    typename C::value_type;
    { c.size() } -> std::convertible_to<std::size_t>;
    c.begin();
    c.end();
};
static_assert(SizedContainer<std::vector<int>> && SizedContainer<std::list<double>> && !SizedContainer<int[3]>);

template <SizedContainer C> requires Scalar<typename C::value_type>
constexpr auto mean(const C& c) {
    typename C::value_type s{0};
    for (const auto& x : c) s = s + x;
    return s / static_cast<typename C::value_type>(c.size());
}

// --- variadic templates and folds [temp.variadic], [expr.prim.fold]
template <class... Ts> constexpr auto sum(Ts... xs) { return (xs + ... + 0); }       // binary right fold
template <class... Ts> constexpr bool all_positive(Ts... xs) { return ((xs > 0) && ...); }  // empty pack -> true
template <class... Ts> constexpr std::size_t count_args(Ts...) { return sizeof...(Ts); }
template <class T, class... Ts> constexpr bool all_same = (std::is_same_v<T, Ts> && ...);
static_assert(sum(1, 2, 3) == 6 && sum() == 0);
static_assert(all_positive(1, 2.5, 3L) && all_positive() && !all_positive(1, -1));
static_assert(count_args(1, "a", 2.0) == 3);
static_assert(all_same<int, int, int> && !all_same<int, int, long>);

// fold over the comma operator: do something for each argument, in order
template <class... Ts> std::string join(const Ts&... xs) {
    std::string out;
    ((out += std::to_string(xs), out += ','), ...);
    if (!out.empty()) out.pop_back();
    return out;
}

// pack expansion in a function call with perfect forwarding: the EX2.1-style timing wrapper
template <class F, class... Args> decltype(auto) call_counted(int& counter, F&& f, Args&&... args) {
    ++counter;
    return std::forward<F>(f)(std::forward<Args>(args)...);
}

// recursion on a pack (pre-C++17 style) vs a fold, same result
constexpr int max_of(int x) { return x; }
template <class... Ts> constexpr int max_of(int x, Ts... rest) { int m = max_of(rest...); return x > m ? x : m; }
static_assert(max_of(3, 9, 2) == 9);

// tuples: apply unpacks a tuple into a pack
constexpr double dot3(double a, double b, double c) { return a * 1 + b * 2 + c * 3; }
static_assert(std::apply(dot3, std::tuple{1.0, 1.0, 1.0}) == 6.0);

int main() {
    CHECK(std::string(kind_sfinae(1)) == "integral" && std::string(kind_sfinae(1.0)) == "floating");
    CHECK(std::string(kind(1)) == "integral" && std::string(kind(1.0f)) == "floating");
    CHECK(mean(std::vector{1.0, 2.0, 6.0}) == 3.0);
    CHECK(mean(std::list{2, 4}) == 3);
    CHECK((mean(std::vector<std::complex<double>>{{1, 1}, {1, -1}}) == std::complex<double>{1, 0}));
    CHECK(join(1, 2, 3) == "1,2,3" && join().empty());
    int calls = 0;
    std::string s = "ab";
    CHECK(call_counted(calls, [](std::string& x, int n) { x += std::to_string(n); return x.size(); }, s, 7) == 3);
    CHECK(s == "ab7" && calls == 1);
    return chk::report("concepts");
}
