// P1206 std::ranges::to
#include <ranges>
#include <vector>
int main() { auto v = std::views::iota(0, 3) | std::ranges::to<std::vector>(); return v.size() == 3 ? 0 : 1; }
