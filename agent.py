import json
from typing import Any, Dict

from langchain_ollama import OllamaChat
from langchain.agents import initialize_agent, Tool
from langchain.prompts import ChatPromptTemplate

from tools import search_course_docs, fetch_course_meta

# System prompt enforcing routing rules
SYSTEM_PROMPT = (
    "You are an FAQ assistant for a course. Use ONLY the provided tools. "
    "If the question is about course content, call `search_course_docs`. "
    "If it asks about schedule, instructor or other metadata, call `fetch_course_meta`. "
    "Never call both tools for the same query. "
    "Return the answer as a JSON object with a field `source` set to either \"chroma\" or \"mcp_meta\"."
)

# Define LangChain tool wrappers
search_tool = Tool(
    name="search_course_docs",
    func=lambda q: "\n".join([doc.page_content for doc in search_course_docs(q, k=3)]),
    description="Searches the course FAQ documents stored in ChromaDB. Input is a natural language query.",
)

meta_tool = Tool(
    name="fetch_course_meta",
    func=lambda q: json.dumps(fetch_course_meta(q)),
    description="Fetches course metadata (schedule, instructor, etc.) via an MCP‑style HTTP call.",
)


def _format_response(answer: str, source: str) -> str:
    payload: Dict[str, Any] = {"answer": answer, "source": source}
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_agent() -> Any:
    llm = OllamaChat(model="llama2")  # any available Ollama chat model
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}")
    ])
    agent = initialize_agent(
        tools=[search_tool, meta_tool],
        llm=llm,
        agent_type="zero-shot-react-description",
        prompt=prompt,
        verbose=False,
    )
    return agent


def answer_query(agent: Any, query: str) -> str:
    # Let the agent decide which tool to use
    raw = agent.run(query)
    # Determine source based on which tool was used (simple heuristic)
    source = "chroma" if "search_course_docs" in raw.lower() else "mcp_meta"
    # If the tool already returned JSON (meta tool), keep it as answer
    try:
        data = json.loads(raw)
        answer = json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        answer = raw
    return _format_response(answer, source)
