// P2442 views::chunk / views::slide
#include <ranges>
#include <vector>
int main() { std::vector a{1, 2, 3}; auto c = a | std::views::chunk(2); auto s = a | std::views::slide(2); return (std::ranges::distance(c) == 2 && std::ranges::distance(s) == 2) ? 0 : 1; }
