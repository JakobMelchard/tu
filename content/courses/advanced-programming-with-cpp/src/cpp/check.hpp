// check.hpp -- the tiny self-check helper every program here uses.
// CHECK(expr) records pass/fail with file:line and keeps going; SKIP() says
// loudly that a feature is missing instead of failing the build;
// chk::report() prints a summary and is the exit code of main.
// The counters are C++17 inline variables: one object per program even though
// every translation unit that includes this header "defines" them [basic.def.odr].
#pragma once
#include <cstdio>
#include <source_location>

namespace chk {
inline int passed = 0;
inline int failed = 0;
inline int skipped = 0;

inline void check(bool ok, const char* expr,
                  std::source_location loc = std::source_location::current()) {
    if (ok) { ++passed; return; }
    ++failed;
    std::fprintf(stderr, "  FAIL %s:%u: %s\n", loc.file_name(), static_cast<unsigned>(loc.line()), expr);
}

inline void skip(const char* feature, const char* why) {
    ++skipped;
    std::printf("  SKIP %s: %s\n", feature, why);
}

// Returns the process exit code: 0 iff nothing failed (skips are not failures).
inline int report(const char* name) {
    std::printf("%-18s %3d passed, %d failed, %d skipped\n", name, passed, failed, skipped);
    return failed == 0 ? 0 : 1;
}
}  // namespace chk

// variadic so that braces with commas, CHECK(v == T{1, 2}), need no extra parentheses
#define CHECK(...) ::chk::check(static_cast<bool>(__VA_ARGS__), #__VA_ARGS__)
