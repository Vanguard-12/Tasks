from typing import Dict

from langgraph.graph import StateGraph, END

from .state import CodeReviewState
from .nodes.draft_review import draft_review
from .nodes.reflect import reflect
from .nodes.rewrite import rewrite


def build_graph() -> StateGraph:
    """Construct and compile the LangGraph workflow.

    Returns a compiled ``StateGraph`` ready to be invoked.
    """
    graph = StateGraph(CodeReviewState)

    # Register nodes
    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Entry point
    graph.set_entry_point("draft_review")

    # Linear edge draft -> reflect
    graph.add_edge("draft_review", "reflect")

    # Conditional routing after reflect
    def route(state: Dict) -> str:
        verdict = state.get("verdict", "needs_revision")
        current_round = state.get("round", 0)
        max_rounds = state.get("max_rounds", 2)
        if verdict == "ok":
            return END
        if current_round < max_rounds:
            return "rewrite"
        return END

    graph.add_conditional_edges("reflect", route, {"rewrite": "rewrite", END: END})

    # After rewrite go back to reflect
    graph.add_edge("rewrite", "reflect")

    compiled = graph.compile()
    return compiled
