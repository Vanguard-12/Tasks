from __future__ import annotations
'''hitl_custom_demo.py

A minimal LangGraph example that demonstrates a custom interrupt (Human‑in‑the‑loop).
The graph consists of a single node that raises an interrupt with a payload
containing a question and a list of possible answers. The driver loop detects
the interrupt, asks the user for a choice via ``questionary`` and then resumes
the graph. After resumption the answer is stored in the graph state and the
final state is printed.

Run with:
    python hitl_custom_demo.py
'''


from typing import TypedDict, Literal, List, Optional

import questionary
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

# ---------------------------------------------------------------------------
# 1. Define the graph state
# ---------------------------------------------------------------------------
class GraphState(TypedDict, total=False):
    """State carried through the graph.

    * ``human_value`` – will be filled with the answer supplied by the user.
    * ``foo`` – an example field that could hold initial data (optional).
    """

    human_value: Optional[str]
    foo: Optional[str]

# ---------------------------------------------------------------------------
# 2. Node that raises a custom interrupt
# ---------------------------------------------------------------------------
def ask_user(state: GraphState) -> GraphState:
    """Node that pauses execution and asks the user a question.

    The function calls ``interrupt`` with a dictionary payload.  When the
    graph is resumed the same payload (now enriched with the user's answer)
    is passed back to this node, allowing us to store the answer in the state.
    """
    # If we are being resumed we will already have an ``answer`` field.
    if "answer" in state:
        # Store the answer and finish.
        state["human_value"] = state["answer"]  # type: ignore[index]
        return state

    # First entry – raise the interrupt.
    payload = {
        "type": "confirm",
        "question": "Are you sure you want to continue?",
        "options": ["approve", "reject"],
    }
    # ``interrupt`` raises a special exception that LangGraph catches and
    # propagates as a chunk with the ``__interrupt__`` key.
    raise interrupt(payload)

# ---------------------------------------------------------------------------
# 3. Build the graph with a checkpoint saver
# ---------------------------------------------------------------------------
saver = InMemorySaver()
graph = StateGraph(GraphState)
graph.add_node("ask", ask_user)
graph.add_edge(START, "ask")
# No further edges – the node returns the final state.
compiled = graph.compile(checkpointer=saver)

# ---------------------------------------------------------------------------
# 4. Driver loop that handles the interrupt and resumes the graph
# ---------------------------------------------------------------------------
def run_demo(thread_id: str = "demo-thread") -> None:
    """Execute the graph, handling the custom interrupt.

    The function streams the graph, looks for a ``__interrupt__`` chunk, asks the
    user for input using ``questionary.select`` and then resumes the graph with
    the enriched payload.
    """
    # Initial run – no state is required, LangGraph will create an empty dict.
    config = {"configurable": {"thread_id": thread_id}}
    iterator = compiled.stream(None, **config)

    for chunk in iterator:
        # ``chunk`` is a dict mapping node names to their output.  When an
        # interrupt occurs LangGraph adds a special ``__interrupt__`` key.
        if "__interrupt__" in chunk:
            # The interrupt payload is stored as a list of ``Command`` objects.
            # The first (and only) element holds the original payload in its
            # ``value`` attribute.
            interrupt_cmd = chunk["__interrupt__"][0]
            payload: dict = interrupt_cmd.value  # type: ignore[assignment]
            print("\n--- Interrupt received ---")
            print(payload)

            # Ask the user using ``questionary``.
            answer = questionary.select(
                payload["question"],
                choices=payload["options"],
            ).ask()
            if answer is None:
                # User aborted (Ctrl‑C).  We simply exit.
                print("No answer provided – exiting.")
                return

            # Enrich the payload with the answer and resume.
            payload["answer"] = answer
            # Resume the graph with the same thread_id.
            resume_iter = compiled.stream(Command(resume=payload), **config)
            for resume_chunk in resume_iter:
                # The resumed run will eventually return the final state.
                if "ask" in resume_chunk:
                    final_state = resume_chunk["ask"]
                    print("\n--- Final state ---")
                    print(final_state)
                    return
        else:
            # Normal (non‑interrupt) chunks – in this tiny graph we only get
            # the final state after the interrupt has been handled.
            continue

if __name__ == "__main__":
    run_demo()
