# Sources: 183.663 / 193.200 Deep Learning for Visual Computing

Register of every source used for [`../notes`](../notes/README.md) and
[`../src`](../src/README.md). Retrieval date 2026-09-28 unless stated. TISS,
VoWi and the CVL homepage change; re-check before registering.

**Citation form.** `[S<n>]`, optionally with a locator (`[S11 ch. 9]`,
`[S7 p. 27]`), several together as `[S7, S9]`. Grouped entries (S18 to S35)
bundle papers on one topic; the notes name the paper when it matters.

**Vendoring policy.** Nothing third-party is committed. Every PDF below is
either unlicensed (student uploads, the 2016 slides) or under the arXiv
non-exclusive distribution licence, which does not allow redistribution.
[`fetch-sources.sh`](fetch-sources.sh) downloads the free ones into the
git-ignored `cite-only/` for personal reading. See [`README.md`](README.md).

**The one-line summary of this pass.** The course has almost certainly been
**renumbered**: 183.663 (3 ECTS) is not public in 2026S, and in its place TISS
lists **193.200 Deep Learning for Visual Computing, VU 4.0 h, 6.0 ECTS**, same
lecturers, same subject list, same assessment; the CVL homepage gives 193.200
as the course number [S3, S4]. **066 646 CSE is not among 193.200's curricula
in 2026S** [S3]. The exam has historically been drawn from a published question
catalogue; three versions of it (2017, 2020, 2022S) are public [S7, S8, S9].

---

## Course-authoritative

### S1: TISS 183.663, 2025S (last offering under this number) ★

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=183663&semester=2025S>
- Transcribed 2026-09-28 (logged-in browser) into [`../docs/tiss.md`](../docs/tiss.md); API record `../docs/tiss-api.md`
- Used for: VU 2.0 h, 3.0 ECTS; Tue 11:00-13:00 FAV HS 1 Helmut Veith, 04.03.-24.06.2025; exam rehearsals 09.06. and 10.06.2025; registration 14.02.-12.03.2025 with an enrolment precondition listing 066 646; CSE obligation "Not specified"; written exam 50 % + compulsory programming exercises 50 % in groups of two; ECTS breakdown 16 h lecture / 34 h exercises / 24 h exam preparation / 1 h exam; literature Goodfellow et al. and Drori; preceding courses 183.605 and 184.702; subject list (nine items) used as the note order.

### S2: TISS 183.663, 2026S (not public)

- URL: `...courseNr=183663&semester=2026S`
- Per [`../docs/tiss.md`](../docs/tiss.md): "The Course is not public in semester 2026S"; semester list 2025S back to 2016W. On 2026-09-28 an unauthenticated browser was redirected to the TU login for this URL (and for 193.200 2027S), so a non-public semester is indistinguishable from "needs login" without logging in.

### S3: TISS 193.200 Deep Learning for Visual Computing, 2026S ★ (new in this pass)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=193200&semester=2026S&locale=en>
- Read 2026-09-28, unauthenticated browser (public). The semester selector lists **only 2026S**: a new course number.
- Fields: VU, **4.0 h, 6.0 ECTS**, presence, LectureTube, TUWEL. Learning outcomes add "image **and 3D data** analysis". Subject list identical to S1. Teaching: "Video lectures, in-person discussion and examples, and individual programming tasks in groups of two". Written; examination modalities "Written exam (50%) and compulsory programming exercises (50%)". ECTS 150 h = 28 h lecture + 54 h "preparation units, individual preparation and tests" + 68 h "solving exercises and hand-in meetings". Lecturers Hermosilla Casajus, Weijler, Kampel (E193).
- Dates: lecture Tue 10:00-12:00, 03.03.-23.06.2026, FAV HS 1 Helmut Veith. Registration 16.02.2026 00:01 - 14.03.2026 23:59 (deregistration same end).
- Exams listed: Fri 23.10.2026 14:00-16:00 EI 9 (registration 02.10.-21.10.2026 09:00, "1. alternative exam date"); Thu 17.12.2026 15:00-17:00 EI 8 (25.11.-15.12.2026, "2. alternative"); Tue 26.01.2027 15:00-17:00 EI 9 (05.01.-24.01.2027, "3. alternative"); Tue 29.06.2027 16:00-18:00 EI 7 (04.06.-04.07.2027, "Exam 1").
- Curricula: 066 522 (Not specified), 066 645 Data Science, 066 926 Business Informatics, 066 932 Visual Computing (mandatory elective). **066 646 CSE absent.**
- Literature: "No lecture notes are available." Preceding courses 183.605, 184.702.

### S4: CVL course homepage

- URL: <https://cvl.tuwien.ac.at/course/dlvc/> (TISS API gives the older `http://www.cvl.tuwien.ac.at/cvl/course/dlvc/`, which serves the same page)
- Used for: **"LVA Number: 193.200"**, VU, summer semester, lecturers Hermosilla-Casajus, Kampel, Weijler; prerequisites (mathematics, statistics, image processing, machine learning; Python 3); GPU options (own CUDA GPU, lab GPU server, AWS SageMaker or Google AI Platform free tiers); grading 50 % exercises in pairs + 50 % written exam; "The lecture will be held on site and there will be no recordings." **No slides, no exercise descriptions, no dates.** Undated page.

## Exam evidence (student-hosted or lecturer-hosted, unlicensed)

### S5: VoWi LVA page, Deep Learning for Visual Computing VU (Kampel)

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Deep_Learning_for_Visual_Computing_VU_(Kampel)>; the sibling page "(Hermosilla Casajus)" has **0 materials**
- Used for: three exercises in pairs, all parts must be submitted; SS21 exam online, written + oral, questions from a catalogue published on TUWEL beforehand; SS22 exam written in presence, no aids, catalogue on TUWEL; January 2023 sitting: five main questions from the catalogue, 1 h. Last listed offering on the page: 2023S.

### S6: VoWi, Exam Questions SS21

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Deep_Learning_for_Visual_Computing_VU_(Kampel)/Exam_Questions_SS21>
- Used for: the written questions (local vs global optimum and momentum; CNN overview and the two stages; the backprop graph with Matrikelnummer digits) and the oral topics (U-Net and its skips, imbalanced data, cross-entropy, conv vs linear layers, transfer learning, dropout placement).

### S7: VoWi, "DLVC 2022S - Questions.pdf" ★

- File page: <https://vowi.fsinf.at/wiki/Datei:TU_Wien-Deep_Learning_for_Visual_Computing_VU_(Kampel)_-_DLVC_2022S_-_Questions.pdf>, 2.58 MB, 38 pp., uploaded 27.10.2022
- The 2022S catalogue with a student's answers; read in a browser with pdf.js (VoWi runs a bot gate). Used for: the question list in [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md), including the additions over 2020: YOLO output tensor, FPN, U-Net merge by concatenation, image-to-image GANs, CycleGAN, transformers, data bias and protected attributes, fairness. **The student answers contain errors** (e.g. p. 14 gives 16x10x10 for a 3x3 conv on 3x32x32, correct is 16x30x30); treat the questions as reliable and the answers as not.

### S8: VoWi, "DL4VC Answers Questions 2020-06-23.pdf"

- File page: <https://vowi.fsinf.at/wiki/Datei:TU_Wien-Deep_Learning_for_Visual_Computing_VU_(Kampel)_-_DL4VC_Answers_Questions_2020-06-23.pdf>, 38 pp.
- The catalogue as of June 2020 with student answers. Used for: the 2020-era questions (kNN, hyperparameter search, parameter count of a 3x3 conv on WxHxD, receptive field, transposed convolution output, YOLO with two anchors and five classes, imbalanced data, learning-rate decay, medical imaging block, XAI).

### S9: GitHub cpra/dlvc2016 (Pramerdorfer, archived)

- URL: <https://github.com/cpra/dlvc2016>; no licence file; last push 2017-05-22; archived
- Contains `exam-questions.pdf` ("183.663 Deep Learning for Visual Computing, Exam Questions and Information", 21.01.2017), `lectures/lecture1..11.pdf` (2016W slides: introduction, image classification, ML basics, features and parametric models, gradient descent 1-2, MLPs and CNNs, CNNs and backprop, training and detection, medical imaging, time series), `assignments/general.md`.
- Used for: the exam rules of the original course ("Every exam consists of a different subset of these questions", 60 minutes, no documents, answers in own words), the pooling input and receptive-field question reproduced in `src/`, the digit-augmentation question, and the lecture order of the 2016W edition.

### S10: GitHub Marentor/dlvc_ss23

- URL: <https://github.com/Marentor/dlvc_ss23>; no licence seen
- Used for: the 2023S exercise shape (a `dlvc` package plus `linear_cats_and_dogs.py`, `cnn_cats_and_dogs.py`, `cnn_cats_and_dogs_pt3.py`: linear classifier, then CNN, then a third part on the same data). Nothing newer than 2023S was found for the Hermosilla era.

## Books

### S11: Goodfellow, Bengio, Courville, *Deep Learning*, MIT Press 2016 ★

- <https://www.deeplearningbook.org/>, free HTML, no PDF by contract. Named in S1. Chapters used: 5 (ML basics), 6 (feedforward, 6.5 backprop), 7 (regularisation), 8 (optimisation), 9 (convolutional networks), 14 (autoencoders), 20 (generative models).

### S12: I. Drori, *The Science of Deep Learning*, Cambridge UP 2022, ISBN 9781108835084

- Companion site <https://www.thescienceofdeeplearning.org/> (selected chapters and exercises). Named in S1. Chapters 2 (forward and backpropagation), 3 (optimisation), 4 (regularisation), 5 (CNNs), 9 (GANs), 10 (VAEs).

### S42: R. Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed. 2022

- <https://szeliski.org/Book/>, free PDF for personal use via a form, not to be reposted. Used for the recap in note 01 (ch. 2 image formation, ch. 3 image processing, ch. 7 features and edges). Not named by TISS.

## Papers (all verified against the arXiv API on 2026-09-28 unless marked)

| id | papers | used in |
|---|---|---|
| S13 | Dumoulin & Visin, *A guide to convolution arithmetic*, arXiv 1603.07285 | 04, `conv_arithmetic.py` |
| S14 | LeCun, Bottou, Bengio, Haffner, *Gradient-based learning applied to document recognition*, Proc. IEEE 1998 (PDF at yann.lecun.com) | 04 |
| S15 | Krizhevsky, Sutskever, Hinton, *ImageNet classification with deep CNNs*, NeurIPS 2012 (papers.nips.cc) | 04 |
| S16 | Simonyan & Zisserman, VGG, arXiv 1409.1556; Szegedy et al., GoogLeNet, 1409.4842; Howard et al., MobileNets, 1704.04861 | 04 |
| S17 | He, Zhang, Ren, Sun, ResNet, arXiv 1512.03385 | 04 |
| S18 | Ioffe & Szegedy, batch norm, 1502.03167; Ba et al., layer norm, 1607.06450; Wu & He, group norm, 1803.08494 | 04, 08 |
| S19 | Glorot & Bengio, AISTATS 2010 (PMLR v9); He et al., *Delving deep into rectifiers*, 1502.01852 | 03, 08 |
| S20 | Kingma & Ba, Adam, 1412.6980; Loshchilov & Hutter, SGDR, 1608.03983; Smith, cyclical LR, 1506.01186 | 02, 08 |
| S21 | Srivastava et al., dropout, JMLR 15 (2014) | 08 |
| S22 | Girshick et al., R-CNN, 1311.2524; Girshick, Fast R-CNN, 1504.08083; Ren et al., Faster R-CNN, 1506.01497 | 05, `detection_utils.py` |
| S23 | Redmon et al., YOLO, 1506.02640; Redmon & Farhadi, YOLOv3, 1804.02767 | 05 |
| S24 | Lin et al., FPN, 1612.03144; Lin et al., focal loss / RetinaNet, 1708.02002 | 05 |
| S25 | Everingham et al., *The PASCAL VOC challenge*, IJCV 88 (2010) (not re-fetched); Lin et al., COCO, 1405.0312 | 05 |
| S26 | Long et al., FCN, 1411.4038; Ronneberger et al., U-Net, 1505.04597; Milletari et al., V-Net (Dice loss), 1606.04797; He et al., Mask R-CNN, 1703.06870 | 05 |
| S27 | Kingma & Welling, VAE, 1312.6114 | 06 |
| S28 | Goodfellow et al., GAN, 1406.2661; Mirza & Osindero, conditional GAN, 1411.1784; Isola et al., pix2pix, 1611.07004; Zhu et al., CycleGAN, 1703.10593 | 06 |
| S29 | Ho, Jain, Abbeel, DDPM, 2006.11239 | 06 |
| S30 | Qi et al., PointNet, 1612.00593; PointNet++, 1706.02413 | 07 |
| S31 | Hermosilla et al., *Monte Carlo convolution for learning on non-uniformly sampled point clouds*, 1806.01759; Hermosilla's homepage <https://phermosilla.github.io/> ("3D and unstructured data ... point clouds, graphs, implicit representations"; no teaching material) | 07 |
| S32 | Hanocka et al., MeshCNN, 1809.05910 | 07 |
| S33 | Mildenhall et al., NeRF, 2003.08934 | 07 |
| S34 | Simonyan et al., saliency maps, 1312.6034; Zhou et al., CAM, 1512.04150; Selvaraju et al., Grad-CAM, 1610.02391; Adebayo et al., sanity checks, 1810.03292 | 08, `gradcam.py` |
| S35 | Zhang et al., mixup, 1710.09412; DeVries & Taylor, cutout, 1708.04552; Micikevicius et al., mixed precision, 1710.03740; R. Zhang, *Making CNNs shift-invariant again*, 1904.11486 | 08, `augment.py` |
| S36 | Mitchell et al., model cards, 1810.03993 | 09 |
| S37 | Hardt, Price, Srebro, equality of opportunity, 1610.02413; Suresh & Guttag, sources of harm, 1901.10002; Chouldechova, 1703.00056; Kleinberg, Mullainathan, Raghavan, 1609.05807 | 09 |
| S38 | Buolamwini & Gebru, *Gender Shades*, PMLR 81 (2018), abstract read at proceedings.mlr.press: error up to 34.7 % vs at most 0.8 %; IJB-A 79.6 %, Adience 86.2 % lighter-skinned | 09 |
| S41 | Dosovitskiy et al., ViT, 2010.11929 | 04 |
| S43 | Geirhos et al., texture bias of ImageNet CNNs, 1811.12231 | 04 |

## Regulation

### S39: EU AI Act, Regulation (EU) 2024/1689

- Text: <https://eur-lex.europa.eu/eli/reg/2024/1689/oj>; article pages and timeline at <https://artificialintelligenceact.eu/> (retrieved 2026-09-28: Art. 5, Art. 99, implementation timeline)
- Used for: risk tiers, the Art. 5 prohibitions relevant to vision (untargeted scraping of facial images, emotion recognition at work and in education, biometric categorisation of sensitive traits, real-time remote biometric identification by law enforcement with three exceptions), fines (Art. 99: up to EUR 35 M or 7 % for prohibited practices, 15 M or 3 %, 7.5 M or 1 %), dates (in force 01.08.2024, prohibitions 02.02.2025, GPAI 02.08.2025).

### S40: Digital Omnibus on AI (amending S39)

- Reported as **Regulation (EU) 2026/1744**, in force 27.07.2026, by secondary sources: <https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/> and a Gibson Dunn client note found by search; consistent with the timeline page of S39. **EUR-Lex was not reachable for the ELI; the regulation number is unverified at the primary source.**
- Used for: Annex III high-risk obligations moved from 02.08.2026 to **02.12.2027**, Annex I (products) to **02.08.2028**; new Art. 5(1)(ba)/(bb) prohibitions (non-consensual intimate imagery, CSAM) from 02.12.2026; Art. 50 transparency from 02.08.2026 with a 02.12.2026 transition for watermarking of systems already on the market.

### S44: High-Level Expert Group on AI, *Ethics Guidelines for Trustworthy AI*, 08.04.2019

- <https://digital-strategy.ec.europa.eu/en/library/ethics-guidelines-trustworthy-ai>
- Used for: lawful / ethical / robust and the seven requirements (note 09).

### S45: Charter of Fundamental Rights of the EU, Art. 21 (non-discrimination)

- <https://fra.europa.eu/en/eu-charter/article/21-non-discrimination>
- Used for: the list of protected grounds (note 09).

## Internal cross-references (not numbered)

- [`../../../ws2026/applied-deep-learning/notes/`](../../applied-deep-learning/notes/README.md): 194.077 notes. Notes 01, 02, 05, 06, 08, 10 are linked instead of duplicated.
- [`../../../ws2026/machine-learning/notes/`](../../machine-learning/notes/README.md): 184.702 (preceding course, 2026W), notes 03, 04, 11, 13.

## Deliberately not used

- **TUWEL**: the course material there is not ours to copy. Never fetched.
- The VoWi `Anki DLVC.zip` deck: flash cards derived from the catalogue, nothing S7/S8 lack.
- Student repos for other universities' "DLVC" courses (NPTEL `gymk/DLVC`): different course.
