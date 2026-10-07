# 04 Memory hierarchy

Slides 20 to 21 [S3], the matmul page's TLB analysis [S8], and exercise 3
[S7], which is a complete lab on this topic. The topic: how an address turns
into a latency, and how to measure the parameters of a machine you were not
told about.

## Three views of an access [S3 p.20]

*Simple*: CPU sends address `0x123abc` to RAM. *Virtual memory*: the MMU
translates the virtual page number to a physical one via the page table;
`0x123abc` becomes `0x456abc`. *Performance*: the translation is cached in
the **TLB** and the data in the **cache**; both are small and both miss.

## Caches [S3 p.21]

Data moves in **lines** of $B$ bytes (64 on x86, 128 on Apple M-series
[S19]). A cache of capacity $C$ with associativity $A$ (ways) has

$$S = \frac{C}{A\,B}\ \text{sets}, \qquad W = \frac{C}{A} = S\,B\ \text{bytes per way},$$

and an address $a$ decomposes as offset $a \bmod B$, set index
$\lfloor a/B \rfloor \bmod S$, tag the remaining high bits. Two addresses
compete for the same set iff they are congruent modulo $W$. The slide's
Skylake (Core i*-6xxx) figures:

| level | size | line | ways | latency | derived: sets, way size |
|---|---|---|---|---|---|
| L1 data | 32 KB | 64 B | 8 | 4 c | 64 sets, 4 KB per way (= page size) |
| L1 instruction | 32 KB | 64 B | 8 | | |
| L2 | 256 KB | 64 B | 4 | 12 c | 1 024 sets, 64 KB per way |
| L3 | 2 to 8 MB | 64 B | 4 to 16 | ≥ 42 c | shared between cores |
| DRAM | | | | ≈ 50 ns | |
| L1 DTLB | 64 entries (4 KB pages), 32 entries (2 MB) | | 4 | | reach 64 × 4 KB = 256 KB |
| L2 TLB (STLB) | 1 536 entries (4 KB, 2 MB) | | 12 | 9 c | reach 6 MB with 4 KB pages |

The course machine is a Rocket Lake, and the sheet says explicitly that its
values differ from slide 21 [S7]; measuring them is exercise 3.

**Locality** [S3 p.21]: temporal (the same address again soon) and spatial
(a neighbouring address soon) are *program* properties; the cache pays them
back. **Miss types**: compulsory (first touch of a line; a program property),
capacity (working set larger than $C$), conflict (more than $A$ live lines in
one set although the cache is not full).

Cost model: average memory access time
$t = t_{\text{hit}} + m \cdot t_{\text{miss}}$ per level, and for a stream with
stride $s$ bytes over a region that does not fit the cache, the compulsory
miss rate is

$$m = \min\!\Bigl(1, \frac{s}{B}\Bigr)\quad\text{(one miss per } B/s \text{ accesses when } s \le B\text{)}.$$

For a column walk of a row-major $n \times n$ double matrix, $s = 8n$: every
access misses once $8n \ge B$, i.e. $n \ge 8$, and needs its own TLB entry
once $8n \ge$ page size, i.e. $n \ge 512$ (note 09).

## TLB and pages [S3 p.20 to 21] [S8]

Translation is per page (4 KB on x86 by default, 2 MB huge pages, 16 KB on
Apple Silicon). A TLB miss that hits the STLB costs its latency (9 c on
Skylake); a miss in all levels is a **page walk**: several dependent loads
of page-table entries, themselves cached, tens of cycles. TLB **reach** is
entries × page size: with 64 entries and 4 KB pages, any working set of more
than 256 KB touched page by page misses the L1 TLB, however small the data
per page. The matmul page's case [S8]: `mm1 700` walks a column of `b` with
stride 5 600 B > 4 KB, so each of the 700 elements sits in its own page; 700
> 512 L2 TLB entries on that Ivy Bridge, so the entries are evicted before
reuse: 331.8 M dTLB misses for 691.3 M dTLB loads (48 %, i.e. practically
every load of `b`; one miss per 24 cycles), 23 c per inner iteration against
4.6 c at `n = 500`, where the 500 pages fit (1 % misses). Later runs of
`mm1 700` were often 4× faster with far fewer dTLB misses, which the page
attributes to transparent huge pages; with THP disabled the slow result came
every time [S8].

## Prefetchers

General knowledge (Intel's manual [S14]; the slides only name prefetching as
a form of parallelism [S3 p.26]): hardware prefetchers detect sequential and
constant-stride streams and fetch the next lines ahead of use; they do not
follow pointers and (on Intel) do not cross 4 KB page boundaries. Hence the
two modes of `memory1` [S7]: `linear` lets the prefetcher and spatial locality work, `random`
defeats both, and the difference between the two at the same size isolates
the prefetcher's contribution.

## Exercise 3 [S7]

Exercise 3 measures the cache, TLB and DRAM parameters of the course machine
with a pointer-chasing program under `perf stat`. It is graded, so this note
gives the general method (below) and not the per-question answers. Our
`src/c/pointer_chase.c` is a pointer-chasing program of the same kind.

Why the L2 cannot be probed for conflicts with virtual strides: L2 is
physically indexed and virtual strides are not physical strides [S7]. Why to
take the minimum of several runs: page placement varies per run and only adds
misses [S7].

## Measured here: the latency staircase

`src/c/pointer_chase.c --sweep` (random order, stride 128 B, 10 M dependent
loads per size, M3 Pro P-core: L1d 128 KB, L2 16 MB shared by the P-cluster,
16 KB pages [S19]; ranges over four `make bench` runs on 2026-09-28; "~c"
uses an **assumed** 4.05 GHz clock, so it is an estimate):

| working set | ns/access | ~c at 4.05 GHz | level |
|---|---|---|---|
| 2 KB to 128 KB | 1.00 to 1.09 | 4.0 to 4.4 | L1 (the knee lies between the 128 KB and 256 KB points, consistent with `hw.perflevel0.l1dcachesize` = 128 KB) |
| 256 KB | 4.6 to 5.0 | 19 to 20 | L2 |
| 512 KB to 2 MB | 5.8 to 6.7 | 23 to 27 | L2 |
| 4 MB | 7.5 to 7.9 | 30 to 32 | L2; the rise is probably TLB reach (Apple publishes no TLB size) |
| 8 MB | 8.5 to 12.8 | 34 to 52 | L2, noisy |
| 16 MB | 16 to 36 | 64 to 145 | L2 capacity edge; the most run-dependent point (the L2 is shared with the other P-cores) |
| 32 MB | 65 to 94 | 260 to 380 | DRAM |
| 64 to 128 MB | 103 to 114 | 420 to 460 | DRAM plus page walks |

The knees give the sizes; the plateaus give the latencies; the slow rise
inside a level is the TLB. That is exercise 3's entire method, on a
different machine. The absolute numbers are not the course's (M3: 128 B
lines, 16 KB pages, no `perf`), the reading is.

## Worked example: design the L1-associativity experiment

Skylake as the example [S3 p.21]: $C_1 = 32$ KB, $A = 8$, so $W = 4$ KB.
Choose stride $= W = 4\,096$: element $i$ is at $4096 i$, all elements share
set 0. With $E \le 8$ elements the eight ways hold them all, misses ~0; with
$E = 9$ every access evicts the line the next access needs (LRU), so all
100 M accesses miss: the knee is at $E = A$. Stride 8 192 gives the same
knee (still one set); stride 2 048 alternates two sets, knee at $2A = 16$.
Then $W = C_1/A$ needs $C_1$, and $S = W/B = 64$ needs the line size $B$.
On Rocket Lake the numbers differ [S7]; the design does not.

## Pitfalls

- Sizing a structure to the full cache: virtual pages land in arbitrary
  ways, so a few sets overflow; use $A-1$ ways' worth [S7].
- Reading cycles at a changing clock in the DRAM regime [S7].
- Measuring L3/DRAM on a shared machine while others do too [S7].
- Confusing the prefetcher's help with cache hits: the same size, linear vs
  random, tells them apart.
- Strides that are powers of two: they hit one set (conflict) and one TLB
  set; useful for a conflict experiment, a trap everywhere else. Pad rows of matrices by a line.
- Forgetting that the TLB has a reach independent of the data size: 700
  elements of 8 B can be 700 pages [S8].

## Exam-style questions

1. **Derive the number of sets and the way size of an 8-way 32 KB cache with 64 B lines, and say which addresses conflict.** $W = 32\text{K}/8 = 4$ KB per way, $S = 4\text{K}/64 = 64$ sets. Addresses congruent modulo 4 KB share a set; more than 8 live lines with the same address bits 6 to 11 thrash [S3 p.21].
2. **`mm1 700` has one dTLB miss every 24 cycles, `mm1 500` almost none. Why?** Column access with stride $8n$ bytes: 5 600 > 4 096, so every element is in its own page; a column touches 700 pages, more than the 512 STLB entries, so entries are evicted before reuse (capacity misses in the TLB); 500 pages fit [S8].
3. **Why can you not measure L2 associativity with virtual-address strides, while you can for L1?** L1 is small enough to be indexed by the page-offset bits, which virtual and physical addresses share (way size = page size; general knowledge, true for the slide's Skylake figures, 32 KB / 8 ways = 4 KB). L2's index uses bits above the page offset, which the OS's page placement scrambles, so a virtual stride equal to the L2 way size is not a physical one [S7].
4. **Sketch the cost of a load that misses every level.** L1 miss → L2 lookup (≈12 c) → L3 lookup (≥ 42 c) → DRAM (≈50 ns ≈ 150 to 200 c at 3 to 4 GHz); if the TLB also misses, a page walk of several dependent cached loads precedes the data access. For dependent loads these add; for independent loads the memory system overlaps them and bandwidth, not latency, is the limit [S3 p.14, 21].

Code: `src/c/pointer_chase.c` (`--sweep`, or `random|linear E stride` under `perf stat` on g0), `src/c/matmul_steps.c`. Sources: [S3 p.14, 20 to 21, 26] [S7] [S8] [S14] [S19].
