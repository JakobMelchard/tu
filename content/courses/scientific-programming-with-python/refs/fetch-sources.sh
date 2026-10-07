#!/usr/bin/env bash
# Download the two free textbooks listed in SOURCES.md into ./vendor
# (git-ignored).  Both are CC BY 4.0 and could legally be committed; they are
# not, because neither is course material.  See README.md.
#
#   ./fetch-sources.sh            fetch both books
#   ./fetch-sources.sh --verify   checksums only, no network
set -euo pipefail

cd "$(dirname "$0")"

# S38 Sundnes, Introduction to Scientific Programming with Python (Springer OA)
S38=S38-sundnes-introduction-to-scientific-programming-with-python-2020.pdf
S38_URL='https://link.springer.com/content/pdf/10.1007/978-3-030-50356-7.pdf'

# S39 Scientific Python Lectures, release 2024.1
S39=S39-scientific-python-lectures-2024.1.pdf
S39_URL='https://github.com/scipy-lectures/scientific-python-lectures/releases/download/2024.1/ScientificPythonLectures.pdf'

verify() {
    echo "recorded on 2026-09-22:"
    echo "  $S38  1841222 bytes"
    echo "  $S39  18078958 bytes"
    echo "actual:"
    for f in "$S38" "$S39"; do
        if [ -s "vendor/$f" ]; then
            printf '  %s  %s bytes  sha256 %s\n' "$f" \
                "$(wc -c < "vendor/$f" | tr -d ' ')" \
                "$(shasum -a 256 "vendor/$f" | cut -d' ' -f1)"
        else
            echo "  $f  MISSING"
        fi
    done
}

if [ "${1-}" = "--verify" ]; then
    verify
    exit 0
fi

mkdir -p vendor
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url>
    if [ -s "vendor/$1" ]; then
        echo "have  vendor/$1"
    else
        echo "fetch vendor/$1"
        curl -fsSL -A "$UA" -o "vendor/$1" "$2"
    fi
}

get "$S38" "$S38_URL"
get "$S39" "$S39_URL"

echo
verify

cat <<'EOF'

Attribution, required by CC BY 4.0 if you reuse anything from either:

  Joakim Sundnes, "Introduction to Scientific Programming with Python",
  Simula SpringerBriefs on Computing 6, Springer Cham 2020,
  doi:10.1007/978-3-030-50356-7 — CC BY 4.0.

  The Scientific Python developers, "Scientific Python Lectures",
  release 2024.1, https://lectures.scientific-python.org/ — CC BY 4.0.

The library documentation this course actually rests on is NOT downloaded:
it is cited at the exact version installed in the repo venv.  See SOURCES.md.

Nor are the two substitute practice sources S41 (Aalto, Python for Scientific
Computing) and S42 (Software Carpentry, Programming with Python).  Both are
CC BY 4.0 living sites with no tagged release, so there is nothing stable to
pin a checksum to; what was taken from them is restated and reimplemented in
../src/exercises, with the licence in each directory's README.md.
EOF
