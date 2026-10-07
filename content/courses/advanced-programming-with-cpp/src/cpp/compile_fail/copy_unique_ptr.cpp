// MUST NOT COMPILE: unique_ptr is move-only.
// expect: deleted copy constructor
#include <memory>
int main() { auto p = std::make_unique<int>(1); auto q = p; return *q; }
