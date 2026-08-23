from rag.retriever import JobRetriever


class SearchJobsTool:
    """
    Tool for hybrid job search and CV-job matching.

    Normal search:

        User Query
             ↓
        FAISS + BM25
             ↓
            RRF
             ↓
        Candidate retrieval
             ↓
        Cross-encoder reranking
             ↓
        Threshold
             ↓
           Top-K


    CV matching:

        User Query + CV
             ↓
        FAISS + BM25
             ↓
            RRF
             ↓
        Candidate retrieval
             ↓
        Cross-encoder reranking
             ↓
        Threshold
             ↓
           Top-K
    """

    name = "search_jobs"

    description = (
        "Searches indexed job offers via hybrid semantic+lexical retrieval with reranking. Set use_cv=true only if the request requires comparing offers against the candidatesprofile rather than a keyword/topic search."
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
        use_cv: bool = False,
        cv_text: str | None = None,
    ):
        """
        Search for relevant job offers.

        Parameters
        ----------
        query:
            User's job-related query.

        top_k:
            Maximum number of results.

        use_cv:
            If True, the CV is included in the search query.

        cv_text:
            Uploaded CV text.
        """

        # --------------------------------------------------------
        # Validate top_k
        # --------------------------------------------------------

        if top_k < 1:
            top_k = 1

        if top_k > 20:
            top_k = 20

        # --------------------------------------------------------
        # Validate CV matching
        # --------------------------------------------------------

        if use_cv and not cv_text:

            return {
                "status": "error",
                "message": (
                    "CV matching was requested, but no CV "
                    "has been uploaded."
                ),
                "matches_found": 0,
                "cv_matching": False,
                "results": [],
            }

        # --------------------------------------------------------
        # Build search query
        # --------------------------------------------------------

        search_query = query

        if use_cv:

            search_query = f"""
User request:
{query}

Candidate CV:
{cv_text}
""".strip()

        # --------------------------------------------------------
        # Retrieve candidates
        # --------------------------------------------------------
        #
        # IMPORTANT:
        # We retrieve/rerank RETRIEVAL_K candidates.
        # The user's top_k is applied AFTER the threshold.
        #

        results = self.retriever.search(
            query=search_query,
            top_k=self.RETRIEVAL_K,
            retrieval_k=self.RETRIEVAL_K,
        )

        # --------------------------------------------------------
        # Apply reranker threshold
        # --------------------------------------------------------

        filtered_results = [
            r
            for r in results
            if r.get(
                "reranker_score",
                0.0,
            ) >= self.RERANKER_THRESHOLD
        ]

        # --------------------------------------------------------
        # Sort by reranker score
        # --------------------------------------------------------

        filtered_results.sort(
            key=lambda r: r.get(
                "reranker_score",
                0.0,
            ),
            reverse=True,
        )

        # --------------------------------------------------------
        # Apply top_k AFTER threshold
        # --------------------------------------------------------

        selected_results = filtered_results[:top_k]

        # --------------------------------------------------------
        # Format results
        # --------------------------------------------------------

        return {
            "status": "success",

            "matches_found": len(
                selected_results
            ),

            "cv_matching": use_cv,

            "results": [
                {
                    "faiss_index": r["index"],

                    "faiss_score": round(
                        r.get(
                            "score",
                            r.get(
                                "faiss_score",
                                0.0,
                            ),
                        ),
                        3,
                    ),

                    "bm25_score": round(
                        r.get(
                            "bm25_score",
                            0.0,
                        ),
                        3,
                    ),

                    "rrf_score": round(
                        r.get(
                            "rrf_score",
                            0.0,
                        ),
                        5,
                    ),

                    "reranker_score": round(
                        r.get(
                            "reranker_score",
                            0.0,
                        ),
                        3,
                    ),

                    "job": r["job"],
                }

                for r in selected_results
            ],
        }