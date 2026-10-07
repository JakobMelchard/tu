#!/usr/bin/env bash
# scripting_patterns.sh - the bash constructs you need for cluster scripts:
# strict mode, variables and quoting, arithmetic, conditionals, loops, arrays,
# functions, exit codes, traps, here-docs and getopts argument parsing.
#
# Usage: bash scripting_patterns.sh [-v] [-n NAME] [-r REPS] [-h] [files...]
# Works with bash 3.2 (macOS) and 4/5 (Linux clusters); bash-4-only features
# are guarded by a version check.
set -euo pipefail          # -e exit on error, -u unset var is an error, pipefail: pipe fails if any part fails
IFS=$'\n\t'                # word splitting only on newline/tab, not on spaces in filenames

# ---------------------------------------------------------------- functions
usage() {                                   # here-doc: multi-line text; <<- strips leading TABS only
    cat <<USAGE
usage: $(basename "$0") [-v] [-n NAME] [-r REPS] [-h] [files...]
  -v        verbose
  -n NAME   greet NAME (default: \$USER)
  -r REPS   repetitions (integer, default 3)
  -h        this help
USAGE
}

log() { [[ $VERBOSE -eq 1 ]] && printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" >&2 || true; }

die() { printf 'error: %s\n' "$*" >&2; exit 1; }   # >&2 : to stderr

square() {                                  # return a value via stdout, capture with $( )
    local x=$1                              # local: does not leak into the caller
    echo $(( x * x ))
}

is_int() { [[ $1 =~ ^-?[0-9]+$ ]]; }        # exit status of the last command is the function's status

cleanup() {                                 # EXIT trap: runs on normal exit, error exit and Ctrl-C
    local rc=$?
    rm -rf "${SCRATCH:-}"
    log "cleanup done, exit status $rc"
}
trap cleanup EXIT
trap 'printf "failed at line %d: %s\n" "$LINENO" "$BASH_COMMAND" >&2' ERR   # tell me WHERE set -e fired

# ---------------------------------------------------------------- getopts
VERBOSE=0; NAME=${USER:-nobody}; REPS=3
while getopts ':vn:r:h' opt; do             # leading ':' = silent mode, we report errors ourselves
    case $opt in
        v) VERBOSE=1 ;;
        n) NAME=$OPTARG ;;
        r) REPS=$OPTARG ;;
        h) usage; exit 0 ;;
        :) die "option -$OPTARG needs an argument" ;;
        \?) die "unknown option -$OPTARG (try -h)" ;;
    esac
done
shift $((OPTIND - 1))                       # drop the parsed options, "$@" is now the positional rest
is_int "$REPS" || die "-r wants an integer, got '$REPS'"

# ---------------------------------------------------------------- variables & quoting
SCRATCH=$(mktemp -d)
log "scratch dir $SCRATCH"
greeting="hello, $NAME"                     # double quotes: expand $var, $( ), \n stays literal
literal='no $expansion here'                # single quotes: nothing is expanded
printf '%s | %s\n' "$greeting" "$literal"
echo "script: $0, args: $#, first: ${1:-<none>}"    # ${var:-default} if unset/empty
path="/home/user/data/run_07.tar.gz"
echo "basename: ${path##*/}  dirname: ${path%/*}  without .tar.gz: ${path%%.tar*}  run no: ${path:20:2}"
echo "uppercase via tr: $(echo "$NAME" | tr '[:lower:]' '[:upper:]')  length: ${#NAME}"

# ---------------------------------------------------------------- arithmetic
n=7
(( n += 3 ))                                # integer arithmetic only
echo "n=$n  n**2=$(( n ** 2 ))  n/3=$(( n / 3 )) (integer division)  n%3=$(( n % 3 ))"
echo "floats need bc or awk: $(awk "BEGIN { printf \"%.3f\", $n / 3 }")"

# ---------------------------------------------------------------- conditionals
file=$SCRATCH/a.txt; echo "some text" > "$file"
if [[ -f $file && -s $file ]]; then echo "$file exists and is non-empty"; fi   # -d dir, -r readable, -x executable
if [[ $n -gt 5 ]]; then echo "n > 5"; elif [[ $n -eq 5 ]]; then echo "n == 5"; else echo "n < 5"; fi
[[ $NAME == j* ]] && echo "NAME starts with j" || echo "NAME does not start with j"    # glob match in [[ ]]
[[ $NAME =~ ^[a-z]+$ ]] && echo "NAME is all lowercase letters" || echo "NAME has other characters"
case $REPS in
    0) echo "no repetitions" ;;
    1|2|3) echo "a few repetitions ($REPS)" ;;
    *) echo "many repetitions ($REPS)" ;;
esac

# ---------------------------------------------------------------- loops
for (( i = 1; i <= REPS; i++ )); do printf 'rep %d: %s\n' "$i" "$greeting"; done
for f in "$SCRATCH"/*.txt; do echo "glob hit: ${f##*/}"; done       # never parse `ls` output
for host in node{01..03}; do echo "brace expansion: $host"; done
count=0
while IFS= read -r line; do (( count += 1 )); done < "$file"       # read a file line by line
echo "lines in $file: $count"
i=0; until [[ $i -ge 2 ]]; do (( i += 1 )); done; echo "until loop ran $i times"

# ---------------------------------------------------------------- arrays
nodes=(n01 n02 "node with space" n04)      # indexed array
nodes+=(n05)                               # append
echo "${#nodes[@]} nodes; second: ${nodes[1]}; all: $(IFS=' '; echo "${nodes[*]}")"   # [*] joins with IFS[0]
for nd in "${nodes[@]}"; do printf '  <%s>\n' "$nd"; done          # "${arr[@]}" keeps elements intact
echo "slice: ${nodes[@]:1:2}"
sizes=$(for k in 1 2 3; do square "$k"; done | tr '\n' ' ')
echo "squares captured from a function: $sizes"
if (( BASH_VERSINFO[0] >= 4 )); then
    declare -A mem                          # associative array (bash >= 4; the cluster has it, macOS /bin/bash not)
    mem[login]=64; mem[compute]=256
    for k in "${!mem[@]}"; do echo "  $k node: ${mem[$k]} GB"; done
else
    echo "(associative arrays need bash >= 4, this is ${BASH_VERSION})"
fi

# ---------------------------------------------------------------- exit codes
grep -q "text" "$file"; echo "grep found it: status $?"        # $? = status of the last command, 0 = success
if ! grep -q "missing" "$file"; then echo "grep did not find 'missing' (status 1, fine inside if)"; fi
false || echo "'false || cmd' runs cmd because false failed"   # without || this would kill the script (set -e)
(exit 42) || echo "subshell exit code was $?"
rc=0; ls /definitely/not/here 2>/dev/null || rc=$?              # capture a failure without tripping set -e / ERR
echo "ls of a missing path returned $rc"

# ---------------------------------------------------------------- positional args
for f in "$@"; do [[ -e $f ]] && echo "arg exists: $f" || echo "arg missing: $f"; done
echo "done (the EXIT trap removes $SCRATCH)"
