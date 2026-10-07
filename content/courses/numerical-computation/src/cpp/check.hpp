// Tiny test harness shared by the C++ programs.
// Each program computes a result, prints it, and CHECK_NEARs it against a
// known value; main() returns the number of failed checks, so `make test`
// fails when any check fails.
#pragma once
#include <cmath>
#include <cstdio>
#include <string>

namespace check {

inline int failures = 0;

inline void near(const std::string& what, double got, double expect, double tol) {
    const double err = std::fabs(got - expect);
    const bool ok = err <= tol;
    std::printf("  [%s] %-42s got %.12g  expect %.12g  |err| %.2e (tol %.1e)\n",
                ok ? "ok" : "FAIL", what.c_str(), got, expect, err, tol);
    if (!ok) ++failures;
}

inline void less(const std::string& what, double got, double bound) {
    const bool ok = got <= bound;
    std::printf("  [%s] %-42s got %.3e  bound %.1e\n", ok ? "ok" : "FAIL", what.c_str(), got, bound);
    if (!ok) ++failures;
}

inline int summary(const char* prog) {
    std::printf("%s: %s (%d failure%s)\n", prog, failures ? "FAILED" : "all checks passed",
                failures, failures == 1 ? "" : "s");
    return failures;
}

}  // namespace check

#define CHECK_NEAR(got, expect, tol) check::near(#got, (got), (expect), (tol))
#define CHECK_LESS(got, bound) check::less(#got, (got), (bound))
