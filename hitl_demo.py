from __future__ import annotations

from typing import TypedDict, NotRequired, Any

from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
import questionary


class GraphState(TypedDict):
    """State schema for the simple HITL graph.

    * ``human_value`` – will be filled with the answer provided by the user.
    * ``foo`` – an example field to demonstrate that initial data can be passed.
    """

    human_value: NotRequired[str]
    foo: NotRequired[Any]


def interrupt_node(state: GraphState) -> GraphState:
    """Node that triggers a custom interrupt.

    The node creates a payload describing the interrupt (type, question, options)
    and calls ``interrupt``. Execution pauses here. When the graph is resumed the
    ``interrupt`` call returns the *payload* (now possibly enriched with the
    user's answer). The node then stores the answer in the state and returns it.
    """
    payload = {
        "type": "confirm",
        "question": "Are you sure you want to continue?",
        "options": ["approve", "reject"],
    }
    # ``interrupt`` signals the runtime to pause and emit ``__interrupt__``.
    response = interrupt(payload)
    # After resumption ``response`` will be the (possibly mutated) payload.
    if isinstance(response, dict) and "answer" in response:
        state["human_value"] = response["answer"]
    return state


def build_graph() -> StateGraph:
    """Constructs and compiles the graph with an in‑memory checkpoint saver."""
    builder = StateGraph(GraphState)
    builder.add_node("ask", interrupt_node)
    builder.add_edge(START, "ask")
    # No further nodes – after the interrupt the same node finishes and the
    # graph ends.
    graph = builder.compile(checkpointer=InMemorySaver())
    return graph


def run() -> None:
    """Runs the graph, handling the custom interrupt via the console.

    The loop:
    1. Starts the graph with an initial state.
    2. Detects a chunk containing ``__interrupt__``.
    3. Shows the question to the user using ``questionary.select``.
    4. Adds the chosen answer to the payload and resumes the graph.
    5. Prints the final state where ``human_value`` holds the user's answer.
    """
    graph = build_graph()
    thread_id = "demo_thread"

    # Initial execution – will pause at the interrupt.
    stream = graph.stream({"foo": "initial"}, configurable={"thread_id": thread_id})
    for chunk in stream:
        if "__interrupt__" in chunk:
            # Extract the payload that was sent to ``interrupt``.
            payload = chunk["__interrupt__"][0].value
            # Ask the user using an interactive menu.
            answer = questionary.select(payload["question"], choices=payload["options"]).ask()
            # Attach the answer to the payload so the node can store it.
            payload["answer"] = answer
            # Resume the graph with the enriched payload.
            resume_stream = graph.stream(Command(resume=payload), configurable={"thread_id": thread_id})
            for rchunk in resume_stream:
                # The final state is emitted in a chunk with the key "node".
                if "node" in rchunk:
                    print("Final state:", rchunk["node"])
                # If, for any reason, another interrupt appears, handle it
                # recursively (not expected in this simple example).
                if "__interrupt__" in rchunk:
                    inner_payload = rchunk["__interrupt__"][0].value
                    inner_answer = questionary.select(
                        inner_payload["question"], choices=inner_payload["options"]
                    ).ask()
                    inner_payload["answer"] = inner_answer
                    # Re‑resume with the new answer.
                    graph.stream(Command(resume=inner_payload), configurable={"thread_id": thread_id})
            break


if __name__ == "__main__":
    run()
