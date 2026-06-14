import sys
import os
from pathlib import Path

from dotenv import load_dotenv

from .graph import build_graph
from .state import CodeReviewState


def main() -> None:
    load_dotenv()  # loads OPENAI_API_KEY or OLLAMA_BASE_URL if present
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli \"<python function code>\"")
        sys.exit(1)
    # The function code can be passed directly or as a path prefixed with @
    arg = sys.argv[1]
    if arg.startswith("@"):  # file reference
        file_path = Path(arg[1:])
        if not file_path.is_file():
            print(f"File not found: {file_path}")
            sys.exit(1)
        code = file_path.read_text()
    else:
        code = arg

    # Initial state
    init_state: CodeReviewState = {
        "code": code,
        "draft_review": "",
        "criteria_scores": {},
        "weakest_criterion": "",
        "verdict": "",
        "round": 0,
        "max_rounds": 2,
    }

    graph = build_graph()
    print("\n=== Starting LangGraph Code Review ===\n")
    final_state = graph.invoke(init_state)
    print("\n=== Final Verdict ===")
    print("Verdict:", final_state.get("verdict"))
    print("Final Review:\n", final_state.get("draft_review"))


if __name__ == "__main__":
    main()
