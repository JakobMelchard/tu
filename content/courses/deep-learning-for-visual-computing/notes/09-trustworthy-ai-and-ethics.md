# 09 Algorithmic governance, trustworthy AI and ethics

> TISS item 9 [S1, S3]. Catalogue weight: two 2022S questions (data bias and
> protected attributes; explainability, fairness assessment, in-processing)
> [S7], medical-data and XAI questions in 2020 [S8]. Sources: HLEG guidelines
> [S44], EU Charter Art. 21 [S45], fairness papers [S37], Gender Shades [S38],
> model cards [S36], AI Act [S39, S40]. Explanation methods: note 08 and
> [ADL 08](../../applied-deep-learning/notes/08-explainable-ai.md).
> ML security, adversarial examples, privacy: [ML 16](../../machine-learning/notes/16-ml-security-privacy-and-mlops.md).

## Definitions

**Algorithmic governance.** The rules, processes and institutions that decide
how automated decision systems may be built, deployed, audited and contested:
law (AI Act, anti-discrimination law, GDPR), standards, internal review,
documentation.

**Trustworthy AI** (EU High-Level Expert Group, 08.04.2019 [S44]): lawful,
ethical and robust; seven requirements: human agency and oversight;
technical robustness and safety; privacy and data governance; transparency;
diversity, non-discrimination and fairness; societal and environmental
well-being; accountability.

**Data bias** (the 2022S list [S7]; framework of Suresh & Guttag [S37]):

| type | mechanism | vision example |
|---|---|---|
| historical | the world the data records is already unequal | image search for "CEO" returns mostly men |
| representation | some groups under-sampled | face datasets 80-86 % lighter-skinned [S38] |
| measurement | the proxy or sensor differs by group | a camera's auto-exposure tuned to light skin |
| aggregation | one model for groups with different relations | one dermatology model across skin types |
| evaluation | benchmark not representative, or wrong metric | accuracy on a lighter-skinned test set |
| deployment | used for a purpose or population it was not built for | a lab classifier used for policing |

**Protected attributes.** Characteristics on which discrimination is
prohibited. EU Charter Art. 21(1) [S45]: sex, race, colour, ethnic or social
origin, genetic features, language, religion or belief, political or any other
opinion, membership of a national minority, property, birth, disability, age,
sexual orientation (non-exhaustive, "such as"). Dropping the attribute from
the input does not remove it: correlated proxies (postcode, clothing, image
background) leak it.

**Group fairness metrics** for a binary decision $\hat Y$, label $Y$,
attribute $A$:
- demographic parity: $P(\hat Y = 1\mid A = a)$ equal for all $a$;
- **equal opportunity** [S37]: equal TPR $P(\hat Y=1\mid Y=1, A=a)$;
- **equalised odds** [S37]: equal TPR **and** FPR;
- predictive parity / calibration: equal $P(Y=1\mid\hat Y=1, A=a)$.
**Impossibility** [S37 Chouldechova, Kleinberg et al.]: if base rates
$P(Y=1\mid A)$ differ, a classifier cannot be calibrated and have equal FPR
and FNR across groups (unless it is perfect). Choosing a metric is a value
judgement, not a technicality.

**Mitigation.** *Pre-processing*: rebalance, reweight or relabel data.
*In-processing*: change the training objective (fairness constraints or
penalties, adversarial removal of $A$ from the representation).
*Post-processing*: group-specific thresholds on the scores (Hardt et al.
[S37]). Why in-processing is hard for a running system [S7]: it requires
retraining with a new objective, the protected attribute at training time
(often not collected, or legally sensitive), re-validation of accuracy, which
usually drops, and re-certification; post-processing works on a frozen model.

**Explainability** [S7, S8]. Why: user trust, debugging, detecting spurious
features and bias, legal duties (transparency and human oversight in the AI
Act), contestability. What: global (what the model uses in general) vs local
(why this prediction); intrinsic vs post-hoc (note 08).

**Model cards** [S36]: a short document shipped with a model: model details,
intended use (and out-of-scope uses), factors (groups, instrumentation,
environments), metrics, evaluation data, training data, **quantitative
analyses disaggregated by group**, ethical considerations, caveats and
recommendations.

**Gender Shades** [S38]: commercial gender classifiers had error rates up to
34.7 % for darker-skinned women and at most 0.8 % for lighter-skinned men; the
benchmarks IJB-A and Adience were 79.6 % and 86.2 % lighter-skinned. The
canonical example of representation + evaluation bias in vision.

## The EU AI Act in two paragraphs

Regulation (EU) 2024/1689 [S39], in force since 01.08.2024, regulates AI by
**risk**. *Unacceptable* practices are banned from 02.02.2025 (Art. 5); for
vision that means untargeted scraping of facial images from the internet or
CCTV to build recognition databases, emotion recognition at work and in
education (except medical or safety reasons), biometric categorisation that
infers race, religion, sexual orientation and similar traits, and real-time
remote biometric identification in public spaces by law enforcement except
for three narrow purposes (victims, imminent threats, suspects of serious
crimes). *High-risk* systems (Annex III: biometrics, critical infrastructure,
education, employment, essential services, law enforcement, migration,
justice; Annex I: safety components of regulated products such as medical
devices) need risk management, data governance (training data relevant,
representative, examined for bias), technical documentation, logging,
transparency to deployers, human oversight, accuracy and robustness, and a
conformity assessment. *Limited-risk* systems carry transparency duties
(Art. 50: tell people they interact with AI, mark synthetic images and
deepfakes). General-purpose models have their own obligations from
02.08.2025. Fines reach EUR 35 M or 7 % of worldwide turnover for prohibited
practices (Art. 99).

Timing changed in 2026: the **Digital Omnibus on AI** (reported as Regulation
(EU) 2026/1744, in force 27.07.2026 [S40]; number not verified at EUR-Lex)
moved the Annex III high-risk obligations from 02.08.2026 to **02.12.2027**
and Annex I to **02.08.2028**, and added prohibitions on generating
non-consensual intimate imagery and CSAM from 02.12.2026. So by the time of a
2027S exam: prohibitions and GPAI rules apply, Art. 50 transparency applies,
high-risk obligations are months away. Check the dates again before the exam;
the course may teach the pre-omnibus timeline.

## Worked example: fairness metrics by hand

Two groups of 100, same classifier:

| | positives | TP | FN | FP | TN | TPR | FPR | $P(\hat Y=1)$ | PPV |
|---|---|---|---|---|---|---|---|---|---|
| A | 50 | 40 | 10 | 10 | 40 | 0.80 | 0.200 | 0.50 | 0.80 |
| B | 20 | 10 | 10 | 5 | 75 | 0.50 | 0.063 | 0.15 | 0.67 |

Demographic parity gap 0.35; equal-opportunity gap 0.30; equalised odds
violated in both rates (0.30, 0.14); PPV gap 0.13. Overall accuracy
$(80 + 85)/200 = 0.825$ hides all of it. Lowering B's threshold until
$\mathrm{TPR}_B = 0.8$ (post-processing) would close the opportunity gap at
the cost of more false positives in B. Base rates differ (0.5 vs 0.2), so no
threshold choice satisfies calibration and equalised odds together.

## Pitfalls

- "Remove the protected attribute and the model is fair" (proxies).
- Reporting one aggregate accuracy: always disaggregate by group [S36].
- Treating fairness metrics as compatible; with unequal base rates they are not.
- Quoting the AI Act high-risk date as 02.08.2026: postponed [S40].
- Confusing explainability with fairness: an explanation can reveal bias, it
  does not remove it.

## Exam-style questions

1. **What is data bias? Name and explain three types. What is a protected
   attribute? List four.** *(22)* Table above; any four of Art. 21(1).
2. **Why should models be explainable, and what does that mean?** *(22)*
   Trust, debugging, bias detection, legal compliance; being able to state,
   globally or for one decision, which input evidence drove the output.
3. **How can fairness be assessed?** *(22)* Choose a group metric that fits
   the harm (equal opportunity when false negatives hurt, demographic parity
   for allocation), compute it per group on representative data with
   confidence intervals, report disaggregated results (model card).
4. **Why is in-processing hard for a running AI solution?** *(22)* Needs
   retraining with a changed objective and the protected attribute, costs
   accuracy, requires re-validation; post-processing is the practical fix.
5. **Classify under the AI Act: (a) a face-recognition database built from
   scraped web photos, (b) emotion recognition of students in exams, (c) a CV
   screening model, (d) an image generator.** *(ours)* (a), (b) prohibited
   (Art. 5); (c) high-risk (employment, Annex III, obligations from
   02.12.2027); (d) transparency duties (Art. 50) and GPAI rules if built on a
   general-purpose model.

## Code

No module: the fairness table is a hand calculation, and the explanation
methods are in `src/py/gradcam.py` (note 08).
