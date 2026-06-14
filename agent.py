from tools import search_course_docs, fetch_course_meta
from typing import List


def _choose_source(question: str) -> str:
    """Very simple keyword‑based routing.

    If the question contains any of the *meta* keywords we delegate to the MCP‑style
    tool, otherwise we query the Chroma FAQ collection.
    """
    meta_keywords = ["schedule", "lecture", "date", "time", "when", "deadline", "next"]
    return "mcp_meta" if any(word in question.lower() for word in meta_keywords) else "chroma"


def answer_question(question: str) -> str:
    """Return an answer together with a ``source:`` line.

    The function respects the routing rule defined in ``_choose_source`` and never
    calls both tools for the same request.
    """
    source = _choose_source(question)
    if source == "mcp_meta":
        answer = fetch_course_meta(question)
    else:
        snippets = search_course_docs(question, k=3)
        answer = "\n".join(snippets) if snippets else "No relevant information found."
    return f"{answer}\nsource: {source}"
