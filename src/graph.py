from langgraph.graph import StateGraph, END
from .agent_state import AgentState
from .nodes import execute_task, verify_result, handle_error

def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    # Register node functions
    graph.add_node("execute_task", execute_task)
    graph.add_node("verify_result", verify_result)
    graph.add_node("handle_error", handle_error)

    # Define edges
    graph.add_edge("execute_task", "verify_result")

    # Conditional routing after verification
    def route(state: AgentState):
        if state["status"] == "success":
            return END
        if state["status"] == "failed":
            if state["attempts"] < state["max_attempts"]:
                return "handle_error"
            else:
                return END
        # Any other status (e.g., pending) – continue execution
        return "execute_task"

    graph.add_conditional_edges("verify_result", route, {
        "handle_error": "handle_error",
        END: END,
        "execute_task": "execute_task",
    })

    graph.add_edge("handle_error", "execute_task")

    # Set entry point
    graph.set_entry_point("execute_task")
    return graph
