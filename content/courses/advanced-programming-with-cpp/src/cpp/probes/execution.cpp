// P0024 parallel algorithms with std::execution policies (libc++: -fexperimental-library)
#include <execution>
#include <numeric>
#include <vector>
int main() { std::vector<int> v(10, 1); return std::reduce(std::execution::par, v.begin(), v.end()) == 10 ? 0 : 1; }
