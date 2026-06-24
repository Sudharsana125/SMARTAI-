# Technical Documentation — Intelligent Customer Support Chatbot

**Version:** 1.0.0 | **Audience:** Developers & System Administrators

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Module Reference](#module-reference)
3. [RAG Pipeline Deep Dive](#rag-pipeline-deep-dive)
4. [Data Flow](#data-flow)
5. [API Configuration](#api-configuration)
6. [Vector Database Schema](#vector-database-schema)
7. [Performance Characteristics](#performance-characteristics)
8. [Extension Guide](#extension-guide)
9. [Testing Guide](#testing-guide)
10. [Deployment](#deployment)

---

## 1. System Architecture

The system follows a **layered RAG (Retrieval-Augmented Generation) architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI (app.py)                 │
│        Chat Window │ Sidebar │ Source Citation Panel     │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   CHATBOT FACADE (chatbot.py)            │
│         Session Memory │ Ingestion │ Query Routing       │
└──────┬─────────────────┬──────────────────┬─────────────┘
       │                 │                  │
┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────────────┐
│  DOCUMENT   │  │   VECTOR     │  │    RAG PIPELINE       │
│  PIPELINE   │  │   STORE      │  │    (rag_pipeline.py)  │
│             │  │(vector_store)│  │                       │
│ Loader      │  │              │  │ LangDetect → Prompt   │
│ Splitter    │  │ ChromaDB     │  │ Builder → LLM Call    │
│ Embedder    │  │ (persisted)  │  │ (OpenAI / Anthropic)  │
└─────────────┘  └──────────────┘  └───────────────────────┘
```

### Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit 1.38 | Chat UI, file upload, source panel |
| LLM Orchestration | LangChain 0.3 | Text splitting, prompt templates |
| LLM Provider | OpenAI GPT-4o / Anthropic Claude | Response generation |
| Embeddings | Sentence Transformers (multilingual MiniLM) | Vector encoding |
| Vector DB | ChromaDB 0.5 (persistent) | Semantic search |
| Document Parsing | pypdf, python-docx | PDF & DOCX extraction |
| Language Detection | langdetect | Multilingual routing |
| Config | python-dotenv | Secrets management |

---

## 2. Module Reference

### `src/utils.py`
Shared utilities used across all modules.

| Function | Description |
|----------|-------------|
| `get_logger(name)` | Returns a configured logger (avoids duplicate handlers on Streamlit reruns) |
| `validate_file(filename, size)` | Checks extension and 25 MB size limit |
| `validate_user_query(query)` | Strips control chars, enforces 2000-char limit |
| `clean_text(text)` | Normalizes whitespace from extracted document text |
| `get_env_var(name, default, required)` | Safe env var fetcher with optional enforcement |
| `truncate_text(text, max_chars)` | Word-boundary truncation for UI previews |

---

### `src/document_loader.py`
Extracts raw text from uploaded files.

| Class/Method | Description |
|-------------|-------------|
| `DocumentLoader.load(path)` | Dispatches to PDF/TXT/DOCX loader by extension |
| `DocumentLoader.load_directory(path)` | Bulk-loads all supported files in a directory |
| `LoadedDocument` | Dataclass holding `content`, `source`, `page`, `metadata` |

**PDF extraction** uses `pypdf.PdfReader`, page by page.
**DOCX extraction** uses `python-docx`, including table rows joined with ` | `.
**TXT extraction** reads with `utf-8` encoding and `errors='replace'`.

---

### `src/text_splitter.py`
Chunks documents for embedding.

| Setting | Default | Effect |
|---------|---------|--------|
| `chunk_size` | 1000 chars | Smaller = more precise retrieval |
| `chunk_overlap` | 150 chars | Preserves context at chunk boundaries |
| Separators | `\n\n`, `\n`, `. `, ` `, `""` | Respects paragraph/sentence boundaries |

Each `TextChunk` carries `.to_metadata_dict()` — a flat dict safe for ChromaDB storage (no nested objects, no `None` values).

---

### `src/embeddings.py`
Wraps Sentence Transformers for vector encoding.

**Model:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimensions:** 384
- **Languages:** 50+ (including Tamil, Hindi, English)
- **Normalization:** L2-normalized (cosine similarity via dot product)
- **Caching:** `@lru_cache` ensures the model loads once per process

---

### `src/vector_store.py`
Persistent ChromaDB wrapper.

| Method | Description |
|--------|-------------|
| `add_chunks(chunks)` | Embeds and inserts chunks; returns count added |
| `similarity_search(query, top_k)` | Returns top-k chunks with cosine similarity scores |
| `list_sources()` | Returns distinct source filenames in the DB |
| `clear()` | Deletes and recreates the collection |
| `is_empty()` | Fast check using `collection.count()` |

**Cosine distance → similarity:** `score = 1.0 - distance` (ChromaDB returns distance, not similarity)

---

### `src/retriever.py`
Sits on top of the vector store; applies score threshold and builds context strings.

| Setting | Default | Effect |
|---------|---------|--------|
| `top_k` | 4 | Max chunks retrieved per query |
| `score_threshold` | 0.15 | Filters out irrelevant results |

`build_context()` formats chunks as:
```
[Excerpt 1 | Source: faq.txt, page 2]
<chunk text>

[Excerpt 2 | Source: return_policy.txt]
<chunk text>
```

---

### `src/multilingual.py`
Language detection and LLM instruction generation.

- Uses `langdetect` with `DetectorFactory.seed = 0` for deterministic results
- Falls back to English for text < 2 characters or on detection failure
- `build_language_instruction()` returns a directive injected into the system prompt

---

### `src/rag_pipeline.py`
Core generation logic.

**System prompt structure:**
```
[Persona + Rules]
[Language instruction]

Context from company knowledge base:
---
[Excerpt 1 | Source: ...]
text...

[Excerpt 2 | Source: ...]
text...
---
```

**LLM providers:**
- `openai`: Uses `openai.OpenAI` client → `chat.completions.create()`
- `anthropic`: Uses `anthropic.Anthropic` client → `messages.create()`

Chat history is trimmed to the **last 8 turns** before each API call to balance memory vs. token cost.

---

### `src/chatbot.py`
High-level facade used by `app.py`.

| Method | Description |
|--------|-------------|
| `ingest_uploaded_file(bytes, name)` | Validates → saves temp file → loads → splits → embeds → stores |
| `load_sample_knowledge_base(dir)` | Bulk-loads all files from `data/company_docs/` |
| `ask(query)` | Validates → checks KB → runs RAG → updates memory → returns `ChatResponse` |
| `clear_chat_history()` | Resets conversational memory |
| `clear_knowledge_base()` | Wipes the vector store |

---

## 3. RAG Pipeline Deep Dive

### Step-by-Step Flow

```
User Query
    │
    ▼
[1] validate_user_query()          ← Strip control chars, check length
    │
    ▼
[2] LanguageDetector.detect()      ← ISO language code (e.g. "ta", "hi", "en")
    │
    ▼
[3] EmbeddingGenerator.embed_query() ← 384-dim vector
    │
    ▼
[4] ChromaDB.query(top_k=4)        ← Cosine similarity search
    │
    ▼
[5] Score threshold filter (≥ 0.15) ← Remove irrelevant chunks
    │
    ▼
[6] build_context()                ← Labelled excerpts string
    │
    ▼
[7] Build system prompt            ← Persona + context + language instruction
    │
    ▼
[8] LLM API call (OpenAI / Anthropic) ← With last 8 turns of history
    │
    ▼
[9] Return ChatResponse            ← answer + sources + language_code
```

### Hallucination Prevention
- The system prompt explicitly forbids the LLM from answering outside the context
- If retrieval returns 0 relevant chunks, the pipeline returns a canned "no information" response **without calling the LLM at all**
- Temperature is set to `0.3` (low) for factual, consistent answers

---

## 4. Data Flow

### Ingestion Flow (one-time per document)
```
Upload → validate_file() → temp file → DocumentLoader.load()
    → DocumentTextSplitter.split_documents()
    → EmbeddingGenerator.embed_texts()  [batch]
    → ChromaDB.add() with metadata
    → temp file deleted
```

### Query Flow (every chat message)
```
User types → validate_user_query() → detect_language()
    → embed_query() → ChromaDB.query() → filter by score
    → build_context() → build_system_prompt()
    → LLM API call (with chat_history[-8:])
    → ChatResponse → update chat_history → render in UI
```

---

## 5. API Configuration

All configuration lives in `.env`:

```bash
LLM_PROVIDER=openai          # or "anthropic"
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

To switch providers, change `LLM_PROVIDER` and restart — no code changes needed.

**Default models:**
- OpenAI: `gpt-4o`
- Anthropic: `claude-sonnet-4-5`

---

## 6. Vector Database Schema

**ChromaDB collection name:** `company_knowledge_base`
**Distance metric:** Cosine (`hnsw:space: cosine`)
**Persist path:** `data/vector_db/`

Each record contains:

| Field | Type | Example |
|-------|------|---------|
| `id` | UUID string | `"3f7a1b2c-..."` |
| `embedding` | `List[float]` (384-dim) | `[0.023, -0.14, ...]` |
| `document` | string | `"Shipping is FREE for orders above..."` |
| `metadata.source` | string | `"faq.txt"` |
| `metadata.page` | int (`-1` = no page) | `2` |
| `metadata.chunk_id` | int | `3` |
| `metadata.file_type` | string | `"pdf"` |

---

## 7. Performance Characteristics

| Operation | Typical Time | Notes |
|-----------|-------------|-------|
| First embedding model load | 10–30 s | Downloads ~120 MB model |
| Subsequent model loads | < 1 s | `lru_cache` keeps it in memory |
| Embedding 1 chunk | ~5 ms | CPU-only |
| Embedding 100 chunks | ~300 ms | Batch processing |
| ChromaDB similarity search | < 50 ms | In-process, local |
| LLM API call (GPT-4o) | 2–8 s | Network + generation |
| Full RAG response | 3–10 s | Dominated by LLM call |

---

## 8. Extension Guide

### Adding a New File Format
1. Add the extension to `SUPPORTED_EXTENSIONS` in `utils.py` and `document_loader.py`
2. Add a `_load_<format>()` method to `DocumentLoader`
3. Dispatch to it in `DocumentLoader.load()`

### Adding a New LLM Provider
1. Add a branch in `RAGPipeline._init_client()`
2. Add a `_call_<provider>()` method following the same signature
3. Add the provider name to `.env.example`

### Changing the Embedding Model
Update `DEFAULT_MODEL_NAME` in `embeddings.py`. Any Sentence Transformers model works. After changing, **clear the vector store** (`⚠️ Reset KB`) and re-ingest all documents — embeddings from different models are incompatible.

---

## 9. Testing Guide

Run the full test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --tb=short 2>&1 | head -60
```

**Test file:** `tests/test_chatbot.py`

Tests cover:
- `utils.py` — validation, text cleaning, env vars
- `text_splitter.py` — chunking logic and overlap
- `document_loader.py` — TXT/PDF/DOCX loading, error handling
- `multilingual.py` — language detection, instruction generation
- `retriever.py` — context building from mock chunks
- `chatbot.py` — empty KB response, input validation

All tests use mocks and do **not** require API keys, a running ChromaDB, or the embedding model.

---

## 10. Deployment

### Local Development
```bash
pip install -r requirements.txt
cp .env.example .env        # fill in API key
streamlit run app.py
```

### Production (Linux server / VM)
```bash
# 1. Create virtual environment
python3.11 -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure secrets
cp .env.example .env && nano .env

# 4. Run on a specific port
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# 5. (Optional) Run as background service with nohup
nohup streamlit run app.py > chatbot.log 2>&1 &
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t chatbot .
docker run -p 8501:8501 --env-file .env chatbot
```

### Streamlit Community Cloud (Free Hosting)
1. Push code to a public GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set main file to `app.py`
4. Add `OPENAI_API_KEY` in the Secrets section
5. Deploy — live URL provided instantly
