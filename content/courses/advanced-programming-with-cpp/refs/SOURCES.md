# Sources - 360.251 Advanced Programming with C++

Register of every source used for [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). Notes cite these as `[S<n>]`, standard sections as
`[S8 [stable.name]]` (the bracketed stable names were checked against the N4950 text).
Retrieval date for everything online: **2026-09-28** unless stated.

**Vendoring policy.** Nothing is vendored. No source below carries a licence that
permits redistribution from this repo (see "licence" on each entry);
[`fetch-sources.sh`](fetch-sources.sh) clones or downloads the free ones into the
git-ignored `cite-only/` for personal study. No TUWEL material: TUWEL needs a login.

**The headline finding.** The lecturers' public material exists, but it is from
**2020W and 2021W** and it teaches **C++17** [S3] [S5]. The 2026W TISS page says
**C++23** and adds "ranges" and "concepts" to an otherwise identical topic list [S1].
No public material for 2022W-2026W was found [S18]. So: the 2021W repositories show
*how the course is run and graded* (hand-ins with tests, oral discussion per hand-in);
the C++20/23 content of the notes comes from the standard [S8] and is verified on this
Mac [S13].

---

## Course-authoritative

### S1 - TISS course page 2026W (latest published offering)

- 360.251 Advanced Programming with C++, 2026W. <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=360251&semester=2026W>
- Transcribed 2026-09-28 in [`../docs/tiss.md`](../docs/tiss.md) (logged-in browser); API record in `../docs/tiss-api.md`. Offerings on TISS: 2020W-2026W; **2027W not published**.
- Used for: VU 2.0 h / 3.0 ECTS, hybrid; mandatory CSE 3rd semester; subject list (C++23 core language and standard library, 14 topics); learning outcomes; teaching methods (hybrid video-conference lectures, case studies in presence, programming homework); lecturers Manstetten, Salzmann, Cervenka, Lacerda de Orio (E360); Thu 09:00-11:00 EI 1 Petritsch HS, 01.10.2026-28.01.2027; registration 01.09-04.10.2026, deregistration 01.11.2026; above 60 participants CSE (066 646) first; grading "solely based on the oral discussions about the students hand-in exercises", held during the semester; Matrix room `#advprog:tuwien.ac.at`; previous knowledge "solid basic knowledge in programming (e.g., C/C++, Python)"; no lecture notes listed.
- Oddities recorded in `docs/tiss.md`: "Mode of examination: written and oral" vs the oral-only modalities text; the 2026W text still announces the first lecture as "Thursday, October 2" (a 2025 date).


## The lecturers' public material (licence: none, so cite only)

All repositories below have **no LICENSE file** (GitHub API `license: null`, and no
licence text anywhere in the trees, checked 2026-09-28). Without a licence they are
all rights reserved: we read them, `fetch-sources.sh` clones them for study, and
nothing from them is copied into this repo. Our code solves *similar* problems in our
own words.

### S3 - `cppitems/cppitems`: the 2021W lecture "items"

- <https://github.com/cppitems/cppitems>, commit `ad07e0b` (2022-02-28), items `000`-`025` as Markdown + C++ snippets.
- Item 000 is the 2021W course organisation: schedule; C++17 topic list identical to S1's minus "ranges" and "concepts"; lectures and exercise discussions by video conference with recordings; submissions **individual**, pushed to per-exercise git repositories on the institute's Gitea (`tea.iue.tuwien.ac.at`) before a Monday 4 pm deadline, head of `master` counts; **EX1, EX2, EX3 graded 10 points each in a 30-minute online interview held in pairs, points for both the discussion and the submitted code**, each a third of the grade; EX0 ungraded (submission-process test); **no final examination**; announcements via TISS, contact `cpp@iue.tuwien.ac.at`, a chat channel; literature list (cppreference, Compiler Explorer, C++ Insights, C++ Core Guidelines, Jason Turner's videos, Meyers, Filipek, Lippman).
- Items with lecture content: 001 toolchain/linting/sanitizers, 003 compilation hands-on, 004 git and CMake, 005 types and expressions, 006 value categories and references, 008 special member functions, 011 function templates, 012 class templates, 014 iterators, 017 lambdas, 018 smart pointers, 020 inheritance, 022 parallelism and concurrency, 024 exceptions, 025 C++ standards and modern CMake. Items 002/007/009/010/013/015/016/019/021/023 publish "possible solutions" to the exercises after their deadlines, with benchmark tables.
- Style: most items are written as question / answer prompts (`> question` then `> - answer`), e.g. 118 such lines in item 001, 85 in 008, 74 in 018. That is the register of the oral discussions.
- The repo ships a `.clang-format` (LLVM base style) and a `.clang-tidy` enabling `cppcoreguidelines-*`, `performance-*`, `bugprone-*`, `modernize-*`, `readability-*` and more.

### S4 - `cppitems/ex*`: the 2021W exercise hand-outs

- <https://github.com/cppitems/ex0> ... `ex3.3`, commits `41dec82` (ex0), `31233ac` (1.1), `7128af5` (1.2), `e97d881` (1.3), `e7d806f` (2.1), `8728241` (2.2), `72ffdc5` (2.3), `2f9aeee` (3.1), `38a6c5e` (3.2), `195e310` (3.3); last pushes 2021-10-13 to 2021-12-20.
- Shape of every hand-out: `CMakeLists.txt` (C++17, `CMAKE_CXX_STANDARD_REQUIRED`), `include/`, `lib/` or `src/`, `tests/` with one executable per requirement (`TestA_...`, `TestB_...`) run by ctest, a benchmark, sanitizers switched on in CMake (AddressSanitizer in all ten; ThreadSanitizer in ex0 and ex3.3; MemorySanitizer in ex0), a README that says which files you may change, and every README ending in some form of **"Prepare yourself for a discussion of your implementation"**, often extended to the benchmark's runtime differences.
- Tasks (paraphrased): 1.1 initialise a member from a by-value / lvalue-ref / rvalue-ref parameter as cheaply as possible, benchmark; 1.2 fix the defaulted copy/move constructor and destructor of a resource-owning vector; 1.3 the four copy/move members of a singly linked list; 2.1 generalise a timing wrapper to any callable and any arguments (variadic template + perfect forwarding); 2.2 a class template holding mean and standard deviation with CTAD from different containers; 2.3 rewrite loop-based container functions with `<algorithm>`, no raw `for` left; 3.1 a standard-conforming bidirectional iterator for a doubly linked list with sentinel node; 3.2 a simplified `unique_ptr` with custom deleter; 3.3 make a given `shared_ptr` reference count thread-safe twice, with atomics and with locks, and benchmark both.

### S5 - `manstetten/cppitems2020`: the 2020W items

- <https://github.com/manstetten/cppitems2020>, commit `204b904` (pushed 2021-10-06). Items `000`-`022`; same organisation and grading as S3 (EX1-EX3 each 1/3 of the grade, 30-minute online interview in pairs, no final exam), repositories `ex0`...`ex3`.
- Used for: confirming the grading scheme was stable across two years; the 2020W versions of the iterator and smart-pointer exercises (items 017, 018 with the same `Test*` layout).

### S6 - `cppitems` organisation, site and tooling

- <https://github.com/cppitems> (19 public repos) and <https://cppitems.github.io> (named in S3 item 000 as the publication site for lecture material and exercises). The site is a JavaScript app rendering the S3 items; last commit `bac465b`, 2022-10-05 ("new render engine"). Other repos are tooling: `webapp`, `render`, `docker`, `theia`/`theia-1` (a browser IDE), `highlight.js` (BSD-3-Clause), `vscode-markdown-cppitems` (MIT). Nothing there is course content for 2022W or later.

### S7 - VoWi page (not read)

- <https://vowi.fsinf.at/wiki/TU_Wien:Advanced_Programming_with_C++_VU_(Manstetten)>. Exists (a web search lists it) but sits behind a bot check; **not read and not bypassed**. Whatever it says about the discussions is unverified here. Open it in a browser.

## The language: normative text and references

### S8 - ISO C++ working draft N4950 (the C++23 text)

- Köppe (ed.), *Working Draft, Standard for Programming Language C++*, N4950, 2023-05-10. <https://open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4950.pdf> (8 043 551 bytes). ISO/IEC copyright: cite only.
- Stable names used in the notes, each found in the text: [basic.def.odr], [basic.link], [module.unit], [intro.object], [basic.life], [basic.stc.general], [basic.types.general], [class.prop], [basic.compound], [dcl.ref], [basic.lval], [conv.lval], [conv.rank], [dcl.init.list], [class.copy.elision], [dcl.spec.auto], [dcl.type.decltype], [temp.deduct.call], [over.match.class.deduct], [expr.static.cast], [class.conv.ctor], [class.conv.fct], [over.ics.rank], [over.match.best], [expr.prim.lambda.capture], [over.oper], [class.spaceship], [special], [class.copy.assign], [class.dtor], [dcl.fct.def.default], [unique.ptr], [util.smartptr.shared], [iterator.concepts], [range.adaptors], [range.utility.conv], [coro.generator], [expr.const], [dcl.constexpr], [dcl.constinit], [temp.constr.decl], [temp.variadic], [expr.prim.fold], [intro.races], [atomics.order], [futures], [thread.jthread.class], [algorithms.parallel.exec], [mdspan.overview], [expected], [print.fun].
- Two findings from the text: [class.prop]/9 makes every aggregate without a user-provided destructor an implicit-lifetime class (even one holding a `std::string`); [func.wrap.func.con] declares `template<class F> function(F&&)`, while libc++ 21 still takes `F` by value [S13].

### S9 - cppreference.com

- <https://en.cppreference.com/w/cpp>, and the offline HTML archive release `v20250209` from <https://github.com/PeterFeicht/cppreference-doc/releases> (`html-book-20250209.tar.xz`, 6 650 380 bytes). Content licence CC BY-SA 3.0 and GFDL: share-alike, so not vendored; the script fetches it.
- Used for: the compiler support tables as a cross-check of S13, and as the reference the course itself lists first [S3].

### S10 - C++ Core Guidelines

- Stroustrup, Sutter (eds.), <https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines>; source <https://github.com/isocpp/CppCoreGuidelines> (Markdown, 841 419 bytes on 2026-09-28). Licence grants copying "for your personal or internal business use only": cite only.
- Used for: rule names cited in the notes (each title checked in the 2026-09-28 file): C.20/C.21 rule of zero/five, C.35, C.46, C.66, C.67, C.128, C.160-C.168, F.15-F.20, F.50, F.52/F.53, I.11, R.1-R.3, R.11, R.20-R.24, R.30, ES.11, ES.46, T.10, T.20, Per.11, CP.2, CP.20, CP.25, CP.42; the course lists them [S3] and its `.clang-tidy` enables `cppcoreguidelines-*`.

### S11 - Stroustrup, *A Tour of C++*, 3rd ed.

- Addison-Wesley 2022, ISBN 978-0-13-681648-5. **Not free: cite only.** The shortest complete C++20 overview; read it before the semester. Not named by the course.

### S16 - Meyers, *Effective Modern C++*

- O'Reilly 2014, ISBN 978-1-491-90399-5. Not free, cite only. Named in the course's literature list [S3] [S5]; Items 1-4 (deduction), 23-30 (move, forwarding) map onto notes 02 and 05.

### S17 - the rest of the course's literature list [S3]

- Filipek, *C++17 in Detail* (2019); Lippman et al., *C++ Primer*, 5th ed. (2012); Compiler Explorer <https://godbolt.org>; C++ Insights <https://cppinsights.io>. Not read for this pass; listed so the course's own list is complete.

## Toolchain facts

### S12 - libc++ C++23 status page

- <https://libcxx.llvm.org/Status/Cxx23.html> (upstream, retrieved 2026-09-28). Says, per paper: `std::generator` (P2502), `chunk`/`slide` (P2442), `cartesian_product` (P2374), `as_const` (P2278), `move_only_function` (P0288), stacktrace (P0881), spanstream (P0448) **not started**; `enumerate`/`stride` complete only in libc++ 23; `zip` in 22; `fold` in 23; `print`/`mdspan` 18; `expected` 16; `ranges::to` 17; `flat_map` 20; std modules 19.
- Caveat: upstream "complete" is when the last piece landed; Apple's libc++ 21 already compiles `views::zip` and `ranges::fold_left` without the feature macros [S13]. What counts is the probe.

### S13 - this Mac, measured 2026-09-28

- Apple M3 Pro, 12 hardware threads, `hw.cachelinesize` 128. Apple clang version 21.0.0 (clang-2100.1.1.101), target arm64-apple-darwin25.6.0, macOS 26.7 (25G229), Xcode toolchain; libc++ `_LIBCPP_VERSION 210106`, `__cplusplus 202302` under `-std=c++23` (also accepts `-std=c++2b`, `c++2c`, `c++26`). CMake 4.4.3.
- Evidence: [`../src/cpp/probe.sh`](../src/cpp/probe.sh) + `../src/cpp/probes/*.cpp` (compile, link, run), [`../src/cpp/features.cpp`](../src/cpp/features.cpp); the table is in `../notes/CHANGELOG.md`.
- Findings beyond the macros: named modules need `-fcxx-modules` (otherwise `module` is not a keyword; `__cpp_modules` stays undefined); `import std` fails (no `std` module shipped); parallel algorithms need `-fexperimental-library` (libdispatch backend, `_LIBCPP_PSTL_BACKEND_LIBDISPATCH` in `__config_site`) and, to silence an ld version warning, `-mmacosx-version-min=<current macOS>`; `std::function` copies an lvalue closure twice.

### S14 - Clang, "Standard C++ Modules"

- <https://clang.llvm.org/docs/StandardCPlusPlusModules.html> (upstream docs, retrieved 2026-09-28): `--precompile` to produce a BMI (`.pcm`), `-fmodule-file=<name>=<path>` or `-fprebuilt-module-path=` to consume it; `.cppm` is recognised as an interface unit. Apple clang 21 additionally needs `-fcxx-modules` and `-x c++-module` [S13].

## In this repo

### S15 - NSSC I notes 10 and 07

- [`../../../ws2026/numerical-simulation-and-scientific-computing-i/notes/10-software-engineering-for-scientific-computing.md`](../../numerical-simulation-and-scientific-computing-i/notes/10-software-engineering-for-scientific-computing.md): git workflow, Make and CMake (with a verified CMake run), compiling and linking, lldb, sanitizers, testing, licences. Note 01 links there instead of repeating it.
- [`../../../ws2026/numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md`](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md): OpenMP, racy-counter losses (60-90 %) and false-sharing costs measured on the same machine. Note 14 cites its numbers instead of re-measuring.

### S18 - search record: what public material exists (negative result)

- GitHub API and web search, 2026-09-28: no organisation `iue-tuwien`, `advprogcpp` or similar (HTTP 404); the `advprog` organisation is an unrelated Polish course; user `manstetten` has 5 public repos (S5 and four unrelated/forks); organisation `cppitems` holds S3, S4, S6, with the last content push 2022-02-28 (S3) and the last site push 2022-10-05 (S6). Repository search for "360.251", "advprog cpp", "manstetten" found nothing newer.
- Consequence: 2022W-2026W hand-outs, if public at all, are not on GitHub under these names. They are probably on the institute's Gitea (S3 names it) or TUWEL (S1 says "TUWEL from 01.10.2026"), both needing a login.
