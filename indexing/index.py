import argparse
from datetime import datetime

from extractor.extract_dir import read_file, scan_files
from indexing.embeddings import Embeddings
from indexing.es_index import ElasticIndex

INDEX_NAME = "documents"

DOCUMENTS_SCHEMA = {
    "properties": {
        "path": {"type": "keyword"},
        "content": {"type": "text", "analyzer": "english"},
        "chunks": {
            "type": "nested",
            "properties": {
                "text": {"type": "text", "analyzer": "english"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "similarity": "cosine",
                },
            },
        },
    }
}


def index(es: ElasticIndex, embeddings: Embeddings, path, depth=None, pattern="*", from_date=None):
    embeddings = Embeddings()
    file_paths = scan_files(path, depth, pattern, from_date)

    for file_path in file_paths:
        content = read_file(file_path)
        chunks = embeddings.chunk(content)
        doc = {
            "path": file_path,
            "content": content,
            "chunks": [{"text": chunk, "embedding": embeddings.embed(chunk)} for chunk in chunks],
        }
        es.store(doc, doc_id=file_path)

        print(f"\n{file_path} ({len(chunks)} chunks)")
        for number, chunk in enumerate(chunks, start=1):
            print(f"  [{number}] {chunk[:100]}...")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--depth", type=int, default=None)
    parser.add_argument("--pattern", default="*")
    parser.add_argument("--from", dest="from_date", type=datetime.fromisoformat, default=None)
    args = parser.parse_args()

    es = ElasticIndex(INDEX_NAME)
    embeddings = Embeddings()
    es.ensure_index(DOCUMENTS_SCHEMA)
    index(es, embeddings, args.path, args.depth, args.pattern, args.from_date)


if __name__ == "__main__":
    main()
