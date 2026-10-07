# 03 Environment: variables, dotfiles, SSH, file transfer, terminal multiplexers

Block 1. Code: [`src/sh/env_setup.sh`](../src/sh/env_setup.sh) (prints a reviewed `.bashrc` block), [`src/sh/ssh_config.example`](../src/sh/ssh_config.example), [`src/sh/sync_to_cluster.sh`](../src/sh/sync_to_cluster.sh) (rsync, dry run by default).

## Logging in to ASC, concretely

This is the part of block 1 that is actually about *these* machines, and it is
also the pre-assignment you must complete before the course starts [S6] [S13].

| | |
|---|---|
| VSC-4 | `ssh [-X] <user>@vsc4.vsc.ac.at`; login nodes `l40 … l47` [S19] (the March-2026 slide says `l40 … l49`, "10 dedicated login nodes" [S9] — a discrepancy; trust `sinfo`/the docs) |
| VSC-5 | `ssh [-X] <user>@vsc5.vsc.ac.at`; login nodes `l50 … l56` [S9] [S19] |
| training accounts | `ssh trainee##@vsc5.vsc.ac.at`, or without a partner-university IP `ssh -t trainee##@vmos.vsc.ac.at vsc5` [S6] [S13] |
| browser | <https://jupyterhub.vsc.ac.at> — "Start", then a Terminal; "Stop my Server" and log out at the end [S6] [S13] |
| GUI | NoMachine for anything graphics-heavy; `ssh -X` only for `gnuplot`-class tools [S19] |

Three things differ from a generic cluster:

1. **Two factors, always.** Password *plus* a one-time password sent by SMS to
   the mobile number on your account. The OTP is valid for 12 hours; the
   password is asked every session [S6] [S19]. This is why ASC needs your
   international mobile number at registration, and why a wrong number is the
   most common reason a participant cannot start the course [S6].
2. **IP restriction.** Since November 2013 logins are only accepted from the IP
   ranges of the partner universities: be on campus, on the university VPN, or
   on ASC's own WireGuard service [S19]. The `vmos.vsc.ac.at` jump host exists
   for `trainee` users precisely because visitors have no such IP [S6].
3. **Login-node limits are enforced, not just requested.** Per user, across all
   your processes on a login node: **24 GB memory and 4 cores**, by cgroup; all
   users together may use at most 80 % of the node. Compile with at most 4
   threads. ASC will kill processes that hurt others and e-mail you about it
   [S19].

On Windows the course asks you to install **PuTTY** plus **FileZilla or WinSCP**
before the course [S6] [S7].

## Environment variables

A process has an *environment*: a list of `NAME=value` strings it inherits from its parent at start. Shell variables live only in the shell; `export NAME` copies them into the environment of every child (compilers, `mpirun`, your program via `getenv`). `env`/`printenv` list them, `unset NAME` removes, `NAME=value cmd` sets for one command only.

Important ones: `HOME`, `USER`, `SHELL`, `PATH`, `LD_LIBRARY_PATH` (extra shared-library directories; modules set it), `CPATH`/`LIBRARY_PATH` (compiler search paths), `OMP_NUM_THREADS`, `EDITOR`, `LANG`, `TMPDIR`, `PS1` (prompt), and site ones like `SCRATCH`/`DATA`. Slurm exports `SLURM_*` inside jobs ([06](06-slurm.md)).

**PATH** is a colon-separated list of directories searched left to right for a command name; `which prog`/`type prog` show what wins. Add your own directory at the front and *keep* the old value: `export PATH="$HOME/bin:$PATH"`. Never put `.` in PATH (a malicious `ls` in a shared directory).

## Dotfiles

Which file bash reads depends on how it starts:

| Shell type | Reads | Example |
|---|---|---|
| login, interactive | `/etc/profile`, then the first of `~/.bash_profile`, `~/.bash_login`, `~/.profile` | `ssh cluster` |
| non-login, interactive | `~/.bashrc` | a new terminal tab, `bash` typed in a shell, tmux pane |
| non-interactive | nothing (only `$BASH_ENV` if set); but `~/.bashrc` is read at the start of ssh remote commands and Slurm jobs **on some sites** | `bash script.sh`, `ssh host cmd`, `sbatch` |

Convention: put everything in `~/.bashrc` and make `~/.bash_profile` contain `[[ -f ~/.bashrc ]] && source ~/.bashrc`. Inside `.bashrc`, guard interactive-only things (aliases, prompt, `stty`) with `case $- in *i*) ;; *) return ;; esac`, otherwise `scp`, `rsync` and batch jobs break on output they do not expect. After editing: `source ~/.bashrc` (no new login needed). Keep a working copy (`cp ~/.bashrc ~/.bashrc.ok`) before experiments; a broken rc file can make every login unusable.

**Two pieces of ASC advice that contradict each other — know both.** The Linux
primer teaches `alias` and `.bashrc` as its bonus section, and the ASC intro
slide even hands you a starting point, `cp ~training/bashrc_recommended ~/.bashrc`
(*"cp overwrites!"*) [S7] [S9]. The user documentation, on the other hand, is
blunt: *"It is an absolute recommendation to not customize the `~/.bashrc` file,
or source any custom scripts with user defined paths, as this may cause the jobs
to fail"*, and lists customising the prompt and sourcing user scripts as "not
recommended" [S19]. Both are defensible and they are aimed at different
failures: the primer is teaching you what the file is; the documentation is
telling you why your Slurm job died. The resolution used in
[`../src/sh/env_setup.sh`](../src/sh/env_setup.sh) is to put only
`export`-and-alias lines behind an interactivity guard, and to `module load`
**nothing** outside a job script.

```bash
alias ll='ls -lh'                      # text substitution for the FIRST word of a command only
alias sq='squeue --me'
unalias ll; \ls                        # bypass an alias once with a backslash
mkcd() { mkdir -p "$1" && cd "$1"; }   # anything with arguments is a function, not an alias
export HISTSIZE=50000 HISTCONTROL=ignoredups; shopt -s histappend
```

`~/.inputrc` configures line editing (`set completion-ignore-case on`), `~/.vimrc` vim (`set number`, `syntax on`), `~/.ssh/config` ssh (below). Do not `module load` in `.bashrc` unless you want *every* job to depend on it; load in the job script.

## SSH

`ssh user@login.host` opens an encrypted shell. Authentication by password or, preferably, by key pair: the private key stays on your laptop (`~/.ssh/id_ed25519`, mode 600, passphrase-protected), the public key goes to `~/.ssh/authorized_keys` on the cluster (mode 600, `~/.ssh` 700).

**On ASC this is the generic story, not the whole one.** The documented way in
to `vsc4`/`vsc5` is password + SMS OTP [S19]; the intro slide mentions ssh-keys
and `ssh -p 27` alongside the PuTTY screenshots but no public page read here
explains them *(unsourced: the slide names them without detail and the user
documentation has no ssh-key page, so treat key-based login as something to ask
support about, not as a recipe)* [S9]. What key pairs unambiguously buy you on
ASC is hops **inside** the cluster — e.g. `ssh n3071-003` onto a node your job
holds [S9] — and `rsync` loops from your laptop through your own jump host.

```bash
ssh-keygen -t ed25519 -C "laptop 2026"        # creates ~/.ssh/id_ed25519 and .pub
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@login.host   # or paste the .pub into the site portal
eval "$(ssh-agent -s)"; ssh-add ~/.ssh/id_ed25519       # type the passphrase once per session
ssh -v user@host                               # debug why a login fails (which key was tried, permissions)
ssh user@host 'squeue --me'                    # run one command remotely
ssh -L 8888:localhost:8888 user@host           # port forward: local 8888 -> remote 8888 (Jupyter on a node)
ssh -J jump.host user@inner.host               # jump through a gateway (ProxyJump)
ssh -X user@host                               # X11 forwarding for the odd GUI (slow; prefer no GUI)
```

`~/.ssh/config` turns all that into `ssh asc` ([example file](../src/sh/ssh_config.example)): `Host` alias, `HostName`, `User`, `IdentityFile`, `ProxyJump`, `ServerAliveInterval` (keep NAT connections alive), `ControlMaster auto` + `ControlPath` (one TCP connection reused by many ssh/scp/rsync calls, big win for many small transfers), `ForwardAgent no` by default. `known_hosts` stores server fingerprints; a *changed* fingerprint warning means the server was reinstalled or something is wrong: ask, do not blindly delete the line.

## Moving files

```bash
scp file user@host:~/dir/                 # single files; scp -r dir  for trees; no resume, no sync
scp user@host:'~/results/*.dat' .         # remote glob needs quoting
rsync -avz --partial --progress src/ user@host:~/proj/    # only changed parts, resumes, keeps times/permissions
rsync -avn ...                            # -n dry run: ALWAYS first when --delete is involved
rsync -av --delete src/ dest/             # mirror: remove files on dest that vanished in src
sftp user@host                            # interactive: ls, cd, lcd, get, put, mget
```

Trailing slash on the rsync source means "contents of": `src/` to `dest/` puts `src`'s files directly into `dest`; `src` to `dest/` creates `dest/src`. Big transfers: `tar` many small files first, use the site's data-mover node if there is one, `nohup rsync ... &` or run it inside tmux so a dropped laptop connection does not abort it. Mounting the cluster via `sshfs` is convenient for editing but slow for data.

## tmux / screen

A terminal multiplexer keeps shell sessions alive on the login node after you disconnect and lets you split windows. Start `tmux` on the login node, work, detach, log out, come back tomorrow, `tmux attach`. (The login node may reboot; nothing in tmux survives that, and long computations belong in Slurm jobs, not in tmux.)

| tmux (prefix `Ctrl-b`) | screen (prefix `Ctrl-a`) | Does |
|---|---|---|
| `tmux new -s work` / `tmux attach -t work` / `tmux ls` | `screen -S work` / `screen -r work` / `screen -ls` | create / reattach / list |
| prefix `d` | prefix `d` | detach |
| prefix `c`, `n`, `p`, `0-9` | prefix `c`, `n`, `p`, `0-9` | new window, next, previous, jump |
| prefix `%` / `"` , arrows | prefix `\|` / `S`, `Tab` | split vertical / horizontal, move |
| prefix `[` then arrows, `q` | prefix `[` | scroll back (copy mode) |
| prefix `x` | prefix `k` | kill pane/window |

`~/.tmux.conf`: `set -g mouse on`, `set -g history-limit 50000`.

## Pitfalls

- `export PATH=/my/bin` (without `:$PATH`): every command is now "not found" until you fix it with `/usr/bin/vim` or a new login.
- Permissions on `~/.ssh` (700) and keys (600) too open: ssh silently ignores the key and asks for a password.
- Agent forwarding to a shared machine lets root there use your key: keep `ForwardAgent no`, use `ProxyJump`.
- `scp -r` follows symlinks and copies the targets; `rsync -a` copies them as links.
- A `.bashrc` that prints (`echo "welcome"`) or runs `module load` with output breaks `scp`/`sftp` and some rsync setups ("protocol error").
- Copying `.bashrc` from another site with hard-coded module names: every login prints errors.
- Editing files on the cluster over sshfs with an IDE that creates lock/tmp files on the parallel filesystem: slow; edit locally, `rsync`, or use the IDE's remote-ssh mode.

## Questions

1. **You add an alias to `~/.bashrc`, open a new ssh session, and it is not there. Why, and what is the two-line fix?**
   ssh gives a *login* shell, which reads `~/.bash_profile`, not `~/.bashrc`. Put `[[ -f ~/.bashrc ]] && source ~/.bashrc` into `~/.bash_profile`.
2. **What does `ssh-add` do and why does it matter for `rsync` in a loop?**
   It loads the decrypted private key into the agent so each new ssh connection does not ask for the passphrase; otherwise every rsync/scp call prompts (or fails in a non-interactive script).
3. **Difference between `rsync -av src dest` and `rsync -av src/ dest`?**
   Without slash the directory `src` itself is created inside `dest` (`dest/src/...`); with slash only its contents land in `dest/`.
4. **Why should long-running work not be started directly in a tmux session on the login node?**
   Login nodes are shared, unscheduled, and CPU/memory limited by policy; heavy processes get killed and slow everybody. tmux is for editing, monitoring and transfers; compute goes through Slurm.
5. **What is the purpose of `ServerAliveInterval` and `ControlMaster` in `~/.ssh/config`?**
   `ServerAliveInterval 60` sends keep-alive packets so idle sessions are not dropped by NAT/firewalls. `ControlMaster auto` multiplexes subsequent ssh/scp/rsync connections over the first one: no repeated handshake/authentication.
