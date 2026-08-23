from rag.embedding_model import EmbeddingModel
from rag.vector_store import FAISSVectorStore
from rag.bm25_store import BM25Store
from rag.reranker import JobReranker
from rag.rrf import RRFFusion


class JobRetriever:
    """
    Hybrid job retrieval pipeline.

    Pipeline:
        1. Dense retrieval (BGE-M3 + FAISS)
        2. Lexical retrieval (BM25)
        3. Reciprocal Rank Fusion (RRF)
        4. Cross-encoder reranking

    Important:
        The retriever generates and reranks `retrieval_k`
        candidates.

        The final `top_k` selection is handled by
        SearchJobsTool AFTER applying the reranker threshold.
    """

    def __init__(self):

        print("Initializing JobRetriever...")

        # Load embedding model once
        self.embedding_model = EmbeddingModel()

        # Load persistent FAISS index
        self.vector_store = FAISSVectorStore()

        # Create BM25 index once
        self.bm25_store = BM25Store()

        # Load reranker once
        self.reranker = JobReranker()

        # RRF fusion
        self.rrf = RRFFusion()

        # Build BM25 once
        self._build_bm25_index()

        print("JobRetriever ready.")

    # ============================================================
    # BM25
    # ============================================================

    def _build_bm25_index(self):
        """
        Build BM25 from the documents already stored
        in the FAISS metadata.

        Executed only once when JobRetriever is initialized.
        """

        documents = self.vector_store.documents

        if not documents:

            print("No documents available for BM25.")

            return

        print(
            f"Building BM25 index for "
            f"{len(documents)} jobs..."
        )

        texts = [
            self._build_job_text(job)
            for job in documents
        ]

        self.bm25_store.build(
            documents=documents,
            texts=texts,
        )

        print("BM25 index ready.")

    # ============================================================
    # SEARCH
    # ============================================================

    def search(
        self,
        query: str,
        top_k: int = 5,
        retrieval_k: int = 20,
    ):
        """
        Hybrid retrieval pipeline.

        The `retrieval_k` candidates are:
            FAISS -> BM25 -> RRF -> Cross-Encoder

        IMPORTANT:
            `top_k` is NOT applied here.

        The reranker returns up to `retrieval_k` candidates,
        because SearchJobsTool must apply the reranker threshold
        BEFORE applying the user's requested top_k.

        Final logic:

            retrieval_k candidates
                    ↓
                reranking
                    ↓
             threshold >= 0.30
                    ↓
                sorting
                    ↓
                  top_k
        """

        # ----------------------------------
        # 1. Dense retrieval
        # ----------------------------------

        query_embedding = (
            self.embedding_model.embed_query(
                query
            )
        )

        faiss_results = (
            self.vector_store.search(
                query_embedding=query_embedding,
                top_k=retrieval_k,
            )
        )

        # ----------------------------------
        # 2. BM25 retrieval
        # ----------------------------------

        bm25_results = (
            self.bm25_store.search(
                query=query,
                top_k=retrieval_k,
            )
        )

        # ----------------------------------
        # 3. RRF fusion
        # ----------------------------------

        fused_results = self.rrf.fuse(
            faiss_results,
            bm25_results,
        )

        # ----------------------------------
        # 4. Candidates for reranking
        # ----------------------------------

        candidates = fused_results[
            :retrieval_k
        ]

        # ----------------------------------
        # 5. Cross-encoder reranking
        # ----------------------------------

        # IMPORTANT:
        # We rerank ALL retrieval_k candidates.
        #
        # We do NOT use top_k here because the final
        # top_k must be applied AFTER the threshold.
        reranked_results = (
            self.reranker.rerank(
                query=query,
                results=candidates,
                top_k=retrieval_k,
            )
        )

        return reranked_results

    # ============================================================
    # TEXT REPRESENTATION
    # ============================================================

    @staticmethod
    def _build_job_text(job):
        """
        Build the same textual representation
        used during indexing.
        """

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