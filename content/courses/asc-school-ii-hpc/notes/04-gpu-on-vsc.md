# 04 GPU programming on the ASC systems

Prepares for *CUDA 4 Dummies* (2 days), the *N-Ways to GPU Programming
Bootcamp* (1.5 days: CUDA, OpenACC, OpenMP offload, standard-language
parallelism, Nsight Systems) and the *Multi-GPU Programming Bootcamp*
(1.5 days, needs CUDA and MPI) [S4]. The GPU programming model itself is the
subject of *Computational Science on Many-Core Architectures* [S11]; here: the three programming routes side by side, and how to get a
GPU job right on VSC-5 and MUSICA. Nothing here was run: the laptop has no
NVIDIA GPU.

## Definitions

- **Host / device**: CPU with its memory / GPU with its own memory (HBM or
  GDDR). Data moves over PCIe or NVLink unless memory is managed/unified.
- **Kernel**: function executed by many GPU threads. **Grid** of **blocks**
  of **threads**; a block runs on one **streaming multiprocessor (SM)**;
  threads execute in **warps** of 32 in lock-step [S20].
- **Shared memory**: per-block scratchpad on the SM; **global memory**: device
  memory visible to all blocks.
- **Occupancy**: resident warps per SM / maximum; latency is hidden by
  switching warps, so enough independent work per SM is needed.
- **Three routes** [S4] [S20] [S16]:
  CUDA (explicit kernels and copies), OpenACC (`#pragma acc`), OpenMP offload
  (`#pragma omp target`). OpenACC and OpenMP leave the kernel generation to
  the compiler.

## The hardware and its Slurm names

| system | partition = QoS | GPUs per node | per-GPU facts | `--gres` |
|---|---|---|---|---|
| VSC-5 | `zen3_0512_a100x2` | 2x A100 PCIe 40 GB, CC 8.0, 108 SMs | FP64 ~10 TF, ~1.6 TB/s | `gpu:1` or `gpu:2`; >1 node only with both [S12] |
| VSC-5 | `zen2_0256_a40x2` | 2x A40 48 GB, CC 8.6, 84 SMs | FP32 strong, FP64 ~0.6 TF | same [S12] |
| MUSICA | `zen4_0768_h100x4` | 4x H100 SXM5 94 GB, NVLink (`NV6`) | GPUs on NUMA 2, 3, 4, 6 | `gpu:1`...`gpu:4` [S13] [S14] |
| MUSICA | `zen5_2304_b200x8` | 8x B200 | private (ISTA), partly available | [S13] |

FP64/bandwidth numbers from the ASC slides as recorded in the sibling register
[S11]; SM counts and compute capabilities from ASC's `deviceQuery` output
[S12]. Ridge points $I^* = P/B$: A100 FP64 $\approx 10^4/1600 \approx 6$
flop/byte; A40 FP64 $\approx 578/696 \approx 0.8$. The A40 is a single-precision
card: a double-precision code belongs on the A100 or H100 [S11].

## Worked example: one kernel, three routes

$y \leftarrow a x + y$ (saxpy/daxpy), $n$ doubles, data already on the device:

```c
/* CUDA */
__global__ void daxpy(int n, double a, const double *x, double *y) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = a * x[i] + y[i];
}
daxpy<<<(n + 255) / 256, 256>>>(n, a, d_x, d_y);   /* grid of ceil(n/256) blocks */

/* OpenACC */
#pragma acc parallel loop present(x[0:n], y[0:n])
for (int i = 0; i < n; i++) y[i] = a * x[i] + y[i];

/* OpenMP offload */
#pragma omp target teams distribute parallel for map(to: x[0:n]) map(tofrom: y[0:n])
for (int i = 0; i < n; i++) y[i] = a * x[i] + y[i];
```

Build lines (compiler names as in the NVIDIA HPC SDK and CUDA toolkit;
module names on ASC not checked):

```bash
nvcc -O3 -arch=sm_80 daxpy.cu -o daxpy_cuda          # A100 = CC 8.0 [S12]
nvc  -O3 -acc -gpu=cc80 -Minfo=accel daxpy.c         # OpenACC, prints what was offloaded
nvc  -O3 -mp=gpu -gpu=cc80 -Minfo=mp daxpy.c         # OpenMP offload
nsys profile -o daxpy_report ./daxpy_cuda            # timeline: kernels vs copies
```

daxpy moves 24 bytes per 2 flops, $I = 1/12$: on every GPU it is
bandwidth-bound, and **if $x, y$ are copied over PCIe for each call** the copy
(~tens of GB/s, unsourced) dominates by 1-2 orders of magnitude over the
kernel (~1.6 TB/s). The first rule of offloading: keep data resident
(`acc data`, `omp target data`, `cudaMalloc` once).

## Worked example: a correct GPU job

[`../src/sh/slurm_templates/gpu.sbatch`](../src/sh/slurm_templates/gpu.sbatch)
takes one MUSICA node, 4 ranks, one H100 each, 22 cores per rank on the
GPU's NUMA domain, in the form of ASC's own vanilla example [S13] [S14]. Inside
the program each rank picks its GPU from its **node-local** rank:

```c
MPI_Comm node;  int local, ndev;
MPI_Comm_split_type(MPI_COMM_WORLD, MPI_COMM_TYPE_SHARED, 0, MPI_INFO_NULL, &node);
MPI_Comm_rank(node, &local);
cudaGetDeviceCount(&ndev);
cudaSetDevice(local % ndev);
```

If `srun` already binds one GPU per task, each rank sees `ndev = 1` and the
modulo still works. ASC notes that `srun` pins tasks to the NUMA domains
attached to the job's GPUs and that some codes need `--gpu-bind=none` [S13].
With a CUDA-aware MPI, device pointers can be passed to `MPI_Send` directly
(topic of the Multi-GPU bootcamp [S4]); otherwise stage through host memory.

## Pitfalls

- No `--gres`: ASC requires it for GPU jobs [S12] [S13]; without it the job
  gets no GPU even on a GPU partition (on sites that confine devices by cgroup,
  `nvidia-smi` then lists none: unsourced for ASC).
- VSC-5: asking for 2 nodes with `--gres=gpu:1` is not allowed [S12].
- Using the A40 for FP64: ~17x slower than the A100 in double [S11].
- Four ranks all on GPU 0 (no device selection): three GPUs idle, one
  oversubscribed.
- Timing a kernel without `cudaDeviceSynchronize()`: launches are
  asynchronous; you time the launch.
- Architecture mismatch: code built for `sm_90` does not run on an A100
  (CC 8.0); build PTX for the lowest target or one binary per partition.

## Questions (ours)

1. *Launch configuration for $n = 10^6$ with 256 threads per block?*
   $\lceil 10^6/256 \rceil = 3907$ blocks; the guard `if (i < n)` handles the
   last partial block.
2. *Why is daxpy a bad showcase for GPU speed-up if data start on the host?*
   Copying $2n$ doubles in and $n$ out over PCIe costs far more than the
   bandwidth-bound kernel; only resident data pays off.
3. *OpenACC or CUDA for porting a large legacy Fortran code in a week?*
   Directives (OpenACC or OpenMP offload): incremental, one loop at a time,
   CPU build unchanged. CUDA when the last factor matters and the kernel is
   small.
4. *A job on `zen4_0768_h100x4` with 4 ranks runs at quarter speed; `nvidia-smi`
   shows one busy GPU. Fix?* Select the device by node-local rank (above) or
   bind one GPU per task via Slurm.
5. *Which VSC-5 GPU for a single-precision molecular-dynamics code, and why?*
   The A40: roughly twice the FP32 throughput of the A100 per the ASC slides
   [S11], and FP64 is not needed.

## Code

- [`../src/sh/slurm_templates/gpu.sbatch`](../src/sh/slurm_templates/gpu.sbatch)
  (syntax-checked by `../src/sh/test_slurm_templates.sh`). No GPU code: none can
  be tested offline on this machine.
- CUDA/OpenCL implementations belong to the Many-Core course folder when it
  gets notes [S11].
