# Desktop Search over Local Files

A desktop search engine that scans a folder, reads text and PDF files, and searches them in
three ways: **BM25** (keyword), **Vector** (meaning, all-MiniLM embeddings) and **Hybrid**
(both merged with Reciprocal Rank Fusion). It is evaluated on 1,453 COVID-19 papers from
TREC-COVID using expert relevance labels.

Built for 7CS134 Data Mining and Analytics, University of Wolverhampton.

## Folder layout

```
extractor/      scan a folder and read text or PDF files
indexing/       chunk, embed and store files in Elasticsearch
searching/      FastAPI search service (BM25, vector, hybrid, download)
ui/             the search page
infra/          Docker files for Elasticsearch and the embedding model
documents/      the 1,453 TREC-COVID papers as .txt files
evaluation/     expert labels (CSV) and the evaluation notebook
```

Large raw downloads are not included. See `documents/trec-covid/README.md` for the data sources.

## Requirements

- **Python 3.9+** – https://www.python.org/downloads/
- **Docker Desktop** – https://www.docker.com/products/docker-desktop/
  Install it, open it and wait until it says it is running.

## How to run

Run these commands in a terminal, from the project folder.

**1. Get the code**

```bash
git clone https://github.com/ngodson111/desktop-search-with-trec-covid-eval.git
cd desktop-search-with-trec-covid-eval
```

**2. Install the Python packages**

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Start Elasticsearch and the embedding model**

```bash
docker compose -f infra/docker-compose.yml up -d
```

The first start downloads the images and the model, so it takes a few minutes.
Check it is ready: `curl localhost:9200` should return JSON.

**4. Build the search index**

```bash
python -m indexing.index documents/trec-covid --pattern="*.txt"
```

This takes several minutes. Check with `curl localhost:9200/documents/_count` – it should say
`"count":1453`.

Optional flags: `--pattern="*.pdf"`, `--depth=2`, `--from 2026-01-01` (only files created on
or after that date). You can point it at any folder, for example `~/Documents`.

**5. Start the search page**

```bash
uvicorn searching.api:app --reload --port 8000
```

Open http://localhost:8000, type a question and press Search. Click a file name to download it.

**6. Run the evaluation (optional)**

```bash
cd evaluation
jupyter notebook evaluation.ipynb
```

Run all cells. It prints Precision@10 and MRR for the three methods.

| Method | Precision@10 | MRR |
|---|---|---|
| BM25 | 0.62 | 0.63 |
| Vector | 0.85 | 1.00 |
| Hybrid | 0.89 | 0.95 |

## Stop

```bash
docker compose -f infra/docker-compose.yml down       # keeps the index
docker compose -f infra/docker-compose.yml down -v    # also deletes the index
```

## Sources

- CORD-19: https://huggingface.co/datasets/allenai/cord19 (Wang et al., 2020)
- TREC-COVID: https://huggingface.co/datasets/BeIR/trec-covid and
  https://huggingface.co/datasets/BeIR/trec-covid-qrels (Voorhees et al., 2020; Thakur et al., 2021)
- Reciprocal Rank Fusion: Cormack, Clarke and Büttcher (2009)
- Tools: Elasticsearch 8.15, Ollama (all-minilm), FastAPI, pypdf, pandas, Jupyter

Data is for research use only; each paper keeps its own licence.
