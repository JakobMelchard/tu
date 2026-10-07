// Sum reduction: Harris's kernel 1 (interleaved, divergent), kernel 3
// (sequential addressing) [S16], and a warp-shuffle + atomicAdd variant.
// UNTESTED here (no nvcc on this Mac). CPU mirror: ../cpp/reduction_scan.cpp
// (reduce_blocks = kernel 3 with a second pass; reduce_thread_tree = the
// barrier-per-level tree). Note 04, "Reductions".
#include <vector>

#include "common.cuh"

constexpr int B = 256;

// Kernel 1: stride doubles; thread t works if t % (2 stride) == 0. Active
// threads are scattered over all warps -> divergence, and the modulo is slow.
__global__ void reduce_interleaved(const double* in, double* out, size_t n) {
    __shared__ double s[B];
    unsigned t = threadIdx.x;
    size_t i = blockIdx.x * size_t(B) + t;
    s[t] = i < n ? in[i] : 0.0;
    __syncthreads();
    for (unsigned stride = 1; stride < B; stride *= 2) {
        if (t % (2 * stride) == 0) s[t] += s[t + stride];
        __syncthreads();
    }
    if (t == 0) out[blockIdx.x] = s[0];
}

// Kernel 3: stride halves; threads 0..stride-1 work. Whole warps retire
// together (no divergence until stride < 32), and s[t], s[t+stride] are
// consecutive 8-byte words across the warp: no bank conflicts [S15].
__global__ void reduce_sequential(const double* in, double* out, size_t n) {
    __shared__ double s[B];
    unsigned t = threadIdx.x;
    size_t i = blockIdx.x * size_t(B) + t;
    s[t] = i < n ? in[i] : 0.0;
    __syncthreads();
    for (unsigned stride = B / 2; stride > 0; stride >>= 1) {
        if (t < stride) s[t] += s[t + stride];
        __syncthreads();
    }
    if (t == 0) out[blockIdx.x] = s[0];
}

// Grid-stride accumulation in registers, warp reduction with shuffles (no
// shared memory, no __syncthreads inside a warp), one atomicAdd per warp.
// atomicAdd(double*) needs compute capability >= 6.0 [S15] "atomicAdd()".
__global__ void reduce_shfl_atomic(const double* in, double* out, size_t n) {
    double v = 0.0;
    for (size_t i = blockIdx.x * size_t(blockDim.x) + threadIdx.x; i < n; i += size_t(gridDim.x) * blockDim.x)
        v += in[i];
    for (int off = 16; off > 0; off >>= 1) v += __shfl_down_sync(0xffffffffu, v, off);
    if ((threadIdx.x & 31) == 0) atomicAdd(out, v);
}

// Two passes of a block kernel, as in the CPU mirror: n -> n/B -> ... -> 1.
template <class K>
double reduce_passes(K kernel, const double* d_in, size_t n, double* buf_a, double* buf_b) {
    const double* src = d_in;
    double* dst = buf_a;
    while (n > 1) {
        size_t nb = (n + B - 1) / B;
        kernel<<<unsigned(nb), B>>>(src, dst, n);
        CUDA_CHECK_LAUNCH();
        src = dst;
        dst = (dst == buf_a) ? buf_b : buf_a;
        n = nb;
    }
    double r = 0;
    CUDA_CHECK(cudaMemcpy(&r, src, sizeof(double), cudaMemcpyDeviceToHost));
    return r;
}

int main() {
    print_device();
    const size_t n = size_t(1) << 25;
    std::vector<double> h(n);
    for (size_t i = 0; i < n; ++i) h[i] = double(int(i % 17) - 8);  // integers: exact sums in any order
    double *d, *a, *b, *acc;
    CUDA_CHECK(cudaMalloc(&d, n * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&a, (n / B + 1) * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&b, (n / B + 1) * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&acc, sizeof(double)));
    CUDA_CHECK(cudaMemcpy(d, h.data(), n * sizeof(double), cudaMemcpyHostToDevice));

    for (size_t m : {size_t(1), size_t(1000), size_t(65537), n}) {
        double r1 = reduce_passes(reduce_interleaved, d, m, a, b);
        double r3 = reduce_passes(reduce_sequential, d, m, a, b);
        CUDA_CHECK(cudaMemset(acc, 0, sizeof(double)));
        reduce_shfl_atomic<<<1024, 256>>>(d, acc, m);
        CUDA_CHECK_LAUNCH();
        double rs = 0;
        CUDA_CHECK(cudaMemcpy(&rs, acc, sizeof(double), cudaMemcpyDeviceToHost));
        double want = 0;
        for (size_t i = 0; i < m; ++i) want += h[i];
        std::printf("  n = %zu: ", m);
        check(r1 == want && r3 == want && rs == want, "kernels 1, 3 and shuffle+atomic equal the host sum exactly");
    }

    auto gbs = [&](float ms) { return n * 8.0 / (ms * 1e-3) * 1e-9; };
    float t1 = time_ms([&] { reduce_passes(reduce_interleaved, d, n, a, b); });
    float t3 = time_ms([&] { reduce_passes(reduce_sequential, d, n, a, b); });
    float ts = time_ms([&] {
        CUDA_CHECK(cudaMemset(acc, 0, sizeof(double)));
        reduce_shfl_atomic<<<1024, 256>>>(d, acc, n);
    });
    std::printf("n = %zu doubles: interleaved %.3f ms (%.0f GB/s), sequential %.3f ms (%.0f GB/s), "
                "shuffle+atomic %.3f ms (%.0f GB/s)\n", n, t1, gbs(t1), t3, gbs(t3), ts, gbs(ts));
    CUDA_CHECK(cudaFree(d));
    CUDA_CHECK(cudaFree(a));
    CUDA_CHECK(cudaFree(b));
    CUDA_CHECK(cudaFree(acc));
    return finish();
}
