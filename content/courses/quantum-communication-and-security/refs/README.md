# refs: 141.320 Quantum Communication and Security

[`SOURCES.md`](SOURCES.md) is the register: entries `S1 … S39`, each with authors, title, journal, arXiv id, retrieval status, licence and what it was used for. The notes cite it as `[S<n>]` with an equation or theorem locator where one exists.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topic → best source sections → our notes → our code |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads 13 free PDFs from arXiv into `cite-only/` |
| `.gitignore` | ignores `cite-only/` |
| `cite-only/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored

The course's lecture notes and exercise sheets are handed out in the course [S1] and have not been seen; TISS lists no literature. TUWEL was not used. So `refs/` holds only text written here.

Licences, as stated on the arXiv pages on 2026-09-28:

- **S5** Tomamichel-Leverrier (Quantum 2017) and **S32** Andriolo et al. (Braz. J. Phys. 2026): **CC BY 4.0**. Could be committed with attribution.
- **S13** Wilde's book draft: **CC BY-NC-SA 4.0**. Could be committed non-commercially with the licence notice.
- Everything else (S3, S4, S6-S12, S19): arXiv non-exclusive distribution licence or the pre-2004 "assumed" licence. **Cite only, never commit.** The TCS 2014 reprint of BB84 (S6) could not be checked (Elsevier HTTP 403).

Even the permissive ones are fetched rather than vendored to keep the repository small and the policy uniform.

```sh
cd ss2027/quantum-communication-and-security/refs && ./fetch-sources.sh
```

The script prints the SHA-256 of the copies read while writing the notes; a different hash usually means a new arXiv version.

## Reading order

1. **S5** §§2-6: the whole security proof of entanglement-based BB84 in 20 pages, with every constant. Notes 03-05 follow its notation ($m$, $k$, $n$, $\delta$, $\nu$, $r$, $t$, $\ell$, $\bar c$).
2. **S3** §§I-III: the practical picture, the secret-fraction formulas, the thresholds.
3. **S9** §§2-3: decoy states with the exact model the code uses. **S10** (4 pages) and **S11** App. A-B for MDI-QKD.
4. **S4** chapters 3, 5, 6: min-entropy, privacy amplification, de Finetti; as reference, not cover to cover.
5. **S32**: the lecturer's 2026 review of security proofs with imperfections; the closest public proxy for how topic 6 will be taught.

## Conventions that differ between sources

- **Trace distance.** S4 uses the unhalved $L_1$ norm in Cor. 5.6.1 ($2\varepsilon+2^{-\frac12(H-\ell)}$) but the halved one in the security definition Eq. (2.6); S5 uses the halved one. Notes use $\frac12\|\cdot\|_1$ throughout.
- **Smoothing ball.** S4: trace norm; S5: purified distance. Finite-key constants depend on it.
- **Max-entropy.** S4: $\log$ of the support size; S5: the Rényi-1/2 form (dual of $H_{\min}$).
- **Sift factor.** S9 writes $q=\tfrac12$ for standard BB84; S5 and S10 use a basis choice without sifting loss in their rate formulas.
