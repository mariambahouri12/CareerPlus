"""Build the FAISS + BM25 indices from the company database."""
from __future__ import annotations

import logging
from typing import List

from domain.entities.company import Company
from infrastructure.retrieval.embedding_model import EmbeddingModel
from infrastructure.retrieval.faiss_store import FAISSVectorStore

logger = logging.getLogger(__name__)


class CompanyIndexer:
    def __init__(
        self,
        index_path: str,
        metadata_path: str,
    ) -> None:
        self.embedding_model = EmbeddingModel()
        self.vector_store = FAISSVectorStore(
            index_path=index_path,
            metadata_path=metadata_path,
        )

    def index(self, companies: List[Company]) -> int:
        if not companies:
            return 0
        docs = [c.to_dict() for c in companies]
        texts = [self._company_text(d) for d in docs]
        embeddings = self.embedding_model.embed_documents(texts)
        # Reset by overwriting the metadata path content — index flat rebuild
        self.vector_store.index = None
        self.vector_store.documents = []
        self.vector_store.add(embeddings, docs)
        logger.info("Indexed %d companies", len(docs))
        return len(docs)

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