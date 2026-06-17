from __future__ import annotations

from typing import Any

from .agent import AgentState, build_agent_graph


def main() -> None:
    # Initial state for the demo task
    initial_state: AgentState = {
        "task": "Вычисли 2+2",
        "result": "",
        "attempts": 0,
        "status": "pending",
        "error": None,
        "max_attempts": 5,
    }

    graph = build_agent_graph()

    print(f"Задача: {initial_state['task']}")

    # ``graph.stream`` yields (node_name, node_output, new_state) tuples.
    final_state: AgentState | None = None
    for node_name, _, state in graph.stream(initial_state):
        # ``state`` is the cumulative state after the node execution.
        if node_name == "execute_task":
            if state["error"]:
                # attempts have not been incremented yet – show next attempt number
                attempt_no = state["attempts"] + 1
                print(f"Попытка {attempt_no}: Error → {state['error']}")
            else:
                attempt_no = state["attempts"] + 1
                print(f"Попытка {attempt_no}: result {state['result']}")
        elif node_name == "verify_result":
            print(f"verify: {state['status']}")
        # ``handle_error`` does not need its own print – the next ``execute_task``
        # will show the incremented attempt number.
        final_state = state

    # After the loop ``final_state`` holds the terminal state.
    if final_state is None:
        return

    if final_state["status"] == "success":
        print(f"Итог: success за {final_state['attempts']} попытки")
    elif final_state["status"] == "max_attempts":
        print(
            f"Итог: max_attempts reached after {final_state['attempts']} попыток"
        )
    else:
        # Any other terminal status (should not happen in this demo)
        print(f"Итог: {final_state['status']} after {final_state['attempts']} попыток")


if __name__ == "__main__":
    main()
