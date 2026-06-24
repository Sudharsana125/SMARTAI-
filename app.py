"""
app.py
======
Streamlit frontend for the Intelligent Customer Support Chatbot.

Provides:
  * A sidebar for uploading and managing company knowledge-base documents.
  * A main chat window with conversational memory.
  * A source-citation panel showing which document excerpts grounded each
    answer.
  * A "Clear chat" button and knowledge-base management controls.

Run with:  streamlit run app.py
"""

import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Ensure the project root is on sys.path so `src.*` imports resolve
# correctly regardless of the working directory Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()  # Load OPENAI_API_KEY / ANTHROPIC_API_KEY / LLM_PROVIDER from .env

from src.chatbot import Chatbot  # noqa: E402
from src.rag_pipeline import LLMProviderError  # noqa: E402
from src.utils import get_logger  # noqa: E402

logger = get_logger(__name__)

st.set_page_config(
    page_title="Intelligent Customer Support Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------- #
# Session state initialization
# --------------------------------------------------------------------------- #
def initialize_chatbot() -> None:
    """
    Lazily initialize the ``Chatbot`` instance and store it in Streamlit's
    session state so it persists across reruns within the same browser
    session, without reloading the embedding model or reconnecting to
    ChromaDB on every interaction.
    """
    if "chatbot" in st.session_state:
        return

    try:
        with st.spinner("Initializing chatbot (loading embedding model)..."):
            st.session_state.chatbot = Chatbot()
        st.session_state.init_error = None
    except LLMProviderError as exc:
        st.session_state.chatbot = None
        st.session_state.init_error = str(exc)
    except Exception as exc:  # noqa: BLE001 - surface any startup failure to the UI
        logger.error("Chatbot initialization failed: %s", exc)
        st.session_state.chatbot = None
        st.session_state.init_error = (
            f"Failed to initialize the chatbot: {exc}"
        )


def initialize_ui_state() -> None:
    """Initialize Streamlit session-state keys used purely for UI rendering."""
    if "messages" not in st.session_state:
        st.session_state.messages = []  # list of {"role", "content", "sources"}
    if "last_upload_results" not in st.session_state:
        st.session_state.last_upload_results = []


# --------------------------------------------------------------------------- #
# Sidebar: knowledge base management
# --------------------------------------------------------------------------- #
def render_sidebar(chatbot: Chatbot) -> None:
    """
    Render the sidebar containing document upload controls, knowledge-base
    status, and management actions.

    Args:
        chatbot: The active ``Chatbot`` instance.
    """
    with st.sidebar:
        st.title("📚 Knowledge Base")
        st.caption("Upload company documents to power accurate support answers.")

        uploaded_files = st.file_uploader(
            "Upload PDF, TXT or DOCX files",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            help="Maximum file size: 25 MB per file.",
        )

        if uploaded_files and st.button("📥 Process Uploaded Files", use_container_width=True):
            process_uploads(chatbot, uploaded_files)

        st.divider()

        if st.button("🧪 Load Sample Knowledge Base", use_container_width=True):
            load_sample_kb(chatbot)

        st.divider()

        # Knowledge base status
        st.subheader("📊 Status")
        kb_size = chatbot.get_knowledge_base_size()
        sources = chatbot.get_indexed_sources()
        st.metric("Indexed Chunks", kb_size)

        if sources:
            with st.expander(f"📄 Indexed Documents ({len(sources)})", expanded=False):
                for source in sources:
                    st.markdown(f"- {source}")
        else:
            st.info("No documents indexed yet. Upload files or load the sample knowledge base.")

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                chatbot.clear_chat_history()
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("⚠️ Reset KB", use_container_width=True):
                chatbot.clear_knowledge_base()
                st.success("Knowledge base cleared.")
                st.rerun()

        st.divider()
        with st.expander("⚙️ Configuration", expanded=False):
            st.markdown(f"**LLM Provider:** `{chatbot.rag_pipeline.provider}`")
            st.markdown(f"**Model:** `{chatbot.rag_pipeline.model_name}`")
            st.markdown(f"**Top-K Retrieval:** `{chatbot.retriever.top_k}`")
            st.caption("Configurable via .env (LLM_PROVIDER, OPENAI_API_KEY, ANTHROPIC_API_KEY).")


def process_uploads(chatbot: Chatbot, uploaded_files) -> None:
    """
    Process and ingest files uploaded through Streamlit's file uploader.

    Args:
        chatbot: The active ``Chatbot`` instance.
        uploaded_files: List of Streamlit ``UploadedFile`` objects.
    """
    results = []
    progress_bar = st.progress(0, text="Processing documents...")

    for idx, uploaded_file in enumerate(uploaded_files):
        file_bytes = uploaded_file.getvalue()
        result = chatbot.ingest_uploaded_file(file_bytes, uploaded_file.name)
        results.append(result)
        progress_bar.progress(
            (idx + 1) / len(uploaded_files),
            text=f"Processed {uploaded_file.name}",
        )

    progress_bar.empty()
    st.session_state.last_upload_results = results

    for result in results:
        if result.success:
            st.success(result.message, icon="✅")
        else:
            st.error(f"{result.filename}: {result.message}", icon="⚠️")

    st.rerun()


def load_sample_kb(chatbot: Chatbot) -> None:
    """
    Load the bundled sample company knowledge base from
    ``data/company_docs`` into the vector store.

    Args:
        chatbot: The active ``Chatbot`` instance.
    """
    with st.spinner("Loading sample knowledge base..."):
        results = chatbot.load_sample_knowledge_base()

    if not results:
        st.warning(
            "No sample documents found in data/company_docs/. "
            "Add .pdf, .txt, or .docx files there first."
        )
        return

    success_count = sum(1 for r in results if r.success)
    st.success(f"Loaded {success_count}/{len(results)} sample document(s).")
    st.rerun()


# --------------------------------------------------------------------------- #
# Main chat window
# --------------------------------------------------------------------------- #
def render_chat_window(chatbot: Chatbot) -> None:
    """
    Render the main chat interface: message history, source citations, and
    the chat input box.

    Args:
        chatbot: The active ``Chatbot`` instance.
    """
    st.title("💬 Intelligent Customer Support Chatbot")
    st.caption(
        "Ask me anything about our products, policies, or services. "
        "I support English, Tamil, Hindi and more."
    )

    # Render existing conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])
            if message.get("language_name") and message["role"] == "assistant":
                st.caption(f"🌐 Detected language: {message['language_name']}")

    # Chat input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        handle_user_message(chatbot, user_input)


def handle_user_message(chatbot: Chatbot, user_input: str) -> None:
    """
    Handle a new user message: display it, run the RAG pipeline, display
    the assistant's response with sources, and persist both to UI state.

    Args:
        chatbot: The active ``Chatbot`` instance.
        user_input: The raw text the user submitted.
    """
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = chatbot.ask(user_input)
            except Exception as exc:  # noqa: BLE001 - surface unexpected errors gracefully
                logger.error("Unhandled error during chat: %s", exc)
                response = None
                st.error(
                    "Something went wrong while generating a response. "
                    "Please try again."
                )
                st.caption(f"Technical details: {exc}")

        if response is not None:
            st.markdown(response.answer)
            if response.sources:
                render_sources(response.sources)
            if response.language_name:
                st.caption(f"🌐 Detected language: {response.language_name}")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response.answer,
                    "sources": response.sources,
                    "language_name": response.language_name,
                }
            )


def render_sources(sources) -> None:
    """
    Render a "Sources" expander panel showing the document excerpts that
    grounded the chatbot's answer, including filename, page, and
    relevance score.

    Args:
        sources: List of ``RetrievedChunk`` objects.
    """
    if not sources:
        return
    with st.expander(f"📎 Sources ({len(sources)})", expanded=False):
        for idx, chunk in enumerate(sources, start=1):
            page_label = f" — Page {chunk.page}" if chunk.page else ""
            st.markdown(f"**{idx}. {chunk.source}{page_label}** _(relevance: {chunk.score:.2f})_")
            preview = chunk.text[:300] + ("..." if len(chunk.text) > 300 else "")
            st.markdown(f"> {preview}")
            if idx < len(sources):
                st.markdown("---")


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #
def main() -> None:
    """Application entry point: initializes state and renders the UI."""
    initialize_ui_state()
    initialize_chatbot()

    if st.session_state.get("init_error"):
        st.error(
            "⚠️ Chatbot failed to initialize:\n\n"
            f"{st.session_state.init_error}\n\n"
            "Please check your `.env` file and ensure `OPENAI_API_KEY` "
            "(or `ANTHROPIC_API_KEY`) is set correctly, then restart the app."
        )
        st.info(
            "Copy `.env.example` to `.env` and fill in your API key to get started."
        )
        st.stop()

    chatbot = st.session_state.chatbot
    render_sidebar(chatbot)
    render_chat_window(chatbot)


if __name__ == "__main__":
    main()
