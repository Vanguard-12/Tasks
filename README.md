# LangGraph Reflection Demo

This repository contains a small **LangGraph** based agent that:

1. **Drafts** a concise answer (5‑10 sentences) to a user‑provided question.
2. Sends the draft to a **reflection** node that critiques the answer and returns a verdict (`ok` or `needs_revision`).
3. If the verdict is `needs_revision` **and** the maximum number of revision rounds has not been reached, a **rewrite** node rewrites the answer using the critique.
4. The loop repeats until the answer is approved or `max_rounds` (default 2) is exhausted.

The whole workflow is expressed as a LangGraph, so the control flow is handled by graph edges – **no try/except retry logic** is used.

---

## Installation

```bash
# Clone the repo and cd into it
git clone <repo-url>
cd <repo-dir>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment variables

Copy the example file and fill in the required key(s):

```bash
cp .env.example .env
```

- **OpenAI** – set `OPENAI_API_KEY`.
- **Ollama** – if you prefer a local model, set `OLLAMA_HOST` (e.g., `http://localhost:11434`). The code will automatically pick Ollama when the OpenAI key is missing.

---

## Usage

Run the CLI entry point:

```bash
python -m src.main --question "Объясни студенту разницу между tool и resource в MCP" --max-rounds 2
```

If you omit `--question`, the program will ask you to type one interactively.

### What you will see

For each round the program prints:

- **Draft** – the current answer.
- **Critique** – the reflection node’s feedback.
- **Verdict** – `ok` or `needs_revision`.
- **Round number**.

When the loop finishes, the final answer (the last draft) is printed.

---

## Project structure

```
src/
├─ __init__.py          # makes src a package
├─ state.py             # TypedDict describing the graph state
├─ nodes.py             # async node implementations (draft, reflect, rewrite)
├─ graph.py             # builds the StateGraph with conditional edges
└─ main.py              # CLI wrapper that runs the compiled graph
```

---

## How it works

1. **State definition** – `ReflectState` (see `src/state.py`).
2. **Nodes** – each node receives the current state, calls an LLM, and returns an updated state.
   * `draft_answer` – creates the first answer.
   * `reflect` – asks the LLM to evaluate the draft and to output a JSON object with a `verdict` and a short `critique`.
   * `rewrite` – rewrites the draft using the critique and increments the round counter.
3. **Graph** – built with `StateGraph(ReflectState)`. Edges are conditional on `state["verdict"]` and `state["round"]`.
4. **Execution** – the compiled graph is invoked with an initial state containing the question and `max_rounds`.

---

## License

MIT License
