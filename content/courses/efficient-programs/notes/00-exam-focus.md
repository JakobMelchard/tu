# 00 Exam focus: what is assessed and how to prepare for it

**There is no past paper and there cannot be one.** The exam is oral [S1]
[S2]. What exists instead is better: the lecturer's slides, script and last
year's three exercise sheets are public [S2]. This note says what is graded,
what the exercises looked like in 2025W, what is new and unexplained in 2026W,
and how to weight the eleven notes.

## What is graded [S1] [S2]

| source | statement |
|---|---|
| TISS, examination modalities [S1] | "The grade is based on the exercises and on an oral examination." |
| TISS, ECTS breakdown [S1] | 3 ECTS = 75 h: lectures 20 h, **exercises 50 h**, "preparing for the exam, and exam" 5 h |
| Homepage, grading [S2] | exercises "where you have to deliver some results"; "The grade will be based on an oral exam that checks your knowledge of the course material, as well as whether you can explain how you achieved the exercise results." |
| Exercise sheets [S5] [S6] [S7] | "Please do not just answer the questions, but document how you arrived at the answers (this is also useful for preparing yourself for the interview part of the exam later in the semester)." |
| TISS, mode of examination [S1] | immanent |

Read together: the exercises are the work (50 of 75 h) and the interview is
where they are graded. Two consequences. First, every number you submit
must come with the command that produced it and a sentence on why it came
out that way. Second, the interview will ask *about your transcript*: "why
did the L1 miss count jump where it did", "what does `:u` do", "why is the
list loop 5 cycles per iteration" [S3 p.16]. (That the interview asks about
the transcript is our reading of [S2] and the sheets, not a stated rule.) The five questions at the end of each
note are written in that register.

## What "exercises" meant in 2025W [S5] [S6] [S7]

Three sheets, each a directory in a git project on `g0`, answered in a
`ExercisesN.txt` with shell transcripts (`script -f`) as evidence:

| sheet | deadline 2025W | topic | notes |
|---|---|---|---|
| 1 [S5] | 24.10 | resource usage of whole programs (time, memory, user versus system mode) and profiling with `gprof` and `gcov` | [02](02-measurement-and-profiling.md) |
| 2 [S6] | 03.11 | latency versus instruction throughput, measured with `cycles:u` and `instructions:u` | [03](03-hardware-latency-and-throughput.md) |
| 3 [S7] | 09.12 | measuring cache, TLB and DRAM parameters with `perf stat` on a pointer-chasing program | [04](04-memory-hierarchy.md) |

The sheets are graded; this wiki explains the tools and the hardware behind
them, and does not answer the sheets' questions.

Question types, then: (a) read a tool's output and answer a factual question
from it; (b) design an experiment that isolates one hardware parameter and
report the parameter; (c) modify code under constraints to hit a counter
target. Notes 02, 03 and 04 cover the theory behind each.

In 2025W the seven lectures were the consecutive Mondays 06.10 to 17.11 [S10],
so the deadlines fell four days after lecture 3 (Fri 24.10), on the evening of
lecture 5 (Mon 03.11) and three weeks after lecture 7 (Tue 09.12). 2026W has a
two-week gap (26.10, 02.11) [S1], so the calendar analogy (about 23.10, 02.11,
09.12) and the lecture-count analogy (after 19.10, on 16.11, about three weeks
after 30.11) disagree for sheet 2. Both are our extrapolation; nothing for
2026W is published yet. Check TUWEL once it appears: the 2026W TISS page shows
no TUWEL link yet [S1].

## New and unexplained in 2026W: the InfLab bookings [S1] [S10]

| date | time | rooms | label |
|---|---|---|---|
| Wed 04.11.2026 | 10:00 to 14:00 | InfLab Q\*bert, Frogger, Pong (all three) | "Test 1" |
| Fri 20.11.2026 | 09:00 to 13:00 | all three | "Test" |
| Fri 04.12.2026 | 09:00 to 13:00 | all three | "Test" |
| Fri 18.12.2026 | 09:00 to 13:00 | all three | "Test" |

2025W had none of these; it had the seven Monday lectures and nothing else
[S10]. Neither TISS nor the homepage says what they are. Three labs booked in
parallel for four hours means many people at machines, not a queue outside an
office. Readings that fit the evidence: a supervised lab test replacing or
supplementing the interview ("Test 1" suggests a numbered series), or
interview slots held in the lab so that the student can show the transcript.
Do not plan around either reading; ask in the first lecture on 05.10.

**Registration.** Registration and deregistration close together on 13.10.2026
23:59 [S1].


## Questions to ask on 05.10

1. What are the InfLab dates on 04.11, 20.11, 04.12, 18.12: tests, interviews, help sessions? Is attendance at all of them required?
2. How many exercise sheets, when, and are the 2025W sheets representative?
3. Is the oral exam per person or per group, how long, and when (the Friday slots?).
4. Which TUWEL course; when do `g0` accounts arrive (they are created in batches on Tuesdays [S2], so the first Tuesday after registering is the earliest batch, our inference).
5. For CSE: does the VU count towards a module or only as a free elective (homepage says module "Computational Informatics" [S2], TISS says elective [S1]).

## How to weight the notes

The deck spends its 100 slides as follows [S3] (sections as in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md)): 13 on why,
method, tools and the compiler (p.1 to 13), 8 on hardware latency and `perf`
(p.14 to 19, 22 to 23), 2 on memory (p.20 to 21), 4 on algorithms and
parallelism (p.24 to 27), 5 on SIMD (p.28 to 32), 6 on specification and
languages (p.33 to 38), **30 on Bentley's transformations** (p.39 to 68), 6 on
memory and energy efficiency (p.69 to 74), 11 on TSP (p.75 to 85), 11 on
matmul (p.86 to 96), 4 on I/O (p.97 to 100). The exercises spend
their hours on tools (ex1), latency vs throughput (ex2) and the memory
hierarchy (ex3), i.e. on notes 02, 03 and 04. So:

- **Must be fluent** (they are the exercises and therefore the interview):
  02 tools, 03 latency/throughput, 04 memory hierarchy.
- **Must be able to explain each step** of the two worked examples, because
  they are the deck's way of teaching everything else: 08 TSP, 09 matmul.
- **Must know by name and condition**: 07 the transformation catalogue (30
  slides; the interview can pick any one and ask "when is this valid, what
  does it cost").
- **Should be able to argue**: 01 method and compiler, 05 algorithms and
  specification, 06 vectorisation recipe.
- **Read once**: 10 energy and I/O.

## What the learning outcome commits the interview to [S1]

"Students are able to determine whether a program is sufficiently efficient,
to find inefficient parts, and to make them more efficient." Three verbs,
three question families: *is this fast enough* (note 01: latency budgets,
`time`), *where is the time* (note 02: profile, counters, TopDown), *what do
I change and what do I expect* (notes 03 to 09). Practise answering each in
two sentences with a number in it.

## About the questions in these notes

All of them are ours, written in the interview register the sheets describe:
"you measured X, explain X". None is a recovered exam question, because none
exists.

## Exam-style questions

1. **What is the grade based on, and what follows for how you write up an exercise?** On the exercises and an oral examination [S1]; the oral exam checks your knowledge of the material and "whether you can explain how you achieved the exercise results" [S2]. So every submitted number needs the command that produced it and the reasoning from counter to answer; the sheets themselves ask you to document how you arrived at the answers [S5] [S6] [S7].
2. **Ex3's example `memory1 random 5000 8` gives 501 793 612 cycles, 35 203 L1 misses and 449 dTLB misses for 100 M accesses. What does it measure?** $3.5 \cdot 10^{-4}$ L1 misses per access, so every access hits L1; the accesses are dependent, so cycles per access is the load latency: 5 cycles for an L1 hit on the course machine [S7].
3. **What is exercise 2 meant to teach, and which of its loops has spare issue slots?** In the sheet's words, how latency and bandwidth (instruction execution bandwidth) influence performance [S6]. The list loops are latency bound by the dependent load, 5 c/iteration on Rocket Lake [S3 p.16], so independent instructions fit into them almost for free; the array loops are not (note 03).
4. **Why does ex1 tell you to delete `magichex.gcda` before the gcov run?** The `.gcda` counts accumulate over runs, and the answer must be about exactly one run with the given invocation [S5] [S18].
5. **What is known about the 2026W InfLab "Test" dates and what do you do about them?** Four bookings (Wed 04.11 10:00 to 14:00, Fri 20.11, 04.12, 18.12 09:00 to 13:00), three labs each, labelled only "Test 1"/"Test", explained nowhere and absent in 2025W [S1] [S10]. Keep the slots free and ask on 05.10.
