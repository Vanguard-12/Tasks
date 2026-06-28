from __future__ import annotations

from langchain.agents import create_agent as langchain_create_agent
from langchain_ollama import ChatOllama

from tools import search_local_kb, web_search


SYSTEM_PROMPT = """You are a RAG assistant with a local ChromaDB knowledge base and Tavily web search.

Use search_local_kb for questions about local documents, notes, internal materials,
or the project knowledge base.

Use web_search for recent news, current facts, releases, prices, or anything that
depends on the live internet.

Do not call both tools unless the user explicitly asks to compare local knowledge
with current web data. Always include exactly one source label in the final answer:
Источник: chromadb or Источник: tavily.
"""


def create_agent():
    return langchain_create_agent(
        model=ChatOllama(model="llama3"),
        tools=[search_local_kb, web_search],
        system_prompt=SYSTEM_PROMPT,
    )


def ask_agent(question: str) -> str:
    result = create_agent().invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    return str(messages[-1].content) if messages else ""
