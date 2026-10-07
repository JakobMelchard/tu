# Makefile for the MPI reference programs (ASC-School I, block 3).
#
#   make            build everything with mpicc
#   make test       run every program with mpirun --oversubscribe -np 4
#   make clean      remove binaries
#
# On a cluster: `module load openmpi` (or the site's toolchain), build on the
# login node, then run inside a Slurm job with `srun ./prog` instead of mpirun
# (see ../sh/slurm/vsc5_mpi.sbatch).  Override with e.g. `make test MPIRUN=srun MPIRUN_FLAGS=`.

CC           = mpicc
CFLAGS       = -O2 -Wall -Wextra -std=gnu11
LDLIBS       = -lm
MPIRUN       = mpirun
NP           = 4
# --oversubscribe: allow NP ranks even on a machine with fewer cores
MPIRUN_FLAGS = --oversubscribe

# OpenMP: Apple clang needs Homebrew libomp; GCC/Linux just needs -fopenmp.
UNAME := $(shell uname -s)
ifeq ($(UNAME),Darwin)
  LIBOMP    ?= /opt/homebrew/opt/libomp
  OMP_CFLAGS = -Xpreprocessor -fopenmp -I$(LIBOMP)/include
  OMP_LDLIBS = -L$(LIBOMP)/lib -lomp
else
  OMP_CFLAGS = -fopenmp
  OMP_LDLIBS = -fopenmp
endif

# Every program needs $(CC) and $(MPIRUN): without them skip the suite.
# hybrid_omp_mpi also needs libomp on macOS: without it skip only that one.
HAVE_MPI := $(and $(shell command -v $(CC) 2>/dev/null),$(shell command -v $(MPIRUN) 2>/dev/null))
HAVE_OMP := $(if $(filter Darwin,$(UNAME)),$(wildcard $(LIBOMP)/include/omp.h),yes)
HYBRID   := $(if $(HAVE_OMP),hybrid_omp_mpi)

PROGS = hello_mpi sendrecv deadlock pingpong nonblocking collectives \
        comm_split cart_topology derived_types onesided shmem_onesided mpi_io \
        pi_reduce heat1d_halo $(HYBRID) \
        ../exercises/2025w-mpi/ring_variants

ifeq ($(HAVE_MPI),)
all test:
	@echo "SKIP: $(CC)/$(MPIRUN) not found -- MPI programs not built"
else
all: $(PROGS)
endif

%: %.c
	$(CC) $(CFLAGS) $< -o $@ $(LDLIBS)

hybrid_omp_mpi: hybrid_omp_mpi.c
	$(CC) $(CFLAGS) $(OMP_CFLAGS) $< -o $@ $(LDLIBS) $(OMP_LDLIBS)

RUN = $(MPIRUN) $(MPIRUN_FLAGS) -np $(NP)

ifneq ($(HAVE_MPI),)
test: all
	$(RUN) ./hello_mpi
	$(RUN) ./sendrecv
	$(RUN) ./deadlock
	@echo "--- the next run is EXPECTED to deadlock and be killed by the alarm after 3 s ---"
	! $(RUN) ./deadlock --unsafe recv-first -t 3
	$(RUN) ./pingpong --quick
	$(RUN) ./nonblocking
	$(RUN) ./collectives
	$(RUN) ./comm_split
	$(RUN) ./cart_topology
	$(RUN) ./derived_types
	$(RUN) ./onesided
	$(RUN) ./shmem_onesided
	$(RUN) ./mpi_io
	$(RUN) ../exercises/2025w-mpi/ring_variants
	@echo "--- the ring invariant must hold for odd P too ---"
	$(MPIRUN) $(MPIRUN_FLAGS) -np 3 ../exercises/2025w-mpi/ring_variants
	$(RUN) ./pi_reduce
	$(RUN) ./heat1d_halo
ifneq ($(HYBRID),)
	OMP_NUM_THREADS=2 $(RUN) ./hybrid_omp_mpi
else
	@echo "SKIP hybrid_omp_mpi: libomp not found in $(LIBOMP)"
endif
	@echo "ALL TESTS PASSED"
endif

clean:
	rm -f $(PROGS) hybrid_omp_mpi *.o mpi_io_demo*.bin

.PHONY: all test clean
