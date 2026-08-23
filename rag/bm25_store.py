import re
from typing import Dict, List

from rank_bm25 import BM25Okapi


class BM25Store:
    """
    In-memory BM25 index for job offers.

    The documents are kept in the same order as the FAISS
    metadata so that document IDs remain aligned.
    """

    def __init__(self):
        self.documents: List[Dict] = []
        self.texts: List[str] = []
        self.bm25 = None

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Simple multilingual tokenizer.

        Keeps words, numbers and common technical terms.
        """
        text = text.lower()

        return re.findall(r"[a-z0-9]+(?:[+#.-]+[a-z0-9]*)*", text)

    def build(
        self,
        documents: List[Dict],
        texts: List[str],
    ) -> None:
        """
        Build the BM25 index from all documents.
        """

        self.documents = documents
        self.texts = texts

        tokenized_corpus = [
            self.tokenize(text)
            for text in texts
        ]

        if not tokenized_corpus:
            self.bm25 = None
            return

        self.bm25 = BM25Okapi(
            tokenized_corpus
        )

    def search(
        self,
        query: str,
        top_k: int = 30,
    ) -> List[Dict]:
        """
        Search using BM25.
        """

        if self.bm25 is None:
            return []

        query_tokens = self.tokenize(query)

        if not query_tokens:
            return []

        scores = self.bm25.get_scores(
            query_tokens
        )

        top_k = min(
            top_k,
            len(scores),
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True,
        )[:top_k]

        results = []

        for index in ranked_indices:
            results.append(
                {
                    "index": index,
                    "bm25_score": float(scores[index]),
                    "job": self.documents[index],
                }
            )

        return results