from typing import Dict, List


class RRFFusion:
    """
    Reciprocal Rank Fusion.

    Combines rankings from multiple retrieval systems
    without requiring their raw scores to be comparable.
    """

    def __init__(self, k: int = 60):
        self.k = k

    def fuse(
        self,
        *result_lists: List[Dict],
    ) -> List[Dict]:

        fused_scores: Dict[int, float] = {}
        documents: Dict[int, Dict] = {}

        for results in result_lists:

            for rank, result in enumerate(
                results,
                start=1,
            ):

                index = result["index"]

                # -----------------------------
                # RRF score
                # -----------------------------

                fused_scores[index] = (
                    fused_scores.get(index, 0.0)
                    + 1.0 / (self.k + rank)
                )

                # -----------------------------
                # Merge information
                # -----------------------------

                if index not in documents:
                    documents[index] = {
                        "index": index,
                        "job": result["job"],
                    }

                # Keep FAISS score
                if "faiss_score" in result:
                    documents[index]["faiss_score"] = (
                        result["faiss_score"]
                    )

                # Keep BM25 score
                if "bm25_score" in result:
                    documents[index]["bm25_score"] = (
                        result["bm25_score"]
                    )

        # -----------------------------
        # Sort by RRF
        # -----------------------------

        ranked_indices = sorted(
            fused_scores.keys(),
            key=lambda index: fused_scores[index],
            reverse=True,
        )

        # -----------------------------
        # Build results
        # -----------------------------

        fused_results = []

        for index in ranked_indices:

            result = dict(
                documents[index]
            )

            result["rrf_score"] = (
                fused_scores[index]
            )

            fused_results.append(result)

        return fused_results