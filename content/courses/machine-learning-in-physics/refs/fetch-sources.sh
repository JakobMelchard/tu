#!/usr/bin/env bash
# Download the free documents the 138.128 notes cite into ./cite-only
# (git-ignored). Personal use; none of these files is committed.
# See SOURCES.md and README.md for the licence of each.
#
#   S6  Mehta et al., Phys. Rep. 810 (2019), arXiv:1803.08823v3
#       arXiv "non-exclusive distribution" licence -> cite only
#   S7  Deisenroth, Faisal, Ong, Mathematics for Machine Learning (CUP 2020)
#       free PDF, personal use -> cite only
#   S8  Hastie, Tibshirani, Friedman, ESL 2nd ed., 12th printing
#       Springer copyright, author-hosted -> cite only
#   S9  James, Witten, Hastie, Tibshirani, Taylor, ISL with Python (2023)
#       Springer copyright, author-hosted -> cite only
#   S10 Hansen, Discrete Inverse Problems (SIAM 2010): NOT free, not fetched.
#
# Never TUWEL, never JupyterHub.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url"
    if ! head -c 5 "$out" | grep -q '%PDF'; then
        echo "      not a PDF (probably an HTML interstitial); open $url in a browser" >&2
        rm -f "$out"
    fi
}

get S6-mehta-high-bias-low-variance-ml-for-physicists.pdf \
    'https://arxiv.org/pdf/1803.08823v3'

get S7-deisenroth-faisal-ong-mathematics-for-machine-learning.pdf \
    'https://mml-book.github.io/book/mml-book.pdf'

# hastie.su.domains/ElemStatLearn/download.html links printings/ESLII_print12.pdf
# (404 on 2026-09-28) and a Google Drive redirect for the print12_toc version.
get S8-hastie-tibshirani-friedman-esl-2e-print12.pdf \
    'https://drive.google.com/uc?export=download&id=1--Wo5Hcl2y_v3DL-tGgcJHRPdtjiVYjS'

# statlearning.com -> hastie.su.domains/ISLP/ISLP_website.pdf.download.html
get S9-james-witten-hastie-tibshirani-taylor-islp.pdf \
    'https://drive.google.com/uc?export=download&id=1ajFkHO6zjrdGNqhqW1jKBZdiNGh_8YQ1'

echo
shasum -a 256 cite-only/*.pdf 2>/dev/null || true
echo "Record changed checksums in SOURCES.md; these files are revised in place."
