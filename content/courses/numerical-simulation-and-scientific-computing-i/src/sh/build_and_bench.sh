#!/usr/bin/env bash
# build_and_bench.sh -- build the C++ reference programs, run their --bench modes
# and print a one-screen summary table of the headline numbers for this machine.
#
#   ./build_and_bench.sh            full benchmarks (a few minutes)
#   ./build_and_bench.sh --quick    use the default (demo) modes instead
#
# The full per-program output is kept in $TMPDIR/nssc_bench.log.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
CPP="$HERE/../cpp"
LOG="${TMPDIR:-/tmp}/nssc_bench.log"
MODE="--bench"
[[ "${1:-}" == "--quick" ]] && MODE=""

make -C "$CPP" all >/dev/null
echo "machine: $(sysctl -n machdep.cpu.brand_string), $(sysctl -n hw.ncpu) logical cores"
echo "compiler: $(clang++ --version | head -1)"
: > "$LOG"
for p in cache_bench matmul_opt fd_poisson1d csr rng_mc omp_examples containers_bench; do
    printf '\n==== %s %s ====\n' "$p" "$MODE" >> "$LOG"
    "$CPP/bin/$p" $MODE >> "$LOG" 2>&1
    printf '  ran %s\n' "$p"
done

# Pull the headline numbers out of the log with awk.
echo
printf '%-42s %s\n' "quantity" "value"
printf '%-42s %s\n' "------------------------------------------" "-----"
printf '%-42s %s\n' "triad bandwidth, 1 core" "$(awk -F': *' '/^triad bandwidth/{print $2}' "$LOG")"
printf '%-42s %s\n' "compute peak, 1 core, scalar" "$(awk -F': *' '/^compute peak/{print $2}' "$LOG")"
printf '%-42s %s\n' "DRAM latency (largest working set)" "$(awk '/KB/ && NF==3 {v=$3} END{print v " ns"}' "$LOG")"
printf '%-42s %s\n' "loop order penalty j-i vs i-j" "$(awk -F'ratio ' '/^loop order/{print $2}' "$LOG")"
printf '%-42s %s\n' "matmul naive -> best GFLOP/s (largest n)" "$(awk '/^naive ijk/{a=$4} /^ikj|^blocked/{if($(NF-1)+0>b)b=$(NF-1)+0} END{print a " -> " b}' "$LOG")"
printf '%-42s %s\n' "2D Poisson CG iterations (largest N)" "$(awk '/^CG /{v=$2} END{print v}' "$LOG")"
printf '%-42s %s\n' "OpenMP speedup at most threads" "$(awk '/^ +[0-9]+ +[0-9.]+ +[0-9.]+ +[0-9.]+$/{v=$3"x on "$1" threads"} END{print v}' "$LOG")"
printf '%-42s %s\n' "false sharing slowdown" "$(awk -F'[()]' '/^false sharing/{print $2}' "$LOG")"
printf '%-42s %s\n' "MC error slope (theory -0.5)" "$(awk '/^fitted slope/{print $7}' "$LOG")"
echo
echo "details: $LOG"
