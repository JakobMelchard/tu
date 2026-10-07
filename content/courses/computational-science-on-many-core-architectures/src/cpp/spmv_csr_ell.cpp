// Sparse matrix-vector product y = A x in three layouts: CSR, ELLPACK
// (column-major, padded to the longest row) and SELL-C-sigma (rows sorted by
// length inside windows of sigma rows, chunks of C rows padded to the chunk's
// longest row) [S20] [S21]. Same per-row summation order in all three, so the
// results are bitwise equal. Note 04 ("Coalescing") and note 03 (bandwidth).
//
// Why the layouts exist: on a GPU, thread i handles row i. In ELL/SELL the k-th
// entries of consecutive rows are adjacent in memory, so a warp's loads
// coalesce; in CSR they are row-length apart. The price is padding: fill
// efficiency beta = nnz / stored entries. On the CPU the layouts cost about the
// same; the point here is the storage and the checked equivalence.
#include <numeric>

#include "common.hpp"

using mc::Mode;

namespace {

struct CSR {
    int n = 0;
    std::vector<int> ptr, col;
    std::vector<double> val;
    size_t nnz() const { return val.size(); }
    int len(int i) const { return ptr[i + 1] - ptr[i]; }
};

CSR laplace2d(int m) {  // 5-point stencil on an m x m grid, Dirichlet, N = m^2
    CSR A;
    A.n = m * m;
    A.ptr.push_back(0);
    for (int i = 0; i < m; ++i)
        for (int j = 0; j < m; ++j) {
            int r = i * m + j;
            auto put = [&](int c, double v) { A.col.push_back(c); A.val.push_back(v); };
            if (i > 0) put(r - m, -1);
            if (j > 0) put(r - 1, -1);
            put(r, 4);
            if (j < m - 1) put(r + 1, -1);
            if (i < m - 1) put(r + m, -1);
            A.ptr.push_back(int(A.col.size()));
        }
    return A;
}

CSR irregular(int n, unsigned seed) {  // row lengths 1..128, heavy-tailed
    mc::Rng r(seed);
    CSR A;
    A.n = n;
    A.ptr.push_back(0);
    for (int i = 0; i < n; ++i) {
        double u = r.uniform();
        int len = 1 + int(127 * u * u * u * u);  // most rows short, a few long
        for (int k = 0; k < len; ++k) {
            A.col.push_back(int(r.next() % unsigned(n)));
            A.val.push_back(r.uniform() - 0.5);
        }
        A.ptr.push_back(int(A.col.size()));
    }
    return A;
}

void spmv_csr(const CSR& A, const std::vector<double>& x, std::vector<double>& y) {
#pragma omp parallel for schedule(static)
    for (int i = 0; i < A.n; ++i) {
        double s = 0;
        for (int k = A.ptr[i]; k < A.ptr[i + 1]; ++k) s += A.val[k] * x[A.col[k]];
        y[i] = s;
    }
}

struct ELL {  // val[k*n + i]: entry k of row i; padding has col = i, val = 0
    int n = 0, K = 0;
    std::vector<int> col;
    std::vector<double> val;
    explicit ELL(const CSR& A) : n(A.n) {
        for (int i = 0; i < n; ++i) K = std::max(K, A.len(i));
        col.assign(size_t(K) * n, 0);
        val.assign(size_t(K) * n, 0.0);
        for (int i = 0; i < n; ++i)
            for (int k = 0; k < K; ++k) {
                bool real = k < A.len(i);
                col[size_t(k) * n + i] = real ? A.col[A.ptr[i] + k] : i;
                val[size_t(k) * n + i] = real ? A.val[A.ptr[i] + k] : 0.0;
            }
    }
    void spmv(const std::vector<double>& x, std::vector<double>& y) const {
#pragma omp parallel for schedule(static)
        for (int i = 0; i < n; ++i) {
            double s = 0;
            for (int k = 0; k < K; ++k) s += val[size_t(k) * n + i] * x[col[size_t(k) * n + i]];
            y[i] = s;
        }
    }
};

struct SELL {  // chunk c holds rows perm[c*C .. c*C+C-1], column-major inside
    int n = 0, C = 0, nchunks = 0;
    std::vector<int> perm, clen, cptr, col;
    std::vector<double> val;
    SELL(const CSR& A, int C_, int sigma) : n(A.n), C(C_) {
        perm.resize(n);
        std::iota(perm.begin(), perm.end(), 0);
        for (int s = 0; s < n; s += sigma)  // sort by length inside each sigma-window only
            std::stable_sort(perm.begin() + s, perm.begin() + std::min(n, s + sigma),
                             [&](int a, int b) { return A.len(a) > A.len(b); });
        nchunks = (n + C - 1) / C;
        cptr.push_back(0);
        for (int c = 0; c < nchunks; ++c) {
            int L = 0;
            for (int r = 0; r < C && c * C + r < n; ++r) L = std::max(L, A.len(perm[c * C + r]));
            clen.push_back(L);
            cptr.push_back(cptr.back() + L * C);
        }
        col.assign(cptr.back(), 0);
        val.assign(cptr.back(), 0.0);
        for (int c = 0; c < nchunks; ++c)
            for (int r = 0; r < C; ++r) {
                int row = c * C + r < n ? perm[c * C + r] : -1;
                for (int k = 0; k < clen[c]; ++k) {
                    bool real = row >= 0 && k < A.len(row);
                    size_t at = cptr[c] + size_t(k) * C + r;
                    col[at] = real ? A.col[A.ptr[row] + k] : 0;
                    val[at] = real ? A.val[A.ptr[row] + k] : 0.0;
                }
            }
    }
    void spmv(const std::vector<double>& x, std::vector<double>& y) const {
#pragma omp parallel for schedule(dynamic, 16)
        for (int c = 0; c < nchunks; ++c) {
            double s[64] = {};  // C <= 64
            for (int k = 0; k < clen[c]; ++k)
                for (int r = 0; r < C; ++r) {
                    size_t at = cptr[c] + size_t(k) * C + r;
                    s[r] += val[at] * x[col[at]];
                }
            for (int r = 0; r < C && c * C + r < n; ++r) y[perm[c * C + r]] = s[r];
        }
    }
};

std::vector<double> rand_vec(int n, unsigned seed) {
    mc::Rng r(seed);
    std::vector<double> x(n);
    for (auto& v : x) v = r.uniform();
    return x;
}

int run_test() {
    std::printf("spmv_csr_ell --test\n");
    CSR L = laplace2d(10);
    std::vector<double> ones(L.n, 1.0), y(L.n);
    spmv_csr(L, ones, y);
    bool ok = y[0] == 2 && y[1] == 1 && y[11] == 0 && y[99] == 2;
    mc::check(ok, "Laplacian * ones = 4 - #neighbours: corner 2, edge 1, interior 0");
    CSR R = irregular(1003, 4);
    for (int which = 0; which < 2; ++which) {
        const CSR& M = which ? R : L;
        auto x = rand_vec(M.n, 9);
        std::vector<double> y0(M.n), y1(M.n), y2(M.n), y3(M.n);
        spmv_csr(M, x, y0);
        ELL(M).spmv(x, y1);
        SELL(M, 8, 64).spmv(x, y2);
        SELL(M, 32, 1).spmv(x, y3);  // sigma = 1: no sorting, pure chunked ELL
        std::printf("  %s: ", which ? "irregular(1003)" : "laplace2d(10)");
        mc::check(y1 == y0 && y2 == y0 && y3 == y0, "ELL, SELL-8-64 and SELL-32-1 equal CSR bitwise");
    }
    // dense cross-check on a small irregular matrix
    CSR S = irregular(40, 2);
    auto x = rand_vec(40, 3);
    std::vector<double> dense(40 * 40, 0.0), yd(40, 0.0), ys(40);
    for (int i = 0; i < 40; ++i)
        for (int k = S.ptr[i]; k < S.ptr[i + 1]; ++k) dense[i * 40 + S.col[k]] += S.val[k];
    for (int i = 0; i < 40; ++i)
        for (int j = 0; j < 40; ++j) yd[i] += dense[i * 40 + j] * x[j];
    spmv_csr(S, x, ys);
    mc::check(mc::max_abs_diff(yd, ys) < 1e-13, "CSR equals the dense product (duplicates summed) to 1e-13");
    return mc::finish();
}

void report(const char* name, const CSR& A, int reps) {
    auto x = rand_vec(A.n, 1);
    std::vector<double> y(A.n);
    ELL E(A);
    SELL S8(A, 8, 256), S32(A, 32, 1024);
    double nnz = A.nnz(), vec = 16.0 * A.n;
    double csr_bytes = 12 * nnz + 4.0 * (A.n + 1) + vec;  // val+col, ptr, x once + y
    std::printf("%s: N = %d, nnz = %.0f, max row %d\n", name, A.n, nnz, E.K);
    std::printf("  %-12s %10s %8s %10s %12s\n", "format", "stored", "beta", "time [ms]", "GB/s (own)");
    auto row = [&](const char* f, double stored, double bytes, double t) {
        std::printf("  %-12s %10.0f %8.3f %10.3f %12.1f\n", f, stored, nnz / stored, t * 1e3, bytes / t * 1e-9);
    };
    row("CSR", nnz, csr_bytes, mc::time_min([&] { spmv_csr(A, x, y); }, reps));
    double se = double(E.val.size());
    row("ELL", se, 12 * se + vec, mc::time_min([&] { E.spmv(x, y); }, reps));
    double s8 = double(S8.val.size()), s32 = double(S32.val.size());
    row("SELL-8-256", s8, 12 * s8 + vec + 4.0 * A.n, mc::time_min([&] { S8.spmv(x, y); }, reps));
    row("SELL-32-1024", s32, 12 * s32 + vec + 4.0 * A.n, mc::time_min([&] { S32.spmv(x, y); }, reps));
}

void run(bool bench) {
    int m = bench ? 2048 : 1024, reps = bench ? 10 : 5;
    std::printf("SpMV, %d threads, best of %d; GB/s counts each format's own stored bytes\n",
                omp_get_max_threads(), reps);
    mc::print_load();
    report("laplace2d", laplace2d(m), reps);
    report("irregular", irregular(bench ? 1 << 19 : 1 << 17, 7), reps);
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
