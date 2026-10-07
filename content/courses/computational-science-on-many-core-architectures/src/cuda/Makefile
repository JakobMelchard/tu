# 360.252 -- CUDA versions of the CPU reference programs in ../cpp.
# UNTESTED on the machine these notes were written on (Apple M3 Pro, no CUDA).
#   make         build bin/* if nvcc exists, otherwise print SKIP and succeed
#   make test    build and run every program (each checks itself, exit 1 on failure)
#   make syntax  parse + type-check host AND device code with clang's CUDA front end
#                against syntax/cuda_runtime.h (a declarations-only stand-in); no nvcc needed
#   make clean
NVCC     ?= nvcc
ARCH     ?= -arch=sm_70
NVFLAGS  := -O2 -std=c++17 $(ARCH) -fmad=false -Xcompiler -Wall
PROGS    := vector_add reduction scan tiled_matmul stencil
HAVE_NVCC := $(shell command -v $(NVCC) 2>/dev/null)
SKIP_MSG := SKIP: $(NVCC) not found in PATH -- CUDA examples not built. The CPU mirrors in ../cpp are the tested versions; run 'make syntax' for a compile-free check.

.PHONY: all test syntax clean
ifeq ($(HAVE_NVCC),)
all test:
	@echo "$(SKIP_MSG)"
else
all: $(addprefix bin/,$(PROGS))

bin/%: %.cu common.cuh
	@mkdir -p bin
	$(NVCC) $(NVFLAGS) $< -o $@

test: all
	@for p in $(PROGS); do printf '== %s\n' $$p; ./bin/$$p || exit 1; done
	@echo "all CUDA tests passed"
endif

CLANG_CUDA := clang++ -std=c++17 -x cuda -nocudainc -nocudalib -fsyntax-only -Wall -Wextra -Isyntax -include syntax/cuda_runtime.h
syntax:
	@for f in $(addsuffix .cu,$(PROGS)); do \
	  $(CLANG_CUDA) --cuda-host-only $$f && \
	  $(CLANG_CUDA) --cuda-device-only --cuda-gpu-arch=sm_70 $$f && echo "syntax ok  $$f" || exit 1; done

clean:
	rm -rf bin
