from typing import Dict, List

from sentence_transformers import CrossEncoder

import config


class CompanyReranker:
    """Cross-encoder reranker for company search."""

    def __init__(self, model_name: str | None = None):
        self.model = CrossEncoder(model_name or config.RERANKER_MODEL)
        print(f"[RERANKER] Device: {self.model.model.device}")

    def rerank(self, query: str, results: List[Dict], top_k: int = 5) -> List[Dict]:
        if not results:
            return []
        pairs = [(query, self._doc_text(r["company"])) for r in results]
        scores = self.model.predict(pairs)
        reranked = []
        for r, s in zip(results, scores):
            item = dict(r)
            item["reranker_score"] = float(s)
            reranked.append(item)
        reranked.sort(key=lambda x: x["reranker_score"], reverse=True)
        return reranked[:top_k]

    @staticmethod
    def _doc_text(company: Dict) -> str:
        return f"""
Company:
{company.get('name', '')}

Domain:
{company.get('domain', '')}

Country:
{company.get('country', '')}

Description:
{company.get('description', '')}
""".strip()