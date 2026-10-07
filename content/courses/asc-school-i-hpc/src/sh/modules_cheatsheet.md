# Environment Modules on the ASC systems — cheatsheet

> The ASC systems run **Tcl Environment Modules**, not Lmod. There is no
> `module spider`, no `ml`, no `(D)` default marker, no hierarchy, and no
> `module save`. Sources and the full argument in
> [`../../notes/05-module-environment.md`](../../notes/05-module-environment.md).

Modules add or remove software from your environment by editing `PATH`,
`CPATH`, `LIBRARY_PATH`, `LD_LIBRARY_PATH`, `MANPATH` and friends, per shell
session. Nothing is installed; the software is already under
`/gpfs/opt/sw/<env>/spack-<version>/…` and the module points at one build of it.

## Commands, as ASC documents them [S10] [S19]

| Command | What |
|---|---|
| `module --help` | general help |
| `module avail` | everything loadable — the tree is **flat**, so this is everything |
| `module avail openmpi` | filter by name; names are **case sensitive** (`Matlab`, `Mathematica`) |
| `module avail -t \| grep -i mpi` | terse output, greppable — this is the substitute for `module spider` |
| `module load <full name>` | load (synonym `module add`) |
| `module load --auto <name>` | also load the dependencies |
| `module list` / `module list -t` | what is loaded (flushed at logout) |
| `module show <name>` | the modulefile: the paths it prepends. No need to load it first. |
| `module rm <name>` / `module unload <name>` | remove |
| `module purge` | remove everything — first line of every job script |

`export MODULES_AUTO_HANDLING=1` in `~/.bashrc` makes `--auto` the default
(`=0` disables it) [S10] [S19]. But see the warning about `.bashrc` below.

## The names are long and there is no default

```
skylake$ module load openmpi/4.1.4-gcc-12.2.0-xt53foa      # works
skylake$ module load openmpi/4.1.4
ERROR: Unable to locate a modulefile for 'openmpi/4.1.4'
```

*"Always state the whole line."* [S10] [S19] The upside: a job script cannot
silently pick up a different compiler next month.

The Spack hash differs per CPU architecture, so **the same package has a
different name on each cluster**:

```
skylake$   module load python/3.11.3-gcc-12.2.0-rtzvjko
zen$       module load python/3.11.3-gcc-12.2.0-hn7p65z
cuda-zen$  module load python/3.9.15-gcc-12.2.0-dnctq7y
```

`skylake` / `zen` / `cuda-zen` is the **software environment**, and its name is
the first field of the ASC prompt (`zen trainee00@l55:~$`) [S7] [S10].

## Dependencies

```
zen$ module load py-numpy/1.24.3-gcc-12.2.0-muackhh
Loading py-numpy/1.24.3-gcc-12.2.0-muackhh
  Loading requirement: netlib-lapack/3.10.1-gcc-12.2.0-4qrxbdw
      python/3.9.15-gcc-12.2.0-my6jxu2
      py-setuptools/63.0.0-gcc-12.2.0-jru4czh
```

## Compilers and MPI wrappers

Shapes from the ASC compiling deck, which ASC itself marks **OUTDATED** — the
version strings and hashes in it are from Spack 0.19 and will not resolve today.
Re-run `module avail` for the current names [S8] [S10].

| language | Intel | GNU | AOCC |
|---|---|---|---|
| C | `icx` | `gcc` | `clang` |
| C++ | `icpx` | `g++` | `clang++` |
| Fortran | `ifx` | `gfortran` | `flang` |

| | Intel oneAPI | Intel classic | Open MPI |
|---|---|---|---|
| MPI module | `intel-oneapi-mpi` | `intel-oneapi-mpi` | `openmpi` |
| compiler module | `compiler/latest` | `intel/19` | any |
| C | `mpiicc` | `mpicc` / `mpigcc` | `mpicc` |
| C++ | `mpiicpc` | `mpicxx` / `mpigxx` | `mpic++` / `mpicxx` |
| Fortran | `mpiifort` | `mpifc` / `mpiifort` | `mpifort` |

ASC's own recommendation: **intel** compilers are usually fastest on `skylake`,
**aocc** on `zen`; `aocc` does not work with CUDA, so use `gcc` on `cuda-zen`
[S10].

Architecture flags [S10]:

```bash
module purge
module load gcc/<version>-<...>-<hash>
gcc -O2 -march=skylake  prog.c   # VSC-4
gcc -O2 -march=znver3   prog.c   # VSC-5 CPU nodes and the A100 GPU nodes
gcc -O2 -march=znver2   prog.c   # the A40 GPU nodes - the ONLY Zen2 on VSC-5
icx -O3 -xHost          prog.c   # Intel
```

MPI:

```bash
module purge
module load compiler/latest
module load intel-oneapi-mpi/<version>-<...>-<hash>
mpiicc -O3 -xHost hello-mpi.c -o hello-mpi
mpiicc -show                     # what the wrapper really runs
mpirun -np 2 ./hello-mpi         # on a login node: 2 ranks only, and briefly
```

Finding an MPI at all:

```bash
module avail -t | grep mpi       # all of them
module avail openmpi             # one flavour
spack find -l mpi                # the package manager's view; usually the same
```

## Pitfalls

- Copying a `module load` line out of a slide deck or an old script: the hash is
  gone. Re-run `module avail`.
- Loading modules in `~/.bashrc`. The ASC documentation calls customising
  `.bashrc` a cause of failing jobs and recommends against it outright [S19].
  Load in the job script, after `module purge`.
- Building on a `zen` login node and running on `zen2_0256_a40x2`
  (`-march=znver3` against Zen2 hardware) [S10].
- Mixing a `gcc`-built library with an `intel`-built MPI. The module names make
  the toolchain visible — use that.
- Reaching for `module spider`, `ml` or `module save`. Lmod commands; not here.

Source entries `S7`–`S19` are in
[`../../refs/SOURCES.md`](../../refs/SOURCES.md).
