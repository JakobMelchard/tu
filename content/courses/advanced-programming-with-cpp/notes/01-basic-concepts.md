# 01 Basic concepts: translation units, linkage, ODR, build, headers and modules

How source files become one program, and the rules that make "it compiles" differ
from "it links" and from "it is correct". The toolchain side (make, CMake, compiler
flags, lldb, sanitizers, git) is in
[NSSC I note 10](../../numerical-simulation-and-scientific-computing-i/notes/10-software-engineering-for-scientific-computing.md)
[S15]; this note does the language side. Lecture items 001, 003, 004, 025 [S3].

Code: `src/cpp/basics_main.cpp`, `basics_other.cpp`, `basics.hpp`, `modules/`.

## Definitions

- **Translation unit (TU)**: one `.cpp` after the preprocessor has pasted in every
  `#include`. The compiler sees one TU at a time; it knows nothing about the others.
- **Declaration** introduces a name and its type (`int f(int);`, `extern int x;`,
  `struct S;`). **Definition** also creates the entity (function body, storage,
  complete class). Every definition is a declaration.
- **Linkage** [S8 [basic.link]]: *external* (the name refers to the same entity from
  every TU: non-`static` functions, `extern`/`inline` variables), *internal* (one entity
  per TU: `static`, anything in an unnamed namespace, non-`inline` `const`/`constexpr`
  variables at namespace scope), *none* (locals), *module* (C++20: visible only inside
  the module).
- **One-definition rule** [S8 [basic.def.odr]]: (a) at most one definition per TU;
  (b) every non-inline function or variable that is odr-used has **exactly one**
  definition in the program; (c) classes, inline functions/variables, templates may be
  defined in several TUs **if all definitions are token-identical and mean the same**.
  Violating (c) is "ill-formed, no diagnostic required": the linker keeps one copy and
  nobody tells you.
- **Header**: a file of declarations and of the definitions (c) allows, included by
  many TUs. `#pragma once` or include guards prevent double inclusion *within* a TU;
  they do nothing across TUs.
- **Build**: preprocess (`-E`) -> compile to object (`-c`, one per TU) -> link (resolve
  external names across objects and libraries). "undefined reference" / "Undefined
  symbols" is a link error: a declaration without a definition.
- **Module** (C++20) [S8 [module.unit]]: a named, separately compiled unit. `export
  module m;` starts the interface; only `export`ed declarations are visible to
  `import m;`. The importer reads a compiled *binary module interface* (BMI, `.pcm` in
  clang) instead of re-parsing text. Macros do not leak in or out.

## Complete example

Two TUs share a header; which variables are one object and which are two?

```sh
# complete example: paste into a shell in an empty directory
cat > basics.hpp <<'X'
#pragma once
inline int shared_counter = 0;   // external linkage: one object per program
static int per_tu = 0;           // internal linkage: one object per TU
int* other_shared();             // declared here, defined in other.cpp
int* other_per_tu();
X
cat > other.cpp <<'X'
#include "basics.hpp"
int* other_shared() { return &shared_counter; }
int* other_per_tu() { return &per_tu; }
X
cat > main.cpp <<'X'
#include "basics.hpp"
#include <cstdio>
int main() {
    std::printf("shared: same object %d\n", &shared_counter == other_shared());  // 1
    std::printf("per_tu: same object %d\n", &per_tu == other_per_tu());          // 0
}
X
clang++ -std=c++23 -Wall -Wextra -c main.cpp && clang++ -std=c++23 -Wall -Wextra -c other.cpp
clang++ main.o other.o -o basics && ./basics
```

Drop `other.o` from the last link line and the linker reports `other_shared()` as an
undefined symbol: the compile steps succeeded, only the declaration existed.

The runnable version with the checks is `src/cpp/basics_main.cpp` (7 checks).

A module instead of a header (`src/cpp/modules/`, built by `make`):

```cpp
// geometry.cppm
module;                  // global module fragment: #includes go here
#include <cmath>
export module geometry;
export namespace geo { struct vec2 { double x, y; }; double norm(vec2 v) { return std::hypot(v.x, v.y); } }
double twice(double x) { return 2 * x; }          // not exported: invisible to importers
```

```sh
clang++ -std=c++23 -fcxx-modules -x c++-module --precompile geometry.cppm -o geometry.pcm
clang++ -std=c++23 -fcxx-modules -c geometry.pcm -o geometry.o
clang++ -std=c++23 -fcxx-modules -fmodule-file=geometry=geometry.pcm -c main.cpp -o main.o
clang++ main.o geometry.o -o main
```

**Module support on this Mac** [S13] [S14]: Apple clang 21 parses `export module` only
with `-fcxx-modules`; `__cpp_modules` stays undefined; `import std;` fails (no `std`
module is shipped); the `.pcm` must be built with the **same flags** as the importer
(a sanitizer mismatch is a hard error: "configuration mismatch"). Upstream clang
documents `--precompile` and `-fmodule-file=` [S14]. For the course: headers remain the
default until the 2027W hand-outs say otherwise.

## Header or source?

| goes in a header | goes in exactly one `.cpp` |
|---|---|
| class definitions, `inline` functions, templates, `inline` variables, `constexpr` functions, declarations | non-inline function bodies, non-inline global variable definitions, `static` helpers, `using namespace` |

Templates live in headers because the compiler must see the definition to instantiate
it in each TU. `constexpr` and `consteval` functions are implicitly `inline`.

## Pitfalls

- `static int x;` or `namespace { ... }` **in a header**: every TU gets its own copy.
  Counters, caches and singletons silently split (`basics_main.cpp` shows `&per_tu_counter`
  differing between TUs).
- An `inline` function in a header that uses such a per-TU entity is an ODR violation
  (definitions refer to different entities); the linker picks one body.
- Two TUs defining `struct Point` differently: undefined behaviour without diagnostic.
  Put it in one header.
- Relying on transitive includes (`std::to_string` via `<iostream>`): libc++ 21 removed
  many; the 2021W hand-outs no longer compile unmodified for this reason [S4] [S13].
- Static initialisation order across TUs is unspecified: a global in TU A must not use
  a global in TU B during initialisation. Fix: function-local static or `constinit` (note 12).
- `using namespace std;` in a header leaks into every includer.
- Undefined behaviour is a *program* property, not a compiler error: signed overflow,
  out-of-bounds, use-after-free, data races compile fine. Sanitizers find them at run
  time; the course hand-outs switch ASan on for Debug builds [S4] (on macOS check that
  it really is on, see note 00).

## Discussion questions

1. **What is the difference between a declaration and a definition? Give one of each for a function, a variable, a class.**
   `int f(int);` / `int f(int x) { return x; }`; `extern int n;` / `int n = 0;`;
   `struct S;` / `struct S { int a; };`. A definition creates the entity; a declaration
   only makes the name usable. The linker needs one definition per odr-used non-inline entity.
2. **Why may a class or a template be defined in many TUs but a normal function not?**
   The ODR's exception (c): the compiler needs the full definition to lay out objects
   or instantiate templates in each TU, so identical definitions are allowed and merged.
   A non-inline function needs only a declaration to be called, so one definition suffices
   and two collide at link time.
3. **What does `inline` mean today?** "Multiple identical definitions allowed; one
   entity." It is about linkage and the ODR, not about inlining (the optimiser decides
   that). Since C++17 it also applies to variables: `inline int x = 0;` in a header is
   one object program-wide.
4. **A global `static const double g = 9.81;` in a header, included in 50 TUs: problem?**
   Harmless in practice (internal linkage, 50 copies of a constant, usually folded
   away), but 50 distinct objects: `&g` differs per TU. `inline constexpr double g = 9.81;`
   gives one object and states intent.
5. **What do modules fix that headers cannot?** Isolation (macros and non-exported
   names do not leak), no repeated parsing (BMI is compiled once), explicit interface
   (`export`), order-independence of imports. Costs: build systems must know the
   dependency order, BMIs are compiler- and flag-specific, and tool support is
   uneven (on this Mac: `-fcxx-modules`, no `import std`).

## In the code

- `src/cpp/basics_*.cpp`, `basics.hpp`: inline vs static vs extern vs constexpr at namespace scope, checked by address.
- `src/cpp/check.hpp`: the `inline` variables that make one pass/fail counter per program.
- `src/cpp/modules/`: a named module and its importer; the Makefile rule shows the four build steps.
- `src/cpp/Makefile`: `make sanitize` builds everything with ASan + UBSan.
