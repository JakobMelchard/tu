#!/usr/bin/env bash
# Download the cite-only PDFs listed in SOURCES.md into ./vendor (git-ignored).
# These files carry no redistribution licence, so they are fetched for personal
# study and never committed. See README.md.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url> [referer]
    local out="vendor/$1" url="$2" ref="${3-}"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    if [ -n "$ref" ]; then
        curl -fsSL -A "$UA" -e "$ref" -o "$out" "$url"
    else
        curl -fsSL -A "$UA" -o "$out" "$url"
    fi
}

# S4 — the course's own lecture notes. Everything else is optional.
get S4-melenk-faustmann-numerical-computation-ws2324.pdf \
    'https://www.tuwien.at/index.php?eID=dumpFile&t=f&f=202609&token=57cfb2dfeef43abeefd966ce28dc8d35e3bff56e'

# S17, S18 — free companions for the CG / GMRES chapter.
get S17-shewchuk-painless-conjugate-gradient.pdf \
    'https://www.cs.cmu.edu/~quake-papers/painless-conjugate-gradient.pdf'
get S18-saad-iterative-methods-2nd.pdf \
    'https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf'

# S10, S11 — past tests on VoWi. The wiki runs a proof-of-work bot gate, so
# these usually need a real browser; if curl returns an HTML page instead of a
# PDF, open the URL in a browser and save it into vendor/ by hand.
V=https://vowi.fsinf.at/images
get S10-faustmann-test1-2022-12-02.pdf "$V/8/87/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test1_02.12.2022.pdf" https://vowi.fsinf.at/ || true
get S10-faustmann-test2-2023-01-26.pdf "$V/8/81/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test2_26.01.2023.pdf" https://vowi.fsinf.at/ || true
get S10-faustmann-test3-2023-02-24.pdf "$V/3/39/TU_Wien-Computernumerik_VU_%28Faustmann%29_-_Test3_24.02.2023.pdf" https://vowi.fsinf.at/ || true
get S11-sturm-test1-2024-11-22.pdf     "$V/e/e9/TU_Wien-Computernumerik_VU_%28Sturm%29_-_Computernumerik_Test_1_2024-11-22.pdf" https://vowi.fsinf.at/ || true
get S11-sturm-test2-2025-01-22.pdf     "$V/9/97/TU_Wien-Computernumerik_VU_%28Sturm%29_-_Computernumerik_Test_2_2025-02-22.pdf" https://vowi.fsinf.at/ || true

echo
echo "expected checksum of the lecture notes:"
echo "292bafb0ab46cb47a6ab4374dba1ae60ffa3a2dba50f660510b883da687d7d61"
shasum -a 256 vendor/S4-melenk-faustmann-numerical-computation-ws2324.pdf 2>/dev/null || true
