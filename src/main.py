import os
import sys
from dotenv import load_dotenv
from .graph import build_graph
from .agent_state import AgentState

def main(task: str, max_attempts: int = 5):
    load_dotenv()  # Load OPENAI_API_KEY from .env if present
    graph = build_graph()
    compiled = graph.compile()

    # Initial state
    state: AgentState = {
        "task": task,
        "result": None,
        "attempts": 0,
        "status": "pending",
        "error": None,
        "max_attempts": max_attempts,
    }

    print(f"Задача: {task}")
    # Stream execution to observe each step
    for event in compiled.stream(state):
        # event is a tuple (node_name, node_output_state)
        node_name, node_state = event
        attempts = node_state["attempts"] + 1 if node_name == "execute_task" else node_state["attempts"]
        if node_name == "execute_task":
            if node_state["error"]:
                print(f"Попытка {attempts}: Error({node_state['error']}) → verify: pending")
            else:
                print(f"Попытка {attempts}: результат {node_state['result']} → verify: pending")
        elif node_name == "verify_result":
            # The verdict is stored in status after verification
            if node_state["status"] == "success":
                print(f"Попытка {attempts}: verify: success")
                break
            elif node_state["status"] == "failed":
                print(f"Попытка {attempts}: verify: failed")
            elif node_state["status"] == "max_attempts":
                print(f"Попытка {attempts}: reached max attempts")
                break
        elif node_name == "handle_error":
            # Nothing to print here – next execute_task will output the attempt number
            pass
    # Final summary
    final_status = node_state["status"]
    total_attempts = node_state["attempts"]
    print(f"Итог: {final_status} за {total_attempts} попытки")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        task_input = " ".join(sys.argv[1:])
    else:
        task_input = "Вычисли 2+2"
    main(task_input)
