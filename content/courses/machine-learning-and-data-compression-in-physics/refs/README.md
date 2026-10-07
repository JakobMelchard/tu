# refs: 138.129 Machine Learning and Data Compression in Physics

[`SOURCES.md`](SOURCES.md) is the register (S1-S36): what each source is, its
licence, and whether it was read, only its abstract checked, or not retrieved.
The notes cite it as `[S<n>]`.

| file | what |
|---|---|
| [`SOURCES.md`](SOURCES.md) | source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | the course has no lecture notes; maps the 138.128 exercise notebooks and the key papers onto our notes and code |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the 18 free arXiv PDFs into `cite-only/` |
| `cite-only/` | created by the script, **git-ignored** ([`.gitignore`](.gitignore)), never committed |

## Nothing is vendored

The course publishes nothing: TISS lists no literature and no lecture notes [S1],
and TUWEL (where a course page might exist) needs a login and was not used.

Most arXiv papers carry arXiv's non-exclusive distribution licence, which lets
arXiv, not us, redistribute them: personal use only. Four are permissive and
*could* be vendored with their licence notice: S13 sparse-ir paper (CC BY-SA 4.0),
S16 quantics PRX (CC0), S29 Yoon et al. (CC0), S34 parquet QTT (CC BY 4.0). They
are fetched like the rest, to keep the policy uniform and the repo small. The
sparse-ir code is MIT [S14]; install it, do not copy it. Wallerberger's exercise
notebooks [S6] have no licence file: link, do not copy.

```sh
cd ws2027/machine-learning-and-data-compression-in-physics/refs && ./fetch-sources.sh
```

Retrieved 2026-09-28: 18 PDFs, 47 MB (S17 alone 12 MB).

## Reading order

1. [`../notes/00-project-focus.md`](../notes/00-project-focus.md) and
   [`../notes/01-project-playbook.md`](../notes/01-project-playbook.md).
2. **S13** (sparse-ir, 10 pages): the IR, sparse sampling and the software in one
   place; then **S10** and **S12** for the derivations behind it.
3. **S18** sections 1, 4, 10 for randomised SVD; **S24** for MPS; **S16** for
   quantics tensor trains.
4. **S17** (Mehta et al.) as the ML reference; it is also on the 138.128 list [S4].
5. **S28** for analytic continuation as practised at E138.
