# Sources: 141.320 Quantum Communication and Security

Register of every source used to write and verify [`../notes`](../notes/README.md) and [`../src`](../src/README.md). Retrieval date 2026-09-28 unless stated. Citation form in the notes: `[S<n>]`, with a locator where a result is cited (`[S5 Eq. (58)]`, `[S4 Cor. 5.6.1]`, `[S9 Table 1]`).

**Retrieval.** "Fetched" means the arXiv abstract page was read, and for S3, S4, S5, S9, S10, S11, S19 the PDF text was read and the cited equation or theorem numbers were checked in it. "Via bibliography" means the reference data come from the reference lists of S3, S4, S5 or S11 and the item itself was not opened.

**Vendoring.** Nothing is vendored. [`fetch-sources.sh`](fetch-sources.sh) downloads the free PDFs into the git-ignored `cite-only/`. S5, S32 are CC BY 4.0 and S13 CC BY-NC-SA 4.0 and could legally be committed; they are fetched like the rest to keep the repo small. All others carry the arXiv non-exclusive licence or none: cite only. See [`README.md`](README.md).

## Course records

### S1: TISS course page 141.320, 2027S
- <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=141320&semester=2027S>, transcribed in [`../docs/tiss.md`](../docs/tiss.md) (2026-09-28). Not re-fetched here (page needs JavaScript).
- Used for: all course facts in note 00 (dates, rooms, registration, grading, lecturer, curriculum, time discrepancy, 2026S comparison).

### S2: TISS API record 141.320, 2027S
- `https://tiss.tuwien.ac.at/api/course/141320-2027S`, stored as `../docs/tiss-api.md` / `.xml`.
- Used for: topic list (the order of notes 01-06), the four learning outcomes (note 00 §2), "Mondays, 14:00 - 16:30".

### S36: semester calendar `../../_schedule/dates.json` (source repo file, not published)
- Used for: public holidays on Mondays (note 00 §5).

### S35: VoWi, "TU Wien:Quantum Communication and Security VU (Murta Guimaraes)"
- <https://vowi.fsinf.at/wiki/TU_Wien:Quantum_Communication_and_Security_VU_(Murta_Guimaraes)> (URL guessed from the VoWi naming scheme). **Not readable**: the fetch returned a bot-filter "Access Denied" page on 2026-09-28. Whether the page exists is unknown. Cited only for that fact.

## Reviews, theses, books

### S3: V. Scarani, H. Bechmann-Pasquinucci, N. J. Cerf, M. Dušek, N. Lütkenhaus, M. Peev, "The security of practical quantum key distribution", Rev. Mod. Phys. 81, 1301 (2009)
- arXiv:0802.4155, doi:10.1103/RevModPhys.81.1301. Fetched; PDF 52 pp. read. arXiv non-exclusive licence: cite only.
- Used for: intercept-resend and Csiszár-Körner (§I.B, Eq. (21) $r=I(A{:}B)-\min(I_{EA},I_{EB})$), authentication (§II.B-C), accessible information not composable (§II.C), EC efficiency 10-20 % and Cascade in one-way proofs (§III.B), 11 % and 12.4 % thresholds (§III.B).

### S4: R. Renner, "Security of Quantum Key Distribution", PhD thesis, ETH Zürich, Diss. ETH No. 16242 (2005)
- arXiv:quant-ph/0512258v2. Fetched; PDF read. Cite only.
- Used for: $\varepsilon$-secure key Eq. (2.6) and §2.2 (composability, locking); min-entropy Defs 3.1.1-3.1.2; smoothing ball Def. 3.2.1 (trace norm); AEP Thm 3.3.6; de Finetti Thm 4.3.2; two-universal Def. 5.4.1; privacy amplification Thm 5.5.1 and Cor. 5.6.1 (unhalved $L_1$); rate Cor. 6.5.2; Bell-diagonal reduction and 12.4 % (§7.1).

### S5: M. Tomamichel, A. Leverrier, "A largely self-contained and complete security proof for quantum key distribution", Quantum 1, 14 (2017)
- arXiv:1506.08458, doi:10.22331/q-2017-07-14-14. **CC BY 4.0.** Fetched; PDF 38 pp. read.
- Used for: protocol and parameters (§3.2), security definition and Lemma 1 (§4, Eqs. (47)-(55)), $p_{\rm guess}$ and min-entropy (Eqs. (12)-(13)), smoothing with purified distance (Def. 5), duality, DPI, chain rule (Eqs. (17)-(19)), Thms 2-3 and Eqs. (56)-(59), Fig. 7 ($\varepsilon=10^{-10}$, $\bar c=\tfrac12$, $r=1.1(m-k)h(\delta)$), uncertainty relation Prop. 4 and Cor. 5, Serfling Lemma 6, Eq. (80), §9 device assumptions.

### S13: M. M. Wilde, "From Classical to Quantum Shannon Theory", arXiv:1106.1445v8 (2019)
- Fetched (abstract). **CC BY-NC-SA 4.0** (stated in the arXiv comments). Background for entropies (note 03); no locator cited.

## Protocols and security proofs

### S6: C. H. Bennett, G. Brassard, "Quantum cryptography: Public key distribution and coin tossing", Proc. IEEE ICCSSP, Bangalore, 175-179 (1984); reprinted Theor. Comput. Sci. 560, 7-11 (2014)
- arXiv:2003.06557 (scan of the 1984 paper), doi:10.1016/j.tcs.2014.05.025. Fetched (arXiv abstract); the Elsevier page returned HTTP 403, so the licence of the TCS reprint was not checked. Cite only.
- Used for: the BB84 protocol (note 02).

### S7: P. W. Shor, J. Preskill, "Simple proof of security of the BB84 quantum key distribution protocol", Phys. Rev. Lett. 85, 441 (2000)
- arXiv:quant-ph/0003004, doi:10.1103/PhysRevLett.85.441. Fetched. Used for: Thm 5.3, $1-2h(e)$, 11 %.

### S14: I. Devetak, A. Winter, "Distillation of secret key and entanglement from quantum states", Proc. R. Soc. A 461, 207-235 (2005)
- arXiv:quant-ph/0306078, doi:10.1098/rspa.2004.1372. Fetched. Used for: Thm 5.1.

### S15: D. Gottesman, H.-K. Lo, N. Lütkenhaus, J. Preskill, "Security of quantum key distribution with imperfect devices", Quantum Inf. Comput. 4(5), 325-360 (2004)
- arXiv:quant-ph/0212066 (journal-ref on arXiv reads "5 (2004) 325-360"). Fetched. Used for: GLLP rate, tagging (Prop. 6.1), basis-independence assumption.

### S19: M. Christandl, R. König, R. Renner, "Post-selection technique for quantum channels with applications to quantum cryptography", Phys. Rev. Lett. 102, 020504 (2009)
- arXiv:0809.3019. Fetched; PDF read. Used for: $(n+1)^{d^2-1}$ and the $2(d^2-1)\log_2(n+1)$ key reduction (Thm 5.4).

### S24: C. Portmann, R. Renner, "Cryptographic security of quantum key distribution", arXiv:1409.3525 (2014)
- Fetched (abstract). Used for: composability, errors add under composition (note 01).

### S25: R. Renner, N. Gisin, B. Kraus, "An information-theoretic security proof for QKD protocols", Phys. Rev. A 72, 012332 (2005)
- arXiv:quant-ph/0502064. Fetched. Used for: collective attacks suffice with one-way post-processing, noisy preprocessing (note 05).

### S26: R. Renner, "Symmetry of large physical systems implies independence of subsystems", Nature Phys. 3, 645 (2007)
- arXiv:quant-ph/0703069 (arXiv title "Symmetry implies independence"). Fetched. Used for: de Finetti (Thm 5.4).

### S27: M. Tomamichel, C. C. W. Lim, N. Gisin, R. Renner, "Tight finite-key analysis for quantum cryptography", Nat. Commun. 3, 634 (2012)
- arXiv:1103.4130. Fetched. Used for: uncertainty-relation finite-key proofs (note 05).

### S37: C. H. Bennett, G. Brassard, N. D. Mermin, "Quantum cryptography without Bell's theorem", Phys. Rev. Lett. 68, 557 (1992); A. K. Ekert, Phys. Rev. Lett. 67, 661 (1991)
- Via bibliography (S5 ref. [3], [2]). Used for: entanglement-based BB84 (note 02).

## Entropies and uncertainty

### S20: M. Berta, M. Christandl, R. Colbeck, J. M. Renes, R. Renner, "The uncertainty principle in the presence of quantum memory", Nature Phys. 6, 659 (2010)
- arXiv:0909.0950. Fetched. Used for: $H(X|B)+H(Z|C)\ge\log\frac1c$ (note 03), tested numerically.

### S21: M. Tomamichel, R. Renner, "Uncertainty relation for smooth entropies", Phys. Rev. Lett. 106, 110506 (2011)
- arXiv:1009.2015. Fetched. Used for: smooth uncertainty relation (notes 03, 05).

## Reconciliation and privacy amplification

### S12: R. Renner, R. König, "Universally composable privacy amplification against quantum adversaries", TCC 2005, LNCS 3378 (2005)
- arXiv:quant-ph/0403133. Fetched. Used for: leftover hash lemma against quantum side information (note 04).

### S22: G. Brassard, L. Salvail, "Secret-key reconciliation by public discussion", EUROCRYPT '93, LNCS 765 (1994)
- Via bibliography (S3). Used for: Cascade (note 04).

### S23: J. L. Carter, M. N. Wegman, "Universal classes of hash functions", J. Comput. Syst. Sci. 18, 143 (1979); M. N. Wegman, J. L. Carter, "New hash functions and their use in authentication and set equality", J. Comput. Syst. Sci. 22 (1981)
- Via bibliography (S3, S4, S5). Used for: two-universal hashing, Wegman-Carter authentication (notes 01, 04).

### S38: R. J. Serfling, "Probability inequalities for the sum in sampling without replacement", Ann. Stat. 2(1), 39-48 (1974)
- Via bibliography (S5 ref. [40]). Used for: Prop. 2.5.

### S39: D. Elkouss, A. Leverrier, R. Alléaume, J. J. Boutros, "Efficient reconciliation protocol for discrete-variable quantum key distribution", Proc. IEEE ISIT 2009, 1879-1883
- Via bibliography (S5 ref. [37]). Used for: LDPC reconciliation with $f\approx1.1$ (note 04).

### S16: C. E. Shannon, "Communication theory of secrecy systems", Bell Syst. Tech. J. 28, 656 (1949)
- Via bibliography (S3). Used for: perfect secrecy and the key bound (note 01).

## Imperfections

### S8: H.-K. Lo, X. Ma, K. Chen, "Decoy state quantum key distribution", Phys. Rev. Lett. 94, 230504 (2005)
- arXiv:quant-ph/0411004. Fetched. Used for: decoy-state security (note 06).

### S9: X. Ma, B. Qi, Y. Zhao, H.-K. Lo, "Practical decoy state for quantum key distribution", Phys. Rev. A 72, 012326 (2005)
- arXiv:quant-ph/0503005. Fetched; PDF 31 pp. read. Used for: model Eqs. (4)-(11), rate Eq. (1) with $q=\tfrac12$, $\mu_{\rm opt}$ Eq. (12), GYS Table 1, two-decoy Eqs. (18)-(25), vacuum+weak Eqs. (33)-(37), deviations §3.6 (3.5 %, 16.8 %), Fig. 2 distances 142.05 and 140.55 km. **These, the deviations and $\mu_{\rm opt}$ are reproduced in `test_decoy.py`** (the 128.55 km of Wang's method is not).

### S10: H.-K. Lo, M. Curty, B. Qi, "Measurement-device-independent quantum key distribution", Phys. Rev. Lett. 108, 130503 (2012)
- arXiv:1109.1473. Fetched; PDF read. Used for: protocol, Table I sifting, Eq. (1), Fig. 2 parameters (0.2 dB/km, 1.5 %, 14.5 %, $6.02\times10^{-6}$, $f=1.16$), ">40 dB (200 km)", quantum-coin remark.

### S11: X. Ma, M. Razavi, "Alternative schemes for measurement-device-independent quantum key distribution", Phys. Rev. A 86, 062319 (2012)
- arXiv:1204.4856. Fetched; PDF read. Used for: closed forms (A9), (A11), (B1), (B7)-(B16), (B27)-(B31), Table I ($p_d=3\times10^{-6}$ per detector). **Reproduced by first-principles models in `test_mdi_qkd.py`.**

### S17: W.-Y. Hwang, "Quantum key distribution with high loss: toward global secure communication", Phys. Rev. Lett. 91, 057901 (2003)
- arXiv:quant-ph/0211153. Fetched. Used for: decoy idea (note 06).

### S18: G. Brassard, N. Lütkenhaus, T. Mor, B. C. Sanders, "Limitations on practical quantum cryptography", Phys. Rev. Lett. 85, 1330 (2000)
- arXiv:quant-ph/9911054 (arXiv title "Security aspects of practical quantum cryptography"). Fetched. Used for: PNS attack.

### S31: L. Lydersen, C. Wiechers, C. Wittmann, D. Elser, J. Skaar, V. Makarov, "Hacking commercial quantum cryptography systems by tailored bright illumination", Nature Photon. 4, 686 (2010)
- arXiv:1008.4593. Fetched. Used for: detector blinding (note 06).

### S28: A. Acín, N. Brunner, N. Gisin, S. Massar, S. Pironio, V. Scarani, "Device-independent security of quantum cryptography against collective attacks", Phys. Rev. Lett. 98, 230501 (2007)
- arXiv:quant-ph/0702152. Fetched. Used for: DI-QKD paragraph.

### S29: R. Arnon-Friedman, R. Renner, T. Vidick, "Simple and tight device-independent security proofs", SIAM J. Comput. 48, 181-225 (2019)
- arXiv:1607.01797. Fetched. Used for: entropy accumulation (DI-QKD paragraph).

### S30: D. P. Nadlinger et al., "Experimental quantum key distribution certified by Bell's theorem", Nature 607, 682-686 (2022)
- arXiv:2109.14600. Fetched. Used for: first DI-QKD demonstration (trapped ions).

## The lecturer's own work

### S32: P. Andriolo, E. Vasquez, E. Agudelo, M. Riegler, M. Pivoluska, G. Murta, "Quantum key distribution with imperfections: recent advances in security proofs", Braz. J. Phys. 56, 157 (2026)
- arXiv:2602.05057 (v2 22.05.2026). **CC BY 4.0.** Fetched (abstract). Used for: reading for topic 6 (notes 00, 06). Content not read in detail.

### S33: G. Murta, F. Grasselli, H. Kampermann, D. Bruß, "Quantum conference key agreement: a review", Adv. Quantum Technol. (2020)
- arXiv:2003.10186, doi:10.1002/qute.202000025. Fetched (abstract). Used for: the lecturer's research profile ([`lecture-notes-map.md`](lecture-notes-map.md)).

### S34: G. Murta, S. B. van Dam, J. Ribeiro, R. Hanson, S. Wehner, "Towards a realization of device-independent quantum key distribution" (2019)
- arXiv:1811.07983 (listed on the author's arXiv page; journal reference not checked). Used for: DI-QKD paragraph.

## Sources deliberately not used

- **TUWEL**: not accessed; nothing fetched.
- The course's own lecture notes: distributed in the course, not public.
