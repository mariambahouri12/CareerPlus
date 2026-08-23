from rag.retriever import JobRetriever


class SearchJobsTool:
    """
    Tool for hybrid job search.

    Pipeline:

        FAISS + BM25
              ↓
             RRF
              ↓
        Candidate retrieval
              ↓
          Cross-encoder
           reranking
              ↓
      reranker_score >= 0.30
              ↓
          sort by score
              ↓
             top_k
    """

    name = "search_jobs"

    description = (
        "Search among job offers already scraped and indexed. "
        "Uses semantic search, lexical search and reranking. "
        "Only returns job offers with a reranker score >= 0.30. "
        "The threshold is applied before top_k selection. "
        "If fewer than top_k offers meet the threshold, "
        "only those offers are returned. "
        "Use this for questions about existing job offers "
        "(skills required, location, technologies, "
        "or relevance to a topic)."
    )

    # ============================================================
    # CONFIGURATION
    # ============================================================

    RERANKER_THRESHOLD = 0.30
    RETRIEVAL_K = 20

    # ============================================================
    # INIT
    # ============================================================

    def __init__(self):

        self.retriever = JobRetriever()

    # ============================================================
    # RUN
    # ============================================================

    def run(
        self,
        query: str,
        top_k: int = 5,
    ):
        """
        Search for relevant job offers.

        Logic:

            1. Retrieve up to RETRIEVAL_K candidates.
            2. Rerank all candidates.
            3. Keep only candidates with
               reranker_score >= RERANKER_THRESHOLD.
            4. Sort by reranker score descending.
            5. Return at most top_k results.

        Examples:

            7 offers >= 0.30 and top_k=5
                -> return 5

            7 offers >= 0.30 and top_k=15
                -> return 7

            3 offers >= 0.30 and top_k=5
                -> return 3

            0 offers >= 0.30
                -> return 0
        """

        # --------------------------------------------------------
        # Validate top_k
        # --------------------------------------------------------

        if top_k < 1:
            top_k = 1

        # --------------------------------------------------------
        # 1. Retrieve and rerank candidates
        # --------------------------------------------------------
        #
        # IMPORTANT:
        # The retriever reranks RETRIEVAL_K candidates.
        # We do NOT pass the user's top_k here because top_k
        # must be applied AFTER the threshold.
        #
        results = self.retriever.search(
            query=query,
            top_k=top_k,
            retrieval_k=self.RETRIEVAL_K,
        )

        # --------------------------------------------------------
        # 2. Apply reranker threshold
        # --------------------------------------------------------

        filtered_results = [
            r
            for r in results
            if r.get(
                "reranker_score",
                0.0
            ) >= self.RERANKER_THRESHOLD
        ]

        # --------------------------------------------------------
        # 3. Sort by reranker score
        # --------------------------------------------------------

        filtered_results.sort(
            key=lambda r: r.get(
                "reranker_score",
                0.0
            ),
            reverse=True,
        )

        # --------------------------------------------------------
        # 4. Apply user's top_k AFTER threshold
        # --------------------------------------------------------

        selected_results = filtered_results[:top_k]

        # --------------------------------------------------------
        # 5. Format output
        # --------------------------------------------------------

        return {
            "matches_found": len(selected_results),

            "results": [
                {
                    "faiss_index": r["index"],

                    "faiss_score": round(
                        r.get(
                            "score",
                            0.0
                        ),
                        3,
                    ),

                    "bm25_score": round(
                        r.get(
                            "bm25_score",
                            0.0
                        ),
                        3,
                    ),

                    "rrf_score": round(
                        r.get(
                            "rrf_score",
                            0.0
                        ),
                        5,
                    ),

                    "reranker_score": round(
                        r.get(
                            "reranker_score",
                            0.0
                        ),
                        3,
                    ),

                    "job": r["job"],
                }

                for r in selected_results
            ],
        }