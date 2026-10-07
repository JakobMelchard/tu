// MUST NOT COMPILE: a consteval function called with a runtime value.
// expect: not a constant expression
consteval int square(int x) { return x * x; }
int main(int argc, char**) { return square(argc); }
