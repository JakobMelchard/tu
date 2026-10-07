# 11 Research topics and paper reading

**Correction to a common belief about this course.** The current assessment does *not* include a separately graded paper presentation: TISS lists coursework, a practical project and a final oral exam [S1, S2], and the "presentation of an advanced research topic" wording belongs to the 2020W–2021S era only [S3, S7]. See [`00-exam-focus.md`](00-exam-focus.md) §2. What *is* current is the learning outcome "understand, summarise, and present machine learning research papers" [S2] and the lecturers' statement that coursework includes "understanding and explaining a proof" [S6]. So paper reading is examinable through the coursework, the project and the oral — just not as a graded talk.

On that reading, the oral will probe whether you understood a paper's *claim* (assumptions, quantifiers, tightness) rather than its narrative. This note is a working method: how to read a theory paper, a summary template, a presentation skeleton, a checklist for evaluating claims, one filled-in example, and a per-topic list of the classic papers with what each one shows. The project is the likeliest place this is used, and [`00-exam-focus.md`](00-exam-focus.md) §5 argues from the 6 ECTS twin's topic list [S4] that it will lean towards the group's own research: graph neural networks, expressivity and logics, and interpretability/robustness/privacy/fairness.

## Definitions

1. **Claim of a theory paper.** A statement of the form "under assumptions $A$, for all (or some) $n,\varepsilon,\delta,\mathcal D,\dots$, algorithm/estimator $\hat h$ satisfies inequality $I$ with probability $\ge1-\delta$ (or in expectation)". The four ingredients $A$, quantifiers, object, inequality are what you must extract.

2. **Vacuous bound.** A bound whose right-hand side exceeds the trivial value (1 for a probability or 0-1 risk, $\mathrm{Var}(y)$ for a regression risk) at the sample sizes and model sizes of the accompanying experiments.

3. **Tight bound.** A bound with a matching lower bound (same dependence on the relevant quantities up to constants or logarithmic factors). "Minimax optimal" means: no estimator does better in the worst case over the assumed class of distributions.

4. **Distribution-free vs distribution-dependent.** Whether the guarantee holds for all $\mathcal D$ (PAC, VC) or under a distributional assumption (margin/noise conditions, sub-Gaussian design, source conditions in kernel regression).

5. **Three-pass reading (Keshav 2007).** Pass 1 (5 min): title, abstract, introduction, section headings, the main theorem, conclusions. Pass 2 (1 h): read everything except proofs, note every assumption, redraw figures, mark unread references. Pass 3 (several hours): re-derive the main result, reconstruct the proof structure, find the step that carries the new idea.

## Results

There are no theorems here; the "results" are procedures.

### How to read a theory paper

1. **Locate the main theorem** and copy it verbatim, with all quantifiers and every constant. Then rewrite it in the notation of these notes ($n$, $\varepsilon$, $\delta$, $L_{\mathcal D}$, $L_S$, $\mathfrak R_n$, $d$).
2. **List the assumptions** in a table: boundedness ($\|x\|\le R$, $|y|\le Y$), i.i.d. sampling, realisability, convexity of the loss, Lipschitzness, eigenvalue decay, separability, width $\to\infty$, etc. For each: is it needed for the proof, or for the statement to be meaningful? Which one would a practitioner not be able to check?
3. **Identify the closest prior result** (usually cited in the introduction as "improves upon") and write both bounds side by side with the same notation. The difference is the contribution.
4. **Find the proof technique**: concentration + union bound (notes 02–04), symmetrisation + Rademacher/contraction (05), stability (06), bias–variance/random-matrix (07, 10), representer/RKHS (08), duality/KKT (09), linearisation/NTK (10), PAC-Bayes, or something new. Name the one lemma that carries the improvement.
5. **Reproduce one step** of the proof in full. Usually the "key lemma" is 10 lines and the rest is bookkeeping.
6. **Check the experiments against the theorem**: same model, same regime ($n$, $d$, $\lambda$), same quantity plotted? Do they plot the bound, or only the phenomenon?

### Summary template (1–2 pages)

```
Title, authors, venue, year. One-sentence contribution.

1. Problem. What is being learned/estimated, and what was unsatisfactory before.
2. Setting and assumptions. Data model, hypothesis class, algorithm, loss;
   assumptions A1..Ak with a one-line comment each (realistic? checkable?).
3. Main result. Theorem stated precisely, in course notation, all quantifiers.
   Plug in numbers: n = 10^3, 10^5; is it vacuous?
4. Proof idea. Five lines: the decomposition, the key lemma, the inequality used.
5. Comparison. Table: this paper vs 2-3 prior results, same notation, columns
   = dependence on n, d, delta, constants, assumptions.
6. Experiments (if any). What is plotted, does it match the theorem's regime.
7. Limitations. Where the assumptions fail; what the theorem does NOT claim.
8. Questions for the authors / follow-ups.
```

### Presentation skeleton (15 minutes, 8–10 slides)

1. Motivation (1 slide): the phenomenon or gap, one picture.
2. Setting (1): notation, assumptions as a short list.
3. Main theorem (1): stated once, completely, with quantifiers; box the new term.
4. Proof idea (2–3): the decomposition; the key lemma with its one-line proof; how the pieces combine. Show one derivation step in full on a slide.
5. Experiments (1): the one plot that matters, with axes explained.
6. Discussion (1): comparison table, limitations, open questions.
7. Backup slides: constants, secondary lemmas, extra plots.

Rules: state the theorem on a single slide; never read from the paper; know the answer to "what happens if assumption A2 is dropped" and "what is the lower bound"; rehearse plugging numbers into the bound out loud; finish with what you would do next.

### Checklist for evaluating claims

- Are the assumptions realistic, and which experiments violate them?
- Plug in numbers: is the bound vacuous at the paper's own $n$? At $n=10^6$?
- Are constants hidden in $O(\cdot)$ or $\tilde O(\cdot)$? Is there a $\log n$ or $\log(1/\delta)$ that matters?
- Dependence on $d$, $n$, $\delta$, $\lambda$: is it tight? Is there a matching lower bound, in the paper or elsewhere (NFL, minimax)?
- Is it distribution-free, or does it need a margin/noise/spectrum condition? Is that condition checkable from data?
- Is the algorithm analysed the algorithm that was run (learning rate, initialisation, early stopping, parametrisation)?
- Is the bound about the output of the algorithm (algorithm-dependent) or about the whole class (uniform)? Note 10 explains why this matters.
- Does the experiment measure the quantity in the theorem (e.g. test 0-1 error vs. a surrogate loss; excess risk vs. absolute risk)?
- Are baselines tuned as carefully as the proposed method?
- Would a simpler explanation (a linear model, a kernel) produce the same plot?
- What is the paper's own list of limitations, and what did it omit?

### Examiner's question types

"State the main theorem." "What is the role of assumption X?" "Give the proof idea in three sentences." "Is the bound tight? How do you know?" "Compare with the classical VC / Rademacher bound." "What happens in the limit $n\to\infty$ / $\lambda\to0$ / width $\to\infty$?" "Is this an upper or lower bound, on what, with what probability?" "How would you test the claim empirically?" "Which result from the course does the proof use?"

## Worked example

Summary of **Belkin, Hsu, Ma & Mandal (2019), "Reconciling modern machine-learning practice and the classical bias–variance trade-off", PNAS 116(32) 15849–15854** [S35]**.**

*Contribution.* Introduces the "double descent" risk curve: test risk as a function of model capacity decreases, increases to a peak at the interpolation threshold, and decreases again beyond it; supported by experiments on random Fourier features, random ReLU features, two-layer networks, random forests and boosting, and by an analysis of random-features least squares.

*Problem.* Classical theory (notes 04–06) predicts a U-shaped test risk vs capacity, with the sweet spot below interpolation, yet practical neural nets are trained to zero training loss and generalise.

*Setting and assumptions.* Regression/classification with $n$ training points; models of capacity $N$ (number of random features / hidden units / total leaves); learner = ERM with, in the overparameterised regime ($N>n$), the *minimum-norm* interpolating solution (for random features: min-$\ell_2$-norm coefficients; for networks: an explicit "weight reuse" training scheme to approximate this). Assumption A1: the learner returns the min-norm interpolator — realistic for least squares trained by GD from zero (Theorem 10.6), only heuristic for the neural-net experiments. A2 (for the analytic part): random Fourier features $\phi(x)=\cos(\langle w,x\rangle+b)$ with Gaussian $w$, so that as $N\to\infty$ the model is kernel regression with the Gaussian kernel.

*Main result (informal, as stated in the paper).* For the random-features model with min-norm interpolation, the test risk as $N$ varies past $n$ exhibits a peak at $N=n$ and then decreases monotonically towards the risk of kernel ridgeless regression (the $N=\infty$ limit), which has the smallest RKHS norm among all interpolants. The paper does not give a closed-form risk; that was done later (Theorem 10.8 for the linear case, Mei & Montanari 2022 for random features).

*Proof idea.* (i) For $N<n$: ERM over an $N$-dimensional linear class, classical bias–variance, variance $\approx\sigma^2N/n$ grows. (ii) At $N=n$ the design matrix is square and typically near-singular: the min-norm solution has huge norm and the variance explodes. (iii) For $N>n$: the min-norm interpolator $\hat w=\Phi^+y$ has $\|\hat w\|$ decreasing in $N$ (more columns, same constraints), and as $N\to\infty$ it converges to the kernel interpolant $\hat f=k(\cdot,X)K^{-1}y$, the minimum-RKHS-norm interpolant; smaller norm = smoother function = better generalisation via the norm-based bounds of note 05 (the argument in the paper is at this level of rigour).

*Comparison.*

| | Classical U-curve [S9 ch. 5–7] | Belkin et al. 2019 [S35] | Hastie et al. 2022 [S36] |
|---|---|---|---|
| regime | $N<n$ | all $N$ | $N,n\to\infty$, $N/n\to\gamma$ |
| learner | ERM | min-norm ERM | min-norm LS / ridge |
| result | risk $\le$ approx + $\sqrt{N/n}$ | empirical curve + heuristic | exact limiting risk $\sigma^2\gamma/(1-\gamma)$, $\ldots$ |
| tight | no | n/a | yes (exact) |

*Experiments.* MNIST subsets with $n=10^4$, random Fourier features $N$ from $10^2$ to $10^5$; test error peaks exactly at $N=n$ and the $N=10^5$ error is below the best $N<n$ error. Also a two-layer net on MNIST with the number of hidden units swept, and random forests with increasing leaves. The peak is sharp for least-squares-type models and weaker for boosting/forests.

*Limitations.* No quantitative theorem; neural-net experiments use a non-standard training scheme to enforce the min-norm behaviour; the label noise level, which decides whether the second descent beats the first minimum (note 10 worked example), is not studied systematically; the "capacity" axis conflates different notions.

*Questions for the authors.* What is the curve with optimally tuned ridge (answer from later work: no peak)? Does the second descent go below the classical minimum for all noise levels (no)? Is the peak present under early stopping (later work: much reduced)?

## Pitfalls

- Summarising the introduction instead of the theorem: the examiner will ask for the quantifiers.
- Reporting $O(\cdot)$ rates without checking the constants and the log factors — many "improved" bounds are worse at any practical $n$.
- Treating an expectation bound as a high-probability bound or vice versa.
- Confusing an upper bound on the *excess* risk with a bound on the risk.
- Presenting a proof by reading the paper's chain of lemmas; present the *decomposition* and one full step instead.
- Claiming a paper "explains" a phenomenon when it exhibits a model in which the phenomenon occurs; the examiner will ask whether the model's assumptions hold in the practical case.
- Ignoring the lower-bound literature: a bound that is tight has a matching lower bound somewhere, and knowing where is half the evaluation.

## Questions

**Q: How would you check whether a generalisation bound is vacuous?**
**A:** Plug in the paper's own $n$, $\delta$, norms/VC dimension with the explicit constants; compare the right-hand side with 1 (0-1 loss) or with $\mathrm{Var}(y)$ (regression). If the constants are hidden, reconstruct them from the proof.

**Q: What are the four things you must extract from a theorem before you can evaluate it?**
**A:** Assumptions, quantifiers (for all vs there exists, in expectation vs with probability $1-\delta$), the object bounded (risk, excess risk, generalisation gap, number of mistakes), and the inequality's dependence on $n,d,\delta$ and constants.

**Q: How do you decide whether a bound is tight?**
**A:** Look for a matching lower bound: NFL / minimax results (note 03), the lower half of the fundamental theorem (note 04), or a lower bound in the paper. Same dependence on $n$ and $d$ up to constants/logs means tight.

**Q: A paper proves a bound for gradient flow with infinite width and shows experiments with SGD at width 512. What do you say?**
**A:** The algorithm analysed is not the algorithm run: finite width, discrete steps, stochastic gradients, standard parametrisation. Ask whether the NTK regime assumptions (Thm 10.5) hold at width 512 and whether the experiment measures the quantity in the theorem.

**Q: What distinguishes a uniform-convergence bound from an algorithm-dependent one, and why does it matter for a deep-learning paper?**
**A:** Uniform bounds hold for all $h\in\mathcal H$ simultaneously and depend only on $\mathcal H$; algorithm-dependent bounds (stability, implicit bias, PAC-Bayes around the trained weights) depend on what the algorithm outputs. Since deep nets can fit random labels (Zhang et al.), uniform bounds over the architecture are vacuous, so only the second kind can be informative.

**Q: What is the first thing to write on a presentation slide about a theorem?**
**A:** The full statement with all quantifiers and assumptions, in a single box, before any interpretation.

**Q: Which result from this course would you use to attack the claim "our model generalises because it has few parameters"?**
**A:** VC dimension is not the number of parameters ($\sin(\omega x)$ has infinite VC dimension with one parameter, note 04); and norm-based/Rademacher bounds (note 05) show the relevant capacity can be a norm, not a count.

## Classic papers per topic

**ERM, regularisation, stability**
- Vapnik (1998), *Statistical Learning Theory*: the ERM/SRM framework, uniform convergence as the central object.
- Bousquet & Elisseeff (2002), "Stability and generalization": uniform stability $\beta$ implies generalisation gap $O(\beta+\sqrt{\log(1/\delta)/n})$; RLM with strongly convex regulariser is $O(1/(\lambda n))$-stable.
- Bartlett & Mendelson (2002), "Rademacher and Gaussian complexities": the data-dependent capacity measure, contraction, margin bounds for kernels and networks.
- Hardt, Recht & Singer (2016), "Train faster, generalize better": SGD with few passes is uniformly stable, giving algorithm-dependent bounds for non-convex training.

**PAC learning**
- Valiant (1984), "A theory of the learnable": the PAC model, efficient learnability of conjunctions and $k$-CNF.
- Blumer, Ehrenfeucht, Haussler & Warmuth (1989), "Learnability and the Vapnik–Chervonenkis dimension": finite VC dimension characterises PAC learnability; the $d\log(1/\varepsilon)/\varepsilon$ sample complexity.
- Kearns & Vazirani (1994), *An Introduction to Computational Learning Theory*: the computational side (hardness, boosting, noise).
- Hanneke (2016), "The optimal sample complexity of PAC learning": removes the $\log(1/\varepsilon)$ factor with a non-ERM learner.

**VC theory**
- Vapnik & Chervonenkis (1971), "On the uniform convergence of relative frequencies of events to their probabilities": growth function, the double-sample argument, VC dimension.
- Sauer (1972); Shelah (1972): the Sauer–Shelah lemma (independently, in combinatorics and model theory).
- Haussler (1995), "Sphere packing numbers for subsets of the Boolean $n$-cube with bounded VC dimension": covering numbers $O((c/\varepsilon)^d)$ for VC classes, the link to chaining.
- Talagrand (1994), "Sharper bounds for Gaussian and empirical processes": the sharp form of uniform convergence for VC classes.

**Kernels and SVM**
- Boser, Guyon & Vapnik (1992), "A training algorithm for optimal margin classifiers": the kernel trick applied to the maximum-margin hyperplane.
- Cortes & Vapnik (1995), "Support-vector networks": soft margin.
- Schölkopf, Herbrich & Smola (2001), "A generalized representer theorem": the version with arbitrary loss and strictly increasing regulariser.
- Platt (1998), "Sequential minimal optimization": the two-variable dual solver.
- Rahimi & Recht (2007), "Random features for large-scale kernel machines": approximate shift-invariant kernels by $m$ random Fourier features with error $O(1/\sqrt m)$.
- Steinwart & Christmann (2008), *Support Vector Machines*: the rigorous reference for consistency and rates.

**Least squares and high-dimensional regression**
- Caponnetto & De Vito (2007), "Optimal rates for the regularized least-squares algorithm": minimax rates for kernel ridge regression under source and capacity conditions.
- Hastie, Montanari, Rosset & Tibshirani (2022), "Surprises in high-dimensional ridgeless least squares interpolation": exact asymptotic risk, double descent for linear models.
- Bartlett, Long, Lugosi & Tsigler (2020), "Benign overfitting in linear regression": when the min-norm interpolator has small excess risk despite fitting noise.
- Mei & Montanari (2022), "The generalization error of random features regression": exact double descent for random features.

**Deep learning theory**
- Cybenko (1989); Hornik (1991); Leshno et al. (1993): universal approximation and its characterisation (non-polynomial activation).
- Barron (1993): $O(1/\sqrt m)$ approximation rate for functions with bounded Fourier moment.
- Telgarsky (2016), "Benefits of depth in neural networks": exponential depth separation.
- Bartlett, Harvey, Liaw & Mehrabian (2019): VC dimension $\Theta(WL\log W)$ for ReLU nets.
- Zhang, Bengio, Hardt, Recht & Vinyals (2017), "Understanding deep learning requires rethinking generalization": random-label fitting; capacity-of-the-class bounds cannot explain generalisation.
- Neyshabur, Tomioka & Srebro (2015), "In search of the real inductive bias"; Neyshabur, Bhojanapalli, McAllester & Srebro (2017), "Exploring generalization in deep learning": norm-based capacity measures and their correlation with generalisation.
- Bartlett, Foster & Telgarsky (2017), "Spectrally-normalized margin bounds for neural networks".
- Dziugaite & Roy (2017), "Computing nonvacuous generalization bounds for deep (stochastic) neural networks with many more parameters than training data": PAC-Bayes with optimised posterior.
- Jacot, Gabriel & Hongler (2018), "Neural tangent kernel: convergence and generalization in neural networks".
- Arora, Du, Hu, Li & Wang (2019), "Fine-grained analysis of optimization and generalization for overparameterized two-layer neural networks": data-dependent NTK generalisation bound $\sqrt{y^\top\Theta^{-1}y/n}$.
- Soudry, Hoffer, Nacson, Gunasekar & Srebro (2018), "The implicit bias of gradient descent on separable data".
- Belkin, Hsu, Ma & Mandal (2019) [S35]: double descent.
- Nagarajan & Kolter (2019), "Uniform convergence may be unable to explain generalization in deep learning".

**Active research directions (2020s)**
- Benign overfitting beyond linear models (kernels, two-layer nets); interpolation with adversarial robustness.
- Scaling laws (Kaplan et al. 2020; Hoffmann et al. 2022) and their toy-model explanations (power-law feature spectra).
- Transformers and in-context learning as learning algorithms (Garg et al. 2022; von Oswald et al. 2023): what function classes can be learned in context, and with what sample complexity.
- Learning under distribution shift and domain adaptation bounds (Ben-David et al. 2010 and successors).
- PAC-Bayes and compression bounds tight enough for large models (Lotfi et al. 2022).
- Algorithmic stability of SGD in the non-convex case; the role of learning rate and batch size (Hardt et al. 2016 and follow-ups).
- Feature learning beyond NTK: mean-field limits, $\mu$P parametrisation (Yang & Hu 2021), and the "lazy vs rich" dichotomy.

## Code

No dedicated module. For a paper on double descent or benign overfitting, `src/py/deep_theory.py` (`double_descent_curve`) is a starting point for a reproduction; for margin/Rademacher papers, `src/py/rademacher.py` and `src/py/svm.py`; for stability/regularisation papers, `src/py/regularisation.py` and `src/py/least_squares.py`.

## References

- Keshav (2007), "How to read a paper", ACM SIGCOMM CCR 37(3).
- Shalev-Shwartz & Ben-David, *Understanding Machine Learning*; Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning*: the two references whose notation the summaries should use.
- The papers listed above.
