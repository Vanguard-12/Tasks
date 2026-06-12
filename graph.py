from typing import Dict, Any
from langgraph.graph import StateGraph, END
from review_state import CodeReviewState
from nodes import draft_review, reflect, rewrite


def build_graph() -> StateGraph:
    """Construct the LangGraph for the code‑review workflow.

    The graph follows the specification:
        START → draft_review → reflect
        if verdict == "ok" → END
        if verdict == "needs_revision" and round < max_rounds → rewrite → reflect
        else → END
    """
    graph = StateGraph(CodeReviewState)

    # Register nodes
    graph.add_node("draft_review", draft_review)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Define edges
    graph.add_edge("START", "draft_review")
    graph.add_edge("draft_review", "reflect")

    # Conditional edge after reflect
    def decide_next(state: Dict[str, Any]):
        verdict = state.get("verdict")
        current_round = state.get("round", 0)
        max_rounds = state.get("max_rounds", 2)
        if verdict == "ok":
            return "END"
        if verdict == "needs_revision" and current_round < max_rounds:
            return "rewrite"
        return "END"

    graph.add_conditional_edges(
        "reflect",
        decide_next,
        {
            "rewrite": "rewrite",
            "END": END,
        },
    )

    # After rewrite go back to reflect
    graph.add_edge("rewrite", "reflect")

    # Set default values for the initial state (will be merged with user‑provided state)
    graph.set_entry_point("draft_review")
    return graph
