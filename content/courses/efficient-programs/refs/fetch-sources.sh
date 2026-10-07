#!/usr/bin/env bash
# Download the cite-only sources listed in SOURCES.md into ./cite-only (git-ignored).
# None of these files carries a redistribution licence, so they are fetched for
# personal study and never committed. Nothing is vendored for this course.
#   ./fetch-sources.sh        fetch what is missing, then pdftotext the slides
#   ./fetch-sources.sh -n     only print what would be fetched
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

DRY=0
[ "${1:-}" = "-n" ] && DRY=1

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
BASE='http://www.complang.tuwien.ac.at/anton/lvas'

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ "$DRY" = 1 ]; then echo "would  $out  <- $url"; return; fi
    if [ -s "$out" ]; then echo "have  $out"; return; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url" || { echo "FAILED $out ($url)" >&2; rm -f "$out"; }
}

# S2 -- course homepage (grading, PR rules, g0 accounts)
get S2-course-homepage.html            "$BASE/effiziente-programme.html"

# S3 -- the English slide deck (primary source; "changes during the semester")
get S3-efficient-slides.pdf            "$BASE/efficient.pdf"

# S4 -- the 2022W German script
get S4-skriptum-effizienz-2022w.html   "$BASE/skriptum-effizienz.html"

# S5-S7 -- last year's exercise sheets
get S5-exercises1-2025w.html           "$BASE/efficient/25/exercises1.html"
get S6-exercises2-2025w.html           "$BASE/efficient/25/exercises2.html"
get S7-exercises3-2025w.html           "$BASE/efficient/25/exercises3.html"

# S8 -- matrix multiply worked example (index page + the sources it links)
get S8-matmul-example.html             "$BASE/effizienz/matmul/"
for f in main.c mm1.c mm2.c mm3.c mm4.c mm5.c Makefile; do
    get "S8-matmul-$f"                 "$BASE/effizienz/matmul/$f"
done

# S9 -- Bentley's TSP programs in C (no tsp7: step 7 was not transliterated)
get S9-tsp.html                        "$BASE/effizienz/tsp.html"
for f in tsp1.c tsp2.c tsp3.c tsp4.c tsp5.c tsp6.c tsp8.c tsp9.c Makefile; do
    get "S9-$f"                        "$BASE/effizienz/$f"
done

# S13 -- Agner Fog: manual 3 (microarchitecture), 4 (instruction tables), 1 (C++)
get S13-agner-microarchitecture.pdf    'https://www.agner.org/optimize/microarchitecture.pdf'
get S13-agner-instruction_tables.pdf   'https://www.agner.org/optimize/instruction_tables.pdf'
get S13-agner-optimizing_cpp.pdf       'https://www.agner.org/optimize/optimizing_cpp.pdf'

# S15 -- Granlund, x86 instruction latencies and throughput
get S15-granlund-x86-timing.pdf        'https://gmplib.org/~tege/x86-timing.pdf'

# text layer of the slides, for grep and for the [S3 p.N] citations
if [ "$DRY" = 0 ] && [ -s cite-only/S3-efficient-slides.pdf ]; then
    if command -v pdftotext >/dev/null 2>&1; then
        [ -s cite-only/S3-efficient-slides.txt ] || pdftotext -layout \
            cite-only/S3-efficient-slides.pdf cite-only/S3-efficient-slides.txt
        echo "text  cite-only/S3-efficient-slides.txt ($(wc -l < cite-only/S3-efficient-slides.txt) lines)"
    else
        echo "pdftotext not found (brew install poppler); skipping the text layer"
    fi
fi

echo
echo "Not fetchable (login or not free):"
echo "  S1/S10 TISS pages: browser, see ../docs/tiss.md"
echo "  S11 Bentley 1982: out of print, ISBN 0-13-970244-X"
echo "  S14 Intel Optimization Reference Manual (248966): needs a click-through at intel.com"
echo "  TUWEL: not accessed"
