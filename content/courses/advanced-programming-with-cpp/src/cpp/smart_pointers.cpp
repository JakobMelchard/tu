// smart_pointers.cpp -- unique_ptr, shared_ptr, weak_ptr, custom deleters, cycles,
// plus a minimal unique_ptr of our own (the classic hand-in shape) (note 10).
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <new>
#include <string>
#include <type_traits>
#include <utility>
#include "check.hpp"

// count heap allocations program-wide by replacing the global operator new
static int allocations = 0;
void* operator new(std::size_t n) {
    ++allocations;
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

int alive = 0;
struct Node {
    std::string name;
    std::shared_ptr<Node> next;           // owning edge
    std::weak_ptr<Node> prev;             // non-owning back edge: breaks the cycle
    explicit Node(std::string n) : name(std::move(n)) { ++alive; }
    ~Node() { --alive; }
};

// --- a minimal unique_ptr: move-only, deleter stored with [[no_unique_address]]
namespace my {
template <class T> struct default_delete { void operator()(T* p) const noexcept { delete p; } };
template <class T, class D = default_delete<T>> class unique_ptr {
    T* p_ = nullptr;
    [[no_unique_address]] D d_{};
public:
    using pointer = T*;
    using element_type = T;
    unique_ptr() = default;
    explicit unique_ptr(T* p, D d = D{}) noexcept : p_(p), d_(std::move(d)) {}
    unique_ptr(const unique_ptr&) = delete;
    unique_ptr& operator=(const unique_ptr&) = delete;
    unique_ptr(unique_ptr&& o) noexcept : p_(std::exchange(o.p_, nullptr)), d_(std::move(o.d_)) {}
    unique_ptr& operator=(unique_ptr&& o) noexcept {
        if (this != &o) { reset(std::exchange(o.p_, nullptr)); d_ = std::move(o.d_); }
        return *this;
    }
    ~unique_ptr() { reset(); }
    void reset(T* p = nullptr) noexcept { if (T* old = std::exchange(p_, p)) d_(old); }
    T* release() noexcept { return std::exchange(p_, nullptr); }
    T* get() const noexcept { return p_; }
    T& operator*() const { return *p_; }
    T* operator->() const noexcept { return p_; }
    explicit operator bool() const noexcept { return p_ != nullptr; }
    friend bool operator==(const unique_ptr& a, std::nullptr_t) noexcept { return a.p_ == nullptr; }
};
}  // namespace my

int main() {
    // unique_ptr: zero overhead with a stateless deleter
    static_assert(sizeof(std::unique_ptr<int>) == sizeof(int*));
    auto closer = [](std::FILE* f) { std::fclose(f); };
    static_assert(sizeof(std::unique_ptr<std::FILE, decltype(closer)>) == sizeof(std::FILE*));
    static_assert(sizeof(std::unique_ptr<std::FILE, int (*)(std::FILE*)>) == 2 * sizeof(void*));
    static_assert(!std::is_copy_constructible_v<std::unique_ptr<int>>);
    {
        std::unique_ptr<std::FILE, decltype(closer)> f{std::tmpfile(), closer};   // RAII for a C handle
        CHECK(f != nullptr);
        CHECK(std::fputs("x", f.get()) >= 0);
    }                                                                            // fclose runs here
    auto arr = std::make_unique<double[]>(4);                                   // value-initialised
    CHECK(arr[3] == 0.0);

    // shared_ptr: make_shared puts object and control block in ONE allocation
    int n0 = allocations;
    auto s1 = std::make_shared<Node>("a");
    int make_shared_allocs = allocations - n0;
    n0 = allocations;
    std::shared_ptr<Node> s2(new Node("b"));
    int new_then_shared_allocs = allocations - n0;
    CHECK(make_shared_allocs == 1 && new_then_shared_allocs == 2);

    {
        auto copy = s1;
        CHECK(s1.use_count() == 2);
    }
    CHECK(s1.use_count() == 1);

    // weak_ptr observes without owning
    std::weak_ptr<Node> w = s1;
    CHECK(!w.expired() && w.lock()->name == "a");
    s1.reset();
    CHECK(w.expired() && w.lock() == nullptr);
    s2.reset();
    CHECK(alive == 0);

    // a cycle of shared_ptrs never dies ...
    {
        auto x = std::make_shared<Node>("x"), y = std::make_shared<Node>("y");
        x->next = y;
        y->next = x;
    }
    CHECK(alive == 2);                      // leaked: each keeps the other's count at 1
    // ... a weak back edge breaks it
    {
        auto x = std::make_shared<Node>("x2"), y = std::make_shared<Node>("y2");
        x->next = y;
        y->prev = x;
    }
    CHECK(alive == 2);                      // only the two leaked ones remain

    // aliasing constructor: shares ownership of the node, points at a member
    auto owner = std::make_shared<Node>("owner");
    std::shared_ptr<std::string> name(owner, &owner->name);
    owner.reset();
    CHECK(*name == "owner" && alive == 3);  // node kept alive through `name`
    name.reset();
    CHECK(alive == 2);

    // our own unique_ptr
    int deleted = 0;
    auto counting = [&deleted](int* p) { ++deleted; delete p; };
    {
        my::unique_ptr<int, decltype(counting)> p(new int(5), counting);
        CHECK(*p == 5 && p);
        auto q = std::move(p);
        CHECK(p == nullptr && *q == 5 && deleted == 0);
        q.reset(new int(6));
        CHECK(deleted == 1 && *q == 6);
        int* raw = q.release();
        CHECK(q == nullptr);
        delete raw;
    }
    CHECK(deleted == 1);                    // released pointer was not deleted by q
    static_assert(sizeof(my::unique_ptr<int>) == sizeof(int*));   // [[no_unique_address]] at work
    return chk::report("smart_pointers");
}
