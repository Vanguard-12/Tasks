from typing import Dict, Any

from langgraph.graph import StateGraph, END

from .state import BriefState
from .nodes import outline, research_step, synthesize

# ---------------------------------------------------------------------------
# Build the LangGraph workflow
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    graph = StateGraph(BriefState)

    # Register nodes
    graph.add_node("outline", outline)
    graph.add_node("research_step", research_step)
    graph.add_node("synthesize", synthesize)

    # Define the flow
    graph.set_entry_point("outline")
    graph.add_edge("outline", "research_step")

    # Conditional edge: continue researching while there are remaining outline items
    def _next(state: Dict[str, Any]) -> str:
        # ``step_index`` is incremented after each research_step
        if state["step_index"] >= len(state["outline"]):
            return "synthesize"
        else:
            return "research_step"

    graph.add_conditional_edges("research_step", _next)
    graph.add_edge("synthesize", END)

    return graph

# Compile the graph once so it can be imported elsewhere
app = build_graph().compile()
