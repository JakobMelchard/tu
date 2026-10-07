#!/usr/bin/env bash
# Download the cite-only PDFs listed in SOURCES.md into ./cite-only (git-ignored).
# These files carry no redistribution licence, so they are fetched for personal
# study and never committed. The three redistributable sources are already in
# ./vendor and are NOT fetched here. See README.md.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ -s "$out" ]; then echo "have  $out"; return; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url" || { echo "FAILED $out ($url)" >&2; rm -f "$out"; }
}

# S16 -- Roofline (Williams, Waterman, Patterson). The ACM DOI is paywalled;
# these two free copies are the CACM article and the longer tech report.
get S16-roofline-cacm-2009.pdf \
    'https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf'
get S16-roofline-ucb-eecs-2008-134.pdf \
    'https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf'

# S18 -- Agner Fog. Manual 3 is the one S8 points at; manual 1 is the C++ one.
get S18-agner-fog-optimizing_cpp.pdf   'https://www.agner.org/optimize/optimizing_cpp.pdf'
get S18-agner-fog-microarchitecture.pdf 'https://www.agner.org/optimize/microarchitecture.pdf'

# S21 -- Shi, on why Amdahl and Gustafson are the same law.
get S21-shi-1996-amdahl-gustafson.pdf \
    "https://cgvr.cs.uni-bremen.de/teaching/mpar_literatur/Reevaluating%20Amdahl's%20Law%20and%20Gustafson's%20Law.pdf"

# S22 -- Saad, Iterative Methods for Sparse Linear Systems, 2nd ed.
get S22-saad-iterative-methods-2nd.pdf \
    'https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf'

# S26 -- Matsumoto & Nishimura, Mersenne Twister (author-hosted).
get S26-matsumoto-nishimura-1998-mt.pdf \
    'http://www.math.sci.hiroshima-u.ac.jp/m-mat/MT/ARTICLES/mt.pdf'

# S31 -- Goto & van de Geijn, Anatomy of High-Performance Matrix Multiplication.
get S31-goto-vandegeijn-anatomy.pdf \
    'https://www.cs.utexas.edu/users/flame/pubs/GotoTOMS_final.pdf'

# S32 -- Shewchuk, Delaunay refinement.
get S32-shewchuk-delaunay-refinement.pdf \
    'https://people.eecs.berkeley.edu/~jrs/papers/2dj.pdf'

# S33 -- Gmsh paper (preprint).
get S33-gmsh-paper-preprint.pdf \
    'https://gmsh.info/doc/preprints/gmsh_paper_preprint.pdf'

# S38 -- AddressSanitizer, USENIX ATC 2012.
get S38-addresssanitizer-atc12.pdf \
    'https://www.usenix.org/system/files/conference/atc12/atc12-final39.pdf'

# S27 -- Marsaglia 1968 is HTML-only on PubMed Central; fetch the page.
get S27-marsaglia-1968-planes.html 'https://pmc.ncbi.nlm.nih.gov/articles/PMC285899/'

echo
echo "Paywalled and therefore not fetchable (open the DOI in a browser):"
echo "  S19 Amdahl 1967          https://doi.org/10.1145/1465482.1465560"
echo "  S20 Gustafson 1988       https://doi.org/10.1145/42411.42415"
echo "  S23 LeVeque 2007         https://doi.org/10.1137/1.9780898717839"
echo "  S24 Lax & Richtmyer 1956 https://doi.org/10.1002/cpa.3160090206"
echo "      Courant/Friedrichs/Lewy 1928 https://doi.org/10.1007/BF01448839"
echo "  S25 Fornberg 1988        https://doi.org/10.1090/S0025-5718-1988-0935077-0"
echo "  S28 Park & Miller 1988   https://doi.org/10.1145/63039.63042"
echo "  S29 Hull & Dobell 1962   https://doi.org/10.1137/1004061"
echo
echo "S8, the lecturer's own book (LGPL-2.1), is a repository, not a PDF:"
echo "  git clone https://github.com/JSchoeberl/IntroSC"
echo
echo "Already committed under vendor/ (do not re-download):"
shasum -a 256 vendor/* 2>/dev/null || true
