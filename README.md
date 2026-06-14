# LangGraph Research Brief Agent

## Overview

This repository contains a **LangGraph**‑based agent that, given a topic, produces a short research brief (≈½–1 page). The workflow is:

1. **Outline** – an LLM generates a 4‑5 item research outline.
2. **Iterative research** – for each outline point the agent makes **one** Tavily web‑search call, summarises the results into a concise note (5‑8 sentences), and stores the note.
3. **Synthesis** – all notes are combined into a coherent brief with headings.

The demo runs entirely from the command line and prints:
- the generated outline,
- each step’s note prefixed with `[Шаг i]`,
- the final brief.

## Setup

```bash
# 1. Clone the repo and cd into it
git clone <repo‑url>
cd <repo‑dir>

# 2. (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

Create a ```.env``` file in the project root with the required API keys:

```
TAVILY_API_KEY=your_tavily_key_here
OPENAI_API_KEY=your_openai_key_here   # omit if you prefer Ollama
```

> **Note** – If you prefer a local Ollama model, replace the OpenAI imports in ``brief_agent.py`` with the Ollama equivalents and set ``OLLAMA_BASE_URL`` in ``.env``.

## Usage

```bash
python brief_agent.py "Как студенту безопасно подключать MCP к LangChain"
```

If no topic is supplied, the default topic from the assignment is used.

The script will output something like:

```
Outline:
1. Обзор MCP и его возможностей
2. Требования к безопасности при работе с MCP
3. Лучшие практики аутентификации и авторизации
4. Интеграция MCP с LangChain: шаги и подводные камни
5. Тестирование и мониторинг безопасности

[Шаг 1] …
[Шаг 2] …
[Шаг 3] …
[Шаг 4] …
[Шаг 5] …

Final Brief:
<coherent ½‑1 page text>
```

## Project Structure

```
brief_agent.py   # main script – state definition, nodes, graph, demo
requirements.txt # Python dependencies
README.md        # this file
.tests/          # optional test suite (run with pytest)
.env             # (not committed) – API keys
```

## Testing (optional)

A minimal test suite is provided under ``tests/test_agent.py``. Run it with:

```bash
pytest
```

## License

MIT License.
