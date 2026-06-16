import uuid
import os
from typing import Any, Dict

import questionary
from langgraph.types import Command

from graph import build_graph
from state import AdventureState


def _extract_interrupt(chunk: Dict[str, Any]) -> Dict[str, Any] | None:
    """Helper to pull the interrupt payload from a streamed chunk.

    LangGraph yields dictionaries; when an interrupt occurs the key
    ``"__interrupt__"`` is present and its value is a list of ``Interrupt``
    objects. The first object's ``value`` attribute holds the payload we
    supplied in ``interrupt(payload)``.
    """
    intr = chunk.get("__interrupt__")
    if intr:
        # ``intr`` is a list – we take the first element.
        return intr[0].value  # type: ignore[attr-defined]
    return None


def run_adventure() -> None:
    # ---------------------------------------------------------------------
    # 1. Gather the initial theme from the user (or use a default).
    # ---------------------------------------------------------------------
    theme = questionary.text("Enter a story theme (default: 'space cat'):").ask()
    if not theme:
        theme = "space cat"

    # ---------------------------------------------------------------------
    # 2. Initialise the graph and start the first stream.
    # ---------------------------------------------------------------------
    graph = build_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    # The initial state only contains the theme.
    initial_state: AdventureState = {"theme": theme}

    # ---------------------------------------------------------------------
    # 3. Process the stream – we expect a single interrupt, then a final
    #    state containing the ending.
    # ---------------------------------------------------------------------
    stream = graph.stream(initial_state, config=config)
    for chunk in stream:
        payload = _extract_interrupt(chunk)
        if payload:
            # -----------------------------------------------------------------
            # 4. Human‑in‑the‑loop: present the question and options.
            # -----------------------------------------------------------------
            question = payload.get("question", "")
            options = payload.get("options", [])
            answer = questionary.select(question, choices=options).ask()
            # Attach the answer to the payload – this will become the resumed
            # input for the next node.
            payload["user_choice"] = answer
            # -----------------------------------------------------------------
            # 5. Resume the graph with the enriched payload.
            # -----------------------------------------------------------------
            resume_stream = graph.stream(Command(resume=payload), config=config)
            for r_chunk in resume_stream:
                # The final chunk contains the updated state under the key
                # "values". When the graph reaches END it yields the state.
                if "values" in r_chunk:
                    final_state: AdventureState = r_chunk["values"]
                    print("\n--- Your Adventure ---\n")
                    print(final_state.get("hook", ""))
                    print(f"\nYou chose: {final_state.get('user_choice', '')}\n")
                    print(final_state.get("ending", ""))
                    return
        # If the chunk is not an interrupt we simply continue – the node may
        # have emitted log messages, but for this simple demo we ignore them.


if __name__ == "__main__":
    # Load environment variables (e.g., OPENAI_API_KEY) if a .env file is present.
    from dotenv import load_dotenv

    load_dotenv()
    run_adventure()
