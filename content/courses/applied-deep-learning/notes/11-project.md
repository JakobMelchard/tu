# 11 The project

The grade in 194.077 comes from one individual project delivered in three assignments — **Initiate**, **Hacking**, **Deliver** [S5, S12–S14] — which between them produce **five graded deliverables worth 10 points each**: the two intermediate assignments, a demo application, a ≤5-page report, and a ≤4-minute live presentation. There is no written exam [S1]. The 75 h nominal budget is fixed [S1] (students report 61 h to over 100 h [S5, S11]), the machine is your own [S5], and the most common way to lose points is not a weak model but a problem that cannot be finished, a missing baseline, a comparison that is not like-for-like, or — the one people forget until it is too late — **no demo application**, which is a tenth of the grade in its own right [S14].

[`00-exam-focus.md`](00-exam-focus.md) is the authority on *what* is assessed and *when*: read it first. This note is the operating procedure for actually doing the work: how to choose a problem that fits the budget, how to size data and compute, which baselines and error analyses are mandatory, and how to compare honestly. The skeleton to copy is `src/project_template/`; the deployment half of assignment 3 is [`12-serving-and-deployment.md`](12-serving-and-deployment.md).

## Concepts

### Choosing a problem

Criteria, all required: (1) personal interest, since 45 h alone on a dull task fails, and **creativity is one of the five graded criteria** [S5]; (2) data available today with a licence that allows use and redistribution of derived results (CC, MIT, ODbL; not "research use on request"); (3) feasible on the hardware *you* have [S5]: a training run $\le 2$ h, whole project $\le 45$ h of programming including the failures; (4) uses at least one of the eight course topics — CNNs, RNNs, deep RL, autoencoders/generative models, transformers, GNNs, explainable AI, LLMs — which TISS states as a hard requirement [S1]; (5) a measurable metric with something to compare against; (6) **an output that can be demonstrated interactively**, because assignment 3 is graded on a demo application [S14] and a project whose result is a number in a log file has nothing to demo.

**The four project types are official and named** [S5, S12]; you must declare one in assignment 1:

| type | what you do | bonus point if |
|---|---|---|
| **Bring your own data** | Collect a dataset semi-automatically (hundreds to thousands of samples) and annotate it. You must still train and run at least a simple network on it, as a baseline for future users. | you publish the dataset [S12]; see FAIR in [`12-serving-and-deployment.md`](12-serving-and-deployment.md) |
| **Bring your own method** | Build or re-implement an architecture on an existing public dataset. Using an existing implementation is fine, but you must alter it and try to improve the results. | you improve on the state of the art |
| **Beat the classics** | Take a problem with an established *traditional* algorithm (the sheet's example: edge detection) and solve it with deep learning. Both must be evaluated with **the same metric**. | your approach beats the traditional one |
| **Beat the stars** | Take a recent idea (the sheet's example: deformable convolutions [S41]) and try to beat the state of the art. Beating a result up to a year old is acceptable. | you beat it |

[S5] recommends *Beat the stars* only to advanced students and calls *Beat the classics* "one of the more challenging". For a 3-ECTS project with a hard January deadline, **Bring your own method** is the safest: the dataset exists, the baseline number exists, and the comparison is built in. Note that "replicate a paper" is not one of the four names — it is how you would *execute* a *Bring your own method* project.

Feasibility estimate: parameters $P$, training samples $N$, epochs $E$: FLOPs $\approx 6 P N E$ (forward $2P$, backward $4P$ per sample). The M3 Pro GPU delivers on the order of $5\cdot10^{12}$ fp32 FLOP/s peak, realistically $1$-$2\cdot10^{12}$ in PyTorch/MPS. $P=10^7$, $N=5\cdot10^4$, $E=30$: $9\cdot10^{13}$ FLOP $\approx 1$-$2$ min of pure compute; in practice 10-30 min because of data loading and small kernels. $P=10^8$ with $N=10^6$: $1.8\cdot10^{16}$, i.e. hours to days; out of budget unless a pretrained backbone is frozen and only features are cached.

### Dataset sizing

Rule of thumb for training from scratch: $\ge 1000$ samples per class for images, $\ge 100$ per class with a pretrained backbone and fine-tuned head; for regression $\ge 10$-$50$ samples per input dimension of a linear model, more for deep. Estimate instead of guessing: train on nested subsets $n \in \{N/16, N/8, N/4, N/2, N\}$, plot validation error against $\log n$; the curve typically follows $\epsilon(n) \approx c + a n^{-b}$ with $b \in [0.3, 0.7]$ (Hestness et al. 2017 [S91]). If the curve is still steep at $n=N$, more data helps; if flat, the model or labels limit. Class imbalance: report per-class recall, not accuracy (majority class 95% $\Rightarrow$ 95% accuracy for free); use `WeightedRandomSampler`, class-weighted loss, or balanced accuracy / macro-F1 as the metric. Protocol: split **once**, by a hash of the sample id (not by index, so re-runs give the same split); train/val/test $\approx 70/15/15$ or the paper's split if it exists; the test set is evaluated **once**, at the very end, on the final model; all model selection and early stopping use val. Group leakage: samples from the same patient/user/session/document go to the same split. Write a data card (Gebru et al. 2021 [S90]): source, licence, collection date, size per split, label definition, known biases, preprocessing.

### Baselines

In increasing order, all reported in the same table as the final model: (1) trivial: majority class (classification), mean or median (regression), "persist last value" (forecasting); (2) classical ML on hand features: logistic regression or random forest on flattened/pooled inputs (`sklearn`, 5 min); (3) a small pretrained model with a linear head (ResNet-18 features, a small sentence encoder). Deep model must beat (2) and (3) by a margin larger than the seed std, otherwise the project's conclusion is "the classical baseline suffices", which is a valid and gradeable result if stated.

### Error analysis

Confusion matrix $C_{ij}$ = count of true class $i$ predicted $j$; per-class precision $C_{ii}/\sum_k C_{ki}$, recall $C_{ii}/\sum_k C_{ik}$, macro-F1. Sort validation samples by loss, look at the worst 20 by eye, categorise (label noise, ambiguous, out-of-distribution, model failure). Slice the metric by attributes available in the metadata (length, brightness, source, class frequency) to find where it fails. Calibration: bin predictions by confidence, plot accuracy per bin against confidence (reliability diagram), expected calibration error $\text{ECE} = \sum_b \frac{n_b}{N}|\text{acc}_b - \text{conf}_b|$; deep nets are overconfident (Guo et al. 2017 [S92]), temperature scaling on val fixes it in one scalar.

### Comparing to the state of the art

Same metric, same split, same preprocessing, same input resolution; otherwise the comparison is between experiments, not methods. Report three numbers: the paper's published value, your reproduction of the paper's method under your setup, and your method. The gap between the first two is the "setup gap" and must be discussed; if you cannot reproduce within noise, say so and compare only against your reproduction. Effect sizes: $\bar m \pm s$ over $n \ge 3$ seeds for every row; a difference smaller than $2s/\sqrt{n}$ is not a difference. Ablations: remove one component at a time from the final model (augmentation, pretraining, the modification you added) and re-run; the ablation table is what shows which change mattered.

### Error target

This is step 1 of the assignment-2 sheet's own recommended approach — "specify an error metric … and a reasonable target value for that error metric" — and the achieved value against that target is a named deliverable [S13]. Write it down **before** the first training run.

At the start of assignment 2, write down: metric, the trivial baseline value, the SOTA value, and the target you commit to (e.g. "within 2 points of the paper's 91.2% accuracy, macro-F1 $> 0.85$") with the reason (published number on the same split, or the learning-curve extrapolation). Also write the compute target (one run $\le 1$ h). The report then states whether the target was met; a missed target with a good analysis of why is graded better than a target quietly moved.

### Work-breakdown structure and time budget

The assignment-1 sheet prescribes the buckets: **dataset collection; designing and building the network; training and fine-tuning; building an application to present the results; writing the final report; preparing the presentation** — each with an estimate in hours [S12]. Assignment 2 then asks for the *actual* hours per bucket, and assignment 3 asks you to discuss estimate versus actual and explain any underestimate [S13, S14]. **The hours themselves do not affect the grade** [S13]; the estimating discipline is the point.

A plan that fits TISS's 75 h [S1] using exactly those six buckets:

| bucket ([S12] name) | hours | content |
|---|---|---|
| *(lecture / Q&A — not a WBS bucket)* | 16 | preliminary lecture, weekly Q&A sessions, watching the recordings |
| dataset collection | 8 | search, licence check, download, split by hashed id, data card, trivial baselines |
| designing and building the network | 14 | classical baseline 2, pretrained baseline 3, own model 9 |
| training and fine-tuning | 14 | tuning 5, ablations 3, seeds 4, final test eval 1, plus reruns |
| building an application | 9 | export (ONNX or a saved checkpoint), a Gradio/Streamlit or browser front end, a Dockerfile or a release with the weights |
| writing the final report | 7 | five pages |
| preparing the presentation | 3 | four minutes, plus a screencast |
| *(presenting and attending)* | 4 | your own talk plus the other two sessions |
| total | 75 | |

Programming totals 45 h as TISS specifies. Note how much of it the demo application takes: **budget it explicitly**, because it is 10 of the 50 points and cannot be improvised the night before. A timer per session (`Timer` in `common.py` for compute, a log for the human) tells you by mid-assignment-2 whether the plan holds.

### Report structure — at most five pages, one PDF [S14]

The sheet requires four questions answered: *what is the problem you tried to solve; why is it a problem; what is your solution; why is it a solution — and in particular, why is or is not deep learning a solution*. Plus: main take-aways and insights; what you would do differently; time spent versus your initial estimate, with the reasons for any underestimate. A large part may be lifted from the assignment-1 proposal with edits.

Five pages is tight, so allocate: problem and motivation (the first two questions) ~0.75 p; related work and the number you compare against ~0.5 p; data — source, licence, splits ~0.5 p; method, with one shape-annotated diagram ~1 p; experiments and results — one table (trivial, classical, pretrained, own, comparison target; mean $\pm$ std over seeds) ~1 p; error analysis (confusion matrix or worst cases, one slice) ~0.5 p; take-aways, what you would do differently, time-vs-estimate, limitations ~0.75 p. The reproducibility details (commit hash, `config.yaml`, command line, run times, seeds) go in the repository README, not into the five pages.

The sheet's own examples of the kind of insight it wants are concrete and mechanical — "batch normalisation improved the results significantly", "Adadelta worked much better than SGD on my data", "setting up the pre-processing took much more time than I expected" [S14]. Write those, not generalities.

### Presentation — a hard four-minute limit [S5, S14]

Not ten minutes. The structure is prescribed: **first two minutes** topic, selected approach, final results; **remaining two minutes** insights for your colleagues and ideally a small demo.

Four minutes is about **four to six slides**, not eight. Slide 1: problem and the metric with its target. Slide 2: method, one diagram. Slide 3: the results table, one row per baseline. Slide 4: insights — what actually mattered, what you would do differently. Slide 5 (optional): the demo, as an **embedded screencast**, which is what the sheet asks for; a live demo in a 4-minute slot is a bad bet. Submit as a PDF or a link to online slides. Rehearse with a timer at least twice; the limit is enforced because 60–70 students have to get through three sessions [S5].

Everything is due **before the first of the three presentation dates**, because presenters are drawn at random [S5, S14] — you can be called in the first session. Reserve the full two hours of all three slots.

### Timeline

Two kinds of row below, kept strictly apart.

**Official 2026W dates** [S1] — these are from TISS and are fixed:

| date | time | what |
|---|---|---|
| 30.07.2026 10:00 – 07.10.2026 23:59 | | registration window (TISS) |
| Wed 07.10.2026 | 16:00–17:00 | preliminary lecture, Zoom — **the assignment deadlines are announced here** |
| 14.10.2026 23:59 | | deregistration deadline |
| Wed 14.10.2026 – 16.12.2026 | 16:00–17:00 | weekly Q&A, Zoom |
| Thu 07.01.2027 | 16:00–17:00 | Q&A, Zoom |
| Wed 13.01 / 20.01 / 27.01.2027 | 10:00–12:00 | presentations, FAV Hörsaal 1, in person |

**Assignment deadlines.** The 2026W dates are not published yet. What *is*
sourced is the rule — deadlines fall "the day before one of the lectures", and
everything is due before the first presentation slot [S5] — and the 2025W dates
the assignment sheets carry: 21.10.2025, 16.12.2025, 13.01.2026 [S12, S13, S14],
each of which fits that rule against the 2025W calendar [S2]. Applying the rule
to 2026W gives **~27.10.2026, ~15.12.2026 and 12.01.2027**. The third follows
directly from the stated rule and is reliable; the first two are an inference
from one year's spacing. **Overwrite all three with the announced dates on
07.10.2026.**

**A working schedule, self-set.** Nothing in this table is official; it is a plan
that fits the official dates above and the inferred deadlines. Adjust it, do not
cite it.

| by | milestone (self-set) |
|---|---|
| 07.10.2026 | shortlist of 3 problems with data links, so the preliminary lecture is useful |
| 14.10.2026 (deregistration) | go/no-go: data downloaded, licence checked, hardware confirmed |
| ~27.10.2026 (**A1**) | two papers read; project type declared; dataset and split; work-breakdown structure with hours incl. the demo app; repo created and shared |
| 13.11.2026 | trivial + classical + pretrained baselines, learning curve, error target frozen |
| 04.12.2026 | own model trained, ablations running, tests and CI green |
| ~15.12.2026 (**A2**) | metric / target / achieved written up; actual hours logged; repo formatted and documented |
| 17.12.2026 – 06.01.2027 | seeds, comparison runs, error analysis, **demo application built**, report draft |
| Thu 07.01.2027 | Q&A: last chance to ask about the report and the demo |
| 12.01.2027 (**A3**) | demo app, 5-page PDF, ≤4-min slides + screencast, all submitted |
| 13.01.2027 | rehearsed talk ready — you may be drawn in the first session |

### Checklist per assignment

**A1 Initiate** [S12]: problem statement in one paragraph; **project type named**; at least two papers cited; course topic named; dataset downloaded and licence recorded; split by hashed id, group leakage considered; data card; trivial baseline numbers; the number you will compare against, found; feasibility FLOP estimate; error target draft; **work-breakdown structure with hours for all six buckets, including building the application**; repository named `<matr>_<subject>` with read access granted; e-mail sent.

**A2 Hacking** [S13]: error metric and target written down *before* training; `config.yaml` and `train.py` from the template; classical and pretrained baselines in the results table; own model overfits one batch; full run $\le 2$ h; logs (loss, LR, grad norm, val metric) saved per run; `best.pt`/`last.pt`; ablation list; **tests for pre- and post-processing**; CI green; `requirements.txt` pinned; `ruff`/`black` clean; **no weights or data committed**; README states metric / target / achieved and hours per task.

**A3 Deliver** [S14]: $\ge 3$ seeds per row; comparison attempted and documented; confusion matrix, worst-20, slices, calibration; test set evaluated once; **demo application that a stranger can run** (browser or Docker, weights fetched from a release); five-page PDF answering the four questions plus take-aways, what-you-would-do-differently and time-vs-estimate; slides under four minutes with a screencast if demoing; everything submitted before the first presentation slot.

### Common failure modes

Too ambitious (new architecture and new dataset and new task); data not obtainable or licence unclear at week 3; no baseline, so "the model gets 78%" is uninterpretable; test-set tuning (early stopping or model selection on test), which invalidates the comparison; no SOTA comparison or comparison on a different split; single seed; not reproducible (no seed, no config, no commit hash); presentation over time; report without a limitations section.

## Architecture sketch

```
raw data (licence!) --> preprocess/split (hash id) --> train/val/test  [N_tr], [N_va], [N_te]
                                   |
                                   v
                   trivial baseline --> classical baseline --> pretrained baseline
                                   |
                                   v
                   config.yaml --> train.py (common.train_loop) --> runs/<name>/{best,last}.pt, log.csv
                                   |
                                   v
                   evaluate.py: val per run; seeds x3; ablations; test ONCE at the end
                                   |
                                   v
                   error analysis (confusion, worst-20, slices, calibration)
                                   |
                                   v
                   report/outline.md --> report.pdf ; presentation/outline.md --> slides.pdf
```

```
src/project_template/
  README.md               problem, target, how to run, results table
  config.yaml             data paths, model, lr, batch_size, steps, seed
  data/                   raw/ (untracked), processed/, splits.json, data_card.md
  models/                 model definitions (one file per architecture)
  train.py                config -> data -> model -> optimizer -> train_loop -> checkpoints, log.csv
  evaluate.py             load best.pt, metrics on val/test, confusion matrix, worst-k dump
  report/outline.md       section headings of the report with word budgets
  presentation/outline.md slide list with time per slide
```

**Worked example: sizing.** Measured with `Timer`: a ResNet-18 at $128\times128$, batch 64, bf16 on MPS runs 2.8 steps/s (180 samples/s) including data loading. Budget 2 h $= 7200$ s $\Rightarrow 20\,160$ steps $\Rightarrow 1.29\cdot10^6$ samples. With $N_{tr} = 20\,000$ that is 64 epochs, more than enough; with $N_{tr}=200\,000$ it is 6.5 epochs, borderline, so either freeze the backbone (forward only, $\approx 3\times$ faster, then cache features so the head trains in seconds) or reduce to $96\times96$ ($1.8\times$ fewer pixels).

**Learning-curve extrapolation.** Validation error on subsets: $n = 500, 1000, 2000, 4000 \Rightarrow \epsilon = 0.400, 0.330, 0.280, 0.245$. Differences per doubling: $0.070, 0.050, 0.035$, ratio $r \approx 0.71$, i.e. $\epsilon(n) \approx c + a n^{-b}$ with $b = -\log_2 r \approx 0.49$. Remaining improvement beyond $n=4000$ is the geometric tail $0.035\, r/(1-r) \approx 0.086$, so the asymptote is $c \approx 0.245 - 0.086 = 0.16$. Two more doublings ($n = 16\,000$) give $0.245 - 0.035(0.71 + 0.71^2) \approx 0.203$. If the SOTA error is $0.12 < c$, more data with this model will not reach it; the plan must change the model (pretraining, architecture), not the dataset. This calculation is the assignment-1 justification of the error target.

## Pitfalls

- Val metric rises for weeks, test result at the end is 10 points worse $\to$ model selection and early stopping were done on test, or val and test overlap $\to$ hashed split, test evaluated once, never look at it earlier.
- Own number beats the paper by 3 points $\to$ different split, resolution, or metric variant (top-1 vs top-5, micro vs macro F1) $\to$ reproduce the paper's method in your setup and compare against that.
- First training run is in week 8 $\to$ data pipeline consumed assignment 2 $\to$ trivial and classical baselines by the end of assignment 1 force the pipeline to exist early.
- Deep model at 82%, random forest at 81% $\to$ task is easy or features are strong $\to$ report it honestly; the grade is for method and analysis, not for the model winning.
- Runs take 6 h each, only 4 fit before the deadline $\to$ no sizing done $\to$ measure throughput on step 1, budget steps as in the worked example, cache frozen features.
- Results table has one seed $\to$ differences are within noise and the reviewer knows $\to$ 3 seeds, mean $\pm$ std; if compute forbids, 3 seeds for the two rows that carry the claim.
- Dataset licence says "non-commercial, no redistribution" and the report must include sample figures $\to$ check the licence in assignment 1; show samples only if allowed, otherwise describe.
- Presentation runs 7 min against a **hard 4-minute limit** [S14] $\to$ no rehearsal, too many slides $\to$ 4-6 slides, two on problem/approach/result and two on insights, timer, method details into backup slides.
- Assignment 3 arrives and there is nothing to demo $\to$ the project's output is a number in a log $\to$ the demo application is 10 of the 50 points [S14]; pick a problem with a visible output in assignment 1 and budget the app in the work-breakdown structure.
- Report cannot be reproduced by the reader $\to$ missing commit hash, config, seeds, run time $\to$ reproducibility appendix written from the run directory, not from memory.

## Questions

1. You have a 12-class image dataset with 3 000 images total, heavily imbalanced (largest class 40%, smallest 1%). Which metric, split, and baseline do you fix in assignment 1, and why?
<details><summary>Answer</summary>
Metric: macro-F1 or balanced accuracy, because accuracy is 40% for the majority-class baseline and hides the small classes. Split: stratified by class, hashed by image id, 70/15/15, so the 1% class has about 4-5 test images; note in the data card that per-class numbers on that class have huge variance. Baselines: majority class (macro-F1 $\approx 1/12 \cdot$ recall of one class, near 0.05), logistic regression on pooled pretrained features, and a fine-tuned pretrained backbone with class-weighted cross-entropy. 250 images per class on average is below the from-scratch rule of thumb, so pretraining is mandatory.
</details>

2. Derive the number of training steps that fit in 90 min at a measured 3.2 steps/s and the number of epochs on 48 000 samples with batch 32; what do you change if the paper trained 200 epochs?
<details><summary>Answer</summary>
$90\cdot60\cdot3.2 = 17\,280$ steps, $17\,280\cdot32 = 553\,000$ samples, $553\,000/48\,000 = 11.5$ epochs. 200 epochs would take 26 h. Options in order: freeze the backbone and cache features (head trains in minutes); reduce resolution; use a pretrained model so 10 epochs suffice; state in the report that the reproduction uses 12 epochs and quantify the gap by a short learning-curve in epochs (metric at 3, 6, 12 epochs) to show whether the curve has flattened.
</details>

3. Your reproduction of the SOTA method gives $88.1 \pm 0.6$ while the paper reports 90.4; your own method gives $89.0 \pm 0.7$. What do you claim?
<details><summary>Answer</summary>
A setup gap of 2.3 points exists; likely causes: fewer epochs, different augmentation, resolution, or an unreported trick. The claim is "under identical setup, own method improves over the reproduced baseline by $0.9$ points; with $n=3$ seeds and $s\approx0.65$ the standard error of the difference is $\approx 0.65\sqrt{2/3} = 0.53$, so the improvement is about 1.7 standard errors: suggestive, not conclusive". Do not claim to approach 90.4. Report all three numbers and discuss the gap in limitations.
</details>

4. Explain why fitting normalisation statistics or a tokenizer on the full dataset before splitting is leakage, and quantify when it matters.
<details><summary>Answer</summary>
The statistics carry information about test samples into the training pipeline; for per-channel mean/std on $10^4$ images the effect is negligible (the estimate changes in the 4th digit), for a tokenizer or TF-IDF vocabulary it is not: rare test words get dedicated tokens that a real deployment would not have, inflating test scores. Feature selection on all data is the extreme case (Hastie et al. ESL 7.10.2, near-perfect test accuracy on noise). Rule: everything that is "fit" is fit on train only, wrapped in a pipeline that is applied to val/test.
</details>

5. The learning curve on subsets $n = 1000, 2000, 4000$ gives errors $0.30, 0.26, 0.235$. Estimate the asymptote and decide whether collecting $4\times$ more data can reach a SOTA error of 0.18.
<details><summary>Answer</summary>
Differences $0.040, 0.025$, ratio $r = 0.625$. Tail beyond $n=4000$: $0.025\cdot r/(1-r) = 0.042$, asymptote $c \approx 0.193$. Two doublings ($n=16\,000$): $0.235 - 0.025(0.625 + 0.39) = 0.210$. Neither reaches 0.18, so more data alone will not; the target requires a better model (pretraining, architecture) and the report should say so with this calculation. Caveat: three points give a rough $r$; add $n=500$ to stabilise it.
</details>

6. Which components of a run directory are needed for someone to reproduce your results table row by row, and which of these does `common.py` provide?
<details><summary>Answer</summary>
Per row: commit hash, resolved `config.yaml` (with seed), command line, PyTorch version and device, `log.csv` (per-step loss, LR, grad norm, val metric), `best.pt` with model/optimizer/scheduler/step/RNG state, the split file `splits.json`, and the evaluation output on val (and once on test). `common.py` gives `seed_all(seed)`, `get_device()`, `train_loop` (per-step losses), `Timer` (run time), `count_params` (for the hyperparameter table); logging, config dumping, and checkpoint writing are added in the template's `train.py`.
</details>

7. In assignment 3 you find that 30% of the worst-20 validation errors are mislabelled. What do you do with the metric, the test set, and the report?
<details><summary>Answer</summary>
Do not relabel the test set after looking at it (that is test tuning); relabelling val is allowed if documented. Estimate the label noise rate on a random (not worst-case) sample of 100 val items, report it, and state that the achievable error is bounded below by roughly that rate. Add "label noise" as a category in the error analysis and to limitations; compare with the SOTA paper, whose number includes the same noise if the split is the same. Optionally train with a noise-robust loss as an ablation.
</details>

8. Draft the results table columns and rows for a replication project on a text classification task with a transformer, and state which cell is evaluated on the test set.
<details><summary>Answer</summary>
Columns: method, params, train time (min, M3 Pro), val macro-F1 (mean $\pm$ std, 3 seeds), test macro-F1. Rows: majority class; TF-IDF + logistic regression; frozen pretrained encoder + linear head; fine-tuned encoder (reproduction of the paper); fine-tuned encoder + own change; published SOTA (val column empty, test column the paper's number, params and time from the paper). Test column filled exactly once, at the end, for every row using the seed-0 `best.pt` selected on val; the ablation table has a val column only.
</details>

## Code

`src/project_template/`: `README.md`, `config.yaml`, `data/`, `models/`, `train.py` (config $\to$ data $\to$ model $\to$ optimizer $\to$ loop with logging, checkpoints, evaluation; self-contained), `evaluate.py` (test split once, majority baseline, confusion matrix, worst errors to `errors.json`), `report/outline.md`, `presentation/outline.md`. Copy the folder, fill `config.yaml`, replace `load_dataset` in `train.py` and register the model in `models/__init__.py`; checkpoints land in `models/checkpoints/<experiment>/{best,last}.pt`.

`src/py/common.py`: `get_device()` (mps > cpu), `seed_all(seed)`, `train_loop(step_fn, optimizer, steps, log_every=0, scheduler=None, clip_grad=None)` returning the per-step losses, `Timer` context manager for throughput measurements, `loss_decreased(losses, frac=0.1)`, `count_params(model, trainable_only=False)` for the hyperparameter table. The eight topic modules `src/py/<module>.py` each expose `run(steps=..., device=None, seed=0) -> dict` with `"losses"` and a metric key; `python src/py/<module>.py` trains a few seconds and prints the metric; `test_<module>.py` asserts `common.loss_decreased(losses)`. Any of them is a starting point for the project's model file. Run from this course folder with `uv run python` (repo venv).

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016): ch. 11 (practical methodology: performance metrics, baselines, more data vs. better model, hyperparameters, debugging), ch. 5.2-5.3 (capacity, validation, cross-validation), ch. 12 (applications).
- Hestness, J. et al. (2017). Deep Learning Scaling is Predictable, Empirically. arXiv:1712.00409 (power-law learning curves).
- Guo, C. et al. (2017). On Calibration of Modern Neural Networks. ICML.
- Gebru, T. et al. (2021). Datasheets for Datasets. CACM 64(12).
- Mitchell, M. et al. (2019). Model Cards for Model Reporting. FAT*.
- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning* (2009), ch. 7.10 (cross-validation done wrong).
- Bouthillier, X. et al. (2021). Accounting for Variance in Machine Learning Benchmarks. MLSys (seed variance, effect sizes).
- Pineau, J. et al. (2021). Improving Reproducibility in Machine Learning Research (the ML reproducibility checklist). JMLR 22.
- Karpathy, A. (2019). *A Recipe for Training Neural Networks*.
- **Course-authoritative:** [S1] TISS 194.077 2026W; [S5] Pacha, *Applied Deep Learning 2025 — Lecture 0 — Preliminary Information*; [S12] *Assignment 1 — Initiate*; [S13] *Assignment 2 — Hacking*; [S14] *Assignment 3 — Deliver*; [S11] VoWi course page. ILEA/TUWEL for the announced 2026W deadlines. See [`../refs/SOURCES.md`](../refs/SOURCES.md).
