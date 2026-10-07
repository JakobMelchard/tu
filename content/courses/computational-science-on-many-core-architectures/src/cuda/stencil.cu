// 2-D Jacobi sweep for the Laplace equation: naive (every neighbour read from
// global memory, caches permitting) vs a shared-memory tile with a one-cell
// halo. Grid (n+2) x (n+2), halo = Dirichlet data, as in the CPU mirror
// ../cpp/stencil_halo.cpp. UNTESTED here (no nvcc on this Mac). Notes 03, 04.
//
// Build with -fmad=false (see Makefile) so the GPU rounds exactly like the CPU
// reference: the check below is bitwise.
#include <vector>

#include "common.cuh"

constexpr int TB = 16;

__device__ __host__ inline double upd(double n, double s, double w, double e) { return 0.25 * (((n + s) + w) + e); }

__global__ void jacobi_naive(const double* u, double* w, int n) {
    int j = blockIdx.x * blockDim.x + threadIdx.x + 1, i = blockIdx.y * blockDim.y + threadIdx.y + 1;
    int W = n + 2;
    if (i <= n && j <= n)
        w[i * W + j] = upd(u[(i - 1) * W + j], u[(i + 1) * W + j], u[i * W + j - 1], u[i * W + j + 1]);
}

// (TB+2)^2 loads per TB^2 updates. Interior threads load their own point;
// edge threads additionally load the halo cell next to them.
__global__ void jacobi_smem(const double* u, double* w, int n) {
    __shared__ double s[TB + 2][TB + 2];
    int tx = threadIdx.x, ty = threadIdx.y;
    int j = blockIdx.x * TB + tx + 1, i = blockIdx.y * TB + ty + 1, W = n + 2;
    bool in = i <= n && j <= n;
    if (in) {
        s[ty + 1][tx + 1] = u[i * W + j];
        if (tx == 0) s[ty + 1][0] = u[i * W + j - 1];
        if (ty == 0) s[0][tx + 1] = u[(i - 1) * W + j];
        if (tx == TB - 1 || j == n) s[ty + 1][tx + 2] = u[i * W + j + 1];
        if (ty == TB - 1 || i == n) s[ty + 2][tx + 1] = u[(i + 1) * W + j];
    }
    __syncthreads();  // every thread reaches this barrier (no early return)
    if (in) w[i * W + j] = upd(s[ty][tx + 1], s[ty + 2][tx + 1], s[ty + 1][tx], s[ty + 1][tx + 2]);
}

static void host_sweep(const std::vector<double>& u, std::vector<double>& w, int n) {
    int W = n + 2;
    for (int i = 1; i <= n; ++i)
        for (int j = 1; j <= n; ++j)
            w[i * W + j] = upd(u[(i - 1) * W + j], u[(i + 1) * W + j], u[i * W + j - 1], u[i * W + j + 1]);
}

int main() {
    print_device();
    for (int n : {67, 4094}) {
        size_t N = size_t(n + 2) * (n + 2);
        std::vector<double> h(N), a, b(N), got(N);
        unsigned long long s = 12345;
        for (auto& v : h) { s = s * 6364136223846793005ULL + 1442695040888963407ULL; v = double(s >> 11) / 9007199254740992.0; }
        double *du, *dw;
        CUDA_CHECK(cudaMalloc(&du, N * 8));
        CUDA_CHECK(cudaMalloc(&dw, N * 8));
        dim3 blk(TB, TB), grd((n + TB - 1) / TB, (n + TB - 1) / TB);
        auto run = [&](bool smem, int iters) {
            CUDA_CHECK(cudaMemcpy(du, h.data(), N * 8, cudaMemcpyHostToDevice));
            CUDA_CHECK(cudaMemcpy(dw, h.data(), N * 8, cudaMemcpyHostToDevice));  // halo in both buffers
            for (int k = 0; k < iters; ++k) {
                if (smem) jacobi_smem<<<grd, blk>>>(du, dw, n); else jacobi_naive<<<grd, blk>>>(du, dw, n);
                CUDA_CHECK_LAUNCH();
                std::swap(du, dw);
            }
            CUDA_CHECK(cudaMemcpy(got.data(), du, N * 8, cudaMemcpyDeviceToHost));
        };
        if (n == 67) {
            a = h;
            b = h;
            for (int k = 0; k < 50; ++k) { host_sweep(a, b, n); std::swap(a, b); }
            run(false, 50);
            bool ok1 = got == a;
            run(true, 50);
            bool ok2 = got == a;
            check(ok1 && ok2, "naive and shared-memory kernels equal the host after 50 sweeps, bitwise (n = 67)");
        } else {
            CUDA_CHECK(cudaMemcpy(du, h.data(), N * 8, cudaMemcpyHostToDevice));
            CUDA_CHECK(cudaMemcpy(dw, h.data(), N * 8, cudaMemcpyHostToDevice));
            float tn = time_ms([&] { jacobi_naive<<<grd, blk>>>(du, dw, n); });
            float ts = time_ms([&] { jacobi_smem<<<grd, blk>>>(du, dw, n); });
            double lup = double(n) * n;
            std::printf("  n = %d: naive %.0f MLUP/s (%.0f GB/s at 16 B/LUP), smem %.0f MLUP/s (%.0f GB/s)\n", n,
                        lup / (tn * 1e3), 16 * lup / (tn * 1e6), lup / (ts * 1e3), 16 * lup / (ts * 1e6));
        }
        CUDA_CHECK(cudaFree(du));
        CUDA_CHECK(cudaFree(dw));
    }
    return finish();
}
