import argparse
import os
import sys
from typing import List, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph

from compare_state import CompareState
from graph import comparison_graph

# ---------------------------------------------------------------------------
# Helper to pretty‑print sections.
# ---------------------------------------------------------------------------

def _print_section(title: str, content: str) -> None:
    separator = "=" * len(title)
    print(f"\n{separator}\n{title}\n{separator}\n{content}\n")

# ---------------------------------------------------------------------------
# Main entry point.
# ---------------------------------------------------------------------------

def main() -> None:
    load_dotenv()  # loads .env if present

    parser = argparse.ArgumentParser(description="LangGraph comparison demo using Tavily.")
    parser.add_argument(
        "--custom",
        nargs=3,
        metavar="ENTITY",
        help="Provide three custom entities to compare (overrides the default list).",
    )
    args = parser.parse_args()

    default_entities = ["Chroma", "FAISS", "Qdrant"]
    entities: List[str] = args.custom if args.custom else default_entities

    # Basic validation – we need exactly three entities.
    if len(entities) != 3:
        print("Error: exactly three entities must be supplied.", file=sys.stderr)
        sys.exit(1)

    # Initialise the graph state.
    initial_state: CompareState = {
        "entities": entities,
        "criteria": [],
        "findings": {},
        "current_pair": 0,
        "final_table": None,
        "verdict": None,
    }

    # Run the compiled graph.
    try:
        result: Dict[str, Any] = comparison_graph.compile().invoke(initial_state)
    except Exception as exc:
        print(f"Execution failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Extract and display the artefacts.
    criteria: List[str] = result.get("criteria", [])
    _print_section("Generated Comparison Criteria", "\n".join(f"- {c}" for c in criteria))

    # Show each finding as it was produced (the state already contains the full matrix).
    findings: Dict[str, List[str]] = result.get("findings", {})
    for entity in entities:
        notes = findings.get(entity, [])
        for crit, note in zip(criteria, notes):
            _print_section(f"Finding – {entity} × {crit}", note)

    table = result.get("final_table", "")
    _print_section("Comparison Table (Markdown)", table)

    verdict_text = result.get("verdict", "")
    _print_section("Verdict", verdict_text)


if __name__ == "__main__":
    main()
