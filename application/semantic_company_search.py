"""Use case: semantic retrieval over company descriptions."""
from __future__ import annotations

from domain.ports.company_repository import CompanyRepositoryPort
from domain.ports.company_retriever import CompanyRetrieverPort


class SemanticCompanySearchUseCase:
    def __init__(
        self,
        retriever: CompanyRetrieverPort,
        repo: CompanyRepositoryPort,
    ) -> None:
        self.retriever = retriever
        self.repo = repo

    def run(self, query: str, top_k: int = 5, threshold: float = 0.30) -> dict:
        candidates = self.retriever.search(query, retrieval_k=20)
        kept = [r for r in candidates if r.get("reranker_score", 0.0) >= threshold]
        kept.sort(key=lambda r: r.get("reranker_score", 0.0), reverse=True)
        return {
            "status": "success",
            "matches_found": len(kept[:top_k]),
            "results": [
                {
                    "company": r["company"],
                    "reranker_score": round(r.get("reranker_score", 0.0), 3),
                    "rrf_score": round(r.get("rrf_score", 0.0), 5),
                }
                for r in kept[:top_k]
            ],
        }