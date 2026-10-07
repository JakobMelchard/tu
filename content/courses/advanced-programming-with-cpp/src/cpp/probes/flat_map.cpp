// P0429 std::flat_map
#include <flat_map>
int main() { std::flat_map<int, int> m{{2, 0}, {1, 0}}; return m.begin()->first - 1; }
