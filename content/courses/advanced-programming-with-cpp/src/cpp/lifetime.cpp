// lifetime.cpp -- trivial types, implicit-lifetime types, object lifetime (note 03).
#include <bit>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <memory>
#include <new>
#include <string>
#include <type_traits>
#include <vector>
#include "check.hpp"

// --- classification [basic.types.general], [class.prop]
struct Pod { int id; double x, y; };                 // trivial + standard-layout + aggregate
struct WithCtor { int v; WithCtor() : v(1) {} };     // user-provided default ctor: not trivial
struct WithDtor { int v; ~WithDtor() {} };           // user-provided dtor: not trivially copyable
struct WithString { int id; std::string name; };     // aggregate, but member is not trivial
struct Mixed { public: int a; private: int b = 0; public: int get() const { return b; } }; // access mix

static_assert(std::is_trivially_copyable_v<Pod> && std::is_standard_layout_v<Pod> && std::is_aggregate_v<Pod>);
static_assert(std::is_trivially_default_constructible_v<Pod>);
static_assert(!std::is_trivially_default_constructible_v<WithCtor> && std::is_trivially_copyable_v<WithCtor>);
static_assert(!std::is_trivially_copyable_v<WithDtor>);
static_assert(std::is_aggregate_v<WithString> && !std::is_trivially_copyable_v<WithString>);
static_assert(!std::is_standard_layout_v<Mixed>);
#if defined(__cpp_lib_is_implicit_lifetime)
// implicit-lifetime: objects may be created implicitly by malloc/memcpy [intro.object]
static_assert(std::is_implicit_lifetime_v<Pod> && std::is_implicit_lifetime_v<int[4]>);
// [class.prop]/9: ANY aggregate whose destructor is not user-provided qualifies, even
// with a std::string member (surprising, but only the aggregate itself is "created").
static_assert(std::is_implicit_lifetime_v<WithString>);
static_assert(std::is_implicit_lifetime_v<WithCtor>);    // trivial copy ctor + trivial dtor
static_assert(!std::is_implicit_lifetime_v<WithDtor>);   // user-provided dtor, not trivial
#endif

// --- a tracer that logs its lifetime events
std::vector<std::string> events;
struct Tracer {
    std::string name;
    int value = 0;
    explicit Tracer(std::string n, int v = 0) : name(std::move(n)), value(v) { events.push_back("ctor " + name); }
    Tracer(const Tracer& o) : name(o.name + "'"), value(o.value) { events.push_back("copy " + name); }
    ~Tracer() { events.push_back("dtor " + name); }
};
Tracer make(const char* n) { return Tracer{n}; }
struct Holder { Tracer t{"member"}; std::vector<int> items{1, 2, 3}; const std::vector<int>& get() const { return items; } };

int main() {
    // trivially copyable => memcpy is a valid copy; bit_cast reinterprets bytes safely
    Pod a{1, 2.0, 3.0}, b{};
    std::memcpy(&b, &a, sizeof a);
    CHECK(b.id == 1 && b.y == 3.0);
    CHECK(std::bit_cast<std::uint32_t>(1.0f) == 0x3f800000u);     // IEEE-754 single 1.0
    CHECK(std::bit_cast<std::uint64_t>(-0.0) == 0x8000000000000000ull);

    // designated initializers (C++20): in declaration order, the rest value-initialised
    Pod d{.id = 7, .y = 1.5};
    CHECK(d.id == 7 && d.x == 0.0 && d.y == 1.5);

    // scope: destruction in reverse order of construction
    events.clear();
    { Tracer t1{"1"}; Tracer t2{"2"}; }
    CHECK((events == std::vector<std::string>{"ctor 1", "ctor 2", "dtor 2", "dtor 1"}));

    // a temporary dies at the end of the full-expression ...
    events.clear();
    int v = make("tmp").value;
    CHECK(v == 0 && events.back() == "dtor tmp");
    // ... unless bound directly to a const& (or &&): lifetime extended to the reference's scope
    events.clear();
    {
        const Tracer& r = make("ext");
        CHECK(events.size() == 1 && r.name == "ext");   // no dtor yet
    }
    CHECK(events.back() == "dtor ext");
    // binding to a MEMBER of a prvalue extends the whole complete object [class.temporary]
    events.clear();
    {
        const Tracer& m = Holder{}.t;
        CHECK(events.size() == 1 && m.name == "member");
    }
    CHECK(events.back() == "dtor member");

    // C++23 (P2718): temporaries in the range-initializer of a range-for live for the whole loop
#if __cpp_range_based_for >= 202211L
    int sum = 0;
    for (int i : Holder{}.get()) sum += i;   // was dangling before C++23: Holder died before the loop
    CHECK(sum == 6);
#else
    chk::skip("P2718 range-for lifetime", "__cpp_range_based_for < 202211");
#endif

    // manual lifetime in raw storage: construct_at / destroy_at (what vector does inside)
    events.clear();
    alignas(Tracer) std::byte buf[sizeof(Tracer)];
    Tracer* p = std::construct_at(reinterpret_cast<Tracer*>(buf), "raw", 3);
    CHECK(p->value == 3 && events.size() == 1);
    std::destroy_at(p);                                 // storage lives on, the object does not
    CHECK(events.back() == "dtor raw");
    // a new object in the same storage: the old pointer p must not be used for it
    Tracer* q = std::construct_at(reinterpret_cast<Tracer*>(buf), "again", 4);
    CHECK(q->value == 4);
    std::destroy_at(q);

    // implicit object creation: malloc'd bytes may hold an implicit-lifetime type (C++20)
    auto* raw = static_cast<Pod*>(std::malloc(sizeof(Pod)));
    raw->id = 5;                                        // OK since P0593: Pod is implicit-lifetime
    CHECK(raw->id == 5);
    std::free(raw);
    return chk::report("lifetime");
}
