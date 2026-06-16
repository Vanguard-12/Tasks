import os
from typing import List

from langchain.tools import tool
from langchain.schema import Document
from tavily import TavilyClient

from vectorstore import create_vectorstore

# Initialise a single persistent vector store that will be shared by the tools.
_vectorstore = create_vectorstore()


@tool
def search_local_kb(query: str, top_k: int = 4) -> str:
    """Semantic search over the locally stored knowledge base (ChromaDB).

    Returns the concatenated page contents of the *top_k* most relevant chunks.
    """
    retriever = _vectorstore.as_retriever(search_kwargs={"k": top_k})
    docs: List[Document] = retriever.get_relevant_documents(query)
    if not docs:
        return "No relevant documents found in the local knowledge base."
    return "\n---\n".join([doc.page_content.strip() for doc in docs])


@tool
def web_search(query: str) -> str:
    """Perform a web search using the Tavily API.

    The function returns a plain‑text concatenation of the top results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set in environment variables.")
    client = TavilyClient(api_key=api_key)
    # Tavily returns a dict with a ``results`` key containing a list of dicts.
    response = client.search(query, max_results=5)
    results = response.get("results", [])
    if not results:
        return "No web results found."
    # Extract the ``content`` field from each result (if present).
    contents = [r.get("content", "").strip() for r in results if r.get("content")]
    return "\n---\n".join(contents)
