import json
from pathlib import Path
from typing import List, Dict

import faiss
import numpy as np


class FAISSVectorStore:
    """Persistent FAISS vector store for job offers."""

    def __init__(
        self,
        index_path: str = "data/faiss/jobs.index",
        metadata_path: str = "data/faiss/jobs_metadata.json",
    ):
        self.index_path = Path(index_path)
        self.metadata_path = Path(metadata_path)

        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index = None
        self.documents: List[Dict] = []

        self._load()

    def _load(self):
        """Load FAISS index and metadata if they exist."""

        if self.index_path.exists():
            self.index = faiss.read_index(
                str(self.index_path)
            )

        if self.metadata_path.exists():
            with open(
                self.metadata_path,
                "r",
                encoding="utf-8",
            ) as file:
                self.documents = json.load(file)

    def add(
        self,
        embeddings,
        documents: List[Dict],
    ):
        """Add embeddings and their documents."""

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        if self.index is None:
            dimension = embeddings.shape[1]

            self.index = faiss.IndexFlatIP(
                dimension
            )

        self.index.add(embeddings)

        self.documents.extend(documents)

        self.save()

    def search(
        self,
        query_embedding,
        top_k: int = 5,
    ) -> List[Dict]:
        """Search for the most similar jobs."""

        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(
            [query_embedding],
            dtype="float32",
        )

        top_k = min(
            top_k,
            self.index.ntotal,
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            results.append(
                {
                    "index": int(index),
                    "faiss_score": float(score),
                    "job": self.documents[index],
                }
            )

        return results

    def save(self):
        """Persist FAISS index and metadata."""

        if self.index is not None:
            faiss.write_index(
                self.index,
                str(self.index_path),
            )

        with open(
            self.metadata_path,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.documents,
                file,
                ensure_ascii=False,
                indent=2,
            )