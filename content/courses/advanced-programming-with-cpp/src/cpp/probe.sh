#!/usr/bin/env bash
# Probe which C++23 features this toolchain actually builds AND runs.
# Feature-test macros are not enough: Apple libc++ 21 ships views::zip and
# ranges::fold_left without defining __cpp_lib_ranges_zip / _fold, and the
# parallel algorithms need -fexperimental-library, which defines no macro.
#   usage: probe.sh <outdir> <cxx> <cxxflags...>
# writes <outdir>/features.flags   -DHAVE_<NAME>=1 for every probe that passed
#        <outdir>/features.txt     one line per probe: name, result, extra flags
#        <outdir>/experimental.flags   flags the parallel algorithms need (may be empty)
#        <outdir>/modules.flags        flags named modules need (may be empty)
set -uo pipefail
out=$1; cxx=$2; shift 2; flags=("$@")
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$out"; tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
: > "$out/features.flags"; : > "$out/features.txt"; : > "$out/experimental.flags"; : > "$out/modules.flags"

# libc++experimental.a on this SDK is built for the current macOS; link for it too
exp=(-fexperimental-library)
if [ "$(uname)" = Darwin ]; then exp+=("-mmacosx-version-min=$(sw_vers -productVersion)"); fi

try() {  # try <name> <extra flags...>: compile, link, run
    local n=$1; shift
    "$cxx" "${flags[@]}" "$@" "$here/probes/$n.cpp" -o "$tmp/$n" >"$tmp/$n.log" 2>&1 && "$tmp/$n" >/dev/null 2>&1
}
record() {  # record <name> <yes|no> <extra flags>
    local up; up=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')
    [ "$2" = yes ] && printf -- '-DHAVE_%s=1 ' "$up" >> "$out/features.flags"
    printf '%-20s %-4s %s\n' "$1" "$2" "$3" >> "$out/features.txt"
}

for f in "$here"/probes/*.cpp; do
    n=$(basename "$f" .cpp)
    if try "$n"; then record "$n" yes ""
    elif try "$n" "${exp[@]}"; then
        record "$n" yes "${exp[*]}"
        [ "$n" = execution ] && printf '%s ' "${exp[@]}" > "$out/experimental.flags"
    else
        record "$n" no "$(grep -m1 -E 'error' "$tmp/$n.log" | sed -E 's/^[^ ]+ //' | cut -c1-70)"
    fi
done

# named modules: plain first, then Apple clang's -fcxx-modules
m="$here/probes/modules.cppm"
if "$cxx" "${flags[@]}" -x c++-module --precompile "$m" -o "$tmp/m.pcm" >/dev/null 2>&1; then
    record modules yes ""
elif "$cxx" "${flags[@]}" -fcxx-modules -x c++-module --precompile "$m" -o "$tmp/m.pcm" >/dev/null 2>&1; then
    record modules yes "-fcxx-modules"; printf -- '-fcxx-modules ' > "$out/modules.flags"
else
    record modules no "named module interface does not precompile"
fi
cat "$out/features.txt"
