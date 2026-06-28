from __future__ import annotations

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from vectorstore import create_vectorstore


@tool
def search_local_kb(query: str, top_k: int = 4) -> str:
    """Search local documents stored in ChromaDB."""
    retriever = create_vectorstore().as_retriever(search_kwargs={"k": top_k})
    documents = retriever.invoke(query)
    if not documents:
        return "Источник: chromadb\nВ локальной базе знаний ничего не найдено."

    lines = ["Источник: chromadb"]
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "local document")
        lines.append(f"[{index}] {source}\n{document.page_content}")
    return "\n\n".join(lines)


@tool
def web_search(query: str) -> str:
    """Search web resources through Tavily for current facts and news."""
    result = TavilySearch(max_results=5).invoke({"query": query})
    return f"Источник: tavily\n{result}"
