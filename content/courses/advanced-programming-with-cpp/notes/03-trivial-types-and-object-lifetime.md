# 03 Trivial types and object lifetime

When may you `memcpy` an object, `malloc` it, put it in a byte buffer, or keep a
reference to it? The answer depends on the type's properties and on the object's
lifetime, which in C++ is a *language* concept, not a memory one. No dedicated 2021W
item [S3]; the rules are in the standard [S8].

Code: `src/cpp/lifetime.cpp`.

## Definitions [S8 [basic.types.general], [class.prop]]

| property | meaning | test |
|---|---|---|
| **trivially copyable** | at least one eligible copy/move ctor or assignment, every eligible one trivial, destructor trivial and not deleted | `std::is_trivially_copyable_v<T>`; `memcpy` is a valid copy |
| **trivial** | trivially copyable + trivial default constructor | `std::is_trivial_v<T>` |
| **standard-layout** | same access control for all non-static members, no virtual, no reference members, ... | `std::is_standard_layout_v<T>`; layout compatible with C, `offsetof` works |
| **aggregate** | no user-declared/inherited constructors, no private/protected direct members, no virtual | `std::is_aggregate_v<T>`; brace/designated initialisation |
| **implicit-lifetime** | scalars, arrays, aggregates whose destructor is not user-provided, classes with a trivial eligible ctor + trivial dtor | `std::is_implicit_lifetime_v<T>` (C++23, present in libc++ 21 [S13]) |

"Trivial" here means "compiler-generated and does nothing beyond what C would do"
(bitwise copy, no-op destructor). A *user-provided* special member (even an empty
`~T() {}`) makes it non-trivial; `= default` on the first declaration keeps it trivial.

**Lifetime** [S8 [basic.life]]: an object's lifetime begins when storage is obtained
*and* initialisation completes, and ends when the destructor call starts (or storage
is reused/released). Storage can outlive the object and vice versa never. Using an
object outside its lifetime is undefined behaviour, even if the bytes are still there.

**Storage durations**: automatic (block scope, destroyed in reverse order), static
(program lifetime, `constinit` to force compile-time init), thread, dynamic
(`new`/`delete`, containers).

**Temporaries** die at the end of the full-expression that created them, unless bound
directly to a `const T&` or `T&&` local reference, which extends the lifetime to the
reference's scope. Binding to a *member* of a prvalue extends the whole object.
C++23 (P2718) also extends every temporary in a range-`for` initialiser to the whole
loop (`__cpp_range_based_for >= 202211`, present in Apple clang 21 [S13]).

**Implicit object creation** (C++20, P0593) [S8 [intro.object]]: `malloc`, `memcpy`,
`std::bit_cast`, arrays of `std::byte` / `unsigned char` implicitly create objects of
implicit-lifetime types if that gives the program defined behaviour. This legalised
the C idiom `auto* p = (Pod*)malloc(sizeof(Pod)); p->x = 1;` after the fact. For
non-implicit-lifetime types you must construct explicitly: `std::construct_at` /
placement `new`, and destroy with `std::destroy_at`.

## Complete example

```cpp
// complete example: lifetime
#include <bit>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <type_traits>

struct Pod { int id; double x; };
struct Named { int id; std::string name; };
struct Loud {
    const char* tag;
    explicit Loud(const char* t) : tag(t) { std::printf("ctor %s\n", tag); }
    ~Loud() { std::printf("dtor %s\n", tag); }
};
Loud make(const char* t) { return Loud{t}; }

int main() {
    static_assert(std::is_trivially_copyable_v<Pod> && !std::is_trivially_copyable_v<Named>);
    static_assert(std::is_implicit_lifetime_v<Named>);         // aggregate: yes, surprisingly
    Pod a{1, 2.5}, b{};
    std::memcpy(&b, &a, sizeof a);                              // OK: trivially copyable
    std::printf("%d %.1f %08x\n", b.id, b.x, std::bit_cast<std::uint32_t>(1.0f));

    int n = make("temp").tag[0];                                // "dtor temp" before next line
    const Loud& kept = make("extended");                        // lives until end of main
    std::printf("n=%d, kept=%s\n", n, kept.tag);

    alignas(Loud) unsigned char buf[sizeof(Loud)];
    Loud* p = std::construct_at(reinterpret_cast<Loud*>(buf), "in-buffer");
    std::destroy_at(p);                                         // storage lives on, object is gone
}
```

Output order: `ctor temp`, `dtor temp`, `ctor extended`, ..., `ctor in-buffer`,
`dtor in-buffer`, and `dtor extended` last.

## Pitfalls

- `memcpy`/`memset` on a type with a `std::string` or a virtual function: undefined
  behaviour (the string's heap pointer is copied, the vptr overwritten). Check
  `std::is_trivially_copyable_v` in a `static_assert` next to every `memcpy`.
- Reading the bytes of a `float` via `*(uint32_t*)&f`: strict aliasing violation. Use
  `std::bit_cast` (C++20) or `memcpy`.
- `const T& r = obj.get_temp().member();` where `member()` returns a reference: no
  extension (the reference binds to the result of a function call, not to the
  temporary). Dangling.
- `std::string_view sv = std::string("x") + "y";` dangles immediately (the view is not a
  reference binding, nothing is extended).
- `is_implicit_lifetime` of an aggregate with a `std::string` member is **true**
  [S8 [class.prop]/9] - but that only allows the *aggregate object* to begin life
  implicitly; its `std::string` member still needs a constructor. Do not `malloc` it.
- After `std::destroy_at(p)` and a new `construct_at` in the same storage, the old
  pointer refers to the new object only if the old one was *transparently replaceable*
  [S8 [basic.life]/8]: same type, not a `const` complete object, not a
  potentially-overlapping subobject (e.g. a base or a `[[no_unique_address]]` member).
  Simplest rule: use the pointer `construct_at` returns (or `std::launder`).
- `std::start_lifetime_as` (C++23) is not in libc++ 21 [S13].

## Discussion questions

1. **What is the difference between "trivial" and "standard-layout"?** Trivial is about
   *behaviour* of the special members (bitwise, no user code); standard-layout is about
   *memory layout* (C-compatible, predictable member offsets). `struct { public: int a;
   private: int b; }` is trivial but not standard-layout; a struct with a user-provided
   destructor can be standard-layout but not trivially copyable.
2. **Why does `std::vector<Pod>` copy faster than `std::vector<Named>`?** For trivially
   copyable elements the library may use one `memmove` of the whole buffer; for
   `Named` it must call each element's copy constructor (one string allocation each).
3. **When does a temporary's lifetime get extended, and when not?** Extended: direct
   binding of a prvalue (or a member access on it) to a local `const&`/`&&`, and since
   C++23 the range-`for` initialiser. Not extended: through a function returning a
   reference, into a `string_view`/`span`, or when the reference is a function
   parameter (the temporary lives until the end of the calling full-expression only).
   Binding a temporary to a reference *member* in a mem-initialiser is ill-formed.
4. **`malloc` a `struct Pod { int id; double x; }` and write `p->id = 1`: defined behaviour?**
   Since C++20 yes: `Pod` is an implicit-lifetime type, and `malloc` implicitly creates
   one if that makes the program defined (P0593) [S8 [intro.object]]. Before C++20 it
   was technically undefined. For `Named` it is still undefined; use `new` or `construct_at`.
5. **What does `std::construct_at(p, args...)` do that `*p = T(args...)` does not?**
   It starts the lifetime of a new object in raw storage (placement new), while `*p = ...`
   calls assignment on an object that must already be alive. `std::vector` uses the
   former for `push_back` into spare capacity and `destroy_at` in `pop_back`.

## In the code

- `src/cpp/lifetime.cpp`: property table as `static_assert`s, including the `is_implicit_lifetime` surprise; a `Tracer` recording ctor/dtor order for scope exit, temporaries, lifetime extension through a member, P2718 range-for; `construct_at`/`destroy_at` in a byte buffer; `malloc` of an implicit-lifetime type. Passes under ASan + UBSan (`make sanitize`).
