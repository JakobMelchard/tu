# 05 Programming models: native (CUDA), annotation-driven (OpenMP, OpenACC), portable (OpenCL, SYCL, HIP)

TISS topic 5: "Programming Models (Annotation-driven such as OpenMP, native
such as CUDA)" [S2]. Host-side OpenMP (`parallel for`, `reduction`, `schedule`,
races, atomics) is NSSC I note 07 [S40] and is not repeated; this note covers
**offload**. Rupp's summary of CUDA: proprietary NVIDIA model since 2007, C++
with extensions, compiler extracts the kernels, vendor libraries (cuBLAS,
cuSPARSE, cuFFT, ...) [S4 `cuda.tex`].

## The one example in every model: $x = y + z$

**CUDA** [S15 §5.1-5.2] (`src/cuda/vector_add.cu`):

```cpp
__global__ void vadd(const double* y, const double* z, double* x, size_t n) {
    for (size_t i = blockIdx.x * size_t(blockDim.x) + threadIdx.x; i < n; i += size_t(gridDim.x) * blockDim.x)
        x[i] = y[i] + z[i];                          // grid-stride loop: any grid covers any n
}
cudaMalloc(&dy, n * 8); cudaMemcpy(dy, hy, n * 8, cudaMemcpyHostToDevice);   // ... dz, dx
vadd<<<blocks, 256>>>(dy, dz, dx, n);                // <<<grid, block, smem bytes, stream>>>
CUDA_CHECK(cudaGetLastError());                      // launch errors surface only here
cudaMemcpy(hx, dx, n * 8, cudaMemcpyDeviceToHost);   // blocks until the kernel is done
```

**OpenMP offload** [S22 §13.8 `target`, §10.2 `teams`, §11.6 `distribute`, §5.8.3 `map`]:

```cpp
#pragma omp target teams distribute parallel for map(to: y[0:n], z[0:n]) map(from: x[0:n])
for (size_t i = 0; i < n; ++i) x[i] = y[i] + z[i];
```
`target`: run on the device; `teams`: "creates a league of teams" [S22] (~ a
grid of blocks); `distribute`: split iterations over teams; `parallel for`:
over the threads of each team. Keep data resident across kernels with
`target data` (§13.5) or `target enter data` / `target exit data` (§13.6-13.7),
refresh with `target update` (§13.9); device functions need `declare target`
(§7.8.1).

**OpenACC** [S23 §2.5.1 `parallel`, §2.5.3 `kernels`, §2.9 `loop`, §2.7 data clauses]:

```cpp
#pragma acc parallel loop gang vector copyin(y[0:n], z[0:n]) copyout(x[0:n])
for (size_t i = 0; i < n; ++i) x[i] = y[i] + z[i];
```
Three levels, gang / worker / vector [S23 §1]. `kernels` lets the compiler
decide what to parallelise; `parallel` asserts it. Data: `#pragma acc data
copyin(...) copy(...)` (§2.6.5), `enter data` / `exit data` (§2.6.6).

**OpenCL** [S24 §3.2 execution model]: a kernel in OpenCL C, compiled at run time:

```c
__kernel void vadd(__global const double* y, __global const double* z, __global double* x, ulong n) {
    size_t i = get_global_id(0);
    if (i < n) x[i] = y[i] + z[i];
}
```
Host: platform, device, context, `clCreateCommandQueueWithProperties`,
`clCreateProgramWithSource` + `clBuildProgram`, `clCreateBuffer`,
`clSetKernelArg`, `clEnqueueNDRangeKernel`, `clEnqueueReadBuffer` [S24]. About
40 lines of boilerplate before the first kernel runs.

**SYCL 2020** [S25] (single-source C++, USM §4.8):

```cpp
sycl::queue q;
double* x = sycl::malloc_device<double>(n, q);      // ... y, z; q.memcpy(...)
q.parallel_for(sycl::range<1>(n), [=](sycl::id<1> i) { x[i] = y[i] + z[i]; }).wait();
```

**HIP** [S26]: CUDA's API with `hip` prefixes (`hipMalloc`, `hipMemcpy`,
`<<<...>>>`), compiled for AMD or NVIDIA; HIPIFY translates CUDA sources.

## Concept map

| concept | CUDA [S15] | OpenCL [S24] | SYCL [S25] | HIP [S26] | OpenMP [S22] | OpenACC [S23] |
|---|---|---|---|---|---|---|
| one lane | thread | work-item | work-item | thread | iteration / thread | vector lane |
| lock-step group | warp (32) | sub-group | sub-group | wavefront (64 CDNA, 32 RDNA) | `simd` | vector |
| cooperating group | thread block | work-group | work-group | block | team | gang |
| whole launch | grid | NDRange | `nd_range` | grid | league of teams | all gangs |
| fast shared scratch | `__shared__` | `__local` | `local_accessor` | `__shared__` | (team-private data) | `cache` directive |
| group barrier | `__syncthreads()` | work-group barrier | `group_barrier` | `__syncthreads()` | `barrier` inside `parallel` | none exposed |
| async queue | stream | command-queue | queue | stream | `nowait` + `depend` | `async(n)` |

The cooperating-group row is the one that matters for algorithms: every
shared-memory tile, tree reduction and block scan of note 04 exists in all six
models under different names.

## Streams and asynchrony (CUDA)

A **stream** is an in-order queue; work in different streams may overlap
[S15 §6.2.8.5]. With pinned host memory (`cudaMallocHost`), `cudaMemcpyAsync`
in stream $k+1$ overlaps the kernel in stream $k$. Pipeline model with $c$
chunks, copy-in $t_i$, kernel $t_k$, copy-out $t_o$ per chunk, copy engines
separate from SMs:
$$T_\text{serial} = c\,(t_i + t_k + t_o), \qquad T_\text{pipelined} \approx (t_i + t_k + t_o) + (c-1)\max(t_i, t_k, t_o).$$
For vector add $t_k \ll t_i$ (PCIe 16-128 GB/s [S4] [S30] vs HBM TB/s), so the
best case hides the kernel, not the copies: $T \to c\,t_i$ plus one
$t_o$ if in- and out-copies share an engine. `vector_add.cu` measures 1 stream
against 4 streams over 16 chunks *(untested here)*.

## Choosing

| | native (CUDA/HIP) | annotation (OpenMP/OpenACC) | portable C++ (SYCL) / C (OpenCL) |
|---|---|---|---|
| control over smem, warps, streams | full | limited (compiler decides) | full |
| code change | rewrite hot loops | pragmas + data regions | rewrite, single source (SYCL) |
| vendors | NVIDIA (HIP: AMD + NVIDIA) | any with compiler support | any with a runtime |
| typical risk | lock-in | silent host fallback, hidden copies | toolchain maturity *(unsourced)* |

Rupp's position for libraries: target several back ends (CUDA, OpenCL,
OpenMP) behind one interface, as ViennaCL does [S4].

## On this Mac

No CUDA, no nvcc; Apple clang has no OpenMP offload target and the GPU speaks
Metal without FP64 [S36]. Everything that runs here is host OpenMP
(`src/cpp`, `-Xpreprocessor -fopenmp -lomp`). The `.cu` files are checked with
clang's CUDA front end against a declarations-only header (`make -C src/cuda
syntax`: host and device side type-check), which catches syntax and type
errors but not a single runtime bug.

## Pitfalls

- Forgetting `cudaGetLastError()` after a launch: errors appear at the next unrelated call.
- `map(tofrom:)` everything on every `target` region: the data moves every time; use data regions.
- OpenMP offload built without a device target silently runs on the host.
- Pageable host memory in `cudaMemcpyAsync`: no overlap.
- Timing with a host clock without synchronising; use events.

## Oral-exam questions

1. **Map CUDA's thread, warp, block, grid onto OpenCL and OpenMP offload.** work-item, sub-group, work-group, NDRange; iteration/thread, simd, team, league of teams.
2. **What does `#pragma omp target teams distribute parallel for` do, word by word?** Offload; create a league of teams; distribute iterations over teams; parallelise each team's share over its threads [S22].
3. **Annotation-driven vs native: when would you choose which?** Pragmas for existing large codes and portability with modest effort; native when you need shared memory, warp-level primitives or stream control.
4. **How do streams make an offloaded computation faster, and what bounds the gain?** Overlap copies and kernels across chunks; bound by the slowest stage, usually the PCIe copies.
5. **Why is a CUDA program not portable to an AMD GPU, and what are the options?** CUDA is NVIDIA-only; HIP (HIPIFY translation), SYCL, OpenCL, OpenMP/OpenACC offload.

Code: `src/cuda/vector_add.cu` (`vadd`, `pipeline`, pinned vs pageable), `src/cuda/Makefile` (`syntax`), `src/cpp/*.cpp` (host OpenMP). Sources: [S4] [S15] [S22]-[S26] [S30] [S36] [S40].
