from typing import Dict

from langgraph.graph import StateGraph, END, START

from state import ReflectState
from nodes import draft_answer, reflect, rewrite

def build_graph(max_rounds: int = 2) -> StateGraph:
    """Construct the LangGraph with conditional edges for reflection/rewrite loop."""
    graph = StateGraph(ReflectState)

    # Register nodes
    graph.add_node("draft", draft_answer)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Define the flow
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "reflect")

    # Conditional edge from reflect based on verdict and round count
    def reflect_next(state: Dict) -> str:
        if state.get("verdict") == "ok":
            return END
        # needs_revision
        if state.get("round", 0) < state.get("max_rounds", max_rounds):
            return "rewrite"
        return END

    graph.add_conditional_edges("reflect", reflect_next, {"rewrite": "rewrite", END: END})
    graph.add_edge("rewrite", "reflect")

    # Set default values for the state (these can be overridden at runtime)
    graph.set_entry_point("draft")
    return graph
