# Desktop Search over Local Files

A small desktop search engine. It scans a folder on your computer, reads text and PDF files,
and lets you search them in three ways side by side:

| Method | What it does |
|---|---|
| **BM25** | Classic keyword search (Elasticsearch) |
| **Vector** | Meaning-based search using sentence embeddings (all-MiniLM via Ollama) |
| **Hybrid (RRF)** | Merges the two lists with Reciprocal Rank Fusion |

It is evaluated on a folder of 1,453 COVID-19 papers from **TREC-COVID**, which comes with
expert relevance labels. Built for the University of Wolverhampton module 7CS134 Data Mining
and Analytics.

## What is in this repository

```
extractor/extract_dir.py      scan a folder and read text or PDF files
indexing/
  embeddings.py               cut text into chunks and turn them into vectors (Ollama)
  es_index.py                 small wrapper around Elasticsearch
  index.py                    build the search index: scan -> read -> chunk -> embed -> store
searching/api.py              FastAPI web service: BM25, vector and hybrid search, file download
ui/index.html                 the search page (three columns)
infra/                        Docker files for Elasticsearch and the embedding model
documents/trec-covid/         1,453 papers as .txt files, plus a README about the dataset
evaluation/
  trec_covid_evaluator.csv    2,072 expert relevance labels for 10 questions
  evaluation.ipynb            notebook that computes Precision@10 and MRR
requirements.txt              Python packages
```

The large raw downloads (CORD-19 metadata, TREC-COVID parquet files) are **not** included.
`documents/trec-covid/README.md` explains where they come from and how the subset was built.

## What you need before you start

1. **Python 3.9 or newer.** Check with `python3 --version`. If you do not have it, download it
   from https://www.python.org/downloads/
2. **Docker Desktop.** This runs Elasticsearch and the embedding model for you, so you do not
   have to install them by hand.
   - Download: https://www.docker.com/products/docker-desktop/
   - Install guide for Mac: https://docs.docker.com/desktop/setup/install/mac-install/
   - Install guide for Windows: https://docs.docker.com/desktop/setup/install/windows-install/
   - Install guide for Linux: https://docs.docker.com/desktop/setup/install/linux/
   - After installing, **open Docker Desktop and wait until it says it is running**. Check with
     `docker --version` in a terminal.
3. About **3 GB of free disk space** for the Docker images and the index.
4. **Git** to clone this repository, or download it as a ZIP from GitHub.

## Step-by-step: running the project

All commands are typed in a terminal (Terminal on Mac, PowerShell or Command Prompt on Windows)
from inside the project folder.

### Step 1 — Get the code

```bash
git clone https://github.com/ngodson111/desktop-search-with-trec-covid-evaluator.git
```

```bash
cd desktop-search-with-trec-covid-evaluator
```

### Step 2 — Create a Python environment and install the packages

A virtual environment keeps this project's packages separate from the rest of your computer.

Mac / Linux:

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
```

```powershell
venv\Scripts\activate
```

Then, on any system:

```bash
pip install -r requirements.txt
```

You should see `(venv)` at the start of your terminal line. Every later step assumes the
environment is active. If you open a new terminal, run the `activate` command again.

### Step 3 — Start Elasticsearch and the embedding model with Docker

Make sure Docker Desktop is open and running, then:

```bash
docker compose -f infra/docker-compose.yml up -d
```

The first time, this downloads Elasticsearch 8.15 and Ollama and pulls the `all-minilm`
embedding model. It can take **5–10 minutes** depending on your internet connection. Later
starts take a few seconds.

Check that both services are up:

```bash
curl localhost:9200
```

You should get a JSON answer with `"cluster_name"` in it.

```bash
curl localhost:11434/api/embed -d '{"model":"all-minilm","input":"hello"}'
```

You should get a long list of numbers (the embedding).

If either command fails, wait a minute and try again. You can see what the containers are doing
with `docker compose -f infra/docker-compose.yml logs -f` (press Ctrl+C to stop watching).

### Step 4 — Build the search index

This reads every paper, cuts it into chunks, turns each chunk into a vector and stores
everything in Elasticsearch:

```bash
python -m indexing.index documents/trec-covid --pattern="*.txt"
```

It prints each file as it goes. For the 1,453 papers it takes roughly **5–15 minutes** (the
embedding step is the slow part). You only need to do this once; the index is kept in a Docker
volume and survives restarts.

Check that everything was indexed:

```bash
curl localhost:9200/documents/_count
```

The answer should contain `"count":1453`.

Options for the indexer:

| Option | Meaning | Example |
|---|---|---|
| `--pattern` | Only index files whose name matches | `--pattern="*.pdf"` |
| `--depth` | How many folder levels deep to look | `--depth=2` |
| `--from` | Only files created on or after this date | `--from 2026-01-01` |

To index your own folder instead, point it at that folder, for example
`python -m indexing.index ~/Documents --pattern="*.pdf"`.

### Step 5 — Start the search website

```bash
uvicorn searching.api:app --reload --port 8000
```

Open http://localhost:8000 in your browser. Type a question such as
*what are the initial symptoms of Covid-19* and press **Search**. You get three columns:
BM25, Vector and Reranked (the hybrid). Click a file name to download that file.

Press Ctrl+C in the terminal to stop the server.

The API can also be called directly, for example:
http://localhost:8000/search/bm25?query=remdesivir

### Step 6 — Run the evaluation (optional)

The notebook runs all 10 questions through the three methods and scores them against the expert
labels. The server from Step 5 does **not** need to be running, but Docker (Step 3) and the
index (Step 4) do.

The notebook must be started from inside the `evaluation` folder:

```bash
cd evaluation
```

```bash
jupyter notebook evaluation.ipynb
```

In the browser window that opens, choose **Run → Run All Cells**. At the end you get the
Precision@10 and MRR table, a per-question table and bar charts.

Expected results:

| Method | Precision@10 | MRR |
|---|---|---|
| BM25 | 0.62 | 0.63 |
| Vector | 0.85 | 1.00 |
| Hybrid (RRF) | 0.89 | 0.95 |

## Stopping and cleaning up

Stop the Docker containers (the index is kept):

```bash
docker compose -f infra/docker-compose.yml down
```

Stop them **and delete the index** so the next start is from scratch:

```bash
docker compose -f infra/docker-compose.yml down -v
```

## Common problems

| Problem | What to do |
|---|---|
| `docker: command not found` | Docker Desktop is not installed or not open. Install it (links above), open it and wait until it is running. |
| `curl localhost:9200` gives "connection refused" | Elasticsearch is still starting. Wait a minute and try again. |
| Indexing fails with a connection error on port 11434 | The embedding model is still being downloaded. Check with `docker compose -f infra/docker-compose.yml logs embedder`. |
| `ModuleNotFoundError` | The virtual environment is not active. Run the `activate` command from Step 2 again. |
| The search page shows "No results" | The index is empty. Run Step 4 and check the count. |
| `_count` shows more than 1453 | You indexed without `--pattern="*.txt"` and picked up README.md. Run the clean-up `down -v` command, start again and re-index with the pattern. |

## Rebuilding the dataset from the original sources (optional)

You do not need this to run the project; the 1,453 papers and the labels are already in the
repository. If you want to rebuild them, download the files below and follow the steps in
`documents/trec-covid/README.md`. Reading the parquet files needs one extra package:
`pip install pyarrow`.

- Papers and questions: https://huggingface.co/datasets/BeIR/trec-covid
- Relevance labels: https://huggingface.co/datasets/BeIR/trec-covid-qrels
- CORD-19 (the underlying collection): https://huggingface.co/datasets/allenai/cord19

## Acknowledgements

- CORD-19: Wang, L.L. et al. (2020). *CORD-19: The COVID-19 Open Research Dataset.*
  https://arxiv.org/abs/2004.10706
- TREC-COVID: Voorhees, E. et al. (2020). *TREC-COVID: Constructing a Pandemic Information
  Retrieval Test Collection.* ACM SIGIR Forum 54(1). https://arxiv.org/abs/2005.04474
- BEIR: Thakur, N. et al. (2021). *BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of
  Information Retrieval Models.* https://arxiv.org/abs/2104.08663
- Reciprocal Rank Fusion: Cormack, G.V., Clarke, C.L.A. and Büttcher, S. (2009). SIGIR 2009.
- Tools: Elasticsearch 8.15, Ollama with the all-minilm model, FastAPI, Uvicorn, pypdf, pandas,
  matplotlib, Jupyter.

The data is for research use only, and each paper keeps its own licence.
