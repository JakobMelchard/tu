// MUST NOT COMPILE: narrowing conversion inside braces.
// expect: cannot be narrowed
int main() { double d = 3.7; int i{d}; return i; }
