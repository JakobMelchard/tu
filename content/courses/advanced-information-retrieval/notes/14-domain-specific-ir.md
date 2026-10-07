# 14 Special topics II: domain-specific retrieval

Web search is one setting. Medical, legal, patent and scientific search differ
in language, document length, the cost of a miss, and how little labelled data
exists [S14]. The 2025S exercise was in exactly such a domain (scientific
articles, biomedical QA) [S21].

## Definitions

1. **Domain-specific IR**: retrieval where the collection, the users and the notion of relevance come from a professional domain (medical, legal, patent, academic) [S14 sl. 3-7].
2. **Systematic review** (medicine): a secondary study that must find **all** publications meeting pre-specified criteria; the search step is a high-recall task done mostly by human screening [S14 sl. 11-13].
3. **Clinical decision support**: case-specific advice linking a patient record to the literature [S14 sl. 14].
4. **Prior case retrieval** (case law): find earlier decisions relevant to a current case; the output is a ranked list by relevance or time; more precision-oriented than systematic reviews [S14 sl. 22-26].
5. **eDiscovery**: produce all documents relevant to a litigation under procedural rules: high recall demanded [S14 sl. 24].
6. **Domain language models**: SciBERT (Semantic Scholar papers), BioBERT (biomedical abstracts), PubMedBERT (PubMed), LegalBERT (legal documents) [S14 sl. 17, 26].
7. **Zero-shot transfer**: applying a model trained on one collection (typically MS MARCO) to another without in-domain training; benchmarked by BEIR across 18 datasets [S58].
8. **Campaigns and datasets**: TREC-COVID (a changing COVID-19 literature corpus and queries) [S14 sl. 16]; TripClick (medical click-log relevance) [S14 sl. 18]; BioASQ (biomedical semantic indexing and QA: phase A documents and snippets, phase B exact and ideal answers) [S57]; LongEval (Sci-Retrieval on scientific articles in 2025; topic extraction, user simulation and RAG added for 2026) [S56].

## Results

**The challenges** [S14 sl. 17-18, 26]:
- Vocabulary: technical terms, abbreviations, gene and drug names; general-domain embeddings and tokenisers split or misrepresent them (note 05). Domain pre-training helps.
- Few labels: annotation needs experts; click logs (TripClick) and campaigns fill the gap, at the cost of label bias.
- Recall vs precision: in systematic reviews and eDiscovery a missed relevant document can be "catastrophic"; case-law retrieval is precision-oriented.
- Long documents: court decisions and patents far exceed 512 tokens; relevance sits in paragraphs, so split into passages or summarise [S14 sl. 26-27].
- Transfer: MS MARCO-trained dense retrievers often underperform BM25 zero-shot; re-rankers and late interaction transfer better, at higher cost [S58].

**The pipeline is the same, the components are adapted** [S14 sl. 19, 27]: first stage (Boolean queries written by experts, BM25, or dense retrieval), then neural re-ranking with a domain language model and domain relevance labels, with long documents handled at paragraph level (e.g. BERT-PLI aggregates paragraph-level interactions for case law [S14 sl. 28-30]).

## Worked example: what a recall target costs

A systematic review with $N=5000$ candidate abstracts from a Boolean search, $R=50$ relevant, screened in ranked order. Suppose a ranker reaches recall 0.95 at depth 1000 and recall 1.0 only at depth 3500 (illustrative numbers).
- Screening to depth 1000: 80 % less reading than screening all 5000, and $0.05\cdot50=2.5$ relevant studies missed on average.
- Guaranteeing all 50: 3500 abstracts, 30 % saved.
- Precision at depth 1000: $47.5/1000=4.75\,\%$. For this task, precision@10 is irrelevant and recall@$k$ at large $k$ (plus a stopping rule) is the metric that matters; the same system could look poor on nDCG@10 and be excellent here.

## Pitfalls

- Reporting nDCG@10 for a recall-oriented task (or recall@1000 for a precision task) measures the wrong thing; pick the metric from the cost model of the people searching.
- Domain-pretrained models still need domain relevance data for fine-tuning; pre-training teaches language, not relevance [S14 sl. 19].
- Click-derived labels (TripClick) encode position and presentation bias; non-clicked results are not non-relevant (note 08, [S12 sl. 14]).
- Temporal drift: collections and queries change (TREC-COVID rounds); a model tuned on last year's snapshot may degrade.
- Expert Boolean queries are a first stage with a precise, auditable meaning; replacing them with dense retrieval changes what can be reported in a systematic review.

## Questions

**Q:** Why is the systematic-review search step a high-recall problem, and how does that change evaluation?
**A:** The review must include all qualifying studies; a miss biases its conclusions. Evaluate recall at the screening depth and the screening effort needed to reach a recall target, not precision at the top [S14 sl. 11].

**Q:** Name three challenges of domain-specific IR and a remedy each.
**A:** Domain vocabulary (domain-pretrained LMs such as BioBERT/LegalBERT), few labels (campaign data, click logs, distillation), long documents (paragraph-level scoring, summaries) [S14 sl. 17-18, 26].

**Q:** How does legal prior-case retrieval differ from eDiscovery?
**A:** Prior-case retrieval is precision-oriented (the most relevant precedents); eDiscovery must produce all relevant documents (high recall) under procedural rules [S14 sl. 22-26].

**Q:** What does BEIR show about transfer of MS MARCO-trained models?
**A:** BM25 is a robust zero-shot baseline; dense retrievers often underperform it out of domain; re-ranking and late interaction are best on average but costly [S58].

**Q:** What does BioASQ Task b ask for?
**A:** Phase A: relevant documents and snippets for expert biomedical questions; phase B: exact answers and paragraph-length ideal answers [S57].

## Code

No domain data is downloaded (network-free tests). The pipeline pieces transfer: [`../src/py/bm25.py`](../src/py/bm25.py) (first stage), [`../src/py/dense_retrieval.py`](../src/py/dense_retrieval.py) (dense first stage), [`../src/py/knrm.py`](../src/py/knrm.py) (re-ranking), [`../src/py/metrics.py`](../src/py/metrics.py) `recall_at_k` for recall-oriented evaluation.
