# 01 Linux command line

Block 1. Code: [`src/sh/essentials_demo.sh`](../src/sh/essentials_demo.sh) runs every command below in a throw-away directory; read the two side by side.

## What the block actually is

One day, 09:00–16:00, online via Zoom, in four *lecture → exercise →
demonstration → break* cycles with lunch 12:00–13:00 [S6]. One deck end to end:
*Linux Intro*, the "Linux primer" [S7], vendored at
[`../refs/vendor/asc-linux-primer.md`](../refs/vendor/asc-linux-primer.md) —
**read it, it is the course.** TISS marks this block
*"participation is required for Linux newbies only"* [S2]. Every participant
gets a temporary `trainee##` account on **VSC-5** and does the exercises there
[S6]; the setup script the exercises use is `~training/vsc_linux_intro.sh`
(also in the primer's repository as `vsc_linux_intro.sh`) [S7].

The primer's running order, which this note follows: terminal and prompt →
execution → history → completion → flags → order → filesystem → path →
**exercise 1** → navigation → file operations → I/O redirection → transfer
(`scp`, `rsync`, FileZilla, WinSCP) → search (`grep`, `find`, wildcards) →
**exercise 2** → ownership and permissions → size and space → pipes → `sed`,
`awk` → escapes and quotes → variables → environment variables → `top` →
**exercise 3** → editors → scripting → **exercise 4** → documentation →
bonus: `alias`, `.bashrc` [S7]. Transfer, variables and `.bashrc` are written up
in [03](03-environment.md); scripting in [02](02-shell-scripting.md).

The prompt in every primer example is `zen trainee00@l55:~$` [S7]. The first
field is **not** part of a standard bash prompt: on the ASC systems it is the
name of the software environment you are in (`skylake`, `zen`, `cuda-zen`),
which decides which modules you can see [S10]. `l55` is a VSC-5 login node
[S9] [S19].

## What you are talking to

A **terminal** draws characters; the **shell** (bash on the ASC systems) is the program inside it that reads a line, splits it into words, expands `$variables` and `*globs`, and runs the first word as a command with the rest as arguments. Everything on a cluster (your interactive session, every Slurm job script) is a bash process reading commands, so the shell is the one tool you cannot avoid.

`command -options arguments`: short options `-l`, combined `-la`, long options `--all`, options with values `-n 5` / `--lines=5`. `--` ends option parsing (`rm -- -weirdfile`).

## The filesystem

One tree rooted at `/`. Relevant branches: `/home/<user>`, `/tmp`, `/usr/bin` and `/opt` (software), `/etc` (configuration), `/proc` (kernel view of processes, `cat /proc/cpuinfo`).

On the ASC systems specifically [S7] [S19]: `$HOME` is `/home/fs7XXXX/<user>`
(or `/home/lv7XXXX/...` for a course/teaching project — both forms appear in the
primer), `$DATA` is `/gpfs/data/fs7XXXX/<user>`, `/local` is a node-local NVMe
disk that exists **only on compute nodes**, and `/tmp` on a compute node is
backed by RAM. Details and quotas in [04](04-cluster-anatomy.md). There is no
`/scratch`.

- absolute path starts with `/`; relative path is resolved against the current directory (`pwd`).
- `.` this directory, `..` parent, `~` home, `~alice` Alice's home, `-` previous directory (`cd -`).
- names are case sensitive; files starting with `.` are hidden from plain `ls`.
- `ls -l` line: `-rwxr-xr-x 1 owner group 4096 Sep 21 10:00 name`: type+permissions, link count, owner, group, bytes, mtime, name. `d` = directory, `l` = symlink.

## The essential commands

| Group | Commands | Remember |
|---|---|---|
| orient | `pwd`, `ls -la`, `cd`, `tree` | `ls -lt` newest first, `ls -S` largest first |
| create | `mkdir -p a/b/c`, `touch f`, `echo txt > f` | `-p` no error if it exists |
| look | `cat`, `less` (q quits, / searches), `head -n 20`, `tail -f log`, `wc -l`, `file` | `tail -f` follows a growing job output |
| copy/move/delete | `cp -r`, `mv`, `rm -r`, `rmdir` | `mv` renames too; `rm` has no undo |
| filter | `sort -k2 -n`, `uniq -c`, `cut -d, -f3`, `tr a-z A-Z`, `grep`, `sed`, `awk`, `paste`, `xargs` | `uniq` only merges adjacent lines: `sort \| uniq` |
| search | `find DIR -name '*.c'`, `grep -rn pattern DIR`, `which prog`, `locate` | quote the glob for `find` |
| permissions | `chmod`, `chown`, `umask` | `chmod u+x script.sh` before `./script.sh` |
| archive | `tar czf a.tar.gz dir`, `tar xzf a.tar.gz`, `tar tzf`, `gzip`, `gunzip`, `zip`/`unzip` | `czf` create, `xzf` extract, `tzf` list |
| disk | `du -sh dir`, `df -h .`; on ASC `mmlsquota --block-size auto -j home_fs7XXXX home` (and `-j data_fs7XXXX data`) [S19] | `du -sh * \| sort -h` finds the big directories; plain `quota` does not work on Spectrum Scale |
| processes | `ps aux`, `top`/`htop`, `kill PID`, `kill -9`, `jobs`, `fg`, `bg`, `nohup`, `&` | Ctrl-C interrupt, Ctrl-Z suspend then `bg` |
| help | `man cmd`, `cmd --help`, `type cmd`, `apropos word` | `man 3 printf` selects the manual section |
| links | `ln -s target linkname` | symlink stores a path; hard link (`ln`) shares the inode |
| misc | `echo`, `printf`, `date`, `seq`, `sleep`, `history`, `clear`, `uname -a`, `hostname`, `whoami` | `!!` last command, `!$` its last argument |

## Pipes and redirection

Every process has three streams: stdin (0), stdout (1), stderr (2).

```bash
cmd  > file        # stdout to file (truncate)      cmd >> file   append
cmd 2> err.log     # stderr only                    cmd 2>&1      stderr where stdout goes now
cmd > all.log 2>&1 # both into one file: order matters, 2>&1 after the redirect
cmd &> all.log     # bash shorthand for the same
cmd < input.txt    # stdin from a file              cmd <<< "string"   from a string
cmd1 | cmd2        # stdout of cmd1 -> stdin of cmd2 (cmd2 starts at the same time; no temp file)
cmd | tee out.txt  # see it AND save it (tee -a appends)
cmd > /dev/null    # discard
```

Pipelines are how you build tools: `grep -h '^Energy' run_*.out | awk '{print $3}' | sort -n | tail -1` is "largest energy over all runs" without writing a program. `xargs` turns stdin into arguments: `find . -name '*.log' | xargs rm` (safer: `find ... -print0 | xargs -0 rm` or `find ... -delete`).

## Permissions

Three triples, user/group/other, each `r`(4) `w`(2) `x`(1): `rwxr-x---` = `750`. On a directory `x` means "may enter/traverse", `r` "may list", `w` "may create/delete entries".

```bash
chmod u+x run.sh        # symbolic: u g o a, + - =, r w x
chmod 644 data.txt      # octal: rw-r--r--
chmod -R g+rX shared/   # X: execute only for directories and already-executable files
chown alice:proj file   # owner and group (usually root only)
umask 027               # mask subtracted from 666/777 for new files/dirs -> 640/750
```

Group permissions are how project members share data on a cluster: files on `$DATA` are normally group read/writable so that project members can exchange data [S19]. `~/.ssh` must be `700` and keys `600` or ssh refuses to use them.

## find, grep, sed, awk

```bash
find . -name '*.dat' -mtime -1            # modified in the last 24 h
find $DATA -size +1G -type f              # big files
find . -name '*.tmp' -delete              # (dry-run first without -delete)
find . -name '*.c' -exec grep -l MPI_Send {} +

grep -n 'error' job.out                   # line numbers      -i case-insensitive   -v invert
grep -rn --include='*.c' 'MPI_Recv' src/  # recursive
grep -E '^(WARN|ERR)' log                 # extended regex; -F fixed string; -c count; -l file names only
grep -A3 -B1 'Traceback' log              # context lines after / before

sed 's/old/new/' f          # first per line      s/old/new/g   all      -E extended regex
sed -n '10,20p' f           # print a range       sed '/^#/d' f  delete comment lines
sed -i.bak 's/x/y/g' f      # in place (GNU: -i alone; macOS BSD sed needs the suffix)

awk '{print $1, $NF}' f                        # first and last field of every line
awk -F, '$3 > 100 {n++} END {print n}' f.csv    # count rows with column 3 > 100
awk '{s += $2} END {print s/NR}' f             # mean of column 2 (NR = record number)
awk 'NR % 10 == 0' f                           # every 10th line
```

Regex minimum: `.` any char, `*` zero or more, `+` one or more (ERE), `^` `$` anchors, `[abc]` class, `[^0-9]` negated, `\.` literal dot, `(a|b)` alternation (ERE), `\b` word boundary (GNU).

## Editors: survival kit

**vim** is modal. `vim file` opens in *normal* mode where keys are commands.

| Key | Does |
|---|---|
| `i` / `a` / `o` | insert before cursor / after / new line below (enter insert mode) |
| `Esc` | back to normal mode (when in doubt, hit it) |
| `:w` `:q` `:wq` `:q!` | save, quit, save+quit, quit discarding changes |
| `x` `dd` `yy` `p` `u` `Ctrl-r` | delete char, delete line, copy line, paste, undo, redo |
| `/pattern` `n` `N` | search forward, next, previous |
| `:%s/old/new/g` | replace in whole file |
| `gg` `G` `:42` `0` `$` `w` `b` | top, bottom, line 42, line start/end, word forward/back |
| `:set number` `:set paste` | line numbers; paste without auto-indent mess |
| `v` `V` then `d`/`y` | visual selection (chars / lines) |

**nano**: `nano file`, type, `Ctrl-O` save, `Ctrl-X` exit, `Ctrl-W` search, `Ctrl-K` cut line, `Ctrl-U` paste, `Ctrl-G` help, `Alt-U` undo. Bottom bar shows the shortcuts (`^` = Ctrl).

Set `export EDITOR=vim` (or nano) so `crontab -e`, `git commit`, `less` use it.

## Archives and compression

`tar` bundles a directory into one file (a "tarball"); `z` adds gzip, `j` bzip2, `J` xz (smaller, slower). Always archive a directory, not loose files, so extraction does not litter the cwd. Check with `tar tzf` before `tar xzf`. `gzip f` replaces `f` by `f.gz` (`-k` keeps). Transfer many small files as one tarball: parallel filesystems hate small files.

## Pitfalls

- Spaces in names: quote `"$f"` everywhere; better, avoid spaces in names on a cluster.
- Unquoted globs: `rm *.log` expands *before* rm runs; `rm * .log` deletes everything.
- `cmd < f > f` truncates `f` before `cmd` reads it. Use `sponge` or a temp file.
- `./script.sh` needs the executable bit *and* `./` (the cwd is not in `PATH`); `bash script.sh` needs neither.
- Ctrl-S freezes the terminal (XON/XOFF); Ctrl-Q unfreezes.
- Files from Windows have `\r\n` line endings: shebang line fails with `bad interpreter: ^M`; `dos2unix f`.
- `tail -f` on a job output on a parallel filesystem may lag; the file is only flushed when the program flushes (`fflush(stdout)` or `stdbuf -oL`).
- `rm -rf $DIR/` with `DIR` unset becomes `rm -rf /`. `set -u` in scripts, `"${DIR:?}"` in commands.

## Questions

1. **`ls -l` shows `-rw-r-----` on `results.dat`. Who can read it, and what single command lets your project group also write it?**
   Owner reads and writes, group reads, others nothing. `chmod g+w results.dat` (or `chmod 660`).
2. **What is the difference between `cmd > log 2>&1` and `cmd 2>&1 > log`?**
   Redirections apply left to right. First form: stdout to `log`, then stderr to where stdout now points (the file). Second: stderr to where stdout points *now* (the terminal), then stdout to the file; stderr stays on the terminal.
3. **Why does `sort f | uniq -c` count duplicates while `uniq -c f` may not?**
   `uniq` only collapses *adjacent* identical lines; sorting brings duplicates together.
4. **You are in vim, typed a lot, and nothing works as expected. What happened and how do you leave without saving?**
   You are probably in insert mode or a stuck command. `Esc` (twice), then `:q!` Enter.
5. **Give one `find` and one `grep` command that together list every C file under `src/` containing `MPI_Barrier`.**
   `find src -name '*.c' -exec grep -l MPI_Barrier {} +` (or `grep -rl --include='*.c' MPI_Barrier src`).
