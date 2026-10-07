// MUST NOT COMPILE: the argument type does not satisfy the constraint.
// expect: no matching function
#include <concepts>
double half(std::floating_point auto x) { return x / 2; }
int main() { return static_cast<int>(half(3)); }
