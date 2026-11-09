from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from indexing.embeddings import Embeddings
from indexing.es_index import ElasticIndex

app = FastAPI()

INDEX_NAME = "documents"
CANDIDATES = 50
RRF_K = 60

es = ElasticIndex(INDEX_NAME)
embeddings = Embeddings()


def to_cosine(es_score):
    return 2 * es_score - 1


def format_results(hits, cosine=False):
    results = []
    for rank, hit in enumerate(hits, start=1):
        score = to_cosine(hit["_score"]) if cosine else hit["_score"]
        results.append({
            "rank": rank,
            "path": hit["_source"]["path"],
            "score": round(score, 4),
            "snippet": hit["_source"]["content"][:200],
        })
    return results


@app.get("/")
def home():
    return FileResponse("ui/index.html")


@app.get("/download")
def download(path: str):
    if not es.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=path.split("/")[-1])


@app.get("/search/bm25")
def search_bm25(query: str, size: int = 10):
    print(f"[bm25] query={query!r} size={size}")
    hits = es.search(query, field="content", size=size)
    return {"mode": "bm25", "query": query, "results": format_results(hits)}


@app.get("/search/vector")
def search_vector(query: str, size: int = 10):
    print(f"[vector] query={query!r} size={size}")
    vector = embeddings.embed(query)
    hits = es.search_embedding(vector, field="chunks.embedding", k=size)
    return {"mode": "vector", "query": query, "results": format_results(hits, cosine=True)}


@app.get("/search/reranked")
def search_reranked(query: str, size: int = 10):
    print(f"[reranked] query={query!r} size={size}")
    bm25_hits = es.search(query, field="content", size=CANDIDATES)
    vector = embeddings.embed(query)
    vector_hits = es.search_embedding(vector, field="chunks.embedding", k=CANDIDATES)
    hits = reciprocal_rank_fusion([bm25_hits, vector_hits])[:size]
    return {"mode": "reranked", "query": query, "results": format_results(hits)}


def reciprocal_rank_fusion(rankings, k=RRF_K):
    scores = {}
    docs = {}

    for hits in rankings:
        for rank, hit in enumerate(hits, start=1):
            doc_id = hit["_id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
            docs[doc_id] = hit

    fused = []
    for doc_id in sorted(scores, key=scores.get, reverse=True):
        fused.append({"_source": docs[doc_id]["_source"], "_score": scores[doc_id]})
    return fused
