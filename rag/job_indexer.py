from typing import List, Dict

from rag.embedding_model import EmbeddingModel
from rag.vector_store import FAISSVectorStore
from storage.job_repository import JobRepository


class JobIndexer:
    """Prepare and index scraped job offers."""

    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSVectorStore()
        self.repository = JobRepository()

    def index_jobs(self, jobs: List[Dict]) -> None:
        """Index a list of job offers."""

        if not jobs:
            return

        self.repository.save(jobs)

        texts = [
            self._build_job_text(job)
            for job in jobs
        ]

        embeddings = (
            self.embedding_model.embed_documents(texts)
        )

        self.vector_store.add(
            embeddings=embeddings,
            documents=jobs,
        )

    @staticmethod
    def _build_job_text(job: Dict) -> str:
        """Build the text used for embedding."""

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