// Prefix sums on the GPU: Hillis-Steele inside one block (the code on Rupp's
// slide [S4]), and the work-efficient Blelloch scan [S17] per block with the
// bank-conflict-avoiding padding of GPU Gems 3 ch. 39 [S18], extended to any n
// by scanning the block sums recursively and adding them back.
// UNTESTED here (no nvcc on this Mac). CPU mirror: ../cpp/reduction_scan.cpp
// (scan_hillis_steele, scan_blelloch, scan_three_phase). Note 04, "Scans".
#include <vector>

#include "common.cuh"

constexpr int B = 256;              // threads per block; each scans 2B elements
constexpr int LOG_BANKS = 5;        // 32 banks of 4-byte words [S15]
#define PAD(i) ((i) + ((i) >> LOG_BANKS))

// Inclusive scan of up to blockDim.x ints in one block, O(n log n) work.
__global__ void scan_hillis_steele_block(const int* in, int* out, int n) {
    extern __shared__ int buf[];
    int t = threadIdx.x;
    int my = t < n ? in[t] : 0;
    for (int stride = 1; stride < int(blockDim.x); stride *= 2) {
        __syncthreads();
        buf[t] = my;
        __syncthreads();
        if (t >= stride) my += buf[t - stride];
    }
    if (t < n) out[t] = my;
}

// Exclusive Blelloch scan of 2B elements per block; block total -> sums.
__global__ void scan_blelloch_block(const int* in, int* out, int* sums, int n) {
    __shared__ int s[PAD(2 * B)];
    int t = threadIdx.x, base = blockIdx.x * 2 * B;
    int ai = t, bi = t + B;
    s[PAD(ai)] = base + ai < n ? in[base + ai] : 0;
    s[PAD(bi)] = base + bi < n ? in[base + bi] : 0;
    int off = 1;
    for (int d = B; d > 0; d >>= 1) {  // up-sweep: build partial sums in place
        __syncthreads();
        if (t < d) {
            int l = off * (2 * t + 1) - 1, r = off * (2 * t + 2) - 1;
            s[PAD(r)] += s[PAD(l)];
        }
        off *= 2;
    }
    if (t == 0) {
        if (sums) sums[blockIdx.x] = s[PAD(2 * B - 1)];
        s[PAD(2 * B - 1)] = 0;
    }
    for (int d = 1; d < 2 * B; d *= 2) {  // down-sweep: push prefixes down the tree
        off >>= 1;
        __syncthreads();
        if (t < d) {
            int l = off * (2 * t + 1) - 1, r = off * (2 * t + 2) - 1;
            int tmp = s[PAD(l)];
            s[PAD(l)] = s[PAD(r)];
            s[PAD(r)] += tmp;
        }
    }
    __syncthreads();
    if (base + ai < n) out[base + ai] = s[PAD(ai)];
    if (base + bi < n) out[base + bi] = s[PAD(bi)];
}

__global__ void add_block_offsets(int* out, const int* offs, int n) {
    int i = blockIdx.x * 2 * B + threadIdx.x;
    int o = offs[blockIdx.x];
    if (i < n) out[i] += o;
    if (i + B < n) out[i + B] += o;
}

// Exclusive scan of any n: scan blocks, scan block sums (recursively), add.
void scan_device(const int* d_in, int* d_out, int n) {
    int nb = (n + 2 * B - 1) / (2 * B);
    int *sums = nullptr, *sums_scanned = nullptr;
    if (nb > 1) {
        CUDA_CHECK(cudaMalloc(&sums, nb * sizeof(int)));
        CUDA_CHECK(cudaMalloc(&sums_scanned, nb * sizeof(int)));
    }
    scan_blelloch_block<<<nb, B>>>(d_in, d_out, sums, n);
    CUDA_CHECK_LAUNCH();
    if (nb > 1) {
        scan_device(sums, sums_scanned, nb);
        add_block_offsets<<<nb, B>>>(d_out, sums_scanned, n);
        CUDA_CHECK_LAUNCH();
        CUDA_CHECK(cudaFree(sums));
        CUDA_CHECK(cudaFree(sums_scanned));
    }
}

int main() {
    print_device();
    // Rupp's slide example [S4]
    std::vector<int> x = {4, 3, 6, 5, 4, 7, 4, 4, 4}, inc(9), exc(9);
    int *dx, *dy;
    CUDA_CHECK(cudaMalloc(&dx, 9 * sizeof(int)));
    CUDA_CHECK(cudaMalloc(&dy, 9 * sizeof(int)));
    CUDA_CHECK(cudaMemcpy(dx, x.data(), 9 * sizeof(int), cudaMemcpyHostToDevice));
    scan_hillis_steele_block<<<1, 32, 32 * sizeof(int)>>>(dx, dy, 9);
    CUDA_CHECK_LAUNCH();
    CUDA_CHECK(cudaMemcpy(inc.data(), dy, 9 * sizeof(int), cudaMemcpyDeviceToHost));
    scan_device(dx, dy, 9);
    CUDA_CHECK(cudaMemcpy(exc.data(), dy, 9 * sizeof(int), cudaMemcpyDeviceToHost));
    check(inc == std::vector<int>({4, 7, 13, 18, 22, 29, 33, 37, 41}), "Hillis-Steele block: slide example, inclusive");
    check(exc == std::vector<int>({0, 4, 7, 13, 18, 22, 29, 33, 37}), "Blelloch: slide example, exclusive");
    CUDA_CHECK(cudaFree(dx));
    CUDA_CHECK(cudaFree(dy));

    for (int n : {1, 512, 513, 1000, (1 << 20) + 3, 1 << 24}) {
        std::vector<int> h(n), got(n), want(n);
        for (int i = 0; i < n; ++i) h[i] = (i * 7 + 3) % 10;
        int run = 0;
        for (int i = 0; i < n; ++i) { want[i] = run; run += h[i]; }
        int *din, *dout;
        CUDA_CHECK(cudaMalloc(&din, n * sizeof(int)));
        CUDA_CHECK(cudaMalloc(&dout, n * sizeof(int)));
        CUDA_CHECK(cudaMemcpy(din, h.data(), n * sizeof(int), cudaMemcpyHostToDevice));
        scan_device(din, dout, n);
        CUDA_CHECK(cudaMemcpy(got.data(), dout, n * sizeof(int), cudaMemcpyDeviceToHost));
        std::printf("  n = %d: ", n);
        check(got == want, "multi-block Blelloch equals the host exclusive scan");
        if (n == 1 << 24) {
            float ms = time_ms([&] { scan_device(din, dout, n); });
            std::printf("  n = 2^24 ints: %.3f ms, %.1f GB/s (8 B/element: read + write)\n", ms, 8.0 * n / (ms * 1e6));
        }
        CUDA_CHECK(cudaFree(din));
        CUDA_CHECK(cudaFree(dout));
    }
    return finish();
}
