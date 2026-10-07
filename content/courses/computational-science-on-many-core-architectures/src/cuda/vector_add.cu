// x = y + z on the GPU: grid-stride kernel, bandwidth vs size (alpha-beta
// model), host<->device transfer rate, and copy/compute overlap with streams.
// UNTESTED here (no nvcc on this Mac). CPU mirror: ../cpp/stream_triad.cpp.
// Notes 02, 03 (alpha-beta, n_1/2) and 05 (streams). Sources: [S4] [S15].
#include <vector>

#include "common.cuh"

// Grid-stride loop: any grid size covers any n; consecutive threads touch
// consecutive doubles, so each warp's 32 loads coalesce into 256 B.
__global__ void vadd(const double* __restrict__ y, const double* __restrict__ z, double* __restrict__ x,
                     size_t n) {
    for (size_t i = blockIdx.x * size_t(blockDim.x) + threadIdx.x; i < n; i += size_t(gridDim.x) * blockDim.x)
        x[i] = y[i] + z[i];
}

static int grid_for(size_t n, int threads) {
    int sms = 0;
    CUDA_CHECK(cudaDeviceGetAttribute(&sms, cudaDevAttrMultiProcessorCount, 0));
    size_t want = (n + threads - 1) / threads, cap = size_t(sms) * 32;  // enough blocks to fill every SM
    return int(want < cap ? want : cap);
}

static void launch(const double* y, const double* z, double* x, size_t n, cudaStream_t s = 0) {
    vadd<<<grid_for(n, 256), 256, 0, s>>>(y, z, x, n);
    CUDA_CHECK_LAUNCH();
}

int main() {
    print_device();
    const size_t nmax = size_t(1) << 26;
    std::vector<double> hy(nmax), hz(nmax), hx(nmax);
    for (size_t i = 0; i < nmax; ++i) { hy[i] = double(i % 1000); hz[i] = 0.5; }
    double *y, *z, *x;
    CUDA_CHECK(cudaMalloc(&y, nmax * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&z, nmax * sizeof(double)));
    CUDA_CHECK(cudaMalloc(&x, nmax * sizeof(double)));
    CUDA_CHECK(cudaMemcpy(y, hy.data(), nmax * sizeof(double), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(z, hz.data(), nmax * sizeof(double), cudaMemcpyHostToDevice));

    // correctness, including an n that is not a multiple of the block size
    for (size_t n : {size_t(1), size_t(1000003), nmax}) {
        CUDA_CHECK(cudaMemset(x, 0, nmax * sizeof(double)));
        launch(y, z, x, n);
        CUDA_CHECK(cudaMemcpy(hx.data(), x, nmax * sizeof(double), cudaMemcpyDeviceToHost));
        bool ok = true;
        for (size_t i = 0; i < nmax; ++i) ok &= hx[i] == (i < n ? hy[i] + hz[i] : 0.0);
        std::printf("  n = %zu: ", n);
        check(ok, "x = y + z on [0,n), untouched beyond n");
    }

    // alpha-beta: T(N) = alpha + 24 N / beta. Rupp's model for this kernel [S4].
    std::printf("\n%12s %12s %10s\n", "N", "time [us]", "GB/s");
    double t_small = 0, t_big = 0;
    for (int lg = 10; lg <= 26; lg += 2) {
        size_t n = size_t(1) << lg;
        float ms = time_ms([&] { launch(y, z, x, n); }, 20);
        std::printf("%12zu %12.2f %10.1f\n", n, ms * 1e3, 24.0 * n / (ms * 1e-3) * 1e-9);
        if (lg == 10) t_small = ms * 1e-3;
        if (lg == 26) t_big = ms * 1e-3;
    }
    double beta = 24.0 * nmax / (t_big - t_small);
    std::printf("alpha ~ T(1024) = %.2f us, beta = %.1f GB/s, n_1/2 = alpha*beta = %.2f MB\n", t_small * 1e6,
                beta * 1e-9, t_small * beta / 1e6);

    // host <-> device over PCIe/NVLink: pageable vs pinned host memory
    double* pinned;
    CUDA_CHECK(cudaMallocHost(&pinned, nmax * sizeof(double)));
    float pg = time_ms([&] { CUDA_CHECK(cudaMemcpy(y, hy.data(), nmax * 8, cudaMemcpyHostToDevice)); }, 3);
    float pn = time_ms([&] { CUDA_CHECK(cudaMemcpy(y, pinned, nmax * 8, cudaMemcpyHostToDevice)); }, 3);
    std::printf("H2D %zu MB: pageable %.1f GB/s, pinned %.1f GB/s\n", nmax * 8 >> 20, nmax * 8 / (pg * 1e6),
                nmax * 8 / (pn * 1e6));

    // streams: split into chunks; copy-in(k+1) overlaps compute(k) and copy-out(k-1)
    const int S = 4;
    cudaStream_t st[S];
    for (auto& s : st) CUDA_CHECK(cudaStreamCreate(&s));
    for (size_t i = 0; i < nmax; ++i) pinned[i] = hy[i];
    double* pout;
    CUDA_CHECK(cudaMallocHost(&pout, nmax * sizeof(double)));
    const size_t chunk = nmax / 16;
    auto pipeline = [&](int ns) {
        for (size_t c = 0; c < 16; ++c) {
            cudaStream_t s = st[c % ns];
            size_t o = c * chunk;
            CUDA_CHECK(cudaMemcpyAsync(y + o, pinned + o, chunk * 8, cudaMemcpyHostToDevice, s));
            launch(y + o, z + o, x + o, chunk, s);
            CUDA_CHECK(cudaMemcpyAsync(pout + o, x + o, chunk * 8, cudaMemcpyDeviceToHost, s));
        }
        CUDA_CHECK(cudaDeviceSynchronize());
    };
    float t1 = time_ms([&] { pipeline(1); }, 3), t4 = time_ms([&] { pipeline(S); }, 3);
    std::printf("copy-in + add + copy-out, 16 chunks: 1 stream %.2f ms, %d streams %.2f ms (%.2fx)\n", t1, S, t4,
                t1 / t4);
    bool ok = true;
    for (size_t i = 0; i < nmax; ++i) ok &= pout[i] == hy[i] + hz[i];
    check(ok, "streamed pipeline gives the same x = y + z");

    for (auto& s : st) CUDA_CHECK(cudaStreamDestroy(s));
    CUDA_CHECK(cudaFreeHost(pinned));
    CUDA_CHECK(cudaFreeHost(pout));
    CUDA_CHECK(cudaFree(y));
    CUDA_CHECK(cudaFree(z));
    CUDA_CHECK(cudaFree(x));
    return finish();
}
