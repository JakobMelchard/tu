// test_matrix.cpp -- tests for la/matrix.hpp: algebraic identities, genericity over
// scalar and range types, error handling, compile-time evaluation (note 13).
#include <complex>
#include <format>
#include <list>
#include <ranges>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>
#include "check.hpp"
#include "la/matrix.hpp"

using la::Matrix;
using cplx = std::complex<double>;

// the concept accepts numbers, rejects things that merely look additive
static_assert(la::Scalar<int> && la::Scalar<double> && la::Scalar<cplx>);
static_assert(!la::Scalar<std::string> && !la::Scalar<void*>);
// rule of zero: the compiler-generated members are right, and noexcept where it matters
static_assert(std::is_nothrow_move_constructible_v<Matrix<double>> && std::is_copy_constructible_v<Matrix<double>>);

// constexpr all the way: a product and its trace evaluated by the compiler
constexpr int trace_of_square() {
    Matrix<int> a{{1, 2}, {3, 4}};
    return la::trace(a * a);            // [[7,10],[15,22]] -> 29
}
static_assert(trace_of_square() == 29);

int main() {
    Matrix a{{1, 2, 3}, {4, 5, 6}};     // CTAD: Matrix<int>
    static_assert(std::is_same_v<decltype(a), Matrix<int>>);
    Matrix<int> b{{1, 0}, {0, 1}, {2, -1}};
    Matrix<int> c{{2, 1}, {1, 3}};

    CHECK(a.rows() == 2 && a.cols() == 3);
    CHECK((a * b == Matrix<int>{{7, -1}, {16, -1}}));
    CHECK((a * b) * c == a * (b * c));                                   // associativity (exact in int)
    CHECK(transpose(transpose(a)) == a);
    CHECK(transpose(a * b) == transpose(b) * transpose(a));
    CHECK(Matrix<int>::identity(2) * c == c && c * Matrix<int>::identity(2) == c);
    CHECK((2 * c - c == c) && (-c + c == Matrix<int>(2, 2)));

    // element access: C++23 m[i, j], C++20 m(i, j), checked at()
#if __cpp_multidimensional_subscript >= 202110L
    CHECK((a[1, 2] == 6));
#endif
    CHECK(a(0, 1) == 2);
    bool threw = false;
    try { (void)a.at(2, 0); } catch (const std::out_of_range&) { threw = true; }
    CHECK(threw);

    // rows are spans, columns are lazy views: ranges algorithms apply directly
    CHECK(std::ranges::fold_left(a.row(1), 0, std::plus{}) == 15);
    CHECK(std::ranges::fold_left(a.col(2), 0, std::plus{}) == 9);
    CHECK(std::ranges::max(a.flat()) == 6);

    // matvec accepts any sized range whose elements convert to the scalar
    Matrix<double> r{{0, -1}, {1, 0}};                                   // rotation by 90 degrees
    CHECK((la::matvec(r, std::vector{1.0, 0.0}) == std::vector{0.0, 1.0}));
    CHECK((la::matvec(r, std::list{0.0, 1.0}) == std::vector{-1.0, 0.0}));
    CHECK((la::matvec(r, std::views::iota(1, 3)) == std::vector{-2.0, 1.0}));   // ints -> double

    // complex scalars: Pauli matrices, sigma_x sigma_y = i sigma_z, [sx, sy] = 2i sz
    const cplx i{0, 1};
    Matrix<cplx> sx{{0, 1}, {1, 0}}, sy{{0, -i}, {i, 0}}, sz{{1, 0}, {0, -1}};
    CHECK(sx * sy == i * sz);
    CHECK(sx * sy - sy * sx == cplx{0, 2} * sz);
    CHECK(sx * sx == Matrix<cplx>::identity(2));
    CHECK(la::trace(sz) == cplx{0});

    // errors: exceptions for violated preconditions ...
    threw = false;
    try { (void)(a * a); } catch (const std::invalid_argument&) { threw = true; }
    CHECK(threw);
    threw = false;
    try { Matrix<int> bad{{1, 2}, {3}}; } catch (const std::invalid_argument&) { threw = true; }
    CHECK(threw);
#if __cpp_lib_expected >= 202202L
    // ... std::expected where a mismatch is a normal outcome the caller must handle
    auto ok = la::try_multiply(a, b);
    auto bad = la::try_multiply(a, a);
    CHECK(ok.has_value() && *ok == a * b);
    CHECK(!bad && bad.error() == la::Error::dimension_mismatch);
#endif

    // value semantics: an rvalue left operand is reused, no new allocation
    Matrix<double> big(100, 100, 1.0), other(100, 100, 2.0);
    const double* storage = big.flat().data();
    Matrix<double> sum = std::move(big) + other;
    CHECK(sum.flat().data() == storage && sum(99, 99) == 3.0);

#if __cpp_lib_mdspan >= 202207L
    auto md = c.md();                     // a std::mdspan over the same storage
    md[0, 1] = 5;
    CHECK(c(0, 1) == 5 && md.extent(0) == 2);
#endif
    CHECK(std::format("{}", Matrix<int>::identity(2)) == "[[1, 0], [0, 1]]");
    CHECK(std::format("{:.1f}", Matrix<double>{{0.25, 1}}) == "[[0.2, 1.0]]");
    return chk::report("matrix");
}
