# Topic map: slide deck sections → sources → notes → code

The deck [S3] (100 slides, 2025-11-17) is the structural index; TISS's
"Subject of course" list [S1] is the same content in one sentence. One row per
deck section, in deck order. Notes are numbered in this order.

| slides [S3] | section | other sources | our note | our code (`../src/c/`) |
|---|---|---|---|---|
| 1–8 | Do we need more efficiency, types, costs, how much, other goals, extreme positions, 80–20, the method loop | [S4] §§ Ist Effizienz nötig … Methoden | [01](../notes/01-why-efficiency-and-method.md) | none |
| 9 | Tools: `time`, `gprof`, `gcov` | [S5] Q1–Q11, [S17], [S18], [S19] | [02](../notes/02-measurement-and-profiling.md) | `profile_demo.c`, `make gcov` |
| 10–13 | Is this not a job for the compiler; stumbling blocks (aliasing, side effects) | [S4] § Was können optimierende Compiler | [01](../notes/01-why-efficiency-and-method.md), [06](../notes/06-vectorisation-and-the-compiler.md) | none |
| 14–19 | Hardware properties: latency table, out-of-order, recurrences, latency vs throughput | [S4] § Hardware-Eigenschaften (2001 table), [S13], [S6] | [03](../notes/03-hardware-latency-and-throughput.md) | `recurrence.c`, `branch_predict.c` |
| 20–21 | Memory, virtual memory, TLB, caches, Skylake parameters | [S7] (the memory1 exercise), [S13] | [04](../notes/04-memory-hierarchy.md) | `pointer_chase.c` |
| 22–23 | `perf stat`, `perf record`/`annotate`/`report`, TopDown | [S4] § Messwerkzeuge, [S16], [S14] | [02](../notes/02-measurement-and-profiling.md) | `profile_demo.c`, `make perf` |
| 24–25 | Data structures and algorithms, O(...) and its limits | [S4] § Algorithmen und Datenstrukturen | [05](../notes/05-algorithms-specification-languages.md) | none |
| 26–27 | Parallel processing, triple buffering | none | [03](../notes/03-hardware-latency-and-throughput.md) | none |
| 28–32 | SIMD, auto-vectorisation, the vectorisable-loop recipe, manual SIMD (popcount) | [S8] mm2/mm3 | [06](../notes/06-vectorisation-and-the-compiler.md) | `matmul_steps.c` (`ikj`) |
| 33 | Efficiency in specification: memmove/memcpy, undefined behaviour, Hyrum's law | [S22] | [05](../notes/05-algorithms-specification-languages.md) | none |
| 34–38 | Programming languages: inherent/idiomatic/compiler efficiency, Gforth chart | [S4] § Die Rolle der Programmiersprache | [05](../notes/05-algorithms-specification-languages.md) | none |
| 39–68 | Bentley's source-level transformations (30 slides) | [S11], [S4] § Beispiel für Optimierung | [07](../notes/07-source-level-transformations.md) | `tsp_greedy.c`, `branch_predict.c` |
| 69–70 | Memory efficiency: packing, factoring, interpreters | none | [10](../notes/10-memory-energy-io.md) | none |
| 71–74 | Energy efficiency, DVFS, race to idle | [S21] | [10](../notes/10-memory-energy-io.md) | none |
| 75–85 | TSP example tsp1 → tsp9, tspi4 | [S9] sources, [S4] cycle counts, [S11] | [08](../notes/08-tsp-worked-example.md) | `tsp_greedy.c` |
| 86–96 | Matrix multiply mm1 → mm7, ATLAS, OpenBLAS | [S8] page + sources | [09](../notes/09-matmul-worked-example.md) | `matmul_steps.c` |
| 97–100 | I/O, asynchronous I/O, system calls, io_uring | none | [10](../notes/10-memory-energy-io.md) | none |

Plus [00-exam-focus.md](../notes/00-exam-focus.md) (format, not a topic).

## Exercise sheets → notes

| sheet | what it measures | notes | our stand-in |
|---|---|---|---|
| [S5] Exercises 1 | `/bin/time` on unknown binaries; gprof and gcov on `magichex.c` | 02 | `profile_demo.c` |
| [S6] Exercises 2 | instructions vs cycles in list and array loops (latency vs bandwidth) | 03 | `recurrence.c` |
| [S7] Exercises 3 | memory hierarchy with `memory1` and `perf stat` events | 04 | `pointer_chase.c` |

## Where the sources disagree or are silent

- **CSE curriculum status.** The homepage [S2] says mandatory elective in
  module "Computational Informatics"; TISS [S1] says plain elective for
  066 646. TISS is the registration system; trust it until the curriculum PDF
  says otherwise.
- **InfLab "Test" bookings** [S1] exist in no other source and did not exist
  in 2025W [S10]. Unexplained; see note 00.
- **Slide details that disagree with each other or with the examples.**
  p.17's diagram labels the pointer-chase load 4 c, yet the measured loop
  takes 5 c/iteration (and [S7]'s L1-hit chase also gives 5 c); p.14 prints
  "50–ns" for DRAM with no upper bound, p.21 says ≈ 50 ns; p.88 gives 0.84
  c/It for `ikj -O3`, p.91 0.85 for the same `mm2`; the slides' `mm3` uses an
  8-double `v8d`, the page's `mm3.c` a 4-double `v4d` [S3] [S8]. The notes
  quote each figure with its page.
- **The numbers.** Slides quote Rocket Lake (p.16–18, [S7]) and Skylake
  (p.21); the matmul page an Ivy Bridge i3 [S8]; the script a Celeron and
  2001-era hardware [S4]; our tables an M3 Pro [S19]. Same shapes, different
  constants: learn the shapes, measure the constants on g0.
