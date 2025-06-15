import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from pathlib import Path


class QuoteSearch:
    def __init__(self, index_path: Path, json_path: Path,
                 model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.index_path = Path(index_path)
        self.json_path = Path(json_path)
        self.model = SentenceTransformer(model_name)

        self.quotes = []
        self.index = None
        self.dimension = None

        self._load()

    def _load(self):
        if self.json_path.exists():
            with self.json_path.open(encoding="utf-8") as f:
                self.quotes = json.load(f)

        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.dimension = self.index.d

    def _save(self):
        with self.json_path.open("w", encoding="utf-8") as f:
            json.dump(self.quotes, f, ensure_ascii=False, indent=2)
        if self.index:
            faiss.write_index(self.index, str(self.index_path))

    def _normalize(self, vecs: np.ndarray) -> np.ndarray:
        return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

    def list_quotes(self):
        return self.quotes

    def add_quote(self, text: str, label: str = None):
        embedding = self.model.encode([text]).astype("float32")
        embedding = self._normalize(embedding)

        if self.index is None:
            self.dimension = embedding.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)

        self.index.add(embedding)
        self.quotes.append({"text": text, "label": label})
        self._save()

    def remove_quote(self, idx: int):
        if idx < 0 or idx >= len(self.quotes):
            raise IndexError("Invalid quote index")

        del self.quotes[idx]

        if self.quotes:
            embeddings = self.model.encode([q["text"] for q in self.quotes]).astype("float32")
            embeddings = self._normalize(embeddings)

            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)
        else:
            self.index = faiss.IndexFlatIP(self.dimension or 384)  # default dimension fallback

        self._save()

    def query(self, text: str, top_n: int = 3, threshold: float = 0.5):
        if not self.index or not self.quotes:
            return []

        embedding = self.model.encode([text]).astype("float32")
        embedding = self._normalize(embedding)

        scores, indices = self.index.search(embedding, top_n)
        matches = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.quotes) and score >= threshold:
                matches.append({
                    "score": float(score),
                    "text": self.quotes[idx]["text"],
                    "label": self.quotes[idx].get("label")
                })

        return matches