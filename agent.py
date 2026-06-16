import re
from typing import List

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from tools import search_course_docs, fetch_course_meta

# ---------------------------------------------------------------------------
# Simple routing logic
# ---------------------------------------------------------------------------

META_KEYWORDS = {"schedule", "time", "date", "metadata", "instructor", "contact", "location"}


def _choose_tool(question: str) -> str:
    """Return the name of the tool that should handle *question*.

    If the question contains any of the ``META_KEYWORDS`` we treat it as a
    metadata request; otherwise we fall back to the Chroma FAQ search.
    """
    lowered = question.lower()
    if any(word in lowered for word in META_KEYWORDS):
        return "meta"
    return "chroma"

# ---------------------------------------------------------------------------
# LLM configuration – we use the local Ollama model (any chat model works).
# ---------------------------------------------------------------------------

llm = ChatOllama(model="llama3.1:8b", temperature=0.0)  # adjust model name as needed

# System prompt that explains the routing rules to the model (useful for chain‑of‑thought).
SYSTEM_PROMPT = (
    "You are a helpful FAQ assistant for a programming course. "
    "When a user asks about lecture content, retrieve the answer from the local FAQ database. "
    "When the user asks about schedule, instructor, contact, or any other course metadata, fetch it using the provided metadata tool. "
    "Never call both tools for the same question. "
    "After you have the answer, append a line exactly like `source: chroma` or `source: mcp_meta` to indicate where the information came from."
)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def answer_question(question: str) -> str:
    """Process *question* using the appropriate tool and return a formatted answer.

    The function performs the following steps:
    1. Decide which tool to call based on simple keyword routing.
    2. Retrieve the raw information.
    3. Pass the raw information to the LLM so it can formulate a friendly answer.
    4. Append the required ``source: ...`` tag.
    """
    tool = _choose_tool(question)
    if tool == "meta":
        # Try to extract a plausible key from the question – very naive approach.
        # We look for the first keyword that matches our META_KEYWORDS.
        match = next((kw for kw in META_KEYWORDS if kw in question.lower()), None)
        key = match if match else "schedule"
        raw = fetch_course_meta(key)
        source_tag = "source: mcp_meta"
    else:
        snippets: List[str] = search_course_docs(question, k=3)
        raw = "\n---\n".join(snippets) if snippets else "No relevant information found."
        source_tag = "source: chroma"

    # Let the LLM turn the raw data into a user‑friendly answer.
    chain = prompt | llm
    response = chain.invoke({"question": question + "\n\nRelevant data:\n" + raw})
    answer = response.content.strip()
    # Ensure the source tag is on its own line.
    if not answer.endswith(source_tag):
        answer = f"{answer}\n{source_tag}"
    return answer


if __name__ == "__main__":
    # Simple demo when the module is executed directly.
    demo_questions = [
        "What is a Python list and how do I create one?",
        "How do I define a function in Python?",
        "When does the course meet?",
    ]
    for q in demo_questions:
        print(f"Q: {q}")
        print(f"A: {answer_question(q)}\n")
