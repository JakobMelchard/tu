# 08 Operator overloading: arithmetic types, <=>, hidden friends, ADL

For a physicist the reason to overload operators is to write `F = q * (E + cross(v, B))`
for a `vec3`. The C++ questions are which operators to write, as members or not, and
what C++20's `<=>` generates for you. No dedicated 2021W item; operators appear in the
iterator item 014 and in hand-out ex2.2's `SpaceVector` [S3] [S4]. C.160-C.168 [S10].

Code: `src/cpp/operators.cpp` (a `vec3` with `<=>`, a `Rational` with a custom
strong ordering, a `std::formatter`).

## Definitions [S8 [over.oper], [class.spaceship]]

- An overloaded operator is a function named `operator@`. At least one operand must be
  a class or enum type. Precedence, associativity and arity cannot change;
  `&&`/`||`/`,` lose short-circuit/sequencing when overloaded (do not).
- **Member or non-member?** Members: `=`, `[]`, `()`, `->`, compound assignment `+=`
  (modify `*this`). Non-members (usually **hidden friends**): symmetric binary operators
  `+ - * / == <=>` so that conversions apply to **both** operands (`2.0 * v` and `v * 2.0`,
  C.161).
- **Hidden friend**: a `friend` function *defined* inside the class. It is not visible
  to ordinary lookup, only to **ADL**, so it is considered only when an argument has
  that class type: fewer candidates, faster compiles, no accidental conversions.
- **ADL** (argument-dependent lookup): for an unqualified call `f(a)`, the compiler also
  searches the namespaces (and hidden friends) of the arguments' types. That is how
  `std::cout << x` finds `std::operator<<` and how `cross(a, b)` finds `phys::cross`.
- **`operator<=>`** (C++20): returns `std::strong_ordering` (substitutable equality:
  `int`, `Rational`), `std::weak_ordering` (equivalent but distinguishable:
  case-insensitive strings) or `std::partial_ordering` (some pairs unordered:
  `double` with NaN). `= default` compares members lexicographically in declaration
  order; the category is the weakest of the members'.
- **Rewritten candidates**: from `==` the compiler derives `!=`; from `<=>` it derives
  `< > <= >=`, and both are tried with reversed operands (`1 == r` uses `r == 1`).
  Defaulting `<=>` also implicitly defaults `==`; a hand-written `<=>` does **not**
  provide `==` (write or default it separately: `==` can be cheaper, e.g. size check first).
- Canonical forms: `T& operator+=(const T&)` returns `*this`; `T operator+(T a, const T& b)
  { a += b; return a; }`; prefix `T& operator++()`, postfix `T operator++(int)`;
  `operator[]` with const and non-const overload (or one deducing-`this` template, C++23);
  C++23 allows multiple arguments: `m[i, j]`.

## Complete example

```cpp
// complete example: operators
#include <cmath>
#include <compare>
#include <cstdio>
#include <limits>

namespace phys {
struct vec3 {
    double x = 0, y = 0, z = 0;
    vec3& operator+=(const vec3& o) { x += o.x; y += o.y; z += o.z; return *this; }
    vec3& operator*=(double s) { x *= s; y *= s; z *= s; return *this; }
    friend vec3 operator+(vec3 a, const vec3& b) { a += b; return a; }
    friend vec3 operator*(vec3 a, double s) { a *= s; return a; }
    friend vec3 operator*(double s, vec3 a) { a *= s; return a; }
    friend double dot(const vec3& a, const vec3& b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
    friend vec3 cross(const vec3& a, const vec3& b) {
        return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
    }
    friend auto operator<=>(const vec3&, const vec3&) = default;   // lexicographic, partial_ordering
};
}  // namespace phys

int main() {
    using phys::vec3;
    const double q = -1.0;
    vec3 E{0, 0, 1}, B{0, 0, 2}, v{1, 0, 0};
    vec3 F = q * (E + cross(v, B));                                // Lorentz force, ADL finds cross
    std::printf("F = (%g, %g, %g)\n", F.x, F.y, F.z);              // (-0, 2, -1)
    std::printf("E == E: %d, v < E: %d\n", E == E, v < E);         // 1, 0 (x decides: 1 > 0)
    vec3 n{std::numeric_limits<double>::quiet_NaN()};
    std::printf("NaN unordered: %d\n", (n <=> v) == std::partial_ordering::unordered);   // 1
}
```

## Pitfalls

- `return a += b;` in a by-value `operator+` returns `T&`, so the result is **copied**
  (not moved). Harmless for a `vec3`, a full allocation for a matrix; caught by a test
  in `matrix/tests/test_matrix.cpp` (note 05).
- Defaulted `<=>` on floating members gives `partial_ordering`; `std::sort` and
  `std::set` need a strict weak order, so NaNs break them silently.
- A defaulted `<=>` over a `std::vector<double>` member compares lexicographically:
  rarely what "less" should mean for a physical vector. Consider not providing `<` at all.
- `operator==` as a member taking `const T&` with an implicit converting constructor:
  `1 == r` fails in C++17 (the left operand is not converted), works in C++20 through
  reversed candidates. Hidden friends avoid the asymmetry in every standard.
- `operator<<` for streams must be a non-member (the left operand is `std::ostream`).
  For `std::format`, specialise `std::formatter<T>` (reuse `formatter<double>` for the spec).
- Overloading `&&`, `||`, `,`, unary `&`: loses built-in semantics, surprises readers.
- Operators with surprising meaning (`+` for set union is fine, `^` for power is not:
  its precedence is lower than `+`).

## Discussion questions

1. **Why implement `operator+` in terms of `operator+=` and not the other way round?**
   `+=` modifies in place (no temporary, can reuse capacity); `+` then needs one copy
   (taken by the by-value parameter, which also lets rvalue left operands be moved in).
   Implementing `+=` via `+` would create a temporary every time.
2. **What does `friend auto operator<=>(const T&, const T&) = default;` give you?**
   All six comparisons: `==`/`!=` (defaulted `==` is implied), `< > <= >=` via
   rewriting; memberwise lexicographic in declaration order; return category = weakest
   member category; `constexpr` and `noexcept` if the members' are.
3. **What is ADL and where do you rely on it daily?** Unqualified function calls also
   search the namespaces associated with the argument types. `std::cout << x`,
   `swap(a, b)` after `using std::swap;`, `begin(r)`, and hidden friends only work
   because of it.
4. **Why hidden friends instead of free functions in the namespace?** They are found
   only via ADL when an operand has the class type, so they do not pollute overload
   resolution for unrelated types (faster compiles, better error messages), and
   implicit conversions apply to both operands symmetrically.
5. **Your `Rational` stores `p/q` normalised. Which ordering category, and how is `<=>` written?**
   `std::strong_ordering`: equal rationals are indistinguishable after normalisation.
   With `q > 0`: `return a.p * b.q <=> b.p * a.q;` (overflow aside). `==` can stay
   defaulted on the normalised members.

## In the code

- `src/cpp/operators.cpp`: `phys::vec3` with compound + binary hidden friends, `cross`/`dot` via ADL, defaulted `<=>` checked to be `partial_ordering`, NaN unordered, `std::set<vec3>`, `operator[]` via deducing `this` (fallback to two overloads when unsupported), `operator<<`, a `std::formatter<vec3>` honouring `{:.2f}`; `Rational` with `strong_ordering` and implicit conversion from `long` on both sides.
- `src/cpp/matrix/include/la/matrix.hpp`: `m[i, j]` (C++23 multidimensional subscript) and `m(i, j)`.
