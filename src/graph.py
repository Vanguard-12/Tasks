import os
from typing import Any, Dict
from langgraph.graph import StateGraph, END, START
from .state import CompareState
from .nodes.compare import (
    plan_criteria,
    research_entity,
    build_table,
    verdict,
)

# ---------------------------------------------------------------------------
# Graph definition
# ---------------------------------------------------------------------------

def build_compare_graph() -> StateGraph:
    """Construct the LangGraph workflow for the comparison task.

    The graph follows the structure described in the assignment:
    START → plan_criteria → research_entity (loop) → build_table → verdict → END
    """
    graph = StateGraph(CompareState)

    # Register nodes
    graph.add_node("plan_criteria", plan_criteria)
    graph.add_node("research_entity", research_entity)
    graph.add_node("build_table", build_table)
    graph.add_node("verdict", verdict)

    # Define edges
    graph.add_edge(START, "plan_criteria")
    graph.add_edge("plan_criteria", "research_entity")

    # Conditional edge for the research loop
    def has_more_pairs(state: CompareState) -> str:
        entities = state["entities"]
        criteria = state["criteria"]
        total = len(entities) * len(criteria)
        return "research_entity" if state.get("pair_index", 0) < total else "build_table"

    graph.add_conditional_edges(
        "research_entity",
        has_more_pairs,
        {"research_entity": "research_entity", "build_table": "build_table"},
    )

    graph.add_edge("build_table", "verdict")
    graph.add_edge("verdict", END)

    return graph

# Compile the graph once so that ``invoke`` can be used directly.
compare_graph = build_compare_graph().compile()
