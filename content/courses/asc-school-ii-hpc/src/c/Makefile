# Makefile for the ASC-School II reference programs (see ../README.md).
#
#   make          build everything
#   make test     run every program; each checks its own result, exits non-zero on failure
#   make vecreport  show which loops of simd_dot.c the compiler vectorised
#   make clean    remove binaries and test output
#
# On a cluster: build on the login node after `module load` of a compiler and
# an MPI, then run inside a job with `make test MPIRUN=srun MPIRUN_FLAGS=`.

CC           = mpicc
CC_SERIAL    = cc
CFLAGS       = -O2 -Wall -Wextra -std=gnu11
# Portable by default.  On x86 add -march=native (AVX2/AVX-512 intrinsics path),
# on Apple silicon NEON is baseline and nothing is needed.
ARCHFLAGS    ?=
LDLIBS       = -lm
MPIRUN       = mpirun
NP           = 4
# --oversubscribe: 4 ranks x 2 threads may exceed the cores of a laptop
MPIRUN_FLAGS = --oversubscribe

UNAME := $(shell uname -s)
ifeq ($(UNAME),Darwin)
  LIBOMP     ?= /opt/homebrew/opt/libomp
  OMP_CFLAGS  = -Xpreprocessor -fopenmp -I$(LIBOMP)/include
  OMP_LDLIBS  = -L$(LIBOMP)/lib -lomp
else
  OMP_CFLAGS  = -fopenmp
  OMP_LDLIBS  = -fopenmp
endif

# Missing toolchain pieces skip the programs that need them instead of failing:
# MPI programs need $(CC) and $(MPIRUN); hybrid_pi and affinity_report also libomp on macOS.
HAVE_MPI := $(and $(shell command -v $(CC) 2>/dev/null),$(shell command -v $(MPIRUN) 2>/dev/null))
HAVE_OMP := $(if $(filter Darwin,$(UNAME)),$(wildcard $(LIBOMP)/include/omp.h),yes)
HYBRID   := $(if $(and $(HAVE_MPI),$(HAVE_OMP)),hybrid_pi affinity_report)
MPI_ONLY := $(if $(HAVE_MPI),mpi_io_write_read)
SKIP_HYB := $(if $(HYBRID),,hybrid_pi affinity_report)
SKIP_MPI := $(if $(MPI_ONLY),,mpi_io_write_read)
# `omp simd` needs only the front end, not the runtime
SIMD_CFLAGS = -fopenmp-simd

PROGS = $(HYBRID) simd_dot $(MPI_ONLY)

all: $(PROGS)

hybrid_pi: hybrid_pi.c
	$(CC) $(CFLAGS) $(OMP_CFLAGS) $< -o $@ $(LDLIBS) $(OMP_LDLIBS)

affinity_report: affinity_report.c
	$(CC) $(CFLAGS) $(OMP_CFLAGS) $< -o $@ $(LDLIBS) $(OMP_LDLIBS)

simd_dot: simd_dot.c
	$(CC_SERIAL) $(CFLAGS) $(ARCHFLAGS) $(SIMD_CFLAGS) $< -o $@ $(LDLIBS)

mpi_io_write_read: mpi_io_write_read.c
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

vecreport: simd_dot.c
	$(CC_SERIAL) $(CFLAGS) $(ARCHFLAGS) $(SIMD_CFLAGS) -Rpass=loop-vectorize \
	    -Rpass-missed=loop-vectorize -c $< -o /dev/null 2>&1 | grep -E 'remark' || true

RUN = $(MPIRUN) $(MPIRUN_FLAGS) -np $(NP)

test: all
	@$(if $(SKIP_HYB),echo "SKIP $(SKIP_HYB): need $(CC)/$(MPIRUN)$(if $(filter Darwin,$(UNAME)), and libomp in $(LIBOMP))")
	@$(if $(SKIP_MPI),echo "SKIP $(SKIP_MPI): needs $(CC)/$(MPIRUN)")
ifneq ($(HYBRID),)
	OMP_NUM_THREADS=2 $(RUN) ./hybrid_pi
	@echo "--- same N, different P x T: the result must not depend on the decomposition ---"
	OMP_NUM_THREADS=1 $(MPIRUN) $(MPIRUN_FLAGS) -np 2 ./hybrid_pi
	OMP_NUM_THREADS=3 $(MPIRUN) $(MPIRUN_FLAGS) -np 3 ./hybrid_pi
	OMP_NUM_THREADS=2 OMP_PROC_BIND=close OMP_PLACES=cores $(RUN) ./affinity_report
endif
	./simd_dot --quick
ifneq ($(MPI_ONLY),)
	$(RUN) ./mpi_io_write_read
	@echo "--- odd P: the 2-D decomposition becomes 3x1 ---"
	$(MPIRUN) $(MPIRUN_FLAGS) -np 3 ./mpi_io_write_read
endif
	@echo "ALL TESTS PASSED"

clean:
	rm -f hybrid_pi affinity_report simd_dot mpi_io_write_read *.o io_demo_*.bin

.PHONY: all test clean vecreport
