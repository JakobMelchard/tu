// ranges.cpp -- iterator categories, a hand-written iterator, sentinels, lazy views,
// range adaptors, ranges::to and what this libc++ lacks (note 11).
#include <algorithm>
#include <deque>
#include <forward_list>
#include <functional>
#include <iterator>
#include <list>
#include <map>
#include <numeric>
#include <ranges>
#include <sstream>
#include <string>
#include <string_view>
#include <utility>
#include <vector>
#include "check.hpp"
#if defined(HAVE_GENERATOR)
#include <generator>
std::generator<long> fibonacci() { long a = 0, b = 1; for (;;) { co_yield a; a = std::exchange(b, a + b); } }
#endif

namespace rg = std::ranges;
namespace vw = std::views;

// --- the iterator hierarchy, as C++20 concepts [iterator.concepts]
static_assert(std::contiguous_iterator<std::vector<int>::iterator>);
static_assert(std::random_access_iterator<std::deque<int>::iterator> && !std::contiguous_iterator<std::deque<int>::iterator>);
static_assert(std::bidirectional_iterator<std::list<int>::iterator> && !std::random_access_iterator<std::list<int>::iterator>);
static_assert(std::forward_iterator<std::forward_list<int>::iterator> && !std::bidirectional_iterator<std::forward_list<int>::iterator>);
static_assert(std::input_iterator<std::istream_iterator<int>> && !std::forward_iterator<std::istream_iterator<int>>);

// --- a singly linked list with a hand-written forward iterator
template <class T> class SList {
    struct Node { T value; Node* next; };
    Node* head_ = nullptr;
public:
    SList(std::initializer_list<T> il) { for (auto it = std::rbegin(il); it != std::rend(il); ++it) head_ = new Node{*it, head_}; }
    SList(const SList&) = delete;
    SList& operator=(const SList&) = delete;
    ~SList() { while (head_) delete std::exchange(head_, head_->next); }

    template <bool Const> class Iter {
        using NodeP = std::conditional_t<Const, const Node*, Node*>;
        NodeP n_ = nullptr;
    public:
        using value_type = T;                           // the five names algorithms look for
        using difference_type = std::ptrdiff_t;
        using reference = std::conditional_t<Const, const T&, T&>;
        using pointer = std::conditional_t<Const, const T*, T*>;
        using iterator_category = std::forward_iterator_tag;
        Iter() = default;                               // forward iterators must be default-constructible
        explicit Iter(NodeP n) : n_(n) {}
        reference operator*() const { return n_->value; }
        pointer operator->() const { return &n_->value; }
        Iter& operator++() { n_ = n_->next; return *this; }
        Iter operator++(int) { Iter t = *this; ++*this; return t; }
        friend bool operator==(const Iter&, const Iter&) = default;
    };
    using iterator = Iter<false>;
    using const_iterator = Iter<true>;
    iterator begin() { return iterator{head_}; }
    iterator end() { return iterator{}; }
    const_iterator begin() const { return const_iterator{head_}; }
    const_iterator end() const { return const_iterator{}; }
};
static_assert(std::forward_iterator<SList<int>::iterator>);
static_assert(rg::forward_range<const SList<int>>);
static_assert(std::is_same_v<rg::range_reference_t<const SList<int>>, const int&>);

// --- a sentinel: end is a different type, checked by a predicate (C-string style)
struct Countdown {
    int from;
    struct It {
        int v;
        using value_type = int;
        using difference_type = std::ptrdiff_t;
        int operator*() const { return v; }
        It& operator++() { --v; return *this; }
        void operator++(int) { --v; }
        bool operator==(std::default_sentinel_t) const { return v == 0; }
    };
    It begin() const { return {from}; }
    std::default_sentinel_t end() const { return {}; }
};
static_assert(std::input_iterator<Countdown::It> && rg::input_range<Countdown>);
static_assert(!rg::common_range<Countdown>);

struct Particle { std::string name; double mass; };

int main() {
    SList<int> l{3, 1, 2};
    CHECK(std::accumulate(l.begin(), l.end(), 0) == 6);           // classic algorithm
    CHECK(rg::max(l) == 3 && rg::find(l, 1) != l.end());          // range algorithms
    for (int& x : l) x *= 10;                                      // range-for uses begin/end
    CHECK(*l.begin() == 30);

    int sum = 0;
    for (int x : Countdown{4}) sum += x;
    CHECK(sum == 10);

    // views are lazy: nothing runs until iteration, and each dereference re-runs the transform
    int calls = 0;
    auto squares = vw::iota(1) | vw::transform([&calls](int i) { ++calls; return i * i; })
                 | vw::filter([](int x) { return x % 2 == 1; }) | vw::take(3);
    CHECK(calls == 0);
    std::vector<int> odd;
    for (int x : squares) odd.push_back(x);
    CHECK((odd == std::vector{1, 9, 25}));
    CHECK(calls > 3);   // filter dereferences (transform runs) once to test, again to yield

    // projections: sort by a member without writing a comparator
    std::vector<Particle> ps{{"mu", 105.7}, {"e", 0.511}, {"tau", 1776.9}};
    rg::sort(ps, {}, &Particle::mass);
    CHECK(ps.front().name == "e");
    auto heavy = rg::find_if(ps, [](double m) { return m > 1000; }, &Particle::mass);
    CHECK(heavy->name == "tau");

    // calling an algorithm on a temporary container: the iterator would dangle, so the
    // library returns std::ranges::dangling instead (a compile error when dereferenced)
    auto r = rg::find(std::vector{1, 2, 3}, 2);
    static_assert(std::is_same_v<decltype(r), rg::dangling>);

    // split + transform: words of a string, lazily
    std::string_view text = "the quick brown fox";
    std::vector<std::size_t> lengths;
    for (auto w : text | vw::split(' ')) lengths.push_back(rg::distance(w));
    CHECK((lengths == std::vector<std::size_t>{3, 5, 5, 3}));

    // keys/values/reverse/drop on associative containers
    std::map<std::string, int> m{{"a", 1}, {"b", 2}, {"c", 3}};
#if defined(HAVE_FOLD)
    CHECK(rg::fold_left(m | vw::values, 0, std::plus{}) == 6);   // C++23 fold, no iterator pair
#else
    auto vals = m | vw::values;
    CHECK(std::accumulate(vals.begin(), vals.end(), 0) == 6);
#endif
    CHECK(*rg::begin(m | vw::keys | vw::reverse) == "c");

#if defined(HAVE_RANGES_TO)
    auto v = vw::iota(0, 5) | vw::transform([](int i) { return 2 * i; }) | rg::to<std::vector>();
    CHECK((v == std::vector{0, 2, 4, 6, 8}));
#else
    chk::skip("ranges::to", "P1206 missing");
#endif
#if defined(HAVE_ZIP)
    std::vector<double> xs{1, 2, 3}, ws{0.5, 0.25, 0.25};
    double weighted = 0;
    for (auto [x, w] : vw::zip(xs, ws)) weighted += x * w;
    CHECK(weighted == 1.75);
#else
    chk::skip("views::zip", "P2321 missing");
#endif
#if defined(HAVE_ENUMERATE)
    for (auto [i, x] : vw::enumerate(odd)) CHECK(odd[static_cast<std::size_t>(i)] == x);
#else
    chk::skip("views::enumerate", "P2164 not in this libc++; use zip(iota(0), r)");
#endif
#if defined(HAVE_CHUNK)
    CHECK(rg::distance(odd | vw::chunk(2)) == 2);
#else
    chk::skip("views::chunk / views::slide", "P2442 not in this libc++");
#endif
#if defined(HAVE_STRIDE)
    CHECK(rg::distance(odd | vw::stride(2)) == 2);
#else
    chk::skip("views::stride", "P1899 not in this libc++");
#endif
#if defined(HAVE_GENERATOR)
    CHECK(*rg::next(fibonacci().begin(), 20) == 6765);
#else
    chk::skip("std::generator", "P2502 not in this libc++ (header <generator> missing)");
#endif
    return chk::report("ranges");
}
