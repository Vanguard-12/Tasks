from __future__ import annotations
"""Human‑in‑the‑loop (interrupt / resume) demo using LangGraph.

The script defines a tiny graph with a single node that raises a custom interrupt.
When the interrupt is caught, the user is asked a question via the console (using
`questionary`). The answer is fed back into the graph, which then finishes and
prints the final state.
"""


from typing import TypedDict, Optional, Any, Dict, List

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
import questionary

# ---------------------------------------------------------------------------
# Graph state definition
# ---------------------------------------------------------------------------

class GraphState(TypedDict, total=False):
    """State carried through the graph.

    `human_value` will contain the answer supplied by the user after the
    interrupt is resumed.
    """

    human_value: Optional[str]

# ---------------------------------------------------------------------------
# Node implementation
# ---------------------------------------------------------------------------

def interrupt_node(state: GraphState) -> Any:
    """Node that either raises an interrupt or stores the resumed answer.

    The node is called twice:
    * **First call** – `state` does not contain an ``answer`` key, so we raise
      an interrupt with a payload describing the question.
    * **Second call (after resume)** – the payload we passed to ``interrupt``
      is returned as ``state``. It now contains the ``answer`` key, which we copy
      into the graph state.
    """

    # When the node is resumed the payload we passed to ``interrupt`` is handed
    # back as the ``state`` argument. Detect that case and store the answer.
    if isinstance(state, dict) and "answer" in state:
        # The user has responded – store the answer in the graph state.
        return {"human_value": state["answer"]}

    # First invocation – raise a custom interrupt.
    payload: Dict[str, Any] = {
        "type": "confirm",
        "question": "Are you sure you want to continue?",
        "options": ["approve", "reject"],
    }
    # ``interrupt`` tells LangGraph to pause execution and emit a chunk with the
    # ``__interrupt__`` key containing this payload.
    return interrupt(payload)

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

# Create a StateGraph that works with ``GraphState``.
graph = StateGraph(GraphState)
graph.add_node("interrupt", interrupt_node)
# The graph finishes after the interrupt node returns a normal state.
graph.add_edge(START, "interrupt")
# No further nodes – the graph ends when the interrupt node returns a dict.
graph = graph.compile(checkpointer=InMemorySaver())

# ---------------------------------------------------------------------------
# Execution loop handling the interrupt
# ---------------------------------------------------------------------------

def run() -> None:
    thread_id = "demo-thread"
    config = {"thread_id": thread_id}

    # Initial stream – start the graph with an empty state.
    stream = graph.stream({"human_value": None}, configurable=config)
    for chunk in stream:
        # LangGraph emits a special ``__interrupt__`` key when an interrupt is
        # raised. The value is a list of ``Interrupt`` objects; we take the first
        # one and read its ``value`` attribute which holds the payload we passed.
        if "__interrupt__" in chunk:
            interrupt_obj = chunk["__interrupt__"][0]
            payload: Dict[str, Any] = interrupt_obj.value  # type: ignore
            # Show the question to the user and capture the answer.
            answer = questionary.select(
                payload["question"], choices=payload["options"]
            ).ask()
            # Enrich the payload with the answer so that the resumed node can
            # store it in the graph state.
            payload["answer"] = answer
            # Resume the graph with the updated payload.
            resume_stream = graph.stream(Command(resume=payload), configurable=config)
            for resume_chunk in resume_stream:
                # The final state will be emitted under the node name (here
                # ``interrupt``) because that node returns the completed state.
                if "interrupt" in resume_chunk:
                    final_state = resume_chunk["interrupt"]
                    print("Final state:", final_state)
            # Once we have resumed and printed the final state we can exit.
            break

if __name__ == "__main__":
    run()
