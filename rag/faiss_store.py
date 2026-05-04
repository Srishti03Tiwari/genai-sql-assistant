# rag/faiss_store.py
import os
import pickle
import faiss
import numpy as np
from config import FAISS_INDEX_PATH, FAISS_CHUNKS_PATH, TOP_K_CHUNKS
from rag.embeddings import embed_texts, embed_query


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> list:
    """Split text into overlapping word-level chunks."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def build_index(docs_path: str = "./data/schema_docs.txt"):
    """
    Read docs → chunk → embed → build FAISS index → save to disk.
    Run this once, or whenever schema_docs.txt changes.
    """
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

    # Read the docs file
    with open(docs_path, "r") as f:
        raw_text = f.read()

    # Split into chunks
    chunks = chunk_text(raw_text)
    print(f"📄 Created {len(chunks)} chunks from docs.")

    # Generate embeddings
    print("🔄 Generating embeddings...")
    embeddings = embed_texts(chunks)
    dim = embeddings.shape[1]
    print(f"✅ Embeddings shape: {embeddings.shape}")

    # Build FAISS index
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    print(f"✅ FAISS index built with {index.ntotal} vectors.")

    # Save index and chunks to disk
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(FAISS_CHUNKS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"💾 Saved index → {FAISS_INDEX_PATH}")
    print(f"💾 Saved chunks → {FAISS_CHUNKS_PATH}")
    return index, chunks


def load_index():
    """Load FAISS index and chunks from disk."""
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"FAISS index not found. Run build_index() first."
        )
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(FAISS_CHUNKS_PATH, "rb") as f:
        chunks = pickle.load(f)
    return index, chunks


def search(query: str, top_k: int = TOP_K_CHUNKS) -> list:
    """Search FAISS index → return top_k most relevant chunks."""
    index, chunks = load_index()
    query_vec = embed_query(query)
    distances, indices = index.search(query_vec, top_k)
    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return results