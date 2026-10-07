// Dense C = A B, naive vs shared-memory-style tiling, on the CPU with OpenMP.
// Mirrors src/cuda/tiled_matmul.cu (the CUDA Programming Guide's shared-memory
// matmul [S15], "Shared Memory"). Note 04, section "Tiling"; note 03 for the
// traffic model.
//
// naive:  one "thread" per C(i,j), reads a row of A and a column of B from
//         memory: 2n loads per 2n flops, AI = 1/8 flop/B without caches.
// tiled:  one "block" per T x T tile of C. It stages a T x T tile of A and of B
//         in a local buffer (the shared memory), then every element staged is
//         used T times: global traffic 2 n^3 / T doubles, AI = T/8 flop/B.
#include "common.hpp"

using mc::Mode;

namespace {

using Mat = std::vector<double>;  // row-major n x n

void matmul_naive(const Mat& A, const Mat& B, Mat& C, int n) {
#pragma omp parallel for collapse(2) schedule(static)
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) {
            double s = 0;
            for (int k = 0; k < n; ++k) s += A[size_t(i) * n + k] * B[size_t(k) * n + j];
            C[size_t(i) * n + j] = s;
        }
}

template <int T>
void matmul_tiled(const Mat& A, const Mat& B, Mat& C, int n) {
    const int nt = (n + T - 1) / T;
#pragma omp parallel for collapse(2) schedule(static)
    for (int bi = 0; bi < nt; ++bi)
        for (int bj = 0; bj < nt; ++bj) {
            alignas(64) double As[T][T], Bs[T][T], acc[T][T] = {};
            for (int bk = 0; bk < nt; ++bk) {
                // "load phase": every thread (i,j) of the block loads one element
                // of each tile, zero-padded at the matrix edge; then __syncthreads()
                for (int i = 0; i < T; ++i)
                    for (int j = 0; j < T; ++j) {
                        int r = bi * T + i, c = bk * T + j, r2 = bk * T + i, c2 = bj * T + j;
                        As[i][j] = (r < n && c < n) ? A[size_t(r) * n + c] : 0.0;
                        Bs[i][j] = (r2 < n && c2 < n) ? B[size_t(r2) * n + c2] : 0.0;
                    }
                // "compute phase" out of the fast buffer; i-k-j order vectorises
                for (int i = 0; i < T; ++i)
                    for (int k = 0; k < T; ++k) {
                        double a = As[i][k];
                        for (int j = 0; j < T; ++j) acc[i][j] += a * Bs[k][j];
                    }
            }
            for (int i = 0; i < T; ++i)
                for (int j = 0; j < T; ++j) {
                    int r = bi * T + i, c = bj * T + j;
                    if (r < n && c < n) C[size_t(r) * n + c] = acc[i][j];
                }
        }
}

Mat random_int_matrix(int n, unsigned seed) {  // entries in [-4, 4]: exact in double
    mc::Rng r(seed);
    Mat m(size_t(n) * n);
    for (auto& x : m) x = double(int(r.next() % 9) - 4);
    return m;
}

Mat random_matrix(int n, unsigned seed) {
    mc::Rng r(seed);
    Mat m(size_t(n) * n);
    for (auto& x : m) x = r.uniform() - 0.5;
    return m;
}

int run_test() {
    std::printf("matmul_tiling --test\n");
    for (int n : {1, 31, 64, 100}) {
        Mat A = random_int_matrix(n, 1 + n), B = random_int_matrix(n, 2 + n);
        Mat C0(size_t(n) * n), C1(C0.size()), C2(C0.size());
        // reference: textbook triple loop, serial
        for (int i = 0; i < n; ++i)
            for (int j = 0; j < n; ++j) {
                double s = 0;
                for (int k = 0; k < n; ++k) s += A[size_t(i) * n + k] * B[size_t(k) * n + j];
                C0[size_t(i) * n + j] = s;
            }
        matmul_naive(A, B, C1, n);
        matmul_tiled<16>(A, B, C2, n);
        std::printf("  n = %3d: ", n);
        mc::check(C1 == C0 && C2 == C0, "naive and tiled(16) equal the serial triple loop exactly (integer entries)");
    }
    const int n = 200;
    Mat A = random_matrix(n, 5), B = random_matrix(n, 6), C1(size_t(n) * n), C2(C1.size());
    matmul_naive(A, B, C1, n);
    matmul_tiled<32>(A, B, C2, n);
    double d = mc::max_abs_diff(C1, C2);
    std::printf("  n = 200 random reals: max |naive - tiled(32)| = %.2e\n", d);
    mc::check(d < 1e-12, "tiled accumulates k in the same order as naive: agrees to < 1e-12");
    // A B with B = identity returns A
    Mat I(size_t(n) * n, 0.0);
    for (int i = 0; i < n; ++i) I[size_t(i) * n + i] = 1.0;
    matmul_tiled<32>(A, I, C2, n);
    mc::check(C2 == A, "A * I == A exactly");
    return mc::finish();
}

void run(bool bench) {
    const int n = bench ? 1536 : 512;
    Mat A = random_matrix(n, 1), B = random_matrix(n, 2), C(size_t(n) * n);
    const double flops = 2.0 * n * n * double(n);
    std::printf("C = A B, n = %d, %d threads, best of 3\n", n, omp_get_max_threads());
    mc::print_load();
    std::printf("  %-12s %10s %10s %24s\n", "variant", "time [s]", "GFLOP/s", "model AI (DRAM, no cache)");
    auto row = [&](const char* name, double t, double ai) {
        std::printf("  %-12s %10.4f %10.2f %20.3f flop/B\n", name, t, flops / t * 1e-9, ai);
    };
    row("naive", mc::time_min([&] { matmul_naive(A, B, C, n); }, 3), 1.0 / 8);
    row("tiled T=8", mc::time_min([&] { matmul_tiled<8>(A, B, C, n); }, 3), 8.0 / 8);
    row("tiled T=16", mc::time_min([&] { matmul_tiled<16>(A, B, C, n); }, 3), 16.0 / 8);
    row("tiled T=32", mc::time_min([&] { matmul_tiled<32>(A, B, C, n); }, 3), 32.0 / 8);
    row("tiled T=64", mc::time_min([&] { matmul_tiled<64>(A, B, C, n); }, 3), 64.0 / 8);
    std::printf("  tile buffers per thread: 3 T^2 doubles = %d KB at T=32, %d KB at T=64 (P-core L1d: 128 KB)\n",
                3 * 32 * 32 * 8 / 1024, 3 * 64 * 64 * 8 / 1024);
}

}  // namespace

int main(int argc, char** argv) {
    Mode m = mc::parse_mode(argc, argv);
    if (m == Mode::test) return run_test();
    run(m == Mode::bench);
    return 0;
}
