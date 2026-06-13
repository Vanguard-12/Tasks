# LangGraph Code Review with Reflexive Critic

## Overview

This repository demonstrates a **LangGraph** workflow that performs a code review of a Python function, evaluates the review on four concrete criteria (PEP8, type‑hints, edge cases, naming), and iteratively rewrites the weakest part of the review until the critic is satisfied or a configurable number of rounds is reached.

The workflow consists of three nodes:

1. **draft_review** – generates an initial 3‑6 bullet review of the supplied code.
2. **reflect** – a critic LLM scores the review on the four criteria, picks the lowest‑scoring criterion, and decides whether the review is good enough (`"ok"`) or needs another revision (`"needs_revision"`).
3. **rewrite** – improves only the portion of the review that corresponds to the weakest criterion and increments the round counter.

The graph loops `reflect → rewrite → reflect` until the verdict is `"ok"` or the maximum number of rounds (`max_rounds`, default = 2) is exhausted.

## Project Structure

```
.
├─ app.py               # entry point – builds the graph and runs the demo
├─ state.py             # TypedDict defining the workflow state
├─ utils.py             # helpers for env loading and LLM client creation
├─ nodes/
│   ├─ draft_review.py
│   ├─ reflect.py
│   └─ rewrite.py
├─ graph.py             # LangGraph construction
├─ cli.py               # tiny CLI wrapper (optional)
├─ requirements.txt
├─ .env.example
└─ README.md
```

## Setup

```bash
# 1. Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the example env file and fill in your credentials
cp .env.example .env
# Edit .env – set either OPENAI_API_KEY or OLLAMA_BASE_URL
```

## Running the Demo

```bash
python app.py
```

You should see a step‑by‑step log similar to:

```
--- Draft Review ---
* The function is simple and correct …
* Missing type hints …
* Naming could be clearer …

--- Critic Scores ---
pep8: 8, type_hints: 3, edge_cases: 7, naming: 6
Weakest criterion: type_hints
Verdict: needs_revision

--- Rewrite (type_hints) ---
* Added type hints …

--- New Scores ---
pep8: 9, type_hints: 8, edge_cases: 7, naming: 6
Verdict: ok
```

If the critic still asks for a revision and the round counter is below `max_rounds`, another rewrite will be performed.

## How It Works

* **state.py** – defines `CodeReviewState` (TypedDict) with fields required by the spec.
* **utils.py** – loads environment variables and creates a LangChain chat model (`ChatOpenAI` or `ChatOllama`).
* **nodes/** – each file implements a LangGraph node function that receives the current state, calls the LLM, updates the state, and prints a short log.
* **graph.py** – builds a `StateGraph` with conditional edges based on `verdict` and `round`.
* **app.py** – prepares the initial state (sample function `sort_numbers`), compiles the graph, runs it, and prints the final outcome.

## Extending the Project

* Swap the LLM provider by adjusting `utils.get_llm()`.
* Add more criteria or richer prompts.
* Persist the review history to a file or database.

---

*Happy coding!*