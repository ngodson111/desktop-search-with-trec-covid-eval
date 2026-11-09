import requests


class Embeddings:
    def __init__(self, model="all-minilm", url="http://localhost:11434",
                 chunk_size=200, overlap=50):
        self.model = model
        self.url = url
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document):
        words = document.split()
        step = self.chunk_size - self.overlap
        chunks = []

        for start in range(0, len(words), step):
            chunk_words = words[start:start + self.chunk_size]
            chunks.append(" ".join(chunk_words))
            if start + self.chunk_size >= len(words):
                break

        return chunks

    def embed(self, chunk):
        response = requests.post(
            f"{self.url}/api/embed",
            json={"model": self.model, "input": chunk},
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]
