# Topic map - TISS topic -> lecturers' public items -> our note -> our code

The structural index is the 2026W TISS "Subject of course" list [S1]: 14 topics, one
note each, in TISS order. The 2021W lecture items [S3] are the closest public
lecture material; they cover the same list **for C++17** (item 000 lists the topics
without "ranges" and "concepts"). Items are numbered by lecture order, not by topic, so
the mapping below is ours, made from the item headings. Exercise names are the 2021W
hand-outs [S4]; all of them are cite-only (no licence).

| # | TISS topic [S1] | 2021W items [S3] | 2021W hand-out [S4] | our note | our code (`../src/cpp/`) | standard [S8] |
|---|---|---|---|---|---|---|
| 1 | basic concepts | 001 toolchain, linting, sanitizers; 003 compilation hands-on; 004 git + CMake; 025 standards, modern CMake | ex0 (vector with tests, the submission dry run) | [01](../notes/01-basic-concepts.md) | `basics_main.cpp`, `basics_other.cpp`, `basics.hpp`, `modules/` | [basic.def.odr], [basic.link], [module.unit] |
| 2 | type deduction | 005 types and expressions; 011 function templates; 012 class templates, deduction guides | ex2.2 (CTAD from containers) | [02](../notes/02-type-deduction.md) | `deduction.cpp` | [dcl.spec.auto], [dcl.type.decltype], [temp.deduct.call], [over.match.class.deduct] |
| 3 | trivial types | no dedicated item (touched in 005, 008) | - | [03](../notes/03-trivial-types-and-object-lifetime.md) | `lifetime.cpp` | [basic.types.general], [class.prop], [basic.life], [intro.object] |
| 4 | pointers / references | 006 references; 018 (raw vs smart); 020 upcasting | - | [04](../notes/04-pointers-references-and-ownership.md) | `pointers.cpp` | [basic.compound], [dcl.ref], [basic.stc.general] |
| 5 | value categories | 006 value categories, forwarding, reference collapsing; 008 | ex1.1 (sink parameters + benchmark) | [05](../notes/05-value-categories.md) | `value_categories.cpp` | [basic.lval], [class.copy.elision] |
| 6 | conversions | 005 (conversions and precedence) | - | [06](../notes/06-conversions.md) | `conversions.cpp` | [conv.rank], [dcl.init.list], [over.ics.rank], [class.conv.ctor], [class.conv.fct] |
| 7 | lambdas | 017 lambda expressions | ex2.1 (callable wrapper) | [07](../notes/07-lambdas.md) | `lambdas.cpp` | [expr.prim.lambda.capture] |
| 8 | operator overloading | no dedicated item (014 iterator operators, ex2.2's `SpaceVector`) | ex2.2 | [08](../notes/08-operator-overloading.md) | `operators.cpp` | [over.oper], [class.spaceship] |
| 9 | classes | 008 special member functions; 020 inheritance; 024 exceptions | ex1.2, ex1.3 (special members of owning types) | [09](../notes/09-classes.md) | `classes.cpp` | [special], [class.copy.assign], [class.dtor], [dcl.fct.def.default] |
| 10 | smart pointers | 018 smart pointers | ex3.2 (own `unique_ptr`), ex3.3 (thread-safe `shared_ptr`) | [10](../notes/10-smart-pointers.md) | `smart_pointers.cpp` | [unique.ptr], [util.smartptr.shared] |
| 11 | iterators / ranges | 014 iterators (ranges: none, C++17) | ex2.3 (algorithms, no raw loops), ex3.1 (bidirectional iterator) | [11](../notes/11-iterators-and-ranges.md) | `ranges.cpp` | [iterator.concepts], [range.adaptors], [range.utility.conv] |
| 12 | constant expressions | 012 (`if constexpr`); 025 (history) | - | [12](../notes/12-constant-expressions.md) | `constexpr.cpp`, `compile_fail/` | [expr.const], [dcl.constexpr], [dcl.constinit] |
| 13 | templates / concepts | 011, 012 (concepts: none, C++17) | ex2.1, ex2.2 | [13](../notes/13-templates-and-concepts.md) | `concepts.cpp`, `matrix/` | [temp.constr.decl], [temp.variadic], [expr.prim.fold] |
| 14 | concurrency | 022 parallelism and concurrency | ex3.3 | [14](../notes/14-concurrency.md) | `concurrency.cpp` | [intro.races], [atomics.order], [futures], [thread.jthread.class], [algorithms.parallel.exec] |

Plus [00-exam-focus.md](../notes/00-exam-focus.md) (how the grade is made) and
`features.cpp` (which C++23 features this Mac has, for every note).

## What the 2021W material does not cover (and the notes therefore take from S8 + S13)

C++20: concepts and `requires`, ranges and views, `<=>`, modules, `consteval`/`constinit`,
`std::jthread`/`stop_token`, `std::span`, designated initialisers, `std::format`.
C++23: deducing `this`, `if consteval`, multidimensional `operator[]`, `std::expected`,
`std::print`, `std::mdspan`, `ranges::to`, `views::zip`, P2718 range-for lifetime.
Whether the 2026W/2027W hand-outs use these is unknown; S1 only says "C++23".
