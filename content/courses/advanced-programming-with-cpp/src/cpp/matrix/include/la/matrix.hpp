// la/matrix.hpp -- a header-only dense matrix, written as the kind of library hand-in
// 360.251 asks for (note 13, src/README.md). Shows: a Scalar concept, rule of zero,
// C++23 multidimensional operator[], spans and views instead of raw loops over indices,
// std::expected for recoverable errors, exceptions for contract violations, constexpr
// (the whole class works in constant evaluation), and std::format support.
#pragma once
#include <algorithm>
#include <cmath>
#include <concepts>
#include <cstddef>
#include <format>
#include <initializer_list>
#include <ranges>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>
#if __has_include(<expected>)
#include <expected>
#endif
#if __has_include(<mdspan>)
#include <mdspan>
#endif

namespace la {

// What the algorithms below need from an element type: a (skew-)field-like value type.
template <class T>
concept Scalar = std::regular<T> && requires(T a, T b) {
    { a + b } -> std::convertible_to<T>;
    { a - b } -> std::convertible_to<T>;
    { a * b } -> std::convertible_to<T>;
    { -a } -> std::convertible_to<T>;
    T{0};
    T{1};
};

enum class Error { dimension_mismatch };

template <Scalar T>
class Matrix {
    std::size_t rows_ = 0, cols_ = 0;
    std::vector<T> data_;   // row-major; the vector owns the memory: rule of zero

public:
    using value_type = T;
    using size_type = std::size_t;

    constexpr Matrix() = default;
    constexpr Matrix(size_type rows, size_type cols, const T& init = T{0})
        : rows_(rows), cols_(cols), data_(rows * cols, init) {}
    constexpr Matrix(std::initializer_list<std::initializer_list<T>> rows)
        : rows_(rows.size()), cols_(rows.size() ? rows.begin()->size() : 0) {
        data_.reserve(rows_ * cols_);
        for (const auto& r : rows) {
            if (r.size() != cols_) throw std::invalid_argument("la::Matrix: ragged initializer");
            data_.insert(data_.end(), r.begin(), r.end());
        }
    }
    static constexpr Matrix identity(size_type n) {
        Matrix m(n, n);
        for (size_type i = 0; i < n; ++i) m(i, i) = T{1};
        return m;
    }

    constexpr size_type rows() const noexcept { return rows_; }
    constexpr size_type cols() const noexcept { return cols_; }

    // unchecked access; operator() for C++20 callers, operator[] with two indices in C++23
    constexpr T& operator()(size_type i, size_type j) { return data_[i * cols_ + j]; }
    constexpr const T& operator()(size_type i, size_type j) const { return data_[i * cols_ + j]; }
#if __cpp_multidimensional_subscript >= 202110L
    constexpr T& operator[](size_type i, size_type j) { return (*this)(i, j); }
    constexpr const T& operator[](size_type i, size_type j) const { return (*this)(i, j); }
#endif
    constexpr const T& at(size_type i, size_type j) const {    // checked access
        if (i >= rows_ || j >= cols_) throw std::out_of_range("la::Matrix::at");
        return (*this)(i, j);
    }

    // views: no copies, no index arithmetic at the call site
    constexpr std::span<T> row(size_type i) { return std::span(data_).subspan(i * cols_, cols_); }
    constexpr std::span<const T> row(size_type i) const { return std::span(data_).subspan(i * cols_, cols_); }
    constexpr auto col(size_type j) const {
        return std::views::iota(size_type{0}, rows_)
             | std::views::transform([this, j](size_type i) -> const T& { return (*this)(i, j); });
    }
    constexpr std::span<T> flat() noexcept { return data_; }
    constexpr std::span<const T> flat() const noexcept { return data_; }
#if __cpp_lib_mdspan >= 202207L
    auto md() { return std::mdspan(data_.data(), rows_, cols_); }
    auto md() const { return std::mdspan(data_.data(), rows_, cols_); }
#endif

    friend constexpr bool operator==(const Matrix&, const Matrix&) = default;

    constexpr Matrix& operator+=(const Matrix& o) { require_same_shape(o); std::ranges::transform(data_, o.data_, data_.begin(), std::plus{}); return *this; }
    constexpr Matrix& operator-=(const Matrix& o) { require_same_shape(o); std::ranges::transform(data_, o.data_, data_.begin(), std::minus{}); return *this; }
    constexpr Matrix& operator*=(const T& s) { for (T& x : data_) x = x * s; return *this; }

    // by-value left operand: `std::move(a) + b` reuses a's storage (note 05).
    // NOT `return a += b;`: that returns a Matrix&, an lvalue, so it is COPIED into
    // the result; only `return a;` (a plain name) is moved implicitly.
    friend constexpr Matrix operator+(Matrix a, const Matrix& b) { a += b; return a; }
    friend constexpr Matrix operator-(Matrix a, const Matrix& b) { a -= b; return a; }
    friend constexpr Matrix operator*(Matrix a, const T& s) { a *= s; return a; }
    friend constexpr Matrix operator*(const T& s, Matrix a) { a *= s; return a; }
    friend constexpr Matrix operator-(Matrix a) { for (T& x : a.data_) x = -x; return a; }

    // i-k-j loop: the inner loop runs over contiguous rows of both b and the result
    friend constexpr Matrix operator*(const Matrix& a, const Matrix& b) {
        if (a.cols_ != b.rows_) throw std::invalid_argument("la::Matrix: inner dimensions differ");
        Matrix c(a.rows_, b.cols_);
        for (size_type i = 0; i < a.rows_; ++i)
            for (size_type k = 0; k < a.cols_; ++k) {
                const T aik = a(i, k);
                auto crow = c.row(i);
                auto brow = b.row(k);
                for (size_type j = 0; j < b.cols_; ++j) crow[j] = crow[j] + aik * brow[j];
            }
        return c;
    }

private:
    constexpr void require_same_shape(const Matrix& o) const {
        if (rows_ != o.rows_ || cols_ != o.cols_) throw std::invalid_argument("la::Matrix: shapes differ");
    }
};

// CTAD from a nested braced list works through the initializer_list constructor:
// Matrix m{{1.0, 2.0}, {3.0, 4.0}};  // Matrix<double>

template <Scalar T> constexpr Matrix<T> transpose(const Matrix<T>& a) {
    Matrix<T> t(a.cols(), a.rows());
    for (std::size_t i = 0; i < a.rows(); ++i)
        for (std::size_t j = 0; j < a.cols(); ++j) t(j, i) = a(i, j);
    return t;
}

template <Scalar T> constexpr T trace(const Matrix<T>& a) {
    T s{0};
    for (std::size_t i = 0; i < std::min(a.rows(), a.cols()); ++i) s = s + a(i, i);
    return s;
}

// A * x for ANY sized input range of scalars (vector, list, a view ...)
template <Scalar T, std::ranges::sized_range R>
    requires std::convertible_to<std::ranges::range_reference_t<R>, T>
constexpr std::vector<T> matvec(const Matrix<T>& a, R&& x) {
    if (std::ranges::size(x) != a.cols()) throw std::invalid_argument("la::matvec: size mismatch");
    std::vector<T> y(a.rows(), T{0});
    for (std::size_t i = 0; i < a.rows(); ++i) {
        auto xi = std::ranges::begin(x);
        for (const T& aij : a.row(i)) y[i] = y[i] + aij * static_cast<T>(*xi++);
    }
    return y;
}

#if __cpp_lib_expected >= 202202L
// the non-throwing variant: a dimension mismatch is an expected outcome here, not a bug
template <Scalar T> constexpr std::expected<Matrix<T>, Error> try_multiply(const Matrix<T>& a, const Matrix<T>& b) {
    if (a.cols() != b.rows()) return std::unexpected(Error::dimension_mismatch);
    return a * b;
}
#endif

}  // namespace la

// std::format("{}", m) -> "[[1, 2], [3, 4]]"; the element format spec is forwarded
template <la::Scalar T, class CharT>
struct std::formatter<la::Matrix<T>, CharT> : std::formatter<T, CharT> {
    template <class Ctx> auto format(const la::Matrix<T>& m, Ctx& ctx) const {
        auto out = ctx.out();
        *out++ = '[';
        for (std::size_t i = 0; i < m.rows(); ++i) {
            if (i) { *out++ = ','; *out++ = ' '; }
            *out++ = '[';
            for (std::size_t j = 0; j < m.cols(); ++j) {
                if (j) { *out++ = ','; *out++ = ' '; }
                ctx.advance_to(out);
                out = std::formatter<T, CharT>::format(m(i, j), ctx);
            }
            *out++ = ']';
        }
        *out++ = ']';
        return out;
    }
};
