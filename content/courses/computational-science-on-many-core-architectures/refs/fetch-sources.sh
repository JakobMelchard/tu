#!/usr/bin/env bash
# Download the cite-only sources listed in SOURCES.md into ./cite-only
# (git-ignored) for personal study. They carry no redistribution licence, or
# are too large to commit, so they are never committed. The one vendored
# source (vendor/rupp-cpu-gpu-mic-comparison, CC BY 4.0) is NOT fetched here.
# Nothing from TUWEL: it needs a login and is not ours to copy.
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

# S4 -- Karl Rupp (the lecturer), VSC School tutorial 2015: the closest public
# match to this course's syllabus. Repository has no licence file.
get S4-rupp-vsc2015-many-core-architectures.pdf 'https://github.com/karlrupp/slides/raw/master/VSC2015.pdf'
for f in bottlenecks cuda gpus mics modeling-examples opencl primitives; do
    get "S4-rupp-vsc2015-src-$f.tex" "https://raw.githubusercontent.com/karlrupp/slides/master/VSC2015/slides/$f.tex"
done

# S10 -- Gustafson 1988, author-hosted copy.
get S10-gustafson-1988-reevaluating-amdahl.pdf 'http://www.johngustafson.net/pubs/pub13/amdahl.pdf'
# S11 -- Roofline, the long tech report (the CACM DOI is paywalled).
get S11-roofline-ucb-eecs-2008-134.pdf 'https://www2.eecs.berkeley.edu/Pubs/TechRpts/2008/EECS-2008-134.pdf'
# S15 -- CUDA C++ Programming Guide (release 13.4 when these notes were written).
get S15-cuda-c-programming-guide.pdf 'https://docs.nvidia.com/cuda/pdf/CUDA_C_Programming_Guide.pdf'
# S16 -- Harris, Optimizing Parallel Reduction in CUDA.
get S16-harris-reduction.pdf 'https://developer.download.nvidia.com/assets/cuda/files/reduction.pdf'
# S17 -- Blelloch, Prefix Sums and Their Applications (author copy).
get S17-blelloch-prefix-sums.pdf 'https://www.cs.cmu.edu/~guyb/papers/Ble93.pdf'
# S18 -- GPU Gems 3, chapter 39 (HTML).
get S18-gpugems3-ch39-scan.html 'https://developer.nvidia.com/gpugems/gpugems3/part-vi-gpu-computing/chapter-39-parallel-prefix-sum-scan-cuda'
# S20 -- SELL-C-sigma, arXiv preprint (arXiv non-exclusive licence).
get S20-kreutzer-sell-c-sigma-arxiv.pdf 'https://arxiv.org/pdf/1307.6209'
# S23 -- OpenACC 3.3 ("no part of this document may be reproduced").
get S23-openacc-3.3.pdf 'https://www.openacc.org/sites/default/files/inline-images/Specification/OpenACC-3.3-final.pdf'
# S24, S25 -- Khronos: use and reproduce the unmodified spec, no distribution grant.
get S24-opencl-3.0-api.pdf 'https://registry.khronos.org/OpenCL/specs/3.0-unified/pdf/OpenCL_API.pdf'
get S25-sycl-2020.pdf 'https://registry.khronos.org/SYCL/specs/sycl-2020/pdf/sycl-2020.pdf'
# S27 -- Kastner et al., Parallel Programming for FPGAs. CC BY 4.0, so it MAY be
# redistributed; fetched rather than committed only because it is 8 MB.
get S27-kastner-pp4fpgas.pdf 'https://arxiv.org/pdf/1805.03648'
# S30 -- AMD Instinct MI300X data sheet.
get S30-amd-mi300x-data-sheet.pdf 'https://www.amd.com/content/dam/amd/en/documents/instinct-tech-docs/data-sheets/amd-instinct-mi300x-data-sheet.pdf'
# S36 -- Metal Shading Language Specification (14 MB).
get S36-metal-shading-language.pdf 'https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf'
# S37 -- Shi, on why Amdahl and Gustafson are the same law.
get S37-shi-1996-amdahl-gustafson.pdf \
    "https://cgvr.cs.uni-bremen.de/teaching/mpar_literatur/Reevaluating%20Amdahl's%20Law%20and%20Gustafson's%20Law.pdf"
# S38 -- Volkov, Better Performance at Lower Occupancy, GTC 2010.
get S38-volkov-gtc2010-lower-occupancy.pdf 'https://www.nvidia.com/content/GTC-2010/pdfs/2238_GTC2010.pdf'

echo
echo "Paywalled or print-only, cite by DOI (open in a browser):"
echo "  S9  Amdahl 1967             https://doi.org/10.1145/1465482.1465560"
echo "  S11 Williams et al. 2009    https://doi.org/10.1145/1498765.1498785"
echo "  S12 Little 1961             https://doi.org/10.1287/opre.9.3.383"
echo "  S14 Hockney 1994            https://doi.org/10.1016/S0167-8191(06)80021-9"
echo "  S19 Hillis & Steele 1986    https://doi.org/10.1145/7902.7903"
echo "  S20 Kreutzer et al. 2014    https://doi.org/10.1137/130930352"
echo "  S21 Bell & Garland 2009     https://doi.org/10.1145/1654059.1654078"
echo "  S33 Hennessy & Patterson, Computer Architecture: A Quantitative Approach, 6th ed. (book)"
echo "  S34 Horowitz 2014           https://doi.org/10.1109/ISSCC.2014.6757323"
echo
echo "Live documentation, read online: S26 HIP (rocm.docs.amd.com), S28 Vitis HLS UG1399 (docs.amd.com)."
echo "OpenMP 5.2 (S22) is vendored once in the repo, in the NSSC I folder:"
echo "  ../../../ws2026/numerical-simulation-and-scientific-computing-i/refs/vendor/openmp-api-specification-5.2.pdf"
echo
echo "Vendored here (do not re-download):"
shasum -a 256 vendor/rupp-cpu-gpu-mic-comparison/* 2>/dev/null || true
