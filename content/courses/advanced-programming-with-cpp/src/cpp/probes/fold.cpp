// P2322 ranges::fold_left
#include <algorithm>
#include <functional>
#include <vector>
int main() { std::vector a{1, 2, 3}; return std::ranges::fold_left(a, 0, std::plus{}) == 6 ? 0 : 1; }
