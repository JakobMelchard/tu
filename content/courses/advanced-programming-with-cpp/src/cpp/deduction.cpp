// deduction.cpp -- auto, decltype, template argument deduction, CTAD (note 02).
// Almost everything is a static_assert: deduction happens at compile time, so if
// this file compiles, the claims hold. The runtime CHECKs cover the rest.
#include <array>
#include <initializer_list>
#include <list>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>
#include "check.hpp"

using std::is_same_v;

// --- auto: same rules as template deduction by value, T in `template<class T> f(T)`
const int ci = 1;
const int& cr = ci;
int arr[3] = {1, 2, 3};
auto a1 = ci;      // int        (top-level const dropped)
auto a2 = cr;      // int        (reference dropped, then const)
auto& a3 = cr;     // const int& (const kept: it is not top-level for the referee)
auto a4 = arr;     // int*       (array-to-pointer decay)
auto& a5 = arr;    // int(&)[3]  (no decay through a reference)
auto a6 = {1, 2};  // std::initializer_list<int>  (the one rule auto does NOT share with templates)
auto a7{1};        // int        (direct-list-init with one element, since C++17)
static_assert(is_same_v<decltype(a1), int>);
static_assert(is_same_v<decltype(a2), int>);
static_assert(is_same_v<decltype(a3), const int&>);
static_assert(is_same_v<decltype(a4), int*>);
static_assert(is_same_v<decltype(a5), int (&)[3]>);
static_assert(is_same_v<decltype(a6), std::initializer_list<int>>);
static_assert(is_same_v<decltype(a7), int>);

// --- decltype: of a name = declared type; of an expression = type + value category
int x = 0;
static_assert(is_same_v<decltype(x), int>);          // unparenthesised id-expression
static_assert(is_same_v<decltype((x)), int&>);       // lvalue expression -> T&
static_assert(is_same_v<decltype(std::move(x)), int&&>);  // xvalue -> T&&
static_assert(is_same_v<decltype(x + 1), int>);      // prvalue -> T

// decltype(auto) returns exactly decltype(return-expression): parentheses matter
decltype(auto) by_name() { return x; }        // int
decltype(auto) by_expr() { return (x); }      // int&  -- a reference to the global
static_assert(is_same_v<decltype(by_name()), int>);
static_assert(is_same_v<decltype(by_expr()), int&>);

// --- function template deduction [temp.deduct.call]
template <class T> constexpr auto by_value(T) { return std::type_identity<T>{}; }
template <class T> constexpr auto by_lref(T&) { return std::type_identity<T>{}; }
template <class T> constexpr auto by_fwd(T&&) { return std::type_identity<T>{}; }
template <class T> using got = typename T::type;

static_assert(is_same_v<got<decltype(by_value(ci))>, int>);         // const dropped
static_assert(is_same_v<got<decltype(by_value(arr))>, int*>);       // decays
static_assert(is_same_v<got<decltype(by_value("hi"))>, const char*>);
static_assert(is_same_v<got<decltype(by_lref(ci))>, const int>);    // const is part of T
static_assert(is_same_v<got<decltype(by_lref(arr))>, int[3]>);      // array kept, size deduced
static_assert(is_same_v<got<decltype(by_fwd(x))>, int&>);           // lvalue -> T = int&
static_assert(is_same_v<got<decltype(by_fwd(ci))>, const int&>);
static_assert(is_same_v<got<decltype(by_fwd(42))>, int>);           // rvalue -> T = int

// size of a C array deduced as a non-type template parameter
template <class T, std::size_t N> constexpr std::size_t length(const T (&)[N]) { return N; }
static_assert(length(arr) == 3);

// deduction does not consider conversions: max(1, 2.0) fails, so ask for it explicitly
template <class T> constexpr T my_max(T a, T b) { return a < b ? b : a; }
template <class A> concept max_deducible = requires(A a) { my_max(a, 2.0); };
static_assert(max_deducible<double> && !max_deducible<int>);
static_assert(my_max<double>(1, 2.5) == 2.5);

// --- CTAD [over.match.class.deduct]
template <class T> struct Stats {
    T mean{};
    std::size_t n = 0;
    template <class Range> explicit Stats(const Range& r) {
        for (const auto& v : r) { mean += v; ++n; }
        if (n) mean /= static_cast<T>(n);
    }
};
// deduction guide: T is the range's value_type (a constructor template parameter
// that is not a class template parameter cannot be deduced without one)
template <class Range> Stats(const Range&) -> Stats<typename Range::value_type>;

int main() {
    std::vector v{1, 2, 3};                    // vector<int>
    std::pair p{1, 2.5};                       // pair<int, double>
    std::array a{1.0, 2.0, 3.0};               // array<double, 3>
    std::vector w{v};                          // vector<int>: copy deduction wins, NOT vector<vector<int>>
    std::vector ww{v, v};                      // vector<vector<int>>
    static_assert(is_same_v<decltype(v), std::vector<int>>);
    static_assert(is_same_v<decltype(p), std::pair<int, double>>);
    static_assert(is_same_v<decltype(a), std::array<double, 3>>);
    static_assert(is_same_v<decltype(w), std::vector<int>>);
    static_assert(is_same_v<decltype(ww), std::vector<std::vector<int>>>);

    Stats s{std::list<double>{1.0, 2.0, 4.5}};
    static_assert(is_same_v<decltype(s), Stats<double>>);
    CHECK(s.n == 3 && s.mean == 2.5);
    Stats si{v};                               // Stats<int>: integer mean truncates (2)
    CHECK(si.mean == 2);

    // using std::string_literals changes what auto sees
    using namespace std::string_literals;
    auto s1 = "abc";
    auto s2 = "abc"s;
    static_assert(is_same_v<decltype(s1), const char*>);
    static_assert(is_same_v<decltype(s2), std::string>);

    CHECK(by_expr() == 0);
    by_expr() = 5;                             // assigns through the returned int&
    CHECK(x == 5);
    return chk::report("deduction");
}
