// MUST NOT COMPILE: signed overflow is UB, and UB is diagnosed in constant evaluation.
// expect: constant expression
constexpr int twice(int x) { return 2 * x; }
static_assert(twice(2'000'000'000) > 0);
int main() {}
