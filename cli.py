import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from review_state import CodeReviewState
from graph import build_graph

load_dotenv()

# Sample function to be reviewed
SAMPLE_CODE = """
def sort_numbers(arr):
    \"\"\"Return a sorted list of numbers.\"\"\"
    return sorted(arr)
"""

def main() -> None:
    # Initial state вЂ“ note that ``round`` starts at 0 and ``max_rounds`` defaults to 2
    init_state: CodeReviewState = {
        "code": SAMPLE_CODE,
        "round": 0,
        "max_rounds": int(os.getenv("MAX_ROUNDS", "2")),
    }

    graph = build_graph()
    # Compile the graph into a runnable runnable (sync for simplicity)
    app = graph.compile()

    # Run the graph вЂ“ ``invoke`` returns the final state
    final_state: Dict[str, Any] = app.invoke(init_state)

    # PrettyвЂ‘print the journey
    print("\n=== CODE TO REVIEW ===\n")
    print(SAMPLE_CODE)
    print("\n=== INITIAL DRAFT REVIEW ===\n")
    print(final_state.get("draft_review", "<no draft>") )
    print("\n=== CRITIC SCORES ===\n")
    scores = final_state.get("criteria_scores", {})
    print(json.dumps(scores, indent=2))
    print("Weakest criterion:", final_state.get("weakest_criterion"))
    print("Verdict:", final_state.get("verdict"))
    if final_state.get("round", 0) > 0:
        print("\n=== REWRITTEN REVIEW (after", final_state["round"], "round(s)) ===\n")
        print(final_state.get("draft_review"))
        print("\n=== UPDATED SCORES ===\n")
        print(json.dumps(final_state.get("criteria_scores", {}), indent=2))

if __name__ == "__main__":
    main()

