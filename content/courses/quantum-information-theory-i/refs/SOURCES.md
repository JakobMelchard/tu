# Sources: 141.282 Quantum Information Theory I

Register of every source used to write and verify [`../notes`](../notes/README.md) and [`../src`](../src/README.md). Notes cite `[S<n>]`, with a locator where one exists (`[S6 §2.4]`, `[S11 Thm 9.2.1]`). Retrieval date 2026-09-28 unless stated. **Vendoring policy:** nothing third-party is committed. Free PDFs are fetched by [`fetch-sources.sh`](fetch-sources.sh) into the git-ignored `cite-only/`; see [`README.md`](README.md) for licences.

## Course records

**S1** TISS course page 141.282, 2027S. <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=141282&semester=2027S>. Transcribed in [`../docs/tiss.md`](../docs/tiss.md) (logged-in browser, 2026-09-28). Used for: type, ECTS, oral exam, dates and room, no registration, weekly lecture notes, lecturers, curricula, literature list.
**S2** TISS API record 141.282-2027S, `../docs/tiss-api.md`. Used for: learning outcomes and the numbered subject outline 1.1-2.8 that the notes follow item by item.
**S3** Semester calendar `_schedule/dates.json` of the source repo, not published (`notes` field of 141.282 and 141.320; lecture-free list). Used for: holidays, neighbouring courses.
**S4** VoWi (vowi.fsinf.at), MediaWiki API searched 2026-09-28 for "Quantum Information Theory", "Quanteninformation", "Huber": **no page for 141.282**. Pages "Quanteninformationstheorie II VO (Friis)" (id 141300, last held 2025W, revision 2025-10-07) and "(Huber)" (id 141B21, last held 2024S, revision 2024-03-06) exist; every section reads "noch offen", no attachments. Used for: "no past questions" in note 00.

## Literature named on TISS

**S5** J. Preskill, *Lecture Notes on Quantum Information and Computation*, ch. 1-6 (1998), 321 pp. <https://www.lorentz.leidenuniv.nl/quantumcomputers/literature/preskill_1_to_6.pdf> (the link on TISS). Free to read; no licence statement: cite only. sha256 `905ab1b7…ca26`. Locators used: §2.3.3 Gleason (p. 56), §3.1.2-3.1.4 POVM and Neumark (pp. 81-86), §3.2-3.4 superoperators, Kraus, channels, §4.1-4.2, §5.2.1, Exercise 5.1.
**S6** Preskill, ch. 2 *Foundations I: States and Ensembles* (July 2015), 53 pp. <http://www.preskill.caltech.edu/ph219/chap2_15.pdf>, index <https://www.preskill.caltech.edu/ph229/>. Cite only. sha256 `709a8a52…0d34`. §2.1-2.3.2, §2.4 Schmidt, §2.5.3-2.5.5 no-signalling and HJW, §2.6.1-2.6.2 fidelity/Uhlmann and distance relations, Ex. 2.5 (optimal two-state measurement), Ex. 2.8 (Peres-Mermin square).
**S7** Preskill, ch. 3 *Foundations II: Measurement and Evolution* (July 2015), 65 pp. <http://www.preskill.caltech.edu/ph219/chap3_15.pdf>. Cite only. sha256 `34141b21…e6ad`. §3.1 measurement and POVMs, §3.2 operator sum and complete positivity, §3.3 channel-state duality and Stinespring, §3.4 three channels.
**S8** Preskill, ch. 4 *Quantum Entanglement* (2001, incomplete), 70 pp. <http://www.preskill.caltech.edu/ph229/notes/chap4_01.pdf>. Cite only. sha256 `f534889a…0546`. §4.1-4.3 (EPR, Bell, CHSH, Cirel'son §4.3.2, all pure entangled states violate §4.3.4), §4.4 dense coding and teleportation, §4.5 EPR key distribution, no cloning, §4.6 mixed-state entanglement and PPT, Ex. 4.10 (Werner $\lambda>1/3$).
**S9** Preskill, ch. 10 *Quantum Shannon Theory* (June 2025), 103 pp. <http://www.preskill.caltech.edu/ph219/chap10_6A_2025.pdf>. Cite only. sha256 `4cfb665b…c16b`. §10.1.4, §10.2-10.2.3 (entropy, SSA), §10.4-10.5 (entanglement concentration, mixed-state measures), §10.6.2 Holevo, §10.8.2.
**S10** R. Jozsa, *Quantum Information and Computation*, lecture notes, DAMTP Cambridge, "Part IIC (January 2019 version)", 88 pp. <https://www.qi.damtp.cam.ac.uk/files/PartIIIQC/Part%202%20QIC%20lecturenotes.pdf> (the link on TISS; path says PartIII, document says Part II). Cite only. sha256 `f783096f…3ce4`. §2.1-2.2, §3.1 no cloning, §3.2 distinguishing non-orthogonal states (Helstrom-Holevo bound, USD remark), §3.3 no-signalling, §3.4 dense coding, §4 teleportation, §5 BB84 (threshold "about 11%").
**S11** M. M. Wilde, *From Classical to Quantum Shannon Theory*, arXiv:1106.1445v8 (2019), 774 pp. <https://arxiv.org/abs/1106.1445>. **CC BY-NC-SA** (4.0 on arXiv, 3.0 in the PDF footer): non-commercial, fetched not vendored. Thm 3.8.1 Schmidt, §3.5.4 no-cloning, Ex. 3.5.8 no-deletion, Ex. 3.6.3 cloning implies signalling, §3.6.2 CHSH game, Def. 4.2.1 POVM, Def. 4.3.2 separable, Thm 4.4.1 Choi-Kraus, Def. 4.4.4 Choi operator, §5.1-5.2 purification and isometric extension, Thm 5.1.1, §6.1-6.3 unit protocols, ch. 9 (Thm 9.2.1 Uhlmann, Thm 9.2.2, Thm 9.3.1 Fuchs-van de Graaf), ch. 11 (Property 11.1.4 concavity, Ex. 11.7.10 Araki-Lieb, Thm 11.7.1 and Cor. 11.9.1 SSA, Thm 11.8.1 monotonicity, Thm 11.8.2 Klein, Cor. 11.8.1 subadditivity, Thm 11.9.1 quantum Pinsker).
**S12** M. M. Wilde, *Quantum Information Theory*, 2nd ed., CUP 2017. Not free: cite only; S11 is its arXiv version.
**S13** M. A. Nielsen, I. L. Chuang, *Quantum Computation and Quantum Information*, CUP 2000 (10th anniv. ed. 2010). Not free: cite only. Section locators (§1.3.5, §1.3.7, §2.2-2.6, §8.2-8.3, §9.2, §11.1-11.3, §12.6) from the 2010 edition, **not re-checked** (book not accessible).
**S14** R. A. Bertlmann, N. Friis, *Modern Quantum Theory: From Quantum Mechanics to Entanglement and Quantum Information*, OUP 2023, ISBN 9780199683338, doi:10.1093/oso/9780199683338.001.0001. By the two lecturers. Not free: cite only. Chapter titles and pages from Crossref (ch. 11 Density Matrices, 12 Hidden-Variable Theories, 13 Bell Inequalities, 14 Quantum Teleportation, 15 Entanglement and Separability, 16 Quantification and Conversion of Entanglement, 18 Multipartite Entanglement, 19-20 entropy, 21 Quantum Channels and Quantum Operations, 23 Quantum Measurements, 24 Quantum Metrology); **contents not seen**, mapping by title only.

## Primary literature (journal data from Crossref or the arXiv API, 2026-09-28)

| id | reference | used in |
|---|---|---|
| S15 | A. Einstein, B. Podolsky, N. Rosen, Phys. Rev. 47, 777 (1935), doi:10.1103/PhysRev.47.777 | 06 |
| S16 | J. S. Bell, Physics 1, 195 (1964), doi:10.1103/PhysicsPhysiqueFizika.1.195 | 06 |
| S17 | J. F. Clauser, M. A. Horne, A. Shimony, R. A. Holt, PRL 23, 880 (1969), doi:10.1103/PhysRevLett.23.880 | 06 |
| S18 | B. S. Cirel'son (Tsirelson), Lett. Math. Phys. 4, 93 (1980), doi:10.1007/BF00417500 | 06 |
| S19 | R. Horodecki, P. Horodecki, M. Horodecki, Phys. Lett. A 200, 340 (1995), doi:10.1016/0375-9601(95)00214-N (CHSH criterion) | 06, `bell.py` |
| S20 | R. F. Werner, PRA 40, 4277 (1989), doi:10.1103/PhysRevA.40.4277 | 06, 10 |
| S21 | A. M. Gleason, J. Math. Mech. 6, 885 (1957), doi:10.1512/iumj.1957.6.56050 | 07 |
| S22 | S. Kochen, E. P. Specker, J. Math. Mech. 17, 59 (1967), doi:10.1512/iumj.1968.17.17004 | 07 |
| S23 | A. Peres, Phys. Lett. A 151, 107 (1990), doi:10.1016/0375-9601(90)90172-K | 07 |
| S24 | N. D. Mermin, PRL 65, 3373 (1990), doi:10.1103/PhysRevLett.65.3373 | 07 |
| S25 | N. D. Mermin, Rev. Mod. Phys. 65, 803 (1993), arXiv:1802.10119 (§V square, §VI star, read) | 06, 07 |
| S26 | A. Cabello, J. M. Estebaranz, G. García-Alcaine, Phys. Lett. A 212, 183 (1996), doi:10.1016/0375-9601(96)00134-X | 07, `bell.py` |
| S27 | C. H. Bennett et al., PRL 70, 1895 (1993), doi:10.1103/PhysRevLett.70.1895 (teleportation) | 08 |
| S28 | M. Żukowski, A. Zeilinger, M. A. Horne, A. K. Ekert, PRL 71, 4287 (1993), doi:10.1103/PhysRevLett.71.4287 (swapping) | 08 |
| S29 | C. H. Bennett, S. J. Wiesner, PRL 69, 2881 (1992), doi:10.1103/PhysRevLett.69.2881 (dense coding) | 08 |
| S30 | C. H. Bennett, G. Brassard, Proc. IEEE ICCSSP Bangalore 1984, pp. 175-179; reprint Theor. Comput. Sci. 560, 7 (2014), arXiv:2003.06557 | 09 |
| S31 | A. K. Ekert, PRL 67, 661 (1991), doi:10.1103/PhysRevLett.67.661 | 09 |
| S32 | C. H. Bennett, G. Brassard, N. D. Mermin, PRL 68, 557 (1992), doi:10.1103/PhysRevLett.68.557 | 09 |
| S33 | A. Peres, PRL 77, 1413 (1996), arXiv:quant-ph/9604005 (PPT) | 10 |
| S34 | M. Horodecki, P. Horodecki, R. Horodecki, Phys. Lett. A 223, 1 (1996), doi:10.1016/S0375-9601(96)00706-2, arXiv:quant-ph/9605038 | 10 |
| S35 | B. M. Terhal, Phys. Lett. A 271, 319 (2000), arXiv:quant-ph/9911057 (witnesses) | 10 |
| S36 | G. Vidal, R. F. Werner, PRA 65, 032314 (2002), arXiv:quant-ph/0102117 (negativity) | 10 |
| S37 | W. K. Wootters, PRL 80, 2245 (1998), arXiv:quant-ph/9709029 (concurrence) | 10, `entanglement.py` |
| S38 | A. Uhlmann, Rep. Math. Phys. 9, 273 (1976), doi:10.1016/0034-4877(76)90060-4 | 05 |
| S39 | R. Jozsa, J. Mod. Opt. 41, 2315 (1994), doi:10.1080/09500349414552171 (fidelity axioms, squared convention) | 05 |
| S40 | C. A. Fuchs, J. van de Graaf, IEEE Trans. Inf. Theory 45, 1216 (1999), arXiv:quant-ph/9712042 | 05 |
| S41 | H. Araki, E. H. Lieb, Commun. Math. Phys. 18, 160 (1970), doi:10.1007/BF01646092 | 03 |
| S42 | E. H. Lieb, M. B. Ruskai, J. Math. Phys. 14, 1938 (1973), doi:10.1063/1.1666274 (SSA) | 03 |
| S43 | O. Klein, Z. Phys. 72, 767 (1931), doi:10.1007/BF01341997 | 03 |
| S44 | W. F. Stinespring, Proc. AMS 6, 211 (1955), doi:10.2307/2032342 | 11 |
| S45 | M.-D. Choi, Linear Algebra Appl. 10, 285 (1975), doi:10.1016/0024-3795(75)90075-0 | 11 |
| S46 | K. Kraus, *States, Effects, and Operations*, Lecture Notes in Physics 190, Springer 1983, doi:10.1007/3-540-12732-1 | 11 |
| S47 | M. A. Naimark, Izv. Akad. Nauk SSSR Ser. Mat. 4, 277 (1940). **Not fetched**; data from secondary literature; the theorem is taken from S5 §3.1.4 | 12 |
| S48 | W. K. Wootters, W. H. Zurek, Nature 299, 802 (1982), doi:10.1038/299802a0 | 13 |
| S49 | D. Dieks, Phys. Lett. A 92, 271 (1982), doi:10.1016/0375-9601(82)90084-6 | 13 |
| S50 | V. Bužek, M. Hillery, PRA 54, 1844 (1996), arXiv:quant-ph/9607018 | 13, `cloning.py` |
| S51 | N. Gisin, S. Massar, PRL 79, 2153 (1997), arXiv:quant-ph/9705046 | 13 |
| S52 | D. Bruß, A. Ekert, C. Macchiavello, PRL 81, 2598 (1998), arXiv:quant-ph/9712019 | 13 |
| S53 | H. Barnum, C. M. Caves, C. A. Fuchs, R. Jozsa, B. Schumacher, PRL 76, 2818 (1996), arXiv:quant-ph/9511010 | 13 |
| S54 | A. K. Pati, S. L. Braunstein, Nature 404, 164 (2000), arXiv:quant-ph/9911090 | 13 |
| S55 | C. W. Helstrom, J. Stat. Phys. 1, 231 (1969), doi:10.1007/BF01007479 | 05, 13 |
| S56 | I. D. Ivanovic, Phys. Lett. A 123, 257 (1987), doi:10.1016/0375-9601(87)90222-2 | 13 |
| S57 | D. Dieks, Phys. Lett. A 126, 303 (1988), doi:10.1016/0375-9601(88)90840-7 | 13 |
| S58 | A. Peres, Phys. Lett. A 128, 19 (1988), doi:10.1016/0375-9601(88)91034-1 | 13 |
| S59 | P. Busch, PRL 91, 120403 (2003), arXiv:quant-ph/9909073 (Gleason for POVMs) | 07 |
| S60 | P. Horodecki, Phys. Lett. A 232, 333 (1997), arXiv:quant-ph/9703004 (PPT entangled 3x3) | 10, `entanglement.py` |
| S61 | K. Chen, L.-A. Wu, Quantum Inf. Comput. 3, 193 (2003), arXiv:quant-ph/0205017 (realignment) | 10, `entanglement.py` |
| S62 | This repo: ws2026 quantum-computing notes C01 and C03 (conventions, teleportation circuit). Internal cross-reference, not a literature source | 01, 08, 13 |
| S63 | P. W. Shor, J. Preskill, PRL 85, 441 (2000), arXiv:quant-ph/0003004 (BB84 security, $1-2h(Q)$) | 09 |

## Not used

TUWEL (course materials, weekly lecture notes): not accessed. The old Preskill URLs `theory.caltech.edu/~preskill/ph229/` and `theory.caltech.edu/people/preskill/ph229/` return 404 (2026-09-28).
