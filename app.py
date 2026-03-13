import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from config.config import APP_NAME
from models.llm import get_llm_response
from models.embeddings import EmbeddingModel
from utils.rag_utils import (
    load_and_chunk_document,
    build_vector_store,
    retrieve_relevant_chunks,
    format_context,
)
from utils.search_utils import perform_web_search

st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar styling ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1b3a5c 100%);
        color: #e8edf3;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stRadio label {
        color: #e8edf3 !important;
    }

    /* ── Main area background ── */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        background-color: #f5f7fa;
    }

    /* ── Chat message bubbles ── */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        margin-bottom: 0.6rem;
        padding: 0.4rem 0.8rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }

    /* ── Quick-question buttons ── */
    div[data-testid="stButton"] > button {
        width: 100%;
        background: rgba(255, 255, 255, 0.08);
        color: #e8edf3;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        transition: background 0.2s ease;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(255,255,255,0.18);
        border-color: rgba(255,255,255,0.5);
    }

    /* ── Source tag badges ── */
    .source-tag {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
        padding: 2px 0;
    }

    /* ── Header strip ── */
    .app-header {
        background: linear-gradient(90deg, #0d3b66 0%, #1a5276 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.2rem;
        color: white;
    }
    .app-header h1 { margin: 0; font-size: 1.6rem; }
    .app-header p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.95rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

def init_session_state() -> None:
    defaults = {
        "messages": [],
        "vector_store": None,
        "embedding_model": None,
        "current_doc_name": None,
        "pending_query": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_embedding_model() -> EmbeddingModel:
    if st.session_state.embedding_model is None:
        with st.spinner("Loading embedding model (first run only)…"):
            st.session_state.embedding_model = EmbeddingModel()
    return st.session_state.embedding_model

def render_sidebar() -> tuple[str, bool]:
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center; padding: 0.5rem 0 1rem;'>
              <div style='font-size:3rem;'></div>
              <h1 style='font-size:1.4rem; margin:0;'>CitizenHelp</h1>
              <p style='opacity:0.75; font-size:0.85rem; margin:0;'>
                Your Government Scheme Guide
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            "Upload a scheme PDF or just ask me about any government scheme. "
            "I'll help you find what you're eligible for!"
        )

        st.markdown("---")

        st.markdown("#### Response Mode")
        mode_label = st.radio(
            label="Choose response style",
            options=["Quick Answer (Concise)", "Full Details (Detailed)"],
            index=0,
            label_visibility="collapsed",
        )
        mode = "concise" if "Concise" in mode_label else "detailed"

        st.markdown("---")

        st.markdown("#### Upload Scheme Document (optional)")
        uploaded_file = st.file_uploader(
            label="Upload PDF or TXT",
            type=["pdf", "txt"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            if uploaded_file.name != st.session_state.current_doc_name:
                with st.spinner("📖 Reading and indexing document…"):
                    try:
                        suffix = os.path.splitext(uploaded_file.name)[1]
                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=suffix
                        ) as tmp:
                            tmp.write(uploaded_file.getvalue())
                            tmp_path = tmp.name

                        embedding_model = get_embedding_model()
                        chunks = load_and_chunk_document(tmp_path)
                        vector_store = build_vector_store(chunks, embedding_model)

                        os.unlink(tmp_path)

                        if vector_store is not None:
                            st.session_state.vector_store = vector_store
                            st.session_state.current_doc_name = uploaded_file.name
                            st.success(
                                f"Document loaded! You can now ask questions about it."
                            )
                        else:
                            st.error("Failed to build vector store. Check console.")

                    except Exception as e:
                        st.error(f"Error processing document: {e}")
            else:
                st.success(
                    f"**{st.session_state.current_doc_name}** is loaded."
                )

        st.markdown("---")

        st.markdown("#### Live Web Search")
        web_search = st.checkbox(
            "Search Latest Updates (DuckDuckGo)",
            value=False,
            help="Fetches live results from the web to supplement document context.",
        )

        st.markdown("---")

        st.markdown("#### Quick Questions")
        quick_questions = {
            "Schemes for farmers": "What government schemes are available for farmers in India?",
            "Housing schemes": "Tell me about housing schemes like PMAY for low-income families.",
            "Schemes for women": "What schemes are available for women entrepreneurs and self-help groups?",
            "Student scholarships": "What scholarships and education schemes are available for students in India?",
        }

        for label, query in quick_questions.items():
            if st.button(label, key=f"btn_{label}"):
                st.session_state.pending_query = query

        st.markdown("---")

        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_query = None
            st.rerun()

    return mode, web_search

def render_chat(mode: str, web_search: bool) -> None:
    st.markdown(
        """
        <div class='app-header'>
          <h1>CitizenHelp — Government Scheme Assistant</h1>
          <p>
            Discover schemes you're eligible for · Learn how to apply ·
            Get the latest updates on central &amp; state government schemes
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            """
            <div style='text-align:center; padding: 3rem 1rem; color: #9ca3af;'>
              <div style='font-size:3rem; margin-bottom:0.5rem;'></div>
              <h3 style='color:#374151;'>Namaste! How can I help you today?</h3>
              <p>Ask me about PM Kisan, Ayushman Bharat, PMAY, Mudra Loan, or any other scheme.<br>
              You can also upload a scheme PDF from the sidebar for detailed Q&amp;A.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "sources" in msg:
                st.markdown(
                    f"<div class='source-tag'>{msg['sources']}</div>",
                    unsafe_allow_html=True,
                )
            if msg["role"] == "assistant" and msg.get("rag_chunks"):
                with st.expander("Document Sources Used"):
                    for i, chunk in enumerate(msg["rag_chunks"], start=1):
                        st.markdown(f"**Chunk {i}:**")
                        st.text(chunk[:600] + ("…" if len(chunk) > 600 else ""))
                        st.markdown("---")

    typed_query = st.chat_input(
        placeholder="Ask about any government scheme…",
        key="chat_input",
    )

    active_query: str | None = typed_query
    if st.session_state.pending_query and not typed_query:
        active_query = st.session_state.pending_query
        st.session_state.pending_query = None

    if active_query:
        _handle_user_query(active_query, mode, web_search)

def _handle_user_query(query: str, mode: str, web_search: bool) -> None:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    rag_chunks: list[str] = []
    context_parts: list[str] = []
    sources_used: list[str] = []

    with st.spinner("Searching for relevant schemes…"):

        if st.session_state.vector_store is not None:
            try:
                embedding_model = get_embedding_model()
                rag_chunks = retrieve_relevant_chunks(
                    query,
                    st.session_state.vector_store,
                    embedding_model,
                    top_k=4,
                )
                if rag_chunks:
                    formatted = format_context(rag_chunks)
                    context_parts.append(
                        "=== DOCUMENT CONTEXT ===\n"
                        + formatted
                        + "\n=== END DOCUMENT CONTEXT ==="
                    )
                    sources_used.append("RAG")
            except Exception as e:
                print(f"[app.py] RAG retrieval error: {e}")

        if web_search:
            try:
                search_results = perform_web_search(query)
                if search_results and "unavailable" not in search_results.lower():
                    context_parts.append(
                        "=== WEB SEARCH RESULTS ===\n"
                        + search_results
                        + "\n=== END WEB SEARCH RESULTS ==="
                    )
                    sources_used.append("Web Search")
            except Exception as e:
                print(f"[app.py] Web search error: {e}")

        llm_messages: list[dict] = []

        if context_parts:
            full_context = "\n\n".join(context_parts)
            llm_messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Here is additional context to help you answer:\n\n"
                        f"{full_context}\n\n"
                        f"Please use the above context when answering my question."
                    ),
                }
            )
            llm_messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Understood. I have reviewed the document context and/or web "
                        "search results and will use them to answer your question."
                    ),
                }
            )

        for msg in st.session_state.messages[:-1]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        llm_messages.append({"role": "user", "content": query})

        response = get_llm_response(llm_messages, mode=mode)

    mode_label = "Quick Answer" if mode == "concise" else "Full Details"
    source_tag_parts = ["Groq LLaMA", f"· {mode_label}"] + [f"· {s}" for s in sources_used]
    source_tag = " ".join(source_tag_parts)

    with st.chat_message("assistant"):
        st.markdown(response)
        st.markdown(
            f"<div class='source-tag'>{source_tag}</div>",
            unsafe_allow_html=True,
        )
        if rag_chunks:
            with st.expander("Document Sources Used"):
                for i, chunk in enumerate(rag_chunks, start=1):
                    st.markdown(f"**Chunk {i}:**")
                    st.text(chunk[:600] + ("…" if len(chunk) > 600 else ""))
                    st.markdown("---")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "sources": source_tag,
            "rag_chunks": rag_chunks,
        }
    )

def main() -> None:
    init_session_state()
    mode, web_search = render_sidebar()
    render_chat(mode, web_search)

if __name__ == "__main__":
    main()
