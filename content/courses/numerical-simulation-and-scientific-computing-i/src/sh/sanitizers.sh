#!/usr/bin/env bash
# sanitizers.sh -- compile buggy_sample.cpp with AddressSanitizer + UndefinedBehaviorSanitizer
# and show what each report looks like. Exit code of the buggy program is expected to be
# non-zero; the script itself succeeds.
# Sources: AddressSanitizer [S38]; clang's ASan/UBSan documentation for the flags [S37].
#
#   ./sanitizers.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${TMPDIR:-/tmp}/buggy_sample"

echo "# without sanitizers the bugs are silent (or crash unpredictably):"
clang++ -std=c++17 -O1 -g "$HERE/buggy_sample.cpp" -o "$OUT.plain"
for bug in heap uaf int stack; do
    out="$( ( "$OUT.plain" "$bug"; exit $? ) 2>&1 || echo "(exit $?)" )"
    printf '  %-6s -> %s\n' "$bug" "${out:-(no output)}"
done

echo
echo "# with -fsanitize=address,undefined -fno-omit-frame-pointer -g:"
clang++ -std=c++17 -O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined "$HERE/buggy_sample.cpp" -o "$OUT.san"
for bug in heap uaf int stack; do
    printf '\n---- %s ----\n' "$bug"
    # ASan aborts on the first error; UBSan prints and continues. Show the first report lines.
    ( ASAN_OPTIONS=detect_leaks=0 "$OUT.san" "$bug"; exit $? ) > "$OUT.log" 2>&1 || true   # inner exit keeps the signal message inside the log
    grep -E 'ERROR|runtime error|SUMMARY|#[0-3] ' "$OUT.log" | head -8
done
rm -f "$OUT.plain" "$OUT.san" "$OUT.log"
echo
echo "# reading the report: SUMMARY names the bug class, the first frames point at buggy_sample.cpp:LINE."
echo "# same flags work for any program; ASan costs ~2x run time, UBSan almost nothing."
