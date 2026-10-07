// P2321 views::zip
#include <ranges>
#include <vector>
int main() { std::vector a{1}, b{2}; for (auto [x, y] : std::views::zip(a, b)) return x + y - 3; }
