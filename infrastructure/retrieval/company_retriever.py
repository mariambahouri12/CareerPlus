"""Hybrid retrieval over company descriptions."""
from __future__ import annotations

from domain.ports.company_retriever import CompanyRetrieverPort
from infrastructure.retrieval.bm25_store import BM25Store
from infrastructure.retrieval.embedding_model import EmbeddingModel
from infrastructure.retrieval.faiss_store import FAISSVectorStore
from infrastructure.retrieval.reranker import CompanyReranker
from infrastructure.retrieval.rrf import RRFFusion


class CompanyRetriever(CompanyRetrieverPort):
    def __init__(self, index_path: str, metadata_path: str) -> None:
        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSVectorStore(index_path=index_path, metadata_path=metadata_path)
        self.bm25_store = BM25Store()
        self.reranker = CompanyReranker()
        self.rrf = RRFFusion()
        self._build_bm25()

    def _build_bm25(self) -> None:
        docs = self.vector_store.documents
        if not docs:
            return
        texts = [self._company_text(d) for d in docs]
        self.bm25_store.build(documents=docs, texts=texts)

    def search(self, query: str, retrieval_k: int = 20) -> list[dict]:
        qv = self.embedding_model.embed_query(query)
        dense = self.vector_store.search(query_embedding=qv, top_k=retrieval_k)
        sparse = self.bm25_store.search(query=query, top_k=retrieval_k)
        fused = self.rrf.fuse(dense, sparse)[:retrieval_k]
        return self.reranker.rerank(query=query, results=fused, top_k=retrieval_k)

    @staticmethod
    def _company_text(c: dict) -> str:
        return f"""
Company:
{c.get('name', '')}

Domain:
{c.get('domain', '')}

Country:
{c.get('country', '')}

Description:
{c.get('description', '')}
""".strip()