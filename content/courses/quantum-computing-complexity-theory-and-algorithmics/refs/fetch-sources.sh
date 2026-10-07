#!/usr/bin/env bash
# Download the cite-only PDFs listed in SOURCES.md into ./vendor (git-ignored).
# None of these files carries a redistribution licence, so they are fetched for
# personal study and never committed.  See README.md.
#
#   ./fetch-sources.sh            everything below
#   ./fetch-sources.sh --core     only the three that matter most (S31, S14, S16)
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
CORE_ONLY=0
[ "${1-}" = "--core" ] && CORE_ONLY=1

get() {  # get <name> <url> [referer]
    local out="vendor/$1" url="$2" ref="${3-}"
    if [ -s "$out" ]; then
        echo "have  $out"
        return 0
    fi
    echo "fetch $out"
    if [ -n "$ref" ]; then
        curl -fsSL -A "$UA" -e "$ref" -o "$out" "$url" || { echo "  !! failed: $1"; rm -f "$out"; return 0; }
    else
        curl -fsSL -A "$UA" -o "$out" "$url" || { echo "  !! failed: $1"; rm -f "$out"; return 0; }
    fi
}

# ---------------------------------------------------------------- S31
# de Wolf, Quantum Computing: Lecture Notes.  The closest thing to a script for
# the C-series and for B06.  arXiv non-exclusive licence: personal use only.
get S31-dewolf-quantum-computing-lecture-notes.pdf \
    'https://arxiv.org/pdf/1907.09415'

# ---------------------------------------------------------------- S14
# Pichler's own Complexity Theory slides.  Only cc01 and cc02 are public;
# cc03..cc16 return 404 (checked 2026-09-22).
P=https://www.dbai.tuwien.ac.at/staff/pichler/complexity
get S14-pichler-complexity-cc01-general.pdf "$P/slides/cc01.pdf"
get S14-pichler-complexity-cc02-fundamentals.pdf "$P/slides/cc02.pdf"

# ---------------------------------------------------------------- S16, S17, S18, S19
# Egly's exercise sheets, programming exercises and exam protocols for 192.036.
# VoWi runs an Anubis proof-of-work bot gate, so curl usually gets an HTML
# challenge page instead of the PDF.  If a file below is missing or tiny, open
# the URL in a real browser and save it into vendor/ by hand.
V=https://vowi.fsinf.at/images
E='TU_Wien-Einf%C3%BChrung_in_Quantencomputing_VU_%28Egly%29'
get S16-egly-exercise-sheet-1.pdf "$V/c/cc/${E}_-_Exercise_Sheet_1.pdf" https://vowi.fsinf.at/
get S16-egly-exercise-sheet-2.pdf "$V/8/8d/${E}_-_Exercise_Sheet_2.pdf" https://vowi.fsinf.at/
get S16-egly-exercise-sheet-3.pdf "$V/6/64/${E}_-_Exercise_Sheet_3.pdf" https://vowi.fsinf.at/
get S16-egly-exercise-sheet-4.pdf "$V/f/f9/${E}_-_Exercise_Sheet_4.pdf" https://vowi.fsinf.at/

if [ "$CORE_ONLY" = 0 ]; then
    get S17-egly-programming-exercise-1.pdf "$V/5/52/${E}_-_Programming_exercise_sheet_1.pdf" https://vowi.fsinf.at/
    get S17-egly-programming-exercise-2.pdf "$V/9/9c/${E}_-_Programming_exercise_sheet_2.pdf" https://vowi.fsinf.at/
    get S17-egly-programming-exercise-3.pdf "$V/3/34/${E}_-_Programming_exercise_sheet_3.pdf" https://vowi.fsinf.at/
    get S18-egly-exercise-test-protocol.pdf "$V/d/da/${E}_-_Ged%C3%A4chtnisprotokoll_exercise_test_qci.pdf" https://vowi.fsinf.at/
    get S19-egly-oral-exam-protocol.txt "$V/c/c5/${E}_-_Ged%C3%A4chtnisprotokoll_oral_exam_qci.txt" https://vowi.fsinf.at/

    # ------------------------------------------------------------ S20
    get S20-waibel-quantum-computing-summary-ws2023.pdf \
        "$V/2/25/TU_Wien-Quantum_Computing_VU_%28Egly%29_-_Summary_QC_WS2023.pdf" https://vowi.fsinf.at/

    # ------------------------------------------------------------ S23
    K='TU_Wien-Komplexit%C3%A4tstheorie_VU_%28Pichler%29'
    get S23-pichler-komplexitaetstheorie-exam-ws2021.pdf "$V/f/f4/${K}_-_Exam-ws2021.pdf" https://vowi.fsinf.at/
    get S23-pichler-einstufungstest-loesungen-2023.pdf \
        "$V/7/7a/${K}_-_Folien_Einstufungstest_L%C3%B6sungen%281%292023.pdf" https://vowi.fsinf.at/

    # ------------------------------------------------------------ S22
    HQ='TU_Wien-Hybrid_Quantum_-_Classical_Systems_VU_%28De_Maio%29'
    get S22-hqcs-first-assignment-2024.pdf "$V/6/65/${HQ}_-_HQCS_First_Assignment_2024_final.pdf" https://vowi.fsinf.at/
    get S22-hqcs-second-assignment-2024.pdf "$V/e/ea/${HQ}_-_HQCS_Second_assignment_2024.pdf" https://vowi.fsinf.at/
    get S22-hqcs-group-assignment-2024.pdf "$V/6/64/${HQ}_-_HQCS_2024_Group_Assignment.pdf" https://vowi.fsinf.at/

    # ------------------------------------------------------------ S14 reading list
    get S14-johnson1990-catalog.pdf "$P/johnson1990.pdf"
    get S14-vollmer1999.pdf "$P/vollmer1999.pdf"
    get S14-cook2003.pdf "$P/cook2003.pdf"
    get S14-dantsin-etal-2001.pdf "$P/dantsin-etal-2001.pdf"
    get S14-eiter1995.pdf "$P/eiter1995.pdf"
    get S14-hermann2007.pdf "$P/hermann2007.pdf"

    # ------------------------------------------------------------ primary papers (arXiv)
    get S37-bernstein-vazirani-quantum-complexity-theory.pdf 'https://arxiv.org/pdf/quant-ph/9701001' || true
    get S39-grover-1996.pdf 'https://arxiv.org/pdf/quant-ph/9605043'
    get S40-shor-1995.pdf 'https://arxiv.org/pdf/quant-ph/9508027'
    get S41-bbbv-1997.pdf 'https://arxiv.org/pdf/quant-ph/9701001'
    get S45-kitaev-1995.pdf 'https://arxiv.org/pdf/quant-ph/9511026'
    get S46-brassard-hoyer-mosca-tapp.pdf 'https://arxiv.org/pdf/quant-ph/0005055'
    get S47-bbht-1998.pdf 'https://arxiv.org/pdf/quant-ph/9605034'
    get S48-farhi-qaoa-2014.pdf 'https://arxiv.org/pdf/1411.4028'
    get S50-omalley-h2-2016.pdf 'https://arxiv.org/pdf/1512.06860'
    get S51-mcclean-barren-plateaus.pdf 'https://arxiv.org/pdf/1803.11173'
    get S52-cerezo-vqa-review.pdf 'https://arxiv.org/pdf/2012.09265'
    get S55-kempe-kitaev-regev-local-hamiltonian.pdf 'https://arxiv.org/pdf/quant-ph/0406180'
    get S58-gidney-ekera-2019.pdf 'https://arxiv.org/pdf/1905.09749'
    get S58-gidney-2025.pdf 'https://arxiv.org/pdf/2505.15917'
fi

echo
echo "in vendor/:"
ls -la vendor/ | tail -n +2
echo
echo "record your own checksums with:  shasum -a 256 vendor/* > vendor/SHA256SUMS"
