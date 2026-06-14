from __future__ import annotations

from typing import TypedDict, Optional, Dict, Any

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
import questionary


class GraphState(TypedDict):
    """State of the graph.

    * ``foo`` – an example initial value.
    * ``human_value`` – will be filled with the answer provided by the user.
    * ``answer`` – temporary field used only when the node is resumed after an interrupt.
    """

    foo: str
    human_value: Optional[str]
    # ``answer`` is not part of the final state, but LangGraph will merge the resume payload
    # into the state dictionary, so we declare it as optional to keep type‑checkers happy.
    answer: Optional[str]


def human_node(state: GraphState) -> GraphState:
    """Node that asks the user for confirmation via a custom interrupt.

    The first time the node runs it raises ``interrupt(payload)`` which causes
    LangGraph to emit a ``__interrupt__`` chunk. When the graph is resumed the
    payload (now possibly containing an ``answer``) is merged back into ``state``.
    """

    # If we have already received an answer (i.e. the node was resumed), store it.
    if state.get("answer"):
        state["human_value"] = state["answer"]
        # Clean up the temporary field – it is not needed in the final output.
        state.pop("answer", None)
        return state

    # No answer yet – trigger a custom interrupt.
    payload: Dict[str, Any] = {
        "type": "confirm",
        "question": "Уверены, что хотите продолжить?",
        "options": ["approve", "reject"],
    }
    raise interrupt(payload)


def build_graph():
    """Construct and compile the LangGraph workflow with an in‑memory checkpoint."""
    builder = StateGraph(GraphState)
    builder.add_node("human_node", human_node)
    builder.add_edge(START, "human_node")
    # No explicit entry point needed; START → human_node is sufficient.
    compiled = builder.compile(checkpointer=InMemorySaver())
    return compiled

# Expose the compiled graph as ``graph`` for external callers (e.g., run.py).
# This mirrors the original expectation that ``from hitl_graph import graph``
# yields an object with a ``stream`` method.
graph = build_graph()

def run():
    """Execute the graph, handling the custom interrupt with ``questionary``.

    The function runs the graph once – it will stop at the interrupt – then asks the
    user a question in the console, resumes the graph with the answer and finally
    prints the resulting state.
    """
    thread_id = "example_thread"
    config = {"configurable": {"thread_id": thread_id}}

    # First pass – will hit the interrupt.
    for chunk in graph.stream(config=config):
        if "__interrupt__" in chunk:
            # Extract the payload we sent via ``interrupt``.
            payload = chunk["__interrupt__"][0].value  # type: ignore[arg-type]
            # Show the question to the user and capture the answer.
            answer = questionary.select(
                payload["question"], choices=payload["options"]
            ).ask()
            # Attach the answer to the payload – this will be merged back into the state.
            payload["answer"] = answer
            # Resume the graph with the enriched payload.
            for resume_chunk in graph.stream(Command(resume=payload), config=config):
                if "node" in resume_chunk:
                    print("Final state:", resume_chunk["node"])
        elif "node" in chunk:
            # In case the graph finishes without an interrupt (should not happen here).
            print("Final state:", chunk["node"])

if __name__ == "__main__":
    run()
