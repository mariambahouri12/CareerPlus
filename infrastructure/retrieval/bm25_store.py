"""In-memory BM25 index over company descriptions."""
from __future__ import annotations

import re
from typing import Dict, List

from rank_bm25 import BM25Okapi


class BM25Store:
    def __init__(self) -> None:
        self.documents: List[Dict] = []
        self.texts: List[str] = []
        self.bm25: BM25Okapi | None = None

    @staticmethod
    def tokenize(text: str) -> List[str]:
        text = text.lower()
        return re.findall(r"[a-z0-9]+(?:[+#.-]+[a-z0-9]*)*", text)

    def build(self, documents: List[Dict], texts: List[str]) -> None:
        self.documents = documents
        self.texts = texts
        corpus = [self.tokenize(t) for t in texts]
        if not corpus:
            self.bm25 = None
            return
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, top_k: int = 30) -> List[Dict]:
        if self.bm25 is None:
            return []
        tokens = self.tokenize(query)
        if not tokens:
            return []
        scores = self.bm25.get_scores(tokens)
        top_k = min(top_k, len(scores))
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {"index": i, "bm25_score": float(scores[i]), "company": self.documents[i]}
            for i in ranked
        ]