#!/usr/bin/env bash
# Download the cite-only PDFs listed in SOURCES.md into ./vendor (git-ignored).
# None of them carries a redistribution licence, so they are fetched for
# personal study and never committed. See README.md.
#
# VoWi (S12-S16, S43) sits behind an Anubis proof-of-work gate: plain HTTP
# clients get an HTML challenge page, not the file. Those fetches are expected
# to fail; the script says so and prints the URLs to open in a browser.
set -uo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
MANUAL=()

get() {  # get <name> <url> [referer]
    local out="vendor/$1" url="$2" ref="${3-}"
    if [ -s "$out" ]; then
        echo "have  $out"
        return 0
    fi
    echo "fetch $out"
    if [ -n "$ref" ]; then
        curl -fsSL -A "$UA" -e "$ref" -o "$out" "$url" || true
    else
        curl -fsSL -A "$UA" -o "$out" "$url" || true
    fi
    # A bot-gate challenge comes back as small HTML; drop it and remember the URL.
    if [ ! -s "$out" ] || ! head -c 5 "$out" | grep -q '%PDF'; then
        case "$out" in
            *.pdf) rm -f "$out"; MANUAL+=("$url"); echo "      -> blocked, save by hand" ;;
            *)     [ -s "$out" ] || { rm -f "$out"; MANUAL+=("$url"); } ;;
        esac
    fi
}

echo "== VoWi: the exam archive (S12-S16, S43) — the course's real syllabus =="
V=https://vowi.fsinf.at/images
R=https://vowi.fsinf.at/
get S12-questions-previous-exams-answered-2024S.pdf \
    "$V/6/6b/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_Questions_previousExams_answered2024S.pdf" "$R"
get S13-formelsammlung-ml.pdf \
    "$V/6/65/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Formlen_ML.pdf" "$R"
get S14-practical-howtos.pdf \
    "$V/6/6b/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_PracticalHowTos.pdf" "$R"
get S15-exercise1-classification-2021S.pdf \
    "$V/3/32/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Exercise1_ML_2021S.pdf" "$R"
get S16-exam-2026-06-23-part2.1-192183.pdf \
    "$V/2/22/TU_Wien-Machine_Learning_VU_%28Musliu%29_-_Exam_2026-06-23_Part2.1.pdf" "$R"
get S43-fragenkatalog-2019S.docx \
    "$V/0/0d/TU_Wien-Machine_Learning_VU_%28Mayer%2C_Musliu%29_-_Fragenkatalog_2019S.docx" "$R"

echo
echo "== Books the course works from (free author/publisher downloads) =="
# S21 - Sutton & Barto. The one book the lecture demonstrably teaches from.
get S21-sutton-barto-rl-2nd.pdf 'http://incompleteideas.net/book/RLbook2020.pdf'

echo
echo "== Free primary papers =="
get S33-breiman-bagging-1996.pdf   'https://www.stat.berkeley.edu/~breiman/bagging.pdf'
get S33-breiman-random-forests-2001.pdf 'https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf'
get S36-demsar-statistical-comparisons-2006.pdf 'https://www.jmlr.org/papers/volume7/demsar06a/demsar06a.pdf'
get S37-bergstra-bengio-random-search-2012.pdf  'https://www.jmlr.org/papers/volume13/bergstra12a/bergstra12a.pdf'
get S39-goodfellow-fgsm-2015.pdf   'https://arxiv.org/pdf/1412.6572'
get S40-lecun-lenet-1998.pdf       'http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf'
get S40-he-resnet-2016.pdf         'https://arxiv.org/pdf/1512.03385'
get S41-ester-dbscan-1996.pdf      'https://cdn.aaai.org/KDD/1996/KDD96-037.pdf'

echo
echo "== Not fetched by this script =="
cat <<'EOF'
  S23 ESL, S24 PRML, S26 Deep Learning, S28 ISLR - free but behind a landing
      page or a per-chapter HTML split; get them from
        https://hastie.su.domains/ElemStatLearn/
        https://www.microsoft.com/en-us/research/publication/pattern-recognition-machine-learning/
        https://www.deeplearningbook.org/
        https://www.statlearning.com/
  S17 the 73 MB re-upload of S21 on VoWi - use S21 instead.
  TUWEL - login required, and not ours to copy. Never fetched.
EOF

if [ "${#MANUAL[@]}" -gt 0 ]; then
    echo
    echo "Blocked (open in a browser and save into vendor/ by hand):"
    printf '  %s\n' "${MANUAL[@]}"
fi

echo
echo "vendor/ now holds:"
ls -la vendor/ 2>/dev/null || true
