# LangGraph Code‑Review with Reflexive Critic

This repository contains a **LangGraph** based agent that reviews a Python function, evaluates the review against four concrete criteria (PEP8, type‑hints, edge cases, naming) and iteratively rewrites the weakest part of the review until the critic is satisfied or a maximum number of rounds is reached.

## Features

* **State model** – `CodeReviewState` stores the original code, the draft review, per‑criterion scores, the weakest criterion, a verdict, and round counters.
* **Three nodes**
  * `draft_review` – generates an initial 3‑6 bullet‑point review.
  * `reflect` – a critic that scores the draft on the four criteria and decides whether a revision is needed.
  * `rewrite` – rewrites only the part of the review that corresponds to the weakest criterion.
* **Loop** – `rewrite → reflect` repeats until the verdict is `ok` or `max_rounds` (default 2) is hit.
* **CLI demo** – runs the graph on a sample function and prints the whole interaction.

## Setup

```bash
# 1. Clone the repo
git clone <repo‑url>
cd <repo‑directory>

# 2. Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure API credentials
cp .env.example .env
#   - For OpenAI: set OPENAI_API_KEY
#   - For a local Ollama model: set OLLAMA_BASE_URL (e.g. http://localhost:11434/v1)

# 4. Run the demo
python cli.py
```

## Expected output (truncated for brevity)

```
=== CODE TO REVIEW ===

def sort_numbers(arr):
    """Return a sorted list of numbers."""
    return sorted(arr)

=== INITIAL DRAFT REVIEW ===

- The function is simple and correctly uses ``sorted``.
- No type hints are provided for the parameter or return value.
- The name ``sort_numbers`` is clear.
- No explicit handling of non‑list inputs or empty lists.
- PEP8 formatting looks fine.

=== CRITIC SCORES ===
{
  "pep8": 9,
  "type_hints": 3,
  "edge_cases": 5,
  "naming": 8
}
Weakest criterion: type_hints
Verdict: needs_revision

=== REWRITTEN REVIEW (after 1 round(s)) ===

- The function is simple and correctly uses ``sorted``.
- **Add type hints**: ``def sort_numbers(arr: list[int]) -> list[int]:``.
- The name ``sort_numbers`` is clear.
- No explicit handling of non‑list inputs or empty lists.
- PEP8 formatting looks fine.

=== UPDATED SCORES ===
{
  "pep8": 9,
  "type_hints": 8,
  "edge_cases": 5,
  "naming": 8
}
```

The critic upgraded the *type_hints* score after the rewrite, and because all scores are now ≥ 7 the verdict becomes `ok` and the graph terminates.

## Customisation

* **Change the maximum number of rounds** – set the environment variable `MAX_ROUNDS` before running the CLI.
* **Swap the LLM** – the code automatically picks OpenAI when `OPENAI_API_KEY` is present, otherwise it falls back to an Ollama endpoint.
* **Provide your own code** – modify `SAMPLE_CODE` in `cli.py` or build a small wrapper that reads a file.

## License

MIT License – feel free to adapt and extend.
