# 01 Project playbook

The PR is one research loop run for a semester: question, baseline, experiment,
validation, write-up. What is graded is the protocol [S1, S2], so the deliverable
is not a model or a library but **a documented answer with numbers, error bars
and a baseline**. Keep a results log from the first day; the protocol is written
from it.

## What the course asks for [S1, S2]

- Project work applying ML in physics, or developing tools, "e.g., for the
  compression of data or in optimization problems, pattern recognition, and the
  prediction of observables".
- 10 ECTS = 250 h; no dates; no TISS registration; topic by arrangement with
  Tomczak or Wallerberger.
- Grade: the protocol. Nothing else is published (note 00).

## Choosing the topic

Criteria, derived from what the protocol has to show:

1. **A known answer somewhere.** A closed form, an exact limit or a trusted code
   (single pole, Onsager, sparse-ir, exact diagonalisation) to validate against.
   Without it, section 3 of the protocol is empty.
2. **A baseline to beat or to match.** IR vs uniform grid, AE vs PCA, MaxEnt vs
   Tikhonov, TT vs dense. "Better than" needs a "than".
3. **A scalar metric** (error at fixed storage, storage at fixed error, $R^2$,
   $L^1$ spectral error) that the question is about.
4. **Laptop scale** for the development loop: one experiment in minutes, the full
   figure set overnight. Scale up only for the final runs.
5. **Inside the supervisor's research**, so the meetings are productive and the
   code base (sparse-ir, w2dynamics) is supported.
6. **Split into a safe core and a risky extension**: the core alone (about 150 h)
   must make a passing protocol.

### Candidates mapped to the lecturers' work

"Fit" is our reading of the public record [S5-S9]; the supervisor decides.

| # | topic | lecturer fit | notes | start from | risk |
|---|---|---|---|---|---|
| A | **Learned vs IR compression** of $G(\tau)$ for a restricted family (e.g. DMFT-like or few-pole spectra): does an AE or a data-adapted basis beat the model-independent IR at equal storage? | Wallerberger: IR, sparse-ir [S10, S13] | 02, 03, 04 | `ir_toy.py`, `autoencoder_compression.compare_poles` | low: IR is the baseline, the single-pole result already shows a gap |
| B | **Sparse sampling under noise**: fitting $G_l$ from noisy QMC-like samples; regularised fits, noise propagation, choice of sampling points | Wallerberger [S12, S13] | 03, 06, 08 | `IRBasis.tau_sampling_points`, `continuation.tikhonov` | low |
| C | **Quantics tensor trains** for a two-variable function ($G(\mathbf k,i\nu)$ of a tight-binding model, a two-particle object of the Hubbard atom): bond dimension vs $\beta$ and grid size, vs IR | Wallerberger [S16, S32, S34] | 05 | `tt_svd.quantics` | medium: TCI needed beyond $2^{20}$ points |
| D | **ML analytic continuation**: supervised network vs MaxEnt on synthetic data, IR coefficients as input, calibrated uncertainty | E138 (ana_cont [S28]); either lecturer | 03, 06 | `continuation.py` | medium: easy to get numbers, hard to make them meaningful |
| E | **Predicting observables** from configurations or band data (Tomczak's BandITT "band interpolation" [S9] suggests ML interpolation of $\varepsilon_n(\mathbf k)$ vs Fourier/Wannier interpolation) | Tomczak [S8, S9] (our extrapolation) | 07 | `observables.py` | high: needs his data and availability |
| F | **Phase classification / unsupervised order parameters** for a model the group studies | generic [S22, S23] | 04, 07 | `ising_snapshots.py` | low, but least connected to the lecturers |

Bad choices: a topic without a reference solution; "apply a transformer to X"
without a physics question; anything needing GPU weeks; data only the
supervisor can produce, unless they commit to producing it in September.

## First contact (draft, to send end of June 2027)

> Subject: 138.129 project in 2027W, QIST 3rd semester
>
> Dear Dr. Wallerberger, I am in the QIST master (066 558) and took 138.128 this
> semester. I would like to do the 138.129 project in 2027W. I am interested in
> compression of imaginary-time propagators: for example, whether a learned
> representation can beat the IR basis for a restricted class of spectra, or
> how sparse sampling behaves with noisy data. I have worked through the IR and
> sparse-sampling papers and reproduced a small IR basis. Would you have time for
> a short meeting in September to agree a topic? Best regards, ...

Adapt the topic line; one paragraph; attach nothing. If no reply in two weeks,
ask after a 138.128 lecture or send a single reminder; copy Tomczak only if the
topic is his.

## Milestones (2027W, 250 h)

| by | what | h (cum.) |
|---|---|---|
| 30.09.2027 | topic agreed; one-page plan: question, metric, baseline, reference solution, core vs extension, meeting cadence, protocol format and deadline | 30 |
| end Oct | baseline reproduced and validated (tests pass against the reference); repository, environment, results log in place | 70 |
| mid Nov | first main result with 5 seeds; meeting: continue core or open the extension | 120 |
| mid Dec | core experiments complete; figures drafted from scripts | 170 |
| mid Jan | extension or robustness checks; error analysis (note 08) | 210 |
| end Jan | protocol draft to the supervisor | 240 |
| Feb | revisions, final commit tagged, protocol submitted | 250 |

Dates after September are a suggestion; replace them with what the supervisor says.

## The loop, per experiment

1. **Hypothesis** in the log before running: what should happen and why
   ("AE with $k=2$ beats IR truncated at 2 for single-pole $G$ by $\ge10\times$").
2. **One change** per run; commit it; record the git hash.
3. **Validate**: tests still pass; the reference case still reproduces.
4. **Measure** with seeds and error bars (note 08).
5. **Log**: expected, measured, verdict, one-line explanation or "unexplained".
6. **Keep failures.** A negative result with a reason is protocol material.

Results-log template (`results/log.md`):

```
| # | date | commit | hypothesis | setup | metric (mean +- sem, n) | baseline | verdict |
|---|------|--------|------------|-------|-------------------------|----------|---------|
| 0 | 10-15 | a1b2c3d | IR L=26 reproduces single pole to 1e-8 | beta=wmax=10 | 6.2e-9 max err | closed form | ok |
| 1 | 10-22 | d4e5f6a | k=1 AE beats PCA(1) on single poles | 64 tau, 1500 train | 1.2e-4 +- ? (5 seeds) | PCA 1.3e-2 | ok, PCA needs k=5 |
| 2 | 10-29 | ... | MLP-AE beats PCA on Ising | L=12, 900 train | 0.62 test / 0.37 train | PCA 0.50 | no: memorises |
```

## Protocol structure

Section list, statistics and figure rules: [08](08-writing-the-protocol.md);
skeleton: [`protocol_template.md`](protocol_template.md).

## Reproducibility checklist

- [ ] One repository; the protocol cites a tag and commit hash.
- [ ] Environment pinned (lock file); Python and library versions in the appendix.
- [ ] Every figure regenerates from one command on a clean checkout.
- [ ] Seeds fixed and listed; results averaged over $\ge5$ seeds or independent chains.
- [ ] Tests encode the validation claims (closed forms, library cross-checks).
- [ ] Generated data reproducible from scripts; external data with a DOI or supervisor's path.
- [ ] Runtimes and hardware stated.
- [ ] Hyperparameters and their selection procedure (never on the test set) in an appendix.
- [ ] Licence file in the repository.

## Pitfalls

- Starting in October without a topic: 250 h do not fit into what remains.
- A topic whose success depends on data or code the supervisor has not committed to.
- Optimising a model before the baseline and the reference check exist.
- One seed, no error bars, no baseline (note 08).
- Writing the protocol in the last two weeks from memory instead of from the log.

## Questions

1. **What must be true of a topic before you agree to it?** A reference solution for
   validation, a baseline, a scalar metric, laptop-scale iteration, and a core that
   passes on its own in about 150 h.
2. **Why propose two or three topics in the first e-mail rather than one?** No dates,
   no registration: the supervisor's interests and time decide; offering choices within
   their research makes a yes likely and the first meeting concrete.
3. **A planned experiment fails. What goes into the protocol?** The hypothesis, the
   measured numbers, the diagnosis (e.g. memorisation: train 0.37 vs test 0.62) and
   what it implies; it demonstrates understanding and is part of the 250 h.
4. **How do you keep the protocol reproducible when the code changes weekly?** Log the
   commit hash per result; regenerate all figures from scripts at the final tag; pin
   the environment.
5. **Which candidate topic has the lowest risk and why?** A (or B): the IR baseline
   and closed forms exist in the repo, the supervisor wrote the reference library, and
   the single-pole experiment already shows a measurable gap to investigate.
