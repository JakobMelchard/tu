// buggy_sample.cpp -- deliberately broken code for the sanitizer demo (topic 10).
// Each bug is selected by argv[1]; compile with -fsanitize=address,undefined -g.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

int heap_overflow() {
    std::vector<int> v(8, 1);
    int s = 0;
    for (int i = 0; i <= 8; ++i) s += v.data()[i];   // reads one past the end
    return s;
}
int use_after_free() {
    int* p = new int[4];
    delete[] p;
    return p[0];                                     // memory already returned
}
int signed_overflow(int x) {
    return x + 1;                                    // UB when x == INT_MAX
}
int stack_overflow() {
    int a[4] = {0, 1, 2, 3};
    int i = 4;
    return a[i];                                     // index computed at run time, out of bounds
}

int main(int argc, char** argv) {
    const char* which = argc > 1 ? argv[1] : "heap";
    if (!std::strcmp(which, "heap")) std::printf("%d\n", heap_overflow());
    else if (!std::strcmp(which, "uaf")) std::printf("%d\n", use_after_free());
    else if (!std::strcmp(which, "int")) std::printf("%d\n", signed_overflow(2147483647));
    else if (!std::strcmp(which, "stack")) std::printf("%d\n", stack_overflow());
    return 0;
}
