// conversions.cpp -- promotions, usual arithmetic conversions, narrowing,
// user-defined conversions and how they rank in overload resolution (note 06).
#include <bit>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>
#include "check.hpp"

// --- integral promotion: arithmetic on small types happens in int [conv.prom]
unsigned char uc = 200;
static_assert(std::is_same_v<decltype(uc + uc), int>);
static_assert(std::is_same_v<decltype('a' + 1), int>);
static_assert(std::is_same_v<decltype(1u + 1L), long>);        // long can hold all unsigned (LP64)
static_assert(std::is_same_v<decltype(1u + 1), unsigned>);     // int -> unsigned: the classic trap
static_assert(std::is_same_v<decltype(1.0f + 1), float>);

// --- narrowing: forbidden inside braces [dcl.init.list]; detect it with a concept
template <class To, class From> concept brace_convertible = requires(From f) { To{f}; };
static_assert(brace_convertible<long, int>);          // widening: fine
static_assert(brace_convertible<double, float>);
static_assert(!brace_convertible<int, double>);       // float -> int: narrowing
static_assert(!brace_convertible<float, double>);     // double -> float: narrowing
static_assert(!brace_convertible<double, long>);      // long -> double: narrowing (not all longs representable)
static_assert(!brace_convertible<unsigned, int>);     // sign change: narrowing
constexpr int small = 3;
constexpr double ok{small};                            // constant whose value fits: NOT narrowing
static_assert(ok == 3.0);

// --- overload ranking [over.ics.rank]: exact > promotion > conversion > user-defined
constexpr int f(int) { return 1; }
constexpr int f(double) { return 2; }
static_assert(f('a') == 1);     // char -> int is a promotion
static_assert(f(2.0f) == 2);    // float -> double is a promotion
template <class T> concept f_callable = requires(T t) { f(t); };
static_assert(!f_callable<long>);          // long -> int and long -> double: both conversions, ambiguous
static_assert(!f_callable<unsigned>);      // same

// --- user-defined conversions [class.conv]
struct Meters {
    double v;
    explicit Meters(double x) : v(x) {}            // explicit: no silent double -> Meters
    explicit operator double() const { return v; } // explicit: no silent Meters -> double
};
struct Celsius {
    double v;
    Celsius(double x) : v(x) {}                    // converting constructor (implicit)
};
double warm(Celsius c) { return c.v + 1; }
struct Wrapper { Celsius c; Wrapper(Celsius x) : c(x) {} };
double unwrap(Wrapper w) { return w.c.v; }
template <class T> concept unwrap_callable = requires(T t) { unwrap(t); };
static_assert(!std::is_convertible_v<double, Meters>);
static_assert(std::is_constructible_v<Meters, double>);
static_assert(std::is_convertible_v<double, Celsius>);
static_assert(unwrap_callable<Celsius> && !unwrap_callable<double>);  // at most ONE user-defined conversion

struct Handle {                                    // explicit operator bool: contextual only
    int fd = -1;
    explicit operator bool() const { return fd >= 0; }
};
static_assert(!std::is_convertible_v<Handle, bool>);

enum class Spin : std::int8_t { down = -1, up = 1 };
static_assert(!std::is_convertible_v<Spin, int>);  // scoped enum: no implicit conversion

int main() {
    // signed/unsigned comparison: -1 is converted to UINT_MAX
    CHECK(!(-1 < 0u));
    CHECK(std::cmp_less(-1, 0u));                  // C++20: value-correct comparison
    std::vector<int> v{1, 2, 3};
    CHECK(std::ssize(v) - 4 < 0);                   // signed size: no wrap-around
    CHECK(v.size() - 4 > v.size());                 // unsigned: wraps to a huge number

    // floating -> integer truncates toward zero; out of range is UB, so check first
    CHECK(static_cast<int>(-2.7) == -2 && std::lround(-2.7) == -3);
    CHECK(std::in_range<std::int8_t>(127) && !std::in_range<std::int8_t>(128));
    // integer -> floating loses precision above 2^53
    long long big = (1LL << 53) + 1;
    CHECK(static_cast<long long>(static_cast<double>(big)) == big - 1);

    Meters m{3.0};
    CHECK(static_cast<double>(m) == 3.0);
    CHECK(warm(20.0) == 21.0);                      // double -> Celsius implicitly
    Handle h{3};
    CHECK(h && !Handle{});                          // contextual conversion to bool is allowed

    CHECK(std::to_underlying(Spin::down) == -1);   // C++23
    CHECK(static_cast<int>(Spin::up) == 1);

    // bit_cast vs static_cast: bits vs value
    CHECK(static_cast<std::uint32_t>(1.0f) == 1u);
    CHECK(std::bit_cast<std::uint32_t>(1.0f) == 0x3f800000u);
    return chk::report("conversions");
}
