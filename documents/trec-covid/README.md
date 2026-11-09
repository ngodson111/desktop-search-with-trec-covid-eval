# TREC-COVID Subset

1,453 CORD-19 papers (title + abstract) sampled from **TREC-COVID**, the official search
benchmark built on CORD-19. Every paper comes with **expert relevance judgments**, so the search
engine can be evaluated without making our own labels.

## Source

| | |
|---|---|
| Benchmark | TREC-COVID (Text REtrieval Conference, NIST) |
| Underlying dataset | CORD-19 ([allenai/cord19](https://huggingface.co/datasets/allenai/cord19)) |
| Papers + questions | [BeIR/trec-covid](https://huggingface.co/datasets/BeIR/trec-covid) (Hugging Face) |
| Relevance labels | [BeIR/trec-covid-qrels](https://huggingface.co/datasets/BeIR/trec-covid-qrels) (Hugging Face) |
| Official site | [ir.nist.gov/trec-covid](https://ir.nist.gov/trec-covid/) |

Citations:

> Voorhees, E., Alam, T., Bedrick, S., et al. (2020). TREC-COVID: Constructing a Pandemic
> Information Retrieval Test Collection. *ACM SIGIR Forum*, 54(1).
> [arXiv:2005.04474](https://arxiv.org/abs/2005.04474)

> Thakur, N., Reimers, N., Rücklé, A., Srivastava, A., Gurevych, I. (2021). BEIR: A Heterogeneous
> Benchmark for Zero-shot Evaluation of Information Retrieval Models. *NeurIPS Datasets and
> Benchmarks*. [arXiv:2104.08663](https://arxiv.org/abs/2104.08663)

## The 10 questions used

| ID | Question |
|---|---|
| q01 | what is the origin of COVID-19 |
| q02 | how does the coronavirus respond to changes in the weather |
| q18 | what are the best masks for preventing infection by Covid-19? |
| q24 | what kinds of complications related to COVID-19 are associated with diabetes |
| q26 | what are the initial symptoms of Covid-19? |
| q30 | is remdesivir an effective treatment for COVID-19 |
| q33 | What vaccine candidates are being tested for Covid-19? |
| q42 | Does Vitamin D impact COVID-19 prevention and treatment? |
| q45 | How has the COVID-19 pandemic impacted mental health? |
| q47 | what are the health outcomes for children who contract COVID-19? |

IDs match the official TREC-COVID topic numbers.

## How the subset was built

1. Chose 10 of the 50 TREC-COVID questions, covering different topics with little overlap.
2. For each question, took a random sample of 150 papers that experts had judged for it
   (random seed 42), skipping papers with fewer than 30 words of text.
3. Combined them (some papers were picked for more than one question): **1,453 papers**.
4. Saved each paper as `<cord_uid>.txt` containing the title, a blank line, then the abstract.
5. Saved every expert judgment for these papers and questions to
   `evaluation/trec_covid_evaluator.csv` (**2,072 labels**).

## Labels

TREC-COVID experts graded each paper for a question:

| TREC score | Meaning | `relevant` column |
|---|---|---|
| 2 | Highly relevant | 1 |
| 1 | Partly relevant | 1 |
| 0 | Not relevant | 0 |

A paper with no judgment for a question counts as not relevant for it.

## Limitations

- The corpus contains only papers that were judged, so it has more relevant papers than a random
  sample of CORD-19 would.
- A paper sampled for one question may be relevant to another question without having been judged
  for it; it then counts as not relevant there.
