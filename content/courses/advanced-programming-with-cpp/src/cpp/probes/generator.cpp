// P2502 std::generator
#include <generator>
std::generator<int> g() { co_yield 1; }
int main() { for (int x : g()) return x - 1; }
