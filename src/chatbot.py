"""
chatbot.py
==========
Top-level ``Chatbot`` class that ties together document ingestion, the
vector store, the retriever, and the RAG pipeline into a single, simple
interface for the Streamlit frontend to use. Also manages conversational
session memory (chat history).
"""

import tempfile
from pathlib import Path
from typing import List, Optional

from src.document_loader import DocumentLoader, DocumentLoaderError
from src.embeddings import EmbeddingGenerator
from src.rag_pipeline import ChatResponse, RAGPipeline
from src.retriever import Retriever
from src.text_splitter import DocumentTextSplitter
from src.utils import FileValidationError, get_logger, validate_file, validate_user_query
from src.vector_store import VectorStore, VectorStoreError

logger = get_logger(__name__)


class IngestionResult:
    """
    Result of ingesting one or more documents into the knowledge base.

    Attributes:
        filename: Name of the ingested file.
        success: Whether ingestion succeeded.
        chunks_added: Number of chunks added to the vector store.
        message: Human-readable status/error message.
    """

    def __init__(self, filename: str, success: bool, chunks_added: int = 0, message: str = ""):
        self.filename = filename
        self.success = success
        self.chunks_added = chunks_added
        self.message = message


class Chatbot:
    """
    High-level facade for the Intelligent Customer Support Chatbot.

    Encapsulates:
      * Knowledge base management (document upload & ingestion).
      * Conversational memory (per-session chat history).
      * Query answering via the RAG pipeline.

    Designed to be instantiated once per Streamlit session and reused
    across interactions (held in ``st.session_state``).
    """

    def __init__(
        self,
        persist_directory: str = "data/vector_db",
        llm_provider: Optional[str] = None,
        top_k: int = 4,
    ) -> None:
        """
        Args:
            persist_directory: Directory where the vector DB is persisted.
            llm_provider: ``"openai"`` or ``"anthropic"``; defaults to the
                ``LLM_PROVIDER`` environment variable.
            top_k: Number of chunks to retrieve per query.
        """
        self.document_loader = DocumentLoader()
        self.text_splitter = DocumentTextSplitter()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore(
            embedding_generator=self.embedding_generator,
            persist_directory=persist_directory,
        )
        self.retriever = Retriever(vector_store=self.vector_store, top_k=top_k)
        self.rag_pipeline = RAGPipeline(retriever=self.retriever, provider=llm_provider)

        # Conversational memory: list of {"role": "user"/"assistant", "content": str}
        self.chat_history: List[dict] = []

    # ------------------------------------------------------------------ #
    # Knowledge base management
    # ------------------------------------------------------------------ #
    def ingest_uploaded_file(self, file_bytes: bytes, filename: str) -> IngestionResult:
        """
        Validate, save, and ingest an uploaded file (from Streamlit's
        file uploader) into the knowledge base.

        Args:
            file_bytes: Raw bytes of the uploaded file.
            filename: Original filename, used to determine file type.

        Returns:
            ``IngestionResult`` describing success/failure and chunk count.
        """
        try:
            validate_file(filename, len(file_bytes))
        except FileValidationError as exc:
            logger.warning("File validation failed for '%s': %s", filename, exc)
            return IngestionResult(filename, success=False, message=str(exc))

        # Write to a temp file so the existing path-based loader can be reused.
        suffix = Path(filename).suffix
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_path = tmp_file.name
        except OSError as exc:
            return IngestionResult(
                filename, success=False, message=f"Could not save uploaded file: {exc}"
            )

        try:
            documents = self.document_loader.load(tmp_path)
            # Restore the original (user-facing) filename in metadata/source
            # since the temp file has a randomly generated name.
            for doc in documents:
                doc.source = filename

            if not documents:
                return IngestionResult(
                    filename, success=False, message="No extractable text found in file."
                )

            chunks = self.text_splitter.split_documents(documents)
            if not chunks:
                return IngestionResult(
                    filename, success=False, message="Document produced no usable text chunks."
                )

            added = self.vector_store.add_chunks(chunks)
            return IngestionResult(
                filename,
                success=True,
                chunks_added=added,
                message=f"Successfully indexed {added} chunk(s) from '{filename}'.",
            )

        except DocumentLoaderError as exc:
            logger.error("Document loading failed for '%s': %s", filename, exc)
            return IngestionResult(filename, success=False, message=str(exc))
        except VectorStoreError as exc:
            logger.error("Vector store ingestion failed for '%s': %s", filename, exc)
            return IngestionResult(
                filename, success=False, message=f"Failed to index document: {exc}"
            )
        except Exception as exc:  # Defensive catch-all for unexpected ingestion errors.
            logger.error("Unexpected ingestion error for '%s': %s", filename, exc)
            return IngestionResult(
                filename, success=False, message=f"Unexpected error: {exc}"
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def ingest_multiple_files(self, files: List[tuple]) -> List[IngestionResult]:
        """
        Ingest multiple uploaded files in sequence.

        Args:
            files: List of ``(file_bytes, filename)`` tuples.

        Returns:
            List of ``IngestionResult`` objects, one per file.
        """
        return [self.ingest_uploaded_file(file_bytes, filename) for file_bytes, filename in files]

    def load_sample_knowledge_base(self, directory: str = "data/company_docs") -> List[IngestionResult]:
        """
        Bulk-ingest all supported files from the sample knowledge base
        directory shipped with the project (useful for first-run demos).

        Args:
            directory: Path to the directory containing sample documents.

        Returns:
            List of ``IngestionResult`` objects, one per file processed.
        """
        results: List[IngestionResult] = []
        directory_path = Path(directory)
        if not directory_path.exists():
            logger.warning("Sample knowledge base directory '%s' not found.", directory)
            return results

        for file_path in sorted(directory_path.iterdir()):
            if file_path.suffix.lower() in DocumentLoader.SUPPORTED_EXTENSIONS:
                try:
                    file_bytes = file_path.read_bytes()
                    results.append(self.ingest_uploaded_file(file_bytes, file_path.name))
                except OSError as exc:
                    results.append(
                        IngestionResult(file_path.name, success=False, message=str(exc))
                    )
        return results

    def get_indexed_sources(self) -> List[str]:
        """Return the list of distinct source documents currently indexed."""
        return self.vector_store.list_sources()

    def get_knowledge_base_size(self) -> int:
        """Return the total number of chunks currently in the vector store."""
        return self.vector_store.count()

    def clear_knowledge_base(self) -> None:
        """Remove all documents from the knowledge base."""
        self.vector_store.clear()

    # ------------------------------------------------------------------ #
    # Chat / conversation
    # ------------------------------------------------------------------ #
    def ask(self, query: str) -> ChatResponse:
        """
        Process a user query: validate input, run the RAG pipeline with
        conversational memory, update history, and return the response.

        Args:
            query: Raw user input text.

        Returns:
            ``ChatResponse`` with the generated answer and source citations.
        """
        try:
            clean_query = validate_user_query(query)
        except ValueError as exc:
            return ChatResponse(answer=str(exc), error=str(exc))

        if self.vector_store.is_empty():
            return ChatResponse(
                answer=(
                    "The knowledge base is currently empty. Please upload some "
                    "company documents first so I can help answer your questions."
                ),
                used_context=False,
            )

        response = self.rag_pipeline.generate_response(clean_query, self.chat_history)

        # Update conversational memory for follow-up question support.
        self.chat_history.append({"role": "user", "content": clean_query})
        self.chat_history.append({"role": "assistant", "content": response.answer})

        return response

    def clear_chat_history(self) -> None:
        """Reset the conversational memory (does not affect the knowledge base)."""
        self.chat_history = []
        logger.info("Chat history cleared.")

    def get_chat_history(self) -> List[dict]:
        """Return the current conversational memory."""
        return self.chat_history
