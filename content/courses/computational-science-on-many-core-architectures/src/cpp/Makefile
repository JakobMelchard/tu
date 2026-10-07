# 360.252 Computational Science on Many-Core Architectures -- CPU reference
# programs (C++17 + OpenMP via Homebrew libomp). Each mirrors the host-side
# logic of a CUDA kernel in ../cuda and IS tested here.
#   make        build everything into bin/
#   make test   run every program with --test (assertions on known results)
#   make bench  run every program with --bench (timing tables, ~1-2 min)
#   make clean  remove bin/
CXX      := clang++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra
LIBOMP   ?= /opt/homebrew/opt/libomp
OMPFLAGS := -Xpreprocessor -fopenmp -I$(LIBOMP)/include
OMPLIBS  := -L$(LIBOMP)/lib -lomp

BIN   := bin
PROGS := stream_triad reduction_scan matmul_tiling stencil_halo spmv_csr_ell atomics_histogram
TARGETS := $(addprefix $(BIN)/,$(PROGS))

.PHONY: all test bench clean
# every program includes omp.h (common.hpp): without libomp skip the suite, like ../cuda
ifeq ($(wildcard $(LIBOMP)/include/omp.h),)
all test bench:
	@echo "SKIP: libomp not found in $(LIBOMP) (brew install libomp) -- CPU mirrors not built"
else
all: $(TARGETS)

$(BIN):
	mkdir -p $(BIN)

$(BIN)/%: %.cpp common.hpp | $(BIN)
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $< -o $@ $(OMPLIBS)

test: all
	@for p in $(PROGS); do printf '== %s\n' $$p; ./$(BIN)/$$p --test || exit 1; done
	@echo "all C++ tests passed"

bench: all
	@for p in $(PROGS); do printf '\n==== %s ====\n' $$p; ./$(BIN)/$$p --bench || exit 1; done
endif

clean:
	rm -rf $(BIN)
