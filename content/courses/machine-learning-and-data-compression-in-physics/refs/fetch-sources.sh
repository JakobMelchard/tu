#!/usr/bin/env bash
# Download the free arXiv PDFs cited in SOURCES.md into ./cite-only (git-ignored).
#
# Licences (as shown on the arXiv abstract pages, 2026-09-28): most are arXiv's
# "non-exclusive distribution" licence, which grants arXiv, not us, the right to
# redistribute -> personal use, cite only, never commit. A few are permissive
# (S13 CC BY-SA 4.0, S16 CC0, S29 CC0, S34 CC BY 4.0) and could be vendored with
# their licence notice; they are fetched too, to keep the policy uniform.
#
# Never touches TUWEL or TISS.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <S-id> <arXiv id> <short name>
    local out="cite-only/$1-$3.pdf"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "https://arxiv.org/pdf/$2"
    sleep 1   # be polite to arXiv
}

get S10 1702.03054 shinaoka-2017-ir-basis
get S11 1807.05237 chikano-2019-irbasis
get S12 1908.07575 li-2020-sparse-sampling
get S13 2206.11762 wallerberger-2023-sparse-ir
get S15 1909.07519 shinaoka-2020-two-particle-sparse-sampling
get S16 2210.12984 shinaoka-2023-quantics-tensor-trains
get S17 1803.08823 mehta-2019-high-bias-low-variance
get S18 0909.4061  halko-martinsson-tropp-2011-randomized
get S21 1312.6114  kingma-welling-2014-vae
get S22 1703.02435 wetzel-2017-pca-to-vae-ising
get S23 1605.01735 carrasquilla-melko-2017-phases
get S24 1306.2164  orus-2014-tensor-networks
get S25 1008.3477  schollwoeck-2011-dmrg-mps
get S28 2105.11211 kaufmann-held-ana-cont
get S29 1806.03841 yoon-sim-han-2018-ml-continuation
get S32 2303.11819 ritter-2024-quantics-tci
get S33 1611.01704 balle-2017-end-to-end-compression
get S34 2410.22975 rohshap-2025-parquet-qtt

echo
echo "Not on arXiv (cite only, see SOURCES.md): S19 Eckart-Young 1936, S20 Onsager 1944 /"
echo "Yang 1952, S26 Oseledets 2011, S27 Jarrell-Gubernatis 1996, S30 Hansen 2010,"
echo "S31 Baldi-Hornik 1989, S36 Cover-Thomas 2006."
