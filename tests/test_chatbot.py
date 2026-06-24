"""
test_chatbot.py
===============
Unit and integration tests for the Intelligent Customer Support Chatbot.
Run with:  pytest tests/ -v
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils import (
    FileValidationError,
    clean_text,
    truncate_text,
    validate_file,
    validate_user_query,
)
from src.document_loader import DocumentLoader, DocumentLoaderError, LoadedDocument
from src.text_splitter import DocumentTextSplitter, TextChunk
from src.multilingual import LanguageDetector
from src.retriever import RetrievedChunk


# =========================================================================
# SECTION 1: utils.py tests
# =========================================================================
class TestValidateUserQuery:
    def test_valid_english_query(self):
        result = validate_user_query("What is your return policy?")
        assert result == "What is your return policy?"

    def test_valid_tamil_query(self):
        result = validate_user_query("உங்கள் திரும்ப கொள்கை என்ன?")
        assert "உங்கள்" in result

    def test_valid_hindi_query(self):
        result = validate_user_query("आपकी वापसी नीति क्या है?")
        assert "वापसी" in result

    def test_strips_leading_trailing_whitespace(self):
        result = validate_user_query("  hello world  ")
        assert result == "hello world"

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError, match="empty"):
            validate_user_query("")

    def test_raises_on_whitespace_only(self):
        with pytest.raises(ValueError, match="empty"):
            validate_user_query("   ")

    def test_raises_on_none(self):
        with pytest.raises(ValueError):
            validate_user_query(None)

    def test_raises_when_exceeds_max_length(self):
        long_query = "a" * 2001
        with pytest.raises(ValueError, match="too long"):
            validate_user_query(long_query)

    def test_accepts_exactly_max_length(self):
        query = "a" * 2000
        result = validate_user_query(query)
        assert len(result) == 2000


class TestCleanText:
    def test_removes_control_characters(self):
        dirty = "Hello\x00World\x01Test"
        assert "\x00" not in clean_text(dirty)
        assert "\x01" not in clean_text(dirty)

    def test_collapses_multiple_spaces(self):
        result = clean_text("Hello    World")
        assert result == "Hello World"

    def test_preserves_single_newlines(self):
        result = clean_text("Line 1\nLine 2")
        assert "Line 1" in result
        assert "Line 2" in result

    def test_empty_string_returns_empty(self):
        assert clean_text("") == ""

    def test_none_like_empty_returns_empty(self):
        assert clean_text(None) == ""


class TestValidateFile:
    def test_valid_pdf(self):
        validate_file("document.pdf", 1024)  # Should not raise

    def test_valid_txt(self):
        validate_file("notes.txt", 512)

    def test_valid_docx(self):
        validate_file("report.docx", 2048)

    def test_raises_on_unsupported_extension(self):
        with pytest.raises(FileValidationError, match="Unsupported"):
            validate_file("image.jpg", 1024)

    def test_raises_on_empty_file(self):
        with pytest.raises(FileValidationError, match="empty"):
            validate_file("empty.txt", 0)

    def test_raises_on_oversized_file(self):
        big_size = 30 * 1024 * 1024  # 30 MB — over 25 MB limit
        with pytest.raises(FileValidationError, match="exceeds"):
            validate_file("big.pdf", big_size)

    def test_raises_on_empty_filename(self):
        with pytest.raises(FileValidationError):
            validate_file("", 1024)


class TestTruncateText:
    def test_short_text_unchanged(self):
        text = "Short text"
        assert truncate_text(text, max_chars=100) == text

    def test_long_text_truncated(self):
        text = "word " * 100  # 500 chars
        result = truncate_text(text, max_chars=50)
        assert len(result) <= 54  # 50 + "..." at word boundary
        assert result.endswith("...")

    def test_empty_text(self):
        assert truncate_text("") == ""


# =========================================================================
# SECTION 2: document_loader.py tests
# =========================================================================
class TestDocumentLoader:
    def setup_method(self):
        self.loader = DocumentLoader()

    def test_load_txt_file(self, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Hello world. This is a test document.", encoding="utf-8")
        docs = self.loader.load(str(txt_file))
        assert len(docs) == 1
        assert "Hello world" in docs[0].content
        assert docs[0].source == "test.txt"
        assert docs[0].page is None

    def test_load_nonexistent_file_raises(self):
        with pytest.raises(DocumentLoaderError, match="not found"):
            self.loader.load("/nonexistent/path/file.txt")

    def test_load_empty_txt_raises(self, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("", encoding="utf-8")
        with pytest.raises(DocumentLoaderError):
            self.loader.load(str(empty_file))

    def test_load_directory_empty(self, tmp_path):
        docs = self.loader.load_directory(str(tmp_path))
        assert docs == []

    def test_load_directory_with_txt(self, tmp_path):
        (tmp_path / "a.txt").write_text("Content of file A.", encoding="utf-8")
        (tmp_path / "b.txt").write_text("Content of file B.", encoding="utf-8")
        docs = self.loader.load_directory(str(tmp_path))
        assert len(docs) == 2

    def test_load_directory_skips_unsupported(self, tmp_path):
        (tmp_path / "a.txt").write_text("Valid content.", encoding="utf-8")
        (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n")
        docs = self.loader.load_directory(str(tmp_path))
        assert len(docs) == 1  # Only the .txt is loaded

    def test_loaded_document_has_correct_metadata(self, tmp_path):
        txt_file = tmp_path / "meta_test.txt"
        txt_file.write_text("Testing metadata extraction.", encoding="utf-8")
        docs = self.loader.load(str(txt_file))
        assert docs[0].metadata.get("file_type") == "txt"


# =========================================================================
# SECTION 3: text_splitter.py tests
# =========================================================================
class TestDocumentTextSplitter:
    def setup_method(self):
        self.splitter = DocumentTextSplitter(chunk_size=200, chunk_overlap=20)

    def _make_doc(self, content, source="test.txt"):
        return LoadedDocument(content=content, source=source)

    def test_splits_long_text(self):
        long_text = "This is a sentence. " * 50  # ~1000 chars
        docs = [self._make_doc(long_text)]
        chunks = self.splitter.split_documents(docs)
        assert len(chunks) > 1

    def test_short_text_is_single_chunk(self):
        docs = [self._make_doc("Short text.")]
        chunks = self.splitter.split_documents(docs)
        assert len(chunks) == 1
        assert chunks[0].text == "Short text."

    def test_chunk_preserves_source(self):
        docs = [self._make_doc("Some content here.", source="myfile.pdf")]
        chunks = self.splitter.split_documents(docs)
        assert all(c.source == "myfile.pdf" for c in chunks)

    def test_empty_document_list(self):
        chunks = self.splitter.split_documents([])
        assert chunks == []

    def test_empty_content_skipped(self):
        docs = [self._make_doc("")]
        chunks = self.splitter.split_documents(docs)
        assert chunks == []

    def test_invalid_overlap_raises(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            DocumentTextSplitter(chunk_size=100, chunk_overlap=100)

    def test_chunk_metadata_dict_no_none_values(self):
        docs = [self._make_doc("Some text for metadata test.")]
        chunks = self.splitter.split_documents(docs)
        for chunk in chunks:
            meta = chunk.to_metadata_dict()
            for v in meta.values():
                assert v is not None, "Metadata must not contain None (ChromaDB requirement)"


# =========================================================================
# SECTION 4: multilingual.py tests
# =========================================================================
class TestLanguageDetector:
    def setup_method(self):
        self.detector = LanguageDetector()

    def test_detects_english(self):
        code = self.detector.detect_language("What is your return policy?")
        assert code == "en"

    def test_detects_hindi(self):
        code = self.detector.detect_language("आपकी वापसी नीति क्या है?")
        assert code == "hi"

    def test_short_text_returns_default(self):
        code = self.detector.detect_language("hi")
        # Very short text — should not crash; may return any code
        assert isinstance(code, str)
        assert len(code) >= 2

    def test_empty_text_returns_default(self):
        code = self.detector.detect_language("")
        assert code == "en"

    def test_get_language_name_english(self):
        assert self.detector.get_language_name("en") == "English"

    def test_get_language_name_tamil(self):
        assert self.detector.get_language_name("ta") == "Tamil"

    def test_get_language_name_hindi(self):
        assert self.detector.get_language_name("hi") == "Hindi"

    def test_get_language_name_unknown(self):
        result = self.detector.get_language_name("xx")
        assert result == "xx"  # Returns code itself for unknowns

    def test_build_language_instruction_english(self):
        instruction = self.detector.build_language_instruction("en")
        assert "English" in instruction

    def test_build_language_instruction_hindi(self):
        instruction = self.detector.build_language_instruction("hi")
        assert "Hindi" in instruction
        assert "MUST respond" in instruction

    def test_detect_with_name_returns_tuple(self):
        code, name = self.detector.detect_with_name("Hello, how can I help?")
        assert isinstance(code, str)
        assert isinstance(name, str)


# =========================================================================
# SECTION 5: retriever.py tests
# =========================================================================
class TestRetriever:
    def _make_chunk(self, text, source="doc.txt", score=0.8, page=None):
        return RetrievedChunk(text=text, source=source, page=page, score=score)

    def test_build_context_empty(self):
        from src.retriever import Retriever
        mock_vs = MagicMock()
        retriever = Retriever(vector_store=mock_vs)
        context = retriever.build_context([])
        assert context == ""

    def test_build_context_single_chunk(self):
        from src.retriever import Retriever
        mock_vs = MagicMock()
        retriever = Retriever(vector_store=mock_vs)
        chunk = self._make_chunk("Our return policy is 30 days.", source="policy.txt")
        context = retriever.build_context([chunk])
        assert "return policy" in context
        assert "policy.txt" in context

    def test_build_context_includes_page(self):
        from src.retriever import Retriever
        mock_vs = MagicMock()
        retriever = Retriever(vector_store=mock_vs)
        chunk = self._make_chunk("Text from page 3.", source="doc.pdf", page=3)
        context = retriever.build_context([chunk])
        assert "page 3" in context

    def test_retrieve_returns_empty_for_empty_query(self):
        from src.retriever import Retriever
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = []
        retriever = Retriever(vector_store=mock_vs)
        result = retriever.retrieve("")
        assert result == []

    def test_retrieve_filters_by_threshold(self):
        from src.retriever import Retriever
        mock_vs = MagicMock()
        mock_vs.similarity_search.return_value = [
            {"text": "High relevance", "source": "a.txt", "page": None, "chunk_id": 0, "score": 0.9},
            {"text": "Low relevance", "source": "b.txt", "page": None, "chunk_id": 0, "score": 0.05},
        ]
        retriever = Retriever(vector_store=mock_vs, score_threshold=0.15)
        chunks = retriever.retrieve("test query")
        assert len(chunks) == 1
        assert chunks[0].text == "High relevance"


# =========================================================================
# SECTION 6: vector_store.py tests (mocked ChromaDB)
# =========================================================================
class TestVectorStoreMocked:
    @patch("src.vector_store.chromadb.PersistentClient")
    def test_init_creates_collection(self, mock_chroma, tmp_path):
        from src.vector_store import VectorStore
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client
        mock_client.get_or_create_collection.return_value = MagicMock(count=lambda: 0)
        mock_embedder = MagicMock()
        vs = VectorStore(embedding_generator=mock_embedder, persist_directory=str(tmp_path))
        mock_client.get_or_create_collection.assert_called_once()

    @patch("src.vector_store.chromadb.PersistentClient")
    def test_is_empty_true_when_count_zero(self, mock_chroma, tmp_path):
        from src.vector_store import VectorStore
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_embedder = MagicMock()
        vs = VectorStore(embedding_generator=mock_embedder, persist_directory=str(tmp_path))
        assert vs.is_empty() is True


# =========================================================================
# SECTION 7: chatbot.py integration tests (mocked LLM)
# =========================================================================
class TestChatbotIntegration:
    @patch("src.rag_pipeline.RAGPipeline._init_client")
    @patch("src.vector_store.chromadb.PersistentClient")
    def test_ask_returns_response_when_kb_empty(self, mock_chroma, mock_llm_init, tmp_path):
        from src.chatbot import Chatbot
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_llm_init.return_value = MagicMock()

        import os
        os.environ.setdefault("OPENAI_API_KEY", "test-key")

        bot = Chatbot(persist_directory=str(tmp_path))
        response = bot.ask("Hello")
        assert "knowledge base" in response.answer.lower() or response.answer

    @patch("src.rag_pipeline.RAGPipeline._init_client")
    @patch("src.vector_store.chromadb.PersistentClient")
    def test_clear_chat_history(self, mock_chroma, mock_llm_init, tmp_path):
        from src.chatbot import Chatbot
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_llm_init.return_value = MagicMock()

        import os
        os.environ.setdefault("OPENAI_API_KEY", "test-key")

        bot = Chatbot(persist_directory=str(tmp_path))
        bot.chat_history = [{"role": "user", "content": "hi"}]
        bot.clear_chat_history()
        assert bot.get_chat_history() == []

    @patch("src.rag_pipeline.RAGPipeline._init_client")
    @patch("src.vector_store.chromadb.PersistentClient")
    def test_ingest_invalid_file_returns_failure(self, mock_chroma, mock_llm_init, tmp_path):
        from src.chatbot import Chatbot
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client
        mock_collection = MagicMock()
        mock_collection.count.return_value = 0
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_llm_init.return_value = MagicMock()

        import os
        os.environ.setdefault("OPENAI_API_KEY", "test-key")

        bot = Chatbot(persist_directory=str(tmp_path))
        result = bot.ingest_uploaded_file(b"content", "image.jpg")
        assert result.success is False
        assert "Unsupported" in result.message
