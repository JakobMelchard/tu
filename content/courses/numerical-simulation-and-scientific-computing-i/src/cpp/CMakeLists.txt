# 360.242 NSSC I -- CMake build, the alternative to the hand-written Makefile.
#
# This file is the worked example for note 10. It was written with CMake
# installed and every line of it was executed; see ../../notes/CHANGELOG.md for
# the two defects that exposed in the note's original snippet. Verified with
# CMake 4.4.3 and AppleClang 21.0.0 on arm64-apple-darwin25.6.0; re-run on
# 2026-09-27 (OpenMP 5.1 found via OpenMP_ROOT, ctest 10/10).
#
#   cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
#   cmake --build build -j
#   ctest --test-dir build --output-on-failure
#
# Reference: the CMake documentation [S36], https://cmake.org/cmake/help/latest/

cmake_minimum_required(VERSION 3.20)
project(nssc1 LANGUAGES CXX
        DESCRIPTION "Reference implementations for 360.242 NSSC I")

set(CMAKE_CXX_STANDARD 17)
# Without this, CMAKE_CXX_STANDARD is a *request*: CMake silently falls back to
# whatever the compiler supports instead of failing. Always pair the two.
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

add_compile_options(-Wall -Wextra)

# ---------------------------------------------------------------------------
# OpenMP.
#
# `find_package(OpenMP REQUIRED)` on its own FAILS with Apple's clang: Xcode's
# compiler does not ship libomp and FindOpenMP does not look inside a Homebrew
# keg. Point it at the keg with OpenMP_ROOT, which FindOpenMP honours through
# CMake's <PackageName>_ROOT search rule [S36]. On Linux with gcc or with a
# Homebrew llvm this block is a no-op.
# ---------------------------------------------------------------------------
if(APPLE)
    execute_process(COMMAND brew --prefix libomp
                    OUTPUT_VARIABLE BREW_LIBOMP
                    OUTPUT_STRIP_TRAILING_WHITESPACE
                    ERROR_QUIET)
    if(BREW_LIBOMP AND IS_DIRECTORY "${BREW_LIBOMP}")
        set(OpenMP_ROOT "${BREW_LIBOMP}")
    endif()
endif()
find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    message(STATUS "OpenMP ${OpenMP_CXX_VERSION} via ${OpenMP_CXX_FLAGS}")
else()
    message(WARNING "OpenMP not found: skipping omp_examples. On macOS run "
                    "`brew install libomp`.")
endif()

find_package(Threads REQUIRED)

# ---------------------------------------------------------------------------
# Programs. Each one runs as a demo, as `--test` and (some) as `--bench`.
# ---------------------------------------------------------------------------
set(PROGRAMS
    cache_bench
    matmul_opt
    fd_poisson1d
    heat2d
    csr
    rng_mc
    containers_bench
    vtk_writer
    threads_cpp)

foreach(prog IN LISTS PROGRAMS)
    add_executable(${prog} ${prog}.cpp)
    target_sources(${prog} PRIVATE common.hpp)
endforeach()

target_link_libraries(threads_cpp PRIVATE Threads::Threads)

if(OpenMP_CXX_FOUND)
    add_executable(omp_examples omp_examples.cpp)
    target_link_libraries(omp_examples PRIVATE OpenMP::OpenMP_CXX)
    list(APPEND PROGRAMS omp_examples)
endif()

# ---------------------------------------------------------------------------
# Tests. `add_test(COMMAND <target>)` resolves the target to its built binary,
# so no path is needed. vtk_writer writes files, so give it its own directory.
# ---------------------------------------------------------------------------
enable_testing()
foreach(prog IN LISTS PROGRAMS)
    add_test(NAME ${prog} COMMAND ${prog} --test)
endforeach()

set_tests_properties(vtk_writer PROPERTIES
                     WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")
if(TARGET omp_examples)
    # the scaling table is timing-sensitive; give it room on a loaded machine
    set_tests_properties(omp_examples PROPERTIES TIMEOUT 120)
endif()
