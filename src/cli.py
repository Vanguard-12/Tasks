import argparse
import os
import sys
from typing import List
from .graph import compare_graph
from .state import CompareState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="LangGraph comparison demo – compare three entities using Tavily web search."
    )
    parser.add_argument(
        "entities",
        nargs="*",
        help="Three entities to compare. If omitted, defaults to Chroma, FAISS, Qdrant.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.entities:
        if len(args.entities) != 3:
            print("Please provide exactly three entities, or none to use the default set.")
            sys.exit(1)
        entities: List[str] = args.entities
    else:
        entities = ["Chroma", "FAISS", "Qdrant"]

    # Initialise the state
    initial_state: CompareState = {
        "entities": entities,
        "criteria": [],
        "findings": {},
        "final_table": None,
        "verdict": None,
        "pair_index": 0,
    }

    try:
        final_state = compare_graph.invoke(initial_state)
    except Exception as exc:
        print(f"\n❌ An error occurred while running the workflow: {exc}\n")
        sys.exit(1)

    # Output results
    print("\n=== Generated Comparison Criteria ===")
    for i, crit in enumerate(final_state.get("criteria", []), 1):
        print(f"{i}. {crit}")

    print("\n=== Findings (entity × criterion) ===")
    findings = final_state.get("findings", {})
    for entity, notes in findings.items():
        print(f"\n--- {entity} ---")
        for crit, note in zip(final_state.get("criteria", []), notes):
            print(f"* {crit}: {note}")

    print("\n=== Final Comparison Table ===\n")
    print(final_state.get("final_table", "[No table generated]"))

    print("\n=== Verdict ===\n")
    print(final_state.get("verdict", "[No verdict generated]"))


if __name__ == "__main__":
    main()
