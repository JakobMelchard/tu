#!/usr/bin/env bash
# essentials_demo.sh - exercises the ~25 essential Linux commands in a scratch
# directory that is removed again on exit.  Read it top to bottom next to
# notes/01-linux-command-line.md; every block prints the command it runs.
#
# Usage: bash essentials_demo.sh          (no arguments, touches nothing outside $TMP)
# Portable across GNU (Linux/cluster) and BSD (macOS) userland: no `sed -i`
# without suffix, no `find -printf`, no `stat -c`.
set -euo pipefail

TMP=$(mktemp -d)                       # a fresh scratch directory
trap 'rm -rf "$TMP"' EXIT              # always clean up, even on error/Ctrl-C
cd "$TMP"

demo() { printf '\n$ %s\n' "$*"; "$@"; }   # print the command, then run it

echo "== where am I, what is here =="
demo pwd
demo mkdir -p project/src project/data "project/results/run 1"   # -p: parents, no error if exists
demo ls -la project
demo cd project; echo "(cd changes the shell's cwd: now $(pwd))"

echo; echo "== creating and looking at files =="
demo touch src/main.c src/util.c                  # create empty / update timestamp
printf 'alpha 1\nbeta 2\ngamma 3\ndelta 4\nepsilon 5\nbeta 2\n' > data/values.txt   # > overwrites
printf 'zeta 6\n' >> data/values.txt                                                # >> appends
demo cat data/values.txt
demo head -n 2 data/values.txt
demo tail -n 2 data/values.txt
demo wc -l data/values.txt                        # -l lines, -w words, -c bytes
demo file data/values.txt

echo; echo "== copy, move, rename, delete =="
demo cp data/values.txt data/values.bak
demo cp -r data data_copy                          # directories need -r
demo mv data/values.bak data/backup.txt            # mv = move AND rename
demo rm data/backup.txt
demo rm -r data_copy                               # -r for directories; -f to ignore missing; NEVER rm -rf / by accident
demo ls -R

echo; echo "== pipes and filters =="
demo sort data/values.txt
demo sort -k2 -n -r data/values.txt                # by 2nd column, numeric, reverse
printf '$ sort data/values.txt | uniq -c\n'; sort data/values.txt | uniq -c      # uniq needs sorted input
printf '$ cut -d" " -f1 data/values.txt | tr a-z A-Z | paste -sd, -\n'
cut -d" " -f1 data/values.txt | tr a-z A-Z | paste -sd, -
demo grep -n 'beta' data/values.txt                # -n line numbers, -i ignore case, -v invert, -r recursive
demo grep -c 'a' data/values.txt                   # count matching lines
printf '$ grep -E "^(a|e)" data/values.txt\n'; grep -E "^(a|e)" data/values.txt   # extended regex
demo sed 's/beta/BETA/' data/values.txt            # stream edit, first match per line (add g for all)
demo sed -n '2,3p' data/values.txt                 # print only lines 2-3
demo awk '{ sum += $2 } END { print "sum of column 2:", sum }' data/values.txt
demo awk -F' ' '$2 > 3 { print $1 }' data/values.txt
printf '$ seq 1 5 | xargs -n 2 echo\n'; seq 1 5 | xargs -n 2 echo         # xargs: stdin -> arguments

echo; echo "== redirection =="
demo ls nonexistent 2> errors.log || true          # 2> sends stderr to a file; || true keeps set -e quiet
demo cat errors.log
ls src nonexistent > both.log 2>&1 || true         # both streams into one file (order matters: > first, then 2>&1)
demo cat both.log
demo tee -a both.log <<< "appended via tee"        # tee: write to file AND stdout

echo; echo "== find =="
demo find . -name '*.c'                            # by name (quote the glob!)
demo find . -type d                                # directories only
demo find . -type f -size -1k                      # files smaller than 1 KiB
demo find . -name '*.log' -exec wc -c {} \;        # run a command per hit

echo; echo "== permissions =="
printf '#!/usr/bin/env bash\necho "hello from a script"\n' > run.sh
demo ls -l run.sh
demo chmod u+x run.sh                              # user executable; chmod 755 == rwxr-xr-x
demo ls -l run.sh
demo ./run.sh                                      # ./ because . is (rightly) not in PATH
demo chmod 600 data/values.txt                     # private file: rw-------
demo ls -l data/values.txt
demo umask                                         # default mask for new files (022 -> 644 / 755)

echo; echo "== links, disk usage, diff =="
demo ln -s data/values.txt shortcut.txt            # symbolic link
demo ls -l shortcut.txt
demo du -sh .                                      # size of this tree
demo df -h .                                       # free space on the filesystem holding .
sed 's/gamma/GAMMA/' data/values.txt > data/values2.txt
demo diff data/values.txt data/values2.txt || true # exit 1 means "files differ"

echo; echo "== archives =="
demo tar czf project.tar.gz src data               # c create, z gzip, f file; x extracts, t lists
demo tar tzf project.tar.gz
demo mkdir extracted; demo tar xzf project.tar.gz -C extracted
demo gzip -k data/values2.txt                      # single file compression (-k keep original)
demo ls -l data
# PITFALL: `gunzip -c f | head -1` can exit 141 under pipefail (head closes the
# pipe early, gunzip gets SIGPIPE).  sed -n 1p reads to EOF and is safe here.
printf '$ gunzip -c data/values2.txt.gz | sed -n 1p\n'; gunzip -c data/values2.txt.gz | sed -n 1p

echo; echo "== processes, help, environment =="
demo which bash
demo uname -a
sleep 30 & bg_pid=$!                               # background job, $! is its PID
printf '$ ps -p %s -o pid,stat,command\n' "$bg_pid"; ps -p "$bg_pid" -o pid,stat,command
demo kill "$bg_pid"                                # SIGTERM; kill -9 as last resort
echo '$ man ls  /  ls --help  /  type cd   (read the manual; type shows builtins)'
demo type cd
demo echo "HOME=$HOME USER=${USER:-?} SHELL=$SHELL"
demo history -c                                    # (clears this non-interactive shell's empty history)

echo; echo "done; scratch dir $TMP is removed by the EXIT trap"
