# rag/embeddings.py
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL
import numpy as np

_model = None  # loaded once, reused

def get_model():
    global _model
    if _model is None:
        print("📥 Loading embedding model (first time only)...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Embedding model loaded.")
    return _model


def embed_texts(texts: list) -> np.ndarray:
    """Embed a list of strings → numpy array shape (N, dim)"""
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.astype("float32")


def embed_query(query: str) -> np.ndarray:
    """Embed a single query string → shape (1, dim)"""
    return embed_texts([query])