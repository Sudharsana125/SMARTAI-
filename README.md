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

## ⚡ Quick Setup (Windows — Your Environment)

### Prerequisites
- Python 3.11 or higher
- An OpenAI API key from [platform.openai.com](https://platform.openai.com) (or Anthropic key)


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
