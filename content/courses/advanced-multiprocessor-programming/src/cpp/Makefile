# 191.022 AMP -- reference implementations (C++17, std::thread, std::atomic)
#   make        build everything into bin/
#   make test   run every program with --test (invariants, linearisability, ~5 s)
#   make bench  run the --bench modes and print timing tables (~1 min)
#   make tsan   rebuild with -fsanitize=thread into bin-tsan/ and run every --test
#   make clean  remove bin/ and bin-tsan/
CXX      := clang++
CXXFLAGS := -std=c++17 -O2 -Wall -Wextra -pthread
TSANFLAGS := -std=c++17 -O1 -g -Wall -Wextra -pthread -fsanitize=thread

PROGS := peterson_filter memory_model spinlocks lists treiber_stack ms_queue striped_hashset work_stealing hazard_pointers
TARGETS := $(addprefix bin/,$(PROGS))
TSAN_TARGETS := $(addprefix bin-tsan/,$(PROGS))

.PHONY: all test bench tsan clean
all: $(TARGETS)

bin bin-tsan:
	mkdir -p $@

bin/%: %.cpp common.hpp | bin
	$(CXX) $(CXXFLAGS) $< -o $@

bin-tsan/%: %.cpp common.hpp | bin-tsan
	$(CXX) $(TSANFLAGS) $< -o $@

test: all
	@for p in $(PROGS); do printf "== %s\n" $$p; ./bin/$$p --test || exit 1; done
	@echo "all C++ tests passed"

bench: all
	@for p in $(PROGS); do printf "\n==== %s ====\n" $$p; ./bin/$$p --bench || exit 1; done

# halt_on_error: any reported race fails the target. Sizes shrink by kScale (common.hpp).
tsan: $(TSAN_TARGETS)
	@for p in $(PROGS); do printf "== tsan %s\n" $$p; TSAN_OPTIONS=halt_on_error=1 ./bin-tsan/$$p --test || exit 1; done
	@echo "all C++ tests passed under ThreadSanitizer"

clean:
	rm -rf bin bin-tsan
