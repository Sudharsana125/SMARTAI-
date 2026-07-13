"""
embeddings.py
=============
Wraps the Google Gemini API to provide a consistent embedding interface for
both document chunks (indexing time) and user queries (retrieval time).

This bypasses the need for local sentence-transformers models, avoiding
network blocks when downloading models from Hugging Face.
"""

from typing import List
import requests
import json

from src.utils import get_logger, get_env_var

logger = get_logger(__name__)

DEFAULT_MODEL_NAME = "models/gemini-embedding-2"


class EmbeddingGenerator:
    """
    Generates vector embeddings for text using the Google Gemini API.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        """
        Args:
            model_name: Name of the Gemini embedding model.
        """
        self.model_name = model_name
        self.api_key = get_env_var("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY is not set. Embeddings will fail.")
        
        # Gemini text-embedding-004 produces 768-dimensional embeddings
        self._dimension = 768

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
            
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:batchEmbedContents?key={self.api_key}"
        
        requests_body = []
        for t in texts:
            requests_body.append({
                "model": self.model_name,
                "content": {"parts": [{"text": t}]}
            })
            
        payload = {"requests": requests_body}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Gemini API Error: {response.text}")
                
            data = response.json()
            embeddings = []
            for item in data.get("embeddings", []):
                embeddings.append(item["values"])
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings via Gemini: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate an embedding for a single user query.

        Args:
            query: The user's search/chat query text.

        Returns:
            Embedding vector as a list of floats.
        """
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        """Return the dimensionality of vectors produced by this model."""
        return self._dimension
