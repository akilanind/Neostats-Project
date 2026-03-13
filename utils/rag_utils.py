import os
import uuid

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
) -> list[dict]:
    try:
        extension = os.path.splitext(file_path)[1].lower()
        full_text: str = ""

        if extension == ".pdf":
            if PdfReader is None:
                raise ImportError("pypdf is not installed. Run: pip install pypdf")
            reader = PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"

        elif extension == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()

        else:
            raise ValueError(f"Unsupported file type: '{extension}'. Use PDF or TXT.")

        if not full_text.strip():
            print(f"[rag_utils.py] Document appears to be empty: {file_path}")
            return []

        chunks: list[dict] = []
        source_name = os.path.basename(file_path)
        step = chunk_size - chunk_overlap
        start = 0
        chunk_id = 0

        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "chunk_id": chunk_id,
                        "source": source_name,
                    }
                )
                chunk_id += 1

            start += step

        print(f"[rag_utils.py] Loaded '{source_name}' → {len(chunks)} chunks.")
        return chunks

    except Exception as e:
        print(f"[rag_utils.py] load_and_chunk_document failed: {e}")
        return []

def build_vector_store(chunks: list[dict], embedding_model) -> object | None:
    try:
        if chromadb is None:
            raise ImportError("chromadb is not installed. Run: pip install chromadb")

        if not chunks:
            print("[rag_utils.py] No chunks to embed — skipping vector store build.")
            return None

        client = chromadb.Client()

        collection_name = f"scheme_docs_{uuid.uuid4().hex[:8]}"
        collection = client.create_collection(name=collection_name)

        texts = [chunk["text"] for chunk in chunks]
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in chunks]
        metadatas = [{"source": chunk["source"], "chunk_id": chunk["chunk_id"]} for chunk in chunks]

        embeddings = embedding_model.embed_texts(texts)

        if not embeddings:
            raise RuntimeError("Embedding model returned no embeddings.")

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"[rag_utils.py] Vector store built with {len(chunks)} chunks.")
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
    try:
        if collection is None:
            print("[rag_utils.py] Collection is None — no retrieval possible.")
            return []

        query_embedding = embedding_model.embed_query(query)

        if not query_embedding:
            raise RuntimeError("Query embedding failed.")

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count()),
        )

        return results["documents"][0] if results["documents"] else []

    except Exception as e:
        print(f"[rag_utils.py] retrieve_relevant_chunks failed: {e}")
        return []

def format_context(chunks: list[str]) -> str:
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
