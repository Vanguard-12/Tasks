from typing import List

from langchain_community.utilities import TavilySearchResults

# The vectorstore will be injected from ``main.py``.
_vectorstore = None


def set_vectorstore(vs):
    """Inject the Chroma vectorstore instance used by the ``search_local_kb`` tool.
    """
    global vectorstore
    vectorstore = vs


def search_local_kb(query: str, top_k: int = 4) -> str:
    """Semantic search in the local ChromaDB knowledge base.

    Returns the concatenated page contents of the most relevant documents.
    If the store is not initialised or no documents match, a friendly message
    is returned.
    """
    if vectorstore is None:
        return "Vector store not initialised."
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.get_relevant_documents(query)
    if not docs:
        return "No relevant documents found in the local knowledge base."
    return "\n\n---\n\n".join([doc.page_content for doc in docs])


def web_search(query: str) -> str:
    """Perform a web search via the Tavily API and return a concise summary.
    """
    tavily = TavilySearchResults()
    try:
        result = tavily.run(query)
    except Exception as exc:
        return f"Web search failed: {exc}"
    return result
