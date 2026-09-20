import json
from pathlib import Path
from typing import Dict, List

import faiss
import numpy as np


class FAISSVectorStore:
    """Persistent FAISS vector store."""

    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

        self.index = None
        self.documents: List[Dict] = []
        self._load()

    def _load(self):
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        if self.metadata_path.exists():
            with open(self.metadata_path, "r", encoding="utf-8") as fh:
                self.documents = json.load(fh)

    def add(self, embeddings, documents: List[Dict]):
        embeddings = np.asarray(embeddings, dtype="float32")
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)
        self.documents.extend(documents)
        self.save()

    def search(self, query_embedding, top_k: int = 5) -> List[Dict]:
        if self.index is None or self.index.ntotal == 0:
            return []
        q = np.asarray([query_embedding], dtype="float32")
        top_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append({
                "index": int(idx),
                "faiss_score": float(score),
                "company": self.documents[idx],
            })
        return results

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, "w", encoding="utf-8") as fh:
            json.dump(self.documents, fh, ensure_ascii=False, indent=2)