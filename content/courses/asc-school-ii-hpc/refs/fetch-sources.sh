#!/usr/bin/env bash
# fetch-sources.sh - personal copies of the course material into ./cite-only
# (git-ignored).  Nothing here is committed: the CC BY-SA repositories could be,
# but are large and change before every course run, so they are cloned fresh;
# the rest has no redistribution licence.  See README.md and SOURCES.md.
#
#   bash fetch-sources.sh            # everything
#   bash fetch-sources.sh --list     # print what would be fetched
#
# Never touches TUWEL.  Needs curl and git; safe to re-run (skips what exists).
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
LIST=0
[ "${1:-}" = "--list" ] && LIST=1

get() {  # get <file name> <url>
    local out="cite-only/$1"
    if [ "$LIST" -eq 1 ]; then echo "get   $out <- $2"; return; fi
    if [ -s "$out" ]; then echo "have  $out"; return; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$2" || { rm -f "$out"; echo "FAILED $2" >&2; }
}

clone() {  # clone <dir> <git url>   (CC BY-SA 4.0 ASC training repositories, S7)
    local out="cite-only/$1"
    if [ "$LIST" -eq 1 ]; then echo "clone $out <- $2"; return; fi
    if [ -d "$out/.git" ]; then echo "have  $out"; return; fi
    echo "clone $out"
    git clone --depth 1 --quiet "$2" "$out" || echo "FAILED $2" >&2
}

# ---- ASC training material, CC BY-SA 4.0 (S7) -------------------------------
G=https://gitlab.tuwien.ac.at/vsc-public/training
clone python4hpc                    "$G/python4hpc.git"
clone introduction-to-deep-learning "$G/introduction-to-deep-learning.git"
clone LLMs-on-supercomputers        "$G/LLMs-on-supercomputers.git"

# ---- ASC-Intro decks (no licence stated; sibling register S9) -----------------
E=https://events.asc.ac.at/event
get gpus.pdf           "$E/275/attachments/270/812/gpus.pdf"
get slurm_advanced.pdf "$E/275/attachments/270/813/slurm_advanced.pdf"

# ---- Machine-readable training calendar (S4), for re-checking the catalogue ---
get asc-trainings.json \
    "https://events.asc.ac.at/export/categ/4.json?limit=400&from=$(date +%Y)-01-01&to=$(( $(date +%Y) + 2 ))-12-31"

# ---- Specifications (redistributable, but linked rather than duplicated) -----
get OpenMP-API-Specification-5-2.pdf \
    "https://www.openmp.org/wp-content/uploads/OpenMP-API-Specification-5-2.pdf"
# MPI 5.0 is vendored in ../../../ws2027/asc-school-i-hpc/refs/vendor/

echo "done; see README.md for what each file is and whether it may be shared"
