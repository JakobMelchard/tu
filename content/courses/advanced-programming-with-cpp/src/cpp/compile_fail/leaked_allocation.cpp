// MUST NOT COMPILE: memory allocated during constant evaluation must be freed by its end.
// expect: constant expression
#include <vector>
constexpr std::vector<int> v{1, 2, 3};
int main() {}
