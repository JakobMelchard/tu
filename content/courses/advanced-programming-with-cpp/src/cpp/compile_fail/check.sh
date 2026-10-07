#!/usr/bin/env bash
# Every file here must be REJECTED by the compiler, with an error matching its
# "// expect:" line. A file that compiles, or fails for another reason, is a test failure.
#   usage: check.sh <cxx> <flags...>
set -uo pipefail
cd "$(dirname "$0")"
cxx=$1; shift
fail=0; n=0
for f in *.cpp; do
    n=$((n + 1))
    want=$(sed -n 's|^// expect: ||p' "$f" | head -1)
    if err=$("$cxx" "$@" -fsyntax-only "$f" 2>&1); then
        echo "  FAIL $f compiled, but must not"; fail=$((fail + 1))
    elif ! grep -q -- "$want" <<<"$err"; then
        echo "  FAIL $f rejected for the wrong reason (wanted: $want)"; fail=$((fail + 1))
    fi
done
printf '%-18s %3d passed, %d failed, 0 skipped\n' compile_fail $((n - fail)) "$fail"
[ "$fail" -eq 0 ]
