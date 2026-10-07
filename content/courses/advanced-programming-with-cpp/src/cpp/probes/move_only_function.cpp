// P0288 std::move_only_function
#include <functional>
int main() { std::move_only_function<int()> f = [] { return 0; }; return f(); }
