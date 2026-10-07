# 09 Classes: special members, rule of zero/five, inheritance vs composition, virtual, CRTP

Two of the three 2021W EX1 parts were "make this resource-owning class correct" (a
vector's copy/move constructor and destructor; a linked list's four copy/move
members) [S4]. Items 008 (special member functions), 020 (inheritance), 024
(exceptions) [S3]. C.20, C.21, C.35, C.67, C.128 [S10].

Code: `src/cpp/classes.cpp`.

## Definitions [S8 [special], [class.copy.assign], [class.dtor], [dcl.fct.def.default]]

- **Special member functions**: default constructor `T()`, copy constructor
  `T(const T&)`, copy assignment `T& operator=(const T&)`, move constructor `T(T&&)`,
  move assignment `T& operator=(T&&)`, destructor `~T()`. The compiler declares them
  implicitly under rules that depend on what *you* declared:

| you declare | default ctor | copy ctor / copy assign | move ctor / move assign | dtor |
|---|---|---|---|---|
| nothing | implicit | implicit | implicit | implicit |
| any other constructor | **not declared** | implicit | implicit | implicit |
| destructor | implicit | implicit (deprecated) | **not declared** | yours |
| copy constructor | **not declared** (it is a ctor) | yours / implicit (deprecated) | **not declared** | implicit |
| copy assignment | implicit | implicit (deprecated) / yours | **not declared** | implicit |
| move constructor | **not declared** (it is a ctor) | **deleted** | yours / not declared | implicit |
| move assignment | implicit | **deleted** | not declared / yours | implicit |

  "Not declared" move means an rvalue argument binds to the copy constructor:
  `T b = std::move(a);` silently copies. `= default` asks for the compiler's version
  (which may still be deleted), `= delete` forbids.
- **Rule of zero** (C.20): if every member manages itself (`std::vector`,
  `std::string`, `std::unique_ptr`), write none of the five; the generated ones are
  correct and `noexcept` where the members' are.
- **Rule of five** (C.21): if you must write one of destructor, copy ctor, copy assign,
  move ctor, move assign (because the class owns a raw resource), write or
  `=default`/`=delete` all five.
- **Copy-and-swap**: `T& operator=(T other) noexcept { swap(*this, other); return *this; }`
  implements both assignments, is self-assignment safe and gives the strong exception
  guarantee (the copy happens before `*this` is touched).
- **Inheritance**: `class D : public B` models is-a; `D` contains a `B` subobject.
  Construction runs base first then members (in declaration order) then the body;
  destruction in reverse. **Composition** (a member of type `B`) models has-a and is
  the default choice.
- **Virtual function**: call through `B&`/`B*` dispatches on the *dynamic* type (via a
  vtable pointer in each object). `override` checks you really override; `final`
  forbids further overriding/derivation (lets the compiler devirtualise). A base used
  polymorphically needs a **virtual destructor** (C.35), otherwise `delete base_ptr`
  is UB. **Pure virtual** `= 0` makes the class abstract.
- **Slicing**: copying a `D` into a `B` object keeps only the `B` part; virtual calls on
  the copy call `B`'s versions. Polymorphic bases should suppress public copying (C.67).
- **CRTP** (curiously recurring template pattern): `struct D : Base<D>`; `Base<D>`
  calls `static_cast<const D&>(*this).impl()`. Static polymorphism: no vtable, calls
  inlined, but no runtime heterogeneity (no `vector<Base*>`). C++23 deducing `this`
  replaces many CRTP uses (`void f(this auto& self)` knows the derived type).

## Complete example

```cpp
// complete example: classes
#include <algorithm>
#include <cstddef>
#include <cstdio>
#include <memory>
#include <type_traits>
#include <utility>
#include <vector>

class Buffer {                          // owns a raw array: rule of five
    std::size_t n_ = 0;
    double* p_ = nullptr;
public:
    Buffer() = default;
    explicit Buffer(std::size_t n) : n_(n), p_(new double[n]{}) {}
    ~Buffer() { delete[] p_; }
    Buffer(const Buffer& o) : n_(o.n_), p_(o.n_ ? new double[o.n_] : nullptr) { std::copy_n(o.p_, n_, p_); }
    Buffer(Buffer&& o) noexcept : n_(std::exchange(o.n_, 0)), p_(std::exchange(o.p_, nullptr)) {}
    Buffer& operator=(Buffer o) noexcept { swap(*this, o); return *this; }   // copy-and-swap
    friend void swap(Buffer& a, Buffer& b) noexcept { std::swap(a.n_, b.n_); std::swap(a.p_, b.p_); }
    std::size_t size() const { return n_; }
};
struct Grid { std::vector<double> v; };  // rule of zero: nothing to write

struct Shape { virtual ~Shape() = default; virtual double area() const = 0; };
struct Square final : Shape { double s; explicit Square(double s) : s(s) {} double area() const override { return s * s; } };
struct Disk final : Shape { double r; explicit Disk(double r) : r(r) {} double area() const override { return 3.14159 * r * r; } };

int main() {
    Buffer a(1000), b = a, c = std::move(a);          // copy, then steal
    b = c;                                             // copy-assign via copy-and-swap
    std::printf("a=%zu b=%zu c=%zu\n", a.size(), b.size(), c.size());   // 0 1000 1000

    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Square>(2));
    shapes.push_back(std::make_unique<Disk>(1));
    double total = 0;
    for (const auto& s : shapes) total += s->area();   // virtual dispatch
    std::printf("total area %.5f\n", total);           // 7.14159
    static_assert(std::is_nothrow_move_constructible_v<Grid>);
}
```

## Pitfalls

- A user-declared destructor (even an empty one for logging) turns every "move" of the
  class into a copy: `classes.cpp` counts 1 copy for `std::move` of such a class, 0 for
  the same class without the destructor.
- Move constructor without `noexcept`: `std::vector<T>` copies on reallocation (note 05).
- Moved-from state must be valid: destructor and assignment must work on it
  (`n_ = 0, p_ = nullptr` above). ex1.2/ex1.3 ran under ASan to catch double frees [S4].
- Self-assignment in a hand-written copy assignment (`delete[] p_; p_ = new ...; copy
  from other.p_` destroys the source first). Copy-and-swap avoids it.
- Missing virtual destructor in a polymorphic base: derived destructor never runs.
- Calling a virtual function in a constructor/destructor calls the version of the class
  currently being constructed, not the derived override.
- Slicing when passing a polymorphic object by value (`classes.cpp`: `id_by_value(d)`
  returns the base's id).
- Protected data members and deep hierarchies: couple derived classes to base internals.
  Prefer composition, and interfaces (abstract bases) for runtime polymorphism.
- Order of member initialisation is the **declaration** order, not the mem-initialiser
  order (`-Wreorder` warns).

## Discussion questions

1. **Your class holds a `double*` from `new[]`. What goes wrong with the compiler-generated copy constructor?**
   It copies the pointer (shallow copy); both objects `delete[]` the same buffer:
   double free (ASan: "attempting double-free"). Write a deep copy, a stealing move,
   and a destructor, or better replace the pointer by `std::vector<double>` (rule of zero).
2. **What exactly should a move constructor do?** Take the source's resources
   (`std::exchange`), leave the source valid and cheap to destroy (null/zero), never
   throw (`noexcept`), allocate nothing.
3. **Why does copy-and-swap give the strong exception guarantee?** The only operation
   that can throw (the copy into the by-value parameter) happens before `*this` is
   modified; `swap` is `noexcept`. If the copy throws, `*this` is unchanged.
4. **When is a virtual destructor needed, and what does it cost?** When objects are
   deleted through a base pointer (including `unique_ptr<Base>`). Cost: a vptr per
   object (8 bytes here: `sizeof(Circle) == 16` for one `double`), an indirect call on
   destruction, and the class is no longer trivially destructible.
5. **CRTP vs virtual functions: when which?** Virtual: the concrete type is known only
   at run time, heterogeneous containers, plugin boundaries. CRTP/templates: type known
   at compile time, hot inner loops (inlining matters), no need to mix types in one
   container. C++23 deducing `this` covers the "base calls derived" part of CRTP with
   less ceremony.

## In the code

- `src/cpp/classes.cpp`: `Buffer` (rule of five with copy-and-swap, self-assignment, move leaving an empty source), `Grid` (rule of zero, `static_assert`ed), `LoggingGrid` vs `QuietGrid` (destructor suppresses move: 1 copy vs 0), `Shape`/`Circle`/`Rect`/`Square` (abstract, `final`, `override`, `dynamic_cast`, `sizeof` with vptr), slicing, a CRTP trapezoid integrator.
- `src/cpp/smart_pointers.cpp`: `my::unique_ptr`, a move-only class with deleted copy.
