#!/usr/bin/env bash
# Download the two textbooks this course's notes rest on into ./vendor
# (git-ignored). See SOURCES.md and README.md for licences.
#
#   S9  Shalev-Shwartz & Ben-David, Understanding Machine Learning (UML)
#       "personal use only. Not for distribution."  -> never commit this file.
#   S10 Mohri, Rostamizadeh & Talwalkar, Foundations of ML, 2nd ed. (FoML)
#       CC-BY-NC-ND -> verbatim non-commercial redistribution IS permitted.
#
# Nothing here touches TUWEL: the course publishes no public material.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url> [referer]
    local out="vendor/$1" url="$2" ref="${3-}"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    if [ -n "$ref" ]; then
        curl -fsSL -A "$UA" -e "$ref" -o "$out" "$url"
    else
        curl -fsSL -A "$UA" -o "$out" "$url"
    fi
}

# S9 — UML. cs.huji.ac.il rejects a bare curl; the UA and referer above are
# enough. If it ever returns an HTML error page instead of a PDF, open
# https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/copy.html
# in a browser and save the file into vendor/ by hand.
get S9-shalev-shwartz-ben-david-understanding-machine-learning.pdf \
    'https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf' \
    'https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/copy.html'

# S10 — FoML. The book page links Dropbox; dl.dropboxusercontent.com serves the
# file directly, while www.dropbox.com returns the viewer HTML.
get S10-mohri-rostamizadeh-talwalkar-foundations-of-machine-learning-2e.pdf \
    'https://dl.dropboxusercontent.com/s/38p0j6ds5q9c8oe/10290.pdf'

# S11 — Telgarsky's deep learning theory notes (optional, for note 10).
# No licence statement; personal use only.
get S11-telgarsky-deep-learning-theory.pdf \
    'https://mjt.cs.illinois.edu/dlt/index.pdf'

# S12 — Bach, Learning Theory from First Principles (optional, notes 07-08).
get S12-bach-learning-theory-from-first-principles.pdf \
    'https://www.di.ens.fr/~fbach/ltfp_book.pdf'

echo
echo "expected checksums as retrieved 2026-09-22:"
cat <<'EOF'
5ad0c69c922e47e423f6b469e8cfbaf07beae6933185af746b670911a8d163f2  S9   (2601512 bytes, 449 pp.)
1a986e004028786686d51730693f200429d31424e687c5e18d19e28511852904  S10  (6224448 bytes, 505 pp.)
EOF
echo
echo "yours:"
shasum -a 256 vendor/S9-*.pdf vendor/S10-*.pdf 2>/dev/null || true
echo
echo "A differing checksum is not an error - these books are revised in place."
echo "Record the new one and re-check the theorem locators in SOURCES.md."
