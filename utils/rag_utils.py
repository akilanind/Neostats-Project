from __future__ import annotations
import os
import uuid
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Optional, Union

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

def load_and_chunk_document(
    file_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[dict[str, Any]]:
    """
    Loads text from a PDF or TXT file and splits it into smaller chunks.
    """
    try:
        if not os.path.exists(file_path):
            print(f"[rag_utils.py] Error: File not found at {file_path}")
            return []

        extension = os.path.splitext(file_path)[1].lower()
        full_text: str = ""

        if extension == ".pdf":
            if PdfReader is None:
                raise ImportError("The 'pypdf' package is missing. Run: pip install pypdf")
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if isinstance(page_text, str):
                    full_text += page_text + "\n"

        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()

        else:
            raise ValueError(f"Unsupported file type: '{extension}'. Use PDF or TXT.")

        if not full_text.strip():
            print(f"[rag_utils.py] Warning: Document appears to be empty: {file_path}")
            return []

        chunks: list[dict[str, Any]] = []
        source_name = os.path.basename(file_path)
        step = chunk_size - chunk_overlap
        start = 0
        chunk_id = 0

        # Use a fresh variable name and explicit cast to help static analysis
        content_to_chunk: str = str(full_text)
        current_idx: int = int(start)

        while current_idx < len(content_to_chunk):
            end_idx = current_idx + chunk_size
            chunk_text = content_to_chunk[current_idx:end_idx].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "chunk_id": chunk_id,
                        "source": source_name,
                    }
                )
                chunk_id += 1

            current_idx += int(step)

        print(f"[rag_utils.py] Successfully loaded '{source_name}' -> {len(chunks)} chunks.")
        return chunks

    except Exception as e:
        print(f"[rag_utils.py] load_and_chunk_document failed for {file_path}: {e}")
        return []

def build_vector_store(chunks: list[dict], embedding_model) -> object | None:
    """
    Creates an in-memory ChromaDB collection from document chunks.
    """
    try:
        if chromadb is None:
            raise ImportError("The 'chromadb' package is missing. Run: pip install chromadb")

        if not chunks:
            print("[rag_utils.py] No chunks provided for vector store.")
            return None

        # Using ephemeral (in-memory) client for simple integration
        client = chromadb.Client()

        collection_name = f"scheme_docs_{uuid.uuid4().hex[:8]}"
        collection = client.create_collection(name=collection_name)

        texts = [chunk["text"] for chunk in chunks]
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in chunks]
        metadatas = [{"source": chunk["source"], "chunk_id": chunk["chunk_id"]} for chunk in chunks]

        # Get embeddings from the provided embedding model
        embeddings = embedding_model.embed_texts(texts)

        if not embeddings:
            raise RuntimeError("Embedding model failed to generate embeddings.")

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"[rag_utils.py] Vector store '{collection_name}' built with {len(chunks)} chunks.")
        return collection

    except Exception as e:
        print(f"[rag_utils.py] build_vector_store failed: {e}")
        return None

def retrieve_relevant_chunks(
    query: str,
    collection,
    embedding_model,
    top_k: int = 4,
) -> list[str]:
    """
    Searches the vector store for chunks relevant to the user's query.
    """
    try:
        if collection is None:
            return []

        query_embedding = embedding_model.embed_query(query)

        if not query_embedding:
            raise RuntimeError("Embed query failed.")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
        )

        return results["documents"][0] if results["documents"] else []

    except Exception as e:
        print(f"[rag_utils.py] retrieve_relevant_chunks failed: {e}")
        return []

def format_context(chunks: list[str]) -> str:
    """
    Formats retrieved chunks into a clean, labeled string for the LLM prompt.
    """
    try:
        if not chunks:
            return ""

        separator = "\n" + "─" * 60 + "\n"
        labelled = [
            f"[Document Chunk {i + 1}]\n{chunk.strip()}"
            for i, chunk in enumerate(chunks)
        ]
        return separator.join(labelled)

    except Exception as e:
        print(f"[rag_utils.py] format_context failed: {e}")
        return ""
