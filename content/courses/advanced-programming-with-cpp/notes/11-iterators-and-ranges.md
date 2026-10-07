# 11 Iterators and ranges: categories, custom iterators, views, adaptors, ranges::to

Iterators are the glue between containers and algorithms; C++20 ranges put concepts on
them and add lazy, composable **views**. 2021W: item 014 (iterators), hand-outs ex2.3
(rewrite loops with `<algorithm>`) and ex3.1 (a standard-conforming bidirectional
iterator for a list) [S3] [S4]. Ranges are new since then: this part is from the
standard [S8] and tested on this Mac [S13].

Code: `src/cpp/ranges.cpp`.

## Definitions [S8 [iterator.concepts], [range.adaptors], [range.utility.conv]]

**Iterator categories** (each refines the previous):

| concept | adds | example |
|---|---|---|
| `input_iterator` | `*it`, `++it`; single pass | `istream_iterator` |
| `forward_iterator` | multi-pass, default-constructible, `==` | `forward_list`, `unordered_map` |
| `bidirectional_iterator` | `--it` | `list`, `map`, `set` |
| `random_access_iterator` | `it + n`, `it[n]`, `<`, `it2 - it1` in O(1) | `deque` |
| `contiguous_iterator` | elements adjacent in memory (`std::to_address`) | `vector`, `array`, `string`, `span` |

The category decides which algorithms apply and at what cost: `std::sort` needs random
access; `std::ranges::distance` is O(1) or O(n); `std::list` has its own `sort`.

- **Writing an iterator**: provide `value_type`, `difference_type` (and for classic
  algorithms `reference`, `pointer`, `iterator_category`), `operator*`, `operator->`,
  prefix and postfix `++` (and `--` for bidirectional), `==`. Verify with
  `static_assert(std::bidirectional_iterator<It>)` instead of waiting for a template
  error deep in `<algorithm>`. A `const_iterator` must yield `const T&`.
- **Range**: anything with `begin(r)` and `end(r)`. **Sentinel**: `end` may have a
  different type than `begin` (a null terminator, a count, `std::default_sentinel_t`);
  classic algorithms require equal types (`common_range`), `std::ranges::` algorithms
  do not.
- **View**: a range that is cheap to copy/move and usually **lazy**: `views::filter`,
  `transform`, `take`, `drop`, `reverse`, `iota`, `keys`, `values`, `split`, `join`,
  `zip`. Composed with `|`. Nothing is computed until iteration, and elements are
  recomputed on every dereference.
- **Projections**: `std::ranges::sort(ps, {}, &Particle::mass)` sorts by a member
  without a comparator lambda.
- **Dangling protection**: `std::ranges::find(std::vector{1, 2}, 2)` returns
  `std::ranges::dangling` (a compile error on use) because the iterator would point
  into a destroyed temporary.
- **`std::ranges::to<C>()`** (C++23): materialise a view into a container.

## C++23 range features on this Mac [S12] [S13]

| feature | paper | Apple clang 21 / libc++ 21 |
|---|---|---|
| `ranges::to` | P1206 | yes |
| `views::zip` | P2321 | **yes, but `__cpp_lib_ranges_zip` undefined** (probe) |
| `ranges::fold_left` etc. | P2322 | **yes, `__cpp_lib_ranges_fold` undefined** (probe) |
| `views::join_with`, `chunk_by`, `repeat` | P2441, P2443, P2474 | macros defined (not exercised here) |
| `views::enumerate` | P2164 | **no** (libc++ 23) |
| `views::chunk`, `views::slide` | P2442 | **no** |
| `views::stride` | P1899 | **no** (libc++ 23) |
| `views::cartesian_product` | P2374 | **no** |
| `views::as_const`, `cbegin` fixes | P2278 | **no** |
| `std::generator` (coroutine range) | P2502 | **no** (`<generator>` missing) |

Guard these with the probe flags (`HAVE_ZIP`, ...), not with `__cpp_lib_*` macros:
the macros under-report.

## Complete example

```cpp
// complete example: ranges
#include <algorithm>
#include <cstdio>
#include <functional>
#include <map>
#include <ranges>
#include <string>
#include <vector>

struct Particle { std::string name; double mass; };   // MeV

int main() {
    namespace vw = std::views;
    std::vector<Particle> ps{{"mu", 105.66}, {"e", 0.511}, {"tau", 1776.9}, {"p", 938.27}};
    std::ranges::sort(ps, {}, &Particle::mass);                  // projection
    auto heavy_names = ps | vw::filter([](const Particle& p) { return p.mass > 100; })
                          | vw::transform(&Particle::name);      // lazy: nothing ran yet
    for (const auto& n : heavy_names) std::printf("%s ", n.c_str());   // mu p tau
    std::puts("");

    auto squares = vw::iota(1) | vw::transform([](int i) { return i * i; }) | vw::take(5)
                 | std::ranges::to<std::vector>();               // C++23
    std::printf("last square %d\n", squares.back());             // 25

    std::vector<double> x{1, 2, 3}, w{0.5, 0.25, 0.25};
    double mean = 0;
    for (auto [xi, wi] : vw::zip(x, w)) mean += xi * wi;         // C++23, present in libc++ 21
    std::map<std::string, int> counts{{"a", 1}, {"b", 2}};
    int total = std::ranges::fold_left(counts | vw::values, 0, std::plus{});
    std::printf("weighted mean %.2f, total %d\n", mean, total);  // 1.75, 3
}
```

## Pitfalls

- **Iterator invalidation** (note 04) applies to views too: a view over a vector
  dangles after the vector reallocates.
- `views::filter` caches its `begin()` on first call: iterating a `const` filter view
  does not compile, and modifying elements so that the predicate changes is UB-adjacent
  ("the predicate must stay satisfied"). Pass views by value or `auto&&`, not `const&`.
- Laziness recomputes: `transform` then `filter` calls the transform twice per yielded
  element (`ranges.cpp` counts it). Materialise with `ranges::to` if it is expensive.
- A view must not outlive the container it refers to; returning `v | vw::filter(...)`
  for a local `v` dangles (the view holds a reference). `std::views::owning_view` exists
  for rvalue containers.
- Classic algorithms need `begin` and `end` of the same type; a sentinel-based range
  needs `std::ranges::` algorithms or `views::common`.
- Custom iterator missing `difference_type`, a default constructor, or a postfix `++`:
  not a `forward_iterator`; `static_assert` it.
- Erasing while iterating: use the returned iterator (`it = v.erase(it)`) or
  `std::erase_if(v, pred)` (C++20).

## Discussion questions

1. **What does `std::sort` require from its iterators, and why can't you `std::sort` a `std::list`?**
   Random access (it indexes and computes distances in O(1)). `list` iterators are
   bidirectional; use `list::sort`, a merge sort that relinks nodes without moving elements.
2. **What must a bidirectional iterator for your list provide to work with `<algorithm>`?**
   The five member types, `*`, `->`, pre/post `++` and `--`, `==` (and `!=` rewritten),
   default construction, and a `const` variant yielding `const T&`; `end()` must be
   decrementable to the last element (a sentinel node makes that easy, as in ex3.1 [S4]).
3. **Loop or algorithm?** Algorithms name the intent (`count_if`, `transform`,
   `accumulate`), cannot have off-by-one errors, work on any container of the right
   category, and can take an execution policy (note 14). Loops are clearer for
   multi-step logic with early exits. ex2.3 asked for this trade-off [S4].
4. **What does "views are lazy" mean in practice?** A pipeline builds an object
   describing the computation; each element is produced when the consumer dereferences.
   Infinite ranges (`iota(1)`) work with `take`; side effects in the lambdas happen at
   iteration time, possibly more than once.
5. **Why does `ranges::find(std::vector{...}, x)` return `dangling`?** The argument is
   an rvalue (a temporary vector) that dies at the end of the full-expression; an
   iterator into it would dangle, so the library returns a type you cannot dereference.
   Only borrowed ranges (`span`, `string_view`, lvalue containers) return real iterators.

## In the code

- `src/cpp/ranges.cpp`: the category hierarchy as `static_assert`s; `SList` with a templated const/non-const forward iterator verified by concepts and used with classic and range algorithms; `Countdown` with `default_sentinel_t`; laziness counted; projections; `dangling`; `split`; `keys`/`values`/`reverse`; `ranges::to`, `zip`, `fold_left` behind probe flags; SKIP lines for `enumerate`, `chunk`, `stride`, `generator`.
- `src/cpp/matrix/include/la/matrix.hpp`: `row(i)` is a `std::span`, `col(j)` a `iota | transform` view.
