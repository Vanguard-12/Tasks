from __future__ import annotations
'''run.py

Entry point that executes the HITL graph defined in ``hitl_graph.py``.
It streams the graph, detects the custom interrupt, asks the user a question
via ``questionary`` (falling back to ``input`` if the library is unavailable),
adds the answer to the payload and resumes the graph.
When the graph finishes the final state is printed, showing the value that
the user supplied.
'''  # noqa: D400

import uuid
from typing import Any

from langgraph.types import Command

# Import the compiled graph from the module we created.

import uuid
from typing import Any

from langgraph.types import Command

# Import the compiled graph (exposed as ``graph``) from the module.
from hitl_graph import graph


def _ask_user(payload: dict) -> str:
    """Present the interrupt payload to the user and return the chosen answer.

    The payload is expected to contain ``question`` (str) and ``options`` (list of str).
    ``questionary`` provides a nice interactive menu; if it cannot be imported we
    fall back to a simple ``input`` prompt.
    """

    question = payload.get("question", "Please provide a response:")
    choices = payload.get("options", [])

    try:
        import questionary
        answer = questionary.select(question, choices=choices).ask()
        if answer is None:
            answer = choices[0] if choices else ""
    except Exception:
        print(question)
        for idx, opt in enumerate(choices, start=1):
            print(f"{idx}. {opt}")
        while True:
            choice = input("Select an option (number or text): ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(choices):
                    answer = choices[idx]
                    break
            elif choice in choices:
                answer = choice
                break
            else:
                print("Invalid selection, try again.")
    return answer


def main() -> None:
    # Unique identifier for the thread – required for checkpointing.
    thread_id = str(uuid.uuid4())

    # Initial state – ``human_value`` is None so the node will trigger an interrupt.
    state: dict[str, Any] = {"human_value": None, "foo": "initial"}

    # ``next_input`` can be either a state dict (first run) or a Command (resume).
    next_input: Any = state

    while True:
        stream = graph.stream(next_input, configurable={"thread_id": thread_id})
        resumed = False
        for chunk in stream:
            if "__interrupt__" in chunk:
                payload = chunk["__interrupt__"][0].value
                answer = _ask_user(payload)
                payload["answer"] = answer
                next_input = Command(resume=payload)
                resumed = True
                break
            else:
                if "node" in chunk:
                    print("Final state:", chunk["node"])
        if not resumed:
            break


if __name__ == "__main__":
    main()
