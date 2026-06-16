import argparse
import asyncio
import os
import logging
from typing import Dict, Any

from dotenv import load_dotenv

from .graph import get_compiled_graph

# Load environment variables from .env if present
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


async def run_workflow(question: str, max_rounds: int) -> Dict[str, Any]:
    """Execute the reflection graph for a single question.

    Returns the final state dictionary.
    """
    # Initialise the state – the graph will fill the rest
    initial_state: Dict[str, Any] = {
        "question": question,
        "draft": "",
        "critique": "",
        "verdict": "",
        "round": 0,
        "max_rounds": max_rounds,
    }
    graph = get_compiled_graph(max_rounds=max_rounds)
    # ``ainvoke`` runs the graph asynchronously and yields the final state
    final_state = await graph.ainvoke(initial_state)
    return final_state


def pretty_print(state: Dict[str, Any]):
    print("\n=== Final Result ===")
    print(f"Question: {state.get('question')}")
    print(f"Rounds performed: {state.get('round')}")
    print("\nFinal draft answer:\n")
    print(state.get("draft"))
    print("\n--- End of answer ---\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph reflection demo")
    parser.add_argument(
        "--question",
        type=str,
        help="Question to answer. If omitted, you will be prompted interactively.",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=2,
        help="Maximum number of rewrite attempts (default: 2).",
    )
    args = parser.parse_args()

    question = args.question
    if not question:
        question = input("Enter the question: ").strip()
    if not question:
        raise ValueError("A non‑empty question is required.")

    logger.info("Starting reflection workflow for question: %s", question)
    final_state = asyncio.run(run_workflow(question, args.max_rounds))
    pretty_print(final_state)


if __name__ == "__main__":
    main()
