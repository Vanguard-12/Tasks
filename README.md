# Structured Output – Union Events Demo

This repository contains a small demonstration of **LangChain structured output** together with **Pydantic v2 discriminated unions**.

## What it does

- Takes a raw log (multiple lines, each line can be a successful request or an error).
- Sends every line to an LLM (OpenAI compatible) with `with_structured_output` so the model returns JSON that matches a Pydantic schema.
- The schema is a **union** of two models (`HttpOkEvent` and `HttpErrorEvent`) discriminated by the field `kind`.
- The CLI prints the parsed events as a nice table.

## Project structure

```
event_models.py   # Pydantic models + discriminated union
event_parser.py   # Split log, call LLM, return list[ApiEvent]
event_cli.py      # Simple CLI that uses the parser and prints a table
README.md         # This file
```

## Installation

```bash
# Clone the repo (if you haven't already)
git clone <repo-url>
cd <repo-directory>

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

The `requirements.txt` already contains:

- `langchain-core`
- `langchain-openai` (or any other LangChain provider you prefer)
- `pydantic>=2`
- `python-dotenv`
- `tabulate`

## Configuration

Create a `.env` file (you can copy from `.env.example`) and set your OpenAI API key:

```
OPENAI_API_KEY=sk-...
# Optional – change the model used by the demo
OPENAI_MODEL=gpt-3.5-turbo
```

The demo works with any OpenAI‑compatible endpoint; if you use a local Ollama
server, set the appropriate environment variables as described in the LangChain
documentation.

## Running the demo

### Using the built‑in example log

```bash
python -m event_cli
```

You should see a table similar to:

```
| kind   | path          |   status |   duration_ms | error_message   |
|--------|---------------|----------|---------------|-----------------|
| ok     | /api/users    |      200 |           123 |                 |
| error  | /api/unknown  |      404 |               | Not Found       |
| error  | /api/create   |      500 |               | Internal Server Error |
```

### Providing your own log

```bash
python -m event_cli --log "200 GET /api/users 123ms\n404 GET /api/unknown Not Found"
```

The `--log` argument can contain any number of lines separated by newlines.  Lines
can also be separated by the delimiter `---` – the parser treats both uniformly.

## How it works under the hood

1. **Splitting** – `event_parser.split_log` breaks the raw text into individual
   non‑empty lines.
2. **Prompt** – a tiny prompt tells the LLM to return JSON that matches the
   schema.
3. **Structured output** – `ChatOpenAI.with_structured_output(ApiEvent)` makes the
   LLM response automatically validated against the discriminated union.
4. **CLI** – the CLI collects the validated models, calls `model_dump()` to get a
   plain dictionary and prints a table with `tabulate`.

## License

This demo is provided under the MIT License.
# Research Brief Agent (LangGraph)

This repository contains a small **LangGraph**‑based agent that builds a short research brief for a student‑provided topic.

## What the agent does
1. **Outline generation** – an LLM creates a 4‑5 item outline for the topic.
2. **Iterative research** – for each outline point the agent performs **one** Tavily web‑search and summarises the results into a 5‑8 sentence note.
3. **Synthesis** – all notes are combined into a coherent brief (≈½‑1 page) with headings.

The whole pipeline is demonstrated by the `brief_agent.py` script.

---

## Installation
```bash
git clone <repo‑url>
cd <repo‑directory>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Create a `.env` file in the project root with the required API keys:
```
TAVILY_API_KEY=your_tavily_key_here
OPENAI_API_KEY=your_openai_key_here   # optional if you use OpenAI
```
If you prefer a local LLM (e.g., Ollama) you can adjust the `ChatOpenAI`
initialisation in `brief/nodes.py`.

## Running the demo
```bash
python brief_agent.py
```
The script prints:
* the generated outline,
* each research note prefixed with its step number,
* the final synthesized brief.

You can change the topic by setting the environment variable `BRIEF_TOPIC` before running the script:
```bash
BRIEF_TOPIC="Your custom topic" python brief_agent.py
```

---

## Project structure
```
brief/                # package containing the LangGraph workflow
│   state.py          # TypedDict defining the workflow state
│   nodes.py          # LLM & Tavily node implementations
│   graph.py          # construction of the StateGraph
brief_agent.py        # entry‑point script that runs the graph
requirements.txt      # Python dependencies
README.md              # this file
```

## Notes & troubleshooting
* **Missing API keys** – the script will raise an error if `TAVILY_API_KEY` (or `OPENAI_API_KEY` when using OpenAI) is not set.
* **Rate limits** – Tavily imposes rate limits; if you hit them, wait a few seconds and retry.
* **LLM model** – the code uses `gpt-3.5-turbo`. You can switch to another model by changing the `model` argument in `ChatOpenAI` calls.

---

## License
This example code is provided for educational purposes and is released under the MIT License.
