from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Generate embeddings for jobs and queries."""

    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
    ):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
        )

    def embed_query(self, text: str):
        return self.model.encode(
            text,
            normalize_embeddings=True,
        )