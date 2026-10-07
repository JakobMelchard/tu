# C++17 reference implementations for the algorithmics part (see notes A03, A05, A06).
# Targets: all (build into build/), test (run every binary with --test), clean.
CXX      = clang++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
BUILD    := build
SRCS     := dijkstra.cpp kruskal.cpp knapsack.cpp edmonds_karp.cpp
BINS     := $(patsubst %.cpp,$(BUILD)/%,$(SRCS))

.PHONY: all test clean

all: $(BINS)

$(BUILD)/%: %.cpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -o $@ $<

$(BUILD):
	mkdir -p $(BUILD)

test: all
	@fail=0; for b in $(BINS); do \
	  if ./$$b --test; then :; else echo "FAIL: $$b"; fail=1; fi; \
	done; \
	if [ $$fail -eq 0 ]; then echo "SUMMARY: all $(words $(BINS)) C++ self-tests passed"; \
	else echo "SUMMARY: some C++ self-tests FAILED"; exit 1; fi

clean:
	rm -rf $(BUILD)
