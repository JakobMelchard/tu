# 14 Concurrency: threads, jthread, mutexes, atomics, futures, execution policies

C++11 gave the language a memory model: a precise definition of which multithreaded
programs have defined behaviour. The core rule is short: **a data race is undefined
behaviour**. Item 022 [S3]; hand-out ex3.3 (make a `shared_ptr` count thread-safe with
atomics and with locks, benchmark both) [S4]; CP.2, CP.20, CP.25, CP.42 [S10]. OpenMP
and scaling laws are in [NSSC I note 07](../../numerical-simulation-and-scientific-computing-i/notes/07-shared-memory-parallel-computing.md) [S15] (not repeated here).

Code: `src/cpp/concurrency.cpp` (14 deterministic checks, clean under ThreadSanitizer:
`make tsan`; `./bin/concurrency --bench` for timings).

## Definitions [S8 [intro.races], [atomics.order], [futures], [thread.jthread.class], [algorithms.parallel.exec]]

- **Data race**: two accesses to the same memory location from different threads, at
  least one a write, not ordered by *happens-before*, and not both atomic. UB: the
  compiler may keep values in registers, merge or tear writes.
- **`std::thread`**: starts a function on a new thread; must be `join()`ed or
  `detach()`ed before destruction, otherwise `std::terminate`.
  **`std::jthread`** (C++20): joins in its destructor and carries a `std::stop_token`
  for cooperative cancellation (`request_stop()` then `join()`). Prefer it (CP.25).
- **`std::mutex`** + RAII lock (`std::lock_guard`, `std::scoped_lock` for several
  mutexes without deadlock, `std::unique_lock` when you must unlock/relock or wait).
  Never raw `lock()`/`unlock()` (CP.20).
- **`std::condition_variable`**: wait until a predicate holds; always
  `cv.wait(lock, predicate)` (spurious wakeups, lost notifications: CP.42).
- **`std::atomic<T>`**: indivisible read-modify-write (`fetch_add`, `exchange`,
  `compare_exchange_weak/strong`). **Memory order**: `seq_cst` (default, one global
  order), `acquire`/`release` (a release store *synchronises-with* the acquire load that
  reads it: everything before the store is visible after the load), `relaxed` (atomicity
  only, fine for counters that nobody synchronises on).
- **`std::future` / `std::promise` / `std::async` / `std::packaged_task`**: a one-shot
  channel for a value *or an exception* from another thread. `std::async(std::launch::async, f)`
  guarantees a new thread; without the policy it may run lazily in `get()`.
- **C++20 coordination**: `std::latch` (count down once), `std::barrier` (reusable phase
  sync), `std::counting_semaphore`, `atomic::wait/notify`.
- **Execution policies** (C++17): `std::execution::seq`, `par` (may run on several
  threads), `par_unseq` (threads and vectorisation; no locks inside the element
  function), `unseq` (C++20). Passed as the first argument to most `<algorithm>`/`<numeric>`
  functions. On this Mac they need **`-fexperimental-library`** (libc++ uses a
  libdispatch backend; `__cpp_lib_execution` stays undefined) and
  `-mmacosx-version-min=<current>` to silence an ld warning [S13].

## Complete example

```cpp
// complete example: concurrency
#include <atomic>
#include <cstdio>
#include <future>
#include <mutex>
#include <numeric>
#include <stop_token>
#include <thread>
#include <vector>

int main() {
    constexpr int T = 4, N = 100'000;
    long locked = 0;
    std::mutex m;
    std::atomic<long> atomic_count{0};
    std::vector<long> partial(T);
    {
        std::vector<std::jthread> ts;
        for (int t = 0; t < T; ++t)
            ts.emplace_back([&, t] {
                long mine = 0;
                for (int i = 0; i < N; ++i) {
                    { std::lock_guard lk(m); ++locked; }                   // correct, slowest
                    atomic_count.fetch_add(1, std::memory_order_relaxed);  // correct, contended
                    ++mine;                                                // private: no sharing
                }
                partial[static_cast<std::size_t>(t)] = mine;               // one write per thread
            });
    }                                                                      // jthreads join here
    std::printf("%ld %ld %ld\n", locked, atomic_count.load(),
                std::accumulate(partial.begin(), partial.end(), 0L));      // 400000 x3

    int data = 0;
    std::atomic<bool> ready{false};
    std::jthread producer([&] { data = 42; ready.store(true, std::memory_order_release); });
    while (!ready.load(std::memory_order_acquire)) std::this_thread::yield();
    std::printf("data=%d\n", data);                                        // 42, guaranteed

    std::jthread worker([](std::stop_token st) { while (!st.stop_requested()) std::this_thread::yield(); });
    worker.request_stop();                                                 // cooperative cancel

    auto f = std::async(std::launch::async, [] { return 6 * 7; });
    std::printf("async=%d\n", f.get());
}
```

## Measured on this Mac (`./bin/concurrency --bench`, M3 Pro, 12 hardware threads, 3 runs) [S13]

| operation on $2\times10^7$ doubles | `seq` | `par` / `par_unseq` | speedup |
|---|---|---|---|
| `std::reduce` | 15.3 ms | 5.3 ms (`par_unseq`) | 2.9x: memory-bandwidth bound (160 MB read) |
| `std::sort` | 458 ms | 318-336 ms (`par`) | 1.4x |

`par_unseq` and `seq` reduce of the same data differ by $5\times10^{-7}$ (on a sum of
$\approx 10^7$): parallel reduction reassociates floating-point additions, so results
are not bit-reproducible across policies or thread counts. For integers they are
identical (checked).

## Pitfalls

- "It worked in my test" is not evidence: a racy `++counter` loses 60-90 % of updates on
  this machine (NSSC I note 07 measured it [S15]), or none on a lucky run. Use TSan
  (`-fsanitize=thread`, works on macOS; the 2021W ex3.3 build enabled it [S4]).
- Holding a lock while calling unknown code (callbacks, `notify` inside the lock is fine
  but costs a wakeup-then-block), locking two mutexes in different orders (deadlock:
  use `std::scoped_lock(a, b)`).
- `std::thread` destroyed while joinable: `std::terminate`. `std::jthread` avoids it.
- `std::async` without `std::launch::async` may never run concurrently; its future's
  destructor blocks (a discarded `std::async(...)` result is synchronous).
- **False sharing**: per-thread counters in one cache line (`hw.cachelinesize` = 128 bytes here) serialise
  through the coherence protocol; pad with `alignas(std::hardware_destructive_interference_size)`
  or accumulate locally (NSSC I note 07 measured 20-50x for atomics [S15]).
- `relaxed` is only for values nobody uses to publish other data; for a "ready" flag use
  release/acquire. When unsure, keep the default `seq_cst`.
- `shared_ptr`'s count is thread-safe, the pointee and the `shared_ptr` object are not
  (note 10).
- Execution policies: the element function must not race (no shared accumulation
  without atomics), must not throw (an escaping exception calls `std::terminate`), and
  with `par_unseq` must not lock.

## Discussion questions

1. **Why is a data race undefined behaviour and not just "a wrong number"?** The
   compiler optimises each thread as if it were alone (it may keep a shared variable in
   a register for a whole loop, or merge stores); hardware reorders memory operations.
   Only synchronisation (mutex, atomics) creates the happens-before edges that forbid
   these transformations.
2. **Atomics vs mutex for a reference count (ex3.3)?** A count is one word with
   read-modify-write: `fetch_add(1, relaxed)` for increments and
   `fetch_sub(1, acq_rel)` (then delete if it was 1) for decrements; no lock, one
   contended cache line. A mutex protects arbitrary critical sections but costs a lock
   acquisition (possibly a syscall) per operation. Expect atomics to be several times
   faster under contention; both are far slower than no sharing.
3. **What does `memory_order_release` / `acquire` guarantee?** If thread B's acquire load
   reads the value written by thread A's release store, everything A wrote before the
   store is visible to B after the load. That is the minimal ordering to publish data
   through a flag; `relaxed` gives atomicity only.
4. **`std::jthread` vs `std::thread`?** `jthread` joins automatically (no terminate on
   exceptions or early returns) and provides a `stop_token` for cooperative cancellation.
   `thread` must be joined/detached manually. Prefer `jthread` unless detaching.
5. **When does `std::execution::par` help, and what may the function not do?** When the
   work per element is large enough to amortise thread dispatch and the operation is
   compute-bound (sort: 1.4x here; memory-bound reduce: 2.9x, saturating bandwidth). The
   element function must be free of data races, must not throw, and under `par_unseq`
   must not take locks or allocate with synchronisation; floating-point reductions
   change in the last bits.

## In the code

- `src/cpp/concurrency.cpp`: mutex, relaxed atomic and private-partial counters; release/acquire publication; `jthread` + `stop_token`; a `Channel<T>` (mutex + condition variable, two producers, one consumer); promise/future, `async` value and exception; `latch`; `shared_ptr` copies across threads; `std::reduce`/`std::sort` with `par`/`par_unseq` (behind `HAVE_EXECUTION`); `--bench`.
- `make tsan`: the same file under ThreadSanitizer (clean, 2026-09-28).
