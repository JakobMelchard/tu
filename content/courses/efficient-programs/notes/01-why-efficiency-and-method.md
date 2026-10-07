# 01 Why efficiency, and the method

Slides 1 to 13 [S3]; prose in the script's sections from *Ist Effizienz
nötig?* to *Was können optimierende Compiler, was nicht?* [S4]. The
topic: when to care about efficiency, what it costs to care and not to care,
and the procedure that keeps optimisation from wrecking the program.

## Do we need more efficiency? [S3 p.1] [S4]

"Computers are fast enough" is true for some software and false for four
recognisable classes: software that was slow and still takes noticeable
time; software now invoked far more often (fast feedback changes the
workflow); software whose inputs grew with the hardware; software that spent
the hardware gain on functionality. Plus energy [S3 p.1]. The script's
exercise: name a product for each of its five cases (these four plus the
software that is already fast enough) [S4].

## Kinds of efficiency [S3 p.2]

Run time: CPU, disk/SSD, network, other I/O. Memory: RAM, ROM (embedded),
persistent storage, removable storage. The script adds efficiency *of use*
(requirements, UI) [S4]. The course is about CPU time first, memory second,
I/O and energy in note 10.

## Costs of inefficiency [S3 p.3] [S4]

User time (waits of 1 to 10 s cost about three times the wait in lost user
time [S4]), changed workflow, missed real-time requirements, more expensive
hardware (servers, or embedded parts times the production run), energy.
Bentley's 1982 prices: \$200 per CPU hour of a DEC-10 against \$50 per
programmer hour [S4]. Today programmer time is the dear resource (our remark,
not the script's), one more reason the *method* below measures before it
optimises.

## How much efficiency is sensible? [S3 p.4] [S4]

Latency budgets below which further speed is invisible:

| interaction | budget |
|---|---|
| command and response | 300 ms feels immediate |
| hand-ear coordination (music) | 20 ms |
| animation | one screen refresh, 7 to 16 ms (60 to 144 Hz) |

Two stop rules: a different component dominates and cannot be improved
(then improving yours is pointless), and the commercial one: optimise while
customers pay more for the speed than the optimisation costs [S4]. For
library components (STL) no upper limit can be given; it depends on the
caller [S4].

## Other goals, or the cost of efficiency [S3 p.5] [S4]

Correctness ("If a program is not correct, it matters little how fast it
runs", Kernighan and Plauger), simplicity, development effort ("Debugging is
twice as hard as writing the code in the first place …", Kernighan),
maintenance, time to market, security. Optimisation trades against all six.

## Extreme positions and the observations that resolve them [S3 p.6 to 7] [S4]

- *No efficiency considerations*: risk of an unusable program, or of large
  changes late in the cycle.
- *Optimise everything*: high development and maintenance cost, a complex
  program in which the important optimisations are overlooked.
- Observations: the **80/20 rule** (a small part of the code takes most of the
  time) and **programmers are bad at predicting hot spots** [S3 p.7]. The
  second is why the first cannot be exploited by thinking.
- Therefore: design and code for simplicity, flexibility and maintainability;
  **measure**; optimise the critical parts, stepwise, staying simple so later
  steps remain possible [S3 p.7] [S4].
- Remaining problem: inefficiency fixed by the specification or the design.
  Answer: prototyping ("plan to throw one away", Brooks) [S4]; note 05 has
  the memmove/memcpy example.

## The method [S3 p.8] [S4]

```
unoptimised program
      |
    tests  --pass-->  measurement  --sufficiently efficient-->  done
                          | too inefficient
                      profiling
                          |
                  program transformation
                          |
                        tests  --pass--> measurement ...
```

Four questions and their tools [S4]: *is it efficient enough* (measurement,
instrumentation); *where does the time go* (profiling, performance counters);
*how do I make this part faster* (correctness-preserving transformation,
notes 06 to 09); *did I break it* (an automatic test system with test cases).
The loop invariant is "tests pass"; the exit condition is the latency budget
above. Every step is one transformation, measured on its own: that is also
what the PR presentation must show, "which optimization steps worked how
well" [S2].

## Is this not a job for the compiler? [S3 p.10 to 13] [S4]

Compilers apply correctness-preserving transformations too, but [S3 p.10]:

1. they take the **input program as the specification**, so they cannot use
   don't-care results or application knowledge (nothing tells `gcc` that
   `sqrt` may be dropped from a comparison, note 08);
2. they must avoid **pessimisations** for any program, so they are
   conservative where the programmer can be sure;
3. they only do what is **cheap in compile time and space**;
4. they only do what is **useful for many programs** (or benchmarks);
5. optimisations **depend on each other**: one missed enabling step blocks
   the rest.

Yet they do surprising things: in `*s1==*s2 && *s1!=0 && *s2!=0` gcc deletes
the third test entirely (it is implied by the first two) [S3 p.10] [S4]. The
script's advice: leave such a redundant test in the source, because without
it the string-compare routine no longer visibly terminates at the end of
`s2`; where the compiler cannot remove such code, keep the optimised-away
form as a comment [S4].

The chart [S3 p.11] plots the normalised speed (log scale, 1 = fastest) of
tsp1 to tsp9 (note 08) under five `-O3` compilers from the late 1990s
(gcc-2.7.2.3, egcs-1.1.2) to 2014/15 (gcc-5.2.0, clang-3.5) and under
gcc-5.2.0 and clang-3.5 at `-O0`. Read off the plot (±10 %): gcc `-O0` is
about 6× slower than gcc `-O3` at every step; clang `-O0` is 1.4× (tsp1) to
2.3× (tsp9) slower than clang `-O3`; the source steps tsp1 → tsp9 give about
3× under gcc `-O3` and about 10× under clang `-O3` (clang starts slow and
catches up at tsp3); from tsp4 on the old compilers are within about 1.5× of
the new ones. Compiler and programmer factors are of the same order and
multiply; neither replaces the other.

**Stumbling blocks** [S3 p.12 to 13] [S4]: the compiler often *could* do the
optimisation, but a detail in the source forbids it. The slide's example is
an argmin loop in three spellings, compiled for RISC-V by gcc 10 `-O3`:

```c
for (i=0, best=0; i<n; i++) if (a[i]<a[best]) best=i;     /* index form: 7 instructions per iteration */
for (p=a, bestp=a, endp=a+n; p<endp; p++) if (*p<*bestp) bestp=p; /* pointer form: 6 */
for (i=0, bestp=a; a+i<a+n; i++) if (a[i]<*bestp) bestp=a+i;      /* index form the compiler can convert */
```

The first form keeps `i` and `best` alive because `best` is returned and
because `i<n` cannot be replaced by `p<endp` without knowing that pointer
arithmetic does not wrap; the third form removes both obstacles and gets the
pointer code [S4]. General blocks [S3 p.13]:

- **Aliasing**: `*p = …; … = *q;` cannot be reordered unless the compiler knows
  `p != q`; `a[i] = a[i]*b[j]` in a loop cannot hoist `b[j]` if `a` and `b`
  may overlap (note 06, `restrict`).
- **Side effects and exceptions**: `if (flag) printf(…)` cannot be moved;
  `a[i] = a[i] + 1/b[j]` cannot hoist `1/b[j]` because the division may trap
  when the loop body would not have executed.
- **Zero-trip loops**: hoisting out of a loop that may run zero times changes
  behaviour unless the compiler peels [S4].

How far to rely on the compiler: the next version, another compiler or a
small edit can lose an optimisation, and finding out what a compiler does
can cost more than doing it by hand; on the other hand people still write
code shaped for processors and non-optimising compilers of decades ago [S4].
The course's position: let the compiler do the mechanical part, remove the
stumbling blocks, and measure.

## Amdahl for one program

Not on the slides; the standard formula (Amdahl's law) that quantifies the
80/20 observation. If a fraction $f$ of the run time is in the part you speed up by a factor $s$,
the whole program speeds up by

$$S = \frac{1}{(1-f) + f/s}, \qquad S < \frac{1}{1-f}.$$

So the profile ($f$) bounds every step before you start, and a step on a 10 %
part can never give more than 1.11×. This is the quantitative form of the
80/20 rule and the reason the method profiles first.

## Worked example: `profile_demo`

`src/c/profile_demo.c --bench` on the M3 Pro [S19], one of four runs (the
absolute times vary ±10 % between runs, the fractions do not): trial-division
prime count 73.8 ms, sieve 3.8 ms, cheap checksum 2.2 ms; total 79.8 ms, the
trial function is $f = 0.925$ (0.92 to 0.93 over the four runs). Replacing
trial division by the sieve is $s = 73.8/3.8 = 19.4$, so

$$S = \frac{1}{0.075 + 0.925/19.4} = 8.2\times$$

(8.0 to 8.2 over the four runs), and the program would drop to about
$3.8 + 3.8 + 2.2 = 9.8$ ms. The checksum, 3 % of the original, is then 22 %
of the new program: worth optimising now, and not before. Two lessons of the method
in one run: the profile decides the order of steps, and the profile changes
after every step.

## Pitfalls

- Optimising before measuring (the hot spot is not where you think [S3 p.7]).
- Measuring `-O0` (the chart on p.11: a factor 1.4 to 7 below `-O3`).
- Comparing against the wrong budget: a 50 ms command-line tool is done.
- Cleverness that the compiler would have done anyway, paid for in
  readability; and the opposite, a stumbling block that costs a factor 2.
- Skipping the tests step of the loop; a fast wrong program is a regression.
- Forgetting that a change on the critical path moves the critical path.

## Exam-style questions

1. **Name the steps of the optimisation method and say what breaks if one is skipped.** Tests, measure, profile, transform, tests again. Skip measuring: you optimise a program that was fast enough. Skip profiling: you optimise the wrong 80 %. Skip the second tests: you ship a bug. Skip transforming one step at a time: you cannot attribute the effect [S3 p.8].
2. **Why can a programmer beat an optimising compiler at all?** The compiler treats the source as the specification, must never pessimise any program, and only spends cheap, widely useful effort; the programmer knows don't-care results, value ranges and which code is hot [S3 p.10]. Example: dropping `sqrt` from a distance comparison (monotone), which the compiler may not do because the source asks for `sqrt`.
3. **A loop hoists `1/b[j]` out in one program and not in another. Why might that be?** Side effects or exceptions: if the loop can execute zero times, hoisting the division would trap where the original did not; the compiler needs to prove the trip count or peel one iteration [S3 p.13] [S4]. Also aliasing: if `a` and `b` may overlap, `b[j]` is not loop-invariant.
4. **Your profile says 60 % of the time is in one function. What is the best total speedup from that function alone, and what should you do after achieving it?** $1/(1-0.6) = 2.5\times$. Re-profile: the remaining 40 % is now the whole program and its internal distribution decides the next step.
5. **Give two latency budgets from the lecture and say what they imply for a program that already meets them.** 300 ms for command-response, 20 ms for musical latency, one frame (7 to 16 ms) for animation [S3 p.4]. A program under its budget needs no CPU-time optimisation; effort goes to the other goals (correctness, simplicity, maintainability) or to another kind of efficiency (memory, energy).

Code: `src/c/profile_demo.c` (the Amdahl example; run `--bench`). Sources: [S2] [S3 p.1 to 13] [S4] [S19].
