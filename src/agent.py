from __future__ import annotations

import os
from typing import TypedDict, Literal, Any, Callable

from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from .tools import unreliable_tool

# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------

class AgentState(TypedDict):
    task: str
    result: str
    attempts: int
    status: Literal["pending", "success", "failed", "max_attempts"]
    error: str | None
    max_attempts: int

# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def execute_task(state: AgentState) -> dict:
    """Run the assigned task using ``unreliable_tool``.

    The function never raises – it catches ``ValueError`` and stores the
    error message in the state. On success the ``result`` field is filled.
    """
    try:
        result = unreliable_tool(state["task"])
        return {"result": result, "error": None, "status": "pending"}
    except ValueError as exc:
        return {"result": "", "error": str(exc), "status": "failed"}


def _get_llm():
    """Return a Chat model.

    Preference is given to OpenAI if the ``OPENAI_API_KEY`` environment variable
    is present; otherwise Ollama is used (default model ``llama3``).
    """
    if os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(model="gpt-3.5-turbo")
    # Fallback to Ollama – assumes Ollama server is running locally.
    return ChatOllama(model="llama3")


def verify_result(state: AgentState) -> dict:
    """Ask an LLM to judge whether ``result`` satisfies ``task``.

    The prompt forces the model to answer with the literal word ``success``
    or ``failed`` (lower‑case). Any other response is treated as ``failed``.
    """
    llm = _get_llm()
    system = SystemMessage(
        content=(
            "You are a judge. Given a task and its result, respond with only the word "
            "'success' if the result correctly fulfills the task, otherwise respond "
            "with 'failed'. Do not add any extra text."
        )
    )
    human = HumanMessage(content=f"Task: {state['task']}\nResult: {state['result']}")
    response = llm.invoke([system, human])
    answer = response.content.strip().lower()
    if answer == "success":
        return {"status": "success"}
    else:
        return {"status": "failed"}


def handle_error(state: AgentState) -> dict:
    """Increment ``attempts`` and decide whether to retry or stop.

    If ``attempts`` reaches ``max_attempts`` the status becomes ``max_attempts``;
    otherwise it stays ``failed`` and the graph will loop back to ``execute_task``.
    """
    attempts = state["attempts"] + 1
    if attempts >= state["max_attempts"]:
        return {"attempts": attempts, "status": "max_attempts"}
    else:
        return {"attempts": attempts, "status": "failed"}

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def build_agent_graph() -> StateGraph[AgentState]:
    """Create and compile the StateGraph according to the assignment spec."""
    graph = StateGraph(AgentState)

    # Register nodes
    graph.add_node("execute_task", execute_task)
    graph.add_node("verify_result", verify_result)
    graph.add_node("handle_error", handle_error)

    # Entry point
    graph.set_entry_point("execute_task")

    # Linear flow: execute -> verify
    graph.add_edge("execute_task", "verify_result")

    # Conditional after verification
    def verify_cond(state: AgentState) -> Literal["success", "failed"]:
        # ``status`` is set by ``verify_result`` to either "success" or "failed"
        return state["status"]  # type: ignore[return-value]

    graph.add_conditional_edges(
        "verify_result",
        verify_cond,
        {"success": END, "failed": "handle_error"},
    )

    # Conditional after handling error / retry logic
    def handle_cond(state: AgentState) -> Literal["END", "execute_task"]:
        return "END" if state["status"] == "max_attempts" else "execute_task"

    graph.add_conditional_edges(
        "handle_error",
        handle_cond,
        {"END": END, "execute_task": "execute_task"},
    )

    return graph.compile()
