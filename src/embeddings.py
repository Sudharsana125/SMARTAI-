"""
embeddings.py
=============
Wraps Sentence Transformers to provide a consistent embedding interface for
both document chunks (indexing time) and user queries (retrieval time).

Using a local Sentence Transformers model (rather than a paid embedding
API) keeps the embedding step free and fast, which is ideal for a
demo/college-project deployment, while still producing high-quality
multilingual-capable vectors.
"""

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from src.utils import get_logger

logger = get_logger(__name__)

# 'paraphrase-multilingual-MiniLM-L12-v2' supports 50+ languages including
# English, Tamil and Hindi, and produces 384-dimensional embeddings with a
# good speed/quality trade-off for a CPU-friendly demo deployment.
DEFAULT_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingGenerator:
    """
    Generates vector embeddings for text using a Sentence Transformers
    model. Wraps the model as a singleton-per-process via ``lru_cache`` on
    the loader so the (relatively large) model is loaded into memory only
    once, even across multiple ``EmbeddingGenerator`` instantiations during
    a Streamlit re-run.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        """
        Args:
            model_name: Name of the Sentence Transformers model to load
                from the HuggingFace hub.
        """
        self.model_name = model_name
        self._model = self._load_model(model_name)

    @staticmethod
    @lru_cache(maxsize=2)
    def _load_model(model_name: str) -> SentenceTransformer:
        """
        Load (and cache) the Sentence Transformers model.

        Args:
            model_name: HuggingFace model identifier.

        Returns:
            Loaded ``SentenceTransformer`` instance.
        """
        logger.info("Loading embedding model '%s' (first load may take a while)...", model_name)
        model = SentenceTransformer(model_name)
        logger.info("Embedding model '%s' loaded successfully.", model_name)
        return model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts (e.g. document chunks).

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors (one list of floats per input text).
        """
        if not texts:
            return []
        embeddings = self._model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a single user query.

        Args:
            query: The user's search/chat query text.

        Returns:
            Embedding vector as a list of floats.
        """
        embedding = self._model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding[0].tolist()

    @property
    def dimension(self) -> int:
        """Return the dimensionality of vectors produced by this model."""
        return self._model.get_sentence_embedding_dimension()
