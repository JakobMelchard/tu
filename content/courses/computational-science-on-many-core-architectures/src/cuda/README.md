# CUDA versions - UNTESTED

**These five programs have never been compiled with nvcc or run: the machine
these notes were written on (Apple M3 Pro, 2026-09-28) has no CUDA toolkit and
no NVIDIA GPU.** What was checked: `make syntax` parses and type-checks host and
device code of every `.cu` file with clang's CUDA front end against
[`syntax/cuda_runtime.h`](syntax/cuda_runtime.h), a declarations-only stand-in.
That catches syntax and type errors, nothing at run time.

The algorithms are tested through their CPU mirrors in `../cpp`
(table in [`../README.md`](../README.md)). Each `.cu` program checks itself
against a host reference and exits 1 on failure, so the first real run is a
test:

```sh
make            # here: prints SKIP (nvcc not found) and exits 0
make test       # on a CUDA machine: build with nvcc (ARCH=-arch=sm_70 by default) and run all five
make syntax     # anywhere with clang
```
