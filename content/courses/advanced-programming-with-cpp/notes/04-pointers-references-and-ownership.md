# 04 Pointers, references and ownership

C gives you pointers; C++ adds references and a vocabulary for *who is responsible
for deleting what*. The discussion question is rarely "what is a pointer" and almost
always "who owns this, and how long does it live?". Lecture items 006, 018, 020 [S3];
Core Guidelines F.15-F.20, I.11, R.1-R.3 [S10].

Code: `src/cpp/pointers.cpp`.

## Definitions [S8 [basic.compound], [dcl.ref]]

- **Pointer** `T*`: an object holding an address (or `nullptr`). Reseatable, nullable,
  supports arithmetic *within one array* (and one past its end). `sizeof(T*)` is 8 here.
- **Reference** `T&`: an alias for an existing object. Must be initialised, cannot be
  reseated, cannot be null (in a correct program), no arithmetic. `sizeof(T&) ==
  sizeof(T)`; `&r` is the referee's address. Assignment through a reference assigns the
  referee.
- **const placement**, read right to left: `const T*` (pointer to const T),
  `T* const` (const pointer), `const T* const`. A `const T&` binds to rvalues too.
- **`std::span<T>`** (C++20): pointer + size, a non-owning view of contiguous elements,
  the modern `(T*, n)` pair. `span<const T>` for read-only.
- **Owner** of a resource: the one object whose destruction releases it. In modern C++
  owners are RAII objects (`std::vector`, `std::string`, `std::unique_ptr`, a `std::fstream`);
  raw `T*` and `T&` are **non-owning** by convention (I.11: never transfer ownership by
  a raw pointer or reference [S10]).
- **Invalid pointer value** [S8 [basic.stc.general]]: a pointer into storage that has been
  released. Dereferencing it is UB; even copying or comparing it is
  implementation-defined.

## Parameter passing (the cheat sheet the discussions test)

| intent | parameter | example |
|---|---|---|
| in, cheap to copy (<= 2-3 words) | `T` | `double`, `std::span<const double>`, `std::string_view` |
| in, expensive | `const T&` | `const Matrix&` |
| in, may be absent | `const T*` | `const Config* cfg` (nullptr = default) |
| in-out | `T&` | `void normalise(Vec& v)` |
| out | return value (`T`, `std::pair`, struct, `std::optional<T>`, `std::expected`) | `Stats analyse(...)` |
| sink: will keep a copy | `T` then `std::move` | `Particle(std::string name) : name_(std::move(name))` |
| sink, move-only / performance-critical | `T&&` | `void push(Task&& t)` |
| transfer ownership | `std::unique_ptr<T>` by value | `void adopt(std::unique_ptr<Node> n)` |
| share ownership | `std::shared_ptr<T>` by value | rarely; see note 10 |

## Complete example

```cpp
// complete example: pointers
#include <cstdio>
#include <functional>
#include <memory>
#include <numeric>
#include <span>
#include <string>
#include <vector>

double sum(std::span<const double> xs) { return std::accumulate(xs.begin(), xs.end(), 0.0); }
void scale(std::span<double> xs, double f) { for (double& x : xs) x *= f; }
const int* find(const std::vector<int>& v, int key) {          // nullable observer
    for (const int& x : v) if (x == key) return &x;
    return nullptr;
}
struct Detector {
    std::string name;
    explicit Detector(std::string n) : name(std::move(n)) {}   // sink by value
};

int main() {
    int a = 1, b = 2;
    int& r = a;
    r = b;                                     // a becomes 2; r still aliases a
    std::vector<double> v{1, 2, 3};
    double c[] = {0.5, 0.5};
    scale(v, 2.0);
    std::printf("a=%d sum(v)=%g sum(c)=%g\n", a, sum(v), sum(c));   // 2 12 1

    std::vector<int> keys{4, 5, 6};
    if (const int* p = find(keys, 5)) std::printf("found at index %td\n", p - keys.data());

    int x = 1, y = 2;
    std::vector<std::reference_wrapper<int>> refs{x, y};   // containers cannot hold int&
    for (int& e : refs) e *= 10;

    auto owner = std::make_unique<Detector>("ATLAS");
    Detector* observer = owner.get();                     // must not outlive owner
    std::printf("x=%d y=%d %s\n", x, y, observer->name.c_str());
}
```

## Pitfalls

- **Dangling references**: returning `T&` to a local, capturing a local by reference in
  a lambda that outlives it (note 07), keeping `&v[0]` or an iterator across
  `v.push_back()` (reallocation), a `string_view` of a temporary string.
- **Invalidation rules** differ per container: `vector` invalidates everything on
  reallocation and everything after the point of insertion/erasure; `list`/`map`
  invalidate only erased elements; `deque` invalidates iterators on insertion at the
  ends but not references.
- **Pointer arithmetic outside one array** is UB, even without dereferencing
  (`p + 10` on a 3-element array).
- `const` through pointers is shallow: a `const` method may modify `*ptr_member`.
- A raw `new` without an owning object is a leak waiting for the first exception.
  Rule: no naked `new`/`delete` in application code (R.11 [S10]); `make_unique`.
- `T&&` in a non-template function is an rvalue reference, not "a reference to anything".

## Discussion questions

1. **Why does C++ need pointers if it has references?** References cannot be reseated,
   cannot be null, cannot be stored in standard containers, and have no arithmetic.
   Pointers are needed for optional relationships, rebinding (a linked list's `next`),
   arrays and raw memory. (This exact question is in the 2021W smart-pointer item [S3].)
2. **You call `v.push_back(x)` while holding `int& first = v[0];`. What can happen?**
   If `size() == capacity()`, the vector allocates a new buffer, moves the elements and
   frees the old one: `first` now refers to released storage (UB on use). ASan reports
   heap-use-after-free. Fix: `reserve`, indices instead of references, or re-fetch.
3. **Why pass a `std::string` sink parameter by value?** One signature serves both
   cases: an lvalue argument costs one copy (unavoidable, you want to keep it) + one
   move; an rvalue costs two moves (or one, with elision). `const std::string&` would
   force a copy for rvalues; overloading `const&` and `&&` saves one move but doubles
   the code (note 05 counts it).
4. **What does `std::span` fix compared with `(double* p, std::size_t n)`?** Size travels
   with the pointer, it converts implicitly from vector/array/C array, supports range-for
   and `subspan`, and `span<const T>` states read-only. It is still non-owning: a span
   of a destroyed vector dangles.
5. **How do you express "this function takes ownership"?** `std::unique_ptr<T>` by value:
   the caller must write `std::move(p)`, visible at the call site. A raw pointer
   parameter says nothing about ownership, which is the point of I.11.

## In the code

- `src/cpp/pointers.cpp`: const-placement traits, reference vs pointer reseating, one-past-the-end arithmetic, `span` from three sources, a nullable observer, vector reallocation (capacity checked, the old pointer deliberately not used), `reference_wrapper`, an ownership transfer.
- Ownership in depth: note 10 and `src/cpp/smart_pointers.cpp`.
