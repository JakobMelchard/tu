# 03 Memory models: C++ atomics and the hardware underneath

TISS lists "memory models" first [S2]. The book treats memory consistency in
chapter 3 (with the Java memory model) and hardware in appendix B [S1]; the
course's project is in C/C++ [S2], so this note follows the C++ model:
cppreference [S20], the standard draft [S31], Boehm & Adve [S19], and the
hardware models x86-TSO [S23] and ARMv8 [S24]. Readable introductions:
Preshing [S21], Sutter's *atomic<> Weapons* [S22]. Code:
`src/cpp/memory_model.cpp`. Hardware background (store buffers, caches):
Efficient Programs 03,
04;
races and false sharing: [NSSC I 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md).

## Why a model is needed

Note 01 assumed **sequential consistency** (SC) [S28]: the result of any run is as if all operations of all threads executed in one interleaving that respects each thread's program order. No CPU gives this by default: a **store buffer** (a per-core FIFO of pending writes) lets a core's load complete before its own earlier store is visible to others, and compilers reorder independent accesses. A **memory model** states which values a load may return.

## The C++ model in five definitions [S20] [S31]

- **Sequenced-before** (sb): program order within one thread.
- **Synchronizes-with** (sw): a release store (or stronger) to atomic $M$ in thread A, read by an acquire load (or stronger) of $M$ in thread B that returns that value.
- **Happens-before** (hb): the transitive closure of sb and sw (ignoring `consume`).
- **Modification order**: all writes to one atomic object form a single total order that every thread agrees on (**coherence**), even with `relaxed`.
- **Data race**: two accesses to the same location, at least one a write, at least one non-atomic, not ordered by hb. **A program with a data race has undefined behaviour** [S20] [S31 intro.races]. There are no benign races [S32].

**SC-DRF** (the contract [S19]): a data-race-free program that uses only `seq_cst` atomics behaves sequentially consistently. Weaker orders trade that guarantee for speed.

| `memory_order` | guarantee |
|---|---|
| `relaxed` | atomicity and coherence only; no ordering of other accesses |
| `release` (store) | everything sb-before the store becomes visible to an acquirer that reads it |
| `acquire` (load) | if it reads a release store, everything sb-before that store happens-before what follows the load |
| `acq_rel` (RMW) | both |
| `seq_cst` (default) | acquire/release **plus one total order** $S$ of all seq_cst operations, consistent with hb [S20] |

A `std::atomic_thread_fence(release)` before a relaxed store, and a `fence(acquire)` after a relaxed load, give the same sw edge as release/acquire accesses. A `fence(seq_cst)` also joins the total order $S$.

## Three litmus tests, derived

**MP (message passing).** T0: `data = 1; flag.store(1, rel)`. T1: `if (flag.load(acq) == 1) r = data`. The load reads the release store, so $w(\text{data}) \xrightarrow{sb} w_{rel}(\text{flag}) \xrightarrow{sw} r_{acq}(\text{flag}) \xrightarrow{sb} r(\text{data})$: the write happens-before the read, and $r = 1$. With relaxed `flag` there is no sw edge; $r = 0$ is allowed (and `data` must then be atomic, or it is a race).

**SB (store buffering).** T0: `x = 1; r1 = y`. T1: `y = 1; r2 = x`. Can $r_1 = r_2 = 0$? With seq_cst: each load reading 0 is before the other thread's store in $S$:
$$w(x) <_S r(y) <_S w(y) <_S r(x) <_S w(x),$$
using program order (consistent with $S$) for $w(x) <_S r(y)$ and $w(y) <_S r(x)$. A cycle: forbidden. With release/acquire there is no sw edge (both loads read the initial values, which were not written by a release), so $0, 0$ is **allowed**. SB is exactly Peterson's `flag[me] = 1; ... read flag[other]` (note 01).

**LB (load buffering).** T0: `r1 = x; y = 1`. T1: `r2 = y; x = 1`. $r_1 = r_2 = 1$ is allowed with relaxed (a store may become visible before an earlier load completes on ARM), forbidden with acquire loads and release stores (a cycle in hb).

## Hardware models

- **x86-TSO** [S23]: each core has a FIFO store buffer; its own loads read from it first; stores drain in order. The **only** visible reordering is a store followed by a load to a different location (SB). `MFENCE` or any `LOCK`-prefixed instruction drains the buffer. So on x86 acquire and release are free; seq_cst costs on the **store** side.
- **ARMv8** [S24]: other-multicopy-atomic (a write becomes visible to all other cores at once) but all four orders load/store × load/store may be reordered unless a dependency, barrier or acquire/release instruction forbids it. `LDAR`/`STLR` are RCsc: an `LDAR` is not reordered before an earlier `STLR`. `LDAPR` (ARMv8.3 RCpc) is: an acquire that may pass an earlier release store.

What the compiler emits (Apple clang 21, `-O2`; `-target x86_64` for the right column) [S35]:

| C++ | arm64 (Apple M3) | x86-64 |
|---|---|---|
| `load(acquire)` | `ldapr` | `mov` |
| `load(seq_cst)` | `ldar` | `mov` |
| `store(release)` | `stlr` | `mov` |
| `store(seq_cst)` | `stlr` | `xchg` |
| `fetch_add(seq_cst)` | `ldaddal` | `lock xadd` |
| `compare_exchange_strong` | `casal` | `lock cmpxchg` |
| `atomic_thread_fence(seq_cst)` | `dmb ish` | `lock or [rsp], 0` |
| `atomic_thread_fence(release)` | `dmb ish` | nothing (compiler barrier only) |

The first row explains the Peterson measurement of note 01: with release stores and acquire loads the lock's read of `flag[other]` compiles to `ldapr`, which may complete before the preceding `stlr` of `flag[me]` is visible, which is the SB outcome, and both threads entered (up to 11918 times per $10^6$ aligned rounds). With seq_cst the load is `ldar` and never passes the `stlr`: 0 overlaps.

## Measured: litmus outcomes on this machine

`./bin/memory_model --bench`, $10^6$ barrier-aligned rounds each, M3 Pro [S35]:

| test | weak outcome observed | C++ says |
|---|---|---|
| MP relaxed flag | 0 | allowed |
| MP release/acquire | 0 | forbidden |
| SB relaxed | 8774 to 26862 | allowed |
| SB release/acquire | 5493 to 65355 | allowed |
| SB seq_cst | 0 | forbidden |
| SB relaxed + `fence(seq_cst)` | 0 | forbidden |
| LB relaxed | 0 | allowed |
| LB acquire/release | 0 | forbidden |

(ranges over two runs on 2026-09-28). "Allowed but never observed" (MP relaxed, LB relaxed) means this core did not do it in $10^6$ tries, **not** that it cannot: ARM permits both [S24], and a different compiler schedule may expose them. Test against the model, not against one machine. Preshing's x86 SB experiment saw about one reordering per 6600 iterations [S21]; the rate is a property of the machine.

## Pitfalls

- `volatile` is not atomic and orders nothing between threads (it only stops the compiler from deleting accesses).
- A data race is undefined behaviour even if "the hardware would do the right thing": the compiler may keep a racy variable in a register forever [S32].
- Acquire/release does not order a store before a later load (SB). Dekker/Peterson-style handshakes need seq_cst or a seq_cst fence.
- ThreadSanitizer does not model standalone fences: code that synchronises only through `atomic_thread_fence` gets false race reports. `work_stealing.cpp` swaps its fences for seq_cst/release accesses under `-fsanitize=thread`.
- "It passed on x86" proves little: x86 only exhibits SB; ARM exhibits much more.

## Exam-style questions

1. **Define data race and happens-before in C++. What is the consequence of a race?** Conflicting accesses, one non-atomic, unordered by hb (the closure of sequenced-before and synchronizes-with); the whole program has undefined behaviour [S20] [S31].
2. **Show that release/acquire makes message passing work.** sb, sw, sb chain from the data write to the data read; hb implies the read sees 1 (derivation above).
3. **Why is $r_1 = r_2 = 0$ impossible in SB with seq_cst but possible with acquire/release?** Seq_cst: one total order consistent with program order gives the cycle above. Acq/rel: no sw edge because each load reads the initial value; x86-TSO and ARM both produce it via the store buffer [S23].
4. **Which reorderings does x86-TSO allow, and what does a seq_cst store compile to there? On ARMv8?** Only store→load; `xchg` (implicitly locked) on x86; `stlr` on ARMv8, with loads as `ldar` so that they cannot pass it [S23] [S24] [S35].
5. **SC-DRF: state it and explain why it lets you use a simpler model most of the time.** Programs without data races whose atomics are all seq_cst behave as if sequentially consistent [S19]; so if you avoid races and weak orders you may reason with interleavings, as in note 01. Weak orders are an optimisation that needs a proof.

Code: `src/cpp/memory_model.cpp` (`litmus`, `mp`, `sb`, `sb_fence`, `lb`, coherence check in `test`). Sources: [S1] [S2] [S19] [S20] [S21] [S22] [S23] [S24] [S28] [S31] [S32] [S35].
