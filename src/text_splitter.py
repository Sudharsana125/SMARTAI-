"""
text_splitter.py
=================
Splits loaded documents into overlapping text chunks suitable for embedding
and retrieval. Wraps LangChain's ``RecursiveCharacterTextSplitter`` while
preserving source/page metadata for each resulting chunk.
"""

from dataclasses import dataclass, field
from typing import List

from src.document_loader import LoadedDocument
from src.utils import get_logger

logger = get_logger(__name__)

# Default chunking configuration. These values balance retrieval precision
# (smaller chunks = more precise matches) against context completeness
# (larger chunks = more coherent context for the LLM).
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150


@dataclass
class TextChunk:
    """
    A single chunk of text ready for embedding.

    Attributes:
        text: The chunk's text content.
        source: Originating document filename.
        page: Page number, if applicable (PDFs only).
        chunk_id: Index of this chunk within its source document.
        metadata: Additional metadata carried over from the source document.
    """

    text: str
    source: str
    page: int = None
    chunk_id: int = 0
    metadata: dict = field(default_factory=dict)

    def to_metadata_dict(self) -> dict:
        """
        Build a ChromaDB-compatible metadata dictionary (flat, primitive
        values only — ChromaDB does not accept nested dicts or ``None``).

        Returns:
            Flat dictionary of metadata suitable for vector store storage.
        """
        meta = {
            "source": self.source,
            "chunk_id": self.chunk_id,
            "page": self.page if self.page is not None else -1,
        }
        for key, value in self.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                meta[key] = value
        return meta


class DocumentTextSplitter:
    """
    Splits ``LoadedDocument`` instances into overlapping ``TextChunk``
    objects using a recursive character-based strategy that respects
    natural text boundaries (paragraphs, sentences, words).
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        """
        Args:
            chunk_size: Target maximum number of characters per chunk.
            chunk_overlap: Number of overlapping characters between
                consecutive chunks, used to preserve context continuity.
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._separators = ["\n\n", "\n", ". ", " ", ""]

    def _split_text(self, text: str) -> List[str]:
        """
        Recursively split text using a priority list of separators,
        producing chunks of at most ``chunk_size`` characters with
        ``chunk_overlap`` characters of overlap between adjacent chunks.
        This re-implements LangChain's RecursiveCharacterTextSplitter
        logic without the external dependency.
        """
        # Find the first separator that actually appears in the text.
        separator = ""
        for sep in self._separators:
            if sep == "" or sep in text:
                separator = sep
                break

        splits = text.split(separator) if separator else list(text)

        chunks: List[str] = []
        current: List[str] = []
        current_len = 0

        for split in splits:
            split_len = len(split)
            # If a single split already exceeds chunk_size, recurse.
            if split_len > self.chunk_size:
                if current:
                    merged = separator.join(current).strip()
                    if merged:
                        chunks.append(merged)
                    current, current_len = [], 0
                # Recurse with the next separator down the list
                next_sep_idx = self._separators.index(separator) + 1
                sub_splitter_seps = self._separators[next_sep_idx:] if next_sep_idx < len(self._separators) else [""]
                sub_text = split
                for sub_sep in sub_splitter_seps:
                    if sub_sep in sub_text or sub_sep == "":
                        sub_splits = sub_text.split(sub_sep) if sub_sep else list(sub_text)
                        for s in sub_splits:
                            if len(s) <= self.chunk_size:
                                chunks.extend(self._merge_splits([s], separator))
                            else:
                                chunks.append(s[:self.chunk_size])
                        break
                continue

            new_len = current_len + len(separator) + split_len if current else split_len
            if new_len > self.chunk_size and current:
                merged = separator.join(current).strip()
                if merged:
                    chunks.append(merged)
                # Keep overlap: retain tail of current that fits in overlap window
                overlap_text = separator.join(current)
                if len(overlap_text) > self.chunk_overlap:
                    overlap_text = overlap_text[-self.chunk_overlap:]
                current = [overlap_text] if overlap_text.strip() else []
                current_len = len(overlap_text)

            current.append(split)
            current_len = len(separator.join(current))

        if current:
            merged = separator.join(current).strip()
            if merged:
                chunks.append(merged)

        return [c for c in chunks if c.strip()]

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """Helper to merge small splits back up to chunk_size."""
        chunks: List[str] = []
        current: List[str] = []
        current_len = 0
        for s in splits:
            if current_len + len(s) > self.chunk_size and current:
                chunks.append(separator.join(current).strip())
                current, current_len = [], 0
            current.append(s)
            current_len += len(s)
        if current:
            chunks.append(separator.join(current).strip())
        return chunks

    def split_documents(self, documents: List[LoadedDocument]) -> List[TextChunk]:
        """
        Split a list of loaded documents into text chunks.

        Args:
            documents: Documents produced by ``DocumentLoader``.

        Returns:
            List of ``TextChunk`` objects across all input documents.
        """
        all_chunks: List[TextChunk] = []

        for doc in documents:
            if not doc.content or not doc.content.strip():
                continue

            raw_chunks = self._split_text(doc.content)
            for idx, chunk_text in enumerate(raw_chunks):
                if not chunk_text.strip():
                    continue
                all_chunks.append(
                    TextChunk(
                        text=chunk_text.strip(),
                        source=doc.source,
                        page=doc.page,
                        chunk_id=idx,
                        metadata=doc.metadata,
                    )
                )

        logger.info(
            "Split %d document(s) into %d chunk(s) (size=%d, overlap=%d).",
            len(documents),
            len(all_chunks),
            self.chunk_size,
            self.chunk_overlap,
        )
        return all_chunks
