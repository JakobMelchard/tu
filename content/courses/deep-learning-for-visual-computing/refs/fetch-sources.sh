#!/usr/bin/env bash
# Download the freely available documents cited in SOURCES.md into ./cite-only
# (git-ignored). None carries a licence that allows redistribution (arXiv
# non-exclusive licence, unlicensed GitHub files, student uploads), so they are
# fetched for personal study only and never committed. See README.md.
#
# VoWi (S7, S8) sits behind a proof-of-work bot gate: curl gets an HTML page.
# Those fetches are expected to fail; the script prints the URLs to open in a
# browser. TUWEL is never fetched.
set -uo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
MANUAL=()

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ -s "$out" ]; then echo "have  $out"; return 0; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url" || true
    if [ ! -s "$out" ] || ! head -c 5 "$out" | grep -q '%PDF'; then
        rm -f "$out"; MANUAL+=("$url"); echo "      -> not a PDF, save by hand"
    fi
}

arxiv() {  # arxiv <S-id> <arXiv id> <short name>
    get "$1-$3-$2.pdf" "https://arxiv.org/pdf/$2"
}

echo "== S9: the 2016W course material (Pramerdorfer, GitHub cpra/dlvc2016, no licence) =="
R=https://raw.githubusercontent.com/cpra/dlvc2016/master
get S9-exam-questions-2017.pdf "$R/exam-questions.pdf"
for i in $(seq 1 11); do get "S9-lecture$i-2016W.pdf" "$R/lectures/lecture$i.pdf"; done

echo "== S7, S8: VoWi question catalogues (bot gate, expected to fail) =="
V=https://vowi.fsinf.at/images
get S7-dlvc-2022S-questions.pdf "$V/5/57/TU_Wien-Deep_Learning_for_Visual_Computing_VU_%28Kampel%29_-_DLVC_2022S_-_Questions.pdf"
get S8-dl4vc-answers-2020-06-23.pdf "$V/a/af/TU_Wien-Deep_Learning_for_Visual_Computing_VU_%28Kampel%29_-_DL4VC_Answers_Questions_2020-06-23.pdf"

echo "== Papers =="
arxiv S13 1603.07285 conv-arithmetic
get  S14-lecun-1998-lenet.pdf 'http://yann.lecun.com/exdb/publis/pdf/lecun-98.pdf'
get  S15-krizhevsky-2012-alexnet.pdf 'https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf'
arxiv S16 1409.1556 vgg
arxiv S16 1409.4842 googlenet
arxiv S16 1704.04861 mobilenets
arxiv S17 1512.03385 resnet
arxiv S18 1502.03167 batchnorm
get  S19-glorot-bengio-2010.pdf 'https://proceedings.mlr.press/v9/glorot10a/glorot10a.pdf'
arxiv S19 1502.01852 he-init
arxiv S20 1412.6980 adam
get  S21-srivastava-2014-dropout.pdf 'https://www.jmlr.org/papers/volume15/srivastava14a/srivastava14a.pdf'
arxiv S22 1311.2524 rcnn
arxiv S22 1504.08083 fast-rcnn
arxiv S22 1506.01497 faster-rcnn
arxiv S23 1506.02640 yolo
arxiv S23 1804.02767 yolov3
arxiv S24 1612.03144 fpn
arxiv S24 1708.02002 focal-loss
arxiv S25 1405.0312 coco
arxiv S26 1411.4038 fcn
arxiv S26 1505.04597 unet
arxiv S26 1606.04797 vnet-dice
arxiv S26 1703.06870 mask-rcnn
arxiv S27 1312.6114 vae
arxiv S28 1406.2661 gan
arxiv S28 1611.07004 pix2pix
arxiv S28 1703.10593 cyclegan
arxiv S29 2006.11239 ddpm
arxiv S30 1612.00593 pointnet
arxiv S30 1706.02413 pointnet2
arxiv S31 1806.01759 mccnn
arxiv S32 1809.05910 meshcnn
arxiv S33 2003.08934 nerf
arxiv S34 1610.02391 gradcam
arxiv S34 1810.03292 sanity-checks
arxiv S35 1710.09412 mixup
arxiv S35 1904.11486 shift-invariance
arxiv S36 1810.03993 model-cards
arxiv S37 1610.02413 equal-opportunity
get  S38-buolamwini-gebru-2018.pdf 'https://proceedings.mlr.press/v81/buolamwini18a/buolamwini18a.pdf'
arxiv S41 2010.11929 vit

echo
echo "== Not fetched by this script =="
cat <<'NOTE'
  S11 Goodfellow et al.: HTML only by contract, read at https://www.deeplearningbook.org/
  S12 Drori: book; selected chapters at https://www.thescienceofdeeplearning.org/
  S42 Szeliski: free PDF behind a form at https://szeliski.org/Book/ (personal use, no reposting)
  S39/S40 AI Act: EUR-Lex HTML, https://eur-lex.europa.eu/eli/reg/2024/1689/oj
  TUWEL: login required, not ours to copy. Never fetched.
NOTE

if [ "${#MANUAL[@]}" -gt 0 ]; then
    echo; echo "Not fetched (open in a browser and save into cite-only/ by hand):"
    printf '  %s\n' "${MANUAL[@]}"
fi
echo; echo "cite-only/ holds $(ls cite-only | wc -l | tr -d ' ') files"
