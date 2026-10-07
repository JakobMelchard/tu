// P0009 std::mdspan + P2128 multidimensional operator[]
#include <mdspan>
int main() { double d[6]{}; std::mdspan m(d, 2, 3); m[1, 2] = 1; return static_cast<int>(d[5]) - 1; }
