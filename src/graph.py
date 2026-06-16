import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END, START

from .state import ReflectState
from .nodes import draft_answer, reflect, rewrite

logger = logging.getLogger(__name__)


def build_reflection_graph(max_rounds: int = 2) -> StateGraph:
    """Construct the LangGraph for the reflection workflow.

    Parameters
    ----------
    max_rounds: int, optional
        Upper bound for the number of rewrite attempts. Defaults to 2.
    """
    graph = StateGraph(ReflectState)

    # Register nodes
    graph.add_node("draft_answer", draft_answer)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    # Define edges
    graph.add_edge(START, "draft_answer")
    graph.add_edge("draft_answer", "reflect")

    # Conditional edge from reflect based on verdict and round count
    def decide_next(state: Dict[str, Any]):
        verdict = state.get("verdict")
        current_round = state.get("round", 0)
        logger.info("Deciding next step – verdict: %s, round: %s", verdict, current_round)
        if verdict == "ok":
            return END
        if verdict == "needs_revision" and current_round < state.get("max_rounds", max_rounds):
            return "rewrite"
        # Any other case – terminate to avoid infinite loops
        return END

    graph.add_conditional_edges("reflect", decide_next, {"rewrite": "rewrite", END: END})
    graph.add_edge("rewrite", "reflect")

    # Set default values for the initial state (except question which is supplied by the caller)
    graph.set_entry_point(START)
    return graph


def get_compiled_graph(max_rounds: int = 2):
    """Convenience wrapper that returns a compiled graph ready for execution."""
    graph = build_reflection_graph(max_rounds=max_rounds)
    return graph.compile()
