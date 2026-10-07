#!/usr/bin/env bash
# Download the public course material and the free papers the notes cite into
# ./cite-only/ (git-ignored). Nothing here is committed: none of it is
# permissively licensed. See SOURCES.md for every entry and its licence.
#
#   Hofstaetter AIR 2022 slides, captions, exercise text  [S4-S15, S17]  GPL-3.0 (repo licence)
#   2023 exercise template text                           [S18]          no licence file
#   BM25 review (author PDF), GloVe, Conv-KNRM, IIR book  [S23, S31, S34, S22]  personal use
#   arXiv papers                                          [S29-S71]      arXiv licences vary
#
# Never TUWEL. Never VoWi (bot-protected; do not circumvent).
#
#   ./fetch-sources.sh           download what is missing
#   ./fetch-sources.sh --check   only check that every URL answers (HEAD), download nothing
set -euo pipefail

cd "$(dirname "$0")"
CHECK=0
[ "${1-}" = "--check" ] && CHECK=1
OUT=cite-only
mkdir -p "$OUT"
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
fail=0

get() {  # get <file name> <url>
    local out="$OUT/$1" url="$2"
    if [ "$CHECK" = 1 ]; then
        code=$(curl -sIL -A "$UA" -o /dev/null -w '%{http_code}' "$url" || true)
        printf '%s %s\n' "$code" "$1"
        [ "$code" = 200 ] || fail=1
        return
    fi
    if [ -s "$out" ]; then echo "have  $out"; return; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url" || { echo "FAILED $url"; rm -f "$out"; fail=1; }
}

RAW=https://raw.githubusercontent.com/sebastian-hofstaetter/teaching/master/advanced-information-retrieval
get S4-teaching-README.md https://raw.githubusercontent.com/sebastian-hofstaetter/teaching/master/README.md
get S4-teaching-LICENSE.txt https://raw.githubusercontent.com/sebastian-hofstaetter/teaching/master/LICENSE
lectures=(
  "S5|0|Lecture 0 - Course Introduction.pdf"
  "S6|1|Lecture 1 - Crash Course - Fundamentals.pdf"
  "S7|2|Lecture 2 - Crash Course - Evaluation.pdf"
  "S8|3|Lecture 3 - Crash Course - Test Collections.pdf"
  "S9|4|Lecture 4 - Word Representation Learning.pdf"
  "S10|5|Lecture 5 - Sequence modelling in NLP.pdf"
  "S11|6|Lecture 6 - Transformer and BERT Pre-training.pdf"
  "S12|7|Lecture 7 - Introduction to Neural Re-Ranking.pdf"
  "S13|8|Lecture 8 - Transformer Contextualized Re-Ranking.pdf"
  "S14|9|Lecture 9 - Domain Specific Applications.pdf"
  "S15|10|Lecture 10 - Dense Retrieval and Knowledge Distillation.pdf"
)
for l in "${lectures[@]}"; do
    IFS='|' read -r sid n name <<<"$l"
    enc=${name// /%20}
    get "$sid-lecture-$n.pdf" "$RAW/$enc"
    get "$sid-lecture-$n-captions.md" "$RAW/Lecture%20$n%20-%20Closed%20Captions.md"
done
get S17-exercise-2022.md "$RAW/neural-ir-exercise-2022/Assignment.md"
get S17-exercise-2021.md "$RAW/neural-ir-exercise-2021/Assignment.md"
get S18-exercise-2023.md https://raw.githubusercontent.com/tuwien-information-retrieval/air-23-template/HEAD/assignment_2.md

get S22-manning-iir.pdf https://nlp.stanford.edu/IR-book/pdf/irbookonlinereading.pdf
get S23-robertson-zaragoza-bm25.pdf https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf
get S31-glove.pdf https://nlp.stanford.edu/pubs/glove.pdf
get S34-conv-knrm.pdf http://www.cs.cmu.edu/~zhuyund/papers/WSDM_2018_Dai.pdf

arxiv=(
  S29:1301.3781 S30:1310.4546 S32:1810.04805 S33:1706.06613 S35:1901.04085 S36:2002.01854
  S37:2004.04906 S38:2004.12832 S39:2112.01488 S40:2010.02666 S41:2104.06967 S42:2007.00808
  S43:1702.08734 S44:1611.09268 S45:2003.07820 S46:2102.07662 S47:1606.05250 S48:2010.06467
  S50:1508.07909 S51:1904.12683 S52:2203.13088 S53:2405.07767 S58:2104.08663 S59:1607.04606
  S60:1808.06226 S61:1609.08144 S62:1408.5882 S63:1409.0473 S64:1706.03762 S65:1602.06359
  S66:2004.14255 S67:1603.09320 S68:1910.01108 S69:1503.02531 S70:1910.14424 S71:2105.04021
)
for a in "${arxiv[@]}"; do
    get "${a%%:*}-arxiv-${a#*:}.pdf" "https://arxiv.org/pdf/${a#*:}"
    [ "$CHECK" = 1 ] || sleep 1          # be polite to arxiv.org
done

if [ "$CHECK" = 0 ]; then
    echo
    echo "sha256 of the slide PDFs as retrieved 2026-09-28 (a difference means the author replaced a file):"
    cat <<'EOF'
5e03e94797edc2a58105060ccf17755d2d21d496f5e441fe3f7e56a1843c4847  S5-lecture-0.pdf
b3cd0eece1c4be4e411ec7f564e19a1ad9a58142791ebbb32378745cf9237c62  S6-lecture-1.pdf
4eab2100dcc3a67aee63d9d4aa821405e9a84ba129570b7c07f50317772e9adb  S7-lecture-2.pdf
c0d7bda68c309c73c7dc57d854ed949e74387e50e30d4122bd97365a84ce3e9d  S8-lecture-3.pdf
ecd511aab1b3fab8ac7d205bc88e50e76c7261cbcc13ba767c6ec87f1955de58  S9-lecture-4.pdf
13d281a5da99cd62ad479ada19594ea7c47ebc10e39a8c303a035d7436010bb0  S10-lecture-5.pdf
0e65355af1784487b7fd16d65e5e81c04d17bbb4de1e971bd4a1002b4067478a  S11-lecture-6.pdf
f2a4d47fac946421dd933130d14431935cd04ffd11b42c8fc5c033f2b72fceb0  S12-lecture-7.pdf
822d3ccac245d8559b8025cf59ea966afded5092ed7b3ecec1b821ef114d39cf  S13-lecture-8.pdf
c97c2624daee143580a18a2658d82284283a51c6562ddf1262e7761b8481433c  S14-lecture-9.pdf
d10c2807d2818d79e62d6d19724ab9c66befc9b7cbf39c0f360e0f399be540ac  S15-lecture-10.pdf
11a9ef825dfd3fe50c8621273d02ea26b6f502b60379db9519d6c5c10de4fd25  S23-robertson-zaragoza-bm25.pdf
EOF
    echo "yours:"
    (cd "$OUT" && shasum -a 256 S5-lecture-0.pdf S6-lecture-1.pdf S7-lecture-2.pdf S8-lecture-3.pdf \
        S9-lecture-4.pdf S10-lecture-5.pdf S11-lecture-6.pdf S12-lecture-7.pdf S13-lecture-8.pdf \
        S14-lecture-9.pdf S15-lecture-10.pdf S23-robertson-zaragoza-bm25.pdf 2>/dev/null) || true
fi
exit "$fail"
