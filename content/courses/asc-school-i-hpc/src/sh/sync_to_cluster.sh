#!/usr/bin/env bash
# sync_to_cluster.sh - rsync a project directory to (or from) the cluster.
# DRY RUN BY DEFAULT: nothing is transferred until you pass --go.
#
# Usage: sync_to_cluster.sh [--go] [--down] [--delete] [SRC] [DEST]
#   default SRC  = current directory
#   default DEST = vsc5:$DATA/<basename of SRC>   ("vsc5" = Host alias in ssh_config.example)
#   --down       reverse direction: pull DEST to SRC (results back to the laptop)
#   --delete     also delete files on the receiving side that are gone on the sending side
#   --go         actually do it (otherwise -n dry run)
#
# rsync copies only changed blocks, resumes, preserves permissions/timestamps,
# and respects an .rsyncignore-style exclude list below.  scp cannot do any of that.
set -euo pipefail

GO=0; DOWN=0; DELETE=()
POS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --go) GO=1 ;;
        --down) DOWN=1 ;;
        --delete) DELETE=(--delete) ;;
        -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
        --) shift; POS+=("$@"); break ;;
        -*) echo "unknown option $1" >&2; exit 2 ;;
        *) POS+=("$1") ;;
    esac
    shift
done

SRC=${POS[0]:-.}
SRC=${SRC%/}                                     # strip trailing slash, we add our own below
NAME=$(basename "$(cd "$SRC" && pwd)")
# $DATA, not $HOME: $HOME is 100 GB, strict, and is not for research data.
# The remote shell expands $DATA, so it is single-quoted here.
DEST=${POS[1]:-vsc5:'$DATA'/$NAME}
DEST=${DEST%/}

# trailing slash on the source = "contents of", so the tree lands in DEST, not DEST/NAME
if [[ $DOWN -eq 1 ]]; then FROM="$DEST/"; TO="$SRC/"; else FROM="$SRC/"; TO="$DEST/"; fi

OPTS=(
    -a            # archive: recursive, keep permissions, times, symlinks
    -v -h         # verbose, human-readable sizes
    -z            # compress in transit (skip for already-compressed data)
    --partial     # keep partially transferred files, resume next time
    --progress
    --exclude .git/ --exclude '*.o' --exclude '__pycache__/' --exclude .venv/
    --exclude '*.tar.gz' --exclude 'build/' --exclude '.DS_Store'
    ${DELETE[@]+"${DELETE[@]}"}   # bash 3.2 (macOS) errors on "${empty[@]}" under set -u
)
[[ $GO -eq 1 ]] || OPTS+=(-n)                    # -n: dry run

echo "rsync ${OPTS[*]} $FROM $TO"
[[ $GO -eq 1 ]] || echo "(dry run; add --go to transfer)"

# rsync -n still logs in to the remote side, so a dry run against an ssh alias
# that is not configured fails with exit 255.  `ssh -G` resolves ~/.ssh/config
# without touching the network; an unconfigured alias resolves to itself.  A
# dotted name is taken as a real hostname and left to ssh.
if [[ $DEST == *:* ]]; then
    HOST=${DEST%%:*}; HOST=${HOST#*@}
    RESOLVED=$(ssh -G "$HOST" 2>/dev/null | awk '$1 == "hostname" { print $2 }') || true
    if [[ $HOST != *.* && ( -z $RESOLVED || $RESOLVED == "$HOST" ) ]]; then
        echo "ssh alias '$HOST' is not configured; see ssh_config.example." >&2
        if [[ $GO -eq 0 ]]; then
            echo "(dry run: remote not contacted; the command above is what --go runs)"
            exit 0
        fi
        exit 1
    fi
fi

rsync "${OPTS[@]}" "$FROM" "$TO"
