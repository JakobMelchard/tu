// P0323 std::expected (+ P2505 monadic and_then/transform)
#include <expected>
std::expected<int, int> f() { return std::unexpected(1); }
int main() { return f().transform([](int v) { return v; }).error_or(0) == 1 ? 0 : 1; }
