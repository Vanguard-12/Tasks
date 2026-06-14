import os
import sys
import random
import re
from typing import TypedDict, Literal, Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# ---------------------------------------------------------------------------
# Load environment variables (API keys, etc.)
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Agent state definition
# ---------------------------------------------------------------------------
class AgentState(TypedDict):
    task: str
    result: Optional[str]
    attempts: int
    status: Literal["pending", "success", "failed", "max_attempts"]
    error: Optional[str]
    max_attempts: int

# ---------------------------------------------------------------------------
# Unreliable tool – 30% chance to raise, otherwise evaluates a simple math expr
# ---------------------------------------------------------------------------
def unreliable_tool(task: str) -> str:
    """Parse a Russian phrase like 'Вычисли 2+2' and return the result.
    Raises ValueError with ~30% probability to simulate failure.
    """
    if random.random() < 0.3:
        raise ValueError("Simulated tool failure")

    # Extract the arithmetic expression after the word "Вычисли"
    match = re.search(r"Вычисли\s*([0-9+\-*/().\s]+)", task, re.IGNORECASE)
    if not match:
        raise ValueError("Could not parse task")
    expr = match.group(1).strip()
    # Very naive safe eval – only numbers and operators are allowed
    if not re.fullmatch(r"[0-9+\-*/().\s]+", expr):
        raise ValueError("Unsafe expression")
    try:
        # eval is acceptable here because of the strict regex above
        result = eval(expr, {"__builtins__": {}})
    except Exception as exc:
        raise ValueError(f"Evaluation error: {exc}")
    return str(result)

# ---------------------------------------------------------------------------
# Node implementations
# ---------------------------------------------------------------------------

def execute_task(state: AgentState) -> AgentState:
    """Call the unreliable tool and store result or error."""
    print(f"\nПопытка {state['attempts'] + 1}:")
    try:
        result = unreliable_tool(state["task"])
        state["result"] = result
        state["error"] = None
        print(f"  результат {result}")
    except Exception as exc:
        state["result"] = None
        state["error"] = str(exc)
        print(f"  Error → {exc}")
    # After execution we keep status as pending – verification will decide
    state["status"] = "pending"
    return state


def verify_result(state: AgentState) -> AgentState:
    """Ask LLM to judge the result. The LLM must answer only 'success' or 'failed'."""
    # Prepare the prompt
    result_text = state["result"] if state["result"] is not None else f"Error: {state['error']}"
    prompt = (
        f"Task: {state['task']}\n"
        f"Result: {result_text}\n"
        "Ответьте ТОЛЬКО одним словом: 'success' если результат удовлетворяет задаче, иначе 'failed'."
    )
    # Initialize LLM (uses OPENAI_API_KEY from env)
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    verdict = response.content.strip().lower()
    if verdict not in {"success", "failed"}:
        # Fallback – treat unknown response as failure
        verdict = "failed"
    state["status"] = verdict
    print(f"  verify: {verdict}")
    return state


def handle_error(state: AgentState) -> AgentState:
    """Increment attempts and decide whether to retry or stop."""
    state["attempts"] += 1
    if state["attempts"] >= state["max_attempts"]:
        state["status"] = "max_attempts"
        print("  Достигнут лимит попыток.")
    else:
        # Prepare for another try
        state["result"] = None
        state["error"] = None
        state["status"] = "pending"
        print("  Подготовка к повтору.")
    return state

# ---------------------------------------------------------------------------
# Build the StateGraph
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("execute_task", execute_task)
    graph.add_node("verify_result", verify_result)
    graph.add_node("handle_error", handle_error)
    graph.set_entry_point("execute_task")

    # execute -> verify
    graph.add_edge("execute_task", "verify_result")

    # Conditional edges from verify_result
    def route_verify(state: AgentState):
        if state["status"] == "success":
            return END
        if state["status"] == "failed" and state["attempts"] < state["max_attempts"]:
            return "handle_error"
        # max attempts reached or unknown status
        return END

    graph.add_conditional_edges("verify_result", route_verify, ["handle_error", END])
    # handle_error -> execute_task (retry)
    graph.add_edge("handle_error", "execute_task")
    return graph.compile()

# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m main \"<task>\"")
        sys.exit(1)
    task = sys.argv[1]
    max_attempts = 5
    initial_state: AgentState = {
        "task": task,
        "result": None,
        "attempts": 0,
        "status": "pending",
        "error": None,
        "max_attempts": max_attempts,
    }
    print(f"Задача: {task}")
    graph = build_graph()
    final_state = graph.invoke(initial_state)
    attempts = final_state["attempts"]
    if final_state["status"] == "success":
        print(f"Итог: success за {attempts} попыт{'ок' if attempts != 1 else 'ку'}")
    else:
        print(f"Итог: failed after {attempts} попыт{'ок' if attempts != 1 else 'ки'}")

if __name__ == "__main__":
    main()
