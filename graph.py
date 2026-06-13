from typing import Dict, Any

from langgraph.graph import StateGraph, END

from compare_state import CompareState
from nodes import plan_criteria, research_entity, build_table, verdict

# ---------------------------------------------------------------------------
# Build the LangGraph workflow.
# ---------------------------------------------------------------------------

def create_comparison_graph() -> StateGraph:
    graph = StateGraph(CompareState)

    # Register node functions.
    graph.add_node("plan_criteria", plan_criteria)
    graph.add_node("research_entity", research_entity)
    graph.add_node("build_table", build_table)
    graph.add_node("verdict", verdict)

    # Define the edges.
    graph.add_edge("START", "plan_criteria")
    graph.add_edge("plan_criteria", "research_entity")

    # Conditional edge for the research loop.
    def more_pairs(state: Dict[str, Any]) -> str:
        entities = state["entities"]
        criteria = state["criteria"]
        total = len(entities) * len(criteria)
        return "research_entity" if state.get("current_pair", 0) < total else "build_table"

    graph.add_conditional_edges(
        "research_entity",
        more_pairs,
        {
            "research_entity": "research_entity",  # continue looping
            "build_table": "build_table",
        },
    )

    graph.add_edge("build_table", "verdict")
    graph.add_edge("verdict", END)

    return graph

# Compile the graph for external use.
comparison_graph = create_comparison_graph()
