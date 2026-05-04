# rag/context_builder.py
from rag.faiss_store import search


def build_context(query: str) -> str:
    """
    Search FAISS for relevant chunks and format
    them into a single context string for the LLM.
    """
    chunks = search(query)
    context = "\n\n---\n\n".join(chunks)
    return context