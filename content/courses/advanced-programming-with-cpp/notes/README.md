# 360.251 Advanced Programming with C++ - notes

Preparation for a course **offered in winter semesters**. The 2027W TISS page is **not
published**; the facts below are the 2026W page [S1]. One note per topic of the
TISS "Subject of course" list, in TISS order [S1]. Each note: definitions, a complete
example that compiles and runs (all 14 were compiled with the flags below and run on
2026-09-28), pitfalls, five discussion-style questions with answers, pointers into
[`../src`](../src/README.md). Reader: physics master's, C and Python background; C++
syntax basics assumed, C++ semantics not.

Every claim carries an `[S<n>]` citation into [`../refs/SOURCES.md`](../refs/SOURCES.md);
changes are in `CHANGELOG.md`.

**Course status, 2026W pattern** [S1]: Thu 09:00-11:00, EI 1 Petritsch HS, hybrid;
registration 01.09-04.10, deregistration until 01.11; cap 60, CSE first. Grade
**solely from oral discussions of the hand-in exercises during the semester, no final
exam**. C++23. Matrix `#advprog:tuwien.ac.at`. Lecturers Manstetten, Salzmann,
Cervenka, Lacerda de Orio (E360). Previous knowledge: solid C/C++ or Python.
Re-check everything when the 2027W page appears: checklist at the end of
[00-exam-focus.md](00-exam-focus.md).

**Sources.** The lecturers' 2020W/2021W lecture items and exercise hand-outs are public
on GitHub [S3] [S4] [S5] (no licence: read, never copied) and show how the hand-ins and
discussions work, but they are C++17. The C++20/23 content is from the working draft
N4950 [S8], cppreference [S9] and the Core Guidelines [S10], and every feature claim is
tested on this Mac [S13]. Stroustrup's *A Tour of C++* [S11] is the best single book
(not free; the course names Meyers [S16] instead).

**Toolchain**: Apple clang 21.0.0, `clang++ -std=c++23 -O2 -Wall -Wextra` (`-std=c++2b`
is accepted too). What it supports:

| C++23 feature | status here | used in |
|---|---|---|
| `std::print` / `println` | yes | `features.cpp` |
| `std::expected` (+ monadic ops) | yes | `features.cpp`, `matrix/` |
| deducing `this` | yes | `lambdas.cpp`, `operators.cpp`, `features.cpp` |
| `std::mdspan`, `m[i, j]` | yes | `features.cpp`, `matrix/` |
| `std::ranges::to` | yes | `ranges.cpp` |
| `views::zip`, `ranges::fold_left` | yes (macros missing: probe) | `ranges.cpp` |
| `if consteval`, `static operator()`, `auto(x)`, P2718 range-for | yes | `constexpr.cpp`, `lambdas.cpp`, `features.cpp`, `lifetime.cpp` |
| `std::flat_map` | yes | `features.cpp` |
| `std::generator` | **no** (SKIP) | `ranges.cpp` |
| `views::enumerate`, `chunk`, `slide`, `stride`, `cartesian_product`, `as_const` | **no** (SKIP) | `ranges.cpp` |
| `std::move_only_function` | **no** (SKIP) | `lambdas.cpp` |
| `std::stacktrace`, `<spanstream>` | **no** | - |
| `import std;` | **no** | - |
| named modules | yes, with `-fcxx-modules` (`__cpp_modules` undefined) | `modules/` |
| parallel algorithms (C++17) | yes, with `-fexperimental-library` | `concurrency.cpp` |

`make -C ../src/cpp features` re-measures the table.

| # | note | one line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | grading by oral discussion; what the 2021W hand-outs and interviews looked like; how to prepare; toolchain traps; what to verify for 2027W |
| 01 | [Basic concepts](01-basic-concepts.md) | translation units, declarations vs definitions, linkage, ODR, headers, named modules on Apple clang; build tools in NSSC I note 10 |
| 02 | [Type deduction](02-type-deduction.md) | template deduction table, `auto`, `decltype((x))`, `decltype(auto)`, CTAD and deduction guides |
| 03 | [Trivial types and object lifetime](03-trivial-types-and-object-lifetime.md) | trivially copyable, standard-layout, aggregate, implicit-lifetime; temporaries and lifetime extension; `construct_at` |
| 04 | [Pointers, references and ownership](04-pointers-references-and-ownership.md) | pointer vs reference, `span`, parameter-passing table, invalidation, owners vs observers |
| 05 | [Value categories](05-value-categories.md) | lvalue/xvalue/prvalue, move semantics, forwarding, copy elision; copies and moves counted |
| 06 | [Conversions](06-conversions.md) | promotions, usual arithmetic conversions, narrowing, overload ranking, `explicit`, casts |
| 07 | [Lambdas](07-lambdas.md) | closures, capture modes, generic/template lambdas, deducing `this`, `std::function` vs templates |
| 08 | [Operator overloading](08-operator-overloading.md) | `vec3` with hidden friends, `<=>` and ordering categories, ADL, `std::formatter` |
| 09 | [Classes](09-classes.md) | special-member generation table, rule of zero/five, copy-and-swap, virtual/final/slicing, CRTP |
| 10 | [Smart pointers](10-smart-pointers.md) | `unique_ptr` + deleters, `shared_ptr` control block, `weak_ptr` and cycles, implementing `unique_ptr` |
| 11 | [Iterators and ranges](11-iterators-and-ranges.md) | iterator concepts, a custom iterator, sentinels, lazy views, projections, `ranges::to`, what libc++ 21 lacks |
| 12 | [Constant expressions](12-constant-expressions.md) | `constexpr`, `consteval`, `if consteval`, `constinit`, compile-time tests and a compile-fail suite |
| 13 | [Templates and concepts](13-templates-and-concepts.md) | SFINAE vs `requires`, subsumption, concept design, variadics and folds, the `la::Matrix` library hand-in |
| 14 | [Concurrency](14-concurrency.md) | data races, `jthread`, mutex/condition variable, atomics and memory order, futures, execution policies measured |
