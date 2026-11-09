from elasticsearch import Elasticsearch


class ElasticIndex:
    def __init__(self, name, url="http://localhost:9200"):
        self.name = name
        self.es = Elasticsearch(url)

    def ensure_index(self, schema):
        if self.es.indices.exists(index=self.name):
            return
        self.es.indices.create(index=self.name, mappings=schema)

    def remove(self):
        self.es.indices.delete(index=self.name, ignore_unavailable=True)

    def store(self, doc, doc_id=None):
        self.es.index(index=self.name, id=doc_id, document=doc, refresh=True)

    def exists(self, doc_id):
        return self.es.exists(index=self.name, id=doc_id)

    def search(self, text, field="content", size=10):
        query = {"match": {field: text}}
        result = self.es.search(index=self.name, query=query, size=size)
        return result["hits"]["hits"]

    def search_embedding(self, vector, field="embedding", k=10):
        knn = {
            "field": field,
            "query_vector": vector,
            "k": k,
            "num_candidates": k * 10,
        }
        result = self.es.search(index=self.name, knn=knn, size=k)
        return result["hits"]["hits"]
