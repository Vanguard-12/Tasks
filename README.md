# Research Brief Agent (LangGraph)

## Overview

This repository contains a **LangGraph**‑based agent that builds a short research brief (about half a page to one page) for a student‑provided topic.

The workflow is:

1. **Outline generation** – an LLM creates a 4‑5 item outline.
2. **Iterative research** – for each outline point the agent makes **one** Tavily web‑search call, summarises the results into a concise note (5‑8 sentences).
3. **Synthesis** – all notes are combined into a coherent brief with headings.

The implementation follows the specification from the assignment "Повторный экзамен: Исследовательский бриф (план → шаги → сводка)".

---

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd <repo-directory>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment variables

Create a copy of the example file and fill in your keys:

```bash
cp .env.example .env
```

The script expects the following variables:

- `OPENAI_API_KEY` – API key for the OpenAI model used for generation and summarisation.
- `OPENAI_MODEL` *(optional)* – model name (default: `gpt-4o-mini`).
- `TAVILY_API_KEY` – API key for Tavily web‑search.

---

## Running the agent

```bash
python brief_agent.py "Your custom research topic"
```

If no topic is supplied, the default topic from the assignment is used:

```
Как студенту безопасно подключать MCP к LangChain
```

The script prints:

- The generated outline.
- Each research step note prefixed with `[Step i]`.
- The final synthesized brief.

---

## Files

- `brief_agent.py` – main script containing the state definition, graph construction, node implementations and a CLI entry point.
- `requirements.txt` – Python dependencies.
- `README.md` – this documentation.
- `.env.example` – template for required environment variables.

---

## Notes & Limitations

- The agent uses **real** Tavily search results; no fabricated references are introduced.
- If the LLM or Tavily APIs are unavailable, the script exits with a clear error message.
- The outline parsing uses a simple ``eval`` on the LLM response; the prompt forces a JSON‑compatible list to keep parsing safe.

---

## License

MIT License (c) 2026
