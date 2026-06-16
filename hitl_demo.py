from __future__ import annotations
"""Human-in-the-loop (custom interrupt) demo using LangGraph.

Run the script with ``python hitl_demo.py``. It will:
1. Build a simple LangGraph with a single node that raises a custom interrupt.
2. Stream the graph, detect the interrupt and ask the user a question via ``questionary``.
3. Resume the graph with the user's answer and print the final state.
"""


import uuid
from typing import TypedDict, Literal, List, Any, Union

import questionary
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Interrupt, Command, interrupt

# ---------------------------------------------------------------------------
# Graph state definition
# ---------------------------------------------------------------------------
class GraphState(TypedDict, total=False):
    """State carried through the graph.

    * ``human_value`` – will hold the answer supplied by the user.
    * ``foo`` – an example field that could be used for initial data.
    * ``answer`` – temporary field used when the node is resumed after an
      interrupt. It is removed from the final output.
    """

    human_value: str | None
    foo: str
    answer: str

# ---------------------------------------------------------------------------
# Node that either raises an interrupt or processes the resumed payload
# ---------------------------------------------------------------------------
def ask_node(state: GraphState) -> Union[GraphState, Interrupt]:
    """Node that asks the user for confirmation.

    If the state already contains an ``answer`` (i.e. the node is being resumed),
    the answer is stored in ``human_value`` and the updated state is returned.
    Otherwise the node raises a custom interrupt with a payload describing the
    question and the allowed responses.
    """

    # Resumed after interrupt – the payload contains the user's answer.
    if "answer" in state:
        # Store the answer in the final field and clean up the temporary key.
        state["human_value"] = state.pop("answer")
        return state

    # First call – raise a custom interrupt.
    payload: dict[str, Any] = {
        "type": "confirm",
        "question": "Are you sure you want to continue?",
        "allow_responses": ["approve", "reject"],
    }
    return interrupt(payload)

# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------
graph = StateGraph(GraphState)
graph.add_node("ask", ask_node)
graph.add_edge(START, "ask")
graph.set_entry_point("ask")
# Use an in‑memory checkpoint so we can pause and resume.
graph = graph.compile(checkpointer=InMemorySaver())

# ---------------------------------------------------------------------------
# Execution loop handling the custom interrupt
# ---------------------------------------------------------------------------
def run_demo() -> None:
    thread_id = str(uuid.uuid4())
    config = {"thread_id": thread_id}
    # Initial empty state – the graph will populate it.
    current_input: Any = {}

    while True:
        # Stream the graph with the current input (either a state dict or a Command).
        for chunk in graph.stream(current_input, config=config):
            # Detect a custom interrupt.
            if "__interrupt__" in chunk:
                # The interrupt payload is stored in the first element of the list.
                payload = chunk["__interrupt__"][0].value
                # Ask the user via questionary.
                answer = questionary.select(
                    payload["question"], choices=payload["allow_responses"]
                ).ask()
                # Attach the answer to the payload and resume the graph.
                payload["answer"] = answer
                current_input = Command(resume=payload)
                # Break out of the inner for‑loop to start a new streaming pass.
                break
            # Normal output – when the graph finishes it yields a chunk with "output".
            if "output" in chunk:
                final_state = chunk["output"]
                print("\n--- Graph finished ---")
                print("Final state:", final_state)
                return
        else:
            # No more chunks – exit the outer while loop.
            break

if __name__ == "__main__":
    run_demo()
