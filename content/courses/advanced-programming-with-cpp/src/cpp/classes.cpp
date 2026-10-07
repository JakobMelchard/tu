// classes.cpp -- special members, rule of zero/five, inheritance vs composition,
// virtual dispatch, slicing, final, CRTP (note 09).
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <memory>
#include <numbers>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>
#include "check.hpp"

// --- rule of five: a class that owns a raw resource must define all five
class Buffer {
    std::size_t n_ = 0;
    double* data_ = nullptr;
public:
    Buffer() = default;
    explicit Buffer(std::size_t n, double v = 0) : n_(n), data_(new double[n]) { std::fill_n(data_, n, v); }
    ~Buffer() { delete[] data_; }
    Buffer(const Buffer& o) : n_(o.n_), data_(o.n_ ? new double[o.n_] : nullptr) { std::copy_n(o.data_, n_, data_); }
    Buffer(Buffer&& o) noexcept : n_(std::exchange(o.n_, 0)), data_(std::exchange(o.data_, nullptr)) {}
    Buffer& operator=(Buffer o) noexcept { swap(*this, o); return *this; }   // copy-and-swap: both assignments
    friend void swap(Buffer& a, Buffer& b) noexcept { std::swap(a.n_, b.n_); std::swap(a.data_, b.data_); }
    std::size_t size() const { return n_; }
    double& operator[](std::size_t i) { return data_[i]; }
    const double* data() const { return data_; }
};

// --- rule of zero: members manage themselves, write none of the five
struct Grid {
    std::vector<double> values;
    std::string label;
};
static_assert(std::is_nothrow_move_constructible_v<Grid> && std::is_copy_constructible_v<Grid>);

// --- declaring a destructor silently removes the implicit move operations
int grid_copies = 0;
struct Tracked { Tracked() = default; Tracked(const Tracked&) { ++grid_copies; } Tracked(Tracked&&) noexcept = default; };
struct LoggingGrid {
    Tracked t;
    ~LoggingGrid() {}                       // user-declared dtor: no implicit move ctor/assign
};
struct QuietGrid { Tracked t; };

// --- runtime polymorphism
struct Shape {
    virtual ~Shape() = default;             // deleting through Shape* must reach the derived dtor
    virtual double area() const = 0;        // pure virtual: Shape is abstract
    virtual std::string name() const { return "shape"; }
};
struct Circle final : Shape {               // final: no further derivation, enables devirtualisation
    double r;
    explicit Circle(double r) : r(r) {}
    double area() const override { return std::numbers::pi * r * r; }
    std::string name() const override { return "circle"; }
};
struct Rect : Shape {
    double w, h;
    Rect(double w, double h) : w(w), h(h) {}
    double area() const override { return w * h; }
};
struct Square : Rect { explicit Square(double s) : Rect(s, s) {} std::string name() const override { return "square"; } };

// slicing needs a copyable base
struct Base { virtual ~Base() = default; virtual int id() const { return 0; } };
struct Derived : Base { int id() const override { return 1; } };
int id_by_value(Base b) { return b.id(); }        // copies only the Base part
int id_by_ref(const Base& b) { return b.id(); }

// --- static polymorphism: CRTP, no vtable, calls resolved at compile time
template <class D> struct Integrator {
    double run(double a, double b, int n) const {       // D supplies weight(i, n)
        const auto& d = static_cast<const D&>(*this);
        double h = (b - a) / n, s = 0;
        for (int i = 0; i <= n; ++i) s += d.weight(i, n) * d.f(a + i * h);
        return s * h;
    }
};
struct TrapezoidSquare : Integrator<TrapezoidSquare> {
    double weight(int i, int n) const { return (i == 0 || i == n) ? 0.5 : 1.0; }
    double f(double x) const { return x * x; }
};

int main() {
    Buffer a(3, 1.0);
    Buffer b = a;                           // deep copy
    b[0] = 5;
    CHECK(a.data() != b.data() && b[0] == 5.0);
    Buffer c = std::move(a);                // steal
    CHECK(a.size() == 0 && a.data() == nullptr && c.size() == 3);
    Buffer& alias = c;
    c = alias;                              // self-assignment is safe with copy-and-swap
    CHECK(c.size() == 3);
    b = Buffer(2);
    CHECK(b.size() == 2);

    // user-declared destructor => "move" falls back to copy
    grid_copies = 0;
    LoggingGrid lg;
    LoggingGrid lg2 = std::move(lg);
    CHECK(grid_copies == 1);
    grid_copies = 0;
    QuietGrid qg;
    QuietGrid qg2 = std::move(qg);
    CHECK(grid_copies == 0);
    (void)lg2; (void)qg2;

    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>(1.0));
    shapes.push_back(std::make_unique<Square>(2.0));
    double total = 0;
    for (const auto& s : shapes) total += s->area();
    CHECK(std::abs(total - (std::numbers::pi + 4)) < 1e-12);
    CHECK(shapes[1]->name() == "square");
    CHECK(dynamic_cast<Rect*>(shapes[1].get()) != nullptr);   // Square is-a Rect
    CHECK(dynamic_cast<Circle*>(shapes[1].get()) == nullptr);
    static_assert(std::is_abstract_v<Shape> && std::is_final_v<Circle>);
    static_assert(std::has_virtual_destructor_v<Shape>);
    static_assert(sizeof(Circle) == sizeof(void*) + sizeof(double));   // vptr + r (typical ABI)

    Derived d;
    CHECK(id_by_ref(d) == 1 && id_by_value(d) == 0);         // slicing

    CHECK(std::abs(TrapezoidSquare{}.run(0, 1, 1000) - 1.0 / 3) < 1e-6);
    return chk::report("classes");
}
