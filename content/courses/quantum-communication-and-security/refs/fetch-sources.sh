#!/usr/bin/env bash
# Download the free sources of 141.320 into ./cite-only (git-ignored, see .gitignore).
# Licences in SOURCES.md: S5 and S32 are CC BY 4.0, S13 CC BY-NC-SA 4.0; everything
# else is under the arXiv non-exclusive licence -> personal use, never commit.
# Nothing here touches TUWEL. Network is needed only when running this script.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <file name> <arXiv id>
    local out="cite-only/$1" url="https://arxiv.org/pdf/$2"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out  <- $url"
    curl -fsSL -A "$UA" -o "$out" "$url"
    sleep 3   # arXiv asks for slow automated access
}

# Core texts (the task list)
get S3-scarani-et-al-2009-security-of-practical-qkd.pdf          0802.4155
get S4-renner-2005-security-of-qkd-thesis.pdf                     quant-ph/0512258
get S5-tomamichel-leverrier-2017-self-contained-qkd-proof.pdf     1506.08458
get S6-bennett-brassard-1984-bb84-scan.pdf                        2003.06557
get S7-shor-preskill-2000-simple-proof-bb84.pdf                   quant-ph/0003004
get S8-lo-ma-chen-2005-decoy-state-qkd.pdf                        quant-ph/0411004
get S10-lo-curty-qi-2012-mdi-qkd.pdf                              1109.1473
get S12-renner-koenig-2005-privacy-amplification.pdf              quant-ph/0403133
get S13-wilde-classical-to-quantum-shannon-theory.pdf             1106.1445

# Used for numbers in src/ (optional but recommended)
get S9-ma-qi-zhao-lo-2005-practical-decoy-state.pdf               quant-ph/0503005
get S11-ma-razavi-2012-alternative-mdi-schemes.pdf                1204.4856
get S19-christandl-koenig-renner-2009-post-selection.pdf          0809.3019
get S32-andriolo-et-al-murta-2026-qkd-imperfections-review.pdf    2602.05057

# S6 also exists as the TCS 2014 reprint, doi:10.1016/j.tcs.2014.05.025; Elsevier
# blocks scripted downloads (HTTP 403 on 2026-09-28), so fetch it in a browser if wanted.

echo
echo "checksums of the copies read on 2026-09-28 (served by arxiv.org/pdf/<id>):"
cat <<'SUMS'
dd1e1948a272ee049e1777ee426c84fb001035c9482105c456227d89e2823c5a  S3   (1179575 bytes, 52 pp.)
8995cf32eabbb5db2b472c02186072821bb6110fc4a8e92bd5599533fdd8397b  S4   (1294285 bytes, 148 pp.)
5a547367a6a9a9cfdee87958058e0f27c82b3bbc5cfc21d8f74301e7f96d8fa7  S5   (1289429 bytes, 38 pp.)
751559e724770c6e28d424279c7b8761e436a57f26ec1dc030bb58c592d0a740  S9   (376867 bytes, 31 pp.)
352aba1e2019fea5bdf80c37842f05876c8d68f4be32eaa6b17e8a6e8b5eddbf  S10  (271146 bytes, 7 pp.)
d1093f0cae9f2e151dbed476d6ee4683c4f7b519ac9d87d7419cc255f6de8f4b  S11  (432673 bytes, 30 pp.)
3dfb069d67a67cf96bee06bc2125870796055ded7420acac5d73c4578b8a9fcd  S19  (140286 bytes, 4 pp.)
SUMS
echo
echo "yours:"
shasum -a 256 cite-only/*.pdf 2>/dev/null || true
echo
echo "A different checksum usually means a new arXiv version; re-check the locators in SOURCES.md."
