
from pathlib import Path
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    MODEL_PATH = (
        Path(__file__).resolve().parent.parent
        / "EmbeddinModel"
        / "all-MiniLM-L6-v2"
    )

    def __init__(self, model=None):
        if model is not None:
            self.model = model
        else:
            if not self.MODEL_PATH.exists():
                raise FileNotFoundError(
                    f"Embedding model not found: {self.MODEL_PATH}"
                )

            self.model = SentenceTransformer(
                str(self.MODEL_PATH),
                local_files_only=True
            )

    def encode(self, text: str) -> list[float]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            raise ValueError("text cannot be empty")

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        if any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            raise ValueError("All texts must be non-empty strings")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings.tolist()