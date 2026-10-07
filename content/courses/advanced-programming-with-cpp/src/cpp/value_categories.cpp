// value_categories.cpp -- lvalue/xvalue/prvalue, move semantics, forwarding,
// copy elision, all made measurable by counting copies and moves (note 05).
#include <string>
#include <type_traits>
#include <utility>
#include <vector>
#include "check.hpp"

// decltype((e)) encodes the category of e [dcl.type.decltype]: T& lvalue, T&& xvalue, T prvalue
template <class T> constexpr const char* category() {
    if constexpr (std::is_lvalue_reference_v<T>) return "lvalue";
    else if constexpr (std::is_rvalue_reference_v<T>) return "xvalue";
    else return "prvalue";
}
#define CATEGORY(...) std::string(category<decltype((__VA_ARGS__))>())

struct Stats { int copies = 0, moves = 0; };
Stats st;
void reset() { st = {}; }

struct Counted {                                  // move is noexcept
    std::vector<double> data = std::vector<double>(100);
    Counted() = default;
    Counted(const Counted& o) : data(o.data) { ++st.copies; }
    Counted(Counted&& o) noexcept : data(std::move(o.data)) { ++st.moves; }
    Counted& operator=(const Counted& o) { data = o.data; ++st.copies; return *this; }
    Counted& operator=(Counted&& o) noexcept { data = std::move(o.data); ++st.moves; return *this; }
};
struct CountedMayThrow {                          // same, but the move is NOT noexcept
    CountedMayThrow() = default;
    CountedMayThrow(const CountedMayThrow&) { ++st.copies; }
    CountedMayThrow(CountedMayThrow&&) { ++st.moves; }
};

Counted make_prvalue() { return Counted{}; }                  // guaranteed elision (C++17)
Counted make_named() { Counted c; c.data[0] = 1; return c; }  // NRVO: allowed, not guaranteed

// three ways to take a sink argument
struct Box { Counted c; };
Box by_cref(const Counted& c) { return Box{c}; }              // always copies
Box by_value(Counted c) { return Box{std::move(c)}; }         // copy-or-move in, then one move
Box by_rref(Counted&& c) { return Box{std::move(c)}; }        // rvalues only, one move

// perfect forwarding: preserves the category of each argument
template <class... Args> Box make_box(Args&&... args) { return Box{Counted(std::forward<Args>(args)...)}; }

int main() {
    int i = 0;
    Counted obj;
    const Counted cobj;
    CHECK(CATEGORY(i) == "lvalue");
    CHECK(CATEGORY(++i) == "lvalue");
    CHECK(CATEGORY(i++) == "prvalue");
    CHECK(CATEGORY(42) == "prvalue");
    CHECK(CATEGORY("literal") == "lvalue");            // string literals are lvalue arrays
    CHECK(CATEGORY(std::move(i)) == "xvalue");
    CHECK(CATEGORY(static_cast<int&&>(i)) == "xvalue");
    CHECK(CATEGORY(Counted{}) == "prvalue");
    CHECK(CATEGORY(Counted{}.data) == "xvalue");       // member of an rvalue
    CHECK(CATEGORY(obj.data) == "lvalue");

    reset(); Counted a = obj;                    CHECK(st.copies == 1 && st.moves == 0);
    reset(); Counted b = std::move(a);           CHECK(st.copies == 0 && st.moves == 1);
    CHECK(a.data.empty());                       // moved-from: valid but unspecified (here: empty)
    reset(); Counted c = std::move(cobj);        CHECK(st.copies == 1 && st.moves == 0);  // const&& binds to const& : a COPY
    reset(); Counted d = make_prvalue();         CHECK(st.copies == 0 && st.moves == 0);  // no temporary exists
    reset(); Counted e = make_named();           CHECK(st.copies == 0 && st.moves <= 1);  // NRVO or implicit move
    (void)b; (void)c; (void)d; (void)e;

    reset(); by_cref(obj);                       CHECK(st.copies == 1 && st.moves == 0);
    reset(); by_cref(Counted{});                 CHECK(st.copies == 1 && st.moves == 0);  // rvalue still copied
    reset(); by_value(obj);                      CHECK(st.copies == 1 && st.moves == 1);
    reset(); by_value(Counted{});                CHECK(st.copies == 0 && st.moves == 1);  // param elided
    reset(); by_rref(Counted{});                 CHECK(st.copies == 0 && st.moves == 1);

    // Counted(...) inside make_box is a prvalue that initialises Box::c directly: the
    // only copy/move left is the one the argument's category asks for
    reset(); make_box(obj);                      CHECK(st.copies == 1 && st.moves == 0);
    reset(); make_box(std::move(obj));           CHECK(st.copies == 0 && st.moves == 1);
    reset(); make_box();                         CHECK(st.copies == 0 && st.moves == 0);

    // push_back vs emplace_back (capacity reserved so no reallocation interferes)
    std::vector<Counted> vec;
    vec.reserve(8);
    Counted local;
    reset(); vec.push_back(local);               CHECK(st.copies == 1 && st.moves == 0);
    reset(); vec.push_back(std::move(local));    CHECK(st.copies == 0 && st.moves == 1);
    reset(); vec.push_back(Counted{});           CHECK(st.copies == 0 && st.moves == 1);
    reset(); vec.emplace_back();                 CHECK(st.copies == 0 && st.moves == 0);

    // reallocation uses move_if_noexcept: strong exception guarantee costs copies
    std::vector<Counted> v1(4);
    v1.shrink_to_fit();
    reset(); v1.emplace_back();                  CHECK(st.copies == 0 && st.moves == 4);
    std::vector<CountedMayThrow> v2(4);
    v2.shrink_to_fit();
    reset(); v2.emplace_back();                  CHECK(st.copies == 4 && st.moves == 0);

    // forwarding reference vs rvalue reference: T&& is forwarding only when T is deduced
    static_assert(std::is_same_v<decltype(std::forward<int&>(i)), int&>);
    static_assert(std::is_same_v<decltype(std::forward<int>(i)), int&&>);
    return chk::report("value_categories");
}
