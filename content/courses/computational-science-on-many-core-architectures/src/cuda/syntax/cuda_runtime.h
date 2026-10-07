// NOT CUDA. A minimal stand-in for <cuda_runtime.h> so that clang's CUDA front
// end (`clang++ -x cuda --cuda-host-only -fsyntax-only`) can parse and
// type-check the .cu files on a machine without the CUDA toolkit (`make syntax`).
// Declarations only; nothing here links or runs. Signatures follow the CUDA
// Runtime API as used in this directory; anything not used is omitted.
#pragma once
#include <cstddef>

#define __host__ __attribute__((host))
#define __device__ __attribute__((device))
#define __global__ __attribute__((global))
#define __shared__ __attribute__((shared))
#define __constant__ __attribute__((constant))
#include <__clang_cuda_builtin_vars.h>

struct dim3 {
    unsigned x, y, z;
    __host__ __device__ constexpr dim3(unsigned x_ = 1, unsigned y_ = 1, unsigned z_ = 1) : x(x_), y(y_), z(z_) {}
};
typedef int cudaError_t;
enum : int { cudaSuccess = 0 };
typedef struct CUstream_st* cudaStream_t;
typedef struct CUevent_st* cudaEvent_t;
enum cudaMemcpyKind { cudaMemcpyHostToHost, cudaMemcpyHostToDevice, cudaMemcpyDeviceToHost, cudaMemcpyDeviceToDevice };
enum cudaDeviceAttr { cudaDevAttrMultiProcessorCount = 16 };
struct cudaDeviceProp {
    char name[256];
    int major, minor, multiProcessorCount, regsPerMultiprocessor;
    size_t totalGlobalMem, sharedMemPerBlock;
};

extern "C" {
cudaError_t cudaMalloc(void**, size_t);
cudaError_t cudaMallocHost(void**, size_t);
cudaError_t cudaFree(void*);
cudaError_t cudaFreeHost(void*);
cudaError_t cudaMemcpy(void*, const void*, size_t, cudaMemcpyKind);
cudaError_t cudaMemcpyAsync(void*, const void*, size_t, cudaMemcpyKind, cudaStream_t);
cudaError_t cudaMemset(void*, int, size_t);
cudaError_t cudaDeviceSynchronize();
cudaError_t cudaGetLastError();
const char* cudaGetErrorString(cudaError_t);
cudaError_t cudaGetDevice(int*);
cudaError_t cudaGetDeviceProperties(cudaDeviceProp*, int);
cudaError_t cudaDeviceGetAttribute(int*, cudaDeviceAttr, int);
cudaError_t cudaStreamCreate(cudaStream_t*);
cudaError_t cudaStreamDestroy(cudaStream_t);
cudaError_t cudaEventCreate(cudaEvent_t*);
cudaError_t cudaEventDestroy(cudaEvent_t);
cudaError_t cudaEventRecord(cudaEvent_t, cudaStream_t = 0);
cudaError_t cudaEventSynchronize(cudaEvent_t);
cudaError_t cudaEventElapsedTime(float*, cudaEvent_t, cudaEvent_t);
unsigned __cudaPushCallConfiguration(dim3, dim3, size_t = 0, cudaStream_t = 0);
cudaError_t cudaConfigureCall(dim3, dim3, size_t = 0, cudaStream_t = 0);  // what clang expects without a CUDA version
cudaError_t cudaLaunchKernel(const void*, dim3, dim3, void**, size_t, cudaStream_t);
}
template <class T> cudaError_t cudaMalloc(T** p, size_t n) { return cudaMalloc((void**)p, n); }
template <class T> cudaError_t cudaMallocHost(T** p, size_t n) { return cudaMallocHost((void**)p, n); }

__device__ void __syncthreads();
__device__ double atomicAdd(double*, double);
__device__ int atomicAdd(int*, int);
__device__ double __shfl_down_sync(unsigned, double, unsigned, int = 32);
