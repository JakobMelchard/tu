# 191.022 AMP - reference implementations

C++17 with `std::thread` and `std::atomic` only (the course project is "C/C++
with pthreads, Java, ..." [S2]; C++ atomics are what the memory-model part
needs). One program per topic, each with a header comment, a demo (no
argument), `--test` (assertions) and `--bench` (tables), each under 300 lines.
Sources are registered in [`../refs/SOURCES.md`](../refs/SOURCES.md).

## Build, test, benchmark

```sh
make -C cpp test     # build bin/ and run every --test (about 10 s from clean)
make -C cpp tsan     # rebuild with -fsanitize=thread into bin-tsan/, run every --test (about 14 s)
make -C cpp bench    # every --bench table (about 20 s)
make -C cpp clean
```

Flags: `clang++ -std=c++17 -O2 -Wall -Wextra -pthread` (TSan: `-O1 -g -fsanitize=thread`, `TSAN_OPTIONS=halt_on_error=1`, so any report fails the target). Verified 2026-09-28 on an Apple M3 Pro with Apple clang 21.0.0: `make test` and `make tsan` pass; TSan was checked to report a deliberate race on this machine, so a clean run is evidence. Build output (`bin/`, `bin-tsan/`) is git-ignored. No network, no data files.

## How concurrency is tested deterministically

Scheduling is not deterministic; the **outcome checks** are. Every test asserts a property that must hold in every interleaving:

| technique | used in | property |
|---|---|---|
| occupancy counter + non-atomic counter | `peterson_filter`, `spinlocks` | at most one thread inside; no lost update (and TSan flags the plain counter if exclusion fails) |
| deterministic replay of an interleaving, single-threaded | `treiber_stack::aba_script` | the ABA bug occurs untagged and not tagged |
| exactly-once accounting | `treiber_stack`, `ms_queue`, `work_stealing`, `hazard_pointers` | every item pushed/enqueued/spawned is obtained exactly once |
| per-key balance | `lists`, `striped_hashset` | (successful adds) - (successful removes) of each key equals final membership, in {0, 1} |
| disjoint-key phase | `lists` | final contents known exactly despite concurrency |
| recorded history + linearisability search | `ms_queue` | 400 histories of 15 calls (398-400 with overlapping calls) all linearisable; a LIFO posing as a queue is rejected |
| forbidden litmus outcomes | `memory_model` | outcomes the C++ model forbids never appear; allowed ones are only reported |
| poisoning instead of freeing | `hazard_pointers` | a late access to a retired node is counted, not undefined behaviour; 0 with HP and epochs |
| FIFO service order | `spinlocks::check_fifo` | CLH and MCS serve in `tail.exchange` order |

What a test **cannot** show: that a weak outcome is impossible on this machine. Where the notes quote "0 observed" for an allowed outcome, they say so.

## Files

| file | note | what | reproduces |
|---|---|---|---|
| `cpp/common.hpp` | | `Timer`, `CHECK`, `Rng`, `cpu_relax`, `run_threads`, `SpinBarrier` (sense-reversing, book ch. 17), `kScale` (test sizes / 8 under TSan) | |
| `cpp/peterson_filter.cpp` | 01 | Peterson, Filter, Bakery with seq_cst atomics; weakened Peterson in barrier-aligned rounds | mutual exclusion [S1 ch. 2]; overlaps with relaxed and release/acquire, none with seq_cst |
| `cpp/memory_model.cpp` | 03 | MP, SB, LB litmus tests with a spin barrier and jitter; coherence check | SB weak outcome with relaxed and acq/rel, never with seq_cst or seq_cst fences [S20] [S23] |
| `cpp/spinlocks.cpp` | 05 | TAS, TTAS, exponential backoff, CLH, MCS, `std::mutex` baseline; throughput and fairness | queue locks FIFO [S13] |
| `cpp/lists.cpp` | 06 | coarse, lazy [S16], lock-free (Harris [S15]) sets with one shared test | |
| `cpp/treiber_stack.cpp` | 08 | tagged Treiber stack over a node array with a free list, ABA replay, elimination backoff with a lock-free exchanger [S17] | ABA [S14] |
| `cpp/ms_queue.cpp` | 07, 02 | Michael-Scott queue with counted pointers and free list [S14]; Wing-Gong style linearisability checker; mutex queue baseline | |
| `cpp/striped_hashset.cpp` | 09 | coarse and striped hash sets with concurrent resize; split-order property check | recursive split ordering [S18], exhaustively for $2^{12}$ keys |
| `cpp/work_stealing.cpp` | 11 | Chase-Lev deque with the orderings of [S25, Fig. 1]; fork-join pool with help-while-waiting; fib, quicksort | |
| `cpp/hazard_pointers.cpp` | 12 | hazard pointers [S26], epoch-based reclamation [S27], an unsafe reclaimer; Treiber stack on top | HP bound: retire list stays below $2H$, protected node survives |

## Practice extension (project rehearsal)

Not written here on purpose: a **lazy skiplist** (note 10) in a new `cpp/skiplist.cpp`, tested with `lists.cpp`'s `test_set` pattern plus a per-level structural check, with a written linearisability argument and a thread-scaling table. That is the shape of the course project [S5] [S37].
