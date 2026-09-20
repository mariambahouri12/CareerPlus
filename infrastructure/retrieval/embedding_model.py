from sentence_transformers import SentenceTransformer

import config


class EmbeddingModel:
    """Generate embeddings for companies and queries."""

    def __init__(self, model_name: str | None = None):
        self.model = SentenceTransformer(model_name or config.EMBEDDING_MODEL)

    def embed_documents(self, texts):
        return self.model.encode(texts, normalize_embeddings=True)

    def embed_query(self, text: str):
        return self.model.encode(text, normalize_embeddings=True)