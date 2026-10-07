# Reference programs for 185.190 Efficient Programs (C11, no dependencies).
#
#   make            build everything
#   make test       every program with --test; exit code != 0 on any failure
#   make bench      the timing runs the notes quote (about 10 s on an M3 Pro)
#   make gcov       line-level execution counts for profile_demo (works with
#                   clang on macOS and gcc on Linux)
#   make gprof      function-level profile (Linux/gcc only: Apple clang
#                   accepts -pg but writes no gmon.out)
#   make perf       perf stat / record / annotate on profile_demo (Linux only)
#   make clean
#
# Portable flags on purpose: no -march=native, no intrinsics, so the same
# source builds on Apple Silicon (clang) and on g0 (Rocket Lake, gcc).
# Override with e.g.  make CC=gcc CFLAGS='-O3 -march=native -std=c11 -Wall -Wextra'

CC     ?= cc
CFLAGS ?= -O2 -std=c11 -Wall -Wextra
LDLIBS  = -lm

PROGS = matmul_steps pointer_chase tsp_greedy branch_predict recurrence profile_demo

all: $(PROGS)

%: %.c util.h
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

test: all
	./matmul_steps --test
	./pointer_chase --test
	./tsp_greedy --test
	./branch_predict --test
	./recurrence --test
	./profile_demo --test
	@echo "ALL TESTS PASSED"

bench: all
	@echo "host: $$(uname -srm)"; ./matmul_steps --bench
	./pointer_chase --sweep
	./tsp_greedy --bench
	./branch_predict --bench
	./recurrence --bench
	./profile_demo --bench

# two-step compile so the .gcno/.gcda names match the source (gcov profile_demo.c)
gcov: profile_demo.c util.h
	$(CC) $(CFLAGS) --coverage -c profile_demo.c -o profile_demo_cov.o
	$(CC) --coverage profile_demo_cov.o -o profile_demo_cov $(LDLIBS)
	rm -f profile_demo_cov.gcda
	./profile_demo_cov >/dev/null
	gcov -o profile_demo_cov.o profile_demo.c
	@echo "--- most executed lines:"; grep -v -- '-:' profile_demo.c.gcov | sort -t: -k1,1 -rn | head -8

gprof: profile_demo.c util.h
	$(CC) $(CFLAGS) -pg profile_demo.c -o profile_demo_pg $(LDLIBS)
	./profile_demo_pg >/dev/null
	gprof -b profile_demo_pg | head -40

perf: profile_demo
	perf stat -e cycles:u -e instructions:u -e branch-misses:u -e L1-dcache-load-misses:u ./profile_demo
	perf record -e cycles:u -o perf.data ./profile_demo >/dev/null
	perf report -i perf.data --stdio | head -30

clean:
	rm -f $(PROGS) profile_demo_cov profile_demo_pg *.o *.gcno *.gcda *.gcov gmon.out perf.data*

.PHONY: all test bench gcov gprof perf clean
