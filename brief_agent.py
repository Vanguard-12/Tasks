"""Entry‑point script for the LangGraph research‑brief agent.

Run the script with a valid ``TAVILY_API_KEY`` (and optionally an OpenAI API key)
present in a ``.env`` file. The script demonstrates the full pipeline:

1. Generate an outline for a default topic.
2. Iteratively research each outline point (one Tavily call per step).
3. Synthesize the collected notes into a short, coherent brief.

The output is printed to the console.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from a .env file in the project root
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_TOPIC = (
    "Как студенту безопасно подключать MCP к LangChain"
)

# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
def main() -> None:
    from brief.graph import app

    # Prepare the initial state – only the topic is required
    inputs = {"topic": os.getenv("BRIEF_TOPIC", DEFAULT_TOPIC)}

    # Run the graph; ``invoke`` returns the final state after all edges are
    # traversed.
    final_state = app.invoke(inputs)

    # -------------------------------------------------------------------
    # Pretty‑print the results
    # -------------------------------------------------------------------
    outline = final_state.get("outline", [])
    notes = final_state.get("notes", [])
    brief = final_state.get("final_brief", "")

    print("\n=== GENERATED OUTLINE ===")
    for i, point in enumerate(outline, 1):
        print(f"{i}. {point}")

    print("\n=== RESEARCH NOTES ===")
    for i, note in enumerate(notes, 1):
        print(f"[Шаг {i}] {note}\n")

    print("\n=== FINAL BRIEF ===\n")
    print(brief)


if __name__ == "__main__":
    main()
