# refs - 360.252 Computational Science on Many-Core Architectures

[`SOURCES.md`](SOURCES.md) is the register (`S1 ... S40`): title, authors, URL,
retrieval date (2026-09-28), licence, and what each source was used for. The
notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topic -> sources -> our note -> our code, one row per topic |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads 23 cite-only files (43 MB) into `cite-only/` for personal use; verified 2026-09-28, no failures |
| `vendor/rupp-cpu-gpu-mic-comparison/` | the one vendored source, **committed** |
| `cite-only/` | created by the script, **git-ignored** (`.gitignore`), never committed |

## Start here

There is **no public course script and no public exercise sheet** for 360.252
(search record [S8]). TISS promises the slides as a download for registered
students [S1]. Until then, in this order:

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): what is known about
   the practical part and the oral exam, and what to check when the 2027W page
   appears.
2. **[S4]**, the lecturer's own 61-slide VSC tutorial (2015), fetched to
   `cite-only/S4-rupp-vsc2015-many-core-architectures.pdf`. Its outline
   (GPUs, MICs, CUDA, OpenCL, parallel primitives, bottlenecks, performance
   modelling by example) is the TISS subject list; one sitting.
3. **[S15]** CUDA C++ Programming Guide §5 (programming model), §7 (SIMT,
   hardware multithreading), §8.3 (memory throughput).
4. [`lecture-notes-map.md`](lecture-notes-map.md), then the notes in order.

## What is vendored, and why it is allowed

| path | source | bytes | licence |
|---|---|---|---|
| `vendor/rupp-cpu-gpu-mic-comparison/` (7 files, unmodified, commit `af35759`) | [S5] | 28 KB | **CC BY 4.0**, `LICENSE.txt` included; attribution: Karl Rupp, <https://github.com/karlrupp/cpu-gpu-mic-comparison> |

```sh
cd refs && shasum -a 256 -c <<'EOF'
2fb2dc63f0b0c0401c149243e5c5738fd5b09ed5274618e40e0b9da476c30d8f  vendor/rupp-cpu-gpu-mic-comparison/LICENSE.txt
56452686099c4f36f4691b12ccefc9a42a01fdaae3fab80816567b93c79efc23  vendor/rupp-cpu-gpu-mic-comparison/README.md
07a42a5a7842e742b6c5741fc46a605d8c0b5d2a9ff3ef859392890f9845e8b4  vendor/rupp-cpu-gpu-mic-comparison/data-amd.txt
3beb5e4f3844f8240862df4d2438da7c8abaf790bf4d527aa7cee6d92d052750  vendor/rupp-cpu-gpu-mic-comparison/data-dp-nvidia.txt
810f12493a5735050d8d38c6e7d7557e26872d91febc480393513a828b52c976  vendor/rupp-cpu-gpu-mic-comparison/data-intel-phi.txt
e4099b6daae9ed199c0d7f0b80f7335016732e37cbcedbaf0c19d02ef83da9cf  vendor/rupp-cpu-gpu-mic-comparison/data-intel.txt
9c861bd525369655e79c9d035d3fe6c7b244a31ec0ef65341aeda2452063f2e8  vendor/rupp-cpu-gpu-mic-comparison/data-sp-nvidia.txt
EOF
```

The OpenMP 5.2 specification [S22] is redistributable too, but it is already
vendored once in this repo (NSSC I folder); the notes link there instead of
committing a second 2 MB copy.

## What is not vendored, and why

- **The lecturer's slides [S4]**: public on GitHub but the repository has no
  licence, so all rights are reserved. Fetched, not committed.
- **Specifications with restrictive notices**: OpenACC 3.3 [S23] forbids
  reproduction without written permission; Khronos OpenCL [S24] and SYCL [S25]
  grant use and reproduction of the unmodified spec but no distribution. Fetched.
- **Vendor documentation and data sheets**: CUDA guide [S15], MI300X [S30],
  Metal spec [S36], Harris [S16], Volkov [S38], GPU Gems [S18]. Fetched.
- **Kastner et al. [S27]**: CC BY 4.0, so it *could* be committed; not done
  because it is 8 MB and a `git clone` of the source repository is better.
- **Rupp's trend data [S39]**: CC BY 4.0; cited, clone it if wanted.
- **Paywalled papers and books**: Amdahl [S9], Roofline CACM [S11] (the free
  tech report is fetched), Little [S12], Hockney [S14], Hillis-Steele [S19],
  SELL-C-sigma journal version [S20] (arXiv copy fetched), Bell-Garland [S21],
  Hennessy-Patterson [S33], Horowitz [S34]. Cited by DOI.
- **TUWEL**: needs a login; never fetched.

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```
