"""
vector_store.py
================
Wraps ChromaDB to provide persistent vector storage for document chunk
embeddings, along with add/query/clear operations used by the rest of the
RAG pipeline.
"""

import uuid
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings

from src.embeddings import EmbeddingGenerator
from src.text_splitter import TextChunk
from src.utils import ensure_directory, get_logger

logger = get_logger(__name__)

DEFAULT_COLLECTION_NAME = "company_knowledge_base"
DEFAULT_PERSIST_DIRECTORY = "data/vector_db"


class VectorStoreError(Exception):
    """Raised when a vector store operation fails."""


class VectorStore:
    """
    Persistent wrapper around a ChromaDB collection.

    Responsible for:
      * Persisting chunk embeddings to disk (so the knowledge base survives
        app restarts).
      * Adding new document chunks.
      * Performing similarity search for retrieval.
      * Clearing/resetting the knowledge base.
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        persist_directory: str = DEFAULT_PERSIST_DIRECTORY,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ) -> None:
        """
        Args:
            embedding_generator: Shared ``EmbeddingGenerator`` instance used
                to embed both stored chunks and incoming queries.
            persist_directory: Directory on disk where ChromaDB persists
                its data.
            collection_name: Name of the ChromaDB collection to use.
        """
        self.embedding_generator = embedding_generator
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        ensure_directory(persist_directory)

        try:
            self._client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                "Connected to ChromaDB collection '%s' at '%s' (%d existing chunks).",
                collection_name,
                persist_directory,
                self._collection.count(),
            )
        except Exception as exc:
            raise VectorStoreError(f"Failed to initialize ChromaDB: {exc}") from exc

    def add_chunks(self, chunks: List[TextChunk]) -> int:
        """
        Embed and add a list of text chunks to the vector store.

        Args:
            chunks: List of ``TextChunk`` objects to index.

        Returns:
            Number of chunks successfully added.

        Raises:
            VectorStoreError: If embedding or insertion fails.
        """
        if not chunks:
            return 0

        try:
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_generator.embed_texts(texts)
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [chunk.to_metadata_dict() for chunk in chunks]

            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )
            logger.info("Added %d chunk(s) to vector store.", len(chunks))
            return len(chunks)
        except Exception as exc:
            raise VectorStoreError(f"Failed to add chunks to vector store: {exc}") from exc

    def similarity_search(
        self,
        query: str,
        top_k: int = 4,
        source_filter: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve the most semantically similar chunks to a query.

        Args:
            query: The user's natural-language query.
            top_k: Number of top results to retrieve.
            source_filter: Optional filename to restrict the search to a
                single source document.

        Returns:
            List of result dictionaries, each containing ``text``,
            ``source``, ``page``, ``chunk_id`` and ``score`` (similarity,
            higher is more relevant).

        Raises:
            VectorStoreError: If the query fails.
        """
        if self.is_empty():
            return []

        try:
            query_embedding = self.embedding_generator.embed_query(query)
            where_clause = {"source": source_filter} if source_filter else None

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, max(self._collection.count(), 1)),
                where=where_clause,
            )

            formatted_results: List[Dict] = []
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for doc_text, metadata, distance in zip(documents, metadatas, distances):
                # ChromaDB cosine distance -> similarity score (0 to 1, higher = better)
                similarity_score = max(0.0, 1.0 - distance)
                page = metadata.get("page", -1)
                formatted_results.append(
                    {
                        "text": doc_text,
                        "source": metadata.get("source", "unknown"),
                        "page": page if page != -1 else None,
                        "chunk_id": metadata.get("chunk_id", 0),
                        "score": round(similarity_score, 4),
                    }
                )
            return formatted_results
        except Exception as exc:
            raise VectorStoreError(f"Similarity search failed: {exc}") from exc

    def is_empty(self) -> bool:
        """Return True if the vector store currently has no indexed chunks."""
        try:
            return self._collection.count() == 0
        except Exception:
            return True

    def count(self) -> int:
        """Return the number of chunks currently stored."""
        try:
            return self._collection.count()
        except Exception:
            return 0

    def list_sources(self) -> List[str]:
        """
        Return a sorted list of unique source filenames currently indexed
        in the vector store.

        Returns:
            Sorted list of distinct document filenames.
        """
        try:
            if self.is_empty():
                return []
            all_records = self._collection.get(include=["metadatas"])
            sources = {
                meta.get("source", "unknown")
                for meta in all_records.get("metadatas", [])
                if meta
            }
            return sorted(sources)
        except Exception as exc:
            logger.error("Failed to list sources: %s", exc)
            return []

    def clear(self) -> None:
        """
        Delete all chunks from the collection, resetting the knowledge
        base. The collection itself is recreated empty.
        """
        try:
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("Vector store collection '%s' cleared.", self.collection_name)
        except Exception as exc:
            raise VectorStoreError(f"Failed to clear vector store: {exc}") from exc
