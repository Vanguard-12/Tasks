from typing import Dict
from state import CodeReviewState
from graph import build_graph


def run_demo() -> None:
    """Run the LangGraph demo on a sample function.

    The demo prints each step (draft, critic scores, possible rewrites) and the final verdict.
    """
    # Sample function to review
    sample_code = """
def sort_numbers(arr):
    return sorted(arr)
"""

    # Initialise the workflow state
    initial_state: CodeReviewState = {
        "code": sample_code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,
        "max_rounds": 2,
    }

    graph = build_graph()
    # Compile the graph into a runnable object
    app = graph.compile()
    # Execute the graph – it will mutate the state and print logs inside nodes
    final_state: Dict = app.invoke(initial_state)

    print("\n=== Final Result ===")
    print(f"Final draft review (round {final_state['round']}):")
    print(final_state["draft_review"])
    print("Scores:")
    for crit, score in final_state.get("criteria_scores", {}).items():
        print(f"  {crit}: {score}")
    print(f"Verdict: {final_state.get('verdict', 'unknown')}")


if __name__ == "__main__":
    run_demo()
