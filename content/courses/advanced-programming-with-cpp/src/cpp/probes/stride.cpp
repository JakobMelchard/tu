// P1899 views::stride
#include <ranges>
#include <vector>
int main() { std::vector a{1, 2, 3}; return std::ranges::distance(a | std::views::stride(2)) == 2 ? 0 : 1; }
