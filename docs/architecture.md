# Architecture Documentation — Intelligent Customer Support Chatbot

---

## 1. System Overview

This chatbot uses **Retrieval-Augmented Generation (RAG)** to answer customer queries
using only information from uploaded company documents — eliminating hallucination
and ensuring every answer is traceable to a source.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TB
    subgraph UI["Streamlit Frontend (app.py)"]
        A[Chat Window]
        B[Sidebar - Document Upload]
        C[Source Citation Panel]
    end

    subgraph FACADE["Chatbot Facade (chatbot.py)"]
        D[Session Memory]
        E[Query Router]
        F[Ingestion Manager]
    end

    subgraph INGESTION["Document Pipeline"]
        G[DocumentLoader - pdf/docx/txt]
        H[TextSplitter - 1000 chars/150 overlap]
        I[EmbeddingGenerator - MiniLM Multilingual]
    end

    subgraph RETRIEVAL["Retrieval Layer"]
        J[VectorStore - ChromaDB Persistent]
        K[Retriever - Top-K + Score Filter]
    end

    subgraph GENERATION["Generation Layer"]
        L[LanguageDetector - langdetect]
        M[RAG Pipeline - Prompt Builder]
        N[LLM Provider - OpenAI GPT-4o or Anthropic Claude]
    end

    B --> F --> G --> H --> I --> J
    A --> E --> D
    E --> K --> J
    K --> M
    L --> M
    M --> N --> A
    N --> C
```

---

## 3. Data Flow Diagram

```mermaid
flowchart TD
    START([User uploads document]) --> V1[Validate file type and size]
    V1 -->|Invalid| ERR1[Show error message]
    V1 -->|Valid| LOAD[Extract text via DocumentLoader]
    LOAD --> SPLIT[Split into chunks - 1000 chars, 150 overlap]
    SPLIT --> EMBED[Generate embeddings - SentenceTransformers 384-dim]
    EMBED --> STORE[Store in ChromaDB with metadata]
    STORE --> READY([Knowledge Base Ready])

    READY --> Q([User types a question])
    Q --> VQUERY[Validate query - clean and length check]
    VQUERY --> LANG[Detect language via langdetect]
    LANG --> QEMBED[Embed query via SentenceTransformers]
    QEMBED --> SEARCH[Cosine similarity search - ChromaDB top-4]
    SEARCH --> FILTER{Score >= 0.15?}
    FILTER -->|No relevant chunks| FALLBACK[Return polite no-info response]
    FILTER -->|Chunks found| CTX[Build context string with source labels]
    CTX --> PROMPT[Build system prompt - Persona + Context + Language]
    PROMPT --> LLM[Call LLM API - GPT-4o or Claude]
    LLM --> RESP[Return answer + sources + language]
    RESP --> MEM[Update chat history - last 8 turns kept]
    MEM --> RENDER([Display in chat UI with Sources panel])
```

---

## 4. RAG Architecture Diagram

```mermaid
flowchart LR
    subgraph OFFLINE["Offline - Indexing Time"]
        D1[Company Documents] --> L1[Load Text]
        L1 --> S1[Split Chunks]
        S1 --> E1[Embed 384-dim]
        E1 --> DB[(ChromaDB Vector Store)]
    end

    subgraph ONLINE["Online - Query Time"]
        Q[User Query] --> E2[Embed Query]
        E2 --> SEARCH[Semantic Search]
        DB --> SEARCH
        SEARCH --> TOP[Top-K Chunks]
        TOP --> AUGMENT[Augment Prompt]
        Q --> AUGMENT
        AUGMENT --> LLM[GPT-4o or Claude]
        LLM --> ANS[Grounded Answer + Sources]
    end
```

---

## 5. Use Case Diagram

```mermaid
graph LR
    CUSTOMER(("Customer"))
    ADMIN(("Admin / Staff"))

    subgraph SYSTEM["Intelligent Customer Support Chatbot"]
        UC1[Ask question in any language]
        UC2[Receive grounded answer with sources]
        UC3[Ask follow-up questions]
        UC4[Clear chat history]

        UC5[Upload company documents]
        UC6[Load sample knowledge base]
        UC7[View indexed documents]
        UC8[Reset knowledge base]
        UC9[Configure LLM provider and model]
    end

    CUSTOMER --> UC1
    UC1 --> UC2
    UC2 --> UC3
    CUSTOMER --> UC4

    ADMIN --> UC5
    ADMIN --> UC6
    ADMIN --> UC7
    ADMIN --> UC8
    ADMIN --> UC9
```

---

## 6. Component Dependency Diagram

```mermaid
graph TD
    APP[app.py - Streamlit UI]
    CB[chatbot.py - Facade]
    RAG[rag_pipeline.py]
    RET[retriever.py]
    VS[vector_store.py]
    EMB[embeddings.py]
    DL[document_loader.py]
    TS[text_splitter.py]
    ML[multilingual.py]
    UT[utils.py]

    APP --> CB
    CB --> RAG
    CB --> RET
    CB --> VS
    CB --> EMB
    CB --> DL
    CB --> TS
    RAG --> RET
    RAG --> ML
    RET --> VS
    VS --> EMB
    DL --> UT
    TS --> DL
    EMB --> UT
    RAG --> UT
    CB --> UT
```

---

## 7. Deployment Architecture

```mermaid
graph TB
    subgraph LOCAL["Local or Server"]
        UI[Streamlit - localhost:8501]
        APP2[Python Application]
        DB2[(ChromaDB - data/vector_db/)]
        MODEL[SentenceTransformer Model Cache]
    end

    subgraph CLOUD["External APIs"]
        OPENAI[OpenAI GPT-4o API]
        ANTHROPIC[Anthropic Claude API]
    end

    BROWSER[Browser] --> UI
    UI --> APP2
    APP2 --> DB2
    APP2 --> MODEL
    APP2 -->|HTTPS| OPENAI
    APP2 -->|HTTPS| ANTHROPIC
```

---

## 8. Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Embedding model | paraphrase-multilingual-MiniLM-L12-v2 | Free, offline, 50+ languages, fast on CPU |
| Vector DB | ChromaDB (persistent) | Zero-config, embedded, survives restarts |
| Chunk size | 1000 chars / 150 overlap | Balances retrieval precision vs. context richness |
| Score threshold | 0.15 cosine similarity | Filters noise without being too restrictive |
| History limit | Last 8 turns | Supports follow-ups without excessive token usage |
| Temperature | 0.3 | Factual consistency over creativity |
| LLM provider | Configurable via .env | Swap OpenAI ↔ Anthropic with one env change |
