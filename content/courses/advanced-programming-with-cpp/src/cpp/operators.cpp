// operators.cpp -- operator overloading: a vec3 with <=>, hidden friends, ADL,
// a rational with a hand-written strong ordering, and std::format support (note 08).
#include <cmath>
#include <compare>
#include <format>
#include <limits>
#include <numeric>
#include <set>
#include <sstream>
#include <type_traits>
#include "check.hpp"

namespace phys {
struct vec3 {
    double x = 0, y = 0, z = 0;

    // compound assignment as members, returning *this by reference
    vec3& operator+=(const vec3& o) { x += o.x; y += o.y; z += o.z; return *this; }
    vec3& operator*=(double s) { x *= s; y *= s; z *= s; return *this; }

    // binary operators as hidden friends: found only by ADL, symmetric conversions,
    // and they do not pollute overload sets for unrelated types
    friend vec3 operator+(vec3 a, const vec3& b) { return a += b; }
    friend vec3 operator-(const vec3& a) { return {-a.x, -a.y, -a.z}; }
    friend vec3 operator-(vec3 a, const vec3& b) { return a += -b; }
    friend vec3 operator*(vec3 a, double s) { return a *= s; }
    friend vec3 operator*(double s, vec3 a) { return a *= s; }   // 2.0 * v needs a non-member
    friend double dot(const vec3& a, const vec3& b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
    friend vec3 cross(const vec3& a, const vec3& b) {
        return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x};
    }

    // one defaulted <=> gives <, <=, >, >= (lexicographic x, y, z); == must be defaulted
    // separately if <=> is not defaulted -- here both are defaulted
    friend auto operator<=>(const vec3&, const vec3&) = default;
    friend bool operator==(const vec3&, const vec3&) = default;

    // index access; C++23 deducing this gives the const and non-const versions at once
#if defined(HAVE_DEDUCING_THIS)
    auto&& operator[](this auto&& self, int i) { return i == 0 ? self.x : i == 1 ? self.y : self.z; }
#else
    double& operator[](int i) { return i == 0 ? x : i == 1 ? y : z; }
    const double& operator[](int i) const { return i == 0 ? x : i == 1 ? y : z; }
#endif
    friend std::ostream& operator<<(std::ostream& os, const vec3& v) {
        return os << '(' << v.x << ", " << v.y << ", " << v.z << ')';
    }
};
double norm(const vec3& v) { return std::sqrt(dot(v, v)); }   // ordinary free function in the namespace
}  // namespace phys

// std::format support: specialise std::formatter, reuse the double formatter for the spec
template <> struct std::formatter<phys::vec3> : std::formatter<double> {
    auto format(const phys::vec3& v, std::format_context& ctx) const {
        auto out = std::format_to(ctx.out(), "(");
        out = std::formatter<double>::format(v.x, ctx);
        out = std::format_to(out, ", ");
        out = std::formatter<double>::format(v.y, ctx);
        out = std::format_to(out, ", ");
        out = std::formatter<double>::format(v.z, ctx);
        return std::format_to(out, ")");
    }
};

// a rational: == on normalised members, <=> hand-written, strong ordering
class Rational {
    long p_, q_;
public:
    constexpr Rational(long p, long q = 1) : p_(p), q_(q) {        // implicit from long: 1 + r works
        long g = std::gcd(p_, q_);
        if (q_ < 0) g = -g;
        p_ /= g; q_ /= g;
    }
    constexpr long num() const { return p_; }
    constexpr long den() const { return q_; }
    friend constexpr bool operator==(const Rational&, const Rational&) = default;
    friend constexpr std::strong_ordering operator<=>(const Rational& a, const Rational& b) {
        return a.p_ * b.q_ <=> b.p_ * a.q_;                  // q > 0 after normalisation
    }
    friend constexpr Rational operator+(const Rational& a, const Rational& b) {
        return {a.p_ * b.q_ + b.p_ * a.q_, a.q_ * b.q_};
    }
};
static_assert(Rational(1, 2) == Rational(2, 4));
static_assert(Rational(1, 3) < Rational(1, 2));
static_assert(1 + Rational(1, 2) == Rational(3, 2));        // hidden friend + implicit conversion of 1
static_assert(Rational(1, 2) + 1 == Rational(6, 4));        // symmetric: works both ways
static_assert(Rational(-1, -2) == Rational(1, 2));

int main() {
    using phys::vec3;
    vec3 a{1, 0, 0}, b{0, 1, 0};
    CHECK(cross(a, b) == (vec3{0, 0, 1}));              // cross found by ADL (no phys::)
    CHECK(dot(a + b, a - b) == 0.0);
    CHECK(2.0 * a == a * 2.0);
    CHECK(norm(vec3{3, 4, 0}) == 5.0);
    CHECK(a != b);                                      // != rewritten from ==

    // defaulted <=> over doubles yields partial_ordering: NaN is unordered
    static_assert(std::is_same_v<decltype(a <=> b), std::partial_ordering>);
    CHECK(b < a);                                       // lexicographic: 0 < 1 in x
    vec3 n{std::numeric_limits<double>::quiet_NaN(), 0, 0};
    CHECK((n <=> a) == std::partial_ordering::unordered);
    CHECK(!(n < a) && !(n > a) && !(n == n));

    // ordered containers need a strict weak order: fine for vec3 without NaNs
    std::set<vec3> s{a, b, a};
    CHECK(s.size() == 2);

    vec3 c = a;
    c[1] = 5;
    const vec3& cc = c;
    CHECK(cc[1] == 5.0);

    std::ostringstream os;
    os << b;
    CHECK(os.str() == "(0, 1, 0)");
    CHECK(std::format("{:.2f}", vec3{1, 2.5, -3}) == "(1.00, 2.50, -3.00)");
    return chk::report("operators");
}
