// P2374 views::cartesian_product
#include <ranges>
#include <vector>
int main() { std::vector a{1, 2}; return std::ranges::distance(std::views::cartesian_product(a, a)) == 4 ? 0 : 1; }
