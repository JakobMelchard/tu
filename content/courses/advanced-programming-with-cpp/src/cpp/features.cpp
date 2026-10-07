// features.cpp -- which C++23 features does THIS toolchain support? (notes README, CHANGELOG)
// Language features are detected with __cpp_* macros (reliable in clang); library
// features with the HAVE_* flags that probe.sh derives by compiling, linking and running
// probes/*.cpp, because libc++ omits some __cpp_lib_* macros for features it ships.
#include <cstdio>
#include <version>
#include "check.hpp"
#if defined(HAVE_PRINT)
#include <print>
#endif
#if defined(HAVE_EXPECTED)
#include <expected>
#endif
#if defined(HAVE_MDSPAN)
#include <mdspan>
#endif
#if defined(HAVE_FLAT_MAP)
#include <flat_map>
#endif
#include <bit>
#include <cstdint>
#include <format>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

void row(const char* feature, const char* paper, bool ok, const char* how) {
    std::printf("  %-34s %-7s %-4s %s\n", feature, paper, ok ? "yes" : "no", how);
}
#define LIB(flag, name, paper) row(name, paper, flag, flag ? "probe compiled+ran" : "probe failed: SKIP in examples")
#if defined(HAVE_PRINT)
#define H_PRINT true
#else
#define H_PRINT false
#endif
#if defined(HAVE_EXPECTED)
#define H_EXPECTED true
#else
#define H_EXPECTED false
#endif
#if defined(HAVE_MDSPAN)
#define H_MDSPAN true
#else
#define H_MDSPAN false
#endif
#if defined(HAVE_RANGES_TO)
#define H_RANGES_TO true
#else
#define H_RANGES_TO false
#endif
#if defined(HAVE_GENERATOR)
#define H_GENERATOR true
#else
#define H_GENERATOR false
#endif
#if defined(HAVE_FLAT_MAP)
#define H_FLAT_MAP true
#else
#define H_FLAT_MAP false
#endif

#if __cpp_explicit_this_parameter >= 202110L
struct ThisDemo { int v = 3; auto&& get(this auto&& self) { return self.v; } };   // templates not allowed in local classes
#endif

#if defined(HAVE_EXPECTED)
std::expected<double, std::string> parse_positive(double x) {
    if (x <= 0) return std::unexpected("not positive");
    return x;
}
#endif

int main() {
    std::printf("__cplusplus = %ld, _LIBCPP_VERSION = %d\n", static_cast<long>(__cplusplus), _LIBCPP_VERSION);
    std::puts("  language:");
    row("deducing this", "P0847", __cpp_explicit_this_parameter >= 202110L, "__cpp_explicit_this_parameter");
    row("if consteval", "P1938", __cpp_if_consteval >= 202106L, "__cpp_if_consteval");
    row("multidimensional operator[]", "P2128", __cpp_multidimensional_subscript >= 202110L, "__cpp_multidimensional_subscript");
    row("static operator()", "P1169", __cpp_static_call_operator >= 202207L, "__cpp_static_call_operator");
    row("auto(x) decay-copy", "P0849", __cpp_auto_cast >= 202110L, "__cpp_auto_cast");
    row("range-for temporaries live", "P2718", __cpp_range_based_for >= 202211L, "__cpp_range_based_for");
#if defined(__cpp_modules)
    row("named modules (__cpp_modules)", "P1103", true, "__cpp_modules");
#else
    row("named modules (__cpp_modules)", "P1103", false, "macro undefined; -fcxx-modules works, see modules/");
#endif
    std::puts("  library:");
    LIB(H_PRINT, "std::print / println", "P2093");
    LIB(H_EXPECTED, "std::expected", "P0323");
    LIB(H_MDSPAN, "std::mdspan", "P0009");
    LIB(H_RANGES_TO, "std::ranges::to", "P1206");
    LIB(H_FLAT_MAP, "std::flat_map", "P0429");
    LIB(H_GENERATOR, "std::generator", "P2502");
    std::puts("  (the full probe table incl. zip, fold, chunk, stride, execution: bin/features.txt)");

    // every "yes" above is exercised, not just detected
#if __cpp_explicit_this_parameter >= 202110L
    ThisDemo s;
    const ThisDemo cs;
    CHECK(s.get() == 3 && cs.get() == 3);
    static_assert(std::is_same_v<decltype(cs.get()), const int&>);   // const-ness deduced
#endif
    constexpr auto where = [] { if consteval { return 1; } else { return 2; } };
    static_assert(where() == 1);
    struct Grid { int d[4]{}; int& operator[](int i, int j) { return d[2 * i + j]; } } g;
    g[1, 1] = 9;
    CHECK(g.d[3] == 9);
    std::vector v{1, 2};
    auto copy = auto(v);                               // a prvalue copy, no named temporary
    copy[0] = 7;
    CHECK(v[0] == 1);
    CHECK(std::byteswap(std::uint32_t{0x11223344}) == 0x44332211u);
    auto sign = [](int x) { if (x > 0) return 1; if (x < 0) return -1; if (x == 0) return 0; std::unreachable(); };
    CHECK(sign(-3) == -1);
    CHECK(std::format("{}", std::vector{1, 2, 3}) == "[1, 2, 3]");   // formatting ranges (P2286)
#if defined(HAVE_PRINT)
    std::println("  std::println works: {:.3f}", 3.14159);
#endif
#if defined(HAVE_EXPECTED)
    auto ok = parse_positive(2.0).transform([](double x) { return x * x; });
    auto bad = parse_positive(-1.0).transform([](double x) { return x * x; });
    CHECK(ok && *ok == 4.0 && !bad && bad.error() == "not positive");
    CHECK(parse_positive(-1.0).value_or(0.0) == 0.0);
#endif
#if defined(HAVE_MDSPAN)
    std::vector<double> buf(6);
    std::mdspan m(buf.data(), 2, 3);                    // row-major (layout_right) view
    m[1, 2] = 5.0;
    CHECK(buf[5] == 5.0 && m.extent(0) == 2 && m.extent(1) == 3);
#endif
#if defined(HAVE_FLAT_MAP)
    std::flat_map<int, char> fm{{3, 'c'}, {1, 'a'}};
    CHECK(fm.begin()->second == 'a' && fm.keys().size() == 2);
#endif
    return chk::report("features");
}
