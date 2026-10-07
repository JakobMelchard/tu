// Shared host helpers for the CUDA examples. UNTESTED on the machine these
// notes were written on (Apple M3 Pro, no CUDA). The host-side logic of every
// kernel is mirrored and tested in ../cpp.
#pragma once
#include <cuda_runtime.h>

#include <cstdio>
#include <cstdlib>

#define CUDA_CHECK(call)                                                                  \
    do {                                                                                  \
        cudaError_t err_ = (call);                                                        \
        if (err_ != cudaSuccess) {                                                        \
            std::fprintf(stderr, "%s:%d: %s\n", __FILE__, __LINE__, cudaGetErrorString(err_)); \
            std::exit(2);                                                                 \
        }                                                                                 \
    } while (0)

// Launch errors are only reported by the next API call; check explicitly.
#define CUDA_CHECK_LAUNCH() CUDA_CHECK(cudaGetLastError())

static int g_fail = 0;
static void check(bool ok, const char* what) {
    std::printf("  [%s] %s\n", ok ? "ok" : "FAIL", what);
    if (!ok) ++g_fail;
}
static int finish() {
    std::printf(g_fail ? "%d check(s) FAILED\n" : "all checks passed\n", g_fail);
    return g_fail ? 1 : 0;
}

// Elapsed milliseconds of f() on the default stream, timed with events.
template <class F>
float time_ms(F f, int reps = 10) {
    cudaEvent_t a, b;
    CUDA_CHECK(cudaEventCreate(&a));
    CUDA_CHECK(cudaEventCreate(&b));
    f();  // warm-up (first launch pays module load)
    float best = 1e30f;
    for (int r = 0; r < reps; ++r) {
        CUDA_CHECK(cudaEventRecord(a));
        f();
        CUDA_CHECK(cudaEventRecord(b));
        CUDA_CHECK(cudaEventSynchronize(b));
        float ms = 0;
        CUDA_CHECK(cudaEventElapsedTime(&ms, a, b));
        if (ms < best) best = ms;
    }
    CUDA_CHECK(cudaEventDestroy(a));
    CUDA_CHECK(cudaEventDestroy(b));
    return best;
}

static void print_device() {
    int dev = 0;
    cudaDeviceProp p;
    CUDA_CHECK(cudaGetDevice(&dev));
    CUDA_CHECK(cudaGetDeviceProperties(&p, dev));
    std::printf("device %d: %s, cc %d.%d, %d SMs, %.1f GB, smem/block %zu KB, regs/SM %d\n", dev, p.name,
                p.major, p.minor, p.multiProcessorCount, p.totalGlobalMem / 1e9, p.sharedMemPerBlock / 1024,
                p.regsPerMultiprocessor);
}
