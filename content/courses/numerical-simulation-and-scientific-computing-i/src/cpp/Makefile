# 360.242 NSSC I -- reference implementations (C++17, clang++, Homebrew libomp)
#   make        build everything into bin/
#   make test   run every program with --test (assertions on known results)
#   make bench  run the benchmark modes and print timing tables
#   make cmake  same build through CMake + ctest (note 10)
#   make clean  remove bin/, build/ and generated .vtk files
CXX      := clang++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra
LIBOMP   ?= /opt/homebrew/opt/libomp
OMPFLAGS := -Xpreprocessor -fopenmp -I$(LIBOMP)/include
OMPLIBS  := -L$(LIBOMP)/lib -lomp

BIN   := bin
PROGS := cache_bench matmul_opt fd_poisson1d heat2d csr rng_mc omp_examples threads_cpp containers_bench vtk_writer
BENCH := cache_bench matmul_opt csr rng_mc omp_examples threads_cpp containers_bench
# without libomp, omp_examples is skipped instead of failing the whole suite
ifeq ($(wildcard $(LIBOMP)/include/omp.h),)
  SKIP  := omp_examples
  PROGS := $(filter-out $(SKIP),$(PROGS))
  BENCH := $(filter-out $(SKIP),$(BENCH))
endif
TARGETS := $(addprefix $(BIN)/,$(PROGS))

.PHONY: all test bench cmake clean
all: $(TARGETS)

$(BIN):
	mkdir -p $(BIN)

# explicit rule wins over the pattern rule: only this program needs OpenMP
$(BIN)/omp_examples: omp_examples.cpp | $(BIN)
	$(CXX) $(CXXFLAGS) $(OMPFLAGS) $< -o $@ $(OMPLIBS)

$(BIN)/%: %.cpp | $(BIN)
	$(CXX) $(CXXFLAGS) $< -o $@

test: all
	@$(if $(SKIP),echo "SKIP $(SKIP): libomp not found in $(LIBOMP) (brew install libomp)")
	@for p in $(PROGS); do printf '== %s\n' $$p; ./$(BIN)/$$p --test || exit 1; done
	@echo "all C++ tests passed"

bench: all
	@for p in $(BENCH); do printf '\n==== %s ====\n' $$p; ./$(BIN)/$$p --bench; done

# The same build via CMake (note 10). Needs cmake >= 3.20; `brew install cmake`.
cmake:
	cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build -j
	ctest --test-dir build --output-on-failure

clean:
	rm -rf $(BIN) build *.vtk
