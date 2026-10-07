// pointers.cpp -- pointers, references, spans and who owns what (note 04).
#include <array>
#include <functional>
#include <memory>
#include <numeric>
#include <span>
#include <string>
#include <type_traits>
#include <vector>
#include "check.hpp"

// const placement: read right to left
static_assert(std::is_const_v<std::remove_pointer_t<const int*>>);   // pointer to const int
static_assert(!std::is_const_v<const int*>);                          // the pointer itself is mutable
static_assert(std::is_const_v<int* const>);                           // const pointer to mutable int
static_assert(sizeof(int&) == sizeof(int));                           // sizeof(ref) = sizeof(referee)

// parameter-passing conventions (C++ Core Guidelines F.15-F.20)
double sum(std::span<const double> xs) {                  // in: read-only view, any contiguous source
    return std::accumulate(xs.begin(), xs.end(), 0.0);
}
void scale(std::span<double> xs, double f) {              // in-out: mutable view, no ownership
    for (double& x : xs) x *= f;
}
struct Particle {
    std::string name;
    explicit Particle(std::string n) : name(std::move(n)) {}   // sink: by value, then move
};
int* find_first(std::vector<int>& v, int key) {           // may-be-null observer: T*
    for (int& x : v) if (x == key) return &x;
    return nullptr;
}

int main() {
    // references: must be initialised, cannot be reseated; assignment writes the referee
    int a = 1, b = 2;
    int& r = a;
    r = b;                       // a = 2, r still refers to a
    CHECK(a == 2 && &r == &a);
    int* p = &a;
    p = &b;                      // pointers reseat
    CHECK(*p == 2 && p == &b);

    // pointer arithmetic is defined only within one array (and one past its end)
    std::array<int, 4> arr{10, 20, 30, 40};
    int* first = arr.data();
    int* last = first + arr.size();              // one-past-the-end: may be formed, not dereferenced
    CHECK(last - first == 4 && *(first + 2) == 30);

    // span: pointer + size, the modern (T*, n) pair; views vector, array and C array alike
    std::vector<double> v{1, 2, 3};
    double c[2] = {0.5, 0.5};
    CHECK(sum(v) == 6.0 && sum(c) == 1.0 && sum(std::span(v).subspan(1)) == 5.0);
    scale(v, 2.0);
    CHECK(v[2] == 6.0);

    // observer returning T* (nullable) vs throwing/optional
    std::vector<int> keys{4, 5, 6};
    CHECK(find_first(keys, 5) == &keys[1] && find_first(keys, 9) == nullptr);

    // invalidation: a pointer/reference/iterator into a vector dies on reallocation
    std::vector<int> grow{1};
    grow.shrink_to_fit();
    const int* before = grow.data();
    const auto cap = grow.capacity();
    grow.push_back(2);                         // size > capacity: reallocates
    CHECK(grow.capacity() > cap);
    // `before` is now an invalid pointer value: dereferencing it is use-after-free (ASan
    // reports it), and even comparing it is implementation-defined [basic.stc.general].
    // Re-obtain pointers/iterators after any operation that may reallocate.
    (void)before;

    // reference_wrapper: rebindable, storable reference (containers cannot hold T&)
    int x = 1, y = 2;
    std::vector<std::reference_wrapper<int>> refs{x, y};
    for (int& e : refs) e *= 10;
    CHECK(x == 10 && y == 20);

    // ownership: exactly one owner; everything else observes
    auto owner = std::make_unique<Particle>("e-");
    Particle* observer = owner.get();          // non-owning, must not outlive owner
    CHECK(observer->name == "e-");
    Particle moved{std::string("mu-")};        // sink parameter: the string is moved in
    CHECK(moved.name == "mu-");
    auto new_owner = std::move(owner);         // ownership transfer is explicit
    CHECK(owner == nullptr && new_owner.get() == observer);

    // nullptr has its own type, so overloads on int vs pointer are unambiguous
    static_assert(std::is_same_v<decltype(nullptr), std::nullptr_t>);
    return chk::report("pointers");
}
