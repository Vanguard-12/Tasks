import os
from typing import Any

import questionary
from langgraph.types import Command

from adventure_graph import graph


def run_adventure() -> None:
    """Entry point for the interactive story.

    The function:
    1. Asks the user for a theme (default ``space cat``).
    2. Starts the LangGraph stream.
    3. Detects the ``__interrupt__`` chunk, shows the question and options via ``questionary``.
    4. Sends the answer back to the graph with ``Command(resume=payload)``.
    5. After the graph finishes, prints the complete story.
    """
    theme = questionary.text("Enter a theme for the story:", default="space cat").ask()
    thread_id = "adventure_thread"
    config = {"configurable": {"thread_id": thread_id}}

    # Initial state contains the chosen theme.
    initial_state: dict[str, Any] = {"theme": theme}

    # Start the graph – it will immediately hit the interrupt after generating the hook.
    iterator = graph.stream(initial_state, config)
    for event in iterator:
        if "__interrupt__" in event:
            # Extract the payload that we passed to ``interrupt``.
            payload = event["__interrupt__"][0].value
            # Show the question and options to the user.
            answer = questionary.select(payload["question"], choices=payload["options"]).ask()
            # Attach the answer to the payload and resume the graph.
            payload["answer"] = answer
            # Resume – the same thread_id ensures the checkpoint is used.
            iterator = graph.stream(Command(resume=payload), config)
            # Continue processing the remaining chunks (there should be none besides the final state).
            for _ in iterator:
                pass
            break
    # Retrieve the final state from the checkpoint.
    final_state = graph.get_state(thread_id).values
    print("\n--- Final Story ---")
    print(final_state.get("hook", ""))
    print(f"Your choice: {final_state.get('user_choice', '')}")
    print(final_state.get("ending", ""))


if __name__ == "__main__":
    run_adventure()
