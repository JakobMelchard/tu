// P0660 std::jthread + std::stop_token
#include <thread>
int main() { std::jthread t([](std::stop_token st) { while (!st.stop_requested()) {} }); }
