from typing import List, Dict

from sentence_transformers import CrossEncoder


class JobReranker:
    """
    Cross-encoder reranker for job search.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-v2-m3",
    ):

        self.model = CrossEncoder(
            model_name
        )

        # Show the device used by the reranker
        print(
            f"[RERANKER] Device: "
            f"{self.model.model.device}"
        )

    def rerank(
        self,
        query: str,
        results: List[Dict],
        top_k: int = 5,
    ) -> List[Dict]:

        if not results:
            return []

        pairs = [
            (
                query,
                self._build_document_text(
                    result["job"]
                ),
            )
            for result in results
        ]

        scores = self.model.predict(
            pairs
        )

        reranked = []

        for result, score in zip(
            results,
            scores,
        ):

            item = dict(result)

            item["reranker_score"] = float(
                score
            )

            reranked.append(item)

        reranked.sort(
            key=lambda x: x["reranker_score"],
            reverse=True,
        )

        return reranked[:top_k]

    @staticmethod
    def _build_document_text(
        job: Dict,
    ) -> str:

        return f"""
Title:
{job.get("title", "")}

Company:
{job.get("company", "")}

Location:
{job.get("location", "")}

Description:
{job.get("description", "")}
""".strip()