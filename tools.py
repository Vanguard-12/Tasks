import os
from typing import List
import httpx
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def _get_chroma_collection(persist_dir: str = "chroma_faq") -> Chroma:
    """Return a ready‑to‑use Chroma vector store.

    The function assumes that the collection has already been created by
    ``load_faq_to_chroma.py``.
    """
    if not os.path.isdir(persist_dir):
        raise RuntimeError(
            f"Chroma directory '{persist_dir}' not found. Run load_faq_to_chroma first."
        )
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return Chroma(persist_directory=persist_dir, embedding_function=embeddings)


def search_course_docs(query: str, k: int = 3) -> List[str]:
    """Search the local FAQ collection and return the top *k* snippets."""
    vectordb = _get_chroma_collection()
    results = vectordb.similarity_search(query, k=k)
    return [doc.page_content for doc in results]


def fetch_course_meta(query: str) -> str:
    """Mock MCP‑style tool.

    It performs a simple HTTP GET to the local mock server (``http://localhost:8000/metadata.json``)
    and tries to return a value that matches the query. If no match is found, the whole JSON
    payload is returned as a string.
    """
    url = "http://localhost:8000/metadata.json"
    try:
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return f"Error fetching metadata: {exc}"

    query_lc = query.lower()
    for key, value in data.items():
        if key.lower() in query_lc:
            return f"{key}: {value}"
    # Fallback – return the whole JSON as a readable string
    return ", ".join([f"{k}: {v}" for k, v in data.items()])
