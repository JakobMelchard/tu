#!/usr/bin/env bash
# Fetch the cite-only sources of SOURCES.md into ./cite-only (git-ignored).
# None of these may be redistributed from this repo:
#   - the lecturers' public GitHub material (S3-S6) carries NO licence file,
#     so it is all rights reserved: readable, cloneable for study, not copyable here;
#   - N4950 (S8) is an ISO working draft;
#   - the cppreference archive (S9) is CC BY-SA 3.0 / GFDL (share-alike, not vendored);
#   - the C++ Core Guidelines (S10) are licensed "for your personal or internal
#     business use only".
# Nothing from TUWEL. Nothing needs a login. Re-running skips what is present.
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

clone() {  # clone <dir> <url> <commit recorded in SOURCES.md>
    local out="cite-only/$1" url="$2" want="$3"
    if [ -d "$out/.git" ]; then echo "have  $out"; else
        echo "clone $out"
        git clone -q "$url" "$out" || { echo "FAILED $out ($url)" >&2; return; }
    fi
    local head; head=$(git -C "$out" rev-parse --short=7 HEAD)
    [ "$head" = "$want" ] || echo "NOTE  $out is at $head, SOURCES.md recorded $want: re-check the map" >&2
}

# S3 -- 2021W lecture items (item 000 = organisation and grading), the most recent public offering
clone S3-cppitems-2021W https://github.com/cppitems/cppitems.git ad07e0b
# S4 -- 2021W exercise hand-outs: ex0, ex1.1-1.3, ex2.1-2.3, ex3.1-3.3
clone S4-ex0   https://github.com/cppitems/ex0.git   41dec82
clone S4-ex1.1 https://github.com/cppitems/ex1.1.git 31233ac
clone S4-ex1.2 https://github.com/cppitems/ex1.2.git 7128af5
clone S4-ex1.3 https://github.com/cppitems/ex1.3.git e97d881
clone S4-ex2.1 https://github.com/cppitems/ex2.1.git e7d806f
clone S4-ex2.2 https://github.com/cppitems/ex2.2.git 8728241
clone S4-ex2.3 https://github.com/cppitems/ex2.3.git 72ffdc5
clone S4-ex3.1 https://github.com/cppitems/ex3.1.git 2f9aeee
clone S4-ex3.2 https://github.com/cppitems/ex3.2.git 38a6c5e
clone S4-ex3.3 https://github.com/cppitems/ex3.3.git 195e310
# S5 -- 2020W items (Manstetten's personal copy)
clone S5-cppitems2020 https://github.com/manstetten/cppitems2020.git 204b904

# S8 -- C++23 working draft N4950 (2023-05-10)
get S8-n4950.pdf 'https://open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4950.pdf'
# S9 -- cppreference offline archive (HTML book), release v20250209
get S9-cppreference-html-book-20250209.tar.xz \
    'https://github.com/PeterFeicht/cppreference-doc/releases/download/v20250209/html-book-20250209.tar.xz'
if [ -s cite-only/S9-cppreference-html-book-20250209.tar.xz ] && [ ! -d cite-only/S9-cppreference ]; then
    mkdir -p cite-only/S9-cppreference && tar -xJf cite-only/S9-cppreference-html-book-20250209.tar.xz -C cite-only/S9-cppreference
fi
# S10 -- C++ Core Guidelines (single Markdown file)
get S10-CppCoreGuidelines.md 'https://raw.githubusercontent.com/isocpp/CppCoreGuidelines/master/CppCoreGuidelines.md'

echo
echo "Not free, cite only (buy or borrow):"
echo "  S11 Stroustrup, A Tour of C++, 3rd ed., Addison-Wesley 2022, ISBN 978-0-13-681648-5"
echo "  S16 Meyers, Effective Modern C++, O'Reilly 2014, ISBN 978-1-491-90399-5"
echo "Not fetched: VoWi (S7) sits behind a bot check; open it in a browser."
echo "Never fetched: TUWEL (needs a login)."
