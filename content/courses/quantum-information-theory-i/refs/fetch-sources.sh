#!/usr/bin/env bash
# Download the free literature named on TISS for 141.282 into ./cite-only
# (git-ignored). See SOURCES.md and README.md for licences.
#
#   S5  Preskill, ch. 1-6 (1998), Leiden mirror linked from TISS     no licence: cite only
#   S6  Preskill, ch. 2 (2015)                                        no licence: cite only
#   S7  Preskill, ch. 3 (2015)                                        no licence: cite only
#   S8  Preskill, ch. 4 (2001)                                        no licence: cite only
#   S9  Preskill, ch. 10 (2025)                                       no licence: cite only
#   S10 Jozsa, QIC lecture notes (Jan 2019), linked from TISS         no licence: cite only
#   S11 Wilde, arXiv:1106.1445v8                                      CC BY-NC-SA: not vendored
#   S25 Mermin, RMP 65, 803 (1993), arXiv:1802.10119                  arXiv licence: cite only
#
# Nothing here touches TUWEL. Nielsen & Chuang (S13) and Bertlmann & Friis
# (S14) are not free and are not downloaded.
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
}

# Preskill moved from theory.caltech.edu/~preskill to preskill.caltech.edu
# (old URLs 404 as of 2026-09-28). Index: https://www.preskill.caltech.edu/ph229/
get S5-preskill-ch1-6-1998-leiden.pdf  'https://www.lorentz.leidenuniv.nl/quantumcomputers/literature/preskill_1_to_6.pdf'
get S6-preskill-ch2-2015.pdf           'http://www.preskill.caltech.edu/ph219/chap2_15.pdf'
get S7-preskill-ch3-2015.pdf           'http://www.preskill.caltech.edu/ph219/chap3_15.pdf'
get S8-preskill-ch4-2001.pdf           'http://www.preskill.caltech.edu/ph229/notes/chap4_01.pdf'
get S9-preskill-ch10-2025.pdf          'http://www.preskill.caltech.edu/ph219/chap10_6A_2025.pdf'
get S10-jozsa-qic-2019.pdf             'https://www.qi.damtp.cam.ac.uk/files/PartIIIQC/Part%202%20QIC%20lecturenotes.pdf'
get S11-wilde-1106.1445v8.pdf          'https://arxiv.org/pdf/1106.1445v8'
get S25-mermin-rmp-1993.pdf            'https://arxiv.org/pdf/1802.10119'

echo
echo "expected checksums as retrieved 2026-09-28:"
cat <<'SUMS'
905ab1b7f99835d823e1ed4513b243353bcb5ba5980be33ddbb5e5d81f97ca26  S5   (1539537 bytes, 321 pp.)
709a8a52cfbc9afb65ed6fb9dfbd9b59afaa8eac21167cbaf37a43b2555b0d34  S6   (376827 bytes, 53 pp.)
34141b215c144c0cc8fd86e9a4ba289e1e8eb73b9dc6cf1dccdf594d4f57e6ad  S7   (433557 bytes, 65 pp.)
f534889a223492ca32873fe20bac3214cf0b2e7d35e0a8d26f44fa10503d0546  S8   (422808 bytes, 70 pp.)
4cfb665bcc4a3c6a7658939ea36b9919bd354540a5a2a34e4d2611969f1ec16b  S9   (659825 bytes, 103 pp.)
f783096f8614cbe2b024e5620de6705e369a8d181de92ea4cdde2556c60b3ce4  S10  (539058 bytes, 88 pp.)
2f5f5feea82ed99dbbbe0d8a79f1c371cda690ab70dbfc929bbda7fb1ae1d6ee  S11  (8835985 bytes, 774 pp.)
196577d5166bc5689a9c95038c85ce594a824556d3afcb1cba31cce1f5463d36  S25
SUMS
echo
echo "yours:"
shasum -a 256 cite-only/*.pdf 2>/dev/null || true
echo
echo "A differing checksum is not an error: Preskill revises chapters in place."
echo "Record the new one and re-check the locators in SOURCES.md."
