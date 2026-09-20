from typing import Dict, List


class RRFFusion:
    """Reciprocal Rank Fusion."""

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(self, *result_lists: List[Dict]) -> List[Dict]:
        fused_scores: Dict[int, float] = {}
        documents: Dict[int, Dict] = {}

        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                idx = result["index"]
                fused_scores[idx] = fused_scores.get(idx, 0.0) + 1.0 / (self.k + rank)
                if idx not in documents:
                    documents[idx] = {"index": idx, "company": result["company"]}
                if "faiss_score" in result:
                    documents[idx]["faiss_score"] = result["faiss_score"]
                if "bm25_score" in result:
                    documents[idx]["bm25_score"] = result["bm25_score"]

        ranked = sorted(fused_scores.keys(), key=lambda i: fused_scores[i], reverse=True)
        fused_results = []
        for idx in ranked:
            r = dict(documents[idx])
            r["rrf_score"] = fused_scores[idx]
            fused_results.append(r)
        return fused_results