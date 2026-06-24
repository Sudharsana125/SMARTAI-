# 🤖 Intelligent Customer Support Chatbot

A production-ready **Generative AI** customer support chatbot powered by **RAG (Retrieval-Augmented Generation)**, **OpenAI GPT-4o** (or Anthropic Claude), **ChromaDB**, and **Streamlit**.

> Built as an AI & Data Science mini project — suitable for live demonstration.

---

## ✨ Features

| Feature | Details |
|---------|---------|
| 📄 **Knowledge Base** | Upload PDF, DOCX, TXT files as company documents |
| 🔍 **RAG Pipeline** | Answers grounded in your documents — no hallucination |
| 🌐 **Multilingual** | Auto-detects & replies in English, Tamil, Hindi + 50 more languages |
| 💬 **Chat Memory** | Remembers conversation context for follow-up questions |
| 📎 **Source Citations** | Every answer shows which document it came from |
| 🔄 **Dual LLM Support** | Switch between OpenAI GPT-4o and Anthropic Claude via `.env` |
| 🎨 **Streamlit UI** | Professional chat interface with sidebar document management |

---

## 📁 Project Structure

```
intelligent_customer_support_chatbot/
│
├── app.py                          ← Streamlit frontend (run this)
├── requirements.txt                ← All Python dependencies
├── .env.example                    ← Copy to .env and fill in API key
├── README.md
│
├── data/
│   ├── company_docs/               ← Place your knowledge-base files here
│   │   ├── faq.txt
│   │   ├── return_refund_policy.txt
│   │   └── product_catalog.txt
│   └── vector_db/                  ← ChromaDB auto-creates files here
│
├── src/
│   ├── __init__.py
│   ├── utils.py                    ← Shared helpers, logging, validation
│   ├── document_loader.py          ← PDF / DOCX / TXT text extraction
│   ├── text_splitter.py            ← Chunk documents for embedding
│   ├── embeddings.py               ← SentenceTransformers wrapper
│   ├── vector_store.py             ← ChromaDB wrapper (store + search)
│   ├── retriever.py                ← Top-K retrieval + context builder
│   ├── multilingual.py             ← Language detection + LLM instruction
│   ├── rag_pipeline.py             ← Core RAG + LLM generation logic
│   └── chatbot.py                  ← High-level facade (used by app.py)
│
├── docs/
│   ├── architecture.md             ← Mermaid diagrams (data flow, RAG, use cases)
│   ├── user_manual.md              ← End-user guide with examples
│   └── technical_documentation.md  ← Developer reference + deployment
│
└── tests/
    └── test_chatbot.py             ← Pytest unit tests (no API key needed)
```

---

## ⚡ Quick Setup (Windows — Your Environment)

### Prerequisites
- Python 3.11 or higher
- An OpenAI API key from [platform.openai.com](https://platform.openai.com) (or Anthropic key)

### Step-by-Step

**Step 1 — Open terminal in your project folder**
```
C:\Users\sudha\chatbot>
```

**Step 2 — Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate
```
You should see `(venv)` in your prompt.

**Step 3 — Install all dependencies**
```bash
pip install -r requirements.txt
```
> ⏳ First install takes 3–5 minutes (downloads embedding model ~120 MB)

**Step 4 — Create your `.env` file**
```bash
copy .env.example .env
```
Then open `.env` in any text editor and fill in:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step 5 — Run the chatbot**
```bash
streamlit run app.py
```
Browser opens automatically at **http://localhost:8501** 🎉

---

## 🚀 First Run Demo

1. In the sidebar, click **"🧪 Load Sample Knowledge Base"**
2. Wait for the green success messages
3. Type in the chat box: `What is your return policy?`
4. See the grounded answer with source citations!

**Try multilingual:**
- Hindi: `मुझे रिफंड कब मिलेगा?`
- Tamil: `டெலிவரி எவ்வளவு நாள் ஆகும்?`

---

## 📤 Adding Your Own Documents

1. Place your `.pdf`, `.docx`, or `.txt` files in `data/company_docs/`
   — OR —
   Upload them directly through the sidebar's file uploader
2. Click **"📥 Process Uploaded Files"**
3. Start asking questions about your content

---

## 🔧 Configuration Options

Edit your `.env` file:

```bash
# Choose provider: "openai" or "anthropic"
LLM_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic (alternative)
ANTHROPIC_API_KEY=sk-ant-...
```

To use **Anthropic Claude** instead of OpenAI:
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

All tests use mocks — **no API key required** to run tests.

---

## 📊 Architecture Summary

```
User Query
    ↓
Language Detection (langdetect)
    ↓
Query Embedding (SentenceTransformers 384-dim)
    ↓
Semantic Search (ChromaDB cosine similarity)
    ↓
Top-K Chunks Retrieved + Score Filtered
    ↓
Context + Prompt Built
    ↓
LLM Call (GPT-4o / Claude) with Chat History
    ↓
Grounded Answer + Source Citations
```

See [`docs/architecture.md`](docs/architecture.md) for full Mermaid diagrams.

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Manual](docs/user_manual.md) | How to use the chatbot (with example conversations) |
| [Architecture](docs/architecture.md) | System diagrams — data flow, RAG, use cases |
| [Technical Docs](docs/technical_documentation.md) | Module reference, extension guide, deployment |

---

## 🌐 Deployment Options

### Streamlit Community Cloud (Free)
1. Push to a public GitHub repo
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set main file as `app.py`
4. Add `OPENAI_API_KEY` in Secrets
5. Deploy!

### Docker
```bash
docker build -t chatbot .
docker run -p 8501:8501 --env-file .env chatbot
```

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Streamlit** — UI
- **LangChain** — Text splitting
- **OpenAI / Anthropic** — LLM generation
- **ChromaDB** — Vector database (local, persistent)
- **Sentence Transformers** — Multilingual embeddings
- **pypdf + python-docx** — Document parsing
- **langdetect** — Language detection

---

## 👨‍💻 Author

**Sudharsana** — AI & Data Science Project
*Intelligent Customer Support Chatbot using RAG, LangChain, ChromaDB & Streamlit*
