from typing import List, Dict
from langchain.tools import tool

from vector_store import add_documents, search
from chunker import chunk_text


@tool
def add_to_knowledge_base(content: str, title: str) -> str:
    """Add a document to the knowledge base.

    The *content* is split into chunks before being stored.
    Returns a short confirmation message.
    """
    chunks = chunk_text(content, title)
    add_documents(chunks)
    return f"Added {len(chunks)} chunks from '{title}' to the knowledge base."


@tool
def search_knowledge_base(query: str, max_results: int = 5) -> str:
    """Search the knowledge base and return the most relevant chunks.

    The result is a newline‑separated list containing title, chunk index and a short snippet.
    """
    results: List[Dict] = search(query, max_results)
    if not results:
        return "No relevant documents found."
    lines = []
    for r in results:
        meta = r.get("metadata", {})
        snippet = r.get("content", "")[:200].replace("\n", " ")
        lines.append(
            f"Title: {meta.get('title', '')}, Chunk: {meta.get('chunk_index', '')}, Snippet: {snippet}"
        )
    return "\n".join(lines)
