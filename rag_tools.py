from typing import List

from langchain.tools import tool
from langchain.schema import Document

from rag_vector_store import add_documents, search
from rag_chunker import chunk_document


@tool
def search_knowledge_base(query: str, max_results: int = 5) -> List[Document]:
    """Semantic search over the knowledge base.

    Returns up to ``max_results`` documents most relevant to ``query``.
    """
    return search(query, k=max_results)


@tool
def add_to_knowledge_base(content: str, title: str) -> str:
    """Add a new piece of information to the knowledge base.

    The ``content`` is split into chunks, each chunk is embedded and stored.
    Returns a short confirmation message.
    """
    docs = chunk_document(content, title)
    add_documents(docs)
    return f"Added {len(docs)} chunk(s) for document titled '{title}'."
