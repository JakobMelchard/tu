#!/usr/bin/env bash
# git_workflow.sh -- annotated feature-branch workflow on a throw-away repository.
# Every step prints the command before running it. Nothing touches your real repos.
# Commands and the branching model follow Pro Git, ch. 2-3 and 7.3 (stash) [S40].
#
#   ./git_workflow.sh              the temporary repository is removed on exit
#   KEEP_DEMO=1 ./git_workflow.sh  keep it for inspection
set -euo pipefail
TMPROOT="$(mktemp -d)"
REPO="$TMPROOT/demo"
[[ "${KEEP_DEMO:-0}" == 1 ]] || trap 'rm -rf "$TMPROOT"' EXIT
mkdir -p "$REPO" && cd "$REPO"
say() { printf '\n# %s\n' "$*"; }
run() { printf '$ %s\n' "$*"; "$@"; }

say "1. create a repository; identity is set locally so the demo works on any machine"
run git init -q -b main
run git config user.name "Demo Student"
run git config user.email "demo@example.com"

say "2. first commit: a README and a .gitignore (never commit build output)"
printf '# demo\n' > README.md
printf 'bin/\n*.o\n*.vtk\n__pycache__/\n' > .gitignore
run git add README.md .gitignore
run git commit -q -m "Initial commit: README and .gitignore"

say "3. start a feature on its own branch (main stays releasable)"
run git switch -c feature/csr-spmv
cat > csr.py <<'PY'
def spmv(row_ptr, col, val, x):
    return [sum(val[k] * x[col[k]] for k in range(row_ptr[i], row_ptr[i + 1])) for i in range(len(row_ptr) - 1)]
PY
run git add csr.py
run git commit -q -m "Add CSR sparse matrix-vector product"
printf 'def test_spmv():\n    assert spmv([0, 1], [0], [2.0], [3.0]) == [6.0]\n' >> csr.py
run git commit -q -am "Add a smoke test for spmv"

say "4. meanwhile main moved on (a hotfix) -- simulate it"
run git switch main
printf '\nBuild with make.\n' >> README.md
run git commit -q -am "README: build instructions"

say "5. rebase the feature onto the new main so history stays linear, then look at it"
run git switch feature/csr-spmv
run git rebase -q main
run git log --oneline --graph --all

say "6. merge with --no-ff so the feature shows up as one unit in the history"
run git switch main
run git merge -q --no-ff -m "Merge feature/csr-spmv" feature/csr-spmv
run git branch -d feature/csr-spmv
run git log --oneline --graph

say "7. tag the state you handed in; tags are how you cite a version in a report"
run git tag -a v0.1 -m "Exercise 1 hand-in"
run git describe --tags

say "8. everyday commands: what changed, stash work in progress, inspect a file's history"
printf 'temporary edit\n' >> README.md
run git status --short
run git diff --stat
run git stash
run git stash pop -q
run git checkout -q -- README.md
run git log --oneline -- csr.py

if [[ "${KEEP_DEMO:-0}" == 1 ]]; then say "done; the demo repo is kept at $REPO"; else say "done; $REPO removed"; fi
