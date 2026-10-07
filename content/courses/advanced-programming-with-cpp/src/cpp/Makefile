# 360.251 Advanced Programming with C++ -- reference programs (C++23, Apple clang 21)
#   make          probe the toolchain, then build every program into bin/
#   make test     run every program's self-checks, the compile-fail suite and the matrix hand-in
#   make features print the C++23 feature table measured by probe.sh
#   make sanitize the same tests built with ASan + UBSan into bin-asan/
#   make tsan     concurrency.cpp built with ThreadSanitizer
#   make cmake    build + ctest the matrix hand-in through CMake (ASan/UBSan on)
#   make clean    remove bin/ and build/
# Feature guards: probe.sh compiles, links and runs probes/*.cpp once and writes
# bin/features.flags (-DHAVE_X=1 per working feature). Every program is compiled with
# those flags and #if-guards what is missing, printing SKIP instead of failing.
# A program that needs a missing feature as a whole (modules/) is skipped with a message.
CXX      := clang++
STD      := -std=c++23
CXXFLAGS := $(STD) -O2 -Wall -Wextra
BIN      := bin

PROGS   := basics deduction lifetime pointers value_categories conversions lambdas \
           operators classes smart_pointers ranges constexpr concepts concurrency features
EXTRA   := matrix modules
FEATS    = $(shell cat $(BIN)/features.flags 2>/dev/null)
EXPFLAGS = $(shell cat $(BIN)/experimental.flags 2>/dev/null)
MODFLAGS = $(shell cat $(BIN)/modules.flags 2>/dev/null)

.PHONY: all test features sanitize tsan cmake clean
all: $(addprefix $(BIN)/,$(PROGS) $(EXTRA))

$(BIN)/features.flags: probe.sh $(wildcard probes/*)
	@mkdir -p $(BIN)
	@echo "probing $(CXX) $(STD) (probes/*.cpp) ..."
	@./probe.sh $(BIN) $(CXX) $(CXXFLAGS) > /dev/null

# basics: two translation units, linked (note 01)
$(BIN)/basics: basics_main.cpp basics_other.cpp basics.hpp check.hpp $(BIN)/features.flags
	$(CXX) $(CXXFLAGS) $(FEATS) basics_main.cpp basics_other.cpp -o $@

# concurrency: the parallel algorithms need libc++'s experimental library
$(BIN)/concurrency: concurrency.cpp check.hpp $(BIN)/features.flags
	$(CXX) $(CXXFLAGS) $(FEATS) $(EXPFLAGS) $< -o $@

# the library hand-in (header-only, tests in matrix/tests)
$(BIN)/matrix: matrix/tests/test_matrix.cpp matrix/include/la/matrix.hpp check.hpp $(BIN)/features.flags
	$(CXX) $(CXXFLAGS) $(FEATS) -Imatrix/include -I. $< -o $@

# named modules: interface -> .pcm -> object, then the importer; skipped if unsupported.
# The .pcm must be built with the importer's flags (a sanitizer mismatch is a hard error).
$(BIN)/modules: modules/geometry.cppm modules/modules_main.cpp check.hpp $(BIN)/features.flags
	@if grep -q HAVE_MODULES $(BIN)/features.flags; then \
	  echo "$(CXX) $(CXXFLAGS) $(MODFLAGS) --precompile modules/geometry.cppm ..."; \
	  $(CXX) $(CXXFLAGS) $(MODFLAGS) -x c++-module --precompile modules/geometry.cppm -o $(BIN)/geometry.pcm && \
	  $(CXX) $(CXXFLAGS) $(MODFLAGS) -c $(BIN)/geometry.pcm -o $(BIN)/geometry.o && \
	  $(CXX) $(CXXFLAGS) $(MODFLAGS) -fmodule-file=geometry=$(BIN)/geometry.pcm -c modules/modules_main.cpp -o $(BIN)/modules_main.o && \
	  $(CXX) $(CXXFLAGS) $(BIN)/modules_main.o $(BIN)/geometry.o -o $@; \
	else echo "SKIP modules: $(CXX) cannot precompile a named module interface (see bin/features.txt)"; fi

$(BIN)/%: %.cpp check.hpp $(BIN)/features.flags
	$(CXX) $(CXXFLAGS) $(FEATS) $< -o $@

test: all
	@fail=0; for p in $(PROGS) $(EXTRA); do \
	  if [ -x $(BIN)/$$p ]; then ./$(BIN)/$$p || fail=1; \
	  else echo "$$p: SKIPPED (not built, see above)"; fi; done; \
	compile_fail/check.sh $(CXX) $(STD) $(FEATS) -I$(CURDIR)/matrix/include -I$(CURDIR) || fail=1; \
	if [ $$fail -eq 0 ]; then echo "all C++ tests passed"; else echo "SOME C++ TESTS FAILED"; exit 1; fi

features: $(BIN)/features.flags $(BIN)/features
	@echo "== probes (compile + link + run), $(CXX) $(STD):"; cat $(BIN)/features.txt
	@echo "== language macros and exercised features:"; ./$(BIN)/features

sanitize:
	$(MAKE) BIN=bin-asan CXXFLAGS="$(STD) -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -Wall -Wextra" test

tsan: $(BIN)/features.flags
	$(CXX) $(STD) -O1 -g -fsanitize=thread $(FEATS) $(EXPFLAGS) concurrency.cpp -o $(BIN)/concurrency-tsan
	./$(BIN)/concurrency-tsan

cmake:
	cmake -S matrix -B build -DCMAKE_BUILD_TYPE=Release -DLA_SANITIZE=ON
	cmake --build build
	ctest --test-dir build --output-on-failure

clean:
	rm -rf bin bin-asan build
