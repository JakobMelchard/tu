# 00 Exam focus: the grade is a conversation about your code

Written 2026-09-28 from [`../refs/SOURCES.md`](../refs/SOURCES.md). The course is
**offered in winter semesters**; the 2027W TISS page is **not published** [S1]. Everything
"current" below is the 2026W page; everything about how discussions run is the
2020W/2021W public material [S3] [S5], two to six years older and C++17.

## What TISS states (2026W) [S1]

| field | 2026W value |
|---|---|
| type | VU, 2.0 h, 3.0 ECTS, hybrid; mandatory, CSE 3rd semester (066 646) |
| slot | Thu 09:00-11:00, EI 1 Petritsch HS, 01.10.2026-28.01.2027 |
| teaching | lectures (hybrid video conference), case studies discussed in presence, programming homework |
| **grading** | *"solely based on the oral discussions about the students hand-in exercises"*, held during the semester. **No final exam.** |
| mode field | "written and oral" (contradicts the line above; not resolved on TISS) |
| registration | 01.09.2026 23:59 - 04.10.2026 23:59; deregistration until 01.11.2026 23:59 |
| cap | above 60, CSE students first |
| subject | C++23 core language and standard library, 14 topics (notes 01-14) |
| lecturers | Manstetten, Salzmann, Cervenka, Lacerda de Orio (E360 Microelectronics) |
| chat | Matrix `#advprog:tuwien.ac.at` |
| previous knowledge | "solid basic knowledge in programming (e.g., C/C++, Python)" |
| literature | none listed |

Three consequences. (1) **Every point is earned during the semester**: a missed
hand-in or discussion cannot be repaired at an exam. (2) **Deregistration after
01.11 counts** (2026W pattern): by then the first hand-in is probably due. (3) The
oral format means *you* are graded, not the code: code you cannot explain is worth
little.

## What the public 2021W material shows [S3] [S4] [S5]

The lecturers published the 2020W and 2021W courses on GitHub (no licence, so read
only; `../refs/fetch-sources.sh` clones them). The organisation item of both years
says, in substance:

- four exercise blocks: **EX0** (ungraded dry run of the workflow), **EX1, EX2, EX3**,
  each with three parts (2021W: `ex1.1`-`ex3.3`), **10 points each, one third of the grade**;
- submission **individual**, by pushing to a per-exercise git repository on the
  institute's Gitea before a Monday 16:00 deadline; the head of `master` counts;
- the grade comes from a **30-minute online interview per block, "in pairs"**, the day
  after the deadline, in a fixed personal slot; points for **both the discussion and the
  submitted code**; camera and microphone required;
- "possible solutions" with benchmark tables were published after each deadline
  (items 007, 009, 010, 013, ...);
- **no final examination**.

Each hand-out [S4] is a small CMake project: provided `include/` and `lib/` with a
deliberately broken or missing part, **one test executable per requirement**
(`TestA_destructor`, `TestB_copyConstructor`, ...), a benchmark, sanitizers switched on
for Debug builds, a README saying *which file you may change*, and the closing line
*"Prepare yourself for a discussion of your implementation"*, often extended to the
runtime differences the benchmark shows. The tasks (details in [`../refs/SOURCES.md`](../refs/SOURCES.md#s4---cppitemsex-the-2021w-exercise-hand-outs)):

| block | 2021W part | topic | our note | our closest code |
|---|---|---|---|---|
| EX1 | 1.1 sink parameters, benchmark | value categories | [05](05-value-categories.md) | `value_categories.cpp` (`by_value`, `by_rref`) |
| | 1.2 copy/move ctor + dtor of an owning vector | special members | [09](09-classes.md) | `classes.cpp` (`Buffer`) |
| | 1.3 the four copy/move members of a linked list | special members | [09](09-classes.md) | `classes.cpp` |
| EX2 | 2.1 timing wrapper for any callable | variadic templates, forwarding | [13](13-templates-and-concepts.md), [07](07-lambdas.md) | `concepts.cpp` (`call_counted`) |
| | 2.2 class template + CTAD from containers | deduction | [02](02-type-deduction.md) | `deduction.cpp` (`Stats`) |
| | 2.3 algorithms instead of loops | iterators | [11](11-iterators-and-ranges.md) | `ranges.cpp` |
| EX3 | 3.1 bidirectional iterator for a list | iterators | [11](11-iterators-and-ranges.md) | `ranges.cpp` (`SList::Iter`) |
| | 3.2 own `unique_ptr` + custom deleter | smart pointers | [10](10-smart-pointers.md) | `smart_pointers.cpp` (`my::unique_ptr`) |
| | 3.3 thread-safe `shared_ptr` count: atomics vs locks | concurrency | [14](14-concurrency.md) | `concurrency.cpp` |

The lecture items themselves are written as question/answer prompts
(`> question` / `> - answer`, e.g. 85 of them in the special-members item) [S3]. That
is the most direct evidence of what the discussion questions sound like: whether the
special members are always implicitly available, why C++ needs pointers when it has
references, what a given line costs.

## What is not known for 2027W

- The number and size of hand-ins, their dates, and whether discussions are still in
  pairs, still 30 minutes, still online (TISS 2026W now says "case studies in presence").
- Whether submission is still via the institute's Gitea or via TUWEL (TISS 2026W says
  "TUWEL from 01.10.2026"). Check TUWEL access before the semester.
- Which C++23 features the hand-outs use and which compiler they are tested with. The
  2021W hand-outs pinned C++17 and pointed to a Docker image with Clang/LLVM [S4].
- No 2022W-2026W material is public [S18]; VoWi was not readable [S7].

## How a discussion probably goes (inference from S3/S4, not a documented format)

1. You share the code. They pick a test or a line: *"walk us through your move
   constructor"*. Expect to justify every changed line.
2. *"Why?"* questions: why `std::move` here but not there, why `noexcept`, why pass
   by value, why this algorithm instead of a loop.
3. *"What if?"* variants: the member is `const`; the type is not movable; two threads
   call this; the container is a `std::list`.
4. The benchmark: predict, then explain your measured numbers. The 2021W solutions
   report about a factor 10 between copying and moving a large vector parameter
   (item 007). A Debug build ruins this: benchmark in Release.
5. Adjacent theory from the lecture items: value categories, special-member
   generation rules, iterator categories, memory order.
6. In pairs: assume either of you may be asked about either topic.

## How to prepare, per hand-in

- [ ] All tests pass in Debug **with sanitizers actually on** (see the trap below), and in Release.
- [ ] For every test: which requirement it checks, and what your code does to pass it.
- [ ] For every line you changed: the alternative you rejected and why.
- [ ] Benchmark in Release, numbers written down, one sentence of explanation each.
- [ ] Known limitations stated before they ask (exception safety, thread safety, allocator).
- [ ] Clean commit history: small commits, messages that say why (it is your submission).
- [ ] Rehearse aloud with the five questions at the end of the matching note, 30-minute timer, ideally with your discussion partner.
- [ ] `clang-tidy` with the course's check set [S3] run once; know why each remaining warning is fine.

**Toolchain traps found on this Mac with the 2021W hand-outs** [S4] [S13]:

- CMake 4.4 refuses `cmake_minimum_required(VERSION 3.0)`: configure with
  `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
- The hand-outs enable ASan only `if CMAKE_CXX_COMPILER_ID STREQUAL "Clang" OR "GNU"`;
  Apple's compiler reports `AppleClang`, so **the sanitizers are silently off** (a Debug
  configure of ex1.2 produced no compile command with `-fsanitize`). Add them yourself
  or use a Linux container.
- `-fsanitize=memory` and `-fsanitize=leak` are unsupported on arm64 macOS: MSan needs Linux.
- ex1.2's tests use `std::to_string` without `#include <string>` and fail on libc++ 21;
  newer libc++ has fewer transitive includes. Include what you use.
- So: have a Linux environment (Docker or a VM, Clang and GCC) ready for 2027W, and
  check that the hand-outs build on it in week 1.

## What to verify when the 2027W page appears

- [ ] Dates and room of the Thursday slot; first lecture date (the 2026W text still said "October 2").
- [ ] Registration window and deregistration deadline; cap and priority rule.
- [ ] The Examination modalities text: still "solely ... oral discussions of hand-in exercises"? Still no final exam?
- [ ] Number of hand-ins, deadlines, discussion dates; in pairs or alone; online or in presence.
- [ ] Submission channel (Gitea account? TUWEL?).
- [ ] C++ standard (C++23 in 2026W) and the reference compiler; whether Apple clang is acceptable.
- [ ] Lecturer list, Matrix room, any literature added.
- [ ] Then update `../docs/tiss.md` and these notes.
