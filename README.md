# LangGraph Code Review Agent

This repository contains a **LangGraph** based agent that performs a code review of a given Python function, evaluates the review against four criteria (PEP8, type‑hints, edge cases, naming) and iteratively rewrites the weakest part of the review until the critic is satisfied or a maximum number of rounds is reached.

## Features

- **Draft review** node – generates a short bullet‑point review.
- **Reflect** node – a critic that scores the review on four criteria and decides whether a rewrite is needed.
- **Rewrite** node – improves the part of the review that received the lowest score.
- Loop with a configurable `max_rounds` (default = 2).
- Simple CLI for quick demos.

## Installation

```bash
git clone <repo-url>
cd <repo-dir>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file from the example and add your OpenAI API key (or configure Ollama):

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY=your-key
```

## Usage

```bash
python -m src.cli "def sort_numbers(arr):\n    return sorted(arr)"
```

The CLI prints:

1. The initial draft review.
2. Scores for each criterion, the weakest criterion and the verdict.
3. Any rewritten sections (if the critic requested a revision).
4. The final review and verdict.

## Project Structure

- `src/state.py` – definition of the `CodeReviewState` TypedDict.
- `src/nodes/` – implementations of the three graph nodes.
- `src/graph.py` – builds and compiles the LangGraph workflow.
- `src/cli.py` – entry point for the command‑line demo.
- `src/utils.py` – helper functions (prompt templating, safe JSON parsing).

## License

MIT
