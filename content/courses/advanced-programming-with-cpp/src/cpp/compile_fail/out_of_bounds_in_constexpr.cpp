// MUST NOT COMPILE: reading past the end of an array in a constant expression.
// expect: constant expression
constexpr int at(int i) { int a[3] = {1, 2, 3}; return a[i]; }
constexpr int x = at(3);
int main() {}
