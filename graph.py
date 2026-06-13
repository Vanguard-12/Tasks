from typing import Dict
from langgraph.graph import StateGraph, END
from state import CodeReviewState
from nodes.draft_review import draft_review
from nodes.reflect import reflect
from nodes.rewrite import rewrite


def build_graph() -> StateGraph:
    """Construct the LangGraph according to the specification.

    Returns a ``StateGraph`` instance ready to be compiled.
    """
    graph = StateGraph(CodeReviewState)

    # Register nodes
    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Define edges
    graph.add_edge("__start__", "draft_review")
    graph.add_edge("draft_review", "reflect")

    # Conditional routing from reflect
    def route(state: Dict) -> str:
        if state["verdict"] == "ok":
            return END
        if state["verdict"] == "needs_revision" and state["round"] < state["max_rounds"]:
            return "rewrite"
        # Either max rounds reached or unknown verdict – terminate
        return END

    graph.add_conditional_edges("reflect", route, {"rewrite": "rewrite", END: END})
    graph.add_edge("rewrite", "reflect")

    # Set default values for fields that may be missing in the initial dict
    graph.set_entry_point("draft_review")
    return graph
