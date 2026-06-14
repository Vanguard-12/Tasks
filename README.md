# LangGraph Reflection Agent

## Description

This project demonstrates a **LangGraph** agent that drafts a concise answer to a question, evaluates it with a separate reflection node, and rewrites the answer up to a configurable number of rounds until the reflection verdict is `ok`.

The workflow follows the diagram:

```
START → draft_answer → reflect
         ↑ ok → END
         needs_revision & round < max_rounds → rewrite → reflect
         otherwise → END
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a ```.env``` file (or copy ```.env.example```) and add your OpenAI API key:

```
OPENAI_API_KEY=sk-...
```

## Usage

```bash
python main.py "Объясни студенту разницу между tool и resource в MCP"
```

If you omit the question argument, the script will prompt you to type one.

## Expected Output

The script prints the draft answer, the critique, the verdict, and any rewritten drafts for each round, finally displaying the final answer.

## Files Overview

- **state.py** – TypedDict defining the graph state.
- **nodes.py** – Implementations of `draft_answer`, `reflect`, and `rewrite` nodes.
- **graph.py** – Construction of the LangGraph with conditional edges.
- **main.py** – CLI entry point that runs the graph.

## License

MIT
