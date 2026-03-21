from __future__ import annotations

class EmbeddingModel:

    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            print("[embeddings.py] Embedding model loaded: all-MiniLM-L6-v2")

        except ImportError:
            print(
                "[embeddings.py] sentence-transformers is not installed. "
                "Run: pip install sentence-transformers"
            )
            self.model = None

        except Exception as e:
            print(f"[embeddings.py] Failed to load embedding model: {e}")
            self.model = None

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        try:
            if self.model is None:
                raise RuntimeError("Embedding model is not loaded.")

            embeddings = self.model.encode(texts, show_progress_bar=False)
            return embeddings.tolist()

        except Exception as e:
            print(f"[embeddings.py] embed_texts failed: {e}")
            return []

    def embed_query(self, query: str) -> list[float]:
        try:
            if self.model is None:
                raise RuntimeError("Embedding model is not loaded.")

            embedding = self.model.encode([query], show_progress_bar=False)
            return embedding[0].tolist()

        except Exception as e:
            print(f"[embeddings.py] embed_query failed: {e}")
            return []
