#!/usr/bin/env bash
# Verify (and if necessary re-fetch) the vendored RFCs, and optionally download
# the cite-only papers into ./vendor, which is git-ignored.  See README.md for
# why the RFCs are vendored and the papers are not.
#
#   ./fetch-sources.sh --verify    checksums only, no network
#   ./fetch-sources.sh             re-fetch anything missing or changed, verify
#   ./fetch-sources.sh --papers    the above, plus the cite-only PDFs
set -euo pipefail

cd "$(dirname "$0")"
MODE="${1:-refetch}"

RFCS=$(sed 's/.*  //; s/^rfc//; s/\.txt$//' rfc/SHA256SUMS)

verify() {
    (cd rfc && shasum -a 256 -c SHA256SUMS)
}

refetch() {
    mkdir -p rfc
    for n in $RFCS; do
        out="rfc/rfc$n.txt"
        if [ -s "$out" ]; then
            continue
        fi
        echo "fetch $out"
        curl -fsS -o "$out" "https://www.rfc-editor.org/rfc/rfc$n.txt"
    done
}

papers() {
    mkdir -p vendor
    get() {  # get <name> <url>
        if [ -s "vendor/$1" ]; then echo "have  vendor/$1"; return; fi
        echo "fetch vendor/$1"
        curl -fsSL -o "vendor/$1" "$2" || echo "  failed (cite-only source, fetch by hand)"
    }
    # S26 -- the end-to-end argument (ACM copyright, free from MIT).
    get S26-saltzer-reed-clark-end-to-end.pdf \
        'https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf'
    # S27 -- Gao & Rexford, stable routing without global coordination.
    get S27-gao-rexford-stable-internet-routing.pdf \
        'https://www.cs.princeton.edu/~jrex/papers/sigmetrics00.pdf'
    # S29 -- Mathis et al., the sqrt(p) throughput model.
    get S29-mathis-macroscopic-tcp.pdf \
        'https://www.cs.cmu.edu/~srini/15-744/papers/Mathis-CCR97.pdf'
}

case "$MODE" in
    --verify) verify ;;
    --papers) refetch; verify; papers ;;
    *)        refetch; verify ;;
esac

echo
echo "$(wc -l < rfc/SHA256SUMS | tr -d ' ') RFCs, $(du -sh rfc | cut -f1) in rfc/"
