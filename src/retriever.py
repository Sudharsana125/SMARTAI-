"""
retriever.py
============
Retrieval layer that sits on top of the ``VectorStore``. Responsible for
fetching the most relevant chunks for a given query, applying a relevance
threshold, and assembling them into a single context string (with source
labels) ready to be injected into the LLM prompt.
"""

from dataclasses import dataclass
from typing import List

from src.utils import get_logger
from src.vector_store import VectorStore

logger = get_logger(__name__)

DEFAULT_TOP_K = 4
DEFAULT_SCORE_THRESHOLD = 0.15  # Minimum similarity score to be considered relevant


@dataclass
class RetrievedChunk:
    """
    A single retrieved chunk along with its relevance score and source
    metadata, used for both context building and the UI's source panel.
    """

    text: str
    source: str
    page: int
    score: float


class Retriever:
    """
    Retrieves relevant document chunks from the vector store and formats
    them into an LLM-ready context block.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ) -> None:
        """
        Args:
            vector_store: The ``VectorStore`` instance to query against.
            top_k: Maximum number of chunks to retrieve per query.
            score_threshold: Minimum similarity score (0-1) for a chunk to
                be considered relevant enough to include in context.
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str) -> List[RetrievedChunk]:
        """
        Retrieve the top relevant chunks for a query, filtering out results
        below the relevance threshold.

        Args:
            query: The user's natural-language query.

        Returns:
            List of ``RetrievedChunk`` objects, ordered by descending
            relevance score.
        """
        if not query or not query.strip():
            return []

        raw_results = self.vector_store.similarity_search(query, top_k=self.top_k)

        chunks = [
            RetrievedChunk(
                text=result["text"],
                source=result["source"],
                page=result["page"],
                score=result["score"],
            )
            for result in raw_results
            if result["score"] >= self.score_threshold
        ]

        logger.info(
            "Retrieved %d relevant chunk(s) for query (out of %d candidates).",
            len(chunks),
            len(raw_results),
        )
        return chunks

    def build_context(self, chunks: List[RetrievedChunk]) -> str:
        """
        Assemble retrieved chunks into a single context string, labeling
        each excerpt with its source so the LLM can ground citations.

        Args:
            chunks: Chunks returned by ``retrieve``.

        Returns:
            Formatted context string. Empty string if no chunks provided.
        """
        if not chunks:
            return ""

        context_parts = []
        for idx, chunk in enumerate(chunks, start=1):
            page_label = f", page {chunk.page}" if chunk.page else ""
            context_parts.append(
                f"[Excerpt {idx} | Source: {chunk.source}{page_label}]\n{chunk.text}"
            )
        return "\n\n".join(context_parts)

    def retrieve_and_build_context(self, query: str) -> tuple:
        """
        Convenience method combining retrieval and context building in a
        single call.

        Args:
            query: The user's natural-language query.

        Returns:
            Tuple of ``(context_string, retrieved_chunks)``.
        """
        chunks = self.retrieve(query)
        context = self.build_context(chunks)
        return context, chunks
