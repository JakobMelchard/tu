# 10 Smart pointers: unique_ptr, shared_ptr, weak_ptr, custom deleters, cycles

Smart pointers are RAII owners of heap objects (or any handle, via a deleter). Two of
the three 2021W EX3 parts implemented them: a simplified `unique_ptr` with a custom
deleter, and a thread-safe reference count for a given `shared_ptr` [S4]. Item 018
[S3]; R.20-R.24, R.30 [S10].

Code: `src/cpp/smart_pointers.cpp` (counts allocations by replacing global `operator new`).

## Definitions [S8 [unique.ptr], [util.smartptr.shared]]

- **`std::unique_ptr<T, D = default_delete<T>>`**: sole owner. Move-only; destructor
  calls `D{}(p)`. With a stateless deleter it is exactly one pointer
  (`sizeof == 8`, checked). `unique_ptr<T[]>` calls `delete[]` and offers `operator[]`.
  Create with `std::make_unique<T>(args...)`; `make_unique_for_overwrite` skips
  value-initialisation.
- **Custom deleter**: any callable taking `T*`. A captureless lambda type costs nothing
  (`[[no_unique_address]]`/EBO in the implementation); a function pointer adds 8 bytes;
  a `std::function` deleter adds 32 (libc++ 21: `sizeof == 40` in total [S13]). Typical: `unique_ptr<FILE, decltype(&fclose)>` or a lambda
  calling `fclose`, `cudaFree`, `MPI_Comm_free`.
- **`std::shared_ptr<T>`**: shared ownership through a **control block** holding the
  strong count, the weak count, the deleter and the allocator. Two pointers wide.
  Copy increments the strong count (atomically), destruction decrements; at zero the
  object is destroyed, at weak zero the control block is freed.
- **`std::make_shared<T>`**: object and control block in **one** allocation (measured: 1
  vs 2 allocations for `shared_ptr<T>(new T)` [S13]). Downside: the object's memory is
  released only when the last `weak_ptr` is gone too.
- **`std::weak_ptr<T>`**: non-owning observer of a `shared_ptr`-managed object.
  `lock()` returns a `shared_ptr` (empty if expired). Breaks ownership cycles (R.24).
- **Aliasing constructor** `shared_ptr<U>(owner, &owner->member)`: shares ownership of
  the owner, points at a member.
- **`enable_shared_from_this<T>`**: lets a member function obtain a `shared_ptr` to
  `*this` (only if the object is already owned by one).
- **Thread safety**: the *control block* is thread-safe (atomic counts); the pointee
  and the `shared_ptr` object itself are not (`std::atomic<std::shared_ptr<T>>` in C++20
  for the latter).

## Which one

| situation | use |
|---|---|
| one owner, maybe transferred | `std::unique_ptr` (default choice, R.21) |
| lifetime genuinely shared, last user unknown (caches, graphs, async tasks) | `std::shared_ptr` |
| observe something shared without extending its life, break cycles | `std::weak_ptr` |
| observe, lifetime obviously longer than the observer | `T*` or `T&` (non-owning) |
| function only uses the object | take `T&` / `T*`, not the smart pointer (R.30) |

## Complete example

```cpp
// complete example: smart_pointers
#include <cstdio>
#include <memory>
#include <string>

struct Node {
    std::string name;
    std::shared_ptr<Node> next;      // owning
    std::weak_ptr<Node> prev;        // observing: no cycle
    explicit Node(std::string n) : name(std::move(n)) { std::printf("+%s ", name.c_str()); }
    ~Node() { std::printf("-%s ", name.c_str()); }
};

int main() {
    {
        auto closer = [](std::FILE* f) { if (f) std::fclose(f); };
        std::unique_ptr<std::FILE, decltype(closer)> f{std::tmpfile(), closer};
        static_assert(sizeof f == sizeof(std::FILE*));          // stateless deleter: free
        std::fputs("data", f.get());
    }                                                           // fclose here, on every path

    {
        auto a = std::make_shared<Node>("a"), b = std::make_shared<Node>("b");
        a->next = b;
        b->prev = a;                                            // weak back edge
        std::printf("\nuse_count a=%ld b=%ld\n", a.use_count(), b.use_count());   // 1 2
    }                                                           // -a -b: both destroyed
    {
        auto x = std::make_shared<Node>("x"), y = std::make_shared<Node>("y");
        x->next = y;
        y->next = x;                                            // strong cycle
    }                                                           // nothing printed: leaked
    std::puts("\n(x and y leaked)");

    std::unique_ptr<Node> u = std::make_unique<Node>("u");
    std::shared_ptr<Node> s = std::move(u);                     // unique -> shared is allowed
    std::printf("\nu empty: %d, s: %s\n", u == nullptr, s->name.c_str());
}
```

## Implementing `unique_ptr` (the ex3.2 shape)

The minimal correct set, in `smart_pointers.cpp` as `my::unique_ptr`: member `T* p_`
and `[[no_unique_address]] D d_`; deleted copy ctor and copy assignment; move ctor
`p_(std::exchange(o.p_, nullptr)), d_(std::move(o.d_))`; move assignment via
`reset(o.release())` plus moving the deleter, guarded against self-move; destructor
`reset()`; `reset(T* p)` stores the new pointer *before* deleting the old one (so a
deleter that re-enters sees a consistent object); `release()`, `get()`, `operator*`,
`operator->`, `explicit operator bool`, comparison with `nullptr`.

## Pitfalls

- Two `shared_ptr`s from the same raw pointer: `shared_ptr<T> a(p), b(p);` creates two
  control blocks and a double delete. Create each object's first owner with
  `make_shared` or from a `unique_ptr`.
- `shared_ptr<T>(this)` inside a member function: same bug; use `enable_shared_from_this`.
- Cycles of `shared_ptr` leak (demonstrated in `smart_pointers.cpp`: `alive == 2` after
  scope exit). LeakSanitizer would report them, but LSan is unsupported on arm64 macOS [S13].
- Passing `shared_ptr` by value everywhere: an atomic increment and decrement per call.
  Pass `const T&` unless the callee stores it.
- `unique_ptr<Base>` owning a `Derived` needs a virtual destructor in `Base`
  (`shared_ptr` captures the right deleter at creation, `unique_ptr` does not).
- `std::make_unique<T[]>(n)` value-initialises (zeroes) the array; for large numeric
  buffers you then write them twice. `make_unique_for_overwrite` does not.
- A deleter stored as `std::function` makes the `unique_ptr` 40 bytes and the reset
  an indirect call.

## Discussion questions

1. **What is in a `shared_ptr`, and why is `make_shared` preferred?** A pointer to the
   object and a pointer to the control block (strong count, weak count, deleter,
   allocator). `make_shared` allocates both at once: one allocation instead of two,
   better locality, and no leak window between `new` and the `shared_ptr` constructor.
2. **Is `std::shared_ptr` thread-safe?** The reference counting is: copies in different
   threads can be created and destroyed concurrently (checked in `concurrency.cpp`).
   Accessing the pointee concurrently needs your own synchronisation, and one
   `shared_ptr` *object* written by one thread while read by another is a data race.
   ex3.3 was exactly about making the count thread-safe with atomics vs locks [S4].
3. **Why is `sizeof(unique_ptr<T>) == sizeof(T*)` but not with a function-pointer deleter?**
   The deleter is stored as a member; an empty class type occupies no storage with
   `[[no_unique_address]]` (or EBO), a function pointer is 8 bytes of state.
4. **How do you break a reference cycle, and how do you use the weak side?** Make one
   direction `weak_ptr` (the back pointer, the parent pointer, the observer list).
   To use it: `if (auto p = w.lock()) { ... }`, which yields an owning `shared_ptr` for
   the duration or nothing if the object is gone.
5. **When should a function take a smart pointer as a parameter?** Only to express
   ownership semantics (R.30): `unique_ptr<T>` by value = "I take ownership",
   `shared_ptr<T>` by value = "I will share ownership", `unique_ptr<T>&` = "I may reseat
   it". To merely use the object, take `T&` or `T*`.

## In the code

- `src/cpp/smart_pointers.cpp`: size checks for three deleter kinds, RAII `FILE*`, `make_unique<double[]>`, allocation counting (1 vs 2), `use_count`, `weak_ptr` expiry, a leaking cycle and a weak back edge, the aliasing constructor, and `my::unique_ptr` with a counting deleter (`reset`, `release`, move).
- `src/cpp/concurrency.cpp` section 9: copying a `shared_ptr` from four threads.
