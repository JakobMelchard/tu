# 05 Algorithms, specification, languages

Slides 24 to 25, 33 to 38 [S3]; the script's sections *Algorithmen und
Datenstrukturen* and *Die Rolle der Programmiersprache* [S4]. The topic:
the decisions above the source level that fix efficiency before any
transformation, and the limits of the tool most people use to make them,
the O-notation.

## Data structures and algorithms [S3 p.24] [S4]

Three positions [S3 p.24]: an efficient implementation of an inefficient
algorithm is a waste of time; an efficient algorithm without regard to
implementation efficiency (the slide asks, the script answers that a good
choice still gains from an efficient implementation [S4]); the target is an
efficient implementation of an efficient algorithm. Constraints: an efficient
algorithm or data structure may conflict with simplicity; the data structure
choice affects much of the code (the TSP's `visited[]` → `tour[]` change
touched the whole function, note 08); abstract data types hide costs,
producing inefficiency by *interface overhead* and *lack of cost awareness*
[S3 p.24]. How to recognise a good choice: by measured efficiency together
with the other goals, not by the O-class alone [S4].

## What O(...) hides [S3 p.25] [S4]

Helpful, but the slide lists its limitations: it often looks at the **worst
case**; it **counts certain operations** that are not always relevant for run
time (the script: compared with cache misses); it **ignores constant
factors**, which the script says often matter more than **logarithmic
factors** [S3 p.25] [S4]. The sorting examples add a fourth blind spot,
**locality**. The slide's examples:

| problem | algorithm | complexity | reality |
|---|---|---|---|
| substring search, pattern $m$ in text $n$ | naive | $O(mn)$ worst, $O(n)$ best | usually fastest: average near $O(n)$, tiny constant |
| | Knuth-Morris-Pratt | $O(n)$ | "usually slower than the simple algorithm" |
| | Boyer-Moore | $O(n)$ worst, $O(n/m)$ best | skips ahead by up to $m$ (general knowledge: wins on long patterns) |
| sorting | quicksort | $O(n^2)$ worst, $O(n \ln n)$ usual | good spatial and temporal locality |
| | heapsort | $O(n \ln n)$ | bad locality |
| | mergesort | $O(n \ln n)$ | good locality |

The script cites Fenwick 2001 (*Some Perils of Performance Prediction*) for
the string-search case [S4].

Constant vs logarithmic factor, made quantitative with the latency table
[S3 p.14] (our estimate, not a slide): a linear scan over $n$ sorted keys
costs about $n/2$ predictable, vectorisable compares, say $c_\ell \approx
0.25$ c each; binary search costs $\log_2 n$ compares, each a data-dependent
branch that mispredicts half the time on random keys, so
$c_b \approx 0.5 \cdot 20 = 10$ c. They cross where

$$\frac{n}{2} c_\ell = c_b \log_2 n \;\Rightarrow\; n \approx 80\,\log_2 n \;\Rightarrow\; n \approx 770.$$

Below several hundred elements the $O(n)$ scan beats the $O(\log n)$ search
on these constants (a branchless binary search moves the crossover down).
The numbers are assumptions, the shape is the point: a log factor buys
nothing until $n$ is large enough to pay the constant.

## Efficiency in the specification [S3 p.33] [S22]

The copy-a-block example, three specifications of the same operation:

| | `memmove` (C), `move` (Forth) | `cmove` (Forth), `rep movsb` (AMD64) | `memcpy` (C) |
|---|---|---|---|
| no overlap | source → dest | source → dest | source → dest |
| start of dest inside source | source → dest | pattern replication | undefined |
| start of source inside dest | source → dest | source → dest | undefined |
| implementation | decision (copy direction) | byte by byte | bigger units |
| efficient implementation | | decision | |
| | well specified | **over**-specified | **under**-specified |

Reading of the slide: `memmove`'s implementation decides the copy direction;
`cmove`'s definition is byte by byte (the pattern replication is observable),
so an efficient implementation must first decide whether the replication
case applies and fall back to bytes if it does; `memcpy` may copy in bigger
units because overlap is undefined, which pushes the risk to the caller.
Undefined behaviour in general: plus, the compiler can optimise more; minus,
the programmer should optimise less and should not make use of
implementation properties [S3 p.33].
And **Hyrum's law** [S22]: with enough users, every observable behaviour
will be depended upon regardless of the contract, so an implementation
cannot in practice change what its users observed. Consequence for design:
specify what you need, no more (leave room for efficient implementations)
and no less (do not create UB traps).

## Programming languages [S3 p.34 to 38] [S4]

Four sources of language-level (in)efficiency: **inherent** (the language
definition forces it), **idiomatic** (the usual style does, the language
would allow better), **compiler** (implementation quality), and efficiency
gained through **development speed** (time left for tuning, a more flexible
program). Examples:

- *Aliasing, C vs Fortran* [S3 p.35]: in `f(double a[], double b[], double c[], long n)` C must assume `c` may overlap `a` or `b` (a store to `c[i]` may change `a[i+1]`), Fortran forbids aliased arguments; inherent for C, idiomatic in that `restrict` fixes it (note 06).
- *Nested data, Java vs C* [S3 p.36]: `struct mystruct a[10000]` is one contiguous block; Java objects force `struct mystruct *b[10000]`, an array of pointers, one indirection and one cache line per element. Inherent.
- *Scaling in address arithmetic, C vs Forth* [S3 p.36]: C scales `p + d` by `sizeof`, so a difference `q - p` and a re-add are two divisions/multiplies; Forth works in bytes. Inherent/idiomatic.
- *Compiler efficiency* [S3 p.37]: speedup over Gforth with code copying (= 1, log scale 1/4 to 32) on eleven benchmarks, for Gforth threaded code (0.3 to 0.8), the Gforth steps ip-update optimisation, stack caching and static superinstructions (about 1.1 to 2.7), SwiftForth, VFX Forth (up to about 8) and, for the four benchmarks with a C version (siev, bubble, matrix, fib), gcc `-O0`, `-O1`, `-O3`, reaching about 30 (fib, `-O1`); `-O3` is slower than `-O1` on bubble and fib. Values read off the bar chart.
- *0-terminated strings* [S3 p.38]: `strlen` is $O(n)$ and `strcat(strcat(strcat(s,s1),s2),s3)` rescans `s` three times, quadratic in the number of appends. Inherent (the representation), idiomatic (the call chain).
- *"C++ is slow"*: idiomatic (allocation-heavy style), not inherent [S3 p.38].
- *Microbenchmarks vs programming contests* [S3 p.38] [S4]: C and Fortran compilers win microbenchmarks; in contests with free language choice they do not, because development speed decides what gets tuned.
- *Riyadh airport* [S3 p.38] [S4]: with Fortran and assembly too slow, with Forth (implemented by an interpreter) and assembly fast enough. Neither source says why; the slide lists it after "programming contests (development speed)".
- *Assembly* [S4]: can still help in places, needs specialist knowledge and is often processor specific (the script's example: `LODSD` on the 386 vs the 486).

## Worked example: an abstraction cost you can compute

A `std::vector<std::vector<double>>` matrix costs one heap block per row:
$n$ pointers to chase, rows not contiguous, no blocking possible, one TLB
entry per row for $n \ge 512$. A flat array with `i*n+j` costs one
multiply-add per access and keeps locality. Same $O(n^3)$ multiply, a factor
of several in cache and TLB misses (note 09's `mm1 700` is exactly the
one-page-per-row pattern [S8]). The O-class did not change; the constant
did.

## Pitfalls

- Choosing by worst-case O-class where the average case is what runs.
- Trusting a log factor to beat a constant at $n = 100$.
- Wrapping a hot data structure in an interface that hides its cost.
- Specifying more than needed (byte-by-byte semantics) or less (UB on
  common inputs).
- Assuming a language's idiom is its limit; assuming the compiler will
  remove an inherent indirection.

## Exam-style questions

1. **Name three limitations of O-notation for predicting run time and give the slide's example for one.** Worst case only; counts operations that may not dominate (misses vs compares); ignores constants and locality. Example: KMP is $O(n)$ but usually slower than naive $O(mn)$ search, whose average is near $O(n)$ with a smaller constant [S3 p.25].
2. **Why is `memcpy` allowed to be faster than `memmove`, and what does the caller pay?** `memcpy` leaves overlapping copies undefined, so the implementation may copy in large units in any order; `memmove` must handle overlap and decides at run time. The caller pays with undefined behaviour on overlap [S3 p.33].
3. **What is Hyrum's law and what does it imply for changing an implementation?** With enough users, all observable behaviours of a system will be depended upon regardless of the contract; so an implementation detail, once observable, is de facto part of the interface and cannot be changed freely [S3 p.33] [S22].
4. **Distinguish inherent and idiomatic inefficiency with one example each.** Inherent: Java's object references force an array of pointers where C has an array of structs. Idiomatic: chained `strcat` rescans the string each time; the language allows keeping the end pointer [S3 p.36, 38].
5. **When does an $O(n)$ linear scan beat an $O(\log n)$ binary search, and why?** For small $n$ (below several hundred with our assumed constants and the lecture's 20 c misprediction): the scan's compares are predictable and vectorisable (fractions of a cycle each), the search's are data-dependent branches that mispredict about half the time (≈10 c each on average); the crossover is where $n c_\ell / 2 = c_b \log_2 n$ [S3 p.14, 25].

Code: none specific; `src/c/matmul_steps.c` uses the flat layout the worked example argues for. Sources: [S3 p.24 to 25, 33 to 38] [S4] [S8] [S22].
