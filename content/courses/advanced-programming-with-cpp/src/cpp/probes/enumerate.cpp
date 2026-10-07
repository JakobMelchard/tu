// P2164 views::enumerate
#include <ranges>
#include <vector>
int main() { std::vector a{7}; for (auto [i, x] : std::views::enumerate(a)) return static_cast<int>(i); }
