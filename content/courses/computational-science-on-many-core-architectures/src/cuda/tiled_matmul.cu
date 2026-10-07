// C = A B in double: one thread per C(i,j), naive vs shared-memory tiles, the
// pattern of the CUDA Programming Guide's shared-memory example [S15].
// UNTESTED here (no nvcc on this Mac). CPU mirror: ../cpp/matmul_tiling.cpp.
// Note 04, "Tiling"; traffic model in note 03 (AI = T/8 flop/B).
#include <cmath>
#include <vector>

#include "common.cuh"

// Thread (tx, ty) of block (bx, by) computes C(row, col). Consecutive tx read
// consecutive B(k, col): coalesced; A(row, k) is a broadcast within a warp.
__global__ void mm_naive(const double* A, const double* B, double* C, int n) {
    int row = blockIdx.y * blockDim.y + threadIdx.y, col = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= n || col >= n) return;
    double s = 0;
    for (int k = 0; k < n; ++k) s += A[size_t(row) * n + k] * B[size_t(k) * n + col];
    C[size_t(row) * n + col] = s;
}

// Each block stages a T x T tile of A and of B in shared memory per k-step;
// every staged value is reused T times. Two __syncthreads per step: after the
// load (tiles complete) and after the compute (nobody overwrites a tile still
// being read). No early return: all threads must reach the barriers.
template <int T>
__global__ void mm_tiled(const double* A, const double* B, double* C, int n) {
    __shared__ double As[T][T];
    __shared__ double Bs[T][T + 1];  // +1 column: no bank conflicts if read column-wise
    int tx = threadIdx.x, ty = threadIdx.y;
    int row = blockIdx.y * T + ty, col = blockIdx.x * T + tx;
    double s = 0;
    for (int k0 = 0; k0 < n; k0 += T) {
        As[ty][tx] = (row < n && k0 + tx < n) ? A[size_t(row) * n + k0 + tx] : 0.0;
        Bs[ty][tx] = (k0 + ty < n && col < n) ? B[size_t(k0 + ty) * n + col] : 0.0;
        __syncthreads();
        for (int k = 0; k < T; ++k) s += As[ty][k] * Bs[k][tx];
        __syncthreads();
    }
    if (row < n && col < n) C[size_t(row) * n + col] = s;
}

static void host_ref(const std::vector<double>& A, const std::vector<double>& B, std::vector<double>& C, int n) {
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j) {
            double s = 0;
            for (int k = 0; k < n; ++k) s += A[size_t(i) * n + k] * B[size_t(k) * n + j];
            C[size_t(i) * n + j] = s;
        }
}

int main() {
    print_device();
    for (int n : {1, 31, 100, 257, 2048}) {
        size_t nn = size_t(n) * n;
        std::vector<double> A(nn), B(nn), C(nn), ref(nn);
        for (size_t i = 0; i < nn; ++i) { A[i] = double(int(i * 7 % 9) - 4); B[i] = double(int(i * 5 % 9) - 4); }
        double *dA, *dB, *dC;
        CUDA_CHECK(cudaMalloc(&dA, nn * 8));
        CUDA_CHECK(cudaMalloc(&dB, nn * 8));
        CUDA_CHECK(cudaMalloc(&dC, nn * 8));
        CUDA_CHECK(cudaMemcpy(dA, A.data(), nn * 8, cudaMemcpyHostToDevice));
        CUDA_CHECK(cudaMemcpy(dB, B.data(), nn * 8, cudaMemcpyHostToDevice));
        dim3 blk16(16, 16), grd16((n + 15) / 16, (n + 15) / 16);
        dim3 blk32(32, 32), grd32((n + 31) / 32, (n + 31) / 32);
        auto naive = [&] { mm_naive<<<grd16, blk16>>>(dA, dB, dC, n); CUDA_CHECK_LAUNCH(); };
        auto t16 = [&] { mm_tiled<16><<<grd16, blk16>>>(dA, dB, dC, n); CUDA_CHECK_LAUNCH(); };
        auto t32 = [&] { mm_tiled<32><<<grd32, blk32>>>(dA, dB, dC, n); CUDA_CHECK_LAUNCH(); };
        if (n <= 257) {
            host_ref(A, B, ref, n);
            bool ok = true;
            for (auto f : {0, 1, 2}) {
                if (f == 0) naive(); else if (f == 1) t16(); else t32();
                CUDA_CHECK(cudaMemcpy(C.data(), dC, nn * 8, cudaMemcpyDeviceToHost));
                ok &= C == ref;  // integer entries: exact regardless of FMA contraction
            }
            std::printf("  n = %d: ", n);
            check(ok, "naive, tiled<16>, tiled<32> equal the host triple loop exactly");
        } else {
            double fl = 2.0 * n * n * double(n);
            float a = time_ms(naive, 3), b = time_ms(t16, 3), c = time_ms(t32, 3);
            std::printf("  n = %d: naive %.1f, tiled16 %.1f, tiled32 %.1f GFLOP/s (FP64)\n", n, fl / a * 1e-6,
                        fl / b * 1e-6, fl / c * 1e-6);
        }
        CUDA_CHECK(cudaFree(dA));
        CUDA_CHECK(cudaFree(dB));
        CUDA_CHECK(cudaFree(dC));
    }
    return finish();
}
