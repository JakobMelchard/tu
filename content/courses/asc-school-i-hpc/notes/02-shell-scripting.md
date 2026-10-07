# 02 Shell scripting

Block 1. Code: [`src/sh/scripting_patterns.sh`](../src/sh/scripting_patterns.sh) (every construct here, with getopts and traps); the Slurm scripts in `src/sh/slurm/` are bash scripts too.

A script is a file of shell commands run by a non-interactive shell. On a cluster you write them to automate "compile, copy input, run, post-process" and because every Slurm job *is* one. Bash version: clusters have 4.x/5.x; macOS `/bin/bash` is 3.2 (no associative arrays, no `mapfile`).

**Scope.** The block-1 deck covers scripting in six slides — shebang, loop,
expansion, if/else, case, function — plus one exercise and a bonus section on
`alias` and `.bashrc` [S7]. That is the examinable surface, and it is the first
half of this note. The rest (strict mode, arrays, traps, `getopts`) is not in
the deck; it is here because the ASC Slurm slides tell you to keep job scripts
under ~50 lines and *"put complicated logic elsewhere"* [S9], and "elsewhere" is
a script like this one. ASC's own advice on the surrounding `.bashrc` is
stricter than the primer's: the user documentation says it is *"an absolute
recommendation to not customize the `~/.bashrc` file, or source any custom
scripts with user defined paths, as this may cause the jobs to fail"* [S19].
See [03](03-environment.md).

## Skeleton

```bash
#!/usr/bin/env bash          # shebang: which interpreter; /bin/sh is NOT bash (POSIX only)
set -euo pipefail            # strict mode, see below
IFS=$'\n\t'                  # optional: no word splitting on spaces
main() { ...; }
main "$@"                    # pass all arguments through, quoted
```

`set -e` exits on the first failing command, `-u` makes an unset variable an error, `-o pipefail` makes a pipeline fail if any element fails (default: only the last counts). `set -x` prints every command as executed (debugging); `bash -n f.sh` only parses.

## Variables and quoting

```bash
name="value"                 # no spaces around =
echo "$name" "${name}_suffix" # braces when followed by text
readonly N=10; export PATH="$HOME/bin:$PATH"   # export = visible to child processes
${var:-default}  ${var:=default}  ${var:?error message}  ${var:+alt}   # unset/empty handling
${#var}  ${var:2:3}  ${var#prefix}  ${var##*/}  ${var%suffix}  ${var%%.*}  ${var/old/new}  ${var//old/new}
```

- Double quotes expand `$var`, `$(cmd)`, `$((expr))` and protect spaces/globs. Single quotes expand nothing. Unquoted `$var` is split into words on `IFS` and glob-expanded: almost always wrong.
- `$(cmd)` captures stdout (prefer over backticks). `$((2 + n * 3))` integer arithmetic; `(( n++ ))`, `(( n > 5 ))` as a test. Floats: `bc -l`, `awk`, or python.
- Special: `$0` script, `$1..$9 ${10}` args, `$#` count, `"$@"` all args as separate words, `$?` last status, `$$` PID, `$!` last background PID, `$_` last argument.

## Conditionals

`[[ ... ]]` is the bash test (safe with empty variables, supports `&&`, `||`, `=~`, glob `==`); `[ ... ]` is the POSIX one and needs quotes. Status 0 is true.

```bash
[[ -f "$f" ]]  -d dir  -e exists  -s non-empty  -r -w -x  -z "$s" empty  -n "$s" non-empty
[[ $a == "$b" ]]  [[ $a != $b ]]  [[ $a == pre* ]]  [[ $a =~ ^[0-9]+$ ]]  (string; regex needs no quotes)
[[ $n -eq 3 ]]  -ne -lt -le -gt -ge     or   (( n == 3 ))               (integers)
if cond; then ...; elif cond; then ...; else ...; fi
case $x in  a|b) ...;;  *.c) ...;;  *) ...;; esac
cond && do_if_true || do_if_false      # careful: the || also fires if do_if_true fails
```

## Loops

```bash
for f in *.dat; do ...; done                 # glob, never $(ls)
for i in {1..10}; do ...; done               # brace range; {01..10} zero-padded; seq for variables
for (( i=0; i<n; i++ )); do ...; done
while IFS= read -r line; do ...; done < file # line by line; -r keeps backslashes
while (( retries < 3 )); do ...; done
until ssh host true; do sleep 5; done
break / continue
```

## Functions

```bash
f() { local x=$1; local -i n=${2:-0}; ...; echo "$result"; return 0; }
out=$(f arg1 arg2)          # capture stdout; return only carries 0..255 status
```

Variables are global unless `local`. Arguments arrive as `$1 $2 ...`. `return` sets `$?`; results go through stdout or a global. Define before use (bash is read top to bottom).

## Arrays

```bash
a=(x y "z w"); a+=(v)             # indexed
"${a[@]}" all as words   "${a[*]}" joined by IFS   ${#a[@]} length   ${a[1]}   "${a[@]:1:2}" slice   ${!a[@]} indices
declare -A m; m[key]=val; "${m[key]}"; for k in "${!m[@]}"          # associative (bash >= 4)
IFS=, read -r -a fields <<< "a,b,c"                                 # split a string into an array
mapfile -t lines < file                                             # file into array (bash >= 4)
```

## Exit codes, errors, traps

Every command returns 0 (success) or 1..255. `exit N` from the script, `return N` from a function. Convention: 1 general, 2 usage, 126 not executable, 127 not found, 128+N killed by signal N (130 Ctrl-C, 137 SIGKILL/OOM, 141 SIGPIPE).

```bash
cmd || { echo "failed" >&2; exit 1; }
if ! cmd; then ...; fi                      # status inside if/while/&&/|| does not trigger set -e
rc=0; cmd || rc=$?                          # capture a failure under set -e
trap 'rm -rf "$TMP"' EXIT                   # cleanup on any exit
trap 'echo "line $LINENO: $BASH_COMMAND failed" >&2' ERR
trap 'echo interrupted; exit 130' INT TERM  # Slurm can send a signal before the time limit (--signal=TERM@60)
```

`set -e` caveats: not active in commands tested by `if`/`while`/`&&`/`||`, and a pipeline only fails with `pipefail`. Functions called in an `if` run with `-e` off. Do not rely on `set -e` alone; check what matters explicitly.

## Here-documents and here-strings

```bash
cat > input.nml <<END          # expands $vars
&params  n = $N  /
END
cat <<'END'                    # quoted delimiter: no expansion (write $ literally)
echo "$HOME stays literal"
END
cat <<-END                     # <<- strips leading TABS (not spaces)
	indented
	END
grep foo <<< "$string"         # here-string
```

Generating input files and small Slurm scripts from a loop is the standard use: `for p in 0.1 0.5 1.0; do sed "s/@P@/$p/" template.sbatch > run_$p.sbatch; sbatch run_$p.sbatch; done`.

## Argument parsing with getopts

```bash
usage() { echo "usage: $0 [-v] [-n NAME] [-r N] files..." >&2; exit 2; }
verbose=0; name=default; reps=1
while getopts ':vn:r:h' opt; do             # ':' after a letter = takes a value; leading ':' = handle errors yourself
  case $opt in
    v) verbose=1 ;;  n) name=$OPTARG ;;  r) reps=$OPTARG ;;  h) usage ;;
    :) echo "-$OPTARG needs a value" >&2; usage ;;
    \?) echo "unknown -$OPTARG" >&2; usage ;;
  esac
done
shift $((OPTIND - 1))                       # "$@" now holds the non-option arguments
```

`getopts` handles only short options (`-v`, `-n x`, `-vn x`). For `--long` options loop over `"$@"` with a `case` (see `sync_to_cluster.sh`).

## Pitfalls

- `for f in $(ls)` and `cat file | while read` (the loop runs in a subshell, variables set inside vanish; redirect `< file` instead).
- `[ $x = y ]` with empty `x` becomes `[ = y ]`: syntax error. Use `[[ ]]` or quote.
- `#!/bin/sh` on Linux is dash: no arrays, no `[[`, no `$'..'`. Use `#!/usr/bin/env bash`.
- Windows line endings: `bad interpreter: /bin/bash^M`.
- `echo $?` after `local rc=$?`: `local` itself returns 0. Separate declaration and assignment.
- Pipelines under `pipefail`: `cmd | head -1` fails with 141 when `head` exits before `cmd` finishes writing (see the gunzip line in `essentials_demo.sh`).
- `((i++))` when `i=0` returns status 1 (post-increment evaluates to 0) and kills a `set -e` script. Use `((i += 1))` or `i=$((i+1))`.
- `$@` unquoted re-splits arguments with spaces. Always `"$@"`.
- The `ERR` trap fires on every failing command, including one you deliberately allowed with `set +e`; use `cmd || rc=$?` instead.
- Modifying a running script file: bash reads it lazily, edits can be executed mid-run.

## Questions

1. **Why does `cat data.txt | while read -r l; do n=$((n+1)); done; echo $n` print an empty line?**
   Each side of a pipe runs in a subshell; `n` is incremented in the subshell and lost. Use `while ...; done < data.txt`.
2. **What does `set -euo pipefail` do, and name one failure it does not catch.**
   Exit on error, unset variables are errors, pipelines fail if any element fails. Not caught: a failing command inside `if cond`, `cmd && x`, or a function called in a condition; also a failing `$(cmd)` on the right of `local`/`export`.
3. **Write a one-line loop submitting `run.sbatch` for `T` in 300, 350, 400 K passed as the first argument.**
   `for T in 300 350 400; do sbatch --job-name="T$T" run.sbatch "$T"; done` (inside `run.sbatch`, `T=$1`).
4. **How do you make a script remove its temporary directory even if it is killed by Ctrl-C or fails halfway?**
   `TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT` right after creating it; `EXIT` fires on normal end, `exit`, `set -e` failures and terminating signals that bash handles (INT, TERM).
5. **`getopts 'ab:' opt` is given `-b`. What happens with and without a leading colon in the option string?**
   With `':ab:'` (silent): `opt` becomes `:` and `OPTARG` = `b`, your `case` handles it. Without: getopts prints its own error, `opt` becomes `?`.
