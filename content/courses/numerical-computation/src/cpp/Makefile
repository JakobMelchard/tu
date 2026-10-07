# C++17 reference implementations for 101.973 Numerical Computation.
#   make        build all programs
#   make test   run each program; every one self-checks against known values
#               (see check.hpp) and exits non-zero on failure
#   make clean  remove binaries (git-ignored, see .gitignore)
# GNU make predefines CXX = c++, so `?=` alone would never pick clang++.
ifeq ($(origin CXX),default)
CXX      := clang++
endif
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

PROGS := lu cg qr fft rk4

.PHONY: all test clean

all: $(PROGS)

%: %.cpp check.hpp
	$(CXX) $(CXXFLAGS) -o $@ $<

test: all
	@status=0; \
	for p in $(PROGS); do \
	  echo "=== $$p"; ./$$p || status=1; \
	done; \
	if [ $$status -eq 0 ]; then echo "ALL C++ TESTS PASSED"; else echo "SOME C++ TESTS FAILED"; fi; \
	exit $$status

clean:
	rm -f $(PROGS)
