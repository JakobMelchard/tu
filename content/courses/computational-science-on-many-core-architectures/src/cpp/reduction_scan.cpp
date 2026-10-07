// Parallel reduction and prefix sum (scan), written the way a GPU does them,
// on the CPU with OpenMP. Mirrors src/cuda/reduction.cu and src/cuda/scan.cu.
// Note 04 (GPU architecture), sections "Reductions" and "Scans".
//
//   reduce_blocks      Harris kernel 3 "sequential addressing" [S16]: blocks of
//                      B elements reduced by a halving tree in a shared buffer,
//                      then a second pass over the block sums (= 2nd launch).
//   reduce_thread_tree per-thread partials combined by an interleaved tree with
//                      a barrier per level: the __syncthreads() pattern [S4].
//   scan_hillis_steele inclusive, log2(n) steps, O(n log n) adds [S19].
//   scan_blelloch      exclusive, up-sweep + down-sweep, 2(n-1) adds [S17] [S18].
//   scan_three_phase   chunk scan, scan of chunk sums, add offsets: how
//                      multi-block GPU scans (and CPU libraries) are built.
#include <numeric>

#include "common.hpp"

using mc::Mode;
using i64 = long long;

namespace {

constexpr int B = 256;  // "threads per block" of the emulated kernel

template <class T>
T reduce_blocks(const std::vector<T>& x) {
    if (x.empty()) return T(0);
    const T* src = x.data();  // first pass reads the input in place
    size_t n = x.size();
    std::vector<T> cur, next;
    while (n > 1) {  // one "kernel launch" per pass
        size_t nb = (n + B - 1) / B;
        next.assign(nb, T(0));
#pragma omp parallel for schedule(static)
        for (size_t b = 0; b < nb; ++b) {
            T s[B];  // shared memory of the block
            for (int t = 0; t < B; ++t) {
                size_t i = b * B + t;
                s[t] = i < n ? src[i] : T(0);
            }
            // each level is one __syncthreads()-separated step; threads t < stride
            // read s[t + stride]: consecutive addresses, no bank conflicts
            for (int stride = B / 2; stride > 0; stride /= 2)
                for (int t = 0; t < stride; ++t) s[t] += s[t + stride];
            next[b] = s[0];
        }
        cur.swap(next);
        src = cur.data();
        n = nb;
    }
    return src[0];
}

template <class T>
T reduce_thread_tree(const std::vector<T>& x) {
    int p = omp_get_max_threads();
    std::vector<T> part(p, T(0));
#pragma omp parallel num_threads(p)
    {
        int tid = omp_get_thread_num(), nt = omp_get_num_threads();
        T s = 0;
#pragma omp for schedule(static)
        for (size_t i = 0; i < x.size(); ++i) s += x[i];
        part[tid] = s;
        for (int stride = 1; stride < nt; stride *= 2) {
#pragma omp barrier
            if (tid % (2 * stride) == 0 && tid + stride < nt) part[tid] += part[tid + stride];
        }
    }
    return part[0];
}

template <class T>
T reduce_omp(const std::vector<T>& x) {
    T s = 0;
#pragma omp parallel for reduction(+ : s) schedule(static)
    for (size_t i = 0; i < x.size(); ++i) s += x[i];
    return s;
}

// Inclusive, double-buffered; returns the number of additions performed.
size_t scan_hillis_steele(std::vector<i64>& a) {
    size_t n = a.size(), adds = 0;
    std::vector<i64> b(n);
    for (size_t d = 1; d < n; d *= 2) {
#pragma omp parallel for schedule(static)
        for (size_t i = 0; i < n; ++i) b[i] = i >= d ? a[i] + a[i - d] : a[i];
        adds += n - d;
        a.swap(b);
    }
    return adds;
}

// Exclusive, in place; pads to a power of two. Returns additions performed.
size_t scan_blelloch(std::vector<i64>& a) {
    size_t n0 = a.size(), n = 1, adds = 0;
    while (n < n0) n *= 2;
    a.resize(n, 0);
    for (size_t d = 1; d < n; d *= 2) {  // up-sweep (reduce) phase
        long m = long(n / (2 * d));
#pragma omp parallel for schedule(static)
        for (long j = 0; j < m; ++j) a[j * 2 * d + 2 * d - 1] += a[j * 2 * d + d - 1];
        adds += size_t(m);
    }
    a[n - 1] = 0;
    for (size_t d = n / 2; d >= 1; d /= 2) {  // down-sweep phase
        long m = long(n / (2 * d));
#pragma omp parallel for schedule(static)
        for (long j = 0; j < m; ++j) {
            size_t l = j * 2 * d + d - 1, r = j * 2 * d + 2 * d - 1;
            i64 t = a[l];
            a[l] = a[r];
            a[r] += t;
        }
        adds += size_t(m);
    }
    a.resize(n0);
    return adds;
}

// Exclusive: each thread scans its chunk, the p chunk totals are scanned,
// each thread adds its offset. Reads and writes every element twice: O(n).
void scan_three_phase(std::vector<i64>& a) {
    int p = omp_get_max_threads();
    std::vector<i64> tot(p + 1, 0);
    size_t n = a.size();
#pragma omp parallel num_threads(p)
    {
        int t = omp_get_thread_num(), nt = omp_get_num_threads();
        size_t lo = n * t / nt, hi = n * (t + 1) / nt;
        i64 s = 0;
        for (size_t i = lo; i < hi; ++i) { i64 v = a[i]; a[i] = s; s += v; }
        tot[t + 1] = s;
#pragma omp barrier
#pragma omp single
        for (int k = 1; k <= nt; ++k) tot[k] += tot[k - 1];
        for (size_t i = lo; i < hi; ++i) a[i] += tot[t];
    }
}

std::vector<i64> random_ints(size_t n, unsigned seed) {
    mc::Rng r(seed);
    std::vector<i64> v(n);
    for (auto& x : v) x = i64(r.next() % 1000) - 500;
    return v;
}

int run_test() {
    std::printf("reduction_scan --test\n");
    // Rupp's slide example [S4]
    std::vector<i64> x = {4, 3, 6, 5, 4, 7, 4, 4, 4};
    std::vector<i64> inc = {4, 7, 13, 18, 22, 29, 33, 37, 41}, exc = {0, 4, 7, 13, 18, 22, 29, 33, 37};
    auto h = x; scan_hillis_steele(h);
    auto b = x; scan_blelloch(b);
    auto t = x; scan_three_phase(t);
    mc::check(h == inc, "Hillis-Steele reproduces the inclusive scan of the slide example");
    mc::check(b == exc, "Blelloch reproduces the exclusive scan of the slide example (n=9, padded to 16)");
    mc::check(t == exc, "three-phase scan reproduces the exclusive scan of the slide example");

    for (size_t n : {size_t(1), size_t(1000), size_t(4096), size_t(100003)}) {
        auto v = random_ints(n, 7 + unsigned(n));
        std::vector<i64> ref_inc(n), ref_exc(n);
        std::inclusive_scan(v.begin(), v.end(), ref_inc.begin());
        std::exclusive_scan(v.begin(), v.end(), ref_exc.begin(), i64(0));
        auto v1 = v, v2 = v, v3 = v;
        scan_hillis_steele(v1); scan_blelloch(v2); scan_three_phase(v3);
        bool ok = v1 == ref_inc && v2 == ref_exc && v3 == ref_exc;
        i64 sref = std::accumulate(v.begin(), v.end(), i64(0));
        ok &= reduce_blocks(v) == sref && reduce_thread_tree(v) == sref && reduce_omp(v) == sref;
        std::printf("  n = %zu: ", n);
        mc::check(ok, "3 scans equal std::*_scan, 3 reductions equal std::accumulate (exact, int64)");
    }
    // work counts: Hillis-Steele sum_{d=2^k<n} (n-d); Blelloch 2(n-1)
    const size_t n = 1 << 12;
    auto v = random_ints(n, 1);
    auto v1 = v, v2 = v;
    size_t hs = scan_hillis_steele(v1), bl = scan_blelloch(v2);
    mc::check(hs == n * 12 - (n - 1), "Hillis-Steele does n log2 n - (n-1) = 45057 adds at n = 4096");
    mc::check(bl == 2 * (n - 1), "Blelloch does 2(n-1) = 8190 adds at n = 4096 (work-efficient)");

    // float: a tree has O(log n) error growth, a running sum O(n)
    std::vector<float> f(1 << 24, 0.1f);
    float serial = 0; for (float y : f) serial += y;
    float tree = reduce_blocks(f);
    double exact = double(f.size()) * double(0.1f);
    std::printf("  2^24 x 0.1f: exact %.1f, running sum %.1f, block tree %.1f\n", exact, serial, tree);
    mc::check(std::fabs(tree - exact) < 1e-4 * exact && std::fabs(serial - exact) > 0.1 * exact,
              "tree error < 1e-4 relative, running-sum error > 10 % (float, 2^24 terms)");
    return mc::finish();
}

void run(bool bench) {
    size_t n = bench ? (size_t(1) << 25) : (size_t(1) << 22);
    mc::Rng r(3);
    std::vector<double> xd(n);
    for (auto& v : xd) v = r.uniform();
    std::printf("reductions, n = %zu doubles (%.0f MB), %d threads, best of 5\n", n, 8e-6 * n,
                omp_get_max_threads());
    mc::print_load();
    double s0 = 0;
    auto show = [&](const char* name, double t) {
        std::printf("  %-26s %9.3f ms %8.1f GB/s\n", name, t * 1e3, 8.0 * n / t * 1e-9);
    };
    show("serial loop", mc::time_min([&] { s0 = 0; for (double v : xd) s0 += v; }));
    show("omp reduction clause", mc::time_min([&] { s0 = reduce_omp(xd); }));
    show("thread tree + barriers", mc::time_min([&] { s0 = reduce_thread_tree(xd); }));
    show("block tree (B=256), 2 passes", mc::time_min([&] { s0 = reduce_blocks(xd); }));

    size_t ns = bench ? (size_t(1) << 24) : (size_t(1) << 20);
    auto xi = random_ints(ns, 5);
    std::printf("scans, n = %zu int64 (%.0f MB)\n", ns, 8e-6 * ns);
    auto shs = [&](const char* name, double t) {
        std::printf("  %-26s %9.3f ms %8.1f Melem/s\n", name, t * 1e3, ns / t * 1e-6);
    };
    std::vector<i64> y(ns);
    shs("std::inclusive_scan serial", mc::time_min([&] { std::inclusive_scan(xi.begin(), xi.end(), y.begin()); }));
    shs("three-phase (chunks)", mc::time_min([&] { y = xi; scan_three_phase(y); }));
    shs("Blelloch up/down sweep", mc::time_min([&] { y = xi; scan_blelloch(y); }, 3));
    shs("Hillis-Steele", mc::time_min([&] { y = xi; scan_hillis_steele(y); }, 3));
    std::printf("  (timings of the three parallel scans include one copy y = x)\n");
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
