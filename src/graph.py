from langgraph.graph import StateGraph
from src.state import ReflectState
from src.nodes import draft_answer, reflect, rewrite


def build_graph() -> StateGraph:
    graph = StateGraph(ReflectState)
    graph.add_node("draft_answer", draft_answer)
    graph.add_node("reflect", reflect)
    graph.add_node("rewrite", rewrite)

    graph.set_entry_point("draft_answer")
    graph.add_edge("draft_answer", "reflect")
    graph.add_conditional_edges(
        "reflect",
        lambda state: "rewrite" if state["verdict"] == "needs_revision" and state["round"] < state["max_rounds"] else "END",
    )
    graph.add_edge("rewrite", "reflect")
    return graph
