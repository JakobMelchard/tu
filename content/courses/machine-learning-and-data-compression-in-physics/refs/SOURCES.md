# Sources: 138.129 Machine Learning and Data Compression in Physics

Register of every source used for [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). The notes cite `[S<n>]`, with a locator where it
matters (`[S18 Thm 10.5]`). Retrieved 2026-09-28 unless stated. arXiv PDFs are
fetched by [`fetch-sources.sh`](fetch-sources.sh) into the git-ignored
`cite-only/`; nothing is vendored (see [`README.md`](README.md)).

**Status legend.** *read*: the PDF or page was retrieved and the cited passage
checked. *abstract*: only the arXiv abstract page (title, authors, journal,
licence) was checked. *not retrieved*: standard reference, bibliographic data
from memory, not checked against the original; verify before citing it in the
protocol.

## Course records

| id | what | status |
|---|---|---|
| S1 | TISS course page 138.129, 2026W (2027W not published), transcribed in [`../docs/tiss.md`](../docs/tiss.md): PR, 8.0 h, 10 ECTS, grade "Protocol", registration "Not necessary", lecturers Tomczak, Wallerberger, QIST 066 558 mandatory 3rd semester | read (transcription 2026-09-28) |
| S2 | TISS API record 2026W, `../docs/tiss-api.md`: subject text, learning outcomes, "Examination modalities: Protocol" | read |
| S3 | semester schedule `_schedule/dates.json` of the source repo (not published), entry 138.129 `notes` | read |
| S4 | 138.128 Machine Learning in Physics, 2027S TISS transcription, [`../../../ss2027/machine-learning-in-physics/docs/tiss.md`](../../machine-learning-in-physics/docs/tiss.md): lectures Fri 05.03.-25.06.2027, tests 05.05. and 23.06.2027, lecturers Andergassen, Ipp, Smolyanyuk, Wallerberger; literature list incl. Mehta et al. and Hansen | read |

## Lecturers

| id | what | status |
|---|---|---|
| S5 | Markus Wallerberger, homepage <https://www.wallerberger.at/>: E138 TU Wien, teaching "Machine Learning in Physics", papers mostly CC-BY-SA | read |
| S6 | Wallerberger, ML in Physics course page <https://www.wallerberger.at/mlphys> and exercise notebooks <https://github.com/mwallerb/ml-phys-exercises> (Ex01 gradient descent ... Ex06 SVD, Ex11 low-rank approximation, Ex12 reinforcement); **no licence file: cite only** | read |
| S7 | GitHub profile <https://github.com/mwallerb>: pinned sparse-ir, w2dynamics, LAZY, libxprec, ALPSCore; profile text "on leave until September 2026" | read |
| S8 | Jan M. Tomczak, King's College London staff page <https://www.kcl.ac.uk/people/jan-tomczak>: Senior Lecturer at KCL since January 2023, previously led a group at TU Wien; correlated materials, realistic simulations | read |
| S9 | Tomczak group site <https://sites.google.com/view/tomczak-group/people/jan-tomczak>: Privatdozent TU Wien since 2019; projects RECORD (FWF-ANR 2023-2027), BandITT, LinReTraCe | read |
| S35 | E138-01 Computational Materials Science (K. Held) <https://www.tuwien.at/en/phy/ifp/theory>: DMFT, GW+DMFT, dynamical vertex approximation | read |

No ML or analytic-continuation paper by **Jan M.** Tomczak was found on arXiv
(author query and web search, 2026-09-28). Do not confuse him with **Jakub M.**
Tomczak, an ML researcher (deep generative models) who dominates such searches.

## Compression of Green's functions (IR, sparse sampling, quantics)

| id | reference | status |
|---|---|---|
| S10 | H. Shinaoka, J. Otsuki, M. Ohzeki, K. Yoshimi, *Compressing Green's function using intermediate representation between imaginary-time and real-frequency domains*, PRB 96, 035147 (2017), arXiv:1702.03054 | abstract; PDF fetched |
| S11 | N. Chikano, K. Yoshimi, J. Otsuki, H. Shinaoka, *irbasis: open-source database and software for IR basis functions*, CPC 240, 181 (2019), arXiv:1807.05237 | abstract |
| S12 | J. Li, M. Wallerberger, N. Chikano, C.-N. Yeh, E. Gull, H. Shinaoka, *Sparse sampling approach to efficient ab initio calculations at finite temperature*, PRB 101, 035144 (2020), arXiv:1908.07575. Sampling: tau at midpoints of the roots of $U_{N-1}$ and $0,\beta$; Matsubara at the frequencies closest to the roots of $\hat U_N$ | read (sampling section) |
| S13 | M. Wallerberger, S. Badr, S. Hoshino, ..., H. Shinaoka, *sparse-ir: optimal compression and sparse sampling of many-body propagators*, SoftwareX 21, 101266 (2023), arXiv:2206.11762, **CC BY-SA 4.0**. Eqs. (2)-(4): $G(\tau)=-\int d\omega\,K(\tau,\omega)\rho(\omega)$, $K=e^{-\tau\omega}/(e^{-\beta\omega}\pm1)$, SVE; basis size grows logarithmically in $\Lambda=\beta\omega_{\max}$; sampling at extrema of $U_{L-1}$, $\hat U_{L-1}$, boundary points moved inwards, 4 extra frequencies | read (secs. 1, 2, 4) |
| S14 | sparse-ir source, <https://github.com/SpM-lab/sparse-ir>, **MIT**; `pip install sparse-ir`; `FiniteTempBasis`, `TauSampling`, `MatsubaraSampling` | read (README) |
| S15 | H. Shinaoka, D. Geffroy, M. Wallerberger, J. Otsuki, K. Yoshimi, E. Gull, J. Kuneš, *Sparse sampling and tensor network representation of two-particle Green's functions*, SciPost Phys. 8, 012 (2020), arXiv:1909.07519 | abstract |
| S16 | H. Shinaoka, M. Wallerberger, Y. Murakami, K. Nogaki, R. Sakurai, P. Werner, A. Kauch, *Multiscale space-time ansatz for correlation functions of quantum systems based on quantics tensor trains*, PRX 13, 021015 (2023), arXiv:2210.12984, **CC0** | abstract |
| S32 | M. K. Ritter, Y. Núñez Fernández, M. Wallerberger, J. von Delft, H. Shinaoka, X. Waintal, *Quantics tensor cross interpolation for high-resolution parsimonious representations of multivariate functions*, PRL 132, 056501 (2024), arXiv:2303.11819 | abstract |
| S34 | S. Rohshap, M. K. Ritter, H. Shinaoka, J. von Delft, M. Wallerberger, A. Kauch, *Two-particle calculations with quantics tensor trains: solving the parquet equations*, PRR 7, 023087 (2025), arXiv:2410.22975, **CC BY 4.0** | abstract |

## Machine learning, compression, tensor networks

| id | reference | status |
|---|---|---|
| S17 | P. Mehta, M. Bukov, C.-H. Wang, A. G. R. Day, C. Richardson, C. K. Fisher, D. J. Schwab, *A high-bias, low-variance introduction to machine learning for physicists*, Phys. Rep. 810, 1 (2019), arXiv:1803.08823 (also 138.128 literature [S4]) | abstract; PDF fetched |
| S18 | N. Halko, P.-G. Martinsson, J. A. Tropp, *Finding structure with randomness*, SIAM Rev. 53, 217 (2011), arXiv:0909.4061. Alg. 4.1, 4.4, 5.1; **Thm 10.5** $\mathbb E\lVert(I-P_Y)A\rVert_F\le(1+k/(p-1))^{1/2}(\sum_{j>k}\sigma_j^2)^{1/2}$, $k,p\ge2$ | read (Thm 10.5) |
| S19 | C. Eckart, G. Young, *The approximation of one matrix by another of lower rank*, Psychometrika 1, 211 (1936) | not retrieved |
| S20 | L. Onsager, PR 65, 117 (1944) (free energy, internal energy); C. N. Yang, PR 85, 808 (1952) (spontaneous magnetisation) | not retrieved; formulas cross-checked numerically ($u(T_c)=-\sqrt2$, MC agreement) in `test_ising_snapshots.py` |
| S21 | D. P. Kingma, M. Welling, *Auto-encoding variational Bayes*, arXiv:1312.6114 (ICLR 2014): reparameterisation, Gaussian KL in closed form | abstract; PDF fetched |
| S22 | S. J. Wetzel, *Unsupervised learning of phase transitions: from PCA to variational autoencoders*, PRE 96, 022140 (2017), arXiv:1703.02435: first principal component / latent variable ~ magnetisation | read (PCA section, fig. 2: latent parameter vs magnetisation) |
| S23 | J. Carrasquilla, R. G. Melko, *Machine learning phases of matter*, Nature Physics (2017), doi:10.1038/nphys4035, arXiv:1605.01735: fully connected net, 100 sigmoid hidden units; $T_c$ from the crossing of the output with 1/2 | read (architecture, fig. 2) |
| S24 | R. Orús, *A practical introduction to tensor networks: MPS and PEPS*, Ann. Phys. 349, 117 (2014), arXiv:1306.2164 | abstract; PDF fetched |
| S25 | U. Schollwöck, *The density-matrix renormalization group in the age of matrix product states*, Ann. Phys. 326, 96 (2011), arXiv:1008.3477 | abstract; PDF fetched |
| S26 | I. V. Oseledets, *Tensor-train decomposition*, SIAM J. Sci. Comput. 33, 2295 (2011), doi:10.1137/090752286: TT-SVD algorithm and error bound $\lVert A-B\rVert_F\le\sqrt{d-1}\,\delta$ | not retrieved (paywalled); the error identity is re-derived in note 05 and tested |
| S31 | P. Baldi, K. Hornik, *Neural networks and principal component analysis: learning from examples without local minima*, Neural Networks 2, 53 (1989) | not retrieved; the claim (linear AE optimum = PCA subspace) is tested numerically |
| S33 | J. Ballé, V. Laparra, E. P. Simoncelli, *End-to-end optimized image compression*, ICLR 2017, arXiv:1611.01704: learned transform coding optimised for rate + $\lambda$ distortion | abstract |
| S36 | T. M. Cover, J. A. Thomas, *Elements of Information Theory*, 2nd ed., Wiley 2006, ch. 10 (rate-distortion; Gaussian $R(D)=\tfrac12\log_2(\sigma^2/D)$) | not retrieved |

## Analytic continuation and inverse problems

| id | reference | status |
|---|---|---|
| S27 | M. Jarrell, J. E. Gubernatis, *Bayesian inference and the analytic continuation of imaginary-time quantum Monte Carlo data*, Phys. Rep. 269, 133 (1996) | not retrieved |
| S28 | J. Kaufmann, K. Held, *ana_cont: Python package for analytic continuation*, arXiv:2105.11211 (E138 TU Wien): Padé and maxent; $\alpha$ by historic ($\chi^2\approx N$), classic, Bryan, chi2kink | read (sec. on $\alpha$) |
| S29 | H. Yoon, J.-H. Sim, M. J. Han, *Analytic continuation via domain-knowledge free machine learning*, PRB 98, 245101 (2018), arXiv:1806.03841, **CC0**: CNN trained on synthetic (G, A) pairs | abstract |
| S30 | P. C. Hansen, *Discrete Inverse Problems: Insight and Algorithms*, SIAM 2010 (138.128 literature [S4]): SVD filter factors, discrepancy principle, L-curve | not retrieved |

## Not used

- TUWEL: not accessed; nothing here depends on it.
- VoWi: not searched for this course; do so when the 2027W page appears.
