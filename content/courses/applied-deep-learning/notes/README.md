# Notes: 194.077 Applied Deep Learning (2026W)

**Start with [`00-exam-focus.md`](00-exam-focus.md).** There is no written exam in this course [S1]: the grade is five deliverables worth 10 points each, on five criteria, and that page documents them from the lecturer's own preliminary lecture [S5] and the three official assignment sheets [S12–S14].

Every claim in these notes carries an `[S<n>]` citation into [`../refs/SOURCES.md`](../refs/SOURCES.md). What changed in the source-verification pass of 2026-09-22 is in `CHANGELOG.md`.

## The notes, in lecture order

The `NN-` prefixes are stable file ids, not the reading order; the **lecture** column is the real order, taken from the public 2025W recordings [S4] and mapped chapter by chapter in [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md). Each note: concepts with formulas, an architecture sketch with tensor shapes, pitfalls, questions with answers, and a pointer to the runnable example in [`../src/py/`](../src/README.md). Named literature: Goodfellow, Bengio & Courville, *Deep Learning* (2016) [S15], cited by chapter.

| lecture | note | one line | code |
|---|---|---|---|
| — | [00 Exam focus](00-exam-focus.md) | **What is assessed**: five deliverables, 50 points, five criteria, four project types, the real deadlines — and no written exam | |
| 1 | *(none)* | Introduction and applications; nothing examinable, nothing to note | |
| 2 | [01 Training fundamentals](01-training-fundamentals.md) | Losses, backprop as reverse-mode AD, SGD/Adam/AdamW, LR schedules, init | `common.py` |
| 3 | [02 CNNs](02-cnns.md) | Convolution arithmetic, receptive field, pooling, ResNet, deformable convs, transfer learning, the detection/segmentation tour | `cnn_shapes.py`, `shape_formulas.py` |
| 4 | [03 RNNs, LSTM and GRU](03-rnns.md) | BPTT, vanishing gradients, gates, sequence task types, teacher forcing, **CTC** | `rnn_sequence.py`, `ctc_loss.py` |
| 5 | [10 Practical](10-practical.md) | PyTorch idioms, capacity vs effective capacity, the Bayes error, hyperparameter search, tracking, reproducibility, debugging order | `common.py`, `../src/project_template/train.py` |
| 6 | [04 Deep RL](04-deep-rl.md) | MDP, policy gradient / REINFORCE, DQN, exploration, reward shaping | `rl_reinforce.py` |
| 7 | [05 Autoencoders and generative models](05-autoencoders-generative.md) | AE, VAE and the ELBO, β-VAE, GAN, Wasserstein, diffusion | `autoencoder_vae.py`, `gan_toy.py` |
| 8 | [06 Transformers](06-transformers.md) | Attention, positions, encoder/decoder, **DETR and the bipartite matching loss**, ViT | `transformer_char.py`, `set_prediction.py` |
| 9 | [01 Training fundamentals](01-training-fundamentals.md) *(second half)* | Preprocessing, augmentation for image/audio/text, adversarial examples, cutout, dropout, batch/layer norm, SWA, visualisation | `cnn_shapes.py` |
| 10 | [08 Explainable AI](08-explainable-ai.md) | Taxonomy, saliency, integrated gradients, Grad-CAM, LIME, RISE, SHAP, limits | `xai_saliency.py` |
| 11 | [07 GNNs](07-gnns.md) | Building the graph, message passing, GCN, GAT, node / link / graph tasks | `gnn_gcn.py` |
| 12 | [12 Serving and deployment](12-serving-and-deployment.md) | The serving ladder, ONNX, number formats, int8 quantisation, pruning, the lottery ticket, FAIR | `deploy_optimize.py` |
| 13 | [09 LLMs](09-llms.md) | Tokenisation, pretraining, LoRA, prompting, RAG, CLIP, MCP, adversarial prompting, model collapse | `llm_finetune_sketch.py` |
| — | [11 The project](11-project.md) | Choosing a problem, dataset sizing, baselines, error analysis, honest comparison, the report and the four-minute talk | `../src/project_template/` |

## Reading order for the project

The lecture order is not the order you need things in. The project starts in week 1 and the topic lectures arrive over the semester, so:

1. **[00 Exam focus](00-exam-focus.md)** — before you register.
2. **[11 The project](11-project.md)** and **[10 Practical](10-practical.md)** — needed for assignment 1, which is due about three weeks in.
3. The **one topic note** your project uses. TISS requires the project to use at least one of the eight advanced topics [S1].
4. **[12 Serving and deployment](12-serving-and-deployment.md)** — read this in November, not in January. Its lecture is one of the last of the semester, and assignment 3 is graded on the demo application it describes [S14].
5. The remaining topic notes, with the lectures.

**The scheduling trap** [S4, S5]: Explainable AI (lecture 10), Graph Neural Networks (lecture 11) and Serving (lecture 12) are all delivered *after* assignment 2 is due. If your project needs any of them, watch the previous year's recording early — every edition back to 2020 is still online [S6, S7].
