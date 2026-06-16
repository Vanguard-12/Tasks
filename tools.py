import json
import os
from pathlib import Path
from typing import List

import httpx
from langchain_community.vectorstores import Chroma

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CHROMA_DIR = Path(__file__).parent / "chroma_faq"
META_URL = os.getenv("META_URL", "http://localhost:8000/meta.json")

# ---------------------------------------------------------------------------
# Tool: search_course_docs
# ---------------------------------------------------------------------------

def _load_chroma() -> Chroma:
    """Load the persisted Chroma collection. Raises if the collection does not exist."""
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Chroma persistence directory not found at {CHROMA_DIR}. "
            "Run `python load_faq_to_chroma.py` first."
        )
    # The embedding model is only needed for similarity search; we can reuse the same model.
    from langchain_ollama import OllamaEmbeddings

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    return vectorstore


def search_course_docs(query: str, k: int = 3) -> List[str]:
    """Search the local FAQ Chroma collection.

    Args:
        query: The user question.
        k: Number of top results to return.

    Returns:
        A list of the most relevant document snippets.
    """
    vectorstore = _load_chroma()
    results = vectorstore.similarity_search(query, k=k)
    # Return just the page content for simplicity
    return [doc.page_content.strip() for doc in results]

# ---------------------------------------------------------------------------
# Tool: fetch_course_meta (MCP‑style mock)
# ---------------------------------------------------------------------------

def fetch_course_meta(key: str) -> str:
    """Fetch a piece of course metadata from a mock HTTP endpoint.

    The mock endpoint serves a static JSON file (see ``mock_data/meta.json``).
    ``key`` should be one of the top‑level keys in that JSON.
    """
    try:
        response = httpx.get(META_URL, timeout=5.0)
        response.raise_for_status()
    except Exception as exc:
        raise ConnectionError(f"Unable to reach metadata service at {META_URL}: {exc}")

    data = response.json()
    if key not in data:
        raise KeyError(f"Metadata key '{key}' not found. Available keys: {list(data.keys())}")
    return str(data[key])

# ---------------------------------------------------------------------------
# Exported tool list for the agent
# ---------------------------------------------------------------------------

__all__ = ["search_course_docs", "fetch_course_meta"]
